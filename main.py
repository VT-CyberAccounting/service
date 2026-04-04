import strawberry
from litestar import Litestar
from os import getenv
from lib import AlchemyDriver, Query
from strawberry.litestar import make_graphql_controller


async def startup():
    AlchemyDriver.init()

async def close():
    await AlchemyDriver.close()


schema = strawberry.Schema(query=Query)
graphql_controller = make_graphql_controller(schema=schema, path="/graphql", graphql_ide="graphiql")

app = Litestar(
    route_handlers=[graphql_controller],
    on_startup=[startup],
    on_shutdown=[close],
    debug=True
)