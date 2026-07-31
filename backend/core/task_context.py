"""Shared execution context used by the fixed workflow engine."""

from typing import Optional


class TaskContext(dict):
    """A small dict-like context for task input, results and artifacts."""

    def __init__(self, task_id: str, scenario: str, params: dict):
        super().__init__(
            task_id=task_id,
            scenario=scenario,
            input=params,
            results={},
            artifacts={},
            metrics={},
            logs=[],
            state="running",
        )

    def record(self, step_id: str, result: dict, artifact_name: Optional[str] = None):
        data = result.get("data", {})
        self["results"][step_id] = data
        if artifact_name:
            self["artifacts"][artifact_name] = data
        meta = result.get("meta", {})
        if meta.get("processing_time_ms") is not None:
            self["metrics"][f"{step_id}.processing_time_ms"] = meta["processing_time_ms"]

    def export(self) -> dict:
        return {
            "task_id": self["task_id"],
            "scenario": self["scenario"],
            "state": self["state"],
            "results": self["results"],
            "artifacts": self["artifacts"],
            "metrics": self["metrics"],
        }
