# 122 · 拓扑/仿真整链**真机复验**（从「验收红」到 `verdict: pass`）

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
   `…\SOLIDWORKS\Simulation\cosworks.dll`（存在）
④ 用**完整路径** `LoadAddIn` ⇒ **0 = swSuccess** ⇒ `GetAddInObject` 随后**非 None**
⇒ 真因：**加载项没启用**（不在 `SOFTWARE\SolidWorks\Addins` 下）⇒ SW 启动时不加载它
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
