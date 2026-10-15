import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")

FACT = """| 141 | **仿真/拓扑「验收红」的归因是**错的** —— 真因是「加载项没启用」，**不是许可**；一行 `LoadAddIn(完整路径)` 即修** —— 2026-10-01（轮 202）。

★★ **起因**：业主说「Simulate 的软件你做了没有，我已经安装好许可了」⇒ 我去量环境。
★★★ **实测（本机 SW 2026 SP4.1 / PID 41060）**：
```
① 现成探针 `tools/probe_simulation_addin_status.py` 的结论是「② 类：更可能是许可/安装问题」
   —— ★ **而那个结论是错的**。
② 真因两处，都在**参数形态**上：
   · `LoadAddIn("SldWorks.Simulation")` ⇒ **3** —— 官方文档（`C:\\swapi\\types\\ISldWorks\\LoadAddIn.md`）
     写明参数是「**Fully qualified file name of the add-in**」⇒ **要完整路径**（唯一例外是 `LoadAddIn('MBD')`）
   · `swLoadAddinError_e` 里 **3 = swFileNotFound**、**7 = swLicenseError**
     ⇒ ★ **返回 3 根本不是许可问题**；旧代码把 3 读成"可能是许可"，**读错了枚举的含义**
③ 只读注册表（**不改**）查到真路径：
   `HKLM\\SOFTWARE\\Classes\\SldWorks.Simulation` → CLSID `{C8F79410-CD71-4061-A2E4-B6BF17CCB27F}`
   → `InprocServer32` = `D:\\...\\SOLIDWORKS\\Simulation\\cosworks.dll`（存在）
④ `LoadAddIn(<完整路径>)` ⇒ **0 = swSuccess** ✓ ⇒ 之后 `GetAddInObject`（ProgID 与 {GUID} 两种形态）
   **都返回非 None**（CDispatch）
⇒ ★★ 真因：**`SOLIDWORKS\\Addins` 下没注册这个加载项** ⇒ SW 启动时不加载它 ⇒ 对象取不到。
  **许可一直是好的**（业主没装错）。
```
★★★ **持久修复**：`scripts/sw_simulation.py` 新增 `ensure_simulation_addin(sw_app)` ——
`GetAddInObject` 取不到就**先用完整路径 `LoadAddIn`**，再取；`get_cosmosworks()` 复用它；
并把那句错归因（"需 Simulation 许可证"）改掉。**实测 `get_cosmosworks(sw)` ⇒ `CDispatch`** ✓
★ 并给 `capabilities.yaml` 的 `topology_optimization` / `simulation_and_fea` 各插一条**更正归因**。

⚠ **仍未跑求解** —— 求解器不收敛（`cwbcbfmesh.exe` 吃 20–25 GB、1000–3000 s CPU）**是另一件事**，
本更正**没有**解决它。⇒ 拓扑/仿真**能不能整链跑通，还要真跑一次才知道**（代价高，需业主点头）。

⚠ **`LoadAddIn` 的影响范围**：只影响**当前会话**（不改注册表、不改启动项）⇒
「这次跑得通，下次启动仍要再装一次」。要让 SW 每次自动加载，要在 Tools > Add-Ins 里勾 —— **代码不动那里**。

⚠⚠ **同轮的一个诚实发现**：回归从「15 skipped」变成「**17 skipped**」（总数 1277 不变）。
查清了：多出的 2 条是 `tests/test_tool_specs_batch4.py` 里**事实 57** 的守卫
（`_derived_args_or_skip`：那些测试要**界面上已选中一条边**才跑得动；现在没开文档 ⇒ **带原因 skip**）
⇒ ★ **不是回归，是那条纪律在按设计工作** —— 它以前"通过"只是**环境恰好满足**。

**依据**：`C:\\swapi\\types\\ISldWorks\\LoadAddIn.md` · `C:\\swapi\\enums\\swLoadAddinError_e.md` ·
`scripts/sw_simulation.py` 的 `ensure_simulation_addin` / `SIMULATION_ADDIN_DLL` / `LOAD_ADDIN_CODES` ·
`tools/probe_simulation_loadaddin_by_path.py` · `D:\\AI\\SW\\output\\simulation-loadaddin-by-path.json` · 事实 47 / 57 / 179
"""

