import os
import secrets
import time

from authlib.integrations.starlette_client import OAuth
from authlib.jose import jwt
from authlib.jose.errors import ExpiredTokenError, JoseError
from litestar import Router, Request, get, post
from litestar.exceptions import HTTPException, NotAuthorizedException, NotFoundException, TooManyRequestsException
from litestar.response import Redirect, Response
from litestar.status_codes import HTTP_202_ACCEPTED, HTTP_409_CONFLICT
from starlette.responses import RedirectResponse

from .driver import Driver

oauth = OAuth()

class CodedAuthException(NotAuthorizedException):
    """401 with a stable machine-readable ``code`` in the response body's ``extra``."""
    code: str = "unauthorized"

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("extra", {"code": self.code})
        super().__init__(*args, **kwargs)

class MissingTokenException(CodedAuthException):
    code = "missing_token"
    detail = "No authentication token was provided."

class InvalidTokenException(CodedAuthException):
    code = "invalid_token"
    detail = "The authentication token is malformed or invalid."

class ExpiredTokenException(CodedAuthException):
    code = "expired_token"
    detail = "The authentication token has expired."

class InvalidDeviceTokenException(NotFoundException):
    detail = "The device pairing token is invalid, expired, or already used."

class InvalidDeviceCodeException(NotFoundException):
    detail = "The device code is invalid or expired."

class TooManyDeviceRetriesException(TooManyRequestsException):
    detail = "Too many failed approval attempts. The pairing token has been revoked."

class DeviceAlreadyApprovedException(HTTPException):
    status_code = HTTP_409_CONFLICT
    detail = "This pairing request has already been approved."

def register_oauth() -> None:
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email'},
    )

@get("/login")
async def login(request: Request) -> RedirectResponse:
    redirect_uri = f"{request.base_url}auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri=redirect_uri)


@get("/callback")
async def callback(request: Request) -> Redirect:
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception:
        return Redirect("/auth/login")

    user_email = token.get("userinfo", {}).get("email")
    if not user_email:
        return Redirect("/auth/login")

    now = int(time.time())
    auth_token = jwt.encode(
        {"alg": "HS256"},
        {"email": user_email, "iat": now, "exp": now + 24 * 60 * 60},
        os.getenv("JWT_SECRET"),
    ).decode("ascii")

    response = Redirect("/")
    response.set_cookie(
        key="auth_token",
        value=auth_token,
        httponly=True,
        secure=True,
        samesite="Lax",
    )
    return response


@get("/logout")
async def logout(request: Request) -> Redirect:
    response = Redirect("/auth/login")
    response.delete_cookie(
        key="auth_token",
    )
    return response


async def email(request: Request) -> str:
    auth_token = request.cookies.get("auth_token")
    if not auth_token:
        raise MissingTokenException()

    try:
        claims = jwt.decode(
            auth_token,
            os.getenv("JWT_SECRET"),
            claims_options={"exp": {"essential": True}},
        )
        claims.validate()
    except ExpiredTokenError:
        raise ExpiredTokenException()
    except (JoseError, ValueError, KeyError):
        raise InvalidTokenException()

    user_email = claims.get("email")
    if not user_email:
        raise InvalidTokenException()

    return user_email


@get("/whoami")
async def whoami(email: str) -> str:
    return email


@post("/device")
async def device(email: str) -> dict:
    pairing_token = secrets.token_urlsafe(32)
    await Driver.redis.hset(f"device:{pairing_token}", mapping={"email": email, "status": "initiated"})
    await Driver.redis.expire(f"device:{pairing_token}", 120)
    return {"token": pairing_token}


@post("/device/redeem")
async def redeem(pairing_token: str) -> dict:
    key = f"device:{pairing_token}"
    if await Driver.redis.hget(key, "status") != "initiated":
        await Driver.redis.delete(key)
        raise InvalidDeviceTokenException()
    code = f"{secrets.randbelow(1000000):06d}"
    await Driver.redis.hset(key, mapping={"status": "redeemed", "code": code})
    return {"code": code}


@post("/device/approve")
async def approve(email: str, pairing_token: str, code: str) -> Response:
    key = f"device:{pairing_token}"
    record = await Driver.redis.hgetall(key)
    if record.get("status") == "approved" and record.get("email") == email:
        raise DeviceAlreadyApprovedException()
    if record.get("status") != "redeemed" or record.get("email") != email:
        await Driver.redis.delete(key)
        raise InvalidDeviceTokenException()
    if code != record.get("code"):
        if await Driver.redis.hincrby(key, "retries", 1) >= 5:
            await Driver.redis.delete(key)
            raise TooManyDeviceRetriesException()
        raise InvalidDeviceCodeException()
    await Driver.redis.hset(key, "status", "approved")
    return Response(content=None, status_code=HTTP_202_ACCEPTED)


@get("/device/status")
async def status(pairing_token: str) -> dict:
    record_status = await Driver.redis.hget(f"device:{pairing_token}", "status")
    if record_status is None:
        raise InvalidDeviceTokenException()
    return {"status": record_status}


@get("/device/token")
async def token(pairing_token: str) -> Response:
    key = f"device:{pairing_token}"
    if await Driver.redis.hget(key, "status") != "approved":
        return Response(content=None, status_code=HTTP_202_ACCEPTED)
    now = int(time.time())
    auth_token = jwt.encode(
        {"alg": "HS256"},
        {"email": await Driver.redis.hget(key, "email"), "iat": now, "exp": now + 7 * 24 * 60 * 60},
        os.getenv("JWT_SECRET"),
    ).decode("ascii")
    await Driver.redis.hset(key, "status", "delivered")
    return Response(content={"token": auth_token})


router = Router(
    path="/auth",
    route_handlers=[login, callback, logout, whoami, device, redeem, approve, status, token],
    dependencies={"email": email},
)