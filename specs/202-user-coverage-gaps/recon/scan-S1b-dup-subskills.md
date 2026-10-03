# 扫描 S1-b · 重复知识（`subskills/**` + `mcp-server/`）

**性质**：只读扫描。**未改动任何既有文件**；未运行 SolidWorks；未运行 pytest。
**唯一新建文件**：本文件。
**扫描日期**：2026-10-03（会话内实测）

---

## 〇 · 扫描范围（实测，非推断）

| 范围 | 数量 | 取法 |
|---|---|---|
| `subskills\**\*.py`（排除 `sw_api_*.py`） | **23** | 递归；该子树下**没有**任何 `sw_api_*.py` 文件（实测 `Get-ChildItem` 结果） |
| `mcp-server\*.py`（排除 `sw_api_*.py`） | **75** | 仅顶层；同样**没有** `sw_api_*.py` 文件 |
| ★ 合计 | **98** | `register_capabilities.py` · `server.py` · `tool_registry.py` · `tool_specs_batch1..72.py`（72 个批次文件） |

> ⇒ ★ **本次范围内「排除 `sw_api_*.py`」这条过滤实际未删掉任何文件**（该命名在本范围不存在）。若上游另有 `sw_api_*.py`，它不在 `mcp-server\` 顶层，也不在 `subskills\` 下。

---

## 一 · 判据（**口径是我定的，不是抄来的 —— 见 §六**）

> ★ **`plan-24h.md:38` 只给了 S1 的一句话定义**：「同一份事实/常量/枚举**散在两个及以上文件**」，产出形如 `清单：fact → 文件:行号 × N`。
> ★ **S1-a 的正式判据表在本仓库里查不到**（`specs\202-user-coverage-gaps\recon\` 下现有 18 个文件，无 `scan-S1a*`；`grep S1-a` 在该目录 0 命中）⇒ 按铁律 5 记「查不到」，并在下面**自述**本次采用的可复算口径，使本表任何一行都能被独立重算。

**一条「重复知识」= 满足以下三条的一个「事实单元」：**

| # | 判据 | 判别方法（可机器复算） |
|---|---|---|
| **J1** | 同一**字面常量 / 数值 / 枚举取值**在 ≥2 个文件里各自出现 | `ast.literal_eval` 收集 `Assign` 右值，按值分组，筛出跨文件组 |
| **J2** | 同一**集合 / 映射字面量**（≥2 元素）在 ≥2 个文件里各自出现 | 同上，`Dict/List/Set/Tuple` 归一化后按 `json.dumps(sort_keys=True)` 分组 |
| **J3** | 同一**字符串事实**（官方成员名 / 错误码 / 报告字段名 / 领域词汇 / 说明文案，长度 ≥4）在 ≥2 个文件里各自出现 | `ast.Constant(str)` 分组，筛出跨 ≥2 文件者，再人工剔掉纯关键字与无信息词 |

**不计入的三类（避免虚高）：**

- **不计入**同一文件内部的自我重复（如 `drawing_workflow.py:1418` 的 docstring 重复同文件 `:21-26`）—— 只作为「第三个家」的旁注写进该行。
- **不计入**参数名 / 工具名这类**跨工具的必然重复**（如 `element_size_mm` 在 batch1 与 batch28 各出现一次）—— 那是 `Param` 契约的正常复用，不是「一份知识两个家」。
- **不计入**已知的单一真源：`mcp-server/tool_registry.py:93/147/158`（`_BARE_COORD_NAMES` / `_LEN_WORDS` / `_ANGLE_WORDS`）、`mcp-server/server.py:174-176`（`HEADLESS_OPEN_FORMATS` / `DFM_PROCESSES` / `FEA_SOLVERS`）—— 实测各只有**一个**定义点。

---

## 二 · 结果总表 —— **51 条**

> 行的含义：一行 = 一条事实单元；`× N` = 它出现在几个文件里。★ 标 `⚠` 的行**已经漂移**（几份内容不一致），比单纯重复更危险。

### 甲 · 官方枚举 / 常量（5 条）

| # | 事实 | 出现位置（`文件:行号`） | ×N | 判据 | 备注 |
|---|---|---|---|---|---|
| 1 | `SW_SOLID_BODY = 0` | `subskills\solidworks-fillet-chamfer-cnc\scripts\create_cnc_mount_template.py:40`<br>`subskills\solidworks-fillet-chamfer-cnc\scripts\verify_advanced_fillets.py:59`<br>`subskills\solidworks-fillet-chamfer-cnc\scripts\verify_open_source_complex_case.py:26`<br>`subskills\solidworks-threaded-holes\scripts\create_threaded_hole_template.py:35` | 4 | J1 | 官方 `swBodyType_e` 的 solid body 索引 |
| 2 | `SW_DISPLAY_ORIGINS = 6` | `verify_advanced_fillets.py:79` · `verify_open_source_complex_case.py:27` | 2 | J1 | |
| 3 | `SW_DISPLAY_REFERENCE_TRIAD = 205` | `verify_advanced_fillets.py:80` · `verify_open_source_complex_case.py:28` | 2 | J1 | |
| 4 | `SW_CHAMFER_DISTANCE_DISTANCE = 2` | `verify_advanced_fillets.py:76` · `verify_open_source_complex_case.py:29` | 2 | J1 | |
| 5 | `SW_CHAMFER_TANGENT_PROPAGATION = 4` | `verify_advanced_fillets.py:77` · `verify_open_source_complex_case.py:30` | 2 | J1 | 第 1–5 条同属 `verify_advanced_fillets.py:59-80` 与 `verify_open_source_complex_case.py:26-30` **两段常量块** |

### 乙 · 领域词汇表 / 规格表（6 条）

| # | 事实 | 出现位置 | ×N | 判据 | 备注 |
|---|---|---|---|---|---|
| 6 | 图幅集合 `A0..A4` **及图幅码 `5=A4 … 9=A0`** | ① `subskills\solidworks-engineering-drawing\scripts\drawing_spec.py:15`（`PAPER_SIZES` 集合）<br>② `drawing_workflow.py:21-26`（dict：code + `width_m` + `height_m`）<br>③ `drawing_workflow.py:1418`（docstring 又写一遍 `5=A4, 6=A3, 7=A2, 8=A1, 9=A0`）<br>④ `drawing_spec.py:74`（错误文案「`paperSize` 必须是 A4/A3/A2/A1/A0」） | 2 | J1/J2 | ⚠ ④ 处**集合本身**在 `drawing_spec.py` 内已是第三份表述 |
| 7 | 投影法集合 `{"first_angle","third_angle"}` **+ 同一句报错文案** | ① `drawing_spec.py:16`（`PROJECTIONS`）+ `:80`<br>② `drawing_workflow.py:467-468`<br>③ `drawing_workflow.py:955-956`<br>④ `drawing_workflow.py:1475-1476`<br>⑤ `drawing_workflow.py:2048-2049` | 2 | J1/J3 | ★ 同一句 `"projection 必须是 first_angle 或 third_angle"` 在 `drawing_workflow.py` 里**抄了 3 遍** |
| 8 | ⚠ **视图方向别名表** | ① `drawing_spec.py:108-110` — **11 项**（front/top/right + 前视/主视/上视/俯视/右视）<br>② `drawing_workflow.py:633-646` — **11 项**（同 11 项）<br>③ `drawing_review.py:325-333` — **19 项**（多 `left`/`bottom`/`isometric` + 左视/仰视/轴测/等轴测） | 3 | J2 | ★★ **三份已经不一致**：项数 11/11/19；归一化正则也不一致 —— `drawing_spec.py:116` 用 `isalnum()`（**保留数字**），另两份用 `[^a-z…]` / `[^a-z0-9…]`（**剔除数字**）；未命中时 `drawing_workflow.py:647` 返回 `None`，另两处返回 compact 串 |
| 9 | 专业工程图标注的**类别键名**（`center_marks`/`center_lines`/`datum_tags`/`geometric_tolerances`/`surface_finish_symbols`/`weld_symbols`(+`hole_callouts`)） | ① `drawing_workflow.py:1655-1662`（生产端 6 键）· `:1719-1726`（汇总端 7 键）· `:1750-1752`（分发循环）<br>② `drawing_review.py:416-424`（消费端 `collection_map` 7 条映射） | 2 | J2/J3 | ⚠ 消费端映射多出一条 `holeCallouts → hole_callouts`，而 6 键的生产端字典里没有它（该键在 `:1722`/`:1782` 才补上） |
| 10 | AutoCAD .NET 的**运行期必需检查 9 项** | ① `subskills\autocad-automation\scripts\acad_dotnet_preflight.py:24-34`（名 `RUNTIME_REQUIRED_CHECKS`）<br>② `subskills\autocad-automation\scripts\acad_dotnet_regression.py:25-35`（名 `REQUIRED_CHECKS`） | 2 | J2 | ⚠ ★ **同一份 9 元组、两个不同变量名** —— 改一处不会改另一处 |
| 11 | ★ **毫米↔米换算常量 `0.001` / `1000.0`** | ① `mcp-server\tool_specs_batch3.py:48`（`_MM = 0.001`）<br>② `mcp-server\tool_specs_batch4.py:52`（`_MM = 0.001`）<br>③ `drawing_workflow.py:2195`（`/1000.0`）· `:2232`（两处 `/1000.0`）<br>④ `create_cnc_mount_template.py:212` · `:219`（`* 1000.0`）<br>⑤ `verify_advanced_fillets.py:262` · `:764` · `:778` · `:787`<br>⑥ `verify_open_source_complex_case.py:132` · `:134` · `:186` | 6 | J1 | ★ 全范围 **12 处**；只有 ①② 用了命名常量，其余 10 处是**裸魔数** |

### 丙 · 官方成员名以字符串字面量重复（9 条）

| # | 事实 | 出现位置 | ×N | 判据 |
|---|---|---|---|---|
| 12 | `"GetVisibilityOfConstructPlanes"` + `"ViewDispRefplanes"`（成对使用） | `create_cnc_mount_template.py:62,63` · `create_threaded_hole_template.py:193,194` | 2 | J3 |
| 13 | `"FirstFeature"` + `"GetNextFeature"`（特征树遍历入口） | `create_cnc_mount_template.py:487,496` · `create_threaded_hole_template.py:614`（**同一行两次**） | 2 | J3 |
| 14 | `"IsLine"` / `"IsCircle"` / `"CircleParams"`（曲线判定三元组） | `create_cnc_mount_template.py:180,198,200` · `create_threaded_hole_template.py:290,292`（+ `:269` 的 `select_sketch`） | 2 | J3 |
| 15 | `"GetSurface"` / `"IsPlane"` / `"IsCylinder"`（曲面类型三元组） | `verify_advanced_fillets.py:301,305,306` · `verify_open_source_bracket.py:90,91,93` | 2 | J3 |
| 16 | `"VarFillet"`（尺寸类型名判定） | `verify_advanced_fillets.py:807` · `verify_open_source_bracket.py:60` | 2 | J3 |
| 17 | `"POINTREF"`（`SelectByID2` 的类型串） | `verify_advanced_fillets.py:388` · `verify_open_source_bracket.py:124` | 2 | J3 |
| 18 | `"GetBox"`（实体包围盒读取） | `drawing_workflow.py:151` · `verify_advanced_fillets.py:284` | 2 | J3 |
| 19 | `"GetPathName"` | `mcp-server\server.py:956` · `:965` · `subskills\...\drawing_workflow.py:1898` | 2 | J3 |
| 20 | `"FullName"`（尺寸全名回读） | `subskills\autocad-automation\scripts\acad_review.py:67` · `drawing_workflow.py:1764` | 2 | J3 |

### 丁 · 错误码 / 报告字段名（7 条）

| # | 事实 | 出现位置 | ×N | 判据 |
|---|---|---|---|---|
| 21 | `"AUTOCAD_DOTNET_RUNTIME_NOT_VERIFIED"` | `acad_dotnet_preflight.py:73` · `:113` · `acad_dotnet_regression.py:232` · `:294` | 2 | J3 |
| 22 | `"AUTOCAD_DOTNET_EVIDENCE_INVALID"` | `acad_dotnet_preflight.py:77` · `acad_dotnet_regression.py:276` | 2 | J3 |
| 23 | `"native-cpp-swb"`（跨语言后端标识） | `subskills\...\hold_line_bridge.py:222` · `:238` · `verify_advanced_fillets.py:474` · `:480` | 2 | J3 |
| 24 | `"CAD_STUDIO_UNSAFE_NATIVE_HOLD_LINE"`（环境变量名） | `hold_line_bridge.py:27`（`UNSAFE_HOLD_LINE_ENV` 定义）· `verify_advanced_fillets.py:950`（**直接写 `os.environ[...] = "1"`**） | 2 | J3 | ⚠ 第二处是**字面重写变量名**而非引用常量 |
| 25 | `"rebuild_after_reopen"`（回归报告字段） | `verify_open_source_bracket.py:250` · `verify_open_source_complex_case.py:267` | 2 | J3 |
| 26 | `"DRAWING_BOM_TEMPLATE_MISSING"` | `drawing_spec.py:96` · `drawing_workflow.py:2230` | 2 | J3 |
| 27 | 中文参数校验文案三句「` 必须是数值`」「` 必须是有限数值`」「` 必须大于 0`」 | `subskills\...\cnc_strategy.py:76` · `:78` · `:188` · `create_threaded_hole_template.py:148` · `:156` · `advanced_fillet_strategy.py:142` | 3 | J3 |

### 戊 · 同名实现重复的函数体（19 条）

> 计数口径：按**函数名**逐条计，不打包。md5 比对的是**含 docstring 的完整源码段**。

| # | 函数名 | 出现位置 | ×N | 判据 | 备注 |
|---|---|---|---|---|---|
| 28 | `clear` | `create_cnc_mount_template.py:53-55` · `create_threaded_hole_template.py:184-186` | 2 | J3 | ★ **全范围唯一一组「实现字节完全相同」的函数** |
| 29 | `assert_feature` | `create_cnc_mount_template.py:45-50` · `create_threaded_hole_template.py:176-181` | 2 | J3 | ⚠ 打印文案不同（`OK: {name}` vs `OK {name}:`；`<unnamed>` vs `<未命名>`） |
| 30 | `hide_reference_planes` | `create_cnc_mount_template.py:58-66` · `create_threaded_hole_template.py:189-197` | 2 | J3 | ⚠ 除 docstring 一句外**逻辑逐行相同** |
| 31 | `current_sketch_name` | `create_cnc_mount_template.py:81-84` · `create_threaded_hole_template.py:238-241` | 2 | J3 | |
| 32 | `select_plane` | `create_cnc_mount_template.py:69-78` · `create_threaded_hole_template.py:213-235` | 2 | J3 | ⚠ ★ **签名已分叉**：前者收 `aliases: tuple`、后者收 `plane_name: str` 并**内建**同一张中英文映射（`:216-220`） |
| 33 | `select_sketch` | `create_cnc_mount_template.py:99-106` · `create_threaded_hole_template.py:254-269` | 2 | J3 | |
| 34 | `circle_center_radius` | `create_cnc_mount_template.py:194-203` · `create_threaded_hole_template.py:286-295` | 2 | J3 | 行数相同（各 10 行） |
| 35 | `all_edges` | `create_cnc_mount_template.py:232-238` · `create_threaded_hole_template.py:298-304` | 2 | J3 | |
| 36 | `edge_signature` | `create_cnc_mount_template.py:206-229`（24 行）· `verify_open_source_complex_case.py:117-141`（25 行） | 2 | J3 | 同 subskill 内的两份 |
| 37 | `finite_number` | `cnc_strategy.py:71-79` · `create_threaded_hole_template.py:144-149` | 2 | J3 | ⚠ ★ **已漂移**：`cnc_strategy` 版 `try/except (TypeError, ValueError)` → 报「必须是数值」；模板版**没有 try**，非法输入直接抛裸 `ValueError` |
| 38 | `validate_basename` | `cnc_strategy.py:82-89`（正则 `INVALID_BASENAME`）· `create_threaded_hole_template.py:160-165`（内联字符集 `<>:"/\|?*`） | 2 | J3 | ⚠ 同一条规则两套实现 |
| 39 | `_finite_positive` | `drawing_workflow.py:275-283` · `subskills\...\advanced_fillet_strategy.py:137-145` | 2 | J3 | |
| 40 | `parse_args`（共用 5 个入参名：`基体长度 mm`/`基体宽度 mm`/`基体厚度 mm`/`--basename`/`--out`） | `create_cnc_mount_template.py:701-736` · `create_threaded_hole_template.py:768-798` | 2 | J3 | 文案见 `create_cnc_mount_template.py:715-717,733` 与 `create_threaded_hole_template.py:772-774,796` |
| 41 | `run_regression` | `acad_dotnet_regression.py:184-300`（117 行）· `verify_open_source_bracket.py:163-262`（100 行） | 2 | J3 | 跨 subskill 的同名同角色 |
| 42 | `_consumed` | `mcp-server\tool_specs_batch{3,4,17,18,21,23,26,29,30}.py` — 精确行号：`batch3:37`·`batch4:55`·`batch17:59`·`batch18:61`·`batch21:72`·`batch23:68`·`batch26:88`·`batch29:74`·`batch30:63` | **9** | J3 | ★ `mcp-server` 内**最大一处**同名 helper 扩散 |
| 43 | `_model` | `batch4:67`·`batch18:69`·`batch23:76`·`batch26:93`·`batch29:79` | **5** | J3 | |
| 44 | `_derive_model` | `batch26:114`·`batch29:96`·`batch31:61` | 3 | J3 | |
| 45 | `_spec` | `batch29:101`·`batch30:68` | 2 | J3 | |
| 46 | `_select_face` | `batch26:103`·`batch29:89` | 2 | J3 | |

