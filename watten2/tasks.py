import asyncio
from asyncio import PriorityQueue, get_event_loop, AbstractEventLoop


class Task:
    def __init__(self, task_id: int, ):
        pass


class TaskWorker:
    def __init__(self, worker: int = 5, max_tasks: int = 100):
        self.worker: int = worker
        self.max_tasks: int = max_tasks
        self.loop: AbstractEventLoop = get_event_loop()
        self.queue: PriorityQueue = PriorityQueue(max_tasks)

    async def add_new_task(self, level: int, task: Task):
        await self.queue.put((level, task))

    async def cleanup(self):
        self.queue.empty()

    async def work(self):
        await asyncio.create_task()
