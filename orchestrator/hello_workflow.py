from datetime import timedelta


from temporalio import activity, workflow

TASK_QUEUE = "avatar-harness"

@activity.defn
async def say_hello(name:str)->str:
    return f"Hello {name} !"


@workflow.defn
class HelloWorkflow:
    """Orchestration logic comes here
        no real work nothing
     """

    @workflow.run
    async def run(self,name:str)->str:
        return await workflow.execute_activity(
            say_hello,
            name,
            start_to_close_timeout=timedelta(seconds=10),
        )
 
