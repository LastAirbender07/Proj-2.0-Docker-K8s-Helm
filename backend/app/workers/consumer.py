"""
Long-running worker process: listens to Redis RQ queue and processes jobs.
Also rq worker automatically handles retries if set.
"""
import os
from redis import Redis
from rq import Worker, Queue, Connection
from ..core.config import settings

listen = [settings.RQ_QUEUE]
redis_conn = Redis.from_url(settings.REDIS_URL)

if __name__ == "__main__":
    with Connection(redis_conn):
        worker = Worker(map(Queue, listen))
        worker.work()