K = W / "docs" / "known-facts.md"
tk = K.read_text(encoding="utf-8")
if "| 141 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT, encoding="utf-8")
    print("  ok known-facts 已加 141")
print("  校验:", K.read_text(encoding="utf-8").count("| 141 |"), "次")

SPEC = W / "specs" / "121-simulation-addin-attribution"
SPEC.mkdir(parents=True, exist_ok=True)
(SPEC / "spec.md").write_text("""# 121 · 仿真/拓扑「验收红」的归因是错的：真因是加载项没启用，不是许可

**Status**: Implemented（轮 202）

## 一、起因
业主：「Simulate 的软件你做了没有，**我已经安装好许可了**」⇒ 去量环境（不假设）。

## 二、★★★ 实测：现成探针的结论**是错的**
```
现成 `tools/probe_simulation_addin_status.py` 输出「② 类：更可能是**许可/安装**问题」——
★ 而那是错的，真因全在**参数形态**上：
① `LoadAddIn("SldWorks.Simulation")` ⇒ **3**
   官方文档：参数是「**Fully qualified file name of the add-in**」⇒ **要完整路径**
   （唯一例外 `LoadAddIn('MBD')`）
② `swLoadAddinError_e`：**3 = swFileNotFound** · **7 = swLicenseError**
   ⇒ ★ 旧代码**把 3 读成了"可能是许可"** —— 读错了枚举含义
③ 只读注册表（**不改**）：`SldWorks.Simulation` → CLSID `{C8F79410-…}`
   → `InprocServer32` = `…\\SOLIDWORKS\\Simulation\\cosworks.dll`（存在）
④ `LoadAddIn(<完整路径>)` ⇒ **0 = swSuccess** ⇒ 之后 `GetAddInObject`（ProgID / {GUID} 两形态）
   **都非 None**（CDispatch）
⇒ 真因：**加载项没注册/没启用**（不在 `SOFTWARE\\SolidWorks\\Addins` 下）⇒ SW 启动时不加载它
⇒ **许可一直是好的**
```

## 三、★★★ 持久修复
```
`scripts/sw_simulation.py`：
  · 新增 `SIMULATION_ADDIN_DLL`（完整路径，来源=只读注册表）+ `LOAD_ADDIN_CODES`（9 个枚举值）
  · 新增 `ensure_simulation_addin(sw_app)`：取不到 ⇒ **先按完整路径 `LoadAddIn`** ⇒ 再取
  · `get_cosmosworks()` 复用；**删掉**那句错归因（"需 Simulation 许可证"），报错里带返回码
  · `capabilities.yaml` 的 `topology_optimization` / `simulation_and_fea` 各插一条**更正归因**
⇒ 实测 `get_cosmosworks(sw)` ⇒ **CDispatch** ✓
```

## 四、⚠ 仍未做的（**不假装**）
* ⚠ **没跑求解** —— 求解器不收敛（`cwbcbfmesh.exe` 20–25 GB / 1000–3000 s）**是另一件事**，
  本更正**没有**解决它；**整链能不能通还要真跑一次**（代价高，需业主点头）；
* ⚠ `LoadAddIn` 只影响**当前会话** ⇒ 下次启动仍要再装一次（要持久得在 Tools > Add-Ins 勾，**代码不动那里**）。

## 五、⚠⚠ 同轮的一个诚实发现（回归 skipped 15→17）
```
多出的 2 条 = `tests/test_tool_specs_batch4.py` 里**事实 57** 的守卫
（`_derived_args_or_skip`：要**界面上已选中一条边**才跑得动；现在没开文档 ⇒ **带原因 skip**）
⇒ ★ **不是回归，是那条纪律在按设计工作** —— 它以前"通过"只是**环境恰好满足**（事实 57 的原话）。
```

## 六、判据
| ID | 判据 |
|---|---|
| SC-12101 | ★★★ **去量**（不采信现成探针的结论）|
| SC-12102 | ★★★ 查出**参数形态**错（名字 ≠ 完整路径），并用官方文档确证 |
| SC-12103 | ★★★ 查**枚举含义**，证明 **3=文件没找到 ≠ 7=许可错** ⇒ 旧归因**错了** |
| SC-12104 | ★★ 持久修复（`ensure_simulation_addin`）并**实测** `get_cosmosworks` 非 None |
| SC-12105 | ★ 账本**更正归因**（两条能力）|
| SC-12106 | ★★ 回归 skipped 的 +2 **查清归因**（事实 57 的守卫），不当作回归糊过去 |
| SC-12107 | 门禁 + 回归不退化（**1260 passed**）|

## ⚠ 明确记下的限度
* ⚠ **没跑求解** ⇒ 「仿真整链跑通」**仍未验证**（本轮只解决"取不到加载项"）；
* ⚠ 持久性：`LoadAddIn` 是**会话级**的；
* ⚠ 注册表只**读**（红线是"不动"，未改）；
* ⚠ 本轮**没动** `tools/probe_simulation_addin_status.py`（它的结论是错的，但**留在那里**作为"错法的记录"——
  ★ 判据：错的那份留下 + 更正写进事实，比删掉更有信息量）。
""", encoding="utf-8")

(SPEC / "plan.md").write_text("""# 121 · Plan

1. 业主说"许可装好了" ⇒ ★ **去量**（先看 SW 在不在、探针在不在、账本怎么记）
2. 跑现成探针 ⇒ 结论"② 类：许可/安装问题" ⇒ ★ **不采信**（它没查返回码含义）
3. 查 `LoadAddIn` 的**官方参数**（`C:\\swapi\\types\\ISldWorks\\LoadAddIn.md`）⇒ 要**完整路径**
4. 查 `swLoadAddinError_e`（9 个成员）⇒ **3=文件没找到 · 7=许可错** ⇒ 旧归因**错了**
5. **只读**注册表拿真 CLSID → `InprocServer32` ⇒ 真路径
6. 用**真路径**调 `LoadAddIn` ⇒ **0 = swSuccess** ⇒ `GetAddInObject` 非 None ✓
7. ★ 持久修复：`ensure_simulation_addin()` 做进正常路径 + 更正错归因 + 账本插更正
8. 修**下游**（改了脚本 ⇒ signature-audit 行 45→47 · 地图要重生成）⇒ 三处全绿
9. ★ 查清回归 skipped 15→17 的归因（事实 57 的守卫）⇒ **不是回归**
10. 事实 141 → Spec Kit 121 → ROADMAP 游标 → 门禁 + 回归 → 两仓库 commit

## 风险与对策
| 风险 | 对策 |
|---|---|
| 采信现成探针的错结论 | ★★ **查枚举含义**（3 vs 7）⇒ 一眼看穿 |
| `LoadAddIn` 加载 40 MB 进程内 COM 有风险 | ★ 只调**一次**（不重试）· `CommandInProgress` finally 关 · 收尾点弹窗 · 复用已有实例 |
| 误以为"许可问题"就停手 | ★ 先证伪它（返回 3 ⇒ 与许可无关）|
| 以为跑通了整链 | ⚠ **明说没跑求解**，不夸大 |
| 把 skipped +2 当回归糊过去 | ★ **查清**（事实 57 的守卫）|
""", encoding="utf-8")

