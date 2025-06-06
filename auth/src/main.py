import asyncio

from argon2 import PasswordHasher
from dishka import make_async_container
from dishka.integrations import faststream as faststream_integration
from dishka.integrations import litestar as litestar_integration
from faststream import FastStream
from faststream.rabbit import RabbitBroker
from litestar import Litestar
import uvicorn


from auth.src.config import Config
from auth.src.controllers.amqp import AuthMQController
from auth.src.controllers.http import AuthController
from auth.src.ioc import AppProvider


config = Config()
hasher = PasswordHasher()
container = make_async_container(AppProvider(), context={Config: config, PasswordHasher: hasher})


async def get_faststream_app() -> FastStream:
    async with container() as opened_container:
        broker = await opened_container.get(RabbitBroker)
        faststream_app = FastStream(broker)
        faststream_integration.setup_dishka(container, faststream_app, auto_inject=True)
        broker.include_router(AuthMQController)
    return faststream_app

async def get_litestar_app() -> Litestar:
    litestar_app = Litestar(
        route_handlers=[AuthController],
    )
    litestar_integration.setup_dishka(container, litestar_app)
    return litestar_app

async def get_app() -> Litestar:
    faststream_app: FastStream = await get_faststream_app()
    litestar_app: Litestar = await get_litestar_app()
    litestar_app.on_startup.append(faststream_app.broker.start)
    litestar_app.on_shutdown.append(faststream_app.broker.close)
    return litestar_app

async def main(config: Config):
        app = await get_app()
        config = uvicorn.Config(app=app, log_level=config.app.log_level)
        server = uvicorn.Server(config)
        await server.serve()

if __name__ == "__main__":
    asyncio.run(main(config))