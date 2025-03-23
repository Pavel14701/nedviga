from logging import Logger

from dishka import Provider, Scope, provide, from_context

from mail.src.application import interfaces
from mail.src.application.interactors import SendSignupMailInteractor
from mail.src.config import Config
from mail.src.infrastructure.gateways import SendEmailGateway
from mail.src.infrastructure.templates import TemplatesGateway


class AppProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    logger = from_context(provides=Logger, scope=Scope.APP)

    send_email_gateway = provide(
        SendEmailGateway,
        scope=Scope.REQUEST,
        provides=interfaces.EmailSender
    )

    get_templates_gateway = provide(
        TemplatesGateway,
        scope=Scope.REQUEST,
        provides=interfaces.GetTemplates
    )

    send_signup_email_interactor = provide(SendSignupMailInteractor, scope=Scope.REQUEST)