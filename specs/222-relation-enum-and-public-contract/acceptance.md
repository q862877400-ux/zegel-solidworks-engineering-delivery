# 222 · 验收记录

日期：2026-10-08。结论：**离线判据全绿（18/18）**；runtime / product = **not_run**。
未证明关系几何、实体对应、自由度、持久性、真实 COM 或工程建模合格；**不升级 capabilities 的 verified**。

> ⚠ 本文件在实施过程中被**独立核对推翻过两次结论**，均已订正。凡标注「由独立核对抓出」的条目，
> 都是**主代理自己的实现或判据有问题**，不是外部问题。

## 一、实际命令与读数

受管 Python（路径写 3.13.12，二进制 `-V` 实报 **3.13.14**；仓库 `__pycache__` 为 `cpython-314` ⇒ 日常口径疑为 3.14，**本次结论仅对 3.13.14 成立**）。标准库 `unittest`，无 pytest / pydantic 安装。

### 1. 本切片判据

```
"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/tests/test_relation_enum_alignment.py"
```

| 时点 | 读数 |
|---|---|
| 改动前（红基线） | `Ran 8 tests` ⇒ **6 failures + 2 errors** |
| 初版修复后 | `Ran 12 tests` ⇒ **OK** |
| **补强判据后（最终）** | `Ran 18 tests in 0.165s` ⇒ **OK（18/18）** |

### 2. 回归

| 测试 | 读数 |
|---|---|
| `tests/test_sw_sketch_relations_safety.py`（221） | `Ran 12 tests` ⇒ **OK** |
| `tests/test_extended_modules_contract.py`（既有） | **14/15** —— 唯一失败 `test_add_relation_passes_two_arguments: No module named 'pythoncom'` |

**关于那 1 个失败**：本机未装 pywin32，`sketch_relations._dispatch_array` 内 `import pythoncom` 即失败。
该函数**本切片未改动**，属**既有环境限制**。★ 如实记录，**不宣称「全部测试通过」**。

### 3. 静态检查

四个改动文件逐个 `ast.parse` 通过。

## 二、改动清单

| 文件 | 改了什么 |
|---|---|
| `scripts/sw_sketch_relations.py` | `RELATION_TYPES` 整表按官方重写（9 键数值 + 2 键改名）；新增 `LEGACY_ALIASES` 与 `_norm_type` 反别名分支；非法名拒绝信息补官方名提示；补来源块 |
| `scripts/sketch_relations.py` | `SKETCH_CONSTRAINT_TYPES` 19 项按官方校正（原表仅 `angle` 正确）；新增 `UNDECIDED_CONSTRAINT_TYPES` + `is_undecided_constraint()`；**补全** `SKETCH_SLOT_CREATION_TYPES`（3→4）与 `SKETCH_RELATION_ENTITY_TYPES`（6→15） |
| `scripts/sw_part.py` | `_SG_RELATIONS` 去非官方名；`add_sketch_relation` **新增前置状态门**；**补 `from typing import Any`** |
| `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py` | **补 `from typing import Any`**（与上者同类缺陷） |
| `mcp-server/tool_specs_batch16.py` | 参数描述**与模块 docstring** 均正名 |
| `docs/known-facts.md` | 事实 149 订正（原文把 `sgEQUAL`/`sgMIDPOINT` 当合法值记录） |
| `tests/test_relation_enum_alignment.py` | 新增，18 例 |
| `tests/test_extended_modules_contract.py` | 去掉硬编码 `kind == 1`；订正槽/实体枚举项数（`3/2/6` → 官方 `4/2/15`） |
| `specs/222-*/tasks.md` | 补勾 + 验收命令改为自含 + 订正 T020 判据 |
| `docs/ROADMAP.md`、`.specify/feature.json` | 游标指向 222 |

## 三、独立核对抓出的**我自己的**缺陷（均已修复）

本切片派了 **80 路 DeepSeek 成员**做独立核对（两波 × 40，报告在 `output/222-verify/`）。
**实现与判据由主代理串行完成** —— 因为 T007/T008/T015 同在 `sw_sketch_relations.py`、
T011/T012 同在 `sw_part.py`，并行编辑会互相覆盖。

