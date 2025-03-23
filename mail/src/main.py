import asyncio
import logging
from logging import Logger

from aiosmtpd.controller import Controller
from dishka import make_async_container
from dishka.integrations import faststream as faststream_integration
from faststream import FastStream

from mail.src.config import Config
from mail.src.controllers.controllers import EmailController, EmailHandler
from mail.src.infrastructure.broker import new_broker
from mail.src.ioc import AppProvider


config = Config()
logging.basicConfig(level=config.app.log_level)
logger = logging.getLogger("SMTPServer")
container = make_async_container(AppProvider(), context={Config: config, Logger: logger})


def get_faststream_app() -> FastStream:
    broker = new_broker(config.rabbitmq)
    app = FastStream(broker)
    faststream_integration.setup_dishka(container, app, auto_inject=True)
    broker.include_router(EmailController)
    return app



async def start_smtp_server(config: Config) -> None:
    controller = Controller(
        handler=EmailHandler(), 
        hostname=config.email.smtp_host, 
        port=config.email.smtp_port
    )
    controller.start()
    logger.info(f"SMTP server is running on {config.email.smtp_host}:{config.email.smtp_port}")
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        controller.stop()
        logger.info("SMTP server stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(start_smtp_server(config))
    except KeyboardInterrupt:
        logger.warning("Server shutdown by user.")
