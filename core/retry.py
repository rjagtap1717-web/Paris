import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry(max_attempts=3, backoff_factor=2.0, initial_wait=1.0, exceptions=(Exception,)):
    """
    Retry decorator for functions that may fail temporarily (e.g., network calls).
    Supports both sync and async functions.
    """
    def decorator(func):
        if __import__("asyncio").iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                wait = initial_wait
                for attempt in range(max_attempts):
                    try:
                        return await func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == max_attempts - 1:
                            logger.error(f"Failed after {max_attempts} attempts. Error: {e}")
                            raise
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {wait}s...")
                        import asyncio
                        await asyncio.sleep(wait)
                        wait *= backoff_factor
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                wait = initial_wait
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        if attempt == max_attempts - 1:
                            logger.error(f"Failed after {max_attempts} attempts. Error: {e}")
                            raise
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {wait}s...")
                        time.sleep(wait)
                        wait *= backoff_factor
            return sync_wrapper
    return decorator
