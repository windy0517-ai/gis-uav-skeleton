# 项目 README

```text
  ___   _____  ___    _   _    _
 |_ _| |___  |/ _ \  | \ | \  / |
  | |     / /| | | | |  \| |\/| |
  | |    / / | |_| | | |\  |  | |
 |___|  /_/   \___/  |_| \_|  |_|

 无人机洪涝应急决策系统
```

## 快速开始

### 1. 安装依赖

```bash
# 推荐用 conda 创建独立环境
conda create -n gis-uav python=3.9
conda activate gis-uav

# 安装 Python 依赖
cd backend
pip install -r requirements.txt
```

### 2. 启动后端

```bash
cd backend
python app.py
```

看到以下输出表示启动成功：
```
=======================================================
  翼澜系统后端已启动！
  API 地址: http://localhost:5000
  健康检查: http://localhost:5000/api/hello
=======================================================
```

### 3. 打开前端

在浏览器直接打开 `frontend/public/index.html`

或通过后端访问：http://localhost:5000

### 4. 验收

| 检查项 | 验证方法 | 预期结果 |
|:-------|:---------|:---------|
| 后端运行 | `curl http://localhost:5000/api/hello` | 返回 JSON `{"message":"Hello!..."}` |
| 前端显示 | 浏览器打开 index.html | 看到三维地图和暗色界面 |
| 联调通过 | 前端点"检测后端"按钮 | 显示"后端已连接" |
| 场景执行 | 点任意场景按钮 | 日志区显示执行步骤 |

### 5. 运行骨架测试

```bash
cd backend
python -m unittest discover -s tests -v
```

测试使用 `provider: "mock"`，不要求先安装真实AI模型或连接MapGIS。

---

## 项目结构

```
gis-uav-skeleton/
├── backend/                          # Python 后端
│   ├── app.py                        # 主入口（已写好，直接运行）
│   ├── requirements.txt              # 依赖列表
│   ├── core/                         # 统一响应契约
│   │   └── contracts.py
│   ├── routes/                       # API 路由（已搭好骨架）
│   │   ├── water_extract.py          # 水体提取 API
│   │   ├── path_plan.py              # 路径规划 API
│   │   ├── object_detect.py          # 目标识别 API
│   │   ├── orchestrator.py           # 编排 Agent API
│   │   └── gis_analysis.py           # GIS 分析 API
│   ├── services/                     # 工具服务与算法适配
│   │   ├── tool_services.py          # 稳定工具入口（接入点）
│   │   ├── workflow_engine.py        # 唯一场景注册表与编排器
│   │   ├── mock_data.py               # 稳定Mock数据
│   │   ├── ndwi_extractor.py         # 🔴 A: 水体提取算法
│   │   ├── path_planner.py           # 🔴 A: 路径规划算法
│   │   ├── color_detector.py         # 🔴 A/B: 颜色检测
│   │   ├── igs_client.py             # 🔴 C: IGServer 客户端
│   │   └── rule_engine.py            # 🔴 A/D: 规则引擎
│   ├── agents/                       # 自然语言 Agent 与计划校验
│   │   ├── emergency_agent.py        # Agent 主流程
│   │   ├── rule_planner.py           # 本地规则规划器
│   │   ├── schemas.py                # 计划结构和校验
│   │   └── tool_registry.py          # 工具白名单
│   ├── mock/                         # Mock 数据
│   └── data/                         # 数据文件（C 下载到这里）
│       ├── sar/                      # SAR 影像
│       ├── geojson/                  # GeoJSON 文件
│       └── dem/                      # 地形数据
│
└── frontend/                         # 前端
    └── public/
        └── index.html                # ✅ 完整可用的三维指挥中心
```

## 当前骨架的接入方式

系统采用“路由 → 工具服务 → 算法/外部适配器”的轻量结构，不引入微服务、消息队列或复杂Agent框架。

