import os
import time

from authlib.jose import jwt
from authlib.jose.errors import ExpiredTokenError, JoseError
from litestar import Router, Request, get
from litestar.exceptions import NotAuthorizedException
from litestar.response import Redirect
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse

oauth = OAuth()


class MissingTokenException(NotAuthorizedException):
    detail = "No authentication token was provided."


class InvalidTokenException(NotAuthorizedException):
    detail = "The authentication token is malformed or invalid."


class ExpiredTokenException(NotAuthorizedException):
    detail = "The authentication token has expired."


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

    # authorize_access_token verifies Google's id_token (signature, issuer,
    # audience, nonce) and exposes the claims as userinfo. Trust it once here,
    # then issue our own session token signed with JWT_SECRET.
    user_email = token.get("userinfo", {}).get("email")
    if not user_email:
        return Redirect("/auth/login")

    now = int(time.time())
    auth_token = jwt.encode(
        {"alg": "HS256"},
        {"email": user_email, "iat": now, "exp": now + 24 * 60 * 60},
        os.getenv("JWT_SECRET"),
    ).decode("ascii")

    response = Redirect("/dashboard")
    response.set_cookie(
        key="auth_token",
        value=auth_token,
        httponly=True,
        secure=True,
        samesite="Lax",
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
        # bad signature or malformed token
        raise InvalidTokenException()

    user_email = claims.get("email")
    if not user_email:
        raise InvalidTokenException()

    return user_email


router = Router(path="/auth", route_handlers=[login, callback])