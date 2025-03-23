from os import environ as env
from pydantic import BaseModel, Field


class RabbitMQConfig(BaseModel):
    host: str = Field(alias='RABBITMQ_HOST')
    port: int = Field(alias='RABBITMQ_PORT')
    login: str = Field(alias='RABBITMQ_USER')
    password: str = Field(alias='RABBITMQ_PASSWORD')
    vhost: str = Field(alias='RABBITMQ_VHOST')


class PostgresConfig(BaseModel):
    host: str = Field(alias='POSTGRES_HOST')
    port: int = Field(alias='POSTGRES_PORT')
    login: str = Field(alias='POSTGRES_USER')
    password: str = Field(alias='POSTGRES_PASSWORD')
    database: str = Field(alias='POSTGRES_DB')


class RedisConfig(BaseModel):
    REDIS_PORT:str = Field(alias='REDIS_PORT')
    REDIS_HOST:str = Field(alias='REDIS_HOST')
    REDIS_DB:str = Field(alias='REDIS_DB')
    REDIS_MAX_CONNECTIONS:int = Field(alias='REDIS_MAX_CONNECTIONS')


class Config(BaseModel):
    rabbitmq: RabbitMQConfig = Field(default_factory=lambda: RabbitMQConfig(**env))
    postgres: PostgresConfig = Field(default_factory=lambda: PostgresConfig(**env))
    redis: RedisConfig = Field(default_factory=lambda: RedisConfig(**env))