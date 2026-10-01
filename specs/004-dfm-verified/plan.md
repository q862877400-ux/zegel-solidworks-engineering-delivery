# Implementation Plan: DFM 复核升 `verified`

**Feature**: `004-dfm-verified` · **Spec**: [spec.md](spec.md)

**Created**: 2026-10-01 · **Status**: Implemented

---

## 一、与既有实现的关系（**不重造**）

本特性**不新增能力实现** —— DFM 的规则引擎**早已存在**：

| 已有模块 | 提供 | 规模 |
|---|---|---|
| `scripts/dfm_review.py` | `DFM_PROCESSES` / `PROCESS_ALIASES` / `UNIT_TO_MM` / `_document_to_mm` / `_manufacturing` / 规则判定与报告 | 42 处关键定义 |
| `scripts/dfm_profiles.py` | 供应商 **profile 能力交集** | 35 处关键定义 |
| `tests/test_dfm_review.py` | 既有回归 | 43 处命中 |
| `tests/test_dfm_queue_worker.py` | 队列工作器回归 | 13 处命中 |
| `mcp-server/` | `cadstudio_check_dfm` 工具（MCP 入口） | — |

⇒ 本特性**只做两件**：
1. **写一个端到端验收命令**（`tools/verify_dfm_e2e.py`），把 `spec.md` 的 SC-001..SC-008
   **逐条**变成可复跑的断言（**故意造违规**，不是"跑通就算"）；
2. **把 `capabilities.yaml` 的 `dfm_checks` 升 `verified`** 并补 `evidence` / `verified_versions`
   （**`limitations` 一条不删**）。

---

## 二、步骤（**先查证，再写**）

### 阶段 0 · 前提核查（**已完成**）
* `dependencies` 只有 `python` ⇒ 本机**不需要** `OCP`/`trimesh`（轮 79 实测确认）；
* 既有测试 **19 passed** ⇒ 实现本身是好的；
* `limitations` 三句已逐条读过（见 `spec.md` 第一节的表）。

### 阶段 1 · 摸清调用契约（**照测试抄，不臆造**）
要写验收命令，必须先知道**文档格式**与**报告字段**。做法：**从既有测试里抄**（那是唯一可靠来源），
**不去猜**：
* 文档形态：`dfm_review._load_document` 读 JSON；`manufacturing` 段 + `features` 段；
* 工艺：`DFM_PROCESSES = {machining, sheet_metal, laser_cutting, 3d_printing}`；
* 单位：`UNIT_TO_MM = {mm:1, cm:10, m:1000, inch:25.4, in:25.4}`。

### 阶段 2 · 写验收命令 `tools/verify_dfm_e2e.py`
* **每条 SC 一个 `chk(...)`**，逐条打印 ✓/✗，**最后 `verdict: pass|fail`**；
* ⚠ **判据要"故意造违规"**：删关键输入 / 篡改证据哈希 / 用窄 profile 收窄交集
  —— 看它们是否**真的**导致 `blocked` 或收窄；
* §四 的「不做」清单里写明：**只补证据，不改实现逻辑**（发现缺陷另开特性）。

### 阶段 3 · 跑 + 落证据
* `python tools/verify_dfm_e2e.py` ⇒ 期望 **`verdict: pass`**；
* 证据落 `D:\AI\SW\output\dfm-evidence.json`。

### 阶段 4 · 清单升级
* `dfm_checks.level`：`stitched` → **`verified`**；
* `evidence`：**命令 + 结果**（与 `costing` / `routing` 同型）；
* `verified_versions`：⚠ 本条**不依赖 SolidWorks、也不依赖 OCP** ⇒
  **不填 CAD 版本**；按 `dxf_preview_scene` 的先例填**依赖版本**（`ezdxf` 是间接依赖，
  但本条的规则引擎只用 `python` 标准库 + `numpy`）⇒ 填 **`['python 3.14.7']`**；
* `limitations`：**一条不删**。

### 阶段 5 · 门禁 + 回归 + 收工
```
python scripts/check_union_conventions.py     # R4：verified 必须有 evidence
python -m compileall -q tools scripts
python -m pytest tests -q                     # 回归
python scripts/release_check.py               # 12 道硬门禁
python scripts/gen_level_audit.py             # R8 生成物刷新
python tools/build_union_map.py               # 地图刷新
python tools/gen_harvest_digest.py            # 状态摘要刷新
```
⇒ **两仓库各自 commit**（代码副本 + 工作区 `specs/004-dfm-verified/`）。

---

## 三、风险与对策

| 风险 | 对策 |
|---|---|
| 验收命令里**臆造**文档字段 ⇒ 跑不通或测了个假的 | **从既有测试抄**格式；跑不通就回测试里找真形态（**不猜**）|
| 把「补证据」做成「改实现」⇒ 混淆两件事 | `spec.md §四` 明确写死：**本特性不改实现逻辑**；发现缺陷**另开特性** |
| 升级后**旧测试的红**被当成"测试过期"草率改掉 | 照轮 78 的做法：**先核升级依据是否充分**，再改期望，并**写明为什么** |
| 又一次"证据指向本机不存在的东西"（轮 77 那类） | **阶段 0 先核依赖**（本特性的 `dependencies` 只有 `python`）|

---

## 四、产物

| 文件 | 作用 |
|---|---|
| `tools/verify_dfm_e2e.py` | 端到端验收（SC-001..SC-008）|
| `D:\AI\SW\output\dfm-evidence.json` | 证据 |
| `capabilities.yaml`（`dfm_checks` 条目）| level / evidence / verified_versions |
| [tasks.md](tasks.md) · [converge.md](converge.md) | Spec Kit 的另两步 |
