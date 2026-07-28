from datetime import timedelta
import asyncio


from temporalio.client import Client
from temporalio.worker import Worker

from orchestrator.hello_workflow import TASK_QUEUE, HelloWorkflow, say_hello

Temporal_host= "localhost:7233"

async def main()->None:
    client = await Client.connect(Temporal_host)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows = [HelloWorkflow],
        activities =[say_hello]
    )
    print(f"Worker started, polling task queue '{TASK_QUEUE}'. Ctrl+C to stop.")
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())