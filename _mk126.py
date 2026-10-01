import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")

# ══════════ ① batch14 ══════════
BATCH = '''"""第十四批 MCP 工具声明：**视图读取 / 体上实体枚举** 2 个。

## 来源与筛选（2026-10-01 轮 207，Spec Kit `126`）

候选源：`D:/AI/SW/output/orphan-capabilities.json`（`tools/probe_unexposed_functions.py` 生成）。
队列 A3 原本列了 4 个（`get_active_view` / `activate_view` / `add_perspective` / `entities_on_body`），
★ **实测后只挂 2 个** —— 另外 2 个的**首参不是约定注入点**：

| 函数 | 真实签名（`inspect.signature`）| 首参 | 本批 |
|---|---|---|---|
| `sw_view.get_active_view` | `(model)` | `model` ✓ | **挂** |
| `sw_selection_spec.entities_on_body` | `(model, kind: str, *, body_index: int = 0)` | `model` ✓ | **挂** |
| `sw_view.activate_view` | `(view) -> bool` | ★ `view` **不在** `model`/`sw_app`/`study` 里 | **不挂** |
| `sw_view.add_perspective` | `(view) -> bool` | ★ 同上 | **不挂** |

## ⚠ 为什么另 2 个不挂（**记录理由，不硬挂**）
```
`activate_view` / `add_perspective` 要的是 **`IView` 对象**（`IModelDoc.ActiveView`），
而既有注入器只有 `""` / `"model"` / `"sw_app"` / `"study"` 四个 —— **没有 `view`**。
★ 而且实测：**既有 `tool_specs_batch*.py` 里没有任何"靠 model 取 view"的先例**可照抄。
⇒ 处置：**本批不挂**，把它记进队列 A10（"找第二类可挂形态"）——
   要么加一个 `view` 注入器（改基础设施），要么写"`model` → `ActiveView` → 调用"的**包装层**。
   ★ 两条路都要**先定行为**（`ActiveView` 在无活动文档/无视图时返回什么），不在本批顺手做。
```

| 不取 | 理由 |
|---|---|
| 真机验证这 2 个 | ★ **暴露 ≠ 验证** —— 排队列 B 组 |

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch14.py
# 定位:   「孤立能力暴露」第十四批（Spec Kit `126`）—— 视图读取 + 体上实体枚举。
# 官方签名依据: 不适用（只做参数搬运）；`kind` 的合法值取自 `sw_selection_spec.ENTITY_KINDS`（**本项目自己的常量**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH14"]

SPECS_BATCH14 = [
    ToolSpec(
        name="solidworks_get_active_view",
        title="Get Active View",
        module="sw_view", function="get_active_view",
        inject="model",
        doc="Get the currently active 3D view (the official member is IModelDoc.ActiveView).",
        params=[],
    ),
    ToolSpec(
        name="solidworks_entities_on_body",
        title="List Entities On Body",
        module="sw_selection_spec", function="entities_on_body",
        inject="model",
        doc="List the entities of one body (kind EDGE or FACE). "
            "⚠ Index order is NOT promised stable by the official API — do not treat "
            "body_index as a persistent reference across rebuilds.",
        params=[
            Param("kind", str,
                  description="Entity kind. Valid values (from sw_selection_spec.ENTITY_KINDS): "
                              "\\"EDGE\\" or \\"FACE\\"."),
            Param("body_index", int, default=0,
                  description="Zero-based solid-body index. ⚠ Not a persistent reference."),
        ],
    ),
]
'''
(W / "..").resolve()
Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch14.py").write_text(BATCH, encoding="utf-8")
print("  ok batch14 已写")

# ══════════ ② Spec Kit 126 五件套 ══════════
S = W / "specs" / "126-view-selection-batch"
S.mkdir(parents=True, exist_ok=True)

