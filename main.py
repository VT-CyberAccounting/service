import strawberry
from litestar import Litestar
from litestar.static_files import create_static_files_router
from os import getenv
from lib import AlchemyDriver, Query
from strawberry.litestar import make_graphql_controller


async def startup():
    AlchemyDriver.init()

async def close():
    await AlchemyDriver.close()


schema = strawberry.Schema(query=Query)
graphql_controller = make_graphql_controller(schema=schema, path="/graphql", graphql_ide="graphiql")
ui_router = create_static_files_router(path="/", directories=["/dist"], html_mode=True)

app = Litestar(
    route_handlers=[graphql_controller, ui_router],
    on_startup=[startup],
    on_shutdown=[close],
    debug=True
)