# S1-a · 重复知识扫描（`scripts/*.py`）

> **只查不改**。本文件是本次扫描的唯一产物；扫描过程未修改任何已有文件，未跑 SolidWorks / pytest。
> 采集方式：只读 `grep` / `glob` / `read` / 只读 PowerShell（`Get-Content`、`Select-String`、`Get-ChildItem`）。

## 范围与口径

| 项 | 值 |
|---|---|
| 快照时刻 | 2026-10-03 21:05（本机时区） |
| `scripts\*.py` 总数 | **165** |
| 排除 `sw_api_*.py`（生成的反射索引） | **12**（`sw_api_cosworks` / `sw_api_dsgnchk` / `sw_api_fworks` / `sw_api_gtswutilities` / `sw_api_sldcostingapi` / `sw_api_sldtoolboxconfigureaddin` / `sw_api_sldworks` / `sw_api_swdimxpert` / `sw_api_swdocumentmgr` / `sw_api_swmotionstudy` / `sw_api_swpublished` / `sw_api_SWRoutingLib`） |
| **实际扫描文件数** | **153** |
| 找到的重复实例 | **31** |

⚠ **扫描期间文件数在变**（165 是 21:05 的快照；首次 glob 时是 162/163，`sw_drawing_create_missing.py`、`sw_drawing_expose.py`、`sw_sheet_metal_weld_entry.py` 是期间出现的）。⇒ 下面每一行都指到**具体文件:行号**，行号以快照为准；新增文件请重跑再核。

判据（任一条即算）：① 同一**魔数**在多处写死且语义相同；② 同一**枚举/常量表**在多文件各写一份；③ 同一段**判据逻辑**出现在多文件。
**不算**：纯样式重复、各自独立的小工具函数（见文末「已排查·不算重复」）。

---

## 一、重复实例表（31 条）

