<!-- domain: 工程图-6 功能 · L4 语义对表（读函数体判断） -->

# bunny-L4 · 工程图 6 功能「能否直接复用 subskill 已有函数」语义对表

**判读范围**：`D:\AI\SW\subskills\solidworks-engineering-drawing\scripts\` 下 4 个 `.py`
—— `drawing_workflow.py`（2746 行，唯一含 COM 创建调用者）· `drawing_review.py`（883 行，纯审视，不碰 COM 创建）· `drawing_spec.py`（145 行，纯 JSON 校验）· `__init__.py`（1 行）。
**方法**：逐个打开函数体读它到底调了谁；官方签名对照 `C:\swapi\types\`。

## 判据（本表只用这一条，不掺「读得到」）

- **能复用** = 模块内存在某个函数，其**函数体里真的调用了官方「创建」接口**，且实参个数 / 顺序 / 类型与官方签名逐位对齐。
- **读回类一律不算**：只调 `GetXxx`、只回读属性/单元格/枚举的，即使能拿到这种表或符号的证据，也记「不能复用」。
- 官方前置（`## Remarks` / 官方例子的调用序）缺口**单列**，不混进「能否复用」。

## 对表

| 功能 | 能否复用 | 依据的函数名 | 该函数内部真正干什么 | 置信度 |
|---|---|---|---|---|
| ① 剖面视图 | **能复用**（有前置缺口） | `add_section_view`（`drawing_workflow.py:998`）<br>辅助：`set_section_style`（`:2540`） | 函数体只有一行 `drawing_model.CreateSectionViewAt5(x, y, 0, "", 0, None, 0)`，7 个实参与官方 7 参 `(X, Y, Z, SectionLabel, Options, ExcludedComponents, SectionDepth)` 逐位对齐，**是真调创建接口**。但它自己不建剖切线：官方 `CreateSectionViewAt5.md` 的 Remarks 明写「调用前先选中剖切线」，而本模块**没有任何函数调用 `IDrawingDoc.MakeSectionLine()`**（该成员在 `C:\swapi\types\IDrawingDoc\MakeSectionLine.md` 确实存在，0 参）。`set_section_style` 是在**已存在**剖视图的 `ISectionViewData` 上写显示属性，属事后改样式、不是创建；`create_feature_manager_section_view`（`:2729`）走 `IModelViewManager`，官方写明那是**零件/装配体（模型）**里的剖视图，别拿它当工程图剖视图用。 | 高 |
| ② 局部视图 | **能复用**（有前置缺口） | `add_detail_view`（`:1022`） | 函数体直接 `CreateDetailViewAt4(...)`，传满 12 个实参，顺序与类型与官方 12 参签名逐位一致（`X,Y,Z,Style,Scale1,Scale2,LabelIn,Showtype,FullOutline,JaggedOutline,NoOutline,ShapeIntensity`），**是真调创建接口**；调用形状与官方 C# 例子第 61 行完全同构。缺口在官方例子的调用序：先 `ActivateView` → 在视图里 `SketchManager.CreateCircle` 画出详图圆 → 才调 `CreateDetailViewAt4`，**本模块没有画详图圆的那一步**（`CreateDetailViewAt4.md` 本身没写 Remarks，缺口是从官方例子读出来的，不是在签名里读出来的）。 | 高 |
| ③ 中心符号线 | **能复用（受限）** | `auto_insert_center_marks`（`:1883`） | 函数体在 `:1934` 调 `IView.AutoInsertCenterMarks2`，10 个实参与官方 10 参逐位对齐（`InsertType/InsertOption/LinearSlotCenter/ArcSlotCenter/UseDocumentDefaults/Size/Gap/ExtendedLines/CenterLineFont/Angle`），并用 `_view_center_marks` 前后计数回读，**是真调创建接口**。**但受限**：recon 把「中心符号线」定的官方成员是 `IDrawingDoc.InsertCenterMark3(Style, Propagate, Slot)`，本模块**没有**它的封装；`AutoInsertCenterMarks2.md` 的 Remarks 恰好把两者分开——"Call IDrawingDoc::InsertCenterMark3 if you want to insert one center mark in one view"。⇒ 能建出的是**按视图自动批量插入的中心标记**，不是定点/带样式的 `InsertCenterMark3`；要后者得自己补。另有一处前置未完全照官方做：官方要求 `ActivateView` 后再 `ActiveDrawingView` 取句柄，本模块 `:1930` 只调了 `ActivateView`，沿用早先取到的 view 对象。 | 中 |
| ④ 孔表 | **不能复用** | `insert_table_annotation`（`:2306`）<br>`get_hole_table`（`:2425`） | `get_hole_table` 只有 `get_com_member(table, "HoleTable")`，纯 getter，且**不关心这张表从哪来**——典型的「能读不能建」。`insert_table_annotation` 看着像创建入口，但它调的 `InsertTableAnnotation` / `InsertTableAnnotation2` **官方签名里根本没有「表种类」参数**：官方 md 为 `InsertTableAnnotation(X, Y, AnchorType, Rows, Columns)`（且该成员官方标 **Obsolete**，被 `InsertTableAnnotation2` 取代）与 `InsertTableAnnotation2(UseAnchorPoint, X, Y, AnchorType, TableTemplate, Rows, Columns)`——第 3/4 位是 `AnchorType`（`swBOMConfigurationAnchorType_e`，**锚点类型**）。⇒ 函数里那个叫 `table_type` 的实参（`:2324` 与 `:2328` 两处 `int(table_type)`）实际落进 `AnchorType`，最多建出**通用表**，建不出孔表。官方孔表入口 `IView.InsertHoleTable2(UseAnchorPoint, X, Y, AnchorType, StartValue, TableTemplate)` 本模块没有。 | 高 |
| ⑤ 修订表 | **不能复用**（仅「已有表加一行」可复用） | `add_revision`（`:2489`）<br>`get_revision_table_feature`（`:2446`）<br>`insert_table_annotation`（`:2306`） | `add_revision` 确实调 `AddRevision(String)`（真写），但它**要求调用方先把修订表对象传进来**，而本模块**没有任何函数创建这张表**；`get_revision_table_feature` 是 getter。建表环节仍落在 `insert_table_annotation` 的 `table_type → AnchorType` 问题上（见 ④）。官方入口 `ISheet.InsertRevisionTable2(UseAnchorPoint, X, Y, AnchorType, TableTemplate, Shape, AutoUpdateZoomCells)` 本模块没有。⇒ 「修订表」作为功能整体不可复用，可复用的只有「已存在的表加一行修订号」这一小段。 | 高 |
| ⑥ 表面粗糙度 | **不能复用** | `_collect_view_professional_annotations`（`:1653`，符号回读在 `:1694`）<br>`drawing_review.py:_professional_annotation_report`（`:409`） | 全模块 `GetSFSymbols` 只出现 **1 次**，且在只读收集器里：`for owner in _as_sequence(_safe_member(view, "GetSFSymbols", default=[]))` → 取 `GetSymbolType/GetSymbol/GetDirectionOfLay` 塞进 `surface_finish_symbols` 列表返回。`drawing_review.py` 那边也只按视图/数量/文字核对这批**读回**记录。**没有任何 `InsertSurfaceFinishSymbol3` 调用**（官方为 `IModelDocExtension.InsertSurfaceFinishSymbol3`，14 参）。纯读回，按判据不算复用点。 | 高 |

