"""Tests for the offline hybrid Agent path."""

import unittest

from agents.emergency_agent import execute_agent
from agents.rule_planner import RulePlanner
from agents.schemas import PlanValidationError, validate_plan
from agents.tool_registry import AGENT_TOOLS
from app import app


class AgentPlanTest(unittest.TestCase):
    def test_rescue_plan(self):
        plan = RulePlanner().make_plan("请分析贵港洪水并寻找受困人员")
        self.assertFalse(plan.needs_clarification)
        self.assertEqual(
            [step.tool_id for step in plan.plan],
            ["water_extract", "object_detect", "gis_overlay", "risk_assess", "path_plan"],
        )

    def test_report_plan(self):
        plan = RulePlanner().make_plan("帮我生成一份灾情简报")
        self.assertEqual(
            [step.tool_id for step in plan.plan],
            ["stats", "risk_assess", "generate_report"],
        )

    def test_unknown_request_needs_clarification(self):
        plan = RulePlanner().make_plan("请帮我做一个完全未知的任务")
        self.assertTrue(plan.needs_clarification)
        self.assertEqual(plan.plan, [])

    def test_invalid_tool_is_rejected(self):
        with self.assertRaises(PlanValidationError):
            validate_plan(
                {"goal": "unsafe", "plan": [{"tool_id": "run_shell"}]},
                AGENT_TOOLS,
            )


class AgentExecutionTest(unittest.TestCase):
    def test_mock_agent_executes_and_records_artifacts(self):
        result = execute_agent(
            "请分析贵港洪水并寻找受困人员",
            {"region": "guigang", "provider": "mock"},
        )
        self.assertEqual(result["status"], "success")
        data = result["data"]
        self.assertEqual(data["state"], "completed")
        self.assertIn("water_extract", data["results"])
        self.assertIn("object_detect", data["results"])
        self.assertIn("flood_extent", data["artifacts"])
        self.assertIn("risk_assessment", data["artifacts"])
        self.assertEqual(data["final_answer"]["risk_level"], "high")

    def test_unknown_request_does_not_execute_tools(self):
        result = execute_agent("请执行一个完全未知的任务", {"provider": "mock"})
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["state"], "needs_clarification")
        self.assertEqual(result["data"]["results"], {})


class AgentApiTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_execute_endpoint(self):
        response = self.client.post(
            "/api/agent/execute",
            json={
                "message": "请分析贵港洪水并寻找受困人员",
                "mode": "hybrid",
                "params": {"provider": "mock"},
            },
        )
        body = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "success")
        self.assertEqual(body["data"]["state"], "completed")
        self.assertTrue(body["data"]["plan"])

    def test_unknown_message_does_not_run_tools(self):
        response = self.client.post(
            "/api/agent/execute",
            json={"message": "执行未知任务", "params": {"provider": "mock"}},
        )
        body = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["data"]["state"], "needs_clarification")
        self.assertEqual(body["data"]["results"], {})

    def test_tool_catalog_endpoint(self):
        response = self.client.get("/api/agent/tools")
        body = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body["status"], "success")
        self.assertIn("water_extract", {item["tool_id"] for item in body["data"]["tools"]})


if __name__ == "__main__":
    unittest.main()
