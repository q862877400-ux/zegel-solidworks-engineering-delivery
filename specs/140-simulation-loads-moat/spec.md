# Feature 140 · 仿真载荷包装层（砌墙 W7 · ★★ 护城河）

> 状态与进度不写在这里（宪法：那在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。

## 一、要解决的问题：**护城河 —— 而"护城河"这三个字是核实过的，不是自称**

```
★ 四家的**工具名**里跟仿真有关的合计只有 **4 个**，且**全是"建研究 / 跑"**：
    `Eduardof0nt` 3（create_motion_study / create_simulation_study / run_simulation）·
    `vespo92` 1（vba_simulation_setup）· `Slacker-LLC` **0**
    （`andrewbartels1` 那 2 个是**误命中** —— 它的 "load" 指 `load_part` / `load_assembly`）
  ⇒ ★ **没有任何一家挂"载荷 / 约束"**。
★ 四家的**测试**里也**没有**仿真载荷的判据（三家为"无"）
  ⇒ ★ 按 `AGENTS.md` §5.0（用户指令）：**找过了、没有 ⇒ 自己搓**。
```

## 二、★★★ 而能力层**早就包装好了** —— 本特性就是目标里那句「有就直接挂」

```
★ `sw_simulation.apply_fixed_restraint(study, *, model=None, restraint_type=0)`
★ `sw_simulation.apply_normal_force(study, magnitude, *, model=None, force_type=1, unit=0)`
  ⇒ ★ **首参是 `study`（不是 raw COM 对象）** ⇒ **已经是包装层** ✓
★ 而且真机**整链已跑通过**（能力清单 `simulation_and_fea` 的文字证据）：
    「赋材料 → 按面坐标选面 → 夹具 → 载荷（**Count == 2**）→ CreateMesh（**7,310 单元**）
      → RunAnalysis（1 秒）→ study.Results 非空、GetPlotCount == 4」
★ 并且**已有可复跑的证据脚本**：`tools/capture_simulation_evidence.py`（205 行）
⇒ ★★ **本特性不写能力层、不写新探针** —— 只挂工具 + 补一个**走工具路径**的证据。
```

## 三、需求（各带来源）

| # | 需求 | 来源 |
|---|---|---|
| R1 | 能对**声明式选中的面**施加**夹具** | 官方 `ICWLoadsAndRestraintsManager.AddRestraint`；本项目 `sw_simulation.apply_fixed_restraint`（MIT） |
| R2 | 能对**声明式选中的面**施加**法向力** | 官方 `…AddForce`；`sw_simulation.apply_normal_force` |
| R3 | 力的大小**单位写清**（牛顿） | 规则 2 的精神（★ 力不是长度/角度，规则 2 没规定后缀，但**明确单位**一致） |
| R4 | 选择必须**声明式** | 并入六条规则**规则 3** |
| R5 | ★ 工具层要能拿到 `study` 与 `model` **两个**宿主对象 | 能力层 docstring：「给了它（`model`）才会把选区实体装成官方要求的 `DispArray`」 |

## 四、★★★★ 第五种包装形状：**三种机制的组合**

```
`apply_fixed_restraint(study, *, model=None, …)` 需要**两个**宿主对象 ⇒ `inject` 只能注一个。
读 `tool_registry` 的组装顺序（L399–432）后确定**可以三者并用**：
    L408-416  `inject`       ⇒ `kwargs[inj] = resolver(params)`
    L419-422  `pre_call`     ⇒ 选择类副作用（**不动 kwargs**）
    L423-432  `derived_args` ⇒ **在 pre_call 之后**往 kwargs 里补（★ 不得覆盖已直传名）
⇒ ★ 所以：`inject="study"`（研究）+ `pre_call`（**先选好面**）+ `derived_args`（**补 `model`**）
★ 既有 **8 个**先例已用 `inject` + `derived_args` 组合 ⇒ **既有机制的组合，不新造**。
★ `study` 的解析器**早就有了**（`RESOLVERS["study"] = resolve_study`，按 `study_name` 解析、空名取第一个）。
```

## 五、★★★ 「插件不在」是个**假象**（本特性差点据此误判，值得记）

```
★ 我用 `win32com.client.Dispatch("SldWorks.Simulation")` 测"插件在不在" ⇒ 报「找不到指定的模块」
⇒ ★ 差点据此判「触发停止条件 §九之 3（需要用户提供的东西）」
★ 而本项目**早就查清**（事实 141/142）：真因是「**加载项没启用**」，**不是许可** ——
    `LoadAddIn` 的参数是「**Fully qualified file name**」，传 ProgID 当然"找不到"（返回 **3 = swFileNotFound**）；
    ★ 而**许可错是 7 = swLicenseError**。
⇒ 用注册表里的**真路径** `LoadAddIn("…\\SOLIDWORKS\\Simulation\\cosworks.dll")` ⇒ **0 = swSuccess**。
★ 本特性实测：`ensure_simulation_addin(sw_app)` ⇒ **CDispatch** ✓ · `get_cosmosworks(sw_app)` ⇒ **CDispatch** ✓
⇒ ★★★ **教训（与用户纪律同源）：判断"某个东西在不在"之前，先查项目里有没有查过它** ——
   我当时**没先查**，直接搓了个探针，**得出错误结论**。
```

## 六、不做什么（有据）

| 不做 | 原因 |
|---|---|
| 不写能力层 | ★ 已经包装好了（本特性的核心判断）|
| 不新写探针 | ★ 既有 `capture_simulation_evidence.py` 已覆盖能力层整链 |
| 不挂「建研究」 | 能力层有 `create_static_study`，但**本批只补"载荷/约束"这条护城河**（留后续批次）|
| 不挂 `sw_simulation_loads` 的另外 26 个 | 压力/扭矩/重力/离心/轴承/远程载荷/12 种连接器 ⇒ 留后续批次 |
| 不碰保存 / 另存 / 删除 | 计划明写本阶段不做高风险写操作 |

## 七、验收

```
① 静态：`all_specs()` 里出现 2 个新工具，且门禁全绿
② ★ 真机（**走工具真实路径**）：`output/simulation-loads-evidence.json` 的 `verdict == "pass"`，且含：
   · `bindings.ok`（两个声明解析得到 · `inject="study"` · 有 `pre_call` · 有 `derived_args`）
   · ★★ `via_tool_path.ok` —— 夹具「固定-1」· 载荷「力-1」（★ 三件套链跑通）
   · ★ `judgement.ok` —— 选区计数 **1 / 1** · `Count == 2`
```