- `backend/routes/`：只处理HTTP请求和响应。
- `backend/services/tool_services.py`：每个功能的稳定工具入口，队员完成算法后接入这里。
- `backend/services/workflow_engine.py`：五个固定MVP场景的唯一注册表和同进程编排器。
- `backend/core/task_context.py`：共享任务上下文、成果物和运行指标。
- `backend/services/mock_data.py`：当前骨架的稳定演示数据。
- `backend/core/contracts.py`：统一响应格式和HTTP状态转换。
- `docs/api_contract.md`：前后端联调必须遵守的接口契约。

默认使用 `provider: "mock"`，因此队员可以先完成接口和前端联调；算法完成后，把请求改为 `provider: "real"`，不需要重写前端或场景编排。

系统同时提供可选的自然语言 Agent：

```text
POST /api/agent/execute
{"message":"分析洪涝并寻找受困人员", "mode":"hybrid", "params":{"provider":"mock"}}
```

第一版使用本地规则规划器生成工具计划，不依赖真实大模型 API。Agent 会经过工具白名单和步骤数校验后，复用现有 `run_tool()` 执行工具；无法识别的任务会要求补充说明，不会盲目执行。

工作流结果会登记为稳定成果物，例如 `flood_extent`、`inspection_route`、`detected_objects`、`risk_assessment`。后续算法只替换成果物的生成方式，不改变成果物名称。

---

## 各成员的工作入口

### 🔴 A（算法/后端）

| 文件 | 要做什么 |
|:-----|:---------|
| `backend/services/ndwi_extractor.py` | 实现 NDWI/SDWI 水体提取算法 |
| `backend/services/path_planner.py` | 实现 A* 路径规划 + 牛耕式覆盖 |
| `backend/services/color_detector.py` | 实现颜色目标检测（可选） |
| `backend/services/rule_engine.py` | 实现规则引擎编排 |

**验证方法**：
```bash
cd backend
python services/ndwi_extractor.py    # 测试水体提取
python services/path_planner.py      # 测试路径规划
```

**参考资源**：
- https://github.com/deepakpraja/floodmap — 水体提取(50行)
- https://github.com/AtsushiSakai/PythonRobotics — A*路径规划
- https://github.com/codediaz/experta — 规则引擎

---

### 🟡 B（前端/三维）

| 文件/位置 | 要做什么 |
|:----------|:---------|
| `frontend/public/index.html` | 修改界面样式、布局、配色 |
| `frontend/public/index.html` 的 `initCesium()` | 加载真实数据到三维场景 |
| `frontend/public/index.html` 中调用 API 的部分 | 对接 A 的后端 API |

**验证方法**：
在浏览器直接打开 `frontend/public/index.html`，看到三维地图和暗色界面即成功。

**参考资源**：
- http://webclient.smaryun.com — MapGIS 官方 3D Demo
- https://github.com/ShenTiger/Cesium-Examples — Cesium 200+ 示例
- https://blog.csdn.net/qq_33224313/article/details/155948019 — MapGIS Cesium教程

---

### 🟢 C（数据/后端）

| 文件/位置 | 要做什么 |
|:----------|:---------|
| `backend/data/sar/` | 下载广西郁江 Sentinel-1 SAR 影像 |
| `backend/data/dem/` | 下载 DEM 地形数据 |
| `backend/services/igs_client.py` | 配置 MapGIS IGServer 连接 |
| `backend/routes/gis_analysis.py` | 替换 mock 为真实 IGServer 调用 |

**参考资源**：
- https://search.asf.alaska.edu — ASF 数据下载
- https://blog.csdn.net/qq_33224313/article/details/154487834 — IGServer 叠置分析教程
- https://github.com/MapGIS/WebClient-JavaScript — MapGIS 官方 SDK

---

### 🔵 D（文档/协调）

| 文件/位置 | 要做什么 |
|:----------|:---------|
| `docs/`（需要创建） | 写设计说明书、用户手册 |
| 全局 | 测试所有人联调、录演示视频、催进度 |

> **每日任务**：截图存档（每天截一张系统运行界面）
> **关键节点**：
> - 7月28日：确认 3D license 回复
> - 9月28日：功能评估（哪些能砍）
> - 10月4-5日：录演示视频
> - 10月10日：提交

