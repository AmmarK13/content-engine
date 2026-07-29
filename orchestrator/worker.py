"""
orchestrator/worker.py

The worker process. Registers both the hello-world workflow (stack health check)
and the real AvatarPipeline workflow.
"""

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from orchestrator.hello_workflow import HelloWorkflow, say_hello, TASK_QUEUE
from orchestrator.pipeline import AvatarPipeline
from orchestrator.activities import run_stage

# Import and register all stub providers so the registry is populated
# before the worker starts accepting work.
from orchestrator.registry import register
from providers.stub_script import StubScriptProvider

# Register stubs - add more here as other team members' stubs land
register(StubScriptProvider())

TEMPORAL_HOST = "localhost:7233"


async def main() -> None:
    client = await Client.connect(TEMPORAL_HOST)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[HelloWorkflow, AvatarPipeline],
        activities=[say_hello, run_stage],
    )
    print(f"Worker started, polling task queue '{TASK_QUEUE}'. Ctrl+C to stop.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())