import strawberry
from litestar import Router, get
from strawberry.litestar import make_graphql_controller

from .auth import email
from .solution import Query
from .submission import Query as SubmissionQuery, Mutation as SubmissionMutation


@get("/livetoken")
async def token(email: str) -> str:
    return f"token for {email}: "


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