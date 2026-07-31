import json
import logging
from typing import Optional, Any
from app.core.config import settings

logger = logging.getLogger("ehis.cache")

class RedisCache:
    def __init__(self):
        self.redis_client = None
        if settings.REDIS_ENABLED:
            try:
                import redis
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    decode_responses=True,
                    socket_connect_timeout=2
                )
                self.redis_client.ping()
                logger.info("Redis cache connected.")
            except Exception as e:
                logger.warning(f"Redis not available, running without cache: {e}")
                self.redis_client = None

    @property
    def is_available(self) -> bool:
        return self.redis_client is not None

    def get(self, key: str) -> Optional[str]:
        if self.redis_client:
            try:
                return self.redis_client.get(key)
            except Exception as e:
                logger.error(f"Redis get error for key '{key}': {e}")
        return None

    def get_json(self, key: str) -> Optional[Any]:
        value = self.get(key)
        if value:
            try:
                return json.loads(value)
            except Exception:
                return None
        return None

    def set(self, key: str, value: str, expire_seconds: int = 3600) -> bool:
        if self.redis_client:
            try:
                self.redis_client.set(key, value, ex=expire_seconds)
                return True
            except Exception as e:
                logger.error(f"Redis set error for key '{key}': {e}")
        return False

    def set_json(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        try:
            return self.set(key, json.dumps(value, default=str), expire_seconds)
        except Exception as e:
            logger.error(f"Redis set_json error for key '{key}': {e}")
            return False

    def delete(self, key: str) -> bool:
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                return True
            except Exception as e:
                logger.error(f"Redis delete error for key '{key}': {e}")
        return False

    def delete_pattern(self, pattern: str) -> int:
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
            except Exception as e:
                logger.error(f"Redis delete_pattern error for pattern '{pattern}': {e}")
        return 0

redis_cache = RedisCache()
