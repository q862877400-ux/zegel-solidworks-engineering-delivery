import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")
S = W / "specs" / "122-topology-chain-reverified"
S.mkdir(parents=True, exist_ok=True)

(S / "spec.md").write_text("""# 122 · 拓扑/仿真整链**真机复验**（从「验收红」到 `verdict: pass`）

**Status**: Implemented（轮 203）

## 一、要什么（specify）
轮 179 起，`topology_optimization` 的验收命令 `tools/capture_topology_evidence.py` **是红的**，
而账本把原因归为「**环境**（`GetAddInObject('SldWorks.Simulation')` 返回 None ⇒ 需 Simulation 许可证）」。
轮 202 业主说「**我已经安装好许可了**」⇒ ★ 本特性的目标：
**把「验收红」这件事查到底，并让整链在真机上重新跑绿。**

## 二、★ 而第一步就推翻了归因（clarify）
```
① 现成探针（`tools/probe_simulation_addin_status.py`）给出「② 类：更可能是**许可/安装**问题」
   —— ★ **不采信**（它没查返回码的含义）
② `swLoadAddinError_e`：**3 = swFileNotFound** · **7 = swLicenseError**
   ⇒ 旧写法 `LoadAddIn("SldWorks.Simulation")` 返回 **3** —— 那是「**文件没找到**」
     （官方文档：该参数要「**Fully qualified file name of the add-in**」，唯一例外是 `LoadAddIn('MBD')`）
   ⇒ ★★ **"需许可证"那半是错的**
③ 只读注册表：`SldWorks.Simulation` → CLSID `{C8F79410-…}` → `InprocServer32` =
   `…\\SOLIDWORKS\\Simulation\\cosworks.dll`（存在）
④ 用**完整路径** `LoadAddIn` ⇒ **0 = swSuccess** ⇒ `GetAddInObject` 随后**非 None**
⇒ 真因：**加载项没启用**（不在 `SOFTWARE\\SolidWorks\\Addins` 下）⇒ SW 启动时不加载它
```

## 三、判据（**不看返回码**，全走回读）
| 环节 | 判据 | 实测 |
|---|---|---|
| 拓扑研究 | `AnalysisType == 13` 且入口是 `CreateNewStudy3`（未走降级）| ✓ 13 / `CreateNewStudy3` |
| 目标+约束 | 两者非 None 且 `mass_constraint_reused` 为真 | ✓ reused=True · **质量降 75.0%** |
| 夹具/载荷 | 选区计数 = 1 且 `Count == 2` | ✓ 1 / 1 / 2 |
| 网格 | `CreateMesh` 返回 0 **且**单元数是合理正整数 | ✓ **85,748**（1.6 s）|
| 求解 | ★ **不是** `RunAnalysis` 返回码，而是 `Results` 非空 + 图数 > 0 | ✓ Results 非空 · 图数 **2**（228.9 s）|
| **Material Mass** | `GetPlotNames` 里出现 `材料质量*` / `Material Mass*` | ✓ **`材料质量1`** |
⇒ **`verdict: pass`**（证据 `output/topology-evidence.json`）

## 四、★★ 一个必须写进判据的**反例**（脚本作者已预置）
```
「无拓扑许可时：会弹『拓扑算例未获许可』且 Results 为空，而**返回码仍为 0**」
⇒ ★ 所以"返回码 0"**不能**当成功判据 —— 本次 JSON 里显式带
  `"run_analysis_return_is_trustworthy": false` ⇒ ★ **判据自己声明了它不可信**（这是好设计）
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-12201 | ★★★ **不采信**现成探针的结论；查出真因（加载项没启用，**不是许可**）|
| SC-12202 | ★★★ 用官方文档 + 枚举证明 **3=文件没找到 ≠ 7=许可错** |
| SC-12203 | ★★ 持久修复（`ensure_simulation_addin`）⇒ 取件成功 |
| SC-12204 | ★★★ 整链真机跑绿，**六条判据全走回读**，落 `verdict: pass` |
| SC-12205 | ✅ **许可确实生效**（拿到 `Results` + `材料质量1` —— 无许可时这两样必空）|
| SC-12206 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ 本轮**只跑了拓扑那条**（`capture_topology_evidence.py`）—— ★ **静力学那条没跑**；
* ⚠ 求解耗时 **228.9 s**（不是失败那四次的 20–25 GB / 1000–3000 s）；
  ⇒ ★ 那四次的"不收敛"**与本轮的 pass 不矛盾**（不同网格/参数），但**成因仍未定**；
* ⚠ `LoadAddIn` 是**会话级**的 ⇒ 下次启动 SW 仍要再装一次（要持久得在 Tools > Add-Ins 勾）；
* ⚠ 本轮**没动**那份结论错的探针（**故意留作记录**）。
""", encoding="utf-8")