| # | 事实 | 出现位置(文件:行号) | 语义真相同? | 建议真源候选 | 置信度 |
|---|---|---|---|---|---|
| 1 | **基准面名候选表**（`Front Plane`/`前视基准面` 等 6 项双向别名） | `sw_part.py:57-64`（`PLANE_NAME_ALIASES` 定义）<br>`sw_assembly.py:49-56`（同名同内容的第二份）<br>`sw_surface_features.py:1056-1057`（第 3 份，内联 6 元组）<br>`sw_part.py:125-135`（`_get_plane_name_candidates`）<br>`sw_assembly.py:263`（同一张表的消费点） | **是**（三份表内容逐字相同、同序；`sw_surface_features` 那份语义亦为「按 UI 语言试基准面名」） | `scripts/sw_part.py` 的 `PLANE_NAME_ALIASES`；`sw_assembly.py` import 之 | 高 |
| 2 | **空 Callout = `VARIANT(pythoncom.VT_DISPATCH, None)`**（已知事实 12/33） | 真源：`sw_connect.py:490-492`（`create_empty_dispatch_variant`）<br>另两份自建实现：`sw_part.py:101-103`、`sw_assembly.py:59-61`<br>薄包装：`sw_surface_features.py:540-543`<br>**违反点**：同文件 `sw_surface_features.py:1059-1060` 却把裸 `None` 传给 `SelectByID2` 的 Callout | **是**（同一表达式 `VARIANT(pythoncom.VT_DISPATCH, None)`） | `sw_connect.create_empty_dispatch_variant`（已存在，两处自建实现应改为调用它） | 高 |
| 3 | **`_select_by_id()`：封 `SelectByID2` 的 9 参调用**（含 Callout 占位） | `sw_part.py:106-122`<br>`sw_assembly.py:64-80` | **是**（函数体与 docstring 逐字相同，仅所在模块不同） | `sw_part._select_by_id`（`sw_assembly.py` 改为 import） | 高 |
| 4 | **判据：选区计数只认 `GetSelectedObjectCount2(-1)` 的回读**（已知事实 8 / 496） | 真源：`sw_selection_spec.py:90-97`<br>另有一份同名的 `sw_selection.py:191-193`（签名不同：收 `ISelectionMgr` 而非 model）<br>内联重写：`sw_simulation.py:785-786`、`sw_sketch_edit_ops.py:101-102` 与 `112-113`、`sw_part.py:279-291`、`sw_surface_features.py:154`、`sw_measure.py:89-90`、`sw_loft.py:75-76` 与 `175-176`、`sw_hole_features.py:1121-1123`、`sw_review.py:544`、`sw_assembly.py:356`、`sw_drawing_create_missing.py:293-301`、`sw_drawing_expose.py:44-49` | **大体是，有一处偏离**：`sw_loft.py:76` 与 `sw_loft.py:176` 把 Type 实参写成 **`1`** 而不是 `-1`（只数一种类型）⇒ **不是同一个口径**；其余为同一表达式 | `sw_selection_spec.get_selection_count` | 高 |
| 5 | **毫米↔米换算常数 `1000` / `0.001`** | 真源：`sw_connect.py:1040-1042`（`mm()`）、`sw_connect.py:1045-1048`（`deg()`）<br>已用真源：`sw_helix.py:46,111-115`、`sw_sketch_edit.py:54,130`<br>内联重写（`× 0.001`）：`sw_part.py:1608-1609`、`sw_part.py:1660-1661`、`sw_surface_features.py:87,218,318,379,641,734`<br>内联重写（`/ 1000.0`）：`sw_wrap.py:88`、`sw_sketch_modify_ops.py:101-102,117,151-152`、`sw_surface_edit_ops.py:146,183,186`、`sw_hole_features.py:1113-1115,1135`、`sw_gear.py:283`、`sw_curve_and_split.py:310-312`、`sw_document_data.py:272`、`sw_drawing_query.py:158-159`、`sw_review.py:839,868`、`sw_hole_features.py:47,50,220-225,947,1154,1157`、`sw_drawing_expose.py:39-41` | **是**（同一换算语义；`sw_connect.py:319,352,390,464` 的 `poll_ms/1000.0` 是**毫秒→秒**，语义不同，不计） | `sw_connect.mm` / `sw_connect.deg`（已存在） | 高 |
| 6 | **声明式选择器文法：`__current_selection__` / `index:<n>` / `index:0,index:1`** | 真源：`sw_selection_spec.py:220-247`（`resolve_entity`）<br>另两份自行解析：`sw_sketch_edit_ops.py:110-124`、`sw_sketch_dimensions.py:93-105` | **是**（同一文法、同一套非法值报错口径）；但 `sw_hole_features.py:706-724` 已正确委派真源，不计 | `sw_selection_spec.resolve_entity`（两份自行解析的改为委派） | 高 |
| 7 | **`_sketch(model)`：取活动草图、取不到就抛「没有活动草图」** | `sw_sketch_dimensions.py:55-59`<br>`sw_sketch_edit_ops.py:79-83` | **是**（5 行逐字相同） | `sw_sketch.resolve_sketch` 的调用点之一抽一处共用 | 高 |
| 8 | **五级验证等级枚举 + 执行模式值域** | `LEVELS = {verified, source_verified, stitched, indexed, not_implemented}`：<br>`capabilities.py:22`、`check_union_conventions.py:43`、`audit_acceptance_criteria.py:46`<br>`VALID_MODES = {interactive, reviewed, unattended}`：<br>`capabilities.py:23`、`check_union_conventions.py:54` | **是**（5 项集合逐字相同；2 项集合逐字相同） | `scripts/capabilities.py`（该模块就是清单校验层） | 高 |
| 9 | **能力清单验收判据**（`level∈LEVELS` · `allowed_modes⊆值域` · `unattended ⇒ level=="verified"` · `verified ⇒ 有 evidence` · `provenance` 四字段） | `capabilities.py:48-61`<br>`check_union_conventions.py:419-438` 与 `263-291`<br>`audit_acceptance_criteria.py:62-80`（`PROV_FIELDS` 在 `47`） | **是**（三条 R11/R6/A2 判据各写一遍，规则文本也各写一遍） | `scripts/capabilities.py`（`check_union_conventions.py` 与 `audit_acceptance_criteria.py` 改为调用） | 高 |
| 10 | **`_checked()`：调用前用签名表校核实参个数，不符就抛** | `sw_costing.py:109`、`sw_featureworks.py:87`、`sw_pattern.py:135`、`sw_pdm.py:118`、`sw_routing.py:124`、`sw_selection.py:146`、`sw_simulation_results.py:137`、`sw_simulation_study.py:187` | **是**（docstring 与判据逐字相同；只差 arity 表变量名与 `None` 时的报错文案） | 一处共用 `_checked(table, target, member, *args)`，各模块只传自己的 arity 表 | 高 |
| 11 | **`_delta()`：特征树增量判据 —— 任一侧读不到就回 `None`，不猜**（规则 6） | 逐字相同的 4 份：`sw_curve_and_split.py:102`、`sw_ref_geometry.py:132`、`sw_surface_edit_ops.py:108`、`sw_surface_ref_ops.py:98`<br>数值差变体 2 份：`sw_drawing_create_missing.py:305`、`sw_sheet_metal_weld_entry.py:256` | **是**（前 4 份逐字相同；后 2 份是同一「读不到即降级」判据的数值版） | 一处共用 `feature_tree_delta(before, after)` | 高 |
| 12 | **`_tree_names()`：取特征树有序特征名清单（委派 `sw_part.feature_names`，失败回 `None`）** | `sw_curve_and_split.py:86-99`、`sw_ref_geometry.py:115-127`、`sw_surface_edit_ops.py:86-103`、`sw_surface_ref_ops.py:82-95` | **是**（代码逐字相同，仅 docstring 详略不同；4 份都在同一处重复记着轮 473「别自己拼一条」的教训） | 直接调 `sw_part.feature_names`，包装只留一处 | 高 |
| 13 | **标识符白名单：`^[A-Za-z][A-Za-z0-9_]{0,63}$` + `_identifier()` 校验** | 正则 3 份：`advanced_geometry.py:19`、`advanced_geometry_ocp.py:23`、`fea_analysis.py:29`<br>校验函数：`advanced_geometry.py:52-57`（名 `_id`）、`advanced_geometry_ocp.py:68-73`、`fea_analysis.py:116-121`、`fea_convergence.py:35-40` | **是，但有一处行为差异**：`fea_convergence.py:38` 用 `char.isalnum()`（**收非 ASCII 字母**）而其余三处用 `[A-Za-z0-9_]` ⇒ 同一规则、两套口径 | 一处共用 `_ID` 正则 + `_identifier()` | 高 |
| 14 | **`_now_iso()`：UTC 秒级 ISO 时间戳** | `advanced_geometry.py:30`、`advanced_geometry_ocp.py:63`、`advanced_surface_ocp.py:45`、`dfm_review.py:55`、`fea_analysis.py:39`、`fea_convergence.py:17`、`routing_review.py:33` | **是**（2 行逐字相同） | 一处共用 | 高 |
| 15 | **`_sha256()`：分块读文件算 SHA-256** | `advanced_geometry.py:47-49`（**一次 `read_bytes`**）、`advanced_geometry_ocp.py:386`、`delivery_compare.py:10`、`dfm_review.py:60-68`（名 `_sha256_file`）、`fea_analysis.py:56`、`sw_delivery.py:42-46` | **是**（同一事实，两种写法：`advanced_geometry.py` 一次全读、其余分块 1 MiB） | 一处共用分块实现 | 高 |
| 16 | **`_versioned_target()`：产物已存在就加 `_v2`/`_v3` 后缀，不覆盖** | `advanced_geometry.py:35-44`、`dfm_review.py:71-81`、`fea_analysis.py:44-53`<br>形变体（收 `out_dir/name/ext`）：`headless_cad_writer.py:47`、`headless_occt_service.py:37` | **是**（前三份逻辑逐字相同；后两份是同规则的另一签名） | 一处共用 | 高 |
| 17 | **`_finite*()`：有限数 / 正数 / 可选上限 校验** | `advanced_geometry.py:60-67`（`_positive`）、`advanced_geometry_ocp.py:76-86`、`advanced_surface_ocp.py:65-75`、`fea_analysis.py:80-90`、`fea_convergence.py:22-32`、`routing_review.py:50`、`sw_gear.py:69` | **大体是**：6 份同一判据；**参数面不同**（`advanced_surface_ocp`/`advanced_geometry_ocp`/`fea_convergence` 有 `maximum`，`fea_analysis`/`advanced_geometry` 没有；报错文案也分两套「必须是有限数值。」/「必须是有限正数。」） | 一处共用带 `maximum` 的版本 | 高 |
| 18 | **`_load_request()`：从 dict 或 JSON 文件读请求 + MiB 安全上限** | `advanced_geometry.py:74-81`（4 MiB）、`advanced_surface_ocp.py:50-58`（4 MiB）、`advanced_geometry_ocp.py:132-140`（1 MiB）、`fea_analysis.py:65-73`（64 MiB）、`fea_convergence.py:43-55`（128 MiB） | **部分**：读取/校验骨架相同，**上限值各不相同且是有意的**（1/4/64/128 MiB）⇒ 上限本身不是重复，重复的是「怎么读 + 怎么卡上限」这段骨架 | 一处共用读取器，上限作为参数传入 | 中 |
| 19 | **仿真枚举 `SWS_RESTRAINT_TYPES`（10 项）+ `SWS_FORCE_TYPES`（3 项）** | `sw_simulation.py:158-176`<br>`sw_simulation_loads.py:142-159` | **是**（两组表逐项同值同注释，仅缩进不同） | `sw_simulation.py` 或新建一个仿真枚举真源模块 | 高 |
| 20 | **仿真枚举 `SWS_ANALYSIS_STUDY_TYPES`（12 项，含 `topology_static = 13` 与「10/11/12 刻意不收录」的说明）** | `sw_simulation.py:191-205`<br>`sw_simulation_study.py:102-114` | **是**（逐项同值；末尾注释措辞不同，语义相同） | 同上 | 高 |
| 21 | **仿真枚举 `SWS_MESH_TYPES`（5 项）** | `sw_simulation.py:183-189`<br>`sw_simulation_study.py:117-123` | **是**（逐项同值） | 同上 | 高 |
| 22 | **`SHEET_PSEUDO_VIEW_TYPE = 1`：「图纸本身」那个不是真视图** | `sw_drawing_query.py:167-169`<br>`sw_drawing_create_missing.py:151-155`（其注释自认「与 `sw_drawing_query.SHEET_PSEUDO_VIEW_TYPE` 同一个事实、同一份官方页」）<br>**已有真源未被用上**：`sw_drawing_view_types.py:42`（`SW_DRAWING_SHEET = 1`） | **是**（同一个官方枚举值；`sw_drawing_create_missing.py:88` 已经从该真源 import 了 `SW_DRAWING_AUXILIARY_VIEW`，却仍自写 `SHEET_PSEUDO_VIEW_TYPE`） | `scripts/sw_drawing_view_types.py`（该文件自称「单一真源」） | 高 |
| 23 | **`_file_signature()`：`(st_size, st_mtime_ns)` 作「本轮真产物」证据** | `sw_delivery.py:35-39`<br>`sw_export.py:237-243`（同名、docstring 同义）<br>内联变体：`delivery_compare.py:27-36` | **是**（两份同名函数逻辑相同；内联变体同语义） | `sw_delivery.py` | 高 |
| 24 | **Win32 模态框检测：按 `#32770` + 同 PID + 可见顶层枚举** | `sw_connect.py:230`（`_DIALOG_CLASS`）+ `272-296`（`_dialog_handles`）+ `395-448`（`residual_dialogs`）<br>`sw_gui_modal.py:50`（`_DIALOG_CLASSES`）+ `53-76`（`find_modals`） | **不完全相同**：类名常量相同，但 `sw_gui_modal.py` 的判据**有意更宽**（`cls=="#32770"` **或** 有 owner，另加 60×40 最小尺寸过滤）—— 其文件头 `15-31` 行把这个差异写明 ⇒ 判据本身不同 | 无单一真源可并（判据有意分叉）；**可合并的只有 `"#32770"` 这个常量** | 中 |
| 25 | **PrintWindow 抓窗口自身（ctypes `restype`/`argtypes` 全套 + `BITMAPINFOHEADER`）** | `sw_capture.py:36-109`（`capture(hwnd, path)`）<br>`sw_jlcfa_locate.py:368-...`（`capture_window(hwnd, path)`，内联同样的 ctypes 声明） | **是**（同一 GDI 抓窗实现；两处都注明「64 位下 GDI 句柄是 64 位，必须显式声明 restype/argtypes」） | `sw_capture.capture` | 高 |
| 26 | **整屏取证截图 `ImageGrab.grab().save(path)`** | `sw_gui_modal.py:142-147`（`screen_png`）<br>`sw_jlcfa_locate.py:360-365`（`capture_front`） | **是**（函数体逐字相同；docstring 也都写「取证一律用整屏；PrintWindow 会丢客户区外的浮窗」） | `sw_gui_modal.screen_png` | 高 |
| 27 | **插件范围提示控件判据：`ct == "Text" and t.startswith("[") and "~" in t`** | `sw_jlcfa_select.py:204`<br>`sw_jlcfa_fill.py:568` | **是**（同一条件式、同一含义：识别插件自报的 `[min~max]/step` 提示） | jlcfa 系列抽一处共用 | 高 |
| 28 | **插件空态占位串 `"请输入产品型号"`（用它把「空的型号输入框」排除掉）** | `sw_jlcfa_fill.py:519`<br>`sw_jlcfa_fill.py:580`<br>`sw_jlcfa_select.py:196` | **是**（同一串、同一用途）；同族事实 `"【去填写】"` **已**抽成常量 `sw_jlcfa_fill.py:45` ⇒ 说明本仓认这个模式，只是这一条没跟上 | 与 `PLACEHOLDER` 并列抽成 jlcfa 系列常量 | 高 |
| 29 | **六向命名选择器 `("+x","-x","+y","-y","+z","-z")`** | `sw_geometry_selectors.py:79`（`DIRECTION_SELECTORS`）+ `81-85`（`_AXIS` 单位向量表）<br>`sw_simulation.py:793`（`FACE_SELECTORS`）+ `839-846`（外法向面心表） | **部分**：6 项名字集合逐字相同（`sw_geometry_selectors.py:161-175` 自认「同一套外法向命名」），但**解析目标不同**（单位向量 vs 包围盒某面中心点）⇒ 名字表重复、语义不同 | 名字表归一，解析函数各自保留 | 中 |
| 30 | **`_expand_path()` 展开用户目录+环境变量取绝对路径 · `_ensure_parent_dir()` 建父目录** | `_expand_path`：`sw_connect.py:627-629`、`sw_review.py:321-323`<br>`_ensure_parent_dir`：`sw_connect.py:632-635`、`sw_export.py:21-25` | **大体是**：`sw_export.py:21` 那份**少了 `expandvars/expanduser`**（只 `abspath`）⇒ 同一函数名、两套口径 | `sw_connect._expand_path` / `_ensure_parent_dir` | 高 |
| 31 | **`_configure_stdio_utf8()`：把 stdout/stderr 切到 UTF-8** | `sw_macro_guard.py:25`、`sw_preflight.py:29`、`validate_mcp.py:69`、`validate_skill.py:13` | **是**（逐字相同）—— 但它同时像「各自 CLI 的独立引导」，**是否该合并取决于是否允许抽一个共享模块** | 一个 `scripts/_stdio.py` 之类的小共用模块 | **低**（本条可能落在「各自独立的小工具函数」排除项里） |

