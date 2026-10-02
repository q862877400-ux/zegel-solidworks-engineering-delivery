# Plan · Feature 140 仿真载荷包装层（护城河）

## 一、要查的官方源与冲突裁决顺序

| 序 | 源 | 本特性用它查什么 |
|---|---|---|
| 1 | 出厂类型库反射（`D:\AI\SW\_raw\reflect_sldworks\`） | **裁决者**：`ICWLoadsAndRestraintsManager.AddRestraint` / `AddForce` 的 arity |
| 2 | `C:\swapi\types\ICWLoadsAndRestraintsManager\*.md` | 精确签名 |
| 3 | 本项目 `docs/known-facts.md` 的 **141 / 142** | ★★ **加载项可达性**（★ 这一条救了本特性，见四）|
| 4 | 本机实测 | 工具路径能否跑通 · 判据（选区计数 + `Count`）|

**冲突裁决**：以**出厂类型库反射**为准（铁律 4）。

## 二、★★★ 本特性的核心判断：能力层**已经包装好了**

```
★ `apply_fixed_restraint(study, *, model=None, restraint_type=0)` —— **首参是 `study`**
★ `apply_normal_force(study, magnitude, *, model=None, force_type=1, unit=0)` —— 同上
⇒ ★ 目标里写的那句「**第一步先核清 … 是否已是包装层，有就直接挂**」——
  ★ **答案是"是"，所以本特性就是"直接挂"。**
★ 而这**不是猜的**：两者首参都不是 raw COM 对象；且能力清单里的文字证据显示整链已跑通。
```

## 三、★ 包装形状：**三种机制的组合**（第五种）

```
★ 读 `tool_registry` 的组装顺序（L399–432）确定**可以三者并用**：
    `inject` → `pre_call` → `derived_args`（★ 后者**不得覆盖已直传名**，L424-431 会 GateError）
⇒ `inject="study"` + `pre_call`（选面）+ `derived_args`（补 `model`）
★ 既有 **8 个**先例已用 `inject` + `derived_args` ⇒ **组合既有机制，不新造**。
★ `derived_args` 补 `model` 是否与已直传名冲突？—— ★ **不冲突**：
  `model` 没有被任何 `Param` 直传（`study_name` / `selection` 都被 `param_alias` 消费）。
```

## 四、★★★ 差点误判：**「插件不在」是假象**

```
★ 本特性开工时，我用 `Dispatch("SldWorks.Simulation")` 测"插件在不在" ⇒ 「找不到指定的模块」
  ⇒ ★ 差点判「触发停止条件 §九之 3」。
★★ 而项目里**早有**事实 141/142 查清了这件事，还有 `ensure_simulation_addin` 把它做对：
    · `LoadAddIn` 的参数是「**Fully qualified file name**」⇒ 传 ProgID 返回 **3 = swFileNotFound**
      （★ **许可错才是 7 = swLicenseError**）⇒ 真因是「**加载项没启用**」，**不是许可**
    · 用注册表里的**真路径** `…\\Simulation\\cosworks.dll` ⇒ **0 = swSuccess**
★ 实测：`ensure_simulation_addin` ⇒ **CDispatch** ✓ · `get_cosmosworks` ⇒ **CDispatch** ✓
⇒ ★★★ **教训（与用户纪律 §5.0 同源）：判断"某个东西在不在"之前，先查项目里有没有查过它。**
   ★ 我当时**没先查**，直接搓探针 ⇒ **错误结论**。★ 这正好是"先找，找不到再自己搓"的反例。
```

## 五、验证设计：**走工具真实路径**（★ 既有脚本不够）

```
★ 既有 `capture_simulation_evidence.py` 走的是**能力层直调**（`sim.apply_fixed_restraint(study, …)`）
  ⇒ 它证明**能力层**能跑，**没证明本批新挂的接线**能跑。
★ 而本项目第 4 条可复用套路是「**证据走工具真实路径**」
  ⇒ ★ 本特性补 `tools/capture_simulation_loads_evidence.py`：按注册器**同一顺序**走
     `inject`(resolve_study) → `pre_call`(选面) → `derived_args`(补 model) → 目标函数。
★ **判据沿用既有脚本那三条**（★ 那是本项目自己的判据，不新造）：
    | 夹具/载荷 | 选区计数 = 1 且 `LoadsAndRestraintsManager.Count == 2` |
    | 网格      | `CreateMesh` 返回 0 且 `ElementCount` 是小的正整数 |
    | 求解      | ★ **不是** `RunAnalysis` 的返回码，而是 `study.Results` 非空 + `GetPlotCount > 0` |
  ⇒ ★ 本脚本**只断言第 1 条**（接线是否正确）；第 2/3 条已被既有脚本覆盖。
```

## 六、风险与对策

| 风险 | 对策 |
|---|---|
| ★★ 「插件不在」误判 ⇒ 白判停止条件 | ★ 用**项目认定的取法**（`ensure_simulation_addin`），不用 `Dispatch` |
| ★ 证据只直调能力层 ⇒ 抓不到声明层 bug | ★ **走工具真实路径**（★ 本批**正是靠它抓到 `magnitude_n` 漏改名**）|
| ★ 选区累加 ⇒ 判据假红 | ★ 每次之间 `ClearSelection2(True)`（★ 照既有脚本 L145/L148）|
| 力的大小单位不明 | ★ 参数名带 `_n` + 说明写"牛顿"；能力层 `unit=0` = `n_or_nm` |