---

## 开发规则

### 第一步：注册 GitHub

如果你还没有 GitHub 账号，现在注册：

1. 访问 https://github.com  → 点 **Sign up**
2. 输入邮箱 → 设密码 → 验证邮箱
3. 记住你的用户名（之后每次操作都要用到）

### 第二步：建仓库（A来做）

A 在 GitHub 上创建一个仓库，作为团队的代码中心：

1. 登录 GitHub，点右上角 + → **New repository**
2. **Repository name**: `gis-uav-path`
3. 勾选 **Public**（所有人能看）
4. 勾选 **Add a README file**
5. 点 **Create repository**

### 第三步：所有人都能访问

A 把团队成员加为 collaborator（协作者）：

1. 进仓库 → Settings → Collaborators → Add people
2. 搜索队友的 GitHub 用户名或邮箱 → 添加
3. 队友会收到邮件邀请 → 点接受

### 第四步：每个人把代码克隆到本地（第一次做一次）

```bash
# 打开终端（CMD 或 Git Bash）
cd 桌面  # 或你想放代码的地方

# 克隆仓库到本地
git clone https://github.com/A的账户名/gis-uav-path.git

# 进入项目目录
cd gis-uav-path
```

完成后，你会在本地看到一个叫 `gis-uav-path` 的文件夹。

### 第五步：日常开发流程（每天必做）

把本地的文件改动同步到 GitHub 上，只需要以下命令：

```bash
# ── 早上第一件事：拉取队友最新的代码 ──
git pull

# ── 完成自己的任务后：提交到 GitHub ──
# 把做了改动的文件标记为"待提交"
git add .

# 提交到本地，附上说明文字（让别人知道改了啥）
git commit -m "A: 实现了NDWI水体提取"

# 推送到 GitHub（其他人才看得到）
git push
```

**每天结束前必须 push 一次**，哪怕只改了 2 行代码。

### 第六步：第一次把骨架代码推上去（A来做）

A 需要把整个项目骨架放到 GitHub 上：

```bash
# 打开骨架文件夹
cd d:/GIS\ develop/gis-uav-skeleton

# 初始化 Git
git init

# 关联远程仓库
git remote add origin https://github.com/A的账户名/gis-uav-path.git

# 把所有文件添加到跟踪
git add .

# 提交
git commit -m "feat: 系统骨架 v0.1 — 含Flask后端+Cesium前端+算法桩代码"

# 推送到 GitHub
git push -u origin main
```

其他队员再次 `git pull` 就能拉到所有文件了。

### 第七步：各自开分支（可选，推荐）

每个人在自己分支上开发，互不干扰：

```bash
# A创建自己的分支
git checkout -b dev-a

# B创建自己的分支
git checkout -b dev-b
# 以此类推...

# 每天流程变这样
git add .
git commit -m "A: NDWI算法实现完成"
git push -u origin dev-a   # 推到自己分支

# 想让你的代码被合并到主分支？在 GitHub 上发起 Pull Request
# D 负责 Review 并合并
```

**简化版**：如果觉得分支概念太复杂，所有人都往 `main` 分支推也可以，但要保证：
1. 改自己的文件，别改别人的
2. `git pull` 一定要在 `git push` 之前执行
3. 如果提示冲突，先别慌，截图发群里

### 不想记命令？用 GitHub Desktop（图形界面）

如果记不住 git 命令，可以装 GitHub Desktop，用鼠标点一点就能完成全部操作：

1. 下载：https://desktop.github.com
2. 安装后登录你的 GitHub 账号
3. 点 **File → Clone Repository** → 选择 `你队友的账户名/gis-uav-path`
4. 修改文件后，GitHub Desktop 会自动显示改动
5. 在左下角写提交信息（如"A: 实现了水体提取"）
6. 点 **Commit to main**
7. 点 **Push origin** → 完成

**只需要这 4 个按钮**：Clone / Commit / Push / Pull。

### 第一次验收：确认所有人都能协作

