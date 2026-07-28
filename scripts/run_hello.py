import asyncio

from temporalio.client import Client


from orchestrator.hello_workflow import TASK_QUEUE, HelloWorkflow

Temporal_host = "localhost:7233"

async def main()->None:
    client = await Client.connect(Temporal_host)
    result = await client.execute_workflow(
        HelloWorkflow.run,
        "avatar-harness",
        id="hello-workflow-1",
        task_queue=TASK_QUEUE,
    )
    print(f"workflow result : {result} ")


if __name__=="__main__":
    asyncio.run(main())

