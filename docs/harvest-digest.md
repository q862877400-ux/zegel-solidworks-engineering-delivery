# 交付状态摘要（**生成物**）

> ⚑ **本节不要手改** —— 由 `tools/gen_harvest_digest.py` 从真源生成；
> 新鲜度由 `scripts/check_digest_freshness.py` 守（重跑必须逐字节相同）。
>
> **为什么单独出一份**：`AGENTS.md §一 A8` 要求报告写「并入了什么 / 仍空缺什么 / 为什么」，
> 而 `harvest-report.md` 的 §二 正文停在「截至第 12 轮」。**手写续写会立刻腐坏** ——
> 所以状态这部分**从真源生成**，报告本体只链接本文件。
>
> 数据源：`capabilities.yaml`（能力/等级/出处/证据）· `git log`（提交构成）·
> `scripts/check_*.py`（门禁栈）· `docs/union-not-doing.json`（不做 + 原因）·
> `docs/family-coverage.json`（官方接口族的**零调用缺口**，见 §4.3）。

## 一 提交构成（**怎么看** —— 本节刻意不放假数字）

> ⚠⚠ **本节不放「提交数 / 主题分布」**（2026-10-01 轮 68 实测出的结论，值得记下来）：
> 本文件是**生成物 + 新鲜度门禁**（重跑必须逐字节相同），而那两个量**每提交一次就变**，
> 且**产生本文件的那次提交无法自计**（自指）。
>
> **走过的三条路，全部失败**：
> 1. 直接数 `HEAD` ⇒ 每提交一次**滞后 1**；
> 2. 借用「`git status` 非空就 `+1`」预测 ⇒ **提交数对了，主题分布照样滞后**
>    （生成器**无法预测**「生成它那次提交」的主题是 `feat` 还是 `docs`）；
> 3. 「全部基于 `HEAD`」+ 写明口径 ⇒ **提交本文件后 `HEAD` 又变了** ⇒ 门禁照样 FAIL。
>
> ★ **根因**：本文件的内容**依赖提交历史**，而它自己**会改变提交历史**。
> ⇒ **正解不是再换一种口径，而是不把易变量放进这个产物里** ——
>   **不靠预测去凑一个看起来新鲜的数字**（那正是本项目反复记录的坏做法）。

**要知道提交构成，跑这两条**（数字永远是当下真的）：

```bash
git rev-list --count origin/main..HEAD          # 相对上游的提交数
git log --format=%s -400 | sed 's/(.*//;s/:.*//' | sort | uniq -c | sort -rn  # 主题分布
```

> ⚑ 本项目**只做本地提交**，未推任何远端（见 `docs/union-not-doing.json` 的「对外发布」条）。
> ⚑ 报告本体的偏离数字（文件数 / 行数 / 提交数）由 `scripts/check_report_freshness.py` 用
>   **「`git add -A && git commit` 之后会变成什么」** 的口径守着 —— 那三个量**可预测**
>   （`git status` 非空就 `+1`），所以放报告正文是稳的；而**主题分布不可预测**，哪里都不放。

## 二 能力状态（硬依据：`capabilities.yaml`）

共 **83** 条能力。

| `level` | 条数 | 含义 |
|---|---|---|
| `verified` | 71 | **有我们自己的运行证据**（`evidence` 非空） |
| `stitched` | 11 | 已缝合，**缺我们自己的运行证据** |
| `not_implemented` | 1 | 明确未实现 |

| `source` | 条数 | 含义 |
|---|---|---|
| `original` | 53 | **本项目自研**（护城河域等） |
| `upstream` | 18 | 上游 `wzyn20051216/solidworks-automation-skill` |
| `mixed` | 11 | 多家来源混合 |
| `undetermined` | 1 | **归属未定**（按铁律 5 不猜） |

## 三 `verified` 的逐条运行证据（**A4 的硬证据**）

`level: verified` 的定义是「**有我们自己的运行证据**」——不是「代码是我们写的」。
下表逐条给出那条证据（可跑的命令 / 可读的文件）。

