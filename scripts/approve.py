"""
scripts/approve.py

CLI tool to send a G80 HumanApprovalV1 signal to a running Temporal workflow.
Usage:
    python scripts/approve.py <workflow_id> [approved|rejected|changes_requested] [master_video_hash]
"""

import asyncio
import sys
from datetime import datetime, timezone

from temporalio.client import Client

from contracts.stages.g80_approval import ApprovalDecision, HumanApprovalV1


async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/approve.py <workflow_id> [decision] [master_video_hash]")
        sys.exit(1)

    workflow_id = sys.argv[1]
    decision_raw = sys.argv[2] if len(sys.argv) > 2 else "approved"
    master_video_hash = sys.argv[3] if len(sys.argv) > 3 else "b" * 64

    decision_enum = ApprovalDecision(decision_raw.lower())

    approval_payload = HumanApprovalV1(
        reviewer_id="cli_reviewer",
        decision=decision_enum,
        master_video_hash=master_video_hash,
        timestamp=datetime.now(timezone.utc),
        comments="Approved via CLI approve.py script",
    )

    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle(workflow_id)

    # Signal the workflow with the HumanApprovalV1 decision
    await handle.signal("approve", approval_payload.model_dump(mode="json"))
    print(f"Approval signal sent to workflow '{workflow_id}' with decision '{decision_enum.value}'.")


if __name__ == "__main__":
    asyncio.run(main())
