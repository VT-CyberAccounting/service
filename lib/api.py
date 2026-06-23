from datetime import datetime, timedelta, timezone
from os import getenv

import strawberry
from google import genai
from litestar import Router, get
from strawberry.litestar import make_graphql_controller

from .auth import email
from .solution import Query
from .submission import Query as SubmissionQuery, Mutation as SubmissionMutation

genai_client: genai.Client | None = None


async def startup():
    global genai_client
    genai_client = genai.Client(
        api_key=getenv("GEMINI_API_KEY"),
        http_options={"api_version": "v1alpha"},
    )


@get("/livetoken")
async def token(email: str) -> str:
    now = datetime.now(tz=timezone.utc)
    window = now + timedelta(hours=24)
    result = await genai_client.aio.auth_tokens.create(
        config={
            "uses": 1000,
            "expire_time": window,
            "new_session_expire_time": window,
            "http_options": {"api_version": "v1alpha"},
        }
    )
    return result.name

async def graphql_context(email: str) -> dict:
    return {"email": email}

solution_schema = strawberry.Schema(query=Query)
submission_schema = strawberry.Schema(query=SubmissionQuery, mutation=SubmissionMutation)

solution_controller = make_graphql_controller(
    schema=solution_schema,
    path="/solution",
    graphql_ide="graphiql",
    context_getter=graphql_context,
)
submission_controller = make_graphql_controller(
    schema=submission_schema,
    path="/submission",
    graphql_ide="graphiql",
    context_getter=graphql_context,
)

router = Router(
    path="/api",
    route_handlers=[token, solution_controller, submission_controller],
    dependencies={"email": email},
)