| 能力 | 运行证据 |
|---|---|
| `requirements_planning` | · `pytest tests/test_engineering_orchestrator.py（需求阶段与阶段编目）` |
| `solidworks_addin_host` | · `pytest tests/test_cad_reliability.py（加载项宿主状态）` |
| `part_and_features` | · `python 真机（轮 405）★ **PASS** —— 24h 计划 v2 段 3 收尾：`solidworks_add_dimension`（`sw_part.add_dimension_report`）。★★ 判据用了事实 53 的处方：**把猜测变成一张穷举表** —— 对盒体 12 条边的**两两共 66 对**逐一试。真机（走 `sw_guard`，7.1 s 无弹窗）：成功的边对是 `[0,1] [0,2] [0,3] [0,4] [0,7] [0,8] [0,11] [1,2]`（**8/8**，到上限就停）—— ★★ **含边 0 的组合都成，连 `[0,1]` 这种相邻边都成**。证据 output/dimension-edge-pairs-evidence.json。★★ 而轮 400 用**同样**的 `[0,1]` 却失败 —— 唯一差别是本轮**每次选之前都 `ClearSelection2(True)`** ⇒ ★ 真因是**探针选区不干净**，不是能力坏了。⚠ **已知限制（未隔离）**：同一包装在**板 + 凸台**的模型上失败（连试 3 次后按事实 53 停止隔离）；官方另注「only use on visible documents」且尺寸**按位置**放置。`<br>· `python 真机（轮 395）★ **PASS** —— objective② 补真缺 `undo`：`scripts/sw_session.py` 新增 `undo_report`（官方 `IModelDoc2.EditUndo2(int Steps)`，**1 参**，回 `void` ⇒ 判据是**特征树退回**）。真机（走 `sw_guard`，5.88 s 无弹窗）：前置 `凸台-拉伸1`（树 **7**）· 负例 `steps=0` 被入口拒 · **`undo_report(doc, 1)` ⇒ 特征树 7 → 6 · `undone: true` · `removed_features: ["凸台-拉伸1"]`** ⇒ `verdict: pass`。证据 output/undo-evidence.json。MCP 工具 **`solidworks_undo`**。★ 意义：我们的工具会**改模型**，改错时没有撤销就只能重来（★ 而 `EditUndo2` 撤的是**会话里的动作**、不区分来源 ⇒ **只在我们自己的改动之后调用**）。`<br>· `pytest tests/test_cad_reliability.py（零件与特征）`<br>· `python tools/verify_bbox_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1：80×60×50 mm 盒子 ⇒ `get_bounding_box` 得 `[80.0, 60.0, 50.0]`，**偏差 0.00e+00**，**8/8 通过**，证据落 output/bbox-smoke-evidence.json）`<br>· `python tools/verify_ellipse_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1：半径 25 的圆 ⇒ 边界框跨度 **50 mm**（量准单位）；椭圆建成并 **`get_ellipses` 读回**，**11/11 通过**，证据落 output/ellipse-smoke-evidence.json）`<br>· `python tools/verify_centerline_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1：`sketch_centerline` 建成 → `get_sketch_segments` **读回 1 段**；**再测单位**：半径 25 的圆 ⇒ 边界框 **50 mm** ⇒ **官方文档的「in meters」是错的**；**8/8 通过**，证据落 output/centerline-smoke-evidence.json）`<br>· `python tools/probe_getlines_count.py（**真机**：画 **1/2/3** 条直线 ⇒ `get_lines` 读回 **12/24/36** 个 `float` ⇒ **每条 12 个**，元素类型是 `float`）`<br>· `python tools/probe_sketch_getter_shapes.py + probe_spline_creation.py + probe_spline_redraw.py（**真机**，SW 2026 SP4.1 / 34.4.1）：**按类型取法全是数值数组** （line/arc/ellipse = **12 / 16 / 22** 个 `float` 每实体，画 1/2 个 ⇒ 12/24 · 16/32 · 22/44）；★★ 并查出 **`sketch_spline` 是静默空操作** —— `CreateSpline2` 返回 `None`、段数 **0**，**重绘后仍是 0**（排除了官方 Remark 的「必须重绘」解释）⇒ 已改成**失败即抛**`<br>· `python tools/probe_slot_and_point_shapes.py（**真机**，SW 2026 SP4.1 / 34.4.1）：★ **推翻轮 141 的一概而论** —— `get_sketch_slots` 画 1/2 个 ⇒ **1/2** 个 `CDispatch`；`get_sketch_points` 画 1/2 条直线 ⇒ **2/4** 个（**每条线两个端点**）⇒ **这两条返回对象列表**，而 `get_lines`/`get_arcs`/`get_ellipses` 返回数值数组`<br>· `python tools/verify_dome_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1：`insert_dome(8)` 在 100x60x20 的板顶面建成 ⇒ 边界框**逐分量**变化 Z 20 → **34.2222**；特征树 19 → 20；**9/9**，其中两条**如实标注**为「未查明」与「不可达」）`<br>· `python tools/audit_get_com_member_semantics.py（**结构审计**：471 个无实参 get_com_member 调用点 ⇒ **193** 处的成员在出厂反射里有**零参重载**（探测调用会执行），其中绝大多数是只读 getter；按「名字像改东西」缩清单得 **24** 处）+ tools/diag_insert_dome.py（真机定位）`<br>· `python tools/probe_window_vs_graphics.py + `_list_sw_windows_all.py`（**真机**，轮 148）：SolidWorks PID 的顶层窗口 **49 个，其中可见的只有 1 个（159x27）** ⇒ `sw_connect.residual_dialogs` 的**两个口径对比**：默认扫到 **49** 个窗口、旧口径（`IsWindowVisible`）只扫到 **1** 个 ⇒ **漏检 48/49**`<br>· `python -m pytest tests/test_modal_dialogs_can_fire.py（**2 passed**）：起一个**真的 `#32770`**（`tools/fake_modal_dialog.py`，**故意不置 `WS_VISIBLE`**）作靶子 ⇒ ★ 新口径**抓得到**它、★ 旧口径（`only_visible=True`）**确实漏掉**它 ⇒ **「漏检」从说法变成了可复现的演示**`<br>· `python tools/verify_composite_curve_smoke.py（**真机**，轮 151）：**阴性结果** —— `IModelDoc2.InsertCompositeCurve()` 返回 **False**，**根因是前提没满足**（真机上两次 `start_sketch`+`end_sketch` **只留下 1 个草图** ⇒ 选不出 2 个草图给它合成）`<br>· `python tools/probe_add_relation_forms.py（**真机**，轮 161，2 条直线的草图）：★ **找到 `AddRelation` 的可行调用形态** —— `list`/`tuple` 报 `com_error 0x80010105` 且计数不变；**`VARIANT(VT_ARRAY|VT_DISPATCH, [实体…])` ⇒ 无错、`GetRelationsCount` 3 → 4**。⇒ `sketch_relations.add_relation` 已按此修（它此前**从没在真机上跑通过**）。`<br>· `python 真机（轮 323）★ **旋转轴的判据**（证据 output/revolve-axis-evidence.json · revolve-axis-fixed-evidence.json）：轴 = **草图里的线段**，类型名 **`EXTSKETCHSEGMENT`**（★ **不是** `SKETCHSEGMENT`），mark **4 或 16**（★ 两个都能建）⇒ 建成 **`旋转1`** · type=**`Revolution`**（★ 四种组合 4/4）；Є 同草图传轴 ⇒ 建成（★ 而修复前 `axis_sketch_name` 是**声明了却从未使用的死参数**）`<br>· `python 真机（轮 331）★ **包覆 PASS 3/3**：建成 **`包覆1`**·类型名 **`Emboss`**（★ 判据 = **读返回对象**的 Name 与 GetTypeName2；★ 而 `feature_names()` 前后 diff **是空的**）· 证据 output/wrap-evidence.json · wrap-returned-object.json`<br>· `python 真机（轮 338）★ **传感器读取 PASS 3/3**：空零件 / 有几何的零件 / 带外部参考的示例图 —— 三处 `ok=True` · `count=0` · `errors=[]`（★ 遍历不炸）· 证据 output/sensor-evidence.json`<br>· `python 真机（轮 339）★ **文档单位 PASS 4/4**：`GetUnits()` ⇒ **`(0, 1, 8, 2, 0)`**（★ 与官方 Remarks 的 5 元组名对得上）⇒ `LengthUnit = 0` = **`swMM`** · `is_mm = true`；对照源 `ISldWorks.GetUserPreferenceIntegerValue(47)` ⇒ **0**；`doc_matches_system_default = true`· 证据 output/units-evidence.json` |
| `external_spur_gear_geometry` | · `pytest tests/test_cad_reliability.py（外部直齿锥齿轮几何）` |
| `holes_and_finishing` | · `python 真机（轮 401）★ **PASS 4/4** —— 24h 计划 v2 段 4（孔族）：`solidworks_hole_pattern`（`scripts/sw_hole_features.hole_pattern_report`）。它把 `create_hole_pattern` 的 **`creator` 可调用对象**换成**具名的 `kind`**（★ MCP 层给不出函数）。真机（走 `sw_guard`，14.4 s 无弹窗）：**4 个通孔 ⇒ requested=4 · holes=4 · 特征树 7 → 15**（`孔_1`..`孔_4`）；三条负例全部被拒（counterbore · blind 缺 depth_mm · 空孔位表）。证据 output/hole-pattern-evidence.json。★ 同族的 `configure_straight_tap` / `configure_tapered_tap` **不挂** —— 它们吃 **COM 元素**，★ 而本仓**没有路径能从孔特征拿到它**（只在 mock 测试里出现过）⇒ MCP 层给不出实参。`<br>· `pytest tests/test_sw_hole_features.py（孔特征与修饰）`<br>· `python tools/verify_hole_standards_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1：`list_hole_standards` → 15 条 · `list_fastener_types('ANSI Inch')` → 14 条 · `list_fastener_table_types` → [0,1,2]，**11/11 通过**，含「**去掉热身就会失败**」的反向验证，证据落 output/hole-standards-smoke-evidence.json）`<br>· `python 真机（2026-10-01 轮 268）：★ 声明式建通孔 **verdict: pass** —— 特征树 7→9（新增 草图2 + 通孔）· center_sent_m=[-0.02, 0.0]；★ 证据 output/hole-by-selection-evidence.json` |
| `parameter_updates` | · `pytest tests/test_cad_reliability.py（参数更新回读）` |
| `custom_properties_and_bom` | · `pytest tests/test_cad_reliability.py（自定义属性与 BOM）` |
| `pack_and_go` | · `pytest tests/test_sw_delivery.py`<br>· `pytest tests/solidworks_week3_delivery_regression.py（Pack and Go 交付）` |
| `assembly_and_mates` | · `pytest tests/test_sw_assembly_doc_contract.py`<br>· `pytest tests/test_sw_assembly_aliases.py（装配与配合）`<br>· `python tools/verify_in_context_reference_smoke.py（**真机**，轮 161，2 零件 + 1 装配）：★ `edit_part_in_context` **已验证生效** —— `EditPart2` 返回 `-1` 且 `GetEditTarget` **非空**；`exit_edit_part_in_context` 调通；`list_external_file_references_count` 基线读回 **0**。⚠ **判据①②（关系数 N→N+1 · 外部参考 0→≥1）还没绿**（`add_relation` 调用形态未解决）⇒ **外部参考还没真的建立，未取证**（8/11）。` |
| `motion_study` | · `pytest tests/test_sw_motion_audit.py（旋转马达创建与结果审计）` |
| `drawing_dimension_insertion` | · `pytest tests/test_cad_reliability.py（工程图尺寸插入回读）` |
| `drawings_and_bom` | · `pytest tests/test_delivery_compare.py`<br>· `pytest tests/test_drawing_subskill.py（工程图与 BOM）` |
| `export_delivery` | · `python 真机（轮 403）★ **PASS** —— 24h 计划 v2 段 6（导出）：`solidworks_export_image`（`sw_export.export_image_report`）。真机（走 `sw_guard`，4.0 s 无弹窗）：一张 PNG ⇒ **`exists=true` · `size_bytes=67997` · `grew_or_created=true`**；负例（非法目录）⇒ `ok=false`。★ 判据**复用本模块既有的 `_export_report`**（回读文件：存在且 size>0，并记 `size_before` / `grew_or_created`）—— 不另造一套。证据 output/export-two-evidence.json。★★ 同轮真机抓到一个真 bug 并修掉：`export_to_image` 里用了 `out_i4()`（标量出参包装）而本模块**漏了导入** ⇒ 一调就 `NameError`（★ **而这正是它一直没被挂的原因**）。`<br>· `pytest tests/test_delivery_compare.py（导出交付）`<br>· `python tools/verify_bmp_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1：`export_to_bmp(model, path, 800, 600)` 建成 ⇒ **读回 BMP 头（偏移 18/22，小端 int32）尺寸 == 800x600**（**定量往返**，空操作满足不了）；官方 Remarks 那条也验了 —— 宽高 ≤ 0 ⇒ 读回 (1460, 1049) 即**窗口尺寸**；扩展名不是 `.bmp` ⇒ ValueError；**8/8 通过**，证据落 output/bmp-smoke-evidence.json）`<br>· `python tools/verify_png_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1：`export_to_image` 出 **PNG 129437 字节**（魔数 `89 50 4E 47…` + `IHDR` 尺寸 **1232x1049**）与 **JPG 54431 字节**（魔数 `FF D8 FF`）；**9/9 通过**，证据落 output/png-smoke-evidence.json）`<br>· `python tools/probe_dwg_magic.py（**真机**，轮 156，钣金件 60x40x1 mm 已保存到 output/）：**读魔数**取证 —— `.dxf` ⇒ **20208 字节**，头部 `  0\r\nSECTI` ⇒ **DXF** ✓；`.dwg` ⇒ **272032 字节**，头部 `AC1015` ⇒ **真 DWG（AC1015 = AutoCAD 2000 / R2000）** ✓。★ 结论：`export_to_dxf` 的「DXF/DWG」是**名实相符**的（正面结论）。★ 另记前置条件：**零件路径要求「钣金件 + 必须先保存」** —— 普通拉伸件会报`ValueError: 导出展开 DXF 前必须先保存钣金零件`（**错误清晰、是对的**）。`<br>· `python tools/probe_export_magic_matrix.py（**真机**，轮 157，钣金件 60x40x1 mm 已保存）：**逐格式读文件头** ⇒ **9/10 名实相符** —— STEP `ISO-10303-21` · STL `stlbn`（二进制）· IGES `SolidWorks IGES file` · Parasolid `**ABCDEFGH…` · DXF `  0\r\nSECTION` · DWG `AC1015` · PNG `\x89PNG` · JPEG `\xff\xd8\xff\xe0…JFIF` · BMP `BM`；★ **`pdf` 在零件上失败**：`AttributeError: <unknown>.GetSldWorksObject``<br>· `python tools/probe_pdf_on_drawing.py（**真机**，轮 158，工程图 1 张图纸已保存）：★★ 修好后 `export_to_pdf` 成功 ⇒ **39830 字节 · 头部 `%PDF-1.4` · 页数 = 1**（数 `/Type /Page`）⇒ 定量证据；★ 同时 `export_to_dxf(.dwg)` 在**工程图**上 ⇒ **279450 字节 · 头部 `AC1015`**（真 DWG）⇒ 轮 156 那条「只测钣金件」的限度补上了。` |
| `headless_open_format_writing` | · `pytest tests/test_headless_cad_writer.py（**7 passed**；覆盖非 OCP 的全部写出格式：.cadstudio.json / STL / OBJ / DXF / SVG / PDF / PNG —— 含 PNG 魔数、%PDF、<svg、STL solid、OBJ `\nf `、previewManifest，以及**输入文档只读**与 **dwg 必须 blocked 且不产文件**）`<br>· `pytest tests/test_mcp_headless_open_format.py（**8 passed**；⭐ **它验的是 MCP 层的参数传递** ——OCP 后端由 `monkeypatch.setattr` 替换为假实现，**不代表 OCP 真能跑**，见本条 limitations 末条）` |
| `geometry_and_delivery_review` | · `pytest tests/test_delivery_compare.py（几何与交付复核）` |
| `dfm_checks` | · `python tools/verify_dfm_e2e.py（**11/11 通过 · verdict: pass**；证据 D:\AI\SW\output\dfm-evidence.json）—— **故意造违规**逐条触发 limitations 的三句：四种工艺都识别 · **单位归一**（mm/inch 结论一致）· **Profile 能力交集**（窄 profile 把 Al7075 判为 `profile_material_capability` 越界）· **B-Rep 证据绑定**不崩 · **缺 bendRadius/kFactor/材料 ⇒ `blocked` + `missingInputs` 点名** · `manualReviewRequired is True` · **`limitations` 里写出「DFM 规则检查不等于制造认证」** · `brepEvidence.available` 显式给出可得性`<br>· `pytest tests/test_dfm_review.py tests/test_dfm_queue_worker.py（**19 passed**）` |
| `configurations_and_design_tables` | · `pytest tests/test_cad_reliability.py（配置与设计表）` |
| `sheet_metal` | · `pytest tests/test_sw_sheet_metal.py`<br>· `pytest tests/solidworks_sheet_metal_regression.py（钣金）` |
| `weldments` | · `python 真机（轮 428）★ **PASS** —— **结构构件**（焊件族第一条）。真机（走 `sw_guard`，无弹窗）：前视基准面上一段 100 mm 直线作路径 + **GB 方管轮廓**（`GB\square-rods.sldlfp`）⇒ **建成 `square-rods (1)`**，★ 判据是**特征树**（不是计数）：`new_type_names` = **["WeldMemberFeat", "WeldmentFeature"]**。证据 output/structural-member-evidence.json。★★ 而本轮探查**推翻了**一条既有结论：`capabilities.yaml` 里轮 364 记的「**本机没装焊件轮廓库**」★ **不成立** —— 本机 `C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\weldment profiles` 下有 **111 个** `.sldlfp`（ansi / GB / iso / DIN / JIS …）。★ 工具不读选区也不依赖选中状态：它自己按**草图名**取线段、建构件、并**用特征树回读**。`<br>· `pytest tests/test_cad_reliability.py（焊件）` |
| `simulation_and_fea` | · `pytest tests/test_fea_analysis.py（CalculiX / Elmer 求解链）`<br>· `**可跑的真机证据**：`python tools/capture_simulation_evidence.py` （2026-10-01 起；期望 `verdict: pass`，证据落 `output/simulation-evidence.json`）`<br>· `⚑ 2026-10-01 真机整链（SW 2026 SP4.1 / 34.4.1，100×60×20 mm 单实体板）：赋材料 → 按**面坐标**选面 → 夹具 → 载荷（`Count == 2`）→ `CreateMesh`（**7,310 个单元**）→ `RunAnalysis`（1 秒）→ **`study.Results` 非空、`GetPlotCount == 4`、`GetPlotNames == ('品质1','应力1','位移1','应变1')`**。**已复现两次。**` |
| `autocad_headless_preview` | · `pytest tests/test_headless_cad_writer.py（**7 passed**）—— 覆盖 limitations 承诺的每一句：PNG（**魔数** `\x89PNG` + IHDR 尺寸）· SVG/PDF/STL/OBJ/DXF 回退 · PreviewScene JSON 与 previewManifest · **`dwg` 必须 blocked 且磁盘上不出现任何 dwg 文件**（杜绝「假装写了 DWG」）· **输入文档只读**（sha256 与 mtime 不变）` |
| `dxf_preview_scene` | · `python tools/verify_dxf_preview_e2e.py（**15/15 通过 · verdict: pass**；证据 D:\AI\SW\output\dxf-preview-evidence.json）—— 逐条判过 limitations 承诺的四件事：白名单实体（3DFACE 只进 warnings）/ 图层计数 / 几何边界 / **拒绝覆盖** + **源 DXF 只读** + CLI 入口` |
| `autocad_script_backend` | · `pytest tests/test_acad_script_backend.py（AutoCAD 脚本后端）` |
| `autocad_dotnet_backend` | · `pytest tests/test_acad_dotnet_preflight.py（AutoCAD .NET 预检）` |
| `topology_optimization` | · `python tools/capture_topology_evidence.py（真机闭环，落 output/topology-evidence.json）`<br>· `pytest tests/test_sw_topology_contract.py（8 条契约测试，无 COM）` |
| `costing` | · `python tools/verify_costing_e2e.py（⇒ verdict: pass；证据 output/costing-evidence.json）` |
| `helix_and_spiral` | · `python tools/verify_helix_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1：新零件 → 进草图 → 画圆 → 选中 → 建螺旋线 → **读回定义** → 关件不保存，**13/13 通过**，证据落 output/helix-smoke-evidence.json）`<br>· `pytest tests/test_sw_helix_contract.py（**契约测试，无 COM**）` |
| `equations` | · `python tools/verify_equation_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1：新建临时零件 → 加方程式 → 列 → 求解 → 关件不保存，**5/5 通过**，证据落 output/equation-smoke-evidence.json）`<br>· `pytest tests/test_sw_equation_contract.py（**10 条契约测试，无 COM**）` |
| `sketch_query` | · `python 真机（轮 399）★ **PASS** —— 24h 计划 v2 段 3：`solidworks_current_sketch_name`（读当前活动草图名）。真机（走 `sw_guard`）：草图打开时回 **「草图1」**（**真名**，不是 English fallback）；草图**关闭后** + 自定义回退值 ⇒ 回**那个回退值**（★ 验证的是**已文档化的局限**：★ 回退值 ≠ 真名 ⇒ 别拿它去按名取草图）。证据 output/part-read-dimension-evidence.json（`verdict: pass` 4/4）。★ 同轮分诊补了**第四/五层证据**：`*_report` 包装已暴露⇒不是缺口（此前把 `sw_selection_spec` 的 2 条误判为缺口）；**空存根**（`pass`-only）⇒不做。`<br>· `python tools/verify_sketch_getters_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1：新零件 → 进草图 → 画 1 条线 + 1 段弧 → 逐个调取法 → 退草图 → 关件不保存，**17/17 通过**，证据落 output/sketch-getters-smoke-evidence.json）`<br>· `pytest tests/test_sw_sketch_contract.py（**12 条契约测试，无 COM**）`<br>· `python tools/probe_sketch_getter_shapes.py + probe_spline_creation.py + probe_spline_redraw.py（**真机**，SW 2026 SP4.1 / 34.4.1）：**按类型取法全是数值数组** （line/arc/ellipse = **12 / 16 / 22** 个 `float` 每实体，画 1/2 个 ⇒ 12/24 · 16/32 · 22/44）；★★ 并查出 **`sketch_spline` 是静默空操作** —— `CreateSpline2` 返回 `None`、段数 **0**，**重绘后仍是 0**（排除了官方 Remark 的「必须重绘」解释）⇒ 已改成**失败即抛**`<br>· `python tools/probe_slot_and_point_shapes.py（**真机**，SW 2026 SP4.1 / 34.4.1）：★ **推翻轮 141 的一概而论** —— `get_sketch_slots` 画 1/2 个 ⇒ **1/2** 个 `CDispatch`；`get_sketch_points` 画 1/2 条直线 ⇒ **2/4** 个（**每条线两个端点**）⇒ **这两条返回对象列表**，而 `get_lines`/`get_arcs`/`get_ellipses` 返回数值数组`<br>· `python tools/capture_sketch_evidence.py（**真机**，2026-10-01 轮 222 / 砌墙 W1：新零件 → 画 1 条线 + 1 个圆 → **退草图** → 按名取草图对象 → 4 个读数 + 2 个负例，**verdict: pass**，证据落 output/sketch-evidence.json）—— ★ 这一步是**挂成 MCP 工具之后**的验证：走的是工具真实路径（import tool_specs_batch18._sketch_args），不是只调底层函数。★ 它当场抓到一个只有真机能暴露的 bug：草图关闭时 sw_part.current_sketch_name 回**英文 fallback**「Sketch1」，而中文 UI 下真名是「草图1」⇒ 新加 sw_sketch.resolve_sketch （中英文候选名 → 特征树兜底 → 抛错）修掉。` |
| `standard_parts_toolbox` | · `python -c "import sw_toolbox_index as tb; print(len(tb.list_standards()), len(tb.load_index()['parts']))"（**2026-10-01 轮 163 实跑**：**19** 套标准 / **1844** 个零件）`<br>· `tb.search('bearing') ⇒ **184** 条（检索可用）` |
| `sketch_chamfer` | · `python tools/verify_sketch_edit_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1：新零件 → 进草图 → 两条相接直线 → 选中两条（选区计数 **2**）→ `create_sketch_chamfer(chamfer_type=2, distance_mm=5)` ⇒ **线段数 2 → 3**）—— **10/10** `verdict: pass``<br>· `python tools/probe_chamfer_forms.py（**真机**，逐类型试：type0/type1 段数不变 · **type2 段数 2 → 3**）` |
| `gtol_insert` | · `python tools/verify_gtol_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1：新零件 → `insert_gtol()` **拿到 CDispatch**）`<br>· `python tools/probe_gtol_frame_order.py（**真机**：`ConvertFormat()` ⇒ 0 → **`AddFrame()` ⇒ True** → `GetFrameCount` ⇒ **2** → `GetFrame(1)/(2)` **有对象**）` |
| `drawing_current_sheet_query` | · `python 真机（轮 301）★ **PASS 5/5** —— 图纸比例读(1:1) · 写 1:5/1:2/1:1 三个都回读一致 · 负例(numerator=3 / -1:5 / 图纸名不存在)都显式拒绝 · 证据 output/sheet-scale-evidence.json`<br>· `python tools/capture_drawing_query_evidence.py（真机，2026-10-01 轮 224 / 砌墙 W2：新建空工程图 ⇒ 三个读数 + 在零件上的负例 + 返回结构不足的负例，verdict: pass，证据落 output/drawing-query-evidence.json）—— ★ 关键正例：空图纸上 list_views 回空表（证明假视图被过滤）。`<br>· `python tools/probe_drawing_object_routes.py（真机探针，定下三个未知：model.GetType()==3 且 GetCurrentSheet() 能直接调 · GetProperties2 是 8 个 double · 空图纸 GetFirstView() 回的是图纸本身；证据 output/drawing-object-routes.json）`<br>· `pytest tests（全量 0 failed，含两个「钉死数量」守卫已同步：all_specs() 65 / 协议层 110）` |
| `file_custom_property_read` | · `python tools/capture_custom_property_evidence.py（真机，2026-10-01 轮 227 / 砌墙 W3：新建零件 ⇒ Add3 写一个属性（count 28→29）⇒ **读回写入值** ⇒ 读全部（count_read 29 == count_reported 29）⇒ 2 个负例，verdict: pass，证据落 output/custom-property-evidence.json）`<br>· `python tools/probe_custom_property_reads.py（真机探针：定下「管理器必须当方法调用」与「by-ref out 不通、只能用单返回值的 Get」；证据 output/custom-property-reads.json）`<br>· `pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 67 / 协议层 112）` |
| `sketch_build` | · `python 真机（轮 399）★ **PASS** —— 24h 计划 v2 段 3：`solidworks_auto_dimension_sketch`（按官方 `ISketch.AutoDimension2` 给当前草图建**真实模型尺寸**）。真机：有活动草图时 ⇒ **status=pass · status_code=0 · selected=2**；负例（**没有活动草图**）⇒ **status=blocked · error_code=SKETCH_NOT_ACTIVE**。证据 output/part-read-dimension-evidence.json。★ 它建的是**真实的 `DisplayDimension`**（★ 可被工程图导入复核），不是草图里画几条线。`<br>· `python 真机（轮 398）★ **PASS** —— 24h 计划 v2 段 2「草图图元」5 个工具（`mcp-server/tool_specs_batch54.py`）：`solidworks_sketch_add_arc` · `solidworks_sketch_add_ellipse` · `solidworks_sketch_add_polygon` · `solidworks_sketch_add_slot` · `solidworks_sketch_add_centerline`。真机（走 `sw_guard`）判据是**段数**（独立于返回值 —— `CreateArc` 那些回 COM 对象而“回对象”≠“图形在”）：arc [0→1] · ellipse [0→1] · polygon [0→7] · slot [0→5] · centerline [0→1]；负例（**不存在的草图名**）⇒ **抛 RuntimeError**。证据 output/sketch-primitives-evidence.json。★★ 同轮抓到两个真 bug：① `sw_sketch.resolve_sketch` 对**非空但找不到**的名字**静默回退**到「特征树里最后一个草图」（会让调用方在**另一个草图**上读/写）—— 已修（兜底只对空名字成立）；② 本批 5 条 ToolSpec **漏了 `inject=\"model\"`**（会让工具拿不到文档对象、一调就 TypeError）—— **契约测试当场抓到**，已补。`<br>· `python tools/capture_sketch_build_evidence.py（真机，2026-10-01 轮 229 / 砌墙 W4：新建零件 → start（前视）→ 画线 → 画圆 → 画矩形 → end，★ **并用 W1 的只读工具回读断言**：线后 count_lines=1 · 圆后 count_arcs=1 · 矩形后 count_lines=5（1 线 + 4 边）· **关掉草图后仍读到 5**；另记两条：不 start 就画线 = 静默 · 坏基准面名 = ValueError。verdict: pass，证据落 output/sketch-build-evidence.json）`<br>· `python tools/capture_sketch_evidence.py（W1，只读批；与本批构成**读写配对**）`<br>· `pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 72 / 协议层 117）` |
| `feature_build_extrude` | · `python tools/capture_feature_build_evidence.py（真机，2026-10-01 轮 230 / 砌墙 W4 续：新建零件 → batch21 建草图（矩形 40×20）→ extrude_boss(10) ⇒ ★ **包围盒 size [40,20,10]**；再建圆草图 → extrude_cut(0=完全贯穿) ⇒ 特征树 19→21；另一新零件 → extrude_midplane(总深 10) ⇒ size [40,20,10] 且 min/max **±5**（两侧对称）；负例：不存在的草图名 ⇒ ValueError。verdict: pass，证据落 output/feature-build-evidence.json）`<br>· `python tools/capture_sketch_build_evidence.py（batch21；与本批合起来构成**建模最小闭环**）`<br>· `pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 75 / 协议层 120）` |
| `chamfer_fillet_on_selection` | · `python tools/capture_chamfer_fillet_evidence.py（真机，2026-10-01 轮 231 / 砌墙 W4 续：建草图→拉伸成盒 → 选 `index:0` → `chamfer(2mm)` ⇒ 特征「**倒角1**」（19→20）；再选 `index:1` → `fillet(3mm)` ⇒ 特征「**圆角1**」（→21）；★ **对照实验**：清空选区后调用 ⇒ **特征数不变**（21→21，且返回对象无名）⇒ 证实「它作用在当前选择上」；负例：`index:9999` ⇒ EntitySelectionError（给出上界 18）。verdict: pass，证据落 output/chamfer-fillet-evidence.json）`<br>· `pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 77 / 协议层 122）`<br>· `python -m pytest tests/test_sw_chamfer_geometry.py（**6 passed**，★ 纯几何无 COM：两个解析公式 + **两条负例**）` |
| `mass_property_read` | · `python tools/capture_mass_property_evidence.py（真机，2026-10-01 轮 234 / 砌墙 W5：建草图（矩形 40×20）→ 拉伸 10mm → 读质量属性 ⇒ ★ **数字断言**：volume **8000** · surface_area **2800** · center_of_mass **[0,0,−5]**；另如实记录 `mass` 的量纲疑点与 `AccuracyLevel` 读不到；负例：在**工程图**上调用 ⇒ RuntimeError。verdict: pass，证据落 output/mass-property-evidence.json）`<br>· `python tools/probe_mass_property_reads.py（真机探针：定下「`CreateMassProperty` **当属性取**即可」——★ 与其兄弟 `CustomPropertyManager`（**必须当方法调**）**相反**；并实测出**单位是毫米系**；证据 output/mass-property-reads.json）`<br>· `pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 78 / 协议层 123）`<br>· `python tools/probe_mass_units_controlled.py（**真机对照实验**，2026-10-01 轮 263：★ **四个量的单位定死** —— Density **kg/m³**（赋 AISI 1020 ⇒ **7900.0**）· Volume **mm³** · CenterOfMass **mm**（z=-5.0）· **Mass = Volume × Density**（数值即 µg））` |
| `assembly_read` | · `python tools/capture_assembly_evidence.py（真机，2026-10-01 轮 237 / 砌墙 W6：造临时零件（40×20×10 盒）存到 output/_fixtures/ → 建装配 → 同一零件加两次；★ **一正一反**：重叠（都在 z=0）⇒ interference_count **1** · 分开（z=0 与 z=60）⇒ **0**（status pass）；另回读 2 个组件与配合清单。verdict: pass，证据落 output/assembly-evidence.json）`<br>· `pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 81 / 协议层 126）` |
| `simulation_loads_wiring` | · `python tools/capture_simulation_loads_evidence.py（真机，2026-10-01 轮 238 / 砌墙 W7：★ **走工具真实路径**（`inject`(resolve_study) + `pre_call`(选面) + `derived_args`(补 model)）⇒ 夹具「**固定-1**」· 载荷「**力-1**」· 选区计数 **1/1** · `LoadsAndRestraintsManager.Count == 2`。verdict: pass，证据落 output/simulation-loads-evidence.json）`<br>· `python tools/capture_simulation_evidence.py（真机，既有脚本，**能力层直调**：赋材料 → 夹具 → 载荷（Count == 2）→ CreateMesh（**7,310 单元**）→ RunAnalysis（1 秒）→ **study.Results 非空、GetPlotCount == 4**（品质/应力/位移/应变）。verdict: pass）`<br>· `pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 83 / 协议层 128）` |
| `simulation_study_create` | · `python tools/capture_simulation_study_evidence.py（真机，2026-10-01 轮 239 / 24h 段 1.1：★ **走工具真实路径** ⇒ 建研究 `DSH-141` 成功，★ `entry_name` = **CreateNewStudy3**、`error_code` = 0；★ **建完回读**名字逐字相等；★ **列出** count 1 且含该名字；★ **负例**：取不存在的名字 ⇒ `found` 为 **False**。verdict: pass，证据落 output/simulation-study-evidence.json）`<br>· `python tools/probe_simulation_study_shapes.py（真机探针：定死三个真形状 —— `create_static_study` 回 **tuple(3)**、`iter_studies` yield **`(index, study)`**、`get_study_by_name` 找不到**回 None 不抛错**）`<br>· `python scripts/check_param_binding.py（★ 本批新增的门禁：声明参数必须『有归属』；★ **已用负例证明它抓得住** —— 临时摘掉 `param_alias` ⇒ exit 1 并精确指出是哪个参数）`<br>· `pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 86 / 协议层 131）` |
| `mesh_create_readback` | · `python tools/capture_mesh_solve_evidence.py（真机，2026-10-01 轮 242：★ **经 `run_isolated` 在子进程执行** ⇒ `mesh_size` 回 `{element_size: 4930.5, tolerance: 246.5}`（0.2s）；`create_mesh` 回 **`{ok: True, element_count: 7250}`**（0.6s）⇒ ★ **网格真的建出来了**；★ 证据落 output/mesh-solve-evidence.json）`<br>· `tests/test_isolate.py（4 条：正常回值 · ★ **超时即杀子进程** · 异常不吞 · 模块不存在说清楚）`<br>· `tools/experiment_subprocess_com.py（★ 隔离方案的**三前提**真机验过：子进程能连同一实例 / 卡住不阻塞主进程 / 可被杀）` |
| `simulation_load_family_breadth` | · `python 真机（轮 425）★ **PASS** —— 刚性连接件（B 组第一条）。真机（走 `sw_guard`，6.4 s 无弹窗）：双体零件上★ **计数 0→1**（判据：回读计数**恰好 +1**）。证据 output/rigid-twobody-evidence.json。★★ 而它一次证实了前面**两条**链上的假设：① 崩的真因是「**读选区只拿得到第 1 个实体**」（事实 336/337：`GetSelectedObject6`/`4`/`5`/`GetSelectedObjectsFace` **五个入口都试过**，而 `Count2(-1)` 如实报 2）⇒ 换成「**按已知实体清单装数组**」（不读选区）后**不再崩**；② 它**要两个体**（事实 338：同族形参名写着 `Comp1`/`Comp2`）—— 单体零件上它**成功返回却不建**（计数 0→0、无错误），那是**应然的**。★★ 因此本工具**不读选区**，而是自己按**序号**把两组实体装好，且**两侧体号可分别指定**。`<br>· `python 真机（轮 415）★ **PASS** —— ◆ 热载荷组：convection 0→1 · heat_flux 1→2 · heat_power 2→3 · **temperature 3→4** · radiation 4→5；◆ 结构载荷组：distributed_mass 0→1 · force 1→2 · **remote_load 2→3**。★ 而真因**不在探针**：能力层里一张**手抄 CHM 的名单**`_ERRORCODE_MEMBERS` **漏了 `AddTemperature` 与 `AddRemoteLoad`** ⇒ `_wants_error_code` 回 False ⇒ **不补 `out_i4()`** ⇒ `com_error(-2147352561, 非选择性的参数)`。★ 而定位它用的是**出厂类型库**：**PowerShell  的纯元数据反射**（`[Reflection.Assembly]::LoadFrom` → `SolidWorks.Interop.cosworks.dll` **34.4.1.1011**）—— ★ **零依赖、不需要 SolidWorks 实例**；它给出★★ **全部 35 个 `Add*` 都带 `ErrorCode:Int32&`**（不带的 0 个）⇒ 名单改为那 35 个（一条改动修好两个名字）。证据 output/thermal-loads-evidence.json 与 output/loads-groupa3-evidence.json。`<br>· `python 真机（轮 414）★ **PASS** —— 24h 计划 v2 段 5（A 组收尾）：`solidworks_simulation_apply_distributed_mass` 与 `solidworks_simulation_apply_force`。真机（走 `sw_guard`，4.0 s 无弹窗）：在 **静力算例**上★ **distributed_mass 计数 0→1** · **force 计数 1→2**（**单调序列**）。证据 output/loads-groupa3-evidence.json。★★ 而真因值得单记：第一版用了**固定算例名** ⇒ 回读计数变 `-1`（`_loads_count` 对“取不到”的约定）⇒ **判据假红**；★ 而诊断探针证明 `Count` 在**静力与热两种算例上都正常**⇒ 真因是**算例名重复**（仓里自注“能力层不检查重名”）⇒ 改成**带时间戳的唯一名**后立刻 pass。★ 这两条与热载荷那 4 条**相反**：它们要 **static**（各载荷对算例类型要求不同）。⚠ `remote_load` **仍不注册**：报缺必填参数，★ 而仓里来源块记的官方声明与`_check` 一致 ⇒ ★ 嫌疑 CHM（2021 版）过时，与 `AddTemperature` 同形（反射 dump 里两个名字都没有）⇒ 按铁律 5 不猜。`<br>· `python 真机（轮 408）★ **PASS** —— 24h 计划 v2 段 5（仿真载荷族）：**4 条热载荷恢复注册**（convection / heat_flux / heat_power / radiation）。★ 起点是**抄官方声明**（收敛报告写的下一步）：CHM 里六条 VB 声明**一模一样**（`AddXxx(DispArray As Object, ByRef ErrorCode)`）且与**已能用的** `AddElasticConnector` 同形⇒ 形态没错。★★ 而线索来自**载荷的性质**：这五条是**热载荷**，而轮 402 我一直在 **`static`** 算例上试它们。真机（走 `sw_guard`，4.9 s 无弹窗）：建 **thermal（`study_type=3`）** 算例后 ★ **convection 0→1 · heat_flux 1→2 · heat_power 2→3 · radiation 3→4**（逐条 +1）。证据 output/thermal-loads-evidence.json。★ 各载荷对算例类型的要求**不同**：这 4 条要 **thermal**，而 `elastic_connector` 相反（在 **static** 下成、在 thermal 下不成）。⚠ `temperature` **仍不注册**：报 `-2147352561 非选择性的参数`（缺必填）—— CHM 那页是 **2021 版**、本机是 2026；而反射 dump 与 arity 表里**都没有这个名字**⇒ 按铁律 5 不猜，下一步查 CHM 的**示例代码**或活的类型库。`<br>· `python 真机（轮 402）★ **PASS** —— 24h 计划 v2 段 5（仿真载荷族）：`solidworks_simulation_apply_elastic_connector`（`sw_simulation_loads.apply_elastic_connector_report`）。★ 调用走**工具层同序**（`inject` → `pre_call` → `derived_args`），★★ 而且照既有脚本留下的**先例警告**：每次**先 `ClearSelection2(True)`** （`select_face_at` 的 `append=False` 只表示“不追加”、**不清空**）。真机：载荷计数 **0 → 1**（★ 判据是回读计数恰好 +1，不是返回值）。证据 output/loads-simple6-evidence.json。⚠ **同批另 5 条（convection / heat_flux / heat_power / temperature / radiation）真机未建成** ⇒ 按硬约束⑥ **回退注册**（★ 包装与探针保留）；★ 真因：这一族里**吃单实体 / 吃数组 / 参数更多**三种混在一起，★ 而仓里的来源块**只抄了 4 条官方声明**（事实 317）。`<br>· `python 真机（轮 349）★ **PASS 5/5** —— **三类荷载全通 + 回读载荷数 = 3**：`add_pressure` ⇒ `ok` · `add_force` ⇒ `ok` · `add_gravity` ⇒ `ok`（都是 `<COMObject>`）· ★ `LoadsAndRestraintsManager.Count` ⇒ **3**（★ 规则 6 的回读：三个荷载**真的加进去了**）· 证据 output/loadfamily-evidence.json`<br>· `python 真机（轮 348/349）★ **两处通用修复（都在能力层 `_check`，一处 ⇒ 整批受益）**：① **末尾 `ByRef ErrorCode` 统一补 `out_i4()`**（★ 缺它 ⇒ `DISP_E_PARAMNOTOPTIONAL`「非选择性的参数」）；② **第 3 参 `RefGeom` 裸传 `None` ⇒ 换成空 Dispatch 参数包**（★ 裸 `None` ⇒ `com_error(-2147352571, '类型不匹配', None, 3)`）。★ 两处都**只对已从官方声明核过的成员**生效（★ 白名单，★ 表外不乱补 —— 铁律 5）。`<br>· `python 真机（轮 245 的历史发现，本批兑现）★ `RegGeom`/`RefGeom` **不能裸传 `None`** —— ★ 而那时**只修了 `add_torque`，`add_force` 漏了**（★ 本轮补上）。`<br>· `★ **静态那一半是绿的**：`all_specs()` 出现这 4 个工具 · `scripts/check_param_binding.py` **PASS**。` |
| `mesh_size_sanity_gate` | · `python tools/capture_mesh_sane_evidence.py（真机，2026-10-01 轮 248：**4/4 通过**，★ **全程无弹框、不挂起**；证据落 output/mesh-sane-evidence.json）`<br>· `★ **对照证据**：tools/capture_simulation_evidence.py 的 `output/simulation-evidence.json`（`suggested_size_mm: 4.933908705960544` · `element_count: 7310` · `plot_count: 4`）—— ★ 那是「参数生效」的权威参照`<br>· `★ 静态：`scripts/check_param_binding.py` PASS（★ 它当场抓到了本批初版漏写 `param_alias`）· 门禁链 18 道 exit 0` |
| `feature_readback_criterion` | · `python tools/capture_modeling_readback_evidence.py（真机，2026-10-01 轮 249：`criterion_selfcheck.ok = true`，★ 两侧都对；证据落 output/modeling-readback-evidence.json）`<br>· `★ **三轮真机打磨**：① 直接调 `GetWhatsWrong2` ⇒ 取不到；② 改用 `Extension.GetWhatsWrongCount` ⇒ 取到（0 条错）；③ 过滤从「枚举容器名」改成「`GetTypeName2` 非空」（★ 与 UI 语言无关）`<br>· `★ 静态：`scripts/check_union_conventions.py` PASS · `check_param_binding.py` PASS` |
| `modeling_feature_readback_tools` | · `★ 既有冒烟（权威 · 本仓库自己的判据）：`python tools/verify_dome_smoke.py` ⇒ 9/9 · verdict: pass（★ 两个独立证据：边界框逐分量变了 [20,60,100]→[34.2222,60,100]；特征树条数 19→20 · ★ 且逐条标注了能证明什么、不能证明什么）`<br>· `★ `python tools/capture_modeling_readback_evidence.py` ⇒ verdict: pass（2/4：`shell` 与 `insert_dome` 的 readback 三条全真）`<br>· `⚠ `python tools/verify_composite_curve_smoke.py` ⇒ 7/8 · verdict: fail，而它写明「前置成立 ⇒ 这是真失败」（★ 不是前置不可达那种免责失败）`<br>· `★ `python tools/probe_shell_thickness_units.py` ⇒ 单位判决 = 毫米（t=2 ⇒ 空腔 96×56×18；t=4 ⇒ 92×52×16）· ⚠ 官方文档写 meters 对本机不成立`<br>· ``python tools/probe_rib_preconditions.py` ⇒ 三变体全 8→8（★ 无错误、无特征）—— ★ 排除了一个假设（★ 排除假设与找到正解同样是进展）` |
| `config_and_export` | · `python tools/capture_config_export_evidence.py（真机，2026-10-01 轮 255：**verdict: pass** · 10/12；★ 证据落 output/config-export-evidence.json）`<br>· `★ 既有冒烟（§5.0 复用）：`python tools/verify_bmp_smoke.py` ⇒ **8/8 · verdict: pass**（★ 它只证「尺寸按请求走 + 文件合法」，**不证画面内容** —— ★ 如实标注）`<br>· `★ 静态：`scripts/check_param_binding.py` PASS（117 个工具）· `check_union_conventions.py` PASS · `tests/test_server_wiring.py` 8 passed` |
| `render_materials_and_appearance` | · `python tools/capture_appearance_evidence.py（真机，2026-10-01 轮 258：**verdict: pass** · 4/4；★ 证据落 output/appearance-evidence.json）`<br>· `★ 既有工具（本批**没有**新建工具）：`solidworks_list_render_materials` / `solidworks_collect_appearance_evidence` / `solidworks_refresh_scene_graph`` |
| `selection_helpers` | · `python 真机（轮 397）★ **PASS 9/9** —— 24h 计划 v2 段 1「选择底座」的 6 个工具（`mcp-server/tool_specs_batch53.py`）：`solidworks_selection_count` · `solidworks_select_entity_by_index` · `solidworks_resolve_selection` · `solidworks_selection_point` · `solidworks_select_by_selector` · `solidworks_resolve_entity`。真机（走 `sw_guard`，3.94 s 无弹窗）：清空后计数 0 · 按序号选边/面 ⇒ 回读计数 1 · `selection_point` ⇒ **ok: true · point_mm: [-20.0, 0.0, -5.0]** · 解析选择器选中 ⇒ 1 · 选择器选中 ⇒ count 1 · 解析实体 ⇒ resolved true/count 1；三条负例全过（越界抛 EntitySelectionError · 空选区拒绝 · 非法选择器拒绝）。证据 output/selection-base-evidence.json。★★ **同轮真机抓到一个真 bug 并修掉**：`selection_point` 内部给 `GetSelectionPoint2` 与 `GetSelectionPoint` **都传了 `(1, -1)`**，而官方签名是 `GetSelectionPoint2(Index, Mark)`（**2 参**）与 `GetSelectionPoint(AtIndex)`（**1 参**）⇒ 走到 1 参那个必然报 `(-2147352562, '无效的参数数目。')`（★ 而那个错指不出是参数个数问题）；修法：**按名字给各自 arity** + **两个入口的报错都留住**（先前是后者覆盖前者）。★★ **另一条真机语义**：`GetSelectionPoint2` 对**面**有效（返回坐标）而对**顶点**的 6 种 (Index, Mark) 组合**全部回 None** —— "selection point" 是**选择时鼠标落在面上的那个位置**，顶点选中时没有面可投影。`<br>· `★ 端到端：`probe_selection_spec_e2e.py` **12/12 通过**（★ 声明式选择 + 按对象选实体）`<br>· `★ 既有：`sw_selection_spec.py` 的 `EntitySelectionError`（★ 越界会大声报错，真机证据见 `output/chamfer-fillet-evidence.json` 的 `negative_out_of_range`）`<br>· `python 真机（2026-10-01 轮 266）：★ `selection_point` **判据自证通过**（两侧）—— 没选中 ⇒ ok=False + 明确原因；选中面 ⇒ ok=True + point；★ 证据 output/selection-point-evidence.json`<br>· `python 真机对照实验（2026-10-01 轮 267）：★ 三点对照 ⇒ 比值 ≈1.000 ⇒ **单位 = 毫米**（output/selection-point-units.json）`<br>· `python 真机（轮 328）★ **顶点枚举**：把 `entities_on_body` 扩展到 `VERTEX`（★ 用已有工具，**不新开**）⇒ 20×20×10 盒子 **FACE=6 · EDGE=12 · VERTEX=8**，★ **欧拉公式 `V−E+F=2` 成立** · 未知类型 ⇒ 显式拒绝 · 证据 output/vertices-evidence.json` |
| `declarative_hole_creation` | · `python 真机（轮 298）★ **PASS 5/5** —— 修掉单位 bug 之后，**5 个孔型全部在全新文档里建成**（through / blind 7->9 / counterbore 7->11 / countersink 7->10 / semicircular_slot 7->9）· 证据 output/hole-units-fixed-evidence.json`<br>· `python 真机（轮 297/296）：单位 bug 的两面 —— 毫米调 countersink **2/2 PASS**（output/countersink-mm-probe.json）· 米调报 `创建圆草图失败`（output/countersink-diag-probe.json）`<br>· `python 真机（轮 292/293）：入口链 PASS · 有视图的图 · 见 drawing_view_operations 条` |
| `weldment_cut_list` | · `python 真机（轮 429）★ **PASS** —— **焊件切割清单那条链**（先建结构构件、再走切割清单）。真机：`evidence_before` 的 `cut_list_folders` = **[]** ⇒ `ensure_cut_list` **建出了** ⇒ `update_cut_list` 报 "切割清单项目1"（type=CutListFolder, body_count=1）⇒ `evidence_after` 非空 ⇒ `export_cut_list_csv` **224 字节**（★ 旧证据只有 **26 B**）。证据 output/cut-list-chain-evidence.json 与 output/cut-list-chain.csv。★★ 而唯一没过的 `set_cut_list_properties` 真因是**本地化名**：英文名（`Description`/`Material`）报「回读失败」，而**中文名（`说明`/`材料`）写入并回读得到**（out-cut-list-property-names-evidence.json PASS）。`<br>· `python 真机（轮 270）：**1/3** —— export ✓ / create_cut_list 后端限制 / set_properties 前置不满足 · 证据 output/weldment-evidence.json` |
| `simulation_solver_options` | · `python 真机（轮 347）★ **PASS 3/3** —— 整条路通了：`create_study` ⇒ `ok=true` · `get_options` ⇒ **`CDispatch`** · `configure_static_solver_report(study, reference_pressure=1.0)` ⇒ **`ok=true` · `changed=["reference_pressure"]` · `returned={'DefinedReferencePressure': 1.0}`**（★ **设置真的生效**）· 证据 output/solver-options-evidence.json`<br>· `python 真机（轮 346）★ **工具层修掉一处一行之差**：`resolve_study` 原先 `next(iter(iter_studies(sw)), None)` **没解包**（★ `iter_studies` 产 `(index, study)` 元组）⇒ 把元组当 study 传下去 ⇒ ★ **所有没声明 `study_name` 的工具全中招**。★ 修后 `study` = **`CDispatch`**，三个配置入口的报错**换了层次**（★ 从无意义的 `SldWorks.Application.X` 变成有意义的「该研究类型可能不是这一族」）。`<br>· `python 真机（轮 345）★ **建研究的两个真实前置查清**：① 第一参必须是 **`ISldWorks`**（★ 传 `doc` ⇒ `AttributeError: <unknown>.GetAddInObject`）· ② 文档里**必须有实体**（★ 否则 `swsStudyError_e = 1`）⇒ `create_study_report` 真机 `ok=true`。`<br>· `python 真机（轮 273）★ `list_setter_summary`（零参）**ok=True**（9 个族 / 202 个 setter 名）· 证据 output/batch37-evidence.json` |
| `topology_constraints_and_controls` | · `python tools/capture_topology_readback_evidence.py（真机：8 项过 7 · set_goal 的 before/after 计数变化是设置真生效的硬证据）` |
| `costing_readback` | · `python 真机（轮 274）：**5/6** —— 四个读数是**真的读到了数据** · 证据 output/costing-evidence.json` |
| `render_material_library` | · `python 真机（轮 373）★ **PASS 5/5** —— `RenderMaterialSpec(file_name=<真实 .p2m>)` 打通整族：`create` ok · `add_entity` ok · `add_render_material` ok · **`list_render_materials` 读到 1 个** · `GetRenderMaterialsCount2(2, names)` 也回 **1** ⇒ 命中 5/5。★ 同时验证新契约：`RenderMaterialSpec()`（空 `file_name`）**明确抛 ValueError**。证据 output/render-material-evidence.json`<br>· `python 真机（轮 373）★ **真因是 `FileName` 必须绑 `.p2m`** —— 四轮收窄的终点（known-facts 287→290）：`CreateRenderMaterial(name)` 建出的外观**没有绑定材质文件**时，`AddDisplayStateSpecificRenderMaterial` **照样回 true** 且 `GetLinkedDisplayStates` **显示已链接**，而 `GetMaterialIds` 回 `None`、`GetRenderMaterialsCount2` 恒 **0**（★ 一个「看起来成功、实际不算数」的外观）。★ 设 `FileName = '<真实 .p2m>'` 之后：`GetMaterialIds` 回 `id1=6`、`GetRenderMaterialsCount2` 回 **2**、我们自己的 `list_render_materials` 读到条目。`<br>· `python 真机（轮 367）★ **顺带修掉第 12 处「设属性写成取或调」**：`create_render_material` 的 `spec.extra` 循环原为 `get_com_member(material, key, float(value))`（事实 227）⇒ `TypeError`；已改 `set_com_member`（★ 前人轮 319 修了 11 处，这一处漏了）。`<br>· `python 真机（轮 371/372）★ **观察点**：`IRenderMaterial.GetLinkedDisplayStates()` 直接回答「外观挂到了哪些显示状态」，★ 不经过「清单」那条可疑中介 ⇒ 用它证明 `Add…` 的**链接**确实生效（而清单仍空）。` |
| `mold_analysis` | · `python 真机（轮 343）★ **冒烟 5/5 PASS**（★ 改前报 3/5 fail，★ 真因是**脚本的键形状假定过时**：它在顶层找 4 个计数键，而实现放在 `counts` 子字典）：「含官方只读入口的键 **6/6**」·「新零件上读数都是空/0 **6 个**」· 证据 output/mold-evidence-smoke.json`<br>· `python 真机（轮 177，复验于 343）★ **4/4 PASS**：`IFeatureManager.MoldDraftAnalysis` ⇒ **AttributeError** · `IModelDoc2.MoldDraftAnalysis` ⇒ **能取到** · ★ **而真机回 `bool`**（★ 官方签名写的是 `Void`）· 证据 output/mold-draft-analysis-owner.json` |
| `preview_and_review_report` | · `python 真机（轮 340）★ **PASS 4/4**：`set_standard_view` ⇒ `ok=true`（★ 而 `readback_ok=false` —— ★ `ActiveView` 成员全报 `<unknown>`，事实 36 形态）；`collect_model_summary` ⇒ **20 个特征**；`build_review_report` ⇒ `status="warn"` · `score=92`（★ 它的判据是 **`evaluation.status`**，不是 `ok`）；产物 **4 个非空 BMP** · 证据 output/review-tools-evidence.json` |
| `motion_validation_and_preconditions` | · `python 真机（轮 278）：**PASS 5/5** 中的 2 项 · 证据 output/motion-evidence.json` |
| `drawing_views_and_summary` | · `python 真机（轮 318）★ **PASS 2/2**（★ 用 **SolidWorks 自带示例图**做夹具）：`bolt-assembly.slddrw` ⇒ `list_views` **5 个视图**（`Drawing View1/2/3`…）· `sheets_summary` = 1 张 `Sheet1`；`box.slddrw` ⇒ `list_views` **4 个视图** · `sheets_summary` = 1 张 `Sheet1`。另：`current_sheet_info` 真机回 `paper_size` / `scale_num` / `scale_den` / `first_angle` / `height_mm`。证据 output/drawing-views-evidence.json · sheets-summary-probe.json` |
| `weldment_profile_and_curve` | · `python 真机（轮 341）★ **PASS 3/3**：`create_weldment_profile` ⇒ **`ok=true`**· `size_bytes=49204`；产物 **`vp2.SLDLFP` 49204 字节**（★ 已**排除 `~$` 锁文件**）· 证据 output/weldment-profile-evidence.json` |
| `costing_templates_and_defaults` | · `python 真机（轮 366）★ **PASS 3/3** —— 修掉一条真 bug 后整族通过：`list_costing_templates_report(cm)` ⇒ `ok=true · count=2` · `get_default_template_report(cm, 0)` 与 `(cm, 1)` ⇒ 都 `ok=true`（回了真实模板路径 `…\lang\chinese-simplified\costing templates\…`）· 证据 output/costing-templates-evidence.json`<br>· `python 真机（轮 366）★ **真 bug 修在一行上**：`list_costing_templates_report` 原先把 `d`（`CostingDefaults`）传给 `list_templates`，而 `GetTemplatePathnames` **挂在 `ICostManager` 上**（反射转储 `iface_sldcostingapi.txt` 的 `## ICostManager`：`GetTemplateCount(Int32)` / `GetTemplatePathnames(Int32)` 成对）⇒ 改成传 `cost_manager` 即通。COM 报的是 `<unknown>.GetTemplatePathnames`（像“成员不存在”，其实是**对象不对** —— 事实 36 的形态）。`<br>· `python 真机（轮 366）★ **受控实验定位**：A（只取 defaults）/ B（先取 model 再取 defaults）都通，而工具层入口不通 ⇒ 把嫌疑缩到“工具层内部那一处传参”上。` |
| `pattern_and_mirror` | · `python 真机（轮 317）★ **两半都建成**：镜像 ⇒ **`镜向1`** · type=**`MirrorPattern`**；阵列 ⇒ **`阵列(圆周)1`** · type=**`CirPattern`**（★ 前置 `基准轴1` 由 `IModelDoc2.InsertAxis2` 建）`<br>· `★ 关键修正：镜像的 mark **原本是反的**（特征 4→1 · 平面 1→2，★ 官方 `InsertMirrorFeature2.md` 的 Remarks 给了完整 mark 表）`<br>· `证据 output/mirror-fixed-evidence.json · pattern-axis-evidence.json · pattern-probe.json` |
| `drawing_view_operations` | · `python 真机（轮 294）：**视图比例三条事实** —— ScaleRatio 回 (1.0,500.0)=1:500 · ScaleDecimal 回 0.002 · **写不进**（关掉 UseSheetScale 后赋值仍不变）；set_view_scale_verified 如实报 ok=false · 证据 output/set-view-scale-probe.json · scale-ratio-probe.json`<br>· `python 真机（轮 293）：有视图的图（3 视图）—— list/collect ok count=3 · get_view_scale ok scale=0.002 · 证据 output/drawing-view-evidence.json`<br>· `python 真机（轮 292）：capture_drawing_query_evidence.py **PASS**（入口链）· 证据 output/drawing-query-evidence.json` |
| `surface_features` | · `python 真机（轮 388）★ **PASS** —— objective② 补的第二个真缺 `filled_surface`：`scripts/sw_surface_features.py` 新增 `insert_fill_surface_report`（官方 `IFeatureManager.InsertFillSurface2`，**6 参**）。真机（走 `sw_guard`，6.47 s 无弹窗）：前置 `曲面-拉伸1`（树 6→7）· 负例 `resolutions = 9` 被拒 · **`insert_fill_surface_report(doc, 2)` ⇒ 新特征 `曲面填充1` · 选 4 条边 · 树 7→8** ⇒ `verdict: pass`。★★ **真机打通的关键**：边界边必须用 `SelectByID2` 带 **mark = 1**（官方 Remarks 的 Boundary curves）；★ `IEntity.Select4` **没有 mark 参数**（事实 32），而传 **mark = 4** 会**静默失败**（回 true 而 `GetSelectedObjectCount2(-1)` = 0 —— 事实 8）。证据 output/fill-surface-evidence.json。`<br>· `python 真机（轮 386）★ **PASS** —— objective② 补的第一个真缺 `extend_surface`：`scripts/sw_surface_features.py` 新增 `insert_extend_surface_report`（官方 `IModelDoc2.InsertExtendSurface(bool ExtendLinear, int EndCondition, double Distance)`，**3 参**，回 `void` ⇒ 判据是**特征树 diff**）。真机（走 `sw_guard` 护栏，5.16 s 无弹窗）：前置曲面 `曲面-拉伸1`（tree 6→7）· 负例（距离 0）被入口拒 · **`extend_surface` ⇒ feature `曲面-延伸1` · faces_selected=4 · tree 7→8** ⇒ `verdict: pass`。证据 output/extend-surface-evidence.json。★ ⚠ 真机推翻了「不选面」当负例的假设 —— **不选面它也能成**（它自己会找面），故负例换成参数校验（距离 ≤ 0）。`<br>· `python 真机（轮 309）★ **PASS 2/2**：`knit_surfaces_report(doc, 0.0001)` ⇒ **新特征 `曲面-缝合1`** · 选中 **8** 面 · **body 2→1**；负例容差 5.0 ⇒ 显式拒绝并列出官方上下限 0.0001–0.1 mm · 证据 output/surface-knit-evidence.json`<br>· `python 真机（轮 308）★ **PASS 2/3**：`create_extruded_surface_report(doc, 10.0)` ⇒ **建成 `曲面-拉伸1`**（特征树 6→7 · 22 参）· 负例 `-5.0` ⇒ 显式拒绝· ⚠ `through_all=True` **未通过**（树 7→7，已如实标）· 证据 output/surface-feature-evidence.json`<br>· `python 真机（轮 308）`output/surface-feature-probe.json`：**首次试通**（★ 与 `IModeler.Create*Surface` 完全不同的入口）` |
| `geometry_measurement` | · `python 真机（轮 382）★ **绝对 mm 判据第一次真机使用 · PASS** —— `tools/prove_absolute_criteria.py`（走 `sw_guard` 护栏）建 100×60×20 mm 板，**数据取自真机几何**（顶点坐标差实测 `delta_mm = [0.0, 0.0, -20.0]` = 板厚；`volume = 120000.0` mm³ · `area = 18400.0` mm² 与手算精确一致），三条判据各带**正例与负例**：`check_axis_alignment` / `check_radii` / `check_same_level` **全部「正例 ok=True 且负例 ok=False」** ⇒ `verdict: pass`。证据 output/absolute-criteria-evidence.json。★ 依据调研 v2 发现①：**定位用绝对、等价用相对** —— 两条互补，只留一条会各瞎一半；**现在两条都真机 PASS 过**（相对判据见 compare_geometry 的既有 evidence）。`<br>· `python 真机（轮 311）★ **PASS 3/3** —— ★ 期望值全部由几何推出且全部对上：两平行面 ⇒ `distance` **10.0 mm**（板厚 10）· 单面 ⇒ `area` **400 mm²**（20×20）与 `perimeter` **80 mm**（4×20）· 未选中 ⇒ 显式拒绝 · 证据 output/measure-evidence.json` |
| `loft_and_sweep` | · `python 真机（轮 315）★ **扫描建成 `扫描1`** · **type=`Sweep`**（★ 走 CreateDefinition(swFmSweep=17)）· 未选中 ⇒ 显式拒绝 · 证据 output/sweep-evidence.json`<br>· `python 真机（轮 314）★ **PASS 3/3** —— 同平面与两平面都建成 **`放样1`** 且 **类型名 = `Blend`**（★ 对照拉伸 = `Extrusion`）· 未选中 ⇒ 显式拒绝 · 证据 output/loft-evidence.json · loom-type-evidence.json` |
| `reference_axis` | · `python 真机（轮 317）★ `model.InsertAxis2(True)` 回 **True** 且出现 **`基准轴1`**；★ 而 `FeatureManager.InsertAxis2` 报 `<unknown>.InsertAxis2`（★ 入口层级错）· 证据 output/pattern-axis-evidence.json` |
| `sketch_primitives_b1` | · `output/b1-sketch-primitives-evidence.json` |
| `sketch_edit_ops_b3` | · `output/b3-sketch-edit-evidence.json` |
| `sketch_modify_ops` | · `★ 2026-10-03（轮 472）**真机 5/5**（走 `tools/sw_guard.py`，全程 `sw_alive: true`、**零弹窗**）：`python tools/sw_guard.py --timeout 500 -- python tools/prove_b4_sketch_modify.py`。证据 output/b4-sketch-modify-evidence.json。★★ **判据按操作分**（★ 本批最要紧的经验）：改**坐标系**的（移动/旋转/镜像）看 `Sketch.ModelToSketchTransform.ArrayData`；改**几何**的（缩放/伸展）看草图线段端点的 bbox。★ 具体数值：移动 5mm ⇒ 平移 [0,0,0]→**[-0.005,-0.005,0]**（严格对应）；旋转 30° ⇒ 3×3 首行 **[0.866025,-0.500001,0]**（cos30°/sin30°）；镜像 ⇒ 首行 **[1,0,0]→[-1,0,0]**；缩放 1.5 ⇒ bbox ±20/±10→**±30/±15**（×1.5）。`<br>· `★ 2026-10-03（轮 472）**走 MCP 契约的真机调用 5/5**（★ 不手调内部实现，而按 `ToolSpec` 声明的 `inject` + `params` 装配）：`python tools/sw_guard.py --timeout 600 -- python tools/prove_tools_by_contract.py solidworks_sketch_`。证据 output/tools-by-contract-evidence.json。`<br>· `★ 同轮静态门禁：`tools/check_inject_binding.py` **PASS 0 条**（★ 每个声明都覆盖了包装的必需对象形参）；五统一门禁（`ToolSpec` 声明时）通过；`tests/test_tool_registry.py` **20 passed**。`<br>· `★ 三源互证（swapi + CHM + 出厂反射，**成员名三方一致**）：`IModelDoc2.SketchModify{Translate,Rotate,Scale,Flip}`、`IModelDocExtension.Stretch`。★ **不用 `Tools*` 族**（`ToolsSketchTranslate()` 零参数、交互式弹框，与无人值守红线冲突）。` |
| `surface_edit_ops` | · `★ 2026-10-03（轮 474）**真机 5/5**（走 `tools/sw_guard.py`，全程 `sw_alive: true`、**零弹窗**）：`python tools/sw_guard.py --timeout 600 -- python tools/prove_b6a_surface_edit.py`。证据 output/b6a-surface-edit-evidence.json。★ 逐条：平面区域 树 6→7 `曲面-基准面1`；等距曲面 树 7→8 `曲面-等距1`；直纹曲面 树 7→8 `直纹曲面1`；删除面 树 7→8 `删除面1`；替换面 树 7→8 `替换面1`。★ 判据 = **特征树叶子名增量**（`sw_part.feature_names`），★ 3/5 的官方返回是 `void`。`<br>· `★ 同轮静态门禁：`tools/check_inject_binding.py` **PASS 0 条**；五统一门禁（声明时）通过。`ToolSpec` **241 → 246**。`<br>· `★ 走 MCP 契约的真机调用（`tools/prove_tools_by_contract.py`）：1/5 —— ★ 而那**是预期的**：该探针**不建前置**，而本批 4/5 都要先选面/边（★ 不是能力不行）。`<br>· `★ 三源互证里**两处“台账给的名字是旧的”**：`InsertRuledSurface` ⇒ 真名在 `IFeatureManager`，且 `…FromEdge` 官方标 **Obsolete**（用 `…FromEdge2`）；`InsertReplaceFace` ⇒ `InsertFeatureReplaceFace`。` |

