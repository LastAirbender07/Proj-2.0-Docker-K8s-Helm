"""
Long-running worker process: listens to Redis RQ queue and processes jobs.
Also RQ worker automatically handles retries if set.
"""
import time
import logging
from redis import Redis, RedisError
from rq import Worker, Queue
from rq.connections import Connection
from app.core.config import settings

logger = logging.getLogger(__name__)
listen = [settings.RQ_QUEUE]


def get_redis_connection(retries: int = 5, delay: int = 3) -> Redis | None:
    for attempt in range(1, retries + 1):
        try:
            conn = Redis.from_url(settings.REDIS_URL)
            # optional ping check
            conn.ping()
            logger.info("Connected to Redis on attempt %d", attempt)
            return conn
        except RedisError as e:
            logger.warning("Redis connection failed (attempt %d/%d): %s", attempt, retries, e)
            time.sleep(delay)
    logger.error("Could not connect to Redis after %d attempts", retries)
    return None


def start_worker():
    """
    Start the RQ worker after establishing a Redis connection.
    Retries gracefully instead of crashing.
    """
    redis_conn = get_redis_connection()
    if not redis_conn:
        logger.error("Redis connection unavailable. Worker exiting.")
        return

    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        logger.info("Worker started. Listening to queues: %s", listen)
        worker.work()


if __name__ == "__main__":
    start_worker()

