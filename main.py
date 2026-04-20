import strawberry
from litestar import Litestar
from litestar.static_files import create_static_files_router
from strawberry.litestar import make_graphql_controller

from lib import AlchemyDriver, Query, S3Driver, SubmissionMutation, SubmissionQuery


async def startup():
    AlchemyDriver.init()
    S3Driver.init()

async def close():
    await AlchemyDriver.close()


schema = strawberry.Schema(query=Query)
submission_schema = strawberry.Schema(query=SubmissionQuery, mutation=SubmissionMutation)

solution_controller = make_graphql_controller(schema=schema, path="/solution", graphql_ide="graphiql")
isubmission_controller = make_graphql_controller(schema=submission_schema, path="/submission", graphql_ide="graphiql", multipart_uploads_enabled=True)
ui_router = create_static_files_router(path="/", directories=["/dist"], html_mode=True)

app = Litestar(
    route_handlers=[solution_controller, submission_controller, ui_router],
    on_startup=[startup],
    on_shutdown=[close],
    debug=True,
)