### 己 · 说明文案 / 注释块（5 条）

| # | 事实 | 出现位置 | ×N | 判据 | 备注 |
|---|---|---|---|---|---|
| 47 | `_GEOM_NOTE`（草图图元坐标口径的整段说明） | `mcp-server\tool_specs_batch21.py:62` · `tool_specs_batch54.py:36` | 2 | J3 | 逐字相同 |
| 48 | `_READBACK`（`ok` 判据是回读 + Simulation 加载项提示） | `mcp-server\tool_specs_batch58.py:52` · `tool_specs_batch60.py:45` | 2 | J3 | 逐字相同 |
| 49 | `param_alias` 构造说明块（docstring） | `mcp-server\tool_specs_batch3.py:38` · `tool_specs_batch4.py:56` | 2 | J3 | 逐字相同 |
| 50 | `_STUDY_ALIAS = {"study_name": None}` | `mcp-server\tool_specs_batch11.py:64` · `batch12:52` · `batch13:57` | 3 | J1/J3 | 三处逐字相同 |
| 51 | ★ **基准面中英文名对**（`"Front Plane"↔"前视基准面"` 等） | ① `create_cnc_mount_template.py:91` · `:533`（`("Front Plane","前视基准面")`）<br>② `create_threaded_hole_template.py:217-219`（三对全表）<br>③ `verify_advanced_fillets.py:139`（`("Front Plane","前视基准面")`）<br>④ `mcp-server\tool_specs_batch21.py:68`（`_PLANE` 描述串，含三对）<br>⑤ `mcp-server\tool_specs_batch34.py:46`（`_PLANE` 描述串，**只列一对**） | 5 | J3 | ⚠ ★ ④⑤ **同名 `_PLANE`、内容不同** —— 同一张表，一处全、一处缺 |

