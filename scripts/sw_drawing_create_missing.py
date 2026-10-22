"""★ 工程图缺口补齐（5 项）：断裂视图 / 辅助视图 / 表面粗糙度符号 / 基准符号 / 气泡序号。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的能力层）
# 文件:   scripts/sw_drawing_create_missing.py
# 定位:   ★ 2026-10-03 承 `specs/202-user-coverage-gaps` 的**工程图 5 项真缺口**：
#   断裂视图 · 辅助视图 · 表面粗糙度符号 · 基准符号 · 气泡序号（BOM 气泡）。
#   ★★ 这 5 项**本仓此前一个都没有** —— `docs/user-feature-coverage.md` §八列了它们，
#     而 `tools/audit_gap_implementations.py`（AST 量「有没有真调用」）也没命中。
#
#   ★★★ **每个函数的官方「前置」都写在 docstring 与返回值里** —— 本文件刻意这么做，
#     原因是这 5 项里有 **3 项靠调用前的选区**，而选区失败时 SolidWorks **静默返回 None**
#     ⇒ ★ 不把前置写清楚，调用者会把「没建出来」读成「能力坏了」。
#
#   =======================  ============================  ==============================
#   功能                      官方成员（反射 arity）              官方前置（逐字来源）
#   =======================  ============================  ==============================
#   断裂视图                  `IView.InsertBreak3`（6 参）        视图须按名字**解析得到**
#                                                          （官方示例用「选中视图」取得 IView）
# 辅助视图                  `IDrawingDoc.CreateAuxiliaryViewAt2`  「based on a **selecte
# d edge
#                                                            in a drawing view**」
# 表面粗糙度符号            `IModelDocExtension.               「based on the **last sel
# ection**」
#                             InsertSurfaceFinishSymbol3`（14 参） 且 **只有 leaderType !=
#                                                            swNO_LEADER 才用位置参数**
# 基准符号                  `IModelDoc2.InsertDatumTag2`（**零参**） 「at a **selected l
# ocation**」
#   气泡序号                  `IDrawingDoc.AutoBalloon5`（1 参，  ① 选视图/图纸 → ②
#                             形参是**对象**）                     `CreateAutoBalloonOptions`
#                                                            → ③ 设属性 → ④ 传对象调用
#   =======================  ============================  ==============================
#
#   ★★ **断裂视图为什么是 `InsertBreak3`**（铁律 4：先看官方是否标 Obsolete）：
# `InsertBreak`（4 参）与 `InsertBreak2`（5 参）**都标 Obsolete** ⇒ 可用的是 `InsertBrea
# k3`。
#     ★ 逐字签名（`C:\swapi\types\IView\InsertBreak3.md`）：
#       ```
#       System.object InsertBreak3( System.int Orientation, System.double Position1,
#         System.double Position2, System.int Style, System.int ShapeIntensity,
#         System.bool BreakSketchBlocks )
#       ```
#     ★ 与反射 dump `sw_api_sldworks.py:9698 'InsertBreak3': 6` **arity 一致** ✓
#
# ★★ **位置参数的单位**（规则 2 + 铁律 5）：官方 **只说 "Location of the first line in t
# he
# break"、没给单位** ⇒ ★ 按 SolidWorks API 惯例当作**米**，对外收**毫米**、边界换算一次
# 。
#     ★ 这个假设有**官方示例的数值佐证**（`Insert_Jagged_Cut_Break_Example_VB.md`）：
#       `InsertBreak3(2, -2.91950859897372E-02, 1.98236302285804E-02, …)`
#       ⇒ -29.195 mm / +19.824 mm ⇒ **官方确实用米** ✓ ★ 而本模块**把这个证据写进返回值**。
# ★ 官方 `GetBreakLines` 的 Remarks 还写明「**A drawing view can have break lines that a
# re
#       not applied**；要看「是不是真的断开了」用 `IView::IsBroken`」
#       ⇒ ★ 本模块**两个都回读**（断裂数 + `IsBroken`），不拿其中一个当唯一判据。
#
#   ★★ **表面粗糙度符号那三条字符串参数**（`MachAllowance` / `OtherVals` / `ProdMethod` /
# `SampleLen` / `MaxRoughness` / `MinRoughness` / `RoughnessSpacing`）官方**全是 `System
# .string`**
#     且**没给格式** ⇒ ★ 一律**原样透传**，不解析、不校验（★ 铁律 5：查不到就说查不到）。
#
#   ★★ **`AutoBalloon5` 的形参是对象**（`AutoBalloonOptions`），★ 而 `mcp-server` 的
#     `Param` **表达不了 COM 对象** ⇒ ★ 本文件在能力层**实现**它（内部先
#     `CreateAutoBalloonOptions()` 拿对象），★ **工具层不给它建 ToolSpec**。
#
#   官方依据（三源互证 · 铁律 4）:
#     · `C:\swapi\types\IView\InsertBreak3.md`（6 参 · Returns BreakLine）
#       + `C:\swapi\enums\swBreakLineOrientation_e.md`（Horizontal=1 / Vertical=2）
#       + `C:\swapi\enums\swBreakLineStyle_e.md`（Straight=1 / ZigZag=2 / Curve=3 /
#         SmallZigZag=4 / Jagged=5）
#       + `C:\swapi\examples\Insert_Jagged_Cut_Break_Example_VB.md`（调用序 + 米制数值）
#       + `C:\swapi\types\IView\GetBreakLines.md` / `IsBroken.md`（两条判据各自的语义）
#     · `C:\swapi\types\IDrawingDoc\CreateAuxiliaryViewAt2.md`（7 参）
# ★ 摘要逐字「Creates an auxiliary view **based on a selected edge in a drawing view**.
# 」
#     · `C:\swapi\types\IModelDocExtension\InsertSurfaceFinishSymbol3.md`（14 参）
#       ★ Remarks 逐字「…uses the location parameters for this method **only if** the surface
#         finish symbol has a leader leaderType **!= swNO_LEADER**.」
#       + `C:\swapi\enums\swSFSymType_e.md`（10 成员）+ `C:\swapi\enums\swLeaderStyle_e.md`
#       + `C:\swapi\examples\Get_Annotations_Array_Example_VB.md`（14 实参的**逐字**写法）
#     · `C:\swapi\types\IModelDoc2\InsertDatumTag2.md`（**零参**）
#       ★ 摘要逐字「Inserts a datum tag symbol **at a selected location**.」
# ★ 同一官方示例里的**调用序**：先 `SelectByID2("", "EDGE", …)`、**再** `InsertDatumTag2
# `
#     · `C:\swapi\types\IDrawingDoc\AutoBalloon5.md`（1 参 · Returns **Array of INotes**）
#       + `C:\swapi\types\IDrawingDoc\CreateAutoBalloonOptions.md`（零参）
# + `C:\swapi\examples\Add_Autoballoon_to_Face_Example_VB.md`（官方给的 4 步 + 13 条属性
# ）
#       + `C:\swapi\types\IAutoBalloonOptions\_overview.md`（19 个属性）
#   许可:   本仓库 MIT。★ **无第三方代码引入**（只照官方签名与官方示例写）。
#   覆盖:   全文件
# ⚠ 本文件为**静态签名比对后新写**，**未在本机实测**（铁律 2：真机由 Lead 独家执行）。
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

try:  # 包内载入（mcp-server 走这条）
    from .sw_connect import get_com_member, mm, set_com_member
    from .sw_drawing_view_types import SW_DRAWING_AUXILIARY_VIEW
except ImportError:  # 顶层载入（脚本 / 探针）
    from sw_connect import get_com_member, mm, set_com_member  # noqa: F401
    from sw_drawing_view_types import SW_DRAWING_AUXILIARY_VIEW  # noqa: F401

__all__ = [
    "insert_break_lines",
    "create_auxiliary_view",
    "insert_surface_finish_symbol",
    "insert_datum_tag",
    "auto_insert_balloons",
    "DRAWING_CREATE_MISSING_STATUS",
    "SW_BREAK_LINE_HORIZONTAL",
    "SW_BREAK_LINE_VERTICAL",
    "SW_BREAK_LINE_STRAIGHT",
    "SW_BREAK_LINE_ZIGZAG",
    "SW_BREAK_LINE_CURVE",
    "SW_BREAK_LINE_SMALL_ZIGZAG",
    "SW_BREAK_LINE_JAGGED",
    "SW_LEADER_NO_LEADER",
    "SW_LEADER_STRAIGHT",
    "SW_SF_BASIC",
]

# ── 官方枚举（★ 逐字数值，来源写在每个常量后面的注释里）──────────────────────────
#: `swBreakLineOrientation_e`（`C:\swapi\enums\swBreakLineOrientation_e.md`，2 个成员）
SW_BREAK_LINE_HORIZONTAL = 1  # swBreakLineHorizontal = 1
SW_BREAK_LINE_VERTICAL = 2  # swBreakLineVertical   = 2

#: `swBreakLineStyle_e`（`C:\swapi\enums\swBreakLineStyle_e.md`，5 个成员）
SW_BREAK_LINE_STRAIGHT = 1  # swBreakLine_Straight     = 1
SW_BREAK_LINE_ZIGZAG = 2  # swBreakLine_ZigZag       = 2
SW_BREAK_LINE_CURVE = 3  # swBreakLine_Curve        = 3
SW_BREAK_LINE_SMALL_ZIGZAG = 4  # swBreakLine_SmallZigZag  = 4
SW_BREAK_LINE_JAGGED = 5  # swBreakLine_Jagged       = 5

#: `swLeaderStyle_e` 里与表面粗糙度符号相关的成员（`C:\swapi\enums\swLeaderStyle_e.md`）
SW_LEADER_NO_LEADER = 0  # swNO_LEADER  = 0  ← ★ Official Remarks 拿它做判据的那个 0
SW_LEADER_STRAIGHT = 1  # swSTRAIGHT   = 1  ← 官方示例用的就是它

#: `swSFSymType_e`（`C:\swapi\enums\swSFSymType_e.md`，10 个成员）—— 只列本模块用得到的
SW_SF_BASIC = 0  # swSFBasic = 0（官方示例第一个实参就是它）

#: `swAnnotationType_e`（`C:\swapi\enums\swAnnotationType_e.md`，19 个成员）
#: ★ 这两个**不是**判据本身（判据用 IView 的 Get*SFCymbolCount / GetDatumTagCount），
#: ★ 而是给调用方一个「按型取注解」的旁路（`IView.GetAnnotationsByType(Type)`，1 参）。
SW_ANNOTATION_DATUM_TAG = 2  # swDatumTag  = 2
SW_ANNOTATION_SF_SYMBOL = 7  # swSFSymbol  = 7

#: ★ 气泡选项用到的 6 个枚举（★ 逐个核过官方页，★ 不写魔数）：
SW_BALLOON_LAYOUT_SQUARE = 1  # swDetailingBalloonLayout_Square          = 1
#   （`C:\swapi\enums\swBalloonLayoutType_e.md`）
SW_BALLOON_STYLE_CIRCULAR = 1  # swBS_Circular                              = 1
#   （`C:\swapi\enums\swBalloonStyle_e.md`）
SW_BALLOON_FIT_5_CHARS = 5  # swBF_5Chars                                = 5
#   （`C:\swapi\enums\swBalloonFit_e.md`）
SW_BALLOON_TEXT_ITEM_NUMBER = 1  # swBalloonTextItemNumber                    = 1
#   （`C:\swapi\enums\swBalloonTextContent_e.md`）
SW_BALLOON_ITEMS_DONT_CHANGE = (
    1  # swBalloonItemNumbers_DoNotChangeItemNumbers = 0x1 or 1
)
#   （`C:\swapi\enums\swBalloonItemNumbersOrder_e.md`）
SW_EDIT_BALLOON_RESEQUENCE = 1  # swEditBalloonOption_Resequence            = 1
#   （`C:\swapi\enums\swEditBalloonOption_e.md`）

#: ★ `swDrawingViewTypes_e` 里「这不是一个视图、而是图纸本身」的那个取值。
#: ★ 与 `sw_drawing_query.SHEET_PSEUDO_VIEW_TYPE` 同一个事实、同一份官方页
#:   （`swDrawingViewTypes_e`：`swDrawingSheet = 1`）；★ 本模块**自己写一份常量**而不
#:   跨模块 import，★ 是为了不让能力层依赖 `sw_drawing_query` 的导入形态。
SHEET_PSEUDO_VIEW_TYPE = 1


#: ★ 本模块覆盖到的缺口项 ⇒ 官方成员（★ 与 `docs/user-feature-coverage.md` §八 对齐用）
DRAWING_CREATE_MISSING_STATUS = {
    "断裂视图": "IView.InsertBreak3（★ InsertBreak / InsertBreak2 都标 Obsolete）",
    "辅助视图": "IDrawingDoc.CreateAuxiliaryViewAt2（★ 前置：先选中视图里的一条边）",
    "表面粗糙度符号": "IModelDocExtension.InsertSurfaceFinishSymbol3（★ 前置：基于最后一次选区）",
    "基准符号": "IModelDoc2.InsertDatumTag2（★ 零参；★ 前置：先选一个位置）",
    "气泡序号": "IDrawingDoc.AutoBalloon5（★ 形参是 AutoBalloonOptions **对象**）",
}


# ── 小工具（★ 判据要能回读 ⇒ 这里只提供「读得到多少」，★ 读不到就回 None，不猜）──────

#: ★ 2026-10-22 统一化：`_as_list` 原与 `sw_sketch.as_sequence` 两份逐字相同，
#:   现收敛到 sw_com_array.as_list；此处保留旧名作别名
try:
    from .sw_com_array import as_list as _as_list
except ImportError:
    from sw_com_array import as_list as _as_list


#: dispatch-guard: exempt internal-helper
def _read(obj, member):
    """★ 安全读一个零参 COM 成员；★ 读不到返回 `None`（★ 不猜、不静默当 0）。"""
    if obj is None:
        return None
    try:
        return get_com_member(obj, member)
    except Exception:  # noqa: BLE001
        return None


def _view_name(view) -> str | None:
    raw = _read(view, "GetName2")
    if raw is None:
        raw = _read(view, "Name")
    return None if raw is None else str(raw)


def _view_type(view) -> int | None:
    raw = _read(view, "Type")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _iter_views(model) -> list:
    """★ **当前图纸**上的真实视图对象（★ 按官方示例的 `GetFirstView` → `GetNextView` 走）。

    ★★ **必须跳过「图纸本身」那一个** —— 真机实测空图纸上 `GetFirstView()` 回的就是它
      （`Type == 1`、名字等于图纸名）⇒ 不跳过会列出一个**假视图**（本仓事实，见
      `sw_drawing_query.list_views` 的同款处理）。
    ★ **返回空列表表示"当前图纸上一个视图都没有"**；★ 返回 `None` 表示**读不到**。
    """
    first = _read(model, "GetFirstView")
    if first is None:
        return None
    views: list = []
    view = first
    seen = 0
    while view is not None and seen < 500:  #: 防御上限，不无限循环
        seen += 1
        if _view_type(view) != SHEET_PSEUDO_VIEW_TYPE:
            views.append(view)
        nxt = _read(view, "GetNextView")
        if nxt is None:
            break
        view = nxt
    return views


def _view_names(model) -> list[str]:
    views = _iter_views(model)
    if views is None:
        return []
    out = []
    for v in views:
        name = _view_name(v)
        out.append(name if name is not None else "<读不到名字>")
    return out


def _find_view(model, view_name: str):
    """★ 按**名字**取视图对象 —— ★ 回 `(view, None)` 或 `(None, 错误说明)`。

    ★ 为什么**按名字**而不是"先选中再 `GetSelectedObject6`"（官方示例那条路）：
      ★ `IView.InsertBreak3` 是**直接调在 IView 对象上**的，★ **调用本身不需要选区** ——
      官方示例要选它，只是**为了拿到那个 IView 对象** ⇒ ★ 本模块改成按名字解析，
      ★ 这样"断裂视图"**不需要调用者先准备选区**（★ 这一点写进返回值 `preconditions_held`）。
    ★ 名字**不区分大小写**地再比一次；★ 仍找不到就**报错并列出当前图纸上的视图名**
      （★ 不静默、★ 不用相近名字代替 —— 铁律 5）。
    """
    if not str(view_name or "").strip():
        return None, "view_name 不能为空"
    views = _iter_views(model)
    if views is None:
        return None, "读不到视图链（GetFirstView 回 None）：文档是工程图吗"
    if not views:
        return None, "当前图纸上一个视图都没有 ⇒ 先建视图再建断裂"
    for v in views:
        if _view_name(v) == str(view_name):
            return v, None
    for v in views:  # 大小写不敏感再比一次
        name = _view_name(v)
        if name is not None and name.lower() == str(view_name).lower():
            return v, None
    return None, "当前图纸上没有名为 %r 的视图；现有的是 %s" % (
        str(view_name),
        _view_names(model),
    )


def _sum_over_views(model, member: str) -> int | None:
    """★ 把一个**零参计数成员**在当前图纸所有视图上求和 —— ★ 这是本模块的**主要判据**。

    ★ 官方 `Get_Annotations_Array_Example_VB.md` 逐字就是这么读的
      （`count = swView.GetSFSymbolCount` / `count = swView.GetDatumTagCount` …）。
    ★★ 为什么用「求和」而不是「只看新视图」：★ 那 5 项里只有断裂视图能指定视图，
      ★ 而 **符号类注解挂在哪个视图取决于调用者的选区** ⇒ ★ 求和才是不挑视图的判据。
    ★ 返回 `None` = **读不到**（★ 不当 0 用，否则会把「读不到」误判成「没建出来」）。
    """
    views = _iter_views(model)
    if views is None:
        return None
    total = 0
    for v in views:
        #: dispatch-fwd: upstream _sum_over_views sites 二级转发：上游 10 个调用点**全是字面量**（5 distinct，两源可查）
        raw = _read(v, member)
        try:
            total += int(raw)
        except (TypeError, ValueError):
            continue
    return total


def _selection_count(model) -> int | None:
    """★ 当前选区计数 —— ★ 用来**回读"调用者前置有没有备好"**（★ 事实 8：`SelectByID2`
    的 bool 返回值不可信，★ **只有计数算数**）。"""
    sm = _read(model, "SelectionManager")
    if sm is None:
        return None
    try:
        return int(get_com_member(sm, "GetSelectedObjectCount2", -1))
    except Exception:  # noqa: BLE001
        return None


def _numeric_delta(before, after) -> int | None:
    """★ **计数**之差（`int(after) - int(before)`）；★ 任一读不到就回 `None`（★ 判据降级、不猜）。

    ★★ 2026-10-22 名字修正：本函数原叫 `_delta` —— 而同一个仓里**另有四份** `_delta`
      返回的是**特征名列表差**（已收敛为 `sw_feature_tree.new_features`）⇒
      ★ 同一个名字指两件事，容易把人带错 ✗ ⇒ 改名为 `_numeric_delta`。
    """
    if before is None or after is None:
        return None
    return int(after) - int(before)


def _break_state(view) -> dict:
    """★ 一个视图的**断裂状态**：`GetBreakLines()` 的数组长度 + `IsBroken()`。

    ★★ **两个都要，理由是官方把它们定义成了两件事**：
      · `GetBreakLines` 的 Remarks 逐字「A drawing view can have break lines **that are not
        applied**. To determine whether a view is broken, use `IView::IsBroken`.」
      · `IsBroken` 的 Remarks 逐字「indicates if the view is **displayed broken**, **not** if the
        view **has break lines**.」
      ⇒ ★ 拿断裂数当「断开了」的判据**会把没生效的断裂线读成已断开** ⇒ ★ 本模块两个都回。
    """
    lines = _as_list(_read(view, "GetBreakLines"))
    broken = _read(view, "IsBroken")
    try:
        broken = None if broken is None else bool(broken)
    except Exception:  # noqa: BLE001
        broken = None
    return {"break_count": len(lines), "is_broken": broken}


# ── ① 断裂视图 ────────────────────────────────────────────────────────────────


def insert_break_lines(
    model,
    view_name: str,
    position1_mm: float,
    position2_mm: float,
    orientation: int = SW_BREAK_LINE_VERTICAL,
    style: int = SW_BREAK_LINE_JAGGED,
    shape_intensity: int = 2,
    break_sketch_blocks: bool = True,
) -> dict:
    """★ **断裂视图**：`IView.InsertBreak3(6 参)` → `BreakLine`（★ **零选区前置**）。

    :param view_name: **当前图纸上**的视图名（如 `"Drawing View1"` / `"视图1"`）。
    :param position1_mm: 第一条断裂线的位置（**毫米**；★ 官方**没给单位**，本模块按米收、
      边界换算一次 —— ★ 官方示例的 `-2.91950859897372E-02` 正是 **-29.195 mm**）。
    :param position2_mm: 第二条断裂线的位置（同上，单位**毫米**）。
    :param orientation: `swBreakLineOrientation_e`：**1=Horizontal · 2=Vertical**。
    :param style: `swBreakLineStyle_e`：**1=Straight · 2=ZigZag · 3=Curve · 4=SmallZigZag · 5=Jagged**。
    :param shape_intensity: 锯齿强度，★ 官方逐字「valid range is **1 (most) through 5 (least)**」
      且**只对锯齿线生效**。
    :param break_sketch_blocks: 官方 `BreakSketchBlocks`：True 连草图块一起断。

    ★★★ **官方 `## Remarks` 的位置语义（逐字转述，不改写）**：
      > If the orientation of the break is **Horizontal** then Position1 and Position2 are
      > **Y** values relative to the drawing view origin …
      > **Vertical** then Position1 and Position2 are **X** values relative to the drawing view origin

      ⇒ ★ 也就是说：**横向断裂吃 Y、纵向断裂吃 X**（★ 两个值都是**相对视图原点**的）
      ⇒ ★ 本模块把「这两个数落在哪根轴上」原样回在 `positions_are_on_axis` 里。

    ★★ **为什么不是 `InsertBreak` / `InsertBreak2`**（铁律 4）：★ 那两个**都标 Obsolete**
      ⇒ 可用的是 `InsertBreak3`；★ 本仓 `sw_api_sldworks.py` 的反射 dump 里
      `'InsertBreak': 4` / `'InsertBreak2': 5` / `'InsertBreak3': 6` **三者的 arity 都在**,
      ★ 所以**只能靠官方页判哪条能走** ⇒ ★ 本模块**只走 `InsertBreak3`**。

    ★ **判据 = `GetBreakLines()` 的数组长度 + `IsBroken()`**（★ 两个都要，理由见
      `_break_state` 的 docstring）★ **不是**"返回非 None"。
    """
    if model is None:
        return {"ok": False, "op": "insert_break_lines", "error": "model 为 None"}
    if orientation not in (SW_BREAK_LINE_HORIZONTAL, SW_BREAK_LINE_VERTICAL):
        return {
            "ok": False,
            "op": "insert_break_lines",
            "error": "orientation 只能是 1(Horizontal) / 2(Vertical)，收到 %r"
            % (orientation,),
        }
    if style not in (
        SW_BREAK_LINE_STRAIGHT,
        SW_BREAK_LINE_ZIGZAG,
        SW_BREAK_LINE_CURVE,
        SW_BREAK_LINE_SMALL_ZIGZAG,
        SW_BREAK_LINE_JAGGED,
    ):
        return {
            "ok": False,
            "op": "insert_break_lines",
            "error": "style 只能是 swBreakLineStyle_e 的 1/2/3/4/5，收到 %r" % (style,),
        }

    view, err = _find_view(model, view_name)
    if view is None:
        return {
            "ok": False,
            "op": "insert_break_lines",
            "error": err,
            "preconditions_held": False,
            "available_views": _view_names(model),
        }

    before = _break_state(view)
    brk = get_com_member(
        view,
        "InsertBreak3",
        int(orientation),
        mm(float(position1_mm)),  #: ★ 官方没说单位 ⇒ 按米（示例佐证）
        mm(float(position2_mm)),
        int(style),
        int(shape_intensity),
        bool(break_sketch_blocks),
    )
    after = _break_state(view)

    #: ★ 回读官方示例读的那两个属性（`swBreakLine.Style` / `swBreakLine.ShapeIntensity`
    #: ）
    ret_style = _read(brk, "Style")
    ret_intensity = _read(brk, "ShapeIntensity")
    delta = _numeric_delta(before["break_count"], after["break_count"])
    return {
        "ok": bool(delta and delta > 0) and after["break_count"] > 0,
        "op": "insert_break_lines",
        "view_name": str(view_name),
        "returned_is_none": brk is None,
        "returned_style": ret_style,
        "returned_shape_intensity": ret_intensity,
        "break_state_before": before,
        "break_state_after": after,
        "break_count_delta": delta,
        "positions_are_on_axis": (
            "Y" if orientation == SW_BREAK_LINE_HORIZONTAL else "X"
        ),
        "position1_mm": float(position1_mm),
        "position2_mm": float(position2_mm),
        "preconditions_held": True,
        "precondition_note": (
            "★ 无选区前置：★ InsertBreak3 是**直接调在 IView 对象上**的 —— 官方示例要先选中视图"
            "只是为了**拿到那个 IView 对象**，★ 本模块改成**按视图名解析**，★ 所以不要求调用者备选区"
        ),
        "official_obsolete_note": (
            "★ InsertBreak / InsertBreak2 **都标 Obsolete** ⇒ 本模块只走 InsertBreak3（6 参）"
        ),
        "unit_assumption": (
            "★ 官方对 Position1/Position2 **未给单位**；本模块按 SolidWorks API 惯例当**米**、"
            "对外收毫米并在边界换算一次 —— ★ 官方示例 `InsertBreak3(2, -2.91950859897372E-02, "
            "1.98236302285804E-02, …)` = -29.195 mm / +19.824 mm，**佐证了米制**"
        ),
        "verified_by": "GetBreakLines().length + IView.IsBroken()",
    }


# ── ② 辅助视图 ────────────────────────────────────────────────────────────────


def create_auxiliary_view(
    model,
    x_mm: float,
    y_mm: float,
    *,
    z_mm: float = 0.0,
    label: str = "",
    not_aligned: bool = True,
    show_arrow: bool = True,
    flip: bool = False,
) -> dict:
    """★ **辅助视图**：`IDrawingDoc.CreateAuxiliaryViewAt2(7 参)` → 新视图对象。

    :param x_mm / y_mm / z_mm: 辅助视图的落位（**毫米**；★ 官方**没给单位**，本模块按米收、
      边界换算一次 —— ★ 与本仓工程图坐标惯例一致，见返回值里的 `unit_assumption`）。
    :param label: 官方 `Label` —— 辅助视图的标签文字。
    :param not_aligned: 官方形参名 `NotAligned`。
    :param show_arrow: 官方 `Showarrow`。
    :param flip: 官方 `Flip` —— True 翻转辅助视图所显示的那一侧。

    ★★★ **官方前置（摘要逐字，本模块最硬的那条约束）**：
      > Creates an auxiliary view **based on a selected edge in a drawing view**.

      ⇒ ★★ **调用前必须先选中一个视图里的一条边**；★ 而实体（边 / 面）**没有可用的名字**
      （本仓事实 32：`SelectByID2("Edge1","EDGE")` 真机计数为 0）⇒ ★ **本模块不代选**
      （★ 规则 3：禁裸坐标），★ 只**回读当前选区计数**、并把它写进
      `preconditions_held` ⇒ ★ 选区没备好时调用者能**看见失败原因**，★ 不会把它
      误读成「能力坏了」。

    ⚠★ **`NotAligned` 的官方说明与形参名自相矛盾，本模块**原样透传、照抄，不替官方解释**：
      官方 Parameters 逐字写的是「**NotAligned**: True **aligns** the view from its owner,
      false does not」—— ★ 名字说「不对齐」、说明说"对齐" ⇒ ★ 本模块**默认传 `True`**（跟形参名），
      ★ 并把这段矛盾**原样引在返回值里**，★ 由真机去定（★ 铁律 5：查不到就说查不到）。

    ★ **判据 = 当前图纸的视图数增量 + 新视图的 `Type`（应为 5 = `swDrawingAuxiliaryView`）**
      —— ★ 不是「返回非 None」。
    """
    if model is None:
        return {"ok": False, "op": "create_auxiliary_view", "error": "model 为 None"}
    before_views = _iter_views(model)
    before_names = _view_names(model)
    before_count = None if before_views is None else len(before_views)
    #: ★★★ 2026-10-07（规格 216 T-216-08）**声明式视图名 + 紧邻选区检查之前选** ——
    #:   ★ 官方那**四步**的第 1 步逐字：「Select one or more views or sheets for which to
    #:     automatically create BOM balloons」⇒ ★ 是**官方前置** ✓
    #:   ★★ 而**注入解析器会清空选区**（**事实 503**）⇒ ★ 模型没法在调工具前选好 ✗
    #:   ★ 规则 3 **不许收裸坐标** ⇒ ★ 收**视图名**（★ 名字不是坐标）；★ 选法走本仓既有的
    #:     `SelectByID2(<名字>, "DRAWINGVIEW", …)` 那一族（★ 同 create_hole_table 等）✓
    #:   ★ 判据是**回读选区计数**（★ 事实 8：SelectByID2 的返回值不可信）✓
    if str(view_name or "").strip():
        ext = get_com_member(model, "Extension")
        if ext is None:
            return {
                "ok": False,
                "op": "auto_insert_balloons",
                "error": "取不到 model.Extension ⇒ ★ 选不了视图（★ 前置未成立）",
            }
        import sw_part as _sp

        try:
            ext.SelectByID2(
                str(view_name),
                "DRAWINGVIEW",
                0,
                0,
                0,
                False,
                0,
                _sp._empty_callout(),
                0,
            )
        except Exception as exc:  # noqa: BLE001
            return {
                "ok": False,
                "op": "auto_insert_balloons",
                "view_name": str(view_name),
                "error": "按视图名选失败：%s: %s（★ 前置未成立、★ 与「气泡进不了图纸」是两件事）"
                % (type(exc).__name__, str(exc)[:120]),
            }
    sel = _selection_count(model)

    aux = get_com_member(
        model,
        "CreateAuxiliaryViewAt2",
        mm(float(x_mm)),
        mm(float(y_mm)),
        mm(float(z_mm)),
        bool(not_aligned),
        str(label),
        bool(show_arrow),
        bool(flip),
    )

    after_views = _iter_views(model)
    after_count = None if after_views is None else len(after_views)
    new_names = (
        []
        if before_names is None or after_views is None
        else [_view_name(v) for v in after_views if _view_name(v) not in before_names]
    )
    new_type = _view_type(aux) if aux is not None else None
    delta = _numeric_delta(before_count, after_count)
    return {
        "ok": bool(delta and delta > 0) and new_type == SW_DRAWING_AUXILIARY_VIEW,
        "op": "create_auxiliary_view",
        "returned_is_none": aux is None,
        "returned_name": _view_name(aux),
        "returned_type": new_type,
        "expected_type": SW_DRAWING_AUXILIARY_VIEW,
        "expected_type_name": "swDrawingAuxiliaryView（★ 取自 scripts/sw_drawing_view_types.py 单一真源）",
        "view_count_before": before_count,
        "view_count_after": after_count,
        "view_count_delta": delta,
        "new_view_names": new_names,
        "selection_count": sel,
        "preconditions_held": bool(sel and sel >= 1),
        "precondition_note": (
            "★ 官方逐字：'based on a **selected edge in a drawing view**' ⇒ ★ 调用前必须先选中"
            "视图里的一条边；★ 边没有可用名字（本仓事实 32）⇒ ★ 本模块**不代选**，只回读选区计数"
        ),
        "not_aligned_ambiguity": (
            "★ 官方形参名 NotAligned，★ 而 Parameters 逐字写 'True **aligns** the view from its "
            "owner' ⇒ ★ 名字与说明矛盾；★ 本模块**原样透传、不替官方解释**"
        ),
        "unit_assumption": (
            "★ 官方对 X/Y/Z **未给单位**；本模块按 SolidWorks API 惯例当**米**、对外收毫米并"
            "在边界换算一次 —— ★ 该假设**未由官方示例佐证**，须真机复核"
        ),
        "verified_by": "view_count_delta + returned_view.Type == 5",
    }


# ── ③ 表面粗糙度符号 ──────────────────────────────────────────────────────────


def insert_surface_finish_symbol(
    model,
    *,
    sym_type: int = SW_SF_BASIC,
    leader_type: int = SW_LEADER_STRAIGHT,
    x_mm: float = 0.0,
    y_mm: float = 0.0,
    z_mm: float = 0.0,
    lay_symbol: int = 0,
    arrow_type: int = 0,
    mach_allowance: str = "",
    other_vals: str = "",
    prod_method: str = "",
    sample_len: str = "",
    max_roughness: str = "",
    min_roughness: str = "",
    roughness_spacing: str = "",
) -> dict:
    """★ **表面粗糙度符号**：`IModelDocExtension.InsertSurfaceFinishSymbol3(14 参)` → `SFSymbol`。

    :param sym_type: `swSFSymType_e`（**0=Basic · 1=JIS_Machining_Req · 2=Dont_Machine**
      · 3..6=JIS_Surface_Texture_1..4 · 7=JIS_No_Machining · 8=JIS_Basic · 9=Machining_Req**）。
    :param leader_type: `swLeaderStyle_e`（**0=NO_LEADER · 1=STRAIGHT · 2=BENT · 3=UNDERLINED**
      · 4=SPLINE · 8=VDA**；★ 注意 256..4100 那几个是**位掩码**、要**与** 1/2/3/4/8 之一**合用**）。
    :param x_mm / y_mm / z_mm: 符号位置（**毫米**）—— ★★ **仅当 `leader_type != swNO_LEADER`
      时才被使用**，见下面逐字的 Remarks。
    :param lay_symbol: `swSFLaySym_e` —— 纹理方向（★ 本模块**不写死默认值**，官方页给的是 0）。
    :param arrow_type: `swArrowStyle_e` —— 箭头样式。
    :param mach_allowance / other_vals / prod_method / sample_len /
      max_roughness / min_roughness / roughness_spacing: 官方**全是 `System.string`** 且
      **官方页没给格式** ⇒ ★ 本模块**原样透传**，★ **不解析、不校验**。

    ★★★ **官方 `## Remarks` 逐字（本函数最核心的一条约束）**：
      > The SOLIDWORKS Design software uses the location parameters for this method
      > **only if** the surface finish symbol has a leader leaderType **!= swNO_LEADER**.

      ⇒ ★★ `leader_type == 0(swNO_LEADER)` 时，**三个位置参数被官方无视** ⇒ ★ 本模块在
      ★ 那一档**主动传 `0,0,0`**（而不是把调用者给的坐标白送进去）★★ 并把
      `location_applied=False` 与 `ignored_location_mm` **回在返回值里** ⇒ ★ 调用者能看见
      ★「我传的坐标被丢了」，★ 不会以为符号位置错了。

    ★★ **另一条官方前置**：官方摘要逐字「Creates a surface-finish symbol based on the
      **last selection**」⇒ ★ 调用前必须有选区；★ 本模块**不代选**（★ 规则 3）、
      只**回读选区计数**写进 `preconditions_held`。

    ★ **判据 = 全图纸 `IView.GetSFSymbolCount` 求和的增量**（★ 官方示例就是这么读的）
      —— ★ 不是「返回非 None」。
    """
    if model is None:
        return {
            "ok": False,
            "op": "insert_surface_finish_symbol",
            "error": "model 为 None",
        }
    #: ★★ 官方 Remarks 的那个判据，在此**落成代码**（★ 只有这一处决定位置参数用不用）
    location_applied = int(leader_type) != SW_LEADER_NO_LEADER
    loc_x, loc_y, loc_z = (
        (mm(float(x_mm)), mm(float(y_mm)), mm(float(z_mm)))
        if location_applied
        else (0.0, 0.0, 0.0)
    )

    sel = _selection_count(model)
    before = _sum_over_views(model, "GetSFSymbolCount")

    #: ★ 官方这一族挂在 **`IModelDocExtension`** 上（★ 不是 `IModelDoc2`）
    #:   ⇒ ★ 取法照本仓 15 个模块的同一写法（★ `sw_costing.py` / `sw_ref_geometry.py` 等）
    ext = _read(model, "Extension")
    if ext is None:
        return {
            "ok": False,
            "op": "insert_surface_finish_symbol",
            "error": "取不到 model.Extension —— ★ InsertSurfaceFinishSymbol3 挂在 "
            "IModelDocExtension 上，★ 不是 IModelDoc2",
            "preconditions_held": bool(sel and sel >= 1),
            "selection_count": sel,
            "precondition_note": "★ 官方摘要逐字：'based on the **last selection**'",
            "verified_by": "★ 没跑到调用那一步 ⇒ 无判据",
        }

    sfs = get_com_member(
        ext,
        "InsertSurfaceFinishSymbol3",
        int(sym_type),
        int(leader_type),
        loc_x,
        loc_y,
        loc_z,
        int(lay_symbol),
        int(arrow_type),
        str(mach_allowance),
        str(other_vals),
        str(prod_method),
        str(sample_len),
        str(max_roughness),
        str(min_roughness),
        str(roughness_spacing),
    )

    after = _sum_over_views(model, "GetSFSymbolCount")
    delta = _numeric_delta(before, after)
    return {
        "ok": bool(delta and delta > 0),
        "op": "insert_surface_finish_symbol",
        "returned_is_none": sfs is None,
        "sf_symbol_count_before": before,
        "sf_symbol_count_after": after,
        "sf_symbol_count_delta": delta,
        "sym_type": int(sym_type),
        "leader_type": int(leader_type),
        "location_applied": location_applied,
        "ignored_location_mm": None
        if location_applied
        else {"x": float(x_mm), "y": float(y_mm), "z": float(z_mm)},
        "selection_count": sel,
        "preconditions_held": bool(sel and sel >= 1),
        "precondition_note": (
            "★ 官方逐字：'based on the **last selection**' ⇒ ★ 调用前必须有选区；"
            "★ 且**只有 leaderType != swNO_LEADER 时官方才用那三个位置参数**"
        ),
        "official_remark_verbatim": (
            "The SOLIDWORKS Design software uses the location parameters for this method only "
            "if the surface finish symbol has a leader leaderType != swNO_LEADER."
        ),
        "annotation_type_hint": (
            "swSFSymbol = 7（C:\\swapi\\enums\\swAnnotationType_e.md）"
            "⇒ 也可用 IView.GetAnnotationsByType(7) 复核"
        ),
        "string_params_note": "★ 官方那 7 个文本参数**全是 System.string 且官方页没给格式** ⇒ 原样透传、不校验",
        "verified_by": "sum(IView.GetSFSymbolCount) delta",
    }


# ── ④ 基准符号 ────────────────────────────────────────────────────────────────


def insert_datum_tag(model) -> dict:
    """★ **基准符号（datum tag）**：`IModelDoc2.InsertDatumTag2()` → `DatumTag`（★ **零参**）。

    ★★★ **两条官方约束**：
      · 官方摘要逐字「Inserts a datum tag symbol **at a selected location**.」
        ⇒ ★★ **调用前必须先选中一个位置**（官方示例里是 `SelectByID2("", "EDGE", …)`）。
      · ★ 官方**零参数** ⇒ ★ 落点**完全由选区决定** ⇒ ★ 本模块**没有坐标入口**，
        ★ 这既是官方签名决定的、★ 也正好合上规则 3（禁裸坐标）。

    ⚠★ **注意入口在 `IModelDoc2` 上**（不是 `IModelDocExtension`）—— ★ 与表面粗糙度符号
      那个 14 参的入口**不是同一个对象**，★ 两个函数的 `get_com_member` 宿主因此不同
      （★ 事实 36 一族：**同名不同族要用对接口**，★ 而这里**连名字都不同**）。

    ★ **判据 = 全图纸 `IView.GetDatumTagCount` 求和的增量**（★ 官方示例就是这么读的）
      —— ★ 不是「返回非 None」。
    """
    if model is None:
        return {"ok": False, "op": "insert_datum_tag", "error": "model 为 None"}
    sel = _selection_count(model)
    before = _sum_over_views(model, "GetDatumTagCount")
    tag = get_com_member(model, "InsertDatumTag2")
    after = _sum_over_views(model, "GetDatumTagCount")
    delta = _numeric_delta(before, after)
    return {
        "ok": bool(delta and delta > 0),
        "op": "insert_datum_tag",
        "returned_is_none": tag is None,
        "datum_tag_count_before": before,
        "datum_tag_count_after": after,
        "datum_tag_count_delta": delta,
        "selection_count": sel,
        "preconditions_held": bool(sel and sel >= 1),
        "precondition_note": (
            "★ 官方逐字：'at a **selected location**' ⇒ ★ 调用前必须先选中一个位置"
            "（官方示例用 SelectByID2 选 EDGE）；★ 官方**零参数** ⇒ 落点完全由选区决定"
        ),
        "entry_point_note": "★ 入口是 IModelDoc2.InsertDatumTag2（零参），**不是** IModelDocExtension",
        "annotation_type_hint": (
            "swDatumTag = 2（C:\\swapi\\enums\\swAnnotationType_e.md）"
            "⇒ 也可用 IView.GetAnnotationsByType(2) 复核"
        ),
        "verified_by": "sum(IView.GetDatumTagCount) delta",
    }


# ── ⑤ 气泡序号（BOM 气泡）─────────────────────────────────────────────────────


def auto_insert_balloons(
    model,
    *,
    layout: int = SW_BALLOON_LAYOUT_SQUARE,
    style: int = SW_BALLOON_STYLE_CIRCULAR,
    size: int = SW_BALLOON_FIT_5_CHARS,
    upper_text_content: int = SW_BALLOON_TEXT_ITEM_NUMBER,
    upper_text: str = "",
    layername: str = "-None-",
    item_number_start: int = 1,
    item_number_increment: int = 1,
    item_order: int = SW_BALLOON_ITEMS_DONT_CHANGE,
    edit_balloons: bool = True,
    edit_balloon_option: int = SW_EDIT_BALLOON_RESEQUENCE,
    reverse_direction: bool = False,
    ignore_multiple: bool = True,
    insert_magnetic_line: bool = True,
    leader_attachment_to_faces: bool = True,
    view_name: str = "",
) -> dict:
    """★ **气泡序号（BOM 气泡）**：`IDrawingDoc.AutoBalloon5(AutoBalloonOptions)` → **Array of INotes**。

    ★★★ **官方 `## Remarks` 给的是**四步**，★ 本模块**严格照那四步走**（逐字转述）：
      > 1. Select one or more views or sheets for which to automatically create BOM balloons.
      > 2. Call `IDrawingDoc::CreateAutoBalloonOptions` to create an `IAutoBalloonOptions` object.
      > 3. Set the properties on the `IAutoBalloonOptions` object.
      > 4. Call this method using the `IAutoBalloonOptions` object in the `BalloonOptions` argument.

      ⇒ ★★ **前置**：★ 必须先选中**一个或多个视图 / 图纸**；★ 而选项对象**必须由调用方那一步
      ★ 用 `CreateAutoBalloonOptions()` 造出来** ⇒ ★ 本函数**内部**造，★ **不要求调用者会造**。

    :param layout: `swBalloonLayoutType_e`（默认 `swDetailingBalloonLayout_Square = 1`）。
    :param style: `swBalloonStyle_e`（默认 `swBS_Circular = 1`）。
    :param size: `swBalloonFit_e`（默认 `swBF_5Chars = 5`）。
    :param upper_text_content: `swBalloonTextContent_e`（默认 `swBalloonTextItemNumber = 1`
      ⇒ **气泡里显示件号**，★ 这正是「气泡序号」的语义）。
    :param item_order: `swBalloonItemNumbersOrder_e`（默认
      `swBalloonItemNumbers_DoNotChangeItemNumbers = 1`）。
    :param edit_balloon_option: `swEditBalloonOption_e`（默认
      `swEditBalloonOption_Resequence = 1`）。
    ★ 其余默认值**逐条照官方示例**（`Add_Autoballoon_to_Face_Example_VB.md`）——
      `ReverseDirection=False` / `IgnoreMultiple=True` / `InsertMagneticLine=True` /
      `LeaderAttachmentToFaces=True` / `Layername="-None-"` / `ItemNumberStart=1` /
      `ItemNumberIncrement=1` / `EditBalloons=True`。

    ⚠★ **默认沿用官方示例的取值，★ 但枚举页对其中几条没写"默认是什么"**
      ⇒ ★ 本模块**不声称这些是 SolidWorks 的默认**，★ 只声称「这是官方示例用的值」。

    ⚠★ **`AutoBalloon5` 的形参是 COM 对象** ⇒ ★ `mcp-server` 的 `Param` 表达不了
      ⇒ ★ **本能力层实现它、工具层不给它建 ToolSpec**（★ 见 `mcp-server/tool_specs_batch73.py`）。

    ★ **判据 = 返回数组的长度（官方 Returns 逐字是 "Array of INotes"）+ 全图纸
      `IView.GetNoteCount` 求和的增量** —— ★ 两个都回，★ **不是**"返回非 None"。
    ★ **属性设不上不静默**：★ 每条属性**逐个**写，★ 写失败的名字进 `property_set_failures`
      （★ 迟到绑定下某些属性可能不可写，★ 例如本仓事实 47 一族的后端限制）。
    """
    if model is None:
        return {"ok": False, "op": "auto_insert_balloons", "error": "model 为 None"}
    sel = _selection_count(model)
    before = _sum_over_views(model, "GetNoteCount")

    #: ★ 官方第 2 步：★ **零参**造选项对象（★ 反射 dump `'CreateAutoBalloonOptions': 0`
    #: ✓）
    opts = get_com_member(model, "CreateAutoBalloonOptions")
    if opts is None:
        return {
            "ok": False,
            "op": "auto_insert_balloons",
            "error": "CreateAutoBalloonOptions() 回 None ⇒ 拿不到 IAutoBalloonOptions 对象",
            "preconditions_held": bool(sel and sel >= 1),
            "selection_count": sel,
            "precondition_note": "★ 官方第 1 步：先选中一个或多个视图 / 图纸",
            "verified_by": "★ 没跑到调用那一步 ⇒ 无判据",
        }

    #: ★ 官方第 3 步：★ 设属性。★ **逐条写、写失败不吞**（★ 名字进 failures）
    wanted = {
        "Layout": int(layout),
        "Style": int(style),
        "Size": int(size),
        "UpperTextContent": int(upper_text_content),
        "UpperText": str(upper_text),
        "Layername": str(layername),
        "ItemNumberStart": int(item_number_start),
        "ItemNumberIncrement": int(item_number_increment),
        "ItemOrder": int(item_order),
        "EditBalloons": bool(edit_balloons),
        "EditBalloonOption": int(edit_balloon_option),
        "ReverseDirection": bool(reverse_direction),
        "IgnoreMultiple": bool(ignore_multiple),
        "InsertMagneticLine": bool(insert_magnetic_line),
        "LeaderAttachmentToFaces": bool(leader_attachment_to_faces),
    }
    failures: list[str] = []
    for key, value in wanted.items():
        try:
            set_com_member(opts, key, value)
        except Exception as exc:  # noqa: BLE001
            failures.append("%s(%s)" % (key, str(exc)[:60]))

    #: ★ 官方第 4 步：★ 把对象塞进 `BalloonOptions`
    notes = get_com_member(model, "AutoBalloon5", opts)
    balloon_notes = _as_list(notes)

    after = _sum_over_views(model, "GetNoteCount")
    delta = _numeric_delta(before, after)
    return {
        #: ★★★ 2026-10-06（规格 209 · B2-2 · idx 34）：**判据收紧成纯回读** ——
        #: 原先 `ok` 是 `bool(balloon_notes) and (delta is None or delta >= 0)`，两处都
        #: 不合规格：
        #: ① 它依赖 `AutoBalloon5` **返回的数组** ⇒ **那是返回值**（规则 6：判据要用回读
        #: ）；
        #:   ② `delta >= 0` **太松**（★ **差 0 也就是「什么都没插」照样通过**）。
        #:   ⇒ 现在：`ok = delta 读得到 且 > 0`（★ **视图的标注数真的涨了**才算成），
        #:   ★ 而返回的数组长度**照旧回报**（`balloon_note_count` / `returned_is_none`），
        #:   只是**不当判据** ✓ —— ★ 这正是裁决书要的那个「**真机定案**」的落点 ✓
        "ok": (delta is not None and delta > 0),
        "criterion": (
            "★ **纯回读**：`sum(IView::GetNoteCount)` 的**增量 > 0**"
            "（★ 不用 `AutoBalloon5` 返回的数组当判据）"
        ),
        "op": "auto_insert_balloons",
        "returned_is_none": notes is None,
        "balloon_note_count": len(balloon_notes),
        "note_count_before": before,
        "note_count_after": after,
        "note_count_delta": delta,
        "options_object_created": True,
        "property_set_failures": failures,
        "selection_count": sel,
        "preconditions_held": bool(sel and sel >= 1),
        "precondition_note": (
            "★ 官方第 1 步逐字：'Select one or more **views or sheets**' ⇒ ★ 调用前必须选中"
            "视图或图纸；★ 第 2 步的选项对象**由本函数内部**用 CreateAutoBalloonOptions() 造"
        ),
        "official_returns_note": "★ 官方 Returns 逐字是 'Array of INotes' ⇒ 数组长度就是气泡数",
        "official_precondition_bom_table": (
            "★★★ 官方示例 `Add_Autoballoon_to_Face_Example_VB.md` 的 Preconditions 逐字："
            "「Open a drawing **with a bill of materials (BOM) table**」⇒ ★★ 没有 BOM 表时"
            "它**静默什么都不插**（★ 2026-10-06 真机定案：`GetNoteCount` **0 → 0**、"
            "返回的数组**长度为 0**）—— ★ 这正好解释了**两家外部项目结论互相矛盾**那件事 ✓"
        ),
        "defaults_note": (
            "★ 默认值逐条照**官方示例**（Add_Autoballoon_to_Face_Example_VB.md）；"
            "★ **不声称**它们是 SolidWorks 的出厂默认"
        ),
        "verified_by": "★ **sum(IView.GetNoteCount) 的增量 > 0**（纯回读）；"
        "★ 返回的数组长度只**回报**、**不当判据**",
    }


# ── ★★ 本模块**不做**的，以及为什么（★ 铁律 4 + 铁律 5）──────────────────────────
#
# ① **`InsertBreak` / `InsertBreak2`**（断裂视图的另两条路）：★ 官方**都标 Obsolete**
#    ⇒ 本模块**只走 `InsertBreak3`**（★ 上一节已逐条写明）。
#
# ② **断裂线的信息读取**（`GetBreakLineInfo2` / `GetBreakLineCount2`）：
#    ★ 本模块的判据用 `GetBreakLines()`（★ 官方 `GetBreakLines.md` 的 See Also 明确列出它）
#    + `IsBroken()` ⇒ ★ 不再引第三条同义路径，★ **免得把「官方没写语义」的成员当真源**。
#
# ③ **表面粗糙度符号的 `lay_symbol` / `arrow_type` 默认值**：
#    ★ 本模块传 **0** ⇒ ★ 但 `swSFLaySym_e` / `swArrowStyle_e` 的 "0 是什么"**本轮没查**
#    ⇒ ★ **不写死「0 = 某个具体样式」的断言**，★ 只把实参原样透出（★ 铁律 5）。
#
# ④ **辅助视图的落位方向**（官方没给任何「视图该往哪边摆」的规则）：★ 本模块**不猜**，
#    ★ `flip` / `not_aligned` 一律**原样透传**，★ 并把官方那句自相矛盾的说明**原样引出**。
#
# ⑤ **工具层（`mcp-server`）不给气泡建 ToolSpec**：★ 形参是 COM 对象、★ `Param` 表达不了
# ⇒ ★ 这不是遗漏，是**形态不同**（★ 同 `sw_mold_core_cavity_split` 那类「另走一层」的处
# 置）。


# ── 规格 209 · B4-5（idx 205 `model_annotations`）─────────────────────────────────────
# ───────
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力实现）· ★ 铁律 1「只缝合不发明」
# 文件:   scripts/sw_drawing_create_missing.py —— 追加 `insert_model_annotations`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B4-5** · 外部项目 idx **205 `model_a
#           nnotations`**。
#   ★★ 裁决书的**建议落点**是 `scripts/sw_drawing.py`，★ 而**我改成落这里** ——
#     理由**可核**：`scripts/sw_drawing.py` 只有 **29 行**、是**桥接壳**
# （它 `exec_module` 加载 `subskills/solidworks-engineering-drawing/scripts/drawing_work
# flow.py`
#     再 `globals().update`），★ **往里加实现会被桥接逻辑吞掉/覆盖**；
# 而**真正带视图助手**的是本模块（`_iter_views` / `_sum_over_views` / `_delta` / `_find_
# view`
# / `_view_names` / `_selection_count` —— ★ 裁决书自己要求「**复用**该文件已有的读侧助手
# ，
#     **别新造**」，★ 那就只能落这里）✓
#   ★ 同一条裁决书还要求与 idx 34 `balloon` / idx 52 `centerline` **同族复用** ——
#     ★ 那两条的落点本来也就是本模块（`auto_insert_balloons` 已在本文件里）✓
# 官方依据 （★ 铁律 4：`C:\swapi` 逐页读过）：
#   · `C:\swapi\types\IDrawingDoc\InsertModelAnnotations4.md` —— **8 参**：
#     `System.object InsertModelAnnotations4(System.int Option, System.int Types,
#      System.bool AllViews, System.bool DuplicateDims, System.bool HiddenFeatureDims,
#      System.bool UsePlacementInSketch, System.bool InsertAllAnnotations,
#      System.bool InsertAllReferenceGeometry)`
#     ★ `## Parameters` 逐字：`Types` **只在两个 `InsertAll*` 都是 False 时才有效**；
# `DuplicateDims=True` = **消除重复尺寸**；`HiddenFeatureDims=True` = 连隐藏特征的尺寸也
# 插；
#       `UsePlacementInSketch=True` = 按**草图里的摆放**插 ✓
#     ★ `## Returns` 逐字：「Array of inserted `IAnnotation` objects」
# ★ 摘要逐字：「Inserts model annotations into this drawing document's **currently selec
# ted
#       drawing view**.」
# · `C:\swapi\enums\swImportModelItemsSource_e.md` —— **EntireModel=0** · SelectedFeatur
# e=1 ·
#     SelectedComponent=2 · AssemblyOnly=3
#   · `C:\swapi\enums\swInsertAnnotation_e.md` —— ★ **26 个成员的位掩码**
#     （★ 官方 Description 逐字 **Bitmask**）⇒ ★ 本模块 **26 个全抄进表**（★ 一个不漏）✓
#   · `C:\swapi\types\IView\GetAnnotationCount.md` —— `System.int GetAnnotationCount()`
#     ★★ **这是本条的判据来源**（视图里的标注数）✓
# · ★★ `C:\swapi\examples\Insert_Model_Annotations_Example_VB.md` —— **调用序**（逐字）
# ：
#     ```
#     Set swView = swDrawing.CreateDrawViewFromModelView3(<模型路径>, "*Front", x, y, 0)
# status = swModelDocExt.SelectByID2("Drawing View1", "DRAWINGVIEW", 0,0,0, False, 0, No
# thing, 0)
#     status = swDrawing.ActivateView("Drawing View1")      ← ★ **先选中、再激活**
#     swModel.ClearSelection2 True
#     annotations = swDrawing.InsertModelAnnotations4(0, swInsertDimensionsMarkedForDrawing,
#                                                      True, False, False, False, False, False)
#     ```
# ⇒ ★★ 本函数**严格照这个序**（★ **`ActivateView` 那一步是示例独有的，签名里看不出来**）
# ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────
# ★★ **判据**（规则 6）：★ 它回**标注对象数组**（COM 对象 ⇒ **过不了 JSON 边界**）⇒
# ★★ 本函数用 **`IView::GetAnnotationCount()` 的前后回读**（本模块既有 `_sum_over_views`
# ）+
#   `_numeric_delta()` 当判据 ✓ —— ★ **不拿返回的数组长度当唯一判据**
#   （★ 同 `PostIntersect` 那类教训）

#: ★ 官方 `swImportModelItemsSource_e`（★ 逐值抄自 `C:\swapi\enums\`）
#: enum-gate: enum swImportModelItemsSource_e
MODEL_ITEM_SOURCES = {
    "entire_model": 0,
    "selected_feature": 1,
    "selected_component": 2,
    "assembly_only": 3,
}

#: ★★ 官方 `swInsertAnnotation_e` —— **26 个成员一个不漏**（★ 位掩码；逐值抄自该页的 Val
#: ue 列）✓
#:   ⚠ **不许跨条复制别的映射表**；★ 本表只属于这个成员 ✓
#: enum-gate: enum swInsertAnnotation_e
ANNOTATION_TYPE_BITS = {
    "swInsertCThreads": 1,
    "swInsertDatums": 2,
    "swInsertDatumTargets": 4,
    "swInsertDimensions": 8,
    "swInsertInstanceCounts": 16,
    "swInsertGTols": 32,
    "swInsertNotes": 64,
    "swInsertSFSymbols": 128,
    "swInsertWelds": 256,
    "swInsertAxes": 512,
    "swInsertCurves": 1024,
    "swInsertPlanes": 2048,
    "swInsertSurfaces": 4096,
    "swInsertPoints": 8192,
    "swInsertOrigins": 16384,
    "swInsertDimensionsMarkedForDrawing": 32768,
    "swInsertHoleWizardProfileDimensions": 65536,
    "swInsertHoleWizardLocationDimensions": 131072,
    "swInsertRefPoints": 262144,
    "swInsertDimensionsNotMarkedForDrawing": 524288,
    "swInsertholeCallout": 1048576,
    "swInsertWeldBeads": 2097152,
    "swInsertSketches": 4194304,
    "swInsertWeldBeads_ET": 8388608,
    "swInsertTolerancedDims": 16777216,
    "swInsertCenterOfMass": 33554432,
}


def _annotation_mask(types) -> int:
    """★ 把**类型名**（逗号分隔字符串，或序列）**按位或**成官方要的位掩码。

    :raises ValueError: 出现**不在官方 26 个成员里**的名字（★ 铁律 5：**不猜**、不静默忽略）✓
    """
    if types is None or types == "":
        return 0
    if isinstance(types, str):
        names = [x.strip() for x in types.split(",") if x.strip()]
    else:
        names = [str(x).strip() for x in types if str(x).strip()]
    mask = 0
    for name in names:
        key = name if name.startswith("swInsert") else "swInsert" + name
        if key not in ANNOTATION_TYPE_BITS:
            raise ValueError(
                "未知的标注类型 %r；合法的是官方 swInsertAnnotation_e 的 26 个成员：%s"
                % (name, ", ".join(sorted(ANNOTATION_TYPE_BITS)))
            )
        mask |= ANNOTATION_TYPE_BITS[key]
    return mask


def insert_model_annotations(
    model,
    view_name: str = "",
    *,
    source: str = "entire_model",
    types="",
    all_views: bool = False,
    duplicate_dims: bool = False,
    hidden_feature_dims: bool = False,
    use_placement_in_sketch: bool = False,
    insert_all_annotations: bool = False,
    insert_all_reference_geometry: bool = False,
) -> dict:
    """★ **把模型标注插进工程图视图**（官方 `IDrawingDoc::InsertModelAnnotations4`，**8 参**）。

    :param view_name: 要操作的视图名（★ 留空 = 用**第一个**视图 —— 本模块的 `_iter_views`）。
    :param source: 官方 `Option` —— `entire_model`(0) / `selected_feature`(1) /
        `selected_component`(2) / `assembly_only`(3)。
    :param types: 官方 `Types`（位掩码）—— 收**逗号分隔的类型名**（可省 `swInsert` 前缀）。
        ★ **只在两个 `insert_all_*` 都是 `False` 时有意义**（官方逐字）。
    :param all_views: 官方 `AllViews`。
    :param duplicate_dims: 官方 `DuplicateDims` —— `True` **消除重复尺寸**。
    :param hidden_feature_dims: 官方 `HiddenFeatureDims`。
    :param use_placement_in_sketch: 官方 `UsePlacementInSketch`。
    :param insert_all_annotations: 官方 `InsertAllAnnotations`。
    :param insert_all_reference_geometry: 官方 `InsertAllReferenceGeometry`。
    :returns: `{ok, entry_used, view, source, mask, types_used, annotation_count_before,
        annotation_count_after, annotation_delta, returned_count, error}`

    ★★ **判据（规则 6）**：★ 它回**标注对象数组**（COM 对象 ⇒ 过不了 JSON 边界）⇒
      ★ 判据是 **`IView::GetAnnotationCount()` 的前后回读**（★ 本模块既有 `_sum_over_views`）+
      `_numeric_delta()` —— ★ **不拿返回数组长度当唯一判据** ✓
    ★★ **调用序照官方示例**：**先选中视图**（`SelectByID2`，类型 `DRAWINGVIEW`）⇒
      **再 `ActivateView`**（★ 这一步签名里看不出来）⇒ `ClearSelection2` ⇒ 调它 ✓
    """
    from sw_connect import get_com_member  # noqa: E402

    out: dict = {
        "ok": False,
        "entry_used": "IDrawingDoc::InsertModelAnnotations4(8 参)",
        "view": None,
        "source": str(source),
        "mask": None,
        "types_used": None,
        "annotation_count_before": None,
        "annotation_count_after": None,
        "annotation_delta": None,
        "returned_count": None,
        "selected_count": None,
        "error": None,
        "note": None,
        "★": "判据 = **`IView::GetAnnotationCount()` 的前后回读**（★ 本模块既有 `_sum_over_views`）；"
        "★ 它回的是 **COM 标注对象数组** ⇒ **过不了 JSON 边界**，故**不当唯一判据**",
    }
    if model is None:
        out["error"] = "model 为 None"
        return out
    src = str(source).strip().lower()
    if src not in MODEL_ITEM_SOURCES:
        out["error"] = "未知的 source %r；合法：%s" % (
            source,
            ", ".join(sorted(MODEL_ITEM_SOURCES)),
        )
        return out
    try:
        out["mask"] = _annotation_mask(types)
    except ValueError as exc:
        out["error"] = str(exc)[:300]
        return out
    if (
        not insert_all_annotations
        and not insert_all_reference_geometry
        and out["mask"] == 0
    ):
        out["error"] = (
            "`types` 是空的、而两个 `insert_all_*` 也都是 False ⇒ ★ 官方逐字："
            "`Types` **只在** `InsertAllAnnotations` 与 `InsertAllReferenceGeometry` "
            "都是 False 时**才有意义** ⇒ 那样等于**什么都没让它插**。"
            "★ 本函数**不猜你要什么**，如实拒绝 ✓"
        )
        return out
    try:
        views = _iter_views(model)
    except Exception as exc:  # noqa: BLE001
        out["error"] = "取视图失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    if not views:
        out["error"] = (
            "这张工程图里**一个视图都没有** ⇒ 官方摘要逐字是"
            "「into this drawing document's **currently selected drawing view**」"
            "⇒ 没有视图就没有可操作的对象 ✓"
        )
        return out
    if str(view_name or "").strip():
        #: ⚠ ★ 我第一版写的是 `target = _find_view(...)` —— ★★ 而它回的是 **`(view, erro
        #: r)` 元组**
        #: （见它的 docstring）⇒ 把元组当视图对象用 ⇒ `_view_name` 读不到 ⇒ 报"取不到视
        #: 图名"
        #:   ★ 一个**指不出真因**的错。★ 记下来：**用既有助手前先读它的返回值形状** ✓
        target, why = _find_view(model, str(view_name).strip())
        if target is None:
            out["error"] = "找不到视图 %r：%s" % (view_name, why)
            return out
    else:
        target = views[0]
    out["view"] = _view_name(target)
    out["annotation_count_before"] = _sum_over_views(model, "GetAnnotationCount")
    if not out["view"]:
        out["error"] = "取不到视图名（★ 后面的 SelectByID2 / ActivateView 都要名字）"
        return out
    try:
        from sw_part import _empty_callout  # noqa: E402

        ext = get_com_member(model, "Extension")
        #: ★★ 官方示例的**调用序**：先选中视图、**再激活**、再清选区
        get_com_member(model, "ClearSelection2", True)
        get_com_member(
            ext,
            "SelectByID2",
            out["view"],
            "DRAWINGVIEW",
            0.0,
            0.0,
            0.0,
            False,
            0,
            _empty_callout(),
            0,
        )
        out["selected_count"] = _selection_count(model)
        get_com_member(model, "ActivateView", out["view"])
        #: ★★ **选区去留取决于 `AllViews`**（★ 这条是读官方示例读出来的，不是猜的）：
        #:   官方示例走的是 `AllViews=True`，所以它在调用前 `ClearSelection2 True`；
        #:   而 `AllViews=False` 时官方摘要要的是「**currently selected drawing view**」
        #:   ⇒ ★★ 那时**必须把视图留在选区里** —— ★ 我第一版**无脑清掉** ⇒
        #:   `InsertModelAnnotations4` **回一个空数组**（★ 一个指不出真因的现象）✓
        if all_views:
            get_com_member(model, "ClearSelection2", True)
        returned = get_com_member(
            model,
            "InsertModelAnnotations4",
            int(MODEL_ITEM_SOURCES[src]),
            int(out["mask"]),
            bool(all_views),
            bool(duplicate_dims),
            bool(hidden_feature_dims),
            bool(use_placement_in_sketch),
            bool(insert_all_annotations),
            bool(insert_all_reference_geometry),
        )
    except Exception as exc:  # noqa: BLE001
        out["error"] = "调用失败：%s: %s" % (type(exc).__name__, str(exc)[:220])
        return out
    out["returned_count"] = len(list(returned)) if returned is not None else 0
    try:
        out["annotation_count_after"] = _sum_over_views(model, "GetAnnotationCount")
        out["annotation_delta"] = _numeric_delta(
            out["annotation_count_before"], out["annotation_count_after"]
        )
    except Exception as exc:  # noqa: BLE001
        out["error"] = "后置回读失败：%s" % str(exc)[:150]
        return out
    out["ok"] = bool(out["annotation_delta"] and out["annotation_delta"] > 0)
    if not out["ok"]:
        out["error"] = (
            "回读判据未过：视图标注数 %r → %r（差 %r）· 官方回的数组长度 %r —— "
            "★ 如实判「没插进去」（★ 不拿返回值冒充）"
            % (
                out["annotation_count_before"],
                out["annotation_count_after"],
                out["annotation_delta"],
                out["returned_count"],
            )
        )
    out["types_used"] = sorted(
        k for k, v in ANNOTATION_TYPE_BITS.items() if v & out["mask"]
    )
    return out


# ── 规格 209 · B2-3（idx 52 `centerline`）─────────────────────────────────────────────
# ───────
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力实现）· ★ 铁律 1「只缝合不发明」
# 文件:   scripts/sw_drawing_create_missing.py —— 追加 `insert_center_lines`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B2-3** · 外部项目 idx **52 `centerli
#           ne`**。
#   ★★ 裁决书（§一）：采纳，且「**须真机定案**」—— 理由：**两家外部项目结论互相矛盾**
# （一家说零件视图上 `InsertCenterLine2` **静默无效**，另一家直接调并回 `bool(result)`）
# ✓
#   ★★★ **关于裁决书那条「与 idx 30 `auto_center_marks` 合并成一条工具两种模式」的建议 ——
#     我核实后**没有照做**，理由可核**：两条入口的**入参形状不同** ——
#     本条的形参可以全做成标量（视图名 + 实体序号 + 类型），而
# `auto_center_marks` 收的是**结构化 requirements 列表**（`[{"id","view","targets","coun
# t"}]`，
# 见 `subskills/…/drawing_workflow.py::auto_insert_center_marks`）⇒ ★ `Param` **表达不了
# **；
# ★★ 硬合并会造出一个「**一半参数对一半模式无意义**」的工具 ⇒ ★ 与本仓「参数要能表态」相
# 悖 ✓
#     ⇒ ★ 本批**只做本条新入口**，并**另行补 `AutoInsertCenterMarks2` 的真机验证**
#       （★ 那正是裁决书 §一 第 2 条点名的缺口：「批量路从未单独真机验证」）✓
# 官方依据 （★ 铁律 4：`C:\swapi` 逐页读过）：
# · `C:\swapi\types\IDrawingDoc\InsertCenterLine2.md` —— `Centerline InsertCenterLine2()
# `
#     ★ 摘要逐字：「Inserts a centerline on the **selected entities**.」
#     ★ `## Returns` 逐字：「Pointer to the `ICenterLine` object」
#     ⚠ ★ **既无 `## Remarks` 也无 `Parameters`** ⇒ ★ 「要选什么」**只能从官方示例读** ✓
# · ★★ `C:\swapi\examples\Get_Centerlines_in_Drawing_Example_VB.md` —— **调用序**（逐字
# ）：
#     ```
#     SelectByID2("cylinder20-9@Drawing View1", "COMPONENT", 0,0,0, False, 0, Nothing, 0)
#     SelectByID2("", "FACE", 0.513…, 0.455…, 250.01…, False, 0, Nothing, 0)
#     Set swCenterLine = swDrawing.InsertCenterLine2()
#     ```
#     ⇒ ★ 官方先选**组件**、再按**点**选一个**面** ⇒ ★ 说明它选的是**工程图视图里**的实体 ✓
#   · `C:\swapi\types\IView\GetVisibleEntities2.md` ——
#     `System.object GetVisibleEntities2(Component2 LpViewComponent, System.int EntityType)`
#     ★★ **没有 out 参** ⇒ pywin32 可直接用 ✓
# · `C:\swapi\enums\swViewEntityType_e.md` —— Edge=1 · Vertex=2 · Face=3 · SilhouetteEdg
# e=4
#   · `C:\swapi\types\IView\GetCenterLineCount.md` —— `System.int GetCenterLineCount()`
#     ★★ **本条的判据来源**（视图里的中心线数）✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────
# ★★ **选择怎么做的（★ 这是本条的实质）**：官方示例走「按点选面」—— ★ 那要**猜坐标**；
#   ★★ 而本仓有更稳的一条（**事实 32**：`IEntity::Select4` **按对象**选）⇒
# ★ 本函数用 `IView::GetVisibleEntities2` 把**视图里可见的实体对象**取出来、再 `Select4`
#  ✓
#   ★ 这选的是**同一类东西**（视图里的实体），★ 只是**不猜坐标** ✓

#: ★ 官方 `swViewEntityType_e`（★ 逐值抄自 `C:\swapi\enums\swViewEntityType_e.md`）
#: enum-gate: enum swViewEntityType_e
VIEW_ENTITY_TYPES = {
    "edge": 1,
    "vertex": 2,
    "face": 3,
    "silhouette_edge": 4,
}


def insert_center_lines(
    model, view_name: str = "", *, entity_type: str = "edge", entity_index: int = 0
) -> dict:
    """★ **在工程图视图里插中心线**（官方 `IDrawingDoc::InsertCenterLine2`，**零参**）。

    :param view_name: 视图名（★ 留空 = 当前图纸第一个视图）。
    :param entity_type: `edge`(1) / `vertex`(2) / `face`(3) / `silhouette_edge`(4)
        （★ 官方 `swViewEntityType_e`；★ 走 `IView::GetVisibleEntities2` 取**视图里可见的**实体）。
    :param entity_index: 选第几个（0 基 —— ★ 声明式，★ 规则 3：**不收坐标**）。
    :returns: `{ok, entry_used, view, entity_type, entity_index, visible_count, selection_count,
        centerline_count_before, centerline_count_after, centerline_delta, returned_is_none,
        error}`

    ★★ **判据（规则 6）**：① **选区计数**（事实 8：不许信返回值）；
      ② ★ **`IView::GetCenterLineCount()` 的前后回读**（本模块既有 `_sum_over_views` + `_delta`）——
      ★ **不拿它回的 `ICenterLine` 当判据** ✓
    ★★ **「静默无效」那件事怎么定案**：★ 选区计数为 0（前置没备成）时，本函数**在调它之前就报错**；
      ★ 只有**确实选到了实体**、调完仍 **Δ=0**，才是「**选了也没用**」的证据 ⇒ ★ **两者必须分开** ✓
    """
    from sw_connect import get_com_member  # noqa: E402

    out: dict = {
        "ok": False,
        "entry_used": "IDrawingDoc::InsertCenterLine2()",
        "view": None,
        "entity_type": str(entity_type),
        "entity_index": int(entity_index),
        "visible_count": None,
        "selection_count": None,
        "centerline_count_before": None,
        "centerline_count_after": None,
        "centerline_delta": None,
        "returned_is_none": None,
        "error": None,
        "note": None,
        "★": "判据 = **选区计数** + **`IView::GetCenterLineCount()` 的前后回读**；"
        "★ 它回的 `ICenterLine` **不当判据**；★★ 选区 0 与「选了仍 Δ=0」**必须分开**",
    }
    if model is None:
        out["error"] = "model 为 None"
        return out
    et = str(entity_type).strip().lower()
    if et not in VIEW_ENTITY_TYPES:
        out["error"] = "未知的 entity_type %r；合法：%s" % (
            entity_type,
            ", ".join(sorted(VIEW_ENTITY_TYPES)),
        )
        return out
    try:
        views = _iter_views(model)
    except Exception as exc:  # noqa: BLE001
        out["error"] = "取视图失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out
    if not views:
        out["error"] = (
            "这张工程图里一个视图都没有 ⇒ 没有可选的实体（★ 官方语义是在**视图里**选）"
        )
        return out
    if str(view_name or "").strip():
        target, why = _find_view(model, str(view_name).strip())
        if target is None:
            out["error"] = "找不到视图 %r：%s" % (view_name, why)
            return out
    else:
        target = views[0]
    out["view"] = _view_name(target)
    out["centerline_count_before"] = _sum_over_views(model, "GetCenterLineCount")
    try:
        from sw_part import _empty_callout  # noqa: E402
        from sw_connect import create_empty_dispatch_variant  # noqa: E402

        #: ★★ **`LpViewComponent` 传裸 `None` 会 `类型不匹配`**（`com_error` -2147352571
        #: ）——
        #: ★ 这正是**已知事实 33**：「`SelectByID2` / `Select4` 的 `Callout` 参数**必须*
        #: *传
        #: `VARIANT(VT_DISPATCH, None)`；**传 `None` 得到 '类型不匹配'（`0x80028CA0`）**
        #: 」的
        #:   **同一形态**（★ 空 Dispatch 形参不能给 Python `None`）⇒ ★ 本函数用
        #:   `sw_connect.create_empty_dispatch_variant()` ✓
        #: ⚠ 我第一次就是传的 `None` ⇒ 四种实体类型**全部**报"类型不匹配" —— ★ **那看着
        #: 像"读不到"，
        #:     实际是我传错了**（★ 与事实 33 记的坑一模一样）✓
        ents = _as_list(
            get_com_member(
                target,
                "GetVisibleEntities2",
                create_empty_dispatch_variant(),
                int(VIEW_ENTITY_TYPES[et]),
            )
        )
        out["visible_count"] = len(ents)
        if not ents:
            out["error"] = (
                "视图里**没有可见的 %s**（`GetVisibleEntities2` 回 0 个）⇒ ★ 前置不成立，"
                "**不调** `InsertCenterLine2`（★ 那样只会得到静默空结果）" % et
            )
            return out
        if entity_index < 0 or entity_index >= len(ents):
            out["error"] = "entity_index=%d 越界（视图里可见的 %s 共 %d 个）" % (
                entity_index,
                et,
                len(ents),
            )
            return out
        get_com_member(model, "ClearSelection2", True)
        get_com_member(ents[entity_index], "Select4", False, _empty_callout())
        out["selection_count"] = _selection_count(model)
        if out["selection_count"] <= 0:
            out["error"] = (
                "**选中后回读计数为 0** ⇒ 那个实体没被选上（★ 事实 8：不许信 `Select4` 的返回值）"
                "—— ★ 此时**不能**把后续的静默结果当成「能力无效」的证据"
            )
            return out
        cl = get_com_member(model, "InsertCenterLine2")
        out["returned_is_none"] = cl is None
    except Exception as exc:  # noqa: BLE001
        out["error"] = "调用失败：%s: %s" % (type(exc).__name__, str(exc)[:220])
        return out
    try:
        out["centerline_count_after"] = _sum_over_views(model, "GetCenterLineCount")
        out["centerline_delta"] = _numeric_delta(
            out["centerline_count_before"], out["centerline_count_after"]
        )
    except Exception as exc:  # noqa: BLE001
        out["error"] = "后置回读失败：%s" % str(exc)[:150]
        return out
    out["ok"] = bool(out["centerline_delta"] and out["centerline_delta"] > 0)
    if not out["ok"]:
        out["error"] = (
            "回读判据未过：**选中了 %d 个实体**（`%s` #%d）之后，视图中心线数仍 "
            "**%r → %r**（差 %r）· 它回的 `ICenterLine` 是 %s —— "
            "★ 这是「**选了也没用**」的证据（★ 与「选不上」分开记）"
            % (
                out["selection_count"],
                et,
                entity_index,
                out["centerline_count_before"],
                out["centerline_count_after"],
                out["centerline_delta"],
                "None" if out["returned_is_none"] else "非 None",
            )
        )
    return out
