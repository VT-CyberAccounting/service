import strawberry
from litestar import Litestar
from litestar.static_files import create_static_files_router
from strawberry.litestar import make_graphql_controller

from lib import AlchemyDriver, Query, SubmissionQuery, SubmissionMutation


async def startup():
    AlchemyDriver.init()

async def close():
    await AlchemyDriver.close()


solution_schema = strawberry.Schema(query=Query)
submission_schema = strawberry.Schema(query=SubmissionQuery, mutation=SubmissionMutation)

solution_controller = make_graphql_controller(schema=solution_schema, path="/solution", graphql_ide="graphiql")
submission_controller = make_graphql_controller(schema=submission_schema, path="/submission", graphql_ide="graphiql")
ui_router = create_static_files_router(path="/", directories=["/dist"], html_mode=True)

app = Litestar(
    route_handlers=[solution_controller, submission_controller, ui_router],
    on_startup=[startup],
    on_shutdown=[close],
    debug=True,
)