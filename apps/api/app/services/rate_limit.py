from fastapi import HTTPException, Request
from redis.asyncio import Redis
from app.config import settings

redis=Redis.from_url(settings.redis_url, decode_responses=True)

async def enforce_rate_limit(request: Request, bucket: str='scan') -> None:
    ip=request.client.host if request.client else 'unknown'
    key=f"safescroll:rl:{bucket}:{ip}"
    try:
        pipe=redis.pipeline()
        pipe.incr(key)
        pipe.expire(key,60)
        count,_=await pipe.execute()
        if int(count)>settings.rate_limit_per_minute:
            raise HTTPException(status_code=429,detail='Too many requests. Please try again shortly.')
    except HTTPException:
        raise
    except Exception:
        # Fail-open for availability; production deployments should alert on Redis failures.
        return
