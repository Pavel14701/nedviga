import redis.asyncio as redis
from redis.asyncio import Redis
from events.src.config import RedisConfig

def new_redis_client(redis_config: RedisConfig) -> Redis:
    pool = redis.ConnectionPool(
        max_connections = redis_config.REDIS_MAX_CONNECTIONS,
        host = redis_config.REDIS_HOST,
        port = redis_config.REDIS_PORT,
        db = redis_config.REDIS_DB)
    return Redis(connection_pool=pool)