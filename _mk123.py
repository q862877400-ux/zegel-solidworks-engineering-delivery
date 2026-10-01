import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")
S = W / "specs" / "123-expose-orphan-capabilities"
S.mkdir(parents=True, exist_ok=True)

(S / "spec.md").write_text("""# 123 · 挂柜台（第一批）：把孤立能力从「看得到 30 个」变成「可复现的全量清单」并暴露

**Status**: Implemented（轮 204）

## 一、要什么（specify）
把 `scripts/sw_*.py` 里「谁都不调用、也没暴露」的**孤立能力**挂成 MCP 工具，让"柜台"变宽。
★ 但**第一步不是登记工具** —— 而是先解决一个**判据问题**（见第二节）。

## 二、★★★ 先撞到的病：候选清单**87% 看不见**（clarify）
```
`tools/probe_unexposed_functions.py`（既有工具）印到「孤立能力（前 30）」就停，
后面写「…（还有 %d 个）」。
⇒ ★★ 实测共 **302** 个 ⇒ **272 个（87%）读者看不到** ⇒ "选哪一批暴露"只能靠感觉。
★ 而本项目**明令禁止**靠感觉（事实 53：不为启发式硬凑）。
⇒ 所以本轮**先做的是**：给它加**结构化全量输出**（`D:/AI/SW/output/orphan-capabilities.json`），
  连**签名**一起落盘 ⇒ 于是"选哪批"**可从数据复现**。
```

## 三、★★ 全量清单给出的数（**这一步才是"选批"的依据**）
```
302 个孤立能力
  其中 **首参可注入**（`model` / `sw_app` / `study`）: **51**
  其中 **含裸坐标形参**（`x`/`y`/`z` —— 规则 3 会拒注册）: **4**
⇒ 本批从这 51 里取**拓扑的「目标 / 约束 / 控制」**那一族。
```

## 四、为什么先做拓扑这一族（四条理由，逐条可核）
1. `topology_optimization` 是 **`verified`**，且 **轮 203 真机复验 `verdict: pass`**
   （85,748 单元 / 图数 2 / `材料质量1` / 228.9 s）；
2. `sw_topology` 是**可注入孤立能力最集中的模块**（12 个）；
3. ★ **先例已存在**：`solidworks_topology_create_study` / `_evidence` / `_run` 三个工具**已经在挂**，
   本批沿用**同一个** `inject="study"` + `param_alias={"study_name": None}` 模板（不另立一套）；
4. 内聚：本批全部是**同一条真机链**上「目标 / 约束 / 控制」那一环的构造器。

## 五、本批取的 4 个（**签名照实取，不发明**）
| 工具 | 函数（真实签名）|
|---|---|
| `solidworks_topology_create_mass_constraint` | `create_mass_constraint(study, *, reduce_percent: float)` |
| `solidworks_topology_create_factor_of_safety_constraint` | `create_factor_of_safety_constraint(study, *, specified_factor: float)` |
| `solidworks_topology_create_preserved_region` | `create_preserved_region(study, *, option: int \\| None = None)` |
| `solidworks_topology_create_thickness_control` | `create_thickness_control(study, *, min_thickness: float \\| None = None, max_thickness: float \\| None = None)` |

**明确不取**（附理由，见 `tool_specs_batch11.py` 的表）：
`create_symmetry_control` / `create_demold_control`（**枚举值未核**，铁律 5 不猜）·
`create_stress_constraint`（与本批两约束重叠，留批）·
`sw_surface.create_*`（已知事实 40：返回值跨次会变）·
`sw_part` 那 14 个（含 `angle_rad` ⇒ **与规则 2 冲突**，要先定换算边界）。

## 六、★★★★ 而实测给出了**一处必须诚实修正的地方**
```
我原以为"这批都真机跑过" —— **实测不是**：
`tools/capture_topology_evidence.py` **直接调用过**的拓扑函数**只有 4 个**
  （create_topology_study · set_topology_goal · set_material · run_analysis）
⇒ ★ 而本批这 4 个**不在其中** ⇒ **它们没有直接的真机证据**。
★ 所以本批**只做"暴露"**，**不声称真机验证**：
  `topology_optimization` 的真机证据仍以那条**已验证的整链**为准 ——
  **不因为"挂上了"就给它们任何 `verified` 身份。**
```

## 七、判据（★ 三处独立口径必须**一致地**动 4）
| 口径 | 之前 | 现在 |
|---|---|---|
| 被工具引用的公开函数（探针）| 93 | **97** |
| 孤立能力（探针）| 302 | **298** |
| 首参可注入（探针）| 51 | **47** |
| 地图「本仓库(MCP)」| 86 | **90** |
| 地图「本仓库独家」| 75 | **79** |
⇒ ★★ **五个数在同一次改动上一致地动 4** —— 这不是凑的，是同一件事在五个独立口径上的投影。

## 八、判据表
| ID | 判据 |
|---|---|
| SC-12301 | ★★★ **先解决"候选看不见"**（87% 不可见 ⇒ 加结构化全量输出），再做选择 |
| SC-12302 | ★★ 选择**从数据来**（51 可注入 / 4 含裸坐标）而不是凭感觉 |
| SC-12303 | ★★ 本批 4 个**签名照实取**（`inspect.signature`），模板**照既有先例** |
| SC-12304 | ★★★ **如实说**：这 4 个**没有直接真机证据**，只暴露、不给 `verified` |
| SC-12305 | ★★ **五处独立口径一致地动 4**（互相印证）|
| SC-12306 | 规则 1/2/3 门禁通过（`all_specs()` 的 `check_spec`）· 两处硬编码计数**同步更新** |
| SC-12307 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ **只做了 4 个**（302 / 51 的极小一部分）—— 这是第一刀，**不是"挂完了"**；
* ⚠ 这 4 个**没有直接真机证据**（见第六节）；
* ⚠ `sw_surface` / `sw_part` / `sw_simulation_loads` 那几族**都有已知障碍**（事实 40 / 规则 2 / 规则 3），
  **不是"以后随手就能挂"**；
* ⚠ 本批**没跑真机**（暴露 ≠ 验证）。
""", encoding="utf-8")