---

## 三 · 单独列出：**同名不同内容**（比重复更危险）

★ 这几处不是「抄了两遍」，而是**同一个名字下已经长出了不同的说法** ⇒ 静默分叉的温床。

| 符号 | 出现位置 | 分叉内容 |
|---|---|---|
| `_PLANE` | `tool_specs_batch21.py:68` / `tool_specs_batch34.py:46` | 前者列 3 对基准面，后者只列 `Front Plane` 一对 |
| `_SEL` | `batch23:97`·`batch26:82`·`batch28:68`·`batch29:67`·`batch34:44`·`batch63:36`·`batch66:25`·`batch67:40` | **8 个文件 8 种写法**（EDGE/FACE/通用/面选择器/草图段…），只有 `batch34:44` 与 `batch23:97` 描述的是同一件事 |
| `_STUDY` | `batch26:77`·`batch28:63`·`batch29:65`（3 处逐字相同）· `batch30:58`（换成拓扑口吻） | 同名两种口径 |
| `_CFG` | `batch33:54`（带 `⚠ Leave empty…` 长注）· `batch36:43`（一句话） | 详略不同 |
| `_PATH` | `batch33:52`（含示例 `D:\\AI\\SW\\output\\part.step`）· `batch59:31`（中文 + READ-BACK 说明） | 语言与内容均不同 |
| `_SKETCH` | `batch22:69`（举 `草图1`）· `batch32:73`（举 `草图2`） | 举例不同，易被当成两套约定 |

