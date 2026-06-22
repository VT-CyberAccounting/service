import os
import strawberry
from litestar import Litestar, get, Request
from litestar.exceptions import NotAuthorizedException
from litestar.static_files import create_static_files_router
from litestar.response import Redirect
from strawberry.litestar import make_graphql_controller
from authlib.integrations.starlette_client import OAuth
from starlette.responses import RedirectResponse
from litestar.middleware.session.client_side import CookieBackendConfig

from lib import AlchemyDriver, Query, SubmissionQuery, SubmissionMutation

oauth = OAuth()

session_config = CookieBackendConfig(secret=os.urandom(16))

async def startup():
    AlchemyDriver.init()
    oauth.register(
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'email'},
    )

async def close():
    await AlchemyDriver.close()

@get("/login")
async def login(request: Request) -> RedirectResponse:
    redirect_uri = f"{request.base_url}auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri=redirect_uri)

@get("/auth/callback")
async def callback(request: Request) -> Redirect:
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception:
        return Redirect("/login")

    response = Redirect("/")
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

@get("/live/token")
async def token(email: str) -> str:
    return f"dummy token for {email}"

async def graphql_context(email: str) -> dict:
    return {"email": email}

solution_schema = strawberry.Schema(query=Query)
submission_schema = strawberry.Schema(query=SubmissionQuery, mutation=SubmissionMutation)

solution_controller = make_graphql_controller(schema=solution_schema, path="/solution", graphql_ide="graphiql")
submission_controller = make_graphql_controller(
    schema=submission_schema,
    path="/submission",
    graphql_ide="graphiql",
    context_getter=graphql_context,
)
ui_router = create_static_files_router(path="/", directories=["/dist"], html_mode=True)

app = Litestar(
    route_handlers=[login, callback, token, solution_controller, submission_controller, ui_router],
    dependencies={"email": email},
    on_startup=[startup],
    on_shutdown=[close],
    middleware=[session_config.middleware],
    debug=True,
)