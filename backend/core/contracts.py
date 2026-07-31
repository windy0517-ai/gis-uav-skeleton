"""Small, dependency-free response helpers shared by routes and tools."""

from datetime import datetime, timezone
from time import perf_counter
from typing import Optional


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def success(data=None, module: str = "system", algorithm: str = "unknown",
            started_at: Optional[float] = None, **meta) -> dict:
    metadata = {
        "module": module,
        "algorithm": algorithm,
        "timestamp": utc_now(),
    }
    if started_at is not None:
        metadata["processing_time_ms"] = round((perf_counter() - started_at) * 1000, 2)
    metadata.update(meta)
    return {
        "status": "success",
        "data": data if data is not None else {},
        "meta": metadata,
        "error": None,
    }


def failure(code: str, message: str, module: str = "system",
            started_at: Optional[float] = None, **meta) -> dict:
    metadata = {
        "module": module,
        "timestamp": utc_now(),
    }
    if started_at is not None:
        metadata["processing_time_ms"] = round((perf_counter() - started_at) * 1000, 2)
    metadata.update(meta)
    return {
        "status": "error",
        "data": None,
        "meta": metadata,
        "error": {"code": code, "message": message},
    }


def http_status(result: dict) -> int:
    """Map the common envelope to a simple HTTP status for Flask routes."""
    return 200 if result.get("status") == "success" else 400