按以下步骤验证 Git 协作流程走通了：

1. A 把骨架代码推上 GitHub（按第六步操作）
2. B 运行 `git clone https://github.com/A的账户名/gis-uav-path.git` 拉到本地
3. B 修改 `README.md`，在底部加上一行 `- B: 环境就绪`
4. B 运行 `git add .` → `git commit -m "B: 环境就绪"` → `git push`
5. A 运行 `git pull` 看到 B 的改动
6. C 和 D 重复 2-5 步

全员都能 push 和 pull 成功 → ✅ Git 协作流程通了。

### 项目结构提交到 GitHub 后的样子

```
gis-uav-path/
├── backend/
│   ├── app.py                # A 启动后端用
│   ├── requirements.txt      # 所有人装依赖用
│   ├── routes/               # API 路由（不用动）
│   │   ├── water_extract.py
│   │   ├── path_plan.py
│   │   ├── object_detect.py
│   │   ├── orchestrator.py
│   │   └── gis_analysis.py
│   └── services/             # 🔴 各人填自己代码的地方
│       ├── ndwi_extractor.py   # A: 水体提取算法
│       ├── path_planner.py     # A: 路径规划算法
│       ├── color_detector.py   # A/B: 颜色检测
│       ├── igs_client.py       # C: IGServer 连接
│       └── rule_engine.py      # A/D: 规则引擎
├── frontend/
│   └── public/
│       └── index.html         # B: 前端界面
└── README.md                  # D: 项目文档
```

| 问题 | 原因 | 解决方法 |
|:-----|:-----|:---------|
| `git push` 提示没权限 | 没接受 collaborator 邀请 | 去邮箱点链接接受，或让 A 重新邀请 |
| `git push` 被拒绝 | 本地比远程旧（别人先推了） | `git pull` 后再 `git push` |
| `git pull` 提示冲突 | 你和别人改了同一个文件的同一行 | 截图发群里，队友帮你解决 |
| `git commit` 后想撤回 | 提交信息写错了 | `git commit --amend -m "新信息"` |
| 忘记 `git add` 就直接 commit | 改的文件没被包含 | 重新 `git add .` 然后 `git commit` |

### 提交信息格式

```bash
# 好的例子
git commit -m "A: 实现了NDWI水体提取算法"
git commit -m "B: 修改了三维地图配色方案"
git commit -m "C: 配置了IGServer连接"
git commit -m "D: 写了设计说明书第一章"
git commit -m "feat: 前端联调后端API成功"

# 不好的例子
git commit -m "改了点东西"      # 别人看不懂改了啥
git commit -m "fix"             # 太模糊
git commit -m "最后版本"        # 没有"最后版本"
```

### 卡住怎么办

```
卡住了（30分钟没进展）
    ↓
截图报错信息 → 发群里
    ↓
队友帮忙 或 百度/Google 搜报错信息
    ↓
30分钟后还是不行 → 找我（A）协调
```

### API 接口规范

所有 API 统一格式：
```json
// 请求
POST /api/xxx
{"参数1": "值1", "参数2": "值2"}

// 响应
{"status": "success", "data": {...}, "meta": {...}, "error": null}
{"status": "error", "data": null, "meta": {...}, "error": {"code": "...", "message": "错误说明"}}
```

完整字段和各模块输入输出见 `docs/api_contract.md`。不要在路由文件中直接新增算法逻辑或固定业务结果。

---

## 进度追踪

| 里程碑 | 截止 | 检查标准 |
|:-------|:----|:---------|
| ✅ 环境就绪 | 7月23日 | 所有人能运行 hello.py |
| ✅ 后端主线 | 7月28日 | 后端 API 全部可调，返回数据 |
| ✅ 三维场景 | 7月28日 | Cesium 三维地图加载 mock 数据 |
| 🔄 前后端联调 | 9月15日 | 前端调后端 API 显示真实数据 |
| 🔄 全链路完成 | 9月28日 | 按钮→算法→显示的完整流程 |
| 🔄 提交 | 10月10日 | 全部材料上传 |
