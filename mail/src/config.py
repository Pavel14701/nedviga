from os import environ as env

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    confirm_path: str = Field(alias='REGISTRATION_CONFIRM_PATH')
    log_level: str = Field(alias='SMTP_LOG_LEVEL') #INFO


class EmailConfig(BaseModel):
    smtp_host: str = Field(alias='SMTP_HOST') #127.0.0.1
    smtp_port: int = Field(alias='SMTP_PORT') #1025
    sender_email: str = Field(alias='SMTP_SENDER_EMAIL') #your_email@example.com


class RabbitMQConfig(BaseModel):
    host: str = Field(alias='RABBITMQ_HOST')
    port: int = Field(alias='RABBITMQ_PORT')
    login: str = Field(alias='RABBITMQ_USER')
    password: str = Field(alias='RABBITMQ_PASSWORD')
    vhost: str = Field(alias='RABBITMQ_VHOST')


class Config(BaseModel):
    app: AppConfig = Field(default_factory=lambda: AppConfig(**env))
    email: EmailConfig = Field(default_factory=lambda: EmailConfig(**env))
    rabbitmq: RabbitMQConfig = Field(default_factory=lambda: RabbitMQConfig(**env))