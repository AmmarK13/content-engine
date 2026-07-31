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

from orchestrator.activities import run_stage
from orchestrator.pipeline import AvatarPipeline, TASK_QUEUE
from orchestrator.registry import register_all_stubs

# Register stubs - add more here as other team members' stubs land
#register(StubScriptProvider())  removing it from here since reigster stub call all. 

TEMPORAL_HOST = "localhost:7233"

async def main():
    
    register_all_stubs()
    
    client = await Client.connect("localhost:7233")
    
    
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[AvatarPipeline],
        activities=[run_stage],
    )
    
    print(f"Starting worker on task queue: {TASK_QUEUE}")
    
    # Run the worker
    await worker.run()



if __name__ == "__main__":
    asyncio.run(main())