(S / "spec.md").write_text("""# Feature Specification: 视图读取 + 体上实体枚举（并**只挂可注入的那 2 个**）

**Feature Branch**: `126-view-selection-batch` · **Created**: 2026-10-01 · **Status**: Implemented

**Input**: 队列 A3（`docs/backlog-8h.md`）—— 原列 4 个，实测后**只挂 2 个**。

## 来源（§I / §IV）
| 需求 | 来源 | license |
|---|---|---|
| 暴露 `get_active_view` | **本项目自身**（包装 `scripts/sw_view.py`）| 本仓库 **MIT** |
| 暴露 `entities_on_body` | **本项目自身**（包装 `scripts/sw_selection_spec.py`）| 本仓库 **MIT** |
| `kind` 的合法值（`EDGE`/`FACE`） | **本项目自己的常量** `sw_selection_spec.ENTITY_KINDS` | 本仓库 **MIT** |
| 工具声明形状 | 既有 `tool_specs_batch7.py`（`inject="model"` 的先例）| 本仓库 **MIT** |

## User Scenarios & Testing

### User Story 1 - 让 AI 助手能读视图/枚举体上实体（Priority: P1）
用户要问"现在是什么视角"、"这块板上有几条边几个面"，现在只能写脚本。

**Independent Test**: 注册后 `all_specs()` 出现这 2 个名字，规则 1/2/3 门禁不拒。

**Acceptance Scenarios**:
1. **Given** 注册表已加载，**When** 调 `len(all_specs())`，**Then** 由 51 变 **53**
2. **Given** `entities_on_body`，**When** 传 `kind="EDGE"` 与 `kind="FACE"`，**Then** 都能被接受（`ENTITY_KINDS` 只有这两个）
3. **Given** `entities_on_body` 的描述，**When** 读它，**Then** 看到**序号不保证稳定**的警告（引自该函数 docstring）

### User Story 2 - 挂不了的要说清为什么（Priority: P2）
`activate_view` / `add_perspective` 在队列里，但本批**不挂** —— 这个决定必须留下理由与去处。

**Independent Test**: 读 `tool_specs_batch14.py` 头部，能看到"首参不是约定注入点"+"没有 `view` 注入器"+"记进 A10"。

**Acceptance Scenarios**:
1. **Given** 那两个函数，**When** 查它们的 `inspect.signature`，**Then** 首参是 `view`（**不在** `model`/`sw_app`/`study` 里）
2. **Given** 既有 `tool_specs_batch*.py`，**When** 搜 `ActiveView|sw_view`，**Then** **无先例** ⇒ 不能照抄

## 明确不做
| 不做 | 理由 |
|---|---|
| 挂 `activate_view` / `add_perspective` | ★ 需要 `view` 注入器或包装层 ⇒ 记进 A10，**先定行为** |
| 真机验证这 2 个 | ★ 暴露 ≠ 验证；排 B 组 |
""", encoding="utf-8")

(S / "plan.md").write_text("""# Implementation Plan: 视图读取 + 体上实体枚举

**Branch**: `126-view-selection-batch` | **Date**: 2026-10-01 | **Spec**: 同目录

## Technical Context
Python 3.14.7 · `tool_registry.Param/ToolSpec`（既有）· 本批不连 COM

## ★ 官方源与裁决顺序（§II）
| 源 | 用途 | 本次 |
|---|---|---|
| `scripts/sw_view.py` / `sw_selection_spec.py` 的函数签名与 docstring | 形参、返回值、注意事项 | `inspect.signature` + `inspect.getsource`（照实）|
| `sw_selection_spec.ENTITY_KINDS`（本项目常量）| `kind` 合法值 | `['EDGE','FACE']` |
| `IModelDoc.ActiveView`（官方属性）| `get_active_view` 的官方依据 | 该函数自己的来源块已写（**本批不引入新 COM 成员**）|
| `C:\\swapi\\types\\IModelDoc2\\ActiveView.md` 等 | 交叉核 | **本批未查**（不引入新成员 ⇒ 不必）；★ 如实记 |

**裁决顺序**：出厂类型库/反射 > `C:\\swapi` markdown > 本项目常量与来源块。

## ⚠ 查不到 / 做不到（§III）
```
① `activate_view` / `add_perspective` 要 `IView`，而**既有注入器没有 `view`**
   核查命令（可重跑）：
       python -c "import re;from pathlib import Path;t=Path(r'C:/swprojects/sw-skill-fork/mcp-server/tool_registry.py').read_text(encoding='utf-8');print(re.findall(r'\\"(model|sw_app|study|view)\\"\\s*:', t))"
   期望：只出现 model/sw_app/study（**没有 view**）
② 既有工具里**没有**"靠 model 取 view"的先例
   核查命令：见 tasks.md T-12602（期望**空**）
⇒ 处置：本批**不挂**这两个，记进队列 A10。
```

## Constitution Check（§I–§V）
| 条 | 判据 | 本次 |
|---|---|---|
| §I 来源 | 每条需求有来源 | ✅ |
| §II 官方源 | 列源 + 裁决序 | ✅（含"未查"的如实标注）|
| §III 查不到 | 附核查命令 | ✅ 两条命令 |
| §IV license | 来源行带 license | ✅ |
| §V 可跑验收 | 每条任务带 `→ 验收:` | ✅ |

## Project Structure
```
mcp-server/tool_specs_batch14.py    ← 新增 2 条
mcp-server/register_capabilities.py ← BATCH_MODULES +1
tests/test_server_wiring.py / test_mcp_protocol_layer.py ← 计数 51→53 · 96→98
```
""", encoding="utf-8")