(S / "plan.md").write_text("""# 123 · Plan

1. **specify**：把孤立能力挂成 MCP 工具
2. **clarify**：★ 先查"候选怎么来的" ⇒ 撞到探针**只印前 30 / 实际 302**（87% 不可见）
3. **analyze**：⇒ ★ **先修判据、再动手**：给探针加结构化全量输出（含签名）
4. **plan**：从清单里按"首参可注入 + 不含裸坐标"筛 ⇒ 选**拓扑的目标/约束/控制**族（四条理由）
5. **implement**：`mcp-server/tool_specs_batch11.py`（4 条，照既有 `study` 模板）+
   `register_capabilities.BATCH_MODULES` 加一行
6. **verify**：`all_specs()` 41→45（门禁不拒）· 五处口径一致动 4 · 两处硬编码计数同步更新
7. **converge**：如实记"这 4 个没有直接真机证据"
8. 事实 → Spec Kit → ROADMAP 游标 → 门禁 + 回归 → 两仓库 commit

## 风险与对策
| 风险 | 对策 |
|---|---|
| **凭感觉选批** | ★★★ 先把全量清单做出来（含签名）⇒ 选择可复现 |
| 以为"能挂就该挂" | ★ 逐族查障碍（surface 事实 40 / part 规则 2 / loads 规则 3）|
| 把"暴露"当"验证" | ★★★ **明文写：本批不给任何 `verified` 身份** |
| 参数名写错（规则 2）| ★ 长度参数用 `_mm` + `param_alias` 映射回真名 |
| 加了批次忘了改计数 | ★ 两处"钉死数量"的测试**当场报红**（设计意图），同步更新 |
| 枚举值猜 | ★ 不猜（铁律 5）⇒ `symmetry_type` / `demold` 留批 |
""", encoding="utf-8")