---

## 四 · 已知例的复核（`{2, 3}` 视图类型魔数）

| 检查项 | 结果 |
|---|---|
| 魔数 `in {2, 3}` 现在还在不在？ | ★ **不在了**。`drawing_workflow.py:1800-1803` 留有注释：「★ 2026-10-03：原为魔数 `in {2, 3}`，改引单一真源 `scripts/sw_drawing_view_types.py`」 |
| 单一真源真被引了吗？ | 是。`drawing_workflow.py:12` 与 `:16` 两处 try/except import `LABELLED_VIEW_TYPES` |
| 范围内还有别处藏着同一组魔数吗？ | ★ **有一处形似的，但不是同一件事**：`subskills\solidworks-engineering-drawing\scripts\drawing_review.py:161` 的 `if len(expected) not in {2, 3}` —— 这是**期望视图数量**的集合（2 或 3 个视图），**与 `swDrawingViewTypes_e` 的 2/3 无关**。★ 已逐字读过上下文确认，不计入本表 |

---

## 五 · 数字核对

| 类别 | 条数 |
|---|---|
| 甲 · 官方枚举/常量 | 5 |
| 乙 · 领域词汇表/规格表 | 6 |
| 丙 · 官方成员名字面量 | 9 |
| 丁 · 错误码/报告字段 | 7 |
| 戊 · 同名实现重复的函数 | 19 |
| 己 · 说明文案/注释块 | 5 |
| ★ **合计** | **51** |

