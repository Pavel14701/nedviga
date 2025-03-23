from os import environ as env

from pydantic import Field, BaseModel, field_validator


class AppConfig(BaseModel):
    log_level: str = Field(default="info", alias='APP_LOG_LEVEL')
    secret_key: str = Field(alias='APP_SECRET_KEY')
    allowed_hosts: list[str] = Field(default_factory=list, alias='APP_ALLOWED_HOSTS')

    @field_validator("allowed_hosts", mode="before")
    def split_allowed_hosts(cls, value):
        if isinstance(value, str):
            return value.split(",")
        return value


class SecurityConfig(BaseModel):
    secret_access_key: str = Field(alias='OAUTH_ACCESS_SECRET')
    secret_refresh_key: str = Field(alias='OAUTH_REFRESH_SECRET')
    algorithm: str = Field(alias='OAUTH_ALGO')
    access_token_expire_minutes: int = Field(default=30, alias='ACCESS_TOKEN_EXPIRE_MINUTES')
    refresh_access_token_expire_days: int = Field(default=7, alias='REFRESH_TOKEN_EXPIRE_DAYS')


class PostgresConfig(BaseModel):
    host: str = Field(alias='POSTGRES_HOST')
    port: int = Field(alias='POSTGRES_PORT')
    login: str = Field(alias='POSTGRES_USER')
    password: str = Field(alias='POSTGRES_PASSWORD')
    database: str = Field(alias='POSTGRES_DB')


class RabbitMQConfig(BaseModel):
    host: str = Field(alias='RABBITMQ_HOST')
    port: int = Field(alias='RABBITMQ_PORT')
    login: str = Field(alias='RABBITMQ_USER')
    password: str = Field(alias='RABBITMQ_PASSWORD')
    vhost: str = Field(alias='RABBITMQ_VHOST')

class RedisConfig(BaseModel):
    REDIS_PORT: str = Field(alias='REDIS_PORT')
    REDIS_HOST: str = Field(alias='REDIS_HOST')
    REDIS_DB: str = Field(alias='REDIS_DB')
    REDIS_MAX_CONNECTIONS: int = Field(alias='REDIS_MAX_CONNECTIONS')
    REDIS_CONFIRM_TIME: int = Field(alias='REDIS_CONFIRM_TIME')


class Config(BaseModel):
    app: AppConfig = Field(default_factory=lambda: AppConfig(**env))
    security: SecurityConfig = Field(default_factory=lambda: SecurityConfig(**env))
    postgres: PostgresConfig = Field(default_factory=lambda: PostgresConfig(**env))
    rabbitmq: RabbitMQConfig = Field(default_factory=lambda: RabbitMQConfig(**env))
    redis: RedisConfig = Field(default_factory=lambda: RedisConfig(**env))