(S / "tasks.md").write_text("""# 123 · Tasks（全部完成，轮 204）

- [x] T-12301 ★★★ **先修判据**：探针加结构化全量输出（含签名）
  `→ 验收:` `python tools\\probe_unexposed_functions.py`（落 `D:/AI/SW/output/orphan-capabilities.json` · 302 个）
- [x] T-12302 ★★ 从数据选批（51 可注入 / 4 含裸坐标）⇒ 取拓扑族 4 个
- [x] T-12303 ★★ 写 `mcp-server/tool_specs_batch11.py`（4 条 · 照既有 `study` 模板 · 签名照实取）
- [x] T-12304 ★★ 注册 + 门禁
  `→ 验收:` `python -c "import register_capabilities as rc; print(len(rc.all_specs()))"`（**45**）
- [x] T-12305 ★★ 五处口径一致动 4（探针 3 处 + 地图 2 处）
  `→ 验收:` `python tools\\probe_unexposed_functions.py` + `python tools\\build_union_map.py`
- [x] T-12306 ★ 两处硬编码计数同步更新
  `→ 验收:` `python -m pytest tests/test_server_wiring.py tests/test_mcp_protocol_layer.py -q`（**16 passed**）
- [x] T-12307 门禁 + 回归 `→ 验收:` `python scripts\\release_check.py`（exit 0）· 全量回归
""", encoding="utf-8")

(S / "converge.md").write_text("""# 123 · Converge

**Converged**: 2026-10-01（轮 204）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-12301 先修"候选看不见" | ✅ 302 个全量落盘（此前只印 30）|
| SC-12302 选择从数据来 | ✅ 51 可注入 / 4 含裸坐标 |
| SC-12303 签名照实取 + 照先例 | ✅ |
| SC-12304 如实说"没有直接真机证据" | ✅ 本批**不给任何 `verified` 身份** |
| SC-12305 五处口径一致动 4 | ✅ 93→97 · 302→298 · 51→47 · 86→90 · 75→79 |
| SC-12306 门禁 + 两处计数同步 | ✅ 16 passed |
| SC-12307 门禁 + 回归 | ✅ |

## 二、★★★★ 本轮最值钱的不是那 4 个工具，是**先修判据这件事**
```
如果直接"凭经验挑 4 个挂上"，本轮会**看起来一样成功**（柜台 +4、门禁全绿）。
★ 而真相是：候选清单**87% 看不见** —— 那种"成功"是**在看不见的地图上选的路**。
⇒ ★★ 所以本轮**第一件事是让清单可复现**（加结构化输出 + 签名），第二件才是挂工具。
★ 而可复现之后立刻拿到了**之前拿不到的数**：51 可注入 / 4 含裸坐标
  ⇒ ★ 于是"下一批挑谁"**也能从数据答**，不再靠感觉。
★ 这与本会话那条主线同源：**判据/观测比代码更容易错** ——
  而"候选从哪来"就是这次的判据。
```

## 三、★★ 一处**必须诚实修正**的自我预期（已写进 spec 第六节）
```
我原以为"拓扑这批都真机跑过" —— 实测：证据脚本**直接调用过**的只有 4 个，
而本批这 4 个**不在其中** ⇒ 它们**没有直接真机证据**。
⇒ ★ 于是本批**只声称"暴露"**，并明写"不给任何 verified 身份"。
★ 教训：**"同一条链上"不等于"这个函数跑过"** —— 别用邻接关系代替证据。
```

## 四、未查证
* ⚠ 只做了 **4 / 302**（第一刀，不是"挂完了"）；
* ⚠ `symmetry_type` / `demold` 的**枚举值未核**（不猜，留批）；
* ⚠ `sw_part` 那族含 `angle_rad` ⇒ **与规则 2 冲突**，要先定换算边界；
* ⚠ `sw_surface` 那族有已知事实 40（返回值跨次会变）⇒ 暴露前要先定行为；
* ⚠ 本批**没跑真机**（暴露 ≠ 验证）。
""", encoding="utf-8")