## 四 **仍空缺什么、为什么**（A8 的正面回答）

### 4.1 未达 `verified` 的能力（12 条）

| 能力 | `level` | `source` | 为什么还没到 `verified`（取 `limitations` 首条）|
|---|---|---|---|
| `autocad_basic_drafting` | `not_implemented` | `upstream` | AutoCAD 2024 ActiveX 当前真机回归被阻塞：Documents、Layers、SelectionSets 代理不稳定；不得宣称原生 DWG 绘图已完成 |
| `surface_modeling` | `stitched` | `mixed` | headless-occt 已真实生成并重开受限封闭直纹/平滑 Loft、直线/单圆弧 Sweep、闭壳 Knit 和开放面 Thicken；操作均要求版本化 B-Rep 证据 |
| `mold_tools` | `stitched` | `mixed` | ⚑ 2026-10-01 并入「生成」侧：新增 scripts/sw_mold.py（InsertMoldPartingLine / InsertMoldPartingSurface / InsertMoldShutOffSurface / InsertMoldCoreCavitySolids / MoldDraftAnalysis / MoldUndercutDetect + mold_evid |
| `routing` | `stitched` | `mixed` | ★★★ 2026-10-01（轮 279）**由 verified 降为 stitched**，依据是**可执行的探测**：cadstudio_routing_preflight 回 **blocked** / readyForNativeWrite=false / error_code=routing_addin_or_license_unavailable，blocker=「未检测到 SOLI |
| `animation_export` | `stitched` | `original` | ★★★★★ 2026-10-01（轮 289）**理由第六次也是最后一次收窄 —— 而这次到了"通用错误码"这一层，按事实 53 停止深挖**：
  ★ **本轮查清了那个错误码的含义**：`save_document` 的内部是 `model.Extension.SaveAs(path, 0, 1, …, errors, warnings)`，★ 而两个输入参数都**对**（`swSaveAsV |
| `sketch_edit_ops` | `stitched` | `original` | ★★★ **2026-10-01（轮 164）更正轮 122 的定性**：轮 122 看到 `type=2` 报`com_error 0x80010105` 就判它「**架构性限制、到不了**」并停手 —— **那是误判**。★ 轮 164 用 `tools/probe_chamfer_forms.py` **逐类型试 + 回读线段数**（`tools/probe_chamfer_forms.py |
| `geometric_tolerance` | `stitched` | `original` | ★★★ **2026-10-01（轮 166）穷尽式结论**：`IGtolFrame.AddIndicator` 那半 —— `tools/probe_gtol_indicator_matrix.py` 把 `BorderType`(0..3) × `TolType`（官方 Remarks 允许的 **5 个**：20/22/21/25/13）= **20 组全试**，而**每一组的帧都拿到了** |
| `analysis_run_readback` | `stitched` | `original` | ★★★ ★ 2026-10-02（轮 376）**措辞更正**（★ 事实 293）：先前写的「`run_analysis` **进入求解即挂**」**会误导** —— 观察器抓到屏幕上一直有一个 SolidWorks Simulation 的**求解进度窗**（`DSH-142`）：`当前任务: **建立刚度矩阵**` · `已用时间: **33分0秒**` · `自由度: 30,456` · ` |
| `topology_iteration_options_backend_limited` | `stitched` | `original` | ⚠⚠⚠ **未真机验证**（真机报后端级错误）—— 等级 = `stitched` |
| `topology_readback` | `stitched` | `original` | ★★ 2026-10-02（轮 383）**真机 7/8**：★ **读数与设参的 7 项全部真机通过**（★ 含 `set_goal` 的「设置生效」判据：`before_taken 0 → after_taken 1`）；★ **唯一不过的是 `set_topology_iteration_options`**，报 **`0x80010105`**（`com_error: (-21474178 |
| `sheet_metal_creation` | `stitched` | `original` | ★★ 从 `sheet_metal` **拆出**（轮 275）：★ 那一条覆盖「钣金建模与展开」（含读数与展开），★ 而本族是**建的六个** |
| `mold_parting_geometry` | `stitched` | `original` | ★★ 2026-10-03（轮 392）`insert_shut_off_surface` 已试三次（无孔 / 有孔 / 孔+分型线+分型面）⇒ 都回 true 而特征树不变 ⇒ ★ 穷尽式结论：不是缺前置，而是「没有可关的断面」（★ 假设：孔需穿过分型面）。★ 不再换条件试（事实 53）。★ 下一步只剩 `insert_core_cavity_solids` —— 它要一整条链（分离成型芯/型腔 |

### 4.2 明确「不做」的（4 条，A1 的另一半）

| 不做 | 原因 |
|---|---|
| 动画导出 AVI（Motion 分析算例） | **环境受限** —— 本机没有 SolidWorks Motion 加载项，而 AVI 导出需要 CosmosMotion 系列算例。 |
| AGPL / GPL / 无许可 / 全版权保留 来源的**代码移植** | **许可红线**（`AGENTS.md §二 铁律 6`）：那几类**只读思想**，不抄代码、不抄文本。 |
| 破解相关（SolidWorks-CAD / Solidworks-Crack 类投递页、破解指南、序列号） | **零接触红线**（`AGENTS.md §二 铁律 2`）：不碰破解相关任何内容。 |
| 对外发布（推远端 / 建自建远端 / 提 PR / release） | **未获授权**（用户已明示「GitHub 上的东西不着急，等我们完全开发完毕了再上传」）。 |

> 完整依据（可核的命令/文件）见 `docs/union-not-doing.json`，形状由 `check_union_conventions.py` 的 **R14** 守。

### 4.3 官方接口族的**零调用**缺口（**从台账生成**，A8 的「仍空缺什么」在族这一层）

> 数据源：`docs/family-coverage.json`（**生成物**，从 `C:\swapi\types\` 的成员目录 +
> 本仓库静态扫描得出；**未执行代码、未连 SolidWorks**）。
> ★⭐⭐ **三列口径不同，不可合并**（合并就是误导）：

| 列 | 值 | 含义 |
|---|---|---|
| 官方接口族 / 成员 | **881** / **15,466** | 全量 |
| 编目录 | 15,466（100%）| 名字在代码里出现过 —— **含只写在 API 名登记表里的** |
| 护栏可调 | 10,579（68%）| 登记在某模块能力表里，**且有可达调用路径** |
| **直接调** | **2,722（18%）** | 静态上**看得见字面量**的调用 |
| ⇒ **编进目录但从未直接调** | **255 族 / 2,093 成员** | 本节的清单 |

#### 按域（`hit > 0` 且 `used == 0`）

| 域 | 族 | 成员 |
|---|---|---|
| 全量索引/sldworks | 97 | 786 |
| 仿真(需许可证) | 34 | 653 |
| 路由/Composer/PDM | 52 | 233 |
| 全量索引/swdimxpert | 42 | 153 |
| 全量索引/sldcostingapi | 7 | 121 |
| 全量索引/swpublished | 11 | 75 |
| 全量索引/swmotionstudy | 6 | 43 |
| 全量索引/SWRoutingLib | 3 | 14 |
| 全量索引/dsgnchk | 1 | 8 |
| 全量索引/sldtoolboxconfigureaddin | 2 | 7 |

#### 最大的 10 个零调用族（**要动就先看这些**）

| 族 | 成员 | 域 |
|---|---|---|
| `ICWDynamicStudyOptions` | 119 | 仿真(需许可证) |
| `ICWStaticStudyOptions` | 57 | 仿真(需许可证) |
| `ICWRemoteLoad` | 42 | 仿真(需许可证) |
| `IPropertyManagerPage2Handler9` | 37 | 全量索引/swpublished |
| `IRayTraceRendererOptions` | 36 | 全量索引/sldworks |
| `ISwScene` | 35 | 全量索引/sldworks |
| `ICWFrequencyStudyOptions` | 33 | 仿真(需许可证) |
| `ICWDropTestSetup` | 30 | 仿真(需许可证) |
| `ITessellation` | 28 | 全量索引/sldworks |
| `ICWBeamBody` | 27 | 仿真(需许可证) |

> ⚠⚠⚠ **读这一段的四条纪律（从台账继承，不遵守必误判）**：
> 1. **三列不可合并** —— 「编目录 100%」只证明「这份 API 清单做完了」，
>    **不等于「这些 API 都能用了」**。
> 2. **`used == 0` ≠ 没实现** —— 反例就在台账里：`IGtolFrame` 曾 `used=0`，
>    而 `scripts/sw_gtol.py` 确实调它（成员名字面量）；台账重算后已变 `used=1`。
>    走**变量**传成员名的调用静态看不见。
> 3. **台账是静态解析** ⇒ 它证明「静态可见性」，**不证运行期可用性**。
> 4. ★ **「该不该做」不在台账里** —— 有的零调用族是**故意不做**的
>    （需许可证 / 需加载项 / 官方仅支持进程内非托管 C++）。
>    这类**不做的原因**登记在 `capabilities.yaml` 的 `backend_catalog` 与
>    §4.2 的「明确不做」清单里，**不要**从本节的数字直接推优先级。
>
> ★ **已知的一条实例**：`ISafeArrayUtility`（21 成员，本节仍在零调用里）
> 经真机穷尽实测**不可达**（`used=0` 是正确的）—— 见 `backend_catalog` 的限制段。

## 五 门禁栈（**方法论沉淀**：把判定交给机器，而不是靠人记得）

`scripts/check_*.py` 共 **20** 道；其中接进 `release_check.py`（发布前硬失败）的：

| 门禁 | 接进 `release_check`？ |
|---|---|
| `scripts/check_diff_markers.py` | ✅ |
| `scripts/check_digest_freshness.py` | ✅ |
| `scripts/check_enum_values_vs_reflection.py` | ✅ |
| `scripts/check_env_pitfalls.py` | ✅ |
| `scripts/check_gate_wiring.py` | ✅ |
| `scripts/check_interface_member_ownership.py` | ✅ |
| `scripts/check_license_redlines.py` | ✅ |
| `scripts/check_member_names.py` | ✅ |
| `scripts/check_member_owner_interface.py` | — |
| `scripts/check_negative_input_selfproof.py` | ✅ |
| `scripts/check_param_binding.py` | ✅ |
| `scripts/check_provenance.py` | ✅ |
| `scripts/check_python_syntax.py` | ✅ |
| `scripts/check_report_criteria_alignment.py` | ✅ |
| `scripts/check_report_freshness.py` | ✅ |
| `scripts/check_signature_audit_freshness.py` | ✅ |
| `scripts/check_spec_acceptance_paths.py` | ✅ |
| `scripts/check_undefined_names.py` | ✅ |
| `scripts/check_union_conventions.py` | ✅ |
| `scripts/check_workspace_shadowing.py` | ✅ |

> 还有两个**生成器 + 新鲜度门禁**配对（生成物不许手改）：
> `tools/build_union_map.py` ⇄ `check_union_conventions.py` 的「地图与来源同步」段；
> `scripts/gen_level_audit.py` ⇄ 同门禁的 R8 段；
> `tools/gen_harvest_digest.py` ⇄ `scripts/check_digest_freshness.py`（本文件）。

