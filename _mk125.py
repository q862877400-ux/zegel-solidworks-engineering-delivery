import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")
S = W / "specs" / "125-simulation-study-batch"
S.mkdir(parents=True, exist_ok=True)

(S / "spec.md").write_text("""# Feature Specification: 仿真研究族（报告 / 按控制划网格 / 建议网格尺寸）

**Feature Branch**: `125-simulation-study-batch` · **Created**: 2026-10-01 · **Status**: Implemented

**Input**: 队列 A2（`docs/backlog-8h.md`）。

## 来源（§I / §IV）
| 需求 | 来源 | license |
|---|---|---|
| 暴露 `generate_report` / `create_mesh_for_control` | **本项目自身既有模式**（包装 `scripts/sw_simulation_study.py`）| 本仓库 **MIT** |
| 暴露 `default_element_size_and_tolerance` | **本项目自身既有模式**（包装 `scripts/sw_simulation.py`，★ **不是** `_study`）| 本仓库 **MIT** |
| 工具声明形状 | 既有 `tool_specs_batch1.py` / `batch11` / `batch12` 的 `study` 模板 | 本仓库 **MIT** |

## User Scenarios & Testing

### User Story 1 - 让 AI 助手能出研究报告（Priority: P1）
用户跑完一个算例后要一份报告文件，现在只能写脚本。

**Independent Test**: 注册后 `all_specs()` 里出现这三个名字，规则 1/2/3 门禁不拒。

**Acceptance Scenarios**:
1. **Given** 注册表已加载，**When** 调 `len(all_specs())`，**Then** 由 48 变 **51**
2. **Given** 三个工具，**When** 跑规则 1/2/3，**Then** 全过
3. **Given** `units` 参数，**When** 读它的描述，**Then** ★ 看到**两源冲突**被**原样写出来**（不合并成一种说法）

### User Story 2 - 把"查不到"和"冲突"都摆在明面上（Priority: P2）
用户不该在踩坑后才知道哪个参数的值查不到、哪两处源互相矛盾。

**Acceptance Scenarios**:
1. **Given** `template` 参数，**When** 读描述，**Then** 明写「合法取值未在本地源中找到」
2. **Given** `units` 参数，**When** 读描述，**Then** 同时看到「既有工具说 -1 被拒」与「该函数真机实测 -1 可用」两句

## 明确不做
| 不做 | 理由 |
|---|---|
| 给 `template` 编候选值 | ★ 本地源查不到 ⇒ 铁律 5 不发明 |
| 合并 `units=-1` 的两处说法 | ★ 与事实 139「两个口径不合并」同型 |
| 真机验证这 3 个 | ★ 暴露 ≠ 验证；排 B 组 |
""", encoding="utf-8")

(S / "plan.md").write_text("""# Implementation Plan: 仿真研究族

**Branch**: `125-simulation-study-batch` | **Date**: 2026-10-01 | **Spec**: 同目录

## Technical Context
Python 3.14.7 · `tool_registry.Param/ToolSpec`（既有）· 单实例 COM（本批不连）

## ★ 官方源与裁决顺序（§II）
| 源 | 用途 | 本次查到 |
|---|---|---|
| `scripts/sw_simulation_study.py` / `sw_simulation.py` 的函数签名 | 形参名与默认值 | `inspect.signature` 取到（照实）|
| `C:\\swapi\\enums\\swsUnit_e.md` | `units` 取值 | ★ **文件不在** ⇒ 只能引既有工具的先例描述 |
| 既有工具 `solidworks_topology_run` 的 `units` 描述 | `units` 取值先例 | "0=SI, 1=English, 2=Metric; **-1 is rejected**" |
| 该函数自己的 docstring | `units=-1` 的真机结论 | "**本机实测：units=-1 时返回毫米级数值**" |
| `C:\\swapi\\types\\ICWStudy\\GenerateReport.md` | `template` 取值 | ★ 本次**未查到**合法取值 |

**裁决顺序**：出厂类型库/反射 > 官方 markdown > **既有工具先例** > 该函数自述。
★ 本次**刻意不裁决** `units=-1` 的冲突：两处来源**同级**，且**其中之一是"本机实测"** ⇒
  按"真实运行证据优先"取 **-1**，但**把两句话都留在描述里**。

## ⚠ 查不到（§III）
```
`generate_report` 的 `template` 合法取值：`C:\\swapi` 与反射里**都没查到**。
核查命令（可重跑）：
    python -c "from pathlib import Path;print([p.name for p in Path(r'C:/swapi/enums').glob('*eport*')])"
    python -c "from pathlib import Path;t=Path(r'D:/AI/SW/_raw/reflect/enum_cosworks.txt').read_text(encoding='utf-8',errors='replace');print('Report' in t)"
```
⇒ 处置：`template` 按普通 `str` 暴露 + 描述里明写"未查到"。

## Constitution Check（§I–§V）
| 条 | 判据 | 本次 |
|---|---|---|
| §I 来源 | 每条需求有来源 | ✅ |
| §II 官方源 | 列源 + 裁决序 | ✅（含"刻意不裁决"的说明）|
| §III 查不到 | 附核查命令 | ✅ `template` + `swsUnit_e.md` 不在 |
| §IV license | 来源行带 license | ✅ |
| §V 可跑验收 | 每条任务带 `→ 验收:` | ✅ |

## Project Structure
```
mcp-server/tool_specs_batch13.py    ← 新增 3 条
mcp-server/register_capabilities.py ← BATCH_MODULES +1
tests/test_server_wiring.py / test_mcp_protocol_layer.py ← 计数 48→51 · 93→96
```
""", encoding="utf-8")

