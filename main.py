import os

from litestar import Litestar
from litestar.middleware.session.client_side import CookieBackendConfig

from lib import AlchemyDriver, auth_router, api_router, register_oauth, api_startup

session_config = CookieBackendConfig(secret=os.urandom(16))

async def startup():
    AlchemyDriver.init()
    register_oauth()
    await api_startup()

async def close():
    await AlchemyDriver.close()

app = Litestar(
    route_handlers=[auth_router, api_router],
    on_startup=[startup],
    on_shutdown=[close],
    middleware=[session_config.middleware],
    debug=True,
)