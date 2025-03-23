from redis.asyncio import ConnectionPool
from auth.src.config import RedisConfig

def new_redis_client(redis_config: RedisConfig) -> ConnectionPool:
    return ConnectionPool(
        max_connections = redis_config.REDIS_MAX_CONNECTIONS,
        host = redis_config.REDIS_HOST,
        port = redis_config.REDIS_PORT,
        db = redis_config.REDIS_DB)