### 3.1 `get_com_member` 实参误用 ⇒ 前置门**恒失败**（真 bug）

我写了 `get_com_member(_sk, "GetConstrainedStatus", "GetConstrainedStatus2")`。
而真函数签名是 `get_com_member(obj, attr_name, *args)`，第 3 参**是调用实参**（`return member(*args)`，`sw_connect.py:183`），
**不是备用成员名** ⇒ 真机上会去调 `GetConstrainedStatus("GetConstrainedStatus2")` ⇒ 实参个数不符 ⇒ 抛错 ⇒ 被吞 ⇒ `_st=None` ⇒ **恒拒**。
⇒ **这道门不是被绕过，而是恒失败** —— fail-closed（不造成破坏）但**工具在真机上根本用不了**。

**为什么判据没抓到**：我的测试桩写成「`attr(*args)` 失败就退回 `attr()`」，**比真函数宽容**，把实参错误吞了。
**修法**：① 实现改为与 `sw_sketch_relations._val` 一致（**只传成员名**，再按需调用）；② 测试桩改为**忠实**（有实参就按实参调，失败就让它失败）。
由独立核对 `w2-26` 抓出。

### 3.2 `_SG_LEGACY_ALIASES` 键大小写不一致 ⇒ **死代码**

我写的键是 `"sgEQUAL"`，而查表用 `_cand.lower()` ⇒ **恒不命中** ⇒ 别名提示恒为空 = 死代码。
**为什么判据没抓到**：原判据只断言「官方名出现在消息里」，而合法值清单 `sorted(_SG_RELATIONS)` 本来就含官方名 ⇒ 空判据。
**修法**：① 键改小写；② 新增判据断言提示的**专有措辞**「官方对应名为」必须出现 + 新增别名表大小写无关的直接判据。
由独立核对 `w2-22` 抓出。

### 3.3 `is_undecided_constraint` 零调用点 ⇒ FR-008 实际未满足

该函数与测试里的 `EXPECTED_UNDECIDED` 常量都是**死代码**（只有定义、无使用），
而我的注释却声称「由它拦下」。由独立核对 `w2-34` 抓出。
**修法**：新增判据真正使用二者 —— 断言未决名**不得出现在可派发表的键里**（结构保护：未决名**没有数值**可派发）+ 断言 `is_undecided_constraint` 认得它们。

### 3.4 一批**空判据**（实现错了也不会失败）

由独立核对 `w2-38` 系统性指出，逐条已修：
- 别名方向只断言「结果 ∈ 官方集合」⇒ `EQUAL→PARALLEL` 也会过 ⇒ 改为断言**确切映射**。
- 公开描述只查 `EQUAL`/`MIDPOINT` 两个词 ⇒ 别的非官方名进来照样过 ⇒ 改为**逐个 sg 名**比对官方清单。
- 「无活动草图」判据无法区分是哪条分支 ⇒ 加断言错误信息含「没有活动草图」。
- 缺**完整性**约束 ⇒ 删掉大半键也能过 ⇒ 新增键集完整性判据（`EXPECTED_RELATION_KEYS` / `EXPECTED_SG_RELATIONS`）。

### 3.5 `tasks.md` 勾选与宣称矛盾

22 条**全部未勾**，而 `acceptance.md` 与 `ROADMAP` 已宣称完成。由 `w2-35` 抓出。
**修法**：补勾 + 把不自含的验收命令（原文写「上述命令」「同上」）改为逐条可复制。
另订正 T020 判据 —— 初版写「仅 4 个文件变化」是**错的**（工作树本来就有 5 项遗留已跟踪改动）。

## 四、过程中发现的**既有致命缺陷**（非本切片引入）

### 4.1 `scripts/sw_part.py` 导入即崩（**同一缺陷有两个实例**）

第 2120 行 `_feature_report(...) -> dict[str, Any]` 用了 `Any`，而该文件**从未 `from typing import Any`**，
也没有 `from __future__ import annotations`：

```
IMPORT FAILED: NameError : name 'Any' is not defined
```

