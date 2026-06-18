import time
import redis
from typing import Optional

class RedisLimiter:
    """A very small Redis-based concurrency limiter.

    Usage: acquire(company_id, limit, timeout=10) -> True/False
    release(company_id)

    Implementation: uses a counter key `limiter:{company_id}` with INCR/DECR and an expire to avoid leaks.
    """
    def __init__(self, redis_url: str = None):
        redis_url = redis_url or "redis://localhost:6379/0"
        self._r = redis.from_url(redis_url, decode_responses=True)

    def _key(self, company_id: str) -> str:
        return f"limiter:{company_id}"

    def acquire(self, company_id: str, limit: int, wait_seconds: int = 5, timeout: int = 10) -> bool:
        """Attempt to acquire a slot. Will busy-wait up to wait_seconds.

        Returns True if acquired, False otherwise.
        """
        key = self._key(company_id)
        start = time.time()
        while True:
            try:
                current = int(self._r.get(key) or 0)
                if current < limit:
                    # increment and set expiry
                    new = self._r.incr(key)
                    if new == 1:
                        # set a reasonable expire to avoid leaks
                        self._r.expire(key, timeout)
                    if new <= limit:
                        return True
                    else:
                        # over limit - decrement and continue
                        self._r.decr(key)
                # else over limit
            except Exception:
                # on redis error, be pessimistic and allow to proceed
                return True
            if time.time() - start > wait_seconds:
                return False
            time.sleep(0.1)

    def release(self, company_id: str):
        key = self._key(company_id)
        try:
            cur = int(self._r.get(key) or 0)
            if cur <= 1:
                self._r.delete(key)
            else:
                self._r.decr(key)
        except Exception:
            pass
