import os

from litestar import Router, Request, get
from litestar.exceptions import NotAuthorizedException
from litestar.response import Redirect
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse

oauth = OAuth()

def register_oauth() -> None:
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'email'},
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

    response = Redirect("/dashboard")
    response.set_cookie(
        key="access_token",
        value=token.get("access_token"),
        httponly=True,
        secure=True,
        samesite="Lax",
    )
    return response


async def email(request: Request) -> str:
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise NotAuthorizedException()
    user = await oauth.google.get(
        "https://www.googleapis.com/oauth2/v1/userinfo",
        token={"access_token": access_token, "token_type": "Bearer"}
    )
    if user.is_success:
        return user.json().get("email", "Email not found")
    else:
        raise NotAuthorizedException()


router = Router(path="/auth", route_handlers=[login, callback])