---

## 二、按判据分类小结

| 判据 | 条数 | 对应行 |
|---|---|---|
| ① 同一魔数写死 | **2** | #2（`VT_DISPATCH`）、#5（`1000` / `0.001`）、#22（`= 1`）、#28（占位串）、#29（选择器名集合） |
| ② 同一枚举/常量表多份 | **7** | #1、#8、#19、#20、#21、#22、#29 |
| ③ 同一段判据逻辑 | **22** | 其余（#3、#4、#6、#7、#9、#10、#11、#12、#13、#14、#15、#16、#17、#18、#23、#24、#25、#26、#27、#30、#31） |

> 分类按「主要命中哪一条」记，一条可能同时命中多条。

## 三、判据逻辑重复最密的四个簇（按「同一个根事实」归并）

1. **「不许静默成功」簇** —— #4（选区回读）、#6（选择器解析）、#7（活动草图）、#11（特征树增量）、#12（特征树名单）、#28（空态控件）。共同事实：**判据必须能回读，读不到就降级成 `None`/报错**。
2. **CAD Studio 中立层工具函数簇** —— #13、#14、#15、#16、#17、#18。这 6 条是同一族「同一段校验/工具代码在 4~7 个 `*.py` 各写一份」，集中在 `advanced_geometry*.py` / `advanced_surface_ocp.py` / `fea_analysis.py` / `fea_convergence.py` / `routing_review.py` / `dfm_review.py`。
3. **COM 调用护栏簇** —— #10（`_checked` arity 校验）、#2（空 Callout）、#3（`_select_by_id`）。
4. **清单验收簇** —— #8、#9（五级枚举 + R6/R11/A2 判据，三个文件各写一遍）。

