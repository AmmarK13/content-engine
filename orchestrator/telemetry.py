from psycopg import connect
import os

from contracts.common.telemetry import StageRunRecordV1


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "content_engine"),
    "user": os.getenv("DB_USER", "temporal"),
    "password": os.getenv("DB_PASSWORD", "temporal"),
}


def get_connection():
    """Return a connection to the local PostgreSQL database."""
    return connect(**DB_CONFIG)


def record_telemetry(record: StageRunRecordV1) -> None:
    """
    Persist one StageRunRecordV1 as a single row - one row per stage
    execution, so end-of-M1 verification can confirm every stage emitted
    cost/latency/provider/version data.
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO stage_run_records (
                    run_id,
                    stage_id,
                    attempt,
                    input_hash,
                    output_hash,
                    provider_name,
                    provider_model,
                    provider_version,
                    provider_capability,
                    provider_endpoint,
                    provider_cost,
                    provider_latency_ms,
                    started_at,
                    ended_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    record.run_id,
                    record.stage_id,
                    record.attempt,
                    record.input_hash,
                    record.output_hash,
                    record.provider.provider,
                    record.provider.model,
                    record.provider.version,
                    record.provider.capability,
                    record.provider.endpoint,
                    record.provider.cost,
                    record.provider.latency_ms,
                    record.started_at,
                    record.ended_at,
                ),
            )
        conn.commit()
