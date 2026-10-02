# Feature 141 · 仿真研究族（建 / 取 / 列）（24h 计划 · 段 1.1）

> 状态与进度不写在这里（宪法：那在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。

## 一、要解决的问题：**W7 的硬前置 —— 没有它，工具只能引用"别人建好的"研究**

```
★ W7（`specs/140`）把仿真载荷挂上了柜台，但它的 `limitations` 第一条就是：
    「★ **没有**「建研究」的工具 ⇒ `study_name` 只能引用**已存在**的研究（空名取第一个）
      —— 建研究要用能力层 `create_static_study`（未挂）」
⇒ ★★ 这意味着：**用户必须先手动在 SolidWorks 里建一个研究**，我们的工具才有东西可用。
⇒ 本特性把那一步补上 ⇒ ★ **仿真链才真正从"能用"变成"闭环"**。
```

## 二、§5.0 先找后搓（**强制第一步**，`AGENTS.md` §5.0）

| 序 | 找哪里 | 结果 |
|---|---|---|
| 1 | 四家 live 测试（`andrewbartels1` 6 个 · 其余三家）| ★ **没有**建研究的判据（0 处）|
| 2 | ★ **自己的仓库** | ★★ **有** —— `tools/capture_simulation_loads_evidence.py:109` **已在用** `create_static_study(sw, "DSH-W7")` 且**真机跑通** ⇒ ★ **判据可复用** |
| 3 | 结论 | ★ **不必自己搓新判据** —— 沿用 W7 那条链，**并加强**（建完回读名字）|

## 三、需求（各带来源）

| # | 需求 | 来源 |
|---|---|---|
| R1 | 能**新建静力学研究**并拿到它 | ★ **`create_static_study(sw_app, name, *, study_type=0, mesh_type=0)`**（首参 `sw_app` ⇒ 注入名已有）；官方 `ICWModelDoc.StudyManager` + `CreateNewStudy3/2/1` |
| R2 | ★ 能判出**是否走了降级路径** | ★ **能力层自己的设计**：`create_static_study` **返回三元组** `(study, entry_name, error_code)`，`entry_name` 标明命中 `CreateNewStudy3/2/1` ⇒ ★ **断言必须看它** |
| R3 | 能**按名字取研究** | `get_study_by_name(sw_app, name)` |
| R4 | 能**列出所有研究** | `iter_studies(sw_app)` |
| R5 | 能拿到**研究管理器** | `get_study_manager(sw_app)`（★ 它是 `get_study_by_name`/`iter_studies` 的底座；★ **是否该挂要判断**，见五）|
| R6 | 名字重复 / 空名要**明确** | 本项目一贯纪律（不静默）|

## 四、★ clarify：四处需要拍板的地方（及我的决定）

### Q1 · `create_static_study` 返回**三元组**，工具对外该回什么？
```
★ 选项：(a) 只回 study 对象（调用方看不到 entry_name）
        (b) ★ **回一个可 JSON 化的字典**（含 `study_name` / `entry_name` / `error_code`）
⇒ ★ **选 (b)** —— 理由：★ **`entry_name` 是"是否降级"的唯一证据**，
  而本项目的纪律是「**不许静默成功**」（规则 6 的同一精神）。
  ⚠ 而 MCP 工具**返回的是字符串**（`run_locked` 包 JSON）⇒ ★ 所以需要一个
  **薄包装**（`inject="sw_app"` + 自己组装字典）⇒ ★ **本批要写一个小能力层函数**，
  或 ★ 用 `extra_op`？—— 见 Q2。
```

### Q2 · 用 `extra_op` 还是新写能力层函数？
```
★ `tool_registry` 有 `extra_op`（L417：`if spec.extra_op is not None: return spec.extra_op(params)`）
★ 而 W1 立的定则：「包装层走**只回读数的薄函数** + `inject="model"`，**不用 `extra_op`**」
⇒ ★ **选：新写一个薄能力层函数**（`sw_simulation.create_study_report`），**不动既有函数**。
  ★ 理由：`extra_op` 会让**逻辑藏在声明里**（★ 与"能力落 scripts/"的纪律冲突）；
    而薄函数**可被直接测试**、也能被别的调用方用。
```

### Q3 · `get_study_manager` 该不该挂？
```
★ 它返回 **COM 对象**（`ICWStudyManager`）⇒ ★ **MCP 回不了对象** ⇒ 单独挂它没意义。
⇒ ★ **不单挂** —— 它的作用**已经被** `create_static_study` / `get_study_by_name` /
  `iter_studies` 三个覆盖（★ 与 W3/W5 的定则一致：「不把已被包含的拆成多个工具」）。
  ★ 但要**核**：`iter_studies(sw_app)` 是否真的回可 JSON 化的东西（见 T1）。
```

### Q4 · 研究**类型**（`study_type`）要不要暴露？
```
★ `SWS_ANALYSIS_STUDY_TYPES` 有多个（static 等）⇒ ⚠ 而**只有 static 被本会话真机验过**。
⇒ ★ **第一版只暴露 `static`**（不暴露 `study_type` 参数），并在说明里写清
  「★ 目前只支持静力学研究」；★ **其它类型未真机验证** ⇒ 不假装支持。
  ★ 这符合硬约束③（未验的必须**明确标注**）。
```

## 五、不做什么（有据）

| 不做 | 原因 |
|---|---|
| 不挂 `get_study_manager` | ★ 回 COM 对象，MCP 用不上；其作用已被三个工具覆盖（Q3）|
| 不暴露 `study_type` / `mesh_type` | ★ 只有 `static` + `solid` 被真机验过（Q4）|
| 不改 `sw_simulation` 的既有四个函数 | ★ 加薄函数即可（Q2）|
| 不碰保存 / 另存 / 删除 | 计划边界 |

## 六、验收

```
① 静态：`all_specs()` 里出现 3 个新工具（建 / 取 / 列），且门禁全绿
② ★ 真机：`output/simulation-study-evidence.json` 的 `verdict == "pass"`，且含：
   · ★★ **`entry_name` 被记录**（判"是否走了降级路径"）
   · ★ **建完回读**：`get_study_by_name(sw, <刚建的名字>)` 能取到，且**名字对上**
   · ★ **列出**：`iter_studies(sw)` 里**至少有一个**，且包含刚建的那个
   · **负例**：取一个**不存在**的研究名 ⇒ 必须**报错或明确回空**（不静默给一个错对象）
```
