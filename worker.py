import os

import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']



redis_url = os.getenv('REDIS_URL', 'redis://:p0a11655774103cd86bcdf8300d9587c10f573be7069ffaf0b7d8c0835c8ac91d@ec2-54-221-249-45.compute-1.amazonaws.com:30669')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
