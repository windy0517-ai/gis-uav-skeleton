"""Backward-compatible import path for the shared workflow engine."""

from services.workflow_engine import RuleEngine, SCENARIOS, execute_workflow

__all__ = ["RuleEngine", "SCENARIOS", "execute_workflow"]