---

## 四、已排查 · **不算**重复（避免误报）

| 疑似对 | 为什么不计入 |
|---|---|
| `sw_view.py:288/294` `get_view_scale`/`set_view_scale`（用 `Scale`） vs `sw_drawing_view.py:694/706`（用 `ScaleRatio`，并在 docstring 里写「`Scale` 是**臆造的成员名**」） | **不同接口**：`sw_view.py:199` 的来源块声明自己面向 **`IModelView`**（三维视图），`sw_drawing_view.py` 面向 **`IDrawingView`**（工程图视图）；`sw_view.py:186` 明写「本模块不混」。⇒ 名字撞车，事实不同。 |
| `sw_connect.py:319/352/390/464` 的 `poll_ms / 1000.0` vs #5 的 mm→m | 语义不同（毫秒→秒），已排除。 |
| `sw_selection.py:146`、`sw_costing.py:109` 等 8 份的 `_checked` 里的 `目标对象为 None` 文案 | 文案各带本模块自己的 COM 对象名，**判据**（arity 不符就抛）才是重复的部分 → 已按 #10 记一条，不按文案逐条记。 |
| `_require()`（`sw_assembly_doc.py:238` / `sw_simulation_loads.py:226` / `sw_simulation_loadprops.py:77` / `sw_sketch.py:157` / `sw_view.py:174`）、`_as_list`（`sw_hole_features.py:436` / `sw_drawing_create_missing.py:170` / `sw_sketch.py:163`）、`_tree_names` 的 `_read` 变体 | 判为「各自独立的小工具函数」（各自报文案 / 各自入参形态），按排除项不计。 |
| `sw_api_*.py` 之间的重复 | 任务已明确排除（生成的反射索引）。 |

## 五、限度声明

- **指不到行号的**：无 —— 31 条全部指到 `文件:行号`。
- **未核实项**：#13 中「`fea_convergence.py:38` 的 `isalnum()` 收非 ASCII 字母」是由 `re` 模式与 `str.isalnum()` 的标准库语义推出的，**本轮未跑 Python 实证**；#5 中 `sw_drawing_expose.py:40` 自称「整个仓库里这一处负责工程图坐标的换算」**与本表统计不符**（已列 20+ 处内联换算），此处只陈述不符，不判定该注释的意图。
- **未跑** SolidWorks / pytest / 任何门禁；**未修改**任何已有文件。