**后果**：公开工具 `solidworks_add_sketch_relation` 指向 `sw_part.add_sketch_relation` ⇒ **该工具此前是死的**。
**为什么长期未暴露**：`tests/test_extended_modules_contract.py` 把整个 `sw_part` 用 `_StubModule` 桩掉了，**从没真正 import 过它**。

**同类第二实例**：`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`（第 2559、2857 行）完全同型。由独立核对 `w2-11` / `w2-09` 抓出。

两处均已补 `from typing import Any`。

### 4.2 两道门禁为何没拦住（**门禁的边界问题**，由独立核对挖出根因）

- `scripts/check_undefined_names.py`：`sw_part.py` 里的 `globals()[_fn] = ...` 命中其 `_has_star_import` 启发式 ⇒ `scan_file` **整文件跳过**（该文件**根本没有 `import *`**，纯误伤）；且门禁只打印聚合计数，**从不报「跳过了谁」**。第二道防线也失效：`Any` 只在**返回注解**里，而门禁整段跳过注解子树 —— 没按「是否选了惰性注解」分情况，而本仓跑 3.13 且该文件**没有** future import ⇒ 注解即时求值 ⇒ **这类 bug 在构造上不可见**。
- `scripts/check_enum_values_vs_reflection.py`：`sketch_relations.py` 是**仅因文件名边界**被漏（门禁只 glob `scripts/sw_*.py`），而它的行形态**完全合格**；`sw_sketch_relations.py` 是**双重行形态失配**（键全大写 + 无 `# swXxx` 注释）。全仓命中 122 行 / 12 文件，**这两张表贡献 0**。
  ⇒ ★ 共同点：**边界外的表静默不报**（既无 PASS 也无 FAIL），从输出**看不出它没管**。

**未修**（属另立规格范围）：这两道门禁的覆盖边界与「跳过要报出来」的改造。

## 五、未过的门（**不得**当成通过）

- **关系几何 / 实体对应 / 自由度 / 持久性**：完全未验。计数增加仍只是计数证据。
- **真实 SAFEARRAY 与 COM**：未运行。所有测试都是假宿主。
- **`block` / `snappoint`**：只做「拒绝派发 + 登记」，**没有**确定对应哪个官方成员。
- **`sw_pattern.py:95/105` 同类候选**（`w2-38` 发现）：来源块自称对应官方页，但官方页只有 3 项 / 2 项，表里却有 7 项 / 8 项，**内容完全对不上**。已登记，未修。
- **发行快照副本**（`w2-34` 发现）：`apps/workbench-ui/src-tauri/resources/skill/` 下有 `sw_part.py` / `tool_specs_batch16.py` 的**打包副本**，仍是旧错值。spec 只点了 `scripts/` 与 `mcp-server/`，故不算违反；但**发版前必须同步**。
- **`_SG_RELATIONS` 的 45 vs 77 条口径**（`w2-31` 发现）：`SketchAddConstraints` 的 Remarks 分两个子块、命名风格不同（旧式 `sgHORIZONTAL` vs 新式 `sgHORIZONTAL2D`）。**不影响本切片**（`sgSAMELENGTH`/`sgATMIDDLE` 在两块里都出现），但口径本身未裁决。
- **`INFLUENCE_TYPE` 官方源自相矛盾**（`w2-16`）：示例一律传 32，而 bitmask 枚举 `Global=32`/`ToNextCurve=0`，与参数表 0–3 体系不同，官方未写换算。离线无法裁定。
- **导入冒烟的范围限制**（`w2-01`~`w2-10`）：只覆盖**导入期**；函数体内缺导入、`get_type_hints()` 路径**未覆盖**。
- **发行收口**：内嵌快照同步、适用生成器、全量门禁**均未运行**。
- **提交 / 部署 / COM / 真机**：未做。

## 六、下一动作

1. 裁决 `sw_pattern.py:95/105`（先读官方页与源码注释，判断是「照录写错」还是「自造抽象」）。
2. 两道门禁的边界改造（「跳过要报出来」+ 文件名 glob 放宽 + 注解按 future import 分情况）。
3. 发版前同步 `apps/workbench-ui/.../resources/skill/` 的打包副本。
4. 真实 SAFEARRAY / COM 另按明确授权与护栏执行。