(S / "plan.md").write_text("""# 122 · Plan

1. **specify**：验收命令是红的 + 账本归因为"环境/许可" ⇒ 目标：查到底并跑绿
2. **clarify**：业主说"许可装好了" ⇒ ★ 那"许可"这个归因**必须先被证伪或证实**（不能直接信）
3. **analyze**：查官方文档（`LoadAddIn` 参数形态）+ 枚举含义 ⇒ **3=文件没找到 · 7=许可错**
   ⇒ 旧探针的结论**错**（它把 3 读成了许可）
4. **plan**：① 只读注册表拿真路径 ② 用完整路径 `LoadAddIn` ③ 若得 0/2 ⇒ 持久修复进正常路径
5. **implement**：`scripts/sw_simulation.py` 加 `SIMULATION_ADDIN_DLL` / `LOAD_ADDIN_CODES` /
   `ensure_simulation_addin()`；`get_cosmosworks()` 复用；账本两条能力插**更正归因**
6. **verify**：`get_cosmosworks(sw)` ⇒ `CDispatch` ✓；然后**真跑整链**
7. **converge**：六条判据全走回读 ⇒ `verdict: pass`；修下游（签名审计 45→47 · 重生成地图 · 报告数字）
8. 事实 → Spec Kit → ROADMAP 游标 → 门禁 + 回归 → 两仓库 commit

## 风险与对策
| 风险 | 对策 |
|---|---|
| 采信"许可问题"就停手 | ★★★ 查**枚举含义** ⇒ 一眼看穿（3 ≠ 7）|
| `LoadAddIn` 加载 40 MB 进程内 COM 有风险 | ★ 只调**一次** · `CommandInProgress` finally 关 · 收尾点弹窗 · 复用已有实例 |
| 求解吃 20–25 GB | ★ **先量成本**：脚本自己写"单次约 3 分钟"⇒ 实测 228.9 s · 85,748 单元 |
| 把"跑绿了"当"整条仿真链都通了" | ⚠ **明说只跑了拓扑那条**，静力学没跑 |
| 以为许可和加载项是同一件事 | ★ 拆开：**许可=7**、**加载项没启用=能加载但没注册** ⇒ 本次是后者 |
""", encoding="utf-8")

(S / "tasks.md").write_text("""# 122 · Tasks（全部完成，轮 203）

- [x] T-12201 ★★★ 证伪"许可"归因（查枚举：3=文件没找到 · 7=许可错）
  `→ 验收:` `Get-Content C:\\swapi\\enums\\swLoadAddinError_e.md`
- [x] T-12202 ★★ 只读注册表拿真路径 ⇒ `LoadAddIn(<完整路径>)` ⇒ **0 = swSuccess**
  `→ 验收:` `python tools\\probe_simulation_loadaddin_by_path.py`
- [x] T-12203 ★★ 持久修复 + 实测取件
  `→ 验收:` `get_cosmosworks(sw)` ⇒ **CDispatch**
- [x] T-12204 ★★★ 整链真机复验 ⇒ **`verdict: pass`**
  `→ 验收:` `python tools\\capture_topology_evidence.py`（exit 0 · 85,748 单元 · 图数 2 · `材料质量1` · 228.9 s）
- [x] T-12205 ★★ 修下游三处（签名审计 45→47 · 重生成地图 · 报告数字）⇒ 全绿
- [x] T-12206 门禁 + 回归 `→ 验收:` `python scripts\\release_check.py`（exit 0）· 全量 **1260 passed / 17 skipped**
""", encoding="utf-8")

(S / "converge.md").write_text("""# 122 · Converge

**Converged**: 2026-10-01（轮 203）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-12201 不采信、查真因 | ✅ 加载项没启用（**不是许可**）|
| SC-12202 3 ≠ 7（枚举 + 官方文档）| ✅ |
| SC-12203 持久修复 | ✅ `get_cosmosworks` ⇒ CDispatch |
| SC-12204 整链跑绿 | ✅ **`verdict: pass`** |
| SC-12205 许可确实生效 | ✅ 拿到 `Results` + `材料质量1` |
| SC-12206 门禁 + 回归 | ✅ **1260 passed / 17 skipped** |

## 二、★★★ 本轮的形状：**"环境问题"这个标签，挡住了一个可修的真因**
```
轮 179 的记账是「验收红 = 原因在**环境**（需 Simulation 许可证）」——
★ 这个标签**看起来负责**（它承认不是代码退化），实际上**让人停止追问**：
  既然"环境问题"、既然"要许可证"，那就等业主装许可 —— **而业主早就装好了**。
★★ 真相是**我的探针把 3 读成许可**（`swFileNotFound` ≠ `swLicenseError`），
  于是"能加载但没启用"这件事**从来没被看见**。
⇒ ★ 教训（可复用）：**给一个问题贴上"环境"标签之前，先证明那个环境条件真的不满足** ——
  否则标签本身就是一层"判据没覆盖"，而它与"没问题"长得一样。
```

## 三、★★ 而脚本作者做对的一件事值得点名
```
`capture_topology_evidence.py` 把「**无许可时返回码仍为 0**」写进了 JSON：
  `"run_analysis_return_is_trustworthy": false`
⇒ ★ **判据自己声明了自己不可信** —— 这正是本会话反复讲的那条纪律的**正面样板**。
★ 所以这次的成功**可信**：它不是靠"返回 0"，是靠 `Results` 非空 + 图数 2 + 出现 `材料质量1`。
```

## 四、⚠ 未查证
* ⚠ **只跑了拓扑那条**；静力学（`tools/capture_simulation_evidence.py`）**没跑**；
* ⚠ 本月早先那四次「不收敛」（20–25 GB / 1000–3000 s）**成因仍未定** ——
  本轮的 pass **不推翻**它们（不同网格/参数），但也**没解释**它们；
* ⚠ `LoadAddIn` 是**会话级**的；
* ⚠ 那份结论错的探针**故意留在仓库里**（作"错法的记录"）。
""", encoding="utf-8")
print("  ok Spec Kit 122 四件套已写")
