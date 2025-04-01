import redis

REDIS_URL='redis://localhost:6379/0'
REDIS_EXPIRE=3600

redis_client = redis.Redis.from_url(REDIS_URL)
DEFAULT_EXPIRE = REDIS_EXPIRE or 3600