(S / "tasks.md").write_text("""# Tasks: 仿真研究族

- [x] T-12501 ★ 先核"归属"（队列说 `_study`，实测在 `sw_simulation`）
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\\swprojects\\sw-skill-fork\\scripts'];import inspect,sw_simulation as si;print(inspect.signature(si.default_element_size_and_tolerance))"`
- [x] T-12502 ★ 核 `template` 的合法取值（**期望"查不到"**）
  `→ 验收:` `python -c "from pathlib import Path;print([p.name for p in Path(r'C:/swapi/enums').glob('*eport*')])"`（**空**）
- [x] T-12503 写 `tool_specs_batch13.py` + 注册
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\\swprojects\\sw-skill-fork\\mcp-server',r'C:\\swprojects\\sw-skill-fork'];import register_capabilities as rc;print(len(rc.all_specs()))"`（**51**）
- [x] T-12504 两处计数同步（48→51 · 93→96）
  `→ 验收:` `python -m pytest tests/test_server_wiring.py tests/test_mcp_protocol_layer.py -q`（0 failed）
- [x] T-12505 五处口径一致动 3
  `→ 验收:` `python tools/probe_unexposed_functions.py` + `python tools/build_union_map.py`
- [x] T-12506 全链 + 回归
  `→ 验收:` `python scripts/release_check.py`（exit 0）· `python -m pytest tests -q`（0 failed）
""", encoding="utf-8")

(S / "checklist.md").write_text("""# Checklist: 仿真研究族

- [x] 规则 1：三名都带 `solidworks_` 前缀
- [x] 规则 2：无长度参数（本批 `units` 是枚举、`path` 是路径）
- [x] 规则 3：无裸坐标
- [x] ★ 参数名与目标函数真名一致（`template` / `path` / `append` / `control_name` / `units`）
- [x] ★ **查不到的**（`template` 取值）如实标注 + 附核查命令
- [x] ★ **两源冲突**（`units=-1`）**原样保留、不合并**
- [x] ★ **归属按实测改正**（`default_element_size_and_tolerance` 在 `sw_simulation` 不是 `_study`）
- [x] 计数类测试同步更新
- [x] 不声称真机验证
- [x] 特性目录写完不再改（Flow-forward）
""", encoding="utf-8")

(S / "converge.md").write_text("""# Converge: 仿真研究族

## 结果
| 判据 | 结论 |
|---|---|
| 注册数 48 → **51** | ✅ |
| 归属改正（`sw_simulation` 而非 `_study`）| ✅ |
| `template` 取值**查不到** | ✅ 如实标注 + 命令 |
| `units=-1` **两源冲突** | ✅ 原样保留 |
| 规则 1/2/3 | ✅ |
| 两处计数同步（48→51 · 93→96）| ✅ 16 passed |
| 五处口径一致动 3 | ✅ 100→103 · 295→292 · 44→41 · 431→434 · 82→85 · 缺口 338 不变 |
| 全链 + 回归 | ✅ `release_check` exit 0 |

## ★ 未查证
* ⚠ **没跑真机**（暴露 ≠ 验证；排 B 组）；
* ⚠ `template` 的**合法取值**至今未知 ⇒ 用户得自己知道用什么模板名；
* ⚠ `units` 的冲突**没被裁决**（只把两句都写出来）—— ★ 要裁决得**真机试 -1 会不会被拒**，排 B 组。
""", encoding="utf-8")