★ **范围最广的 3 条**：`SW_SOLID_BODY`（4 个家）· `_consumed`（9 个文件）· 基准面中英文名对（5 个家）。

---

## 六 · 如实记录：**查不到 / 未计入**

1. ★ **S1-a 的正式判据表在本仓库查不到** —— `specs\202-user-coverage-gaps\recon\` 下 18 个文件里没有 `scan-S1a*`；`grep -i "S1-a\|S1a"` 在 `specs\202-user-coverage-gaps\` 全目录 0 命中。⇒ 本表的 §一 是**自述口径**，不是引用 S1-a。若 S1-a 的口径与此不同，本表需按 S1-a 重算。
2. ★ **本次范围内没有 `sw_api_*.py`** ⇒ 那条排除规则**未生效**（已实测，非推断）。
3. **未做的检查**：跨 `scripts/` 的配对（如 `drawing_workflow.py` ↔ `scripts/sw_review.py`）**不在本段范围**，故未统计；已知例里提到的 `scripts/sw_drawing_view_types.py` 只作为单源存在被引用，不在本范围。
4. **判定为「不算重复」而剔除的**：`Param` 参数名跨批次的复用（`element_size_mm`、`tolerance_mm`、`study_name` 等）—— 那是一个声明式契约的正常多处实例化，不是「一份知识两个家」；已在本表 §一 明写剔除理由。
5. **未做的**：本次**未运行任何 SolidWorks 调用、未运行 pytest、未改动任何既有文件**；所有读数来自 `ast.parse` + 文本读，逐条行号已逐条回读原文核对（见各行括号内的行内容）。