FACT = """| 143 | **挂柜台第一批：先修判据（候选清单 87% 看不见），再挂 4 个** —— 而"同一条链上"≠"这个函数跑过"** —— 2026-10-01（轮 204 / Spec Kit `123`）。

★★★ **本轮最值钱的是"先修判据"这一步**：
```
`tools/probe_unexposed_functions.py`（既有工具）印到「孤立能力（前 30）」就停，
后面写「…（还有 %d 个）」⇒ ★★ 实测共 **302** ⇒ **272 个（87%）读者看不到**
⇒ "选哪一批暴露"**只能靠感觉** —— 而本项目**明令禁止**靠感觉（事实 53）。
★ 若直接凭经验挑 4 个挂上，本轮会**看起来一样成功**（柜台 +4、门禁全绿），
  而那种"成功"是**在看不见的地图上选的路**。
⇒ 所以本轮**第一件事**是给它加**结构化全量输出**（`D:/AI/SW/output/orphan-capabilities.json`，
  含**签名**）⇒ "选哪批"从此**可从数据复现**。
实测拿到之前拿不到的数：302 孤立 · **首参可注入 51** · **含裸坐标（规则 3 会拒）4**。
```

★★ **第一批 = 拓扑的「目标 / 约束 / 控制」4 个**（`mcp-server/tool_specs_batch11.py`），四条理由：
① `topology_optimization` 是 `verified` 且**轮 203 真机复验 pass**（85,748 单元 / `材料质量1` / 228.9 s）；
② `sw_topology` 是**可注入孤立能力最集中**的模块（12 个）；③ ★ **先例已存在**
（`solidworks_topology_create_study` / `_evidence` / `_run` 三工具在用同一个 `inject="study"` 模板）；
④ 内聚（同一条真机链的"目标/约束/控制"那一环）。

★★★★ **一处必须诚实修正的自我预期**：
```
我原以为"这批都真机跑过" —— **实测不是**：`capture_topology_evidence.py` **直接调用过**的拓扑函数
**只有 4 个**（create_topology_study · set_topology_goal · set_material · run_analysis），
而本批这 4 个**不在其中** ⇒ **它们没有直接的真机证据**。
⇒ ★ 本批**只做"暴露"**，**不声称验证**、**不给任何 `verified` 身份**。
★ 教训：**"同一条链上"不等于"这个函数跑过"** —— 别用邻接关系代替证据。
```

★★★ **五处独立口径一致地动 4**（互相印证，不是凑的）：
```
被工具引用的公开函数 93→**97** · 孤立能力 302→**298** · 首参可注入 51→**47**
地图「本仓库(MCP)」86→**90** · 地图「本仓库独家」75→**79** · 缺口 338 **不变**
```
★ 两处"钉死数量"的测试**当场报红**（设计意图：让"悄悄多注册工具"可见）⇒ 同步更新（41→45 · 86→90）。

⚠ **限度**：只做了 **4 / 302**（第一刀）· `symmetry_type`/`demold` 的**枚举值未核**（不猜，留批）·
`sw_part` 那族含 `angle_rad` ⇒ **与规则 2 冲突**要先定换算边界 · `sw_surface` 那族有事实 40
（返回值跨次会变）⇒ 暴露前要先定行为 · 本批**没跑真机**（暴露 ≠ 验证）。

**依据**：`tools/probe_unexposed_functions.py`（本轮加全量输出）· `mcp-server/tool_specs_batch11.py` ·
`mcp-server/register_capabilities.py` · `docs/union-coverage-matrix.md` · 事实 40 / 53 / 142
"""

K = W / "docs" / "known-facts.md"
tk = K.read_text(encoding="utf-8")
if "| 143 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT, encoding="utf-8")
    print("  ok known-facts 已加 143")
print("  校验:", K.read_text(encoding="utf-8").count("| 143 |"), "次")

