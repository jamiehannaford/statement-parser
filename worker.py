from redis import Redis
from rq import Queue, Connection
from rq.worker import SimpleWorker as Worker

listen = ['high', 'default', 'low']

conn = Redis(host='redis', port='6379', db=0)
queue = Queue(connection=conn)

if __name__ == '__main__':
    worker = Worker([queue], connection=queue.connection)
    worker.work()