## 汇总

- **能复用 3 项**：① 剖面视图 · ② 局部视图 · ③ 中心符号线（**受限**：只有自动批量路线，没有 `InsertCenterMark3`）
- **不能复用 3 项**：④ 孔表 · ⑤ 修订表 · ⑥ 表面粗糙度
- ① ② 虽有真实创建调用，但官方前置（画剖切线 / 画详图圆）在本模块内**无人负责**，直接拿来用会返回空或建不出东西。

## 三条交叉印证与记录（只记录，未改任何文件）

1. **模块自己就写明了边界**：`validate_generic_drawing_generation`（`:2094`）在改文档前主动拒活——`views.sections/details` 一律 `DRAWING_REQUESTED_VIEWS_UNSUPPORTED`（消息原文「通用生成器尚不能创建请求的辅助、轴测、剖视或局部视图」）；`holeRequirements` → `DRAWING_HOLE_REQUIREMENTS_UNSUPPORTED`（原文「尚不能创建孔标注或孔表」）；`professionalAnnotations` 里除 `centerMarks` 外任何字段 → `DRAWING_PROFESSIONAL_ANNOTATIONS_UNSUPPORTED`。⇒ 与本表 ③④⑥ 结论互相印证，且印证了「③ 的自动中心标记是它唯一放行的专业标注」。
2. **一处注释与官方源冲突（已定位，未修改）**：`insert_table_annotation` 上方来源块写「`InsertTableAnnotation` 的 Int32 Type 决定表的种类（孔表/修订表/BOM…）」，但官方两页 md 的第 3/4 参数实名 `AnchorType`，**没有表种类参数**。按铁律 5 的口径记为「本仓该说法无官方源支撑」，不在本次改动范围内。
3. **读快照时文件正在被改动**：两次读取之间头部新增了 `from scripts.sw_drawing_view_types import LABELLED_VIEW_TYPES`（第 12/16 行）。本表所有行号以**后一次**读取为准（例：`add_section_view` 在 `:998`，不是 `:996`；文件总行数 2746）。