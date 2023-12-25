from fastapi_redis_session.config import basicConfig
import random
from datetime import timedelta

basicConfig(
    redisURL="redis://localhost:6380/1",
    sessionIdName="session_id",
    sessionIdGenerator=lambda: str(random.randint(1000, 9999)),
    expireTime=timedelta(days=1),
    )