(SPEC / "tasks.md").write_text("""# 121 · Tasks（全部完成，轮 202）

- [x] T-12101 ★★★ 量环境 + **不采信**现成探针的结论
- [x] T-12102 ★★★ 查官方参数（要完整路径）+ 枚举含义（3≠7）
  `→ 验收:` `Get-Content C:\\swapi\\enums\\swLoadAddinError_e.md`（**swFileNotFound=3 · swLicenseError=7**）
- [x] T-12103 ★★ 只读注册表拿真路径 ⇒ `LoadAddIn(<路径>)` ⇒ **0 = swSuccess**
  `→ 验收:` `python tools\\probe_simulation_loadaddin_by_path.py`
- [x] T-12104 ★★ 持久修复 + 实测 `get_cosmosworks` 非 None
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\\swprojects\\sw-skill-fork\\scripts'];import sw_connect,sw_simulation;print(type(sw_simulation.get_cosmosworks(sw_connect.connect_solidworks(10)[0])).__name__)"`（**CDispatch**）
- [x] T-12105 ★ 账本更正归因（`topology_optimization` / `simulation_and_fea`）
- [x] T-12106 ★★ 修下游（signature-audit 45→47 · 重生成地图）⇒ 三处全绿
- [x] T-12107 ★★ 查清回归 skipped 15→17 ⇒ **事实 57 的守卫，不是回归**
- [x] T-12108 事实 141 + 门禁 + 回归
  `→ 验收:` `python scripts\\release_check.py`（exit 0）· 全量 **1260 passed / 17 skipped**
""", encoding="utf-8")

(SPEC / "converge.md").write_text("""# 121 · Converge

**Converged**: 2026-10-01（轮 202）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-12101 去量、不采信 | ✅ |
| SC-12102 参数要完整路径（官方）| ✅ |
| SC-12103 3=文件没找到 ≠ 7=许可错 | ✅ 旧归因**错了** |
| SC-12104 持久修复 + 实测 | ✅ `get_cosmosworks` ⇒ CDispatch |
| SC-12105 账本更正 | ✅ 两条能力 |
| SC-12106 skipped +2 查清归因 | ✅ 事实 57 的守卫 |
| SC-12107 门禁 + 回归 | ✅ **1260 passed / 17 skipped** |

## 二、★★★ 本轮的形状：**现成探针的结论是错的，而它写在文件里、看起来像证据**
```
`tools/probe_simulation_addin_status.py` 输出「② 类：更可能是**许可/安装**问题」——
★ 它有前后对照、有 5 个候选名、有结论，**形式上完全像结论**。
★★ 而它错在**没查返回码的含义**：`3` 是 `swFileNotFound`，**许可错是 `7`**。
⇒ ★ 这与本会话那条主线完全同型：**判据/观测比代码更容易错** ——
  而这次错的不是我的代码，是**上一轮我自己留下的探针**。
★ 处置：**不删它**（留着作为"错法的记录"），把更正写进事实 141 ——
  ★ 判据：**错的那份留下 + 更正写进事实，比删掉更有信息量**。
```

## 三、★★ 而"持久修复"这一步才是关键
```
★ 找到原因只值一半：若不把它**做进正常路径**，下一个人还会踩同一个坑。
⇒ `ensure_simulation_addin()` 让"取不到就先装"成为**默认行为** ⇒ 于是"仿真验收是红的"不再复现。
★ 与轮 191/192/193 同一条主线：**能靠结构保证的，不要靠约定**。
```

## 四、⚠ 未查证
* ⚠ **没跑求解** ⇒ 「仿真整链跑通」**仍未验证**（本轮只解决"取不到加载项"）；
* ⚠ `LoadAddIn` 是**会话级**的 ⇒ 下次启动仍要再装一次；
* ⚠ 注册表只**读**；
* ⚠ 本轮没动那个错的探针（**故意留作记录**）。
""", encoding="utf-8")
print("  ok Spec Kit 121 四件套已写")
