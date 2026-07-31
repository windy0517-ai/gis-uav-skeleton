# 翼澜系统接口契约

## 设计原则

- 路由只负责HTTP请求，不写算法逻辑。
- 工具函数在 `backend/services/tool_services.py` 中提供稳定入口。
- 队员可以替换工具的真实实现，但不应改变返回字段。
- `provider` 支持三种模式：`mock`、`real`、`auto`。
- `mock` 是当前默认模式，保证骨架随时可运行；`real` 用于模块完成后的接入；`auto` 允许失败时按项目降级策略回退。

## 统一响应格式

成功：

```json
{
  "status": "success",
  "data": {},
  "meta": {
    "module": "water_extract",
    "algorithm": "sdwi",
    "provider": "mock",
    "processing_time_ms": 1.2,
    "timestamp": "2026-07-25T00:00:00+00:00"
  },
  "error": null
}
```

失败：

```json
{
  "status": "error",
  "data": null,
  "meta": {"module": "water_extract"},
  "error": {
    "code": "WATER_EXTRACT_FAILED",
    "message": "错误说明"
  }
}
```

## 工具接口

### `POST /api/water/extract`

输入示例：

```json
{
  "image_path": "data/sar/guigang_s1.tif",
  "provider": "mock",
  "algorithm": "sdwi"
}
```

`data` 至少包含 `geojson`；真实算法可增加 `area_km2`、`confidence` 等统计字段。

### `POST /api/path/plan`

输入示例：

```json
{
  "start": [109.55, 23.05],
  "goal": [109.65, 23.10],
  "coverage_polygon": null,
  "no_fly_zones": [],
  "grid_size_m": 30,
  "provider": "mock"
}
```

`data` 至少包含 `route`（GeoJSON FeatureCollection）。

### `POST /api/detect/objects`

输入示例：

```json
{
  "image_path": "data/uav_images/sample.jpg",
  "provider": "mock"
}
```

`data` 至少包含 `geojson` 和 `counts`。

### `POST /api/gis/overlay`

输入示例：

```json
{
  "layer1_gdbp": "gdbp://.../flood_extent",
  "layer2_gdbp": "gdbp://.../buildings",
  "over_type": 1,
  "provider": "mock"
}
```

`data` 至少包含 `stats`。

### `POST /api/orchestrator/execute`

输入示例：

```json
{
  "scenario": "flood_recon",
  "params": {"provider": "mock", "region": "guigang"}
}
```

场景执行结果中的 `data.results` 保存每个工具的结果：

```text
results.water_extract
results.path_plan
results.gis_overlay
results.object_detect
results.stats
```

前端只读取这些约定字段，不依赖具体算法名称。

## 工作流上下文与成果物

每个工作流完成后，`data` 中还会返回：

```json
{
  "state": "completed",
  "artifacts": {
    "flood_extent": {},
    "inspection_route": {},
    "detected_objects": {},
    "affected_stats": {},
    "risk_assessment": {},
    "decision_metrics": {}
  },
  "metrics": {}
}
```

成果物名称保持稳定，算法实现可以替换，但不能改变其用途。例如水体算法始终产生 `flood_extent`，路径规划算法始终产生 `inspection_route`。

## 任务状态

当前版本采用同步执行，但仍返回任务状态，方便后续扩展：

```text
running → completed
       ↘ failed
```

`GET /api/orchestrator/tasks/{task_id}` 可查询已完成任务的结果。

## Agent 接口

### `POST /api/agent/execute`

第一版 Agent 使用本地规则规划器，不依赖真实大模型 API。Agent 只允许调用工具白名单中的工具，并复用现有 `TaskContext`、`run_tool()` 和成果物登记机制。

请求示例：

```json
{
  "message": "请分析贵港洪涝情况，重点寻找受困人员，并规划巡检路线",
  "mode": "hybrid",
  "params": {
    "region": "guigang",
    "provider": "mock"
  }
}
```

返回结果中的 `data` 至少包含：

```text
task_id
mode
goal
plan
state
results
artifacts
final_answer
logs
metrics
```

Agent 计划中的 `tool_id` 必须属于以下白名单：

```text
water_extract
path_plan
object_detect
gis_overlay
gis_simulate
risk_assess
stats
generate_report
```

任务查询：

```http
GET /api/agent/tasks/{task_id}
```

工具目录：

```http
GET /api/agent/tools
```

无法识别自然语言任务时，接口返回 `status=success`、`state=needs_clarification`，但不会执行任何工具。

## 风险评估

`risk_assess` 当前是可解释规则占位工具，输出：

- `risk_level`：`high` / `medium` / `low`
- `reasons`：触发风险等级的依据
- `recommended_action`：行动建议
- `confidence`：规则结果置信度

后续可以替换为模型或更复杂的空间分析，而不影响前端契约。
