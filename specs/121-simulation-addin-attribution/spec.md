# 121 · 仿真/拓扑「验收红」的归因是错的：真因是加载项没启用，不是许可

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
   → `InprocServer32` = `…\SOLIDWORKS\Simulation\cosworks.dll`（存在）
④ `LoadAddIn(<完整路径>)` ⇒ **0 = swSuccess** ⇒ 之后 `GetAddInObject`（ProgID / {GUID} 两形态）
   **都非 None**（CDispatch）
⇒ 真因：**加载项没注册/没启用**（不在 `SOFTWARE\SolidWorks\Addins` 下）⇒ SW 启动时不加载它
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