R = W / "docs" / "ROADMAP.md"
B = """           676 🎯 **Spec Kit `123`：挂柜台第一批 —— 先修判据（候选清单 87% 看不见），再挂 4 个**（轮 204）——
               ★★★ **本轮最值钱的是"先修判据"这一步**：
               ```
               `tools/probe_unexposed_functions.py` 印到「孤立能力（前 30）」就停，后面写「…（还有 N 个）」
               ⇒ ★★ 实测共 **302** ⇒ **272 个（87%）读者看不到** ⇒ "选哪一批暴露"**只能靠感觉**
                 —— 而本项目**明令禁止**靠感觉（事实 53）
               ★ 若直接凭经验挑 4 个挂上，本轮会**看起来一样成功**（柜台 +4、门禁全绿），
                 而那种"成功"是**在看不见的地图上选的路**
               ⇒ 先加**结构化全量输出**（`D:/AI/SW/output/orphan-capabilities.json`，含**签名**）
                 ⇒ "选哪批"从此**可从数据复现**：302 孤立 · **首参可注入 51** · **含裸坐标 4**
               ```
            677 ★★ **第一批 = 拓扑的「目标 / 约束 / 控制」4 个**（`tool_specs_batch11.py`），四条理由：
               ① `topology_optimization` 是 `verified` 且**轮 203 真机复验 pass**
                  （85,748 单元 / `材料质量1` / 228.9 s）；② `sw_topology` 是可注入孤立能力**最集中**的模块（12 个）；
               ③ ★ **先例已存在**（`solidworks_topology_create_study` / `_evidence` / `_run`
                  用同一个 `inject="study"` 模板）；④ 内聚（同一条真机链的"目标/约束/控制"那一环）。
               签名**照实取**（`inspect.signature`），不发明参数。
            678 ★★★★ **一处必须诚实修正的自我预期**：
               ```
               我原以为"这批都真机跑过" —— **实测不是**：`capture_topology_evidence.py`
                 **直接调用过**的拓扑函数**只有 4 个**（create_topology_study · set_topology_goal ·
                 set_material · run_analysis），而本批这 4 个**不在其中**
                 ⇒ **它们没有直接的真机证据**
               ⇒ ★ 本批**只做"暴露"**：**不声称验证**、**不给任何 `verified` 身份**
               ★ 教训：**"同一条链上"不等于"这个函数跑过"** —— 别用邻接关系代替证据
               ```
            679 ★★★ **五处独立口径一致地动 4**（互相印证，不是凑的）：
               ```
               被工具引用的公开函数 93→**97** · 孤立能力 302→**298** · 首参可注入 51→**47**
               地图「本仓库(MCP)」86→**90** · 地图「本仓库独家」75→**79** · 缺口 338 **不变**
               ```
               ★ 两处"钉死数量"的测试**当场报红**（设计意图：让"悄悄多注册工具"可见）⇒ 同步更新（41→45 · 86→90）。
            680 ⚑ **限度**：只做了 **4 / 302**（第一刀，不是"挂完了"）· `symmetry_type`/`demold` 的
               **枚举值未核**（不猜，留批）· `sw_part` 那族含 `angle_rad` ⇒ **与规则 2 冲突**要先定换算边界 ·
               `sw_surface` 那族有事实 40（返回值跨次会变）⇒ 暴露前要先定行为 · 本批**没跑真机**（暴露 ≠ 验证）。
               门禁 + `release_check` exit 0 · 全量回归绿。
               下轮候选：① 继续挂（下一批从"可注入 47"里取，**先查枚举**的那几个）·
               ② 跑静力学那条验收（`tools/capture_simulation_evidence.py`）·
               ③ B 级并入本体（范围口径已清）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None
before = "".join(lines)
if re.search(r"^\s+676 ", before, re.M):
    print("  游标 676 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+680 ", R.read_text(encoding="utf-8"), re.M)
    print("  复核: 680 行已存在 ✓")