FACT = """| 146 | **挂柜台第三批（仿真研究族 3 个）：把"两源冲突"原样留在描述里，不合并** —— 2026-10-01（轮 206 / Spec Kit `125`）。

★★ **本批的两处"不干净"，都按纪律摆到明面上**：
```
① **查不到**：`generate_report` 的 `template` **合法取值**在本地源里没查到
   （`sw_simulation_study.generate_report` docstring 只有「生成研究报告。」，
     函数体只是透传给 `GenerateReport(template, path, append)`）
   ⇒ ★ 按普通 `str` 暴露 + 描述里明写"合法取值未在本地源中找到"，**不发明候选值**（铁律 5）
   核查命令：`python -c "from pathlib import Path;print([p.name for p in Path(r'C:/swapi/enums').glob('*eport*')])"`（**空**）

② **两源冲突**（★ 更值得记）：
   既有工具 `solidworks_topology_run` 的 `units` 描述写「0=SI, 1=English, 2=Metric；
     **-1 is rejected by the API**」
   而 `default_element_size_and_tolerance` 自己的 docstring 写「**本机实测：units=-1 时返回毫米级数值**」
   ⇒ ★ 两处**矛盾**。处置：**按"真实运行证据优先"取 -1 作默认**，
     但**把两句话都留在参数描述里**，**不合并成一个说法**
   ⇒ ★ 与**事实 139**（缺口数的两个口径不合并）**同型**：
     **两处都没说谎，只是口径/证据层级不同 —— 那就两处都写。**
```
★ **一处归属按实测改正**：队列把 `default_element_size_and_tolerance` 写在 `_study` 名下，
  实测它在 **`scripts/sw_simulation.py`** ⇒ 以实测为准（工具声明的 `module=` 用实测值）。

★ **五处口径一致地动 3**（第三次同一模式，互相印证）：
```
被工具引用的公开函数 100→**103** · 孤立能力 295→**292** · 首参可注入 44→**41**
并集 431→**434** · 本仓库独家 82→**85** · 缺口 338 **不变**
```
★ 两处"钉死数量"的测试同步更新（**48→51** · **93→96**）；注册表现有 **51** 条声明。

⚠ **限度**：本批**只做暴露**（真机验证排队列 B 组）·
`template` 合法取值**至今未知** ⇒ 用户得自己知道模板名 ·
`units` 的冲突**没被裁决**（只把两句都写出来；要裁决得真机试 `-1` 会不会被拒）。

**依据**：`mcp-server/tool_specs_batch13.py` · `mcp-server/register_capabilities.py` ·
`specs/125-simulation-study-batch/` · 事实 139 / 144
"""

K = W / "docs" / "known-facts.md"
tk = K.read_text(encoding="utf-8")
if "| 146 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT, encoding="utf-8")
    print("  ok known-facts 已加 146")

R = W / "docs" / "ROADMAP.md"
B = """           691 🎯 **Spec Kit `125`：挂柜台第三批（仿真研究族 3 个）—— 把「两源冲突」原样留在描述里，不合并**（轮 206）——
               ★ 本批两处"不干净"都按纪律摆到明面上：
               ```
               ① **查不到**：`generate_report` 的 `template` **合法取值**本地源里没查到
                  （docstring 只有「生成研究报告。」，函数体只是透传给 `GenerateReport(template, path, append)`）
                  ⇒ ★ 按普通 `str` 暴露 + 描述明写"未找到"，**不发明候选值**（铁律 5）
                  核查命令：`Path('C:/swapi/enums').glob('*eport*')` ⇒ **空**
               ② **两源冲突**：既有工具的 `units` 描述写「**-1 is rejected by the API**」，
                  而该函数自己的 docstring 写「**本机实测：units=-1 时返回毫米级数值**」
                  ⇒ ★ 按"真实运行证据优先"取 **-1** 作默认，**但两句话都留在描述里**，不合并
                  ⇒ 与**事实 139**（缺口数两个口径不合并）**同型**
               ```
            692 ★ **一处归属按实测改正**：队列把 `default_element_size_and_tolerance` 写在 `_study` 名下，
               实测它在 **`scripts/sw_simulation.py`** ⇒ 以实测为准（工具声明 `module=` 用实测值）。
            693 ★ **五处口径一致地动 3**（**第三次**同一模式，互相印证）：
               ```
               被工具引用的公开函数 100→**103** · 孤立能力 295→**292** · 首参可注入 44→**41**
               并集 431→**434** · 本仓库独家 82→**85** · 缺口 338 **不变**
               ```
               ★ 两处"钉死数量"的测试同步更新（**48→51** · **93→96**）· 注册表现有 **51** 条声明。
            694 ⚑ **限度**：本批**只做暴露**（真机排队列 B 组）· `template` 合法取值**至今未知** ·
               `units` 的冲突**没被裁决**（要裁决得真机试 `-1` 会不会被拒）。
               门禁 + `release_check` exit 0 · 全量回归绿。
            695 ▶ **队列续作**（`docs/backlog-8h.md`）：下一项 = **A3 视图/选择族**
               （`get_active_view` / `activate_view` / `add_perspective` / `entities_on_body`）⇒ 继续自动推进。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None
before = "".join(lines)
if re.search(r"^\s+691 ", before, re.M):
    print("  游标 691 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+695 ", R.read_text(encoding="utf-8"), re.M)
    print("  复核: 695 行已存在 ✓")