(S / "tasks.md").write_text("""# Tasks: 视图读取 + 体上实体枚举

- [x] T-12601 ★ 核"哪些真能挂"（首参是否约定注入点）
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\\swprojects\\sw-skill-fork\\scripts'];import inspect,sw_view as v;print(inspect.signature(v.get_active_view), inspect.signature(v.activate_view))"`
  （期望 `(model)` 与 `(view) -> bool` ⇒ **后者不挂**）
- [x] T-12602 ★ 核"有没有 view 包装的先例"（**期望空**）
  `→ 验收:` `Select-String -Path C:\\swprojects\\sw-skill-fork\\mcp-server\\tool_specs_batch*.py -Pattern 'ActiveView|sw_view'`（**空**）
- [x] T-12603 写 `tool_specs_batch14.py` + 注册
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\\swprojects\\sw-skill-fork\\mcp-server',r'C:\\swprojects\\sw-skill-fork'];import register_capabilities as rc;print(len(rc.all_specs()))"`（**53**）
- [x] T-12604 两处计数同步（51→53 · 96→98）
  `→ 验收:` `python -m pytest tests/test_server_wiring.py tests/test_mcp_protocol_layer.py -q`（0 failed）
- [x] T-12605 五处口径一致动 2
  `→ 验收:` `python tools/probe_unexposed_functions.py` + `python tools/build_union_map.py`
- [x] T-12606 全链 + 回归
  `→ 验收:` `python scripts/release_check.py`（exit 0）· `python -m pytest tests -q`（0 failed）
""", encoding="utf-8")

(S / "checklist.md").write_text("""# Checklist: 视图读取 + 体上实体枚举

- [x] 规则 1：两名都带 `solidworks_` 前缀
- [x] 规则 2：无长度/角度参数
- [x] 规则 3：无裸坐标
- [x] ★ 参数名与目标函数真名一致（`kind` / `body_index`）
- [x] ★ `kind` 的合法值**从常量读**（`ENTITY_KINDS`），**不手抄**
- [x] ★ 把该函数的**"序号不稳定"警告**搬进工具描述（不许把它丢掉）
- [x] ★ **挂不了的写明理由与去处**（A10），**不硬挂**
- [x] 计数类测试同步更新
- [x] 不声称真机验证
- [x] 特性目录写完不再改（Flow-forward）
""", encoding="utf-8")

(S / "converge.md").write_text("""# Converge: 视图读取 + 体上实体枚举

## 结果
| 判据 | 结论 |
|---|---|
| 注册数 51 → **53**（★ 队列说 4 个，**实测只挂 2 个**）| ✅ |
| `kind` 合法值从常量读 | ✅ `['EDGE','FACE']` |
| "序号不稳定"警告搬进描述 | ✅ |
| 另 2 个**不挂**且写明理由与去处 | ✅ |
| 规则 1/2/3 | ✅ |
| 两处计数同步（51→53 · 96→98）| ✅ |
| 五处口径一致动 2 | ✅ |
| 全链 + 回归 | ✅ |

## ★ 未查证
* ⚠ **没跑真机**（暴露 ≠ 验证）；
* ⚠ `C:\\swapi` 里 `ActiveView` 的 markdown **本批没查**（不引入新成员 ⇒ 非必需）——
  ★ 若将来要包装 `view`，**那时必须查**（A10）；
* ⚠ `activate_view` / `add_perspective` 在**无活动文档**时的行为**未定** ⇒ 那是 A10 做包装层前必须先落的事。
""", encoding="utf-8")
print("  ok Spec Kit 126 五件套已写")
