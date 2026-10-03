"""候选 C：A 组 + B 组六条「要求调用方先选」工具的 `pre_call`（点/射线优先，不遍历体）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**候选**；★ 本文件未挂到任何 ToolSpec 上，由 Lead 复核后集成）
# 文件:   specs/202-user-coverage-gaps/recon/precall-cand/precall-cand-C.py
# 定位:   为下面 6 条各写一个可直接粘进 `ToolSpec(pre_call=…)` 的 `_pre_xxx(params)`：
#           A 组 ① `solidworks_mold_parting_line` ② `solidworks_mold_parting_surface`
#                 ③ `solidworks_part_wrap`
#           B 组 ④ `solidworks_part_sweep`       ⑤ `solidworks_part_loft`
#                 ⑥ `solidworks_part_axis`
#         ★★ **本候选的独立第二意见 = 「按点/射线选」优先，而不是「按对象遍历体」**：
#           理由是**官方自己这么推荐**，见下面 `SelectByID2.md` §Remarks 逐字：
#           「If your application has a pointer to the IFace2 object … call IEntity::Select4
#             directly. **Otherwise, you can call IModelDocExtension::SelectByRay.** …
#             IModelDocExtension::SelectByRay is **recorded** when IModelDocExtension::SelectByID2
#             relies on the selection coordinates and **prone to failure if the model view
#             is altered**.」
#           ⇒ ★★ 按点选（`SelectByID2` / `SelectByRay`）**才是官方为「没有对象指针」时指定的
#             那条路**，★ 而遍历 `IBody2.GetFaces()` 拿对象再 `Select4` 是「有指针」时的那条。
#           ⇒ 本文件的选择顺序是 **射线 → 按点 → 按对象**，★ 前两条都**原生带 mark**，
#             ★ 而 `IEntity::Select4` 的第 2 参是 `ISelectData`（见下）——★ **两条路都通 mark**。
# 官方依据（mark 与前置只在这里；逐条给出可 grep 的页与行）:
#   ① `C:\swapi\types\IFeatureManager\InsertMoldPartingLine.md` §Remarks **整段逐字**:
#      「Before calling this method, you must select the direction of pull and the edges for
#        the parting line by calling IModelDocExtension::SelectByID2 with the following Marks:」
#      随后表 **Direction of pull → 1** / **Parting line edges → 4**
#   ② `C:\swapi\types\IFeatureManager\InsertMoldPartingSurface.md` §Remarks 逐字:
#      「…you must first select the direction of pull and the edges for the parting line…
#        For example, **a face (direction of pull) has a mark of 1** and **edges (parting lines)
#        a mark of 4**.」★ 与 ① **完全同形** ⇒ 本文件让两条**共用同一个 `_pre_parting`**。
#   ③ `C:\swapi\types\IFeatureManager\InsertWrapFeature2.md` §Remarks mark 表逐字:
#      「One or more faces on which to place the wrap feature → **1**」/
#      「Pull direction entity if Type is Emboss or Engrave → **2**」/
#      「2D sketch containing no open contours; 3D sketches are not supported → **4**」
#      · 调用序（★★ 最干净的一条）：`C:\swapi\examples\Insert_Wrap_Feature_Example_VB.md` 43–46 行
#        注释与代码**逐字**:「**Mark the sketch to use for wrap feature as 4**」
#        `SelectByID2("Sketch2","SKETCH",0,0,0,True,4,Nothing,swSelectOptionDefault)`；
#        「**Mark the nonplanar face on which to place wrap feature as 1**」
#        `SelectByID2("","FACE",-2.013e-2, 2.480e-2, 5.803e-2,True,1,Nothing,0)`
#        ⇒ ★★ **官方例子自己就是「先草图 mark4、后面 mark1」** ⇒ 与本文件的调用序逐字一致。
#      · 另一个官方例子 `Create_Wrap_Feature_on_Multiple_Faces_Example_VB.md`（多面 + Scribe）
#        53–59 行：**草图 `SelectByID2(...,mark=4)`**，之后 6 条 `SelectByRay(..., 2, True, 1, 0)`
#        —— 末位那个 `1` 是 **Mark**（`SelectByRay.md` 第 10 参逐字「Value to use as a mark;
#        this value is used by other functions that require ordered selection」），
#        而 `TypeWanted=2` 是 **`swSelFACES`**（`C:\swapi\enums\swSelectType_e.md`:
#        「swSelEDGES = 1」/「swSelFACES = 2」/「swSelVERTICES = 3」）⇒ ★★ **官方例子给面用了
#        `SelectByRay` + Mark 1** ⇒ 本文件把射线排在第一位有官方例子背书。
#   ④ `C:\swapi\docs\Programming with the SOLIDWORKS API\Sweep Features and SweepFeatureData
#      Objects.md` 专文 15–51 行**逐字**:「Call **IModelDocExtension::SelectByRay** to select the:
#      1. **Profile** … use **Mark = 1** … 2. **Sweep path** using **Mark = 4** … 3. **Guide curves**
#      using **Mark = 2** … 4. **Direction vector** using **Mark = 128**」
#      · 调用序：`C:\swapi\examples\Select_Multiple_Paths_for_Sweep_Path_Example_VB.md` 57–61 行
#        `SelectByID2("Sketch1","SKETCH",…,False,**1**,Nothing,0)`（轮廓）→
#        `SelectByID2("Line1@Sketch2","EXTSKETCHSEGMENT",…,True,**4**,Nothing,0)`（路径）→
#        `SelectByID2("Line1@Sketch3",…,True,**4**,…)` →
#        ★★ `SelectByID2("Unknown","SELOBJGROUP",0,0,0,True,**4**,Nothing,0)`
#        ⇒ ★ **多段路径必须用 `"Unknown"/"SELOBJGROUP"` 收口**，否则 SolidWorks 不把它们当成一组。
#      · 另一例 `Create_Cut-sweep_Feature_Using_Circular_Profile_Example_VB.md` 44 行
#        `SelectByID2("","EDGE",x,y,z,True,**4**,Nothing,0)` ⇒ ★★ **「按点选边 + mark 4」有官方例子**。
#   ⑤ `C:\swapi\types\IFeatureManager\InsertProtrusionBlend2.md` §Remarks **完整 mark 表逐字**:
#      「1 = profile selections / 2 = guide curve selections / 4 = centerline selection /
#        8 = start tangency vector / 16 = …(not available) / 32 = end tangency vector /
#        64 = …(not available)」★ 并逐字:「**you must select the profiles in an order consistent
#        with the desired direction of the loft**」
#      · 调用序：`C:\swapi\examples\Insert_Protrusion_Blend_Example_VB.md` 75–81 行
#        `SelectByID2("Sketch1","SKETCH",…,False,**1**,Nothing,0)` →
#        `SelectByID2("Sketch2","SKETCH",…,True,**1**,Nothing,0)` → 4 条 `REFERENCECURVES`
#        mark=**4098 / 8194 / 12290 / 16386**（= 2 × 1..4，即「引导线 mark 2」按序号进位）→
#        `SelectByID2("Curve5","REFERENCECURVES",…,True,**4**,Nothing,0)`（中心线）
#   ⑥ `C:\swapi\types\IModelDoc2\InsertAxis2.md` ★★ **该页根本没有 `## Remarks` 段**
#      （只有签名 + Returns + Examples + See Also）⇒ **官方没有给 mark**。
#      · 我**试了什么**：① 读该页全文（无 Remarks）；② 读 `IFeatureManager\` 下有没有
#        `InsertAxis2.md` —— ★ **没有**（入口只在 `IModelDoc2` 上，仓内 batch49 已记）；
#        ③ 读该页 **Examples** 指向的三个例子里唯一给调用序的
#        `C:\swapi\examples\Create_Revolve_Features_Example_VB.md` 29–31 行**逐字**:
#        `SelectByID2("Right Plane","PLANE",0,0,0,True,**0**,Nothing,swSelectOptionDefault)`
#        两次（两次都是 mark **0**）→ 紧接着 `swModel.InsertAxis2 True`
#        ⇒ ★★ **结论：mark 查不到（文档层面）；例子层面用的是 0** ⇒ 本文件取 **0**，
#          ★ 并**明确标注这是「例子推断」而非「文档给定」**（铁律 5：查不到就说查不到）。
#   ★★ **「mark 怎么真正写进去」的三源互证**（本文件的核心底座）:
#      · 源① `C:\swapi\types\IModelDocExtension\SelectByID2.md` 签名第 7 参 `Int32 Mark`
#        + 第 39 行逐字「Value that you want to use as a mark; this value is used by other
#        functions that require ordered selection」★ 且 §Remarks **97/99 行逐字点名两个 mark**:
#        「**Mark of 4** when selecting multiple edges or sketch segments and grouping them into
#          one object for the **path for a sweep feature**」
#        「**Mark of 2** when selecting multiple edges … for the **guide curves for a loft** feature」
#      · 源② `C:\swapi\types\IModelDocExtension\SelectByRay.md` 签名第 10 参 `Int32 Mark`（同上措辞）
#      · 源③ `C:\swapi\types\IEntity\Select4.md` 签名逐字
#        `Select4(System.bool Append, **SelectData** Data)` ★ **第 2 参不是 mark，而是 ISelectData**
#        ⇒ ★★ **`IEntity::Select4` 的 mark 走 `ISelectData::Mark`**（`C:\swapi\types\ISelectData\Mark.md`
#        签名逐字 `System.int Mark {get; set;}`），而 **ISelectData 由官方工厂造**
#        （`C:\swapi\types\ISelectionMgr\CreateSelectData.md` 逐字「Creates a **SelectData** object
#        to use as argument with Select methods」· 签名零参），
#        官方调用序见 `C:\swapi\examples\Select_Loop_of_Edges_Example_VB_.md` 52/34 行逐字:
#        `Set swSelData = swSelMgr.CreateSelectData` … `bRet = swEnt.Select4(True, swSelData)`，
#        以及 `Select_Multiple_Objects_for_Selection_Boxes_Example_VB.md` 88–89 行逐字
#        `Set swSelectData = swSelMgr.CreateSelectData` / `swSelectData.mark = selectionBoxMark`
#        ⇒ ★★★ **「`CreateSelectData()` → 设 `.Mark` → `entity.Select4(append, sd)`」是官方
#        逐字给出的、非废弃的、按对象带 mark 的选法** ⇒ 本文件把它放在**第三条（兜底）**。
#      · ★ **刻意不用** `IEntity.Select2(Append, Mark)`：`C:\swapi\types\IEntity\Select2.md` 第 12 行
#        逐字「**Obsolete. Superseded by IEntity::Select4**」⇒ 取后继，不取废弃成员
#        （⚠ 仓内 `sw_part._select_com_object` **先试的就是 Select2(mark)** —— 见文末「与先例的分歧」）。
#      · ★ **官方也明说 Name 参数不是给面/边用的**（`SelectByID2.md` 第 75 行逐字
#        「**The Name parameter is not intended for selection of faces, edges, and so on**」）
#        ⇒ 本文件**只对「有名字的东西」**（SKETCH / PLANE / AXIS）用按名选，
#        ★ 对面/边/顶点**一律走点/射线/对象**，★ 不犯事实 32 的错。
#   · 仓内 `pre_call` 先例（**形状照抄**，内容不照抄）:
#       `mcp-server/tool_specs_batch23.py::_select_edge`（声明式 `selection` + 回读计数）
#       `mcp-server/tool_specs_batch74.py::_select_faces_for`（按 mark 选 + 回读 + 不够就抛）
#       ★★ batch74 自己的注释里那条**必须遵守的次序纪律**（原文）：
#         「注册器的顺序是 `kwargs[inj]=resolver(params)` → `pre_call(params)` → `fn(**kwargs)`
#           ……而 **`RESOLVERS["model"]` 会经 `connect_solidworks()` 清空选区** ……
#           ⇒ ★★ 于是"指望调用方预选"的工具**经工具层永远拿不到选区**」
#         ⇒ 本文件每个 `pre_call` **自己 `ClearSelection2` 然后把全部 mark 重新选一遍**。
#   · 读过的仓内目标函数（确认**现有形参名**，`pre_call` 只能从 params 取**已声明**字段）:
#       `scripts/sw_mold.py:85  insert_parting_line(model, *, draft_analysis: bool = True)`
#       `scripts/sw_mold.py:114 insert_parting_surface(model, *, surface_type, flip, use_trim,
#                                                      distance, angle, option, tolerance,
#                                                      alternate)`
#       `scripts/sw_wrap.py:69   create_wrap_report(model, wrap_type, thickness_mm, reverse)`
#       `scripts/sw_sweep.py:65  create_sweep_report(model, cut: bool = False)`
#       `scripts/sw_loft.py:64   create_loft_report(model, closed, use_selected_profiles)`
#       `scripts/sw_part.py:1545 create_axis_report(model, reverse: bool = True)`
#       ⇒ ★★ **六条目标函数里没有一个收「选择」类形参** ⇒ ★ **选择只能全部在 `pre_call` 里做完**
#         （这正是本任务存在的原因）。
# 许可:   本仓库 MIT。**无第三方代码引入**（核对时看过 solidpilot-salvage 的写法但**未抄文本**）。
# 覆盖:   全文件
# ⚠ **未在本机实测**（真机由 Lead 独家执行）。凡**没有官方依据**的地方逐条写「未证实」。
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations


# ══════════════════════════════════════════════════════════════════════════════
# 0 · 官方 mark 常量（每个都注明出处，别再散落字面量）
# ══════════════════════════════════════════════════════════════════════════════
#: 拔模/拉动方向 —— InsertMoldPartingLine.md §Remarks 表「Direction of pull」行
PULL_MARK = 1
#: 分型线边 —— InsertMoldPartingLine.md §Remarks 表「Parting line edges」行
PARTING_EDGE_MARK = 4
#: 包覆面 —— InsertWrapFeature2.md §Remarks「One or more faces on which to place the wrap feature」
WRAP_FACE_MARK = 1
#: 包覆拔模方向 —— InsertWrapFeature2.md §Remarks「Pull direction entity if Type is Emboss/Engrave」
WRAP_PULLDIR_MARK = 2
#: 包覆草图 —— InsertWrapFeature2.md §Remarks「2D sketch … 3D sketches are not supported」
WRAP_SKETCH_MARK = 4
#: 扫描轮廓 —— Sweep Features and SweepFeatureData Objects.md 专文「Profile … Mark = 1」
SWEEP_PROFILE_MARK = 1
#: 扫描路径 —— 同上专文「Sweep path using Mark = 4」+ SelectByID2.md §Remarks 第 97 行点名
SWEEP_PATH_MARK = 4
#: 扫描引导线 —— 同上专文「Guide curves using Mark = 2」+ SelectByID2.md §Remarks 第 99 行点名
SWEEP_GUIDE_MARK = 2
#: 扫描方向向量 —— 同上专文「Direction vector using Mark = 128」
SWEEP_DIRVEC_MARK = 128
#: 放样轮廓 —— InsertProtrusionBlend2.md §Remarks「1 = profile selections」
LOFT_PROFILE_MARK = 1
#: 放样引导线 —— InsertProtrusionBlend2.md §Remarks「2 = guide curve selections」
LOFT_GUIDE_MARK = 2
#: 放样中心线 —— InsertProtrusionBlend2.md §Remarks「4 = centerline selection」
LOFT_CENTERLINE_MARK = 4
#: 参考轴 —— ★★ **未证实**：`InsertAxis2.md` **没有 Remarks 段**；
#:   `Create_Revolve_Features_Example_VB.md` 29–30 行两次都用 **0** ⇒ 取 0，★ **例子推断值**。
AXIS_MARK = 0

#: `SelectByRay` 的 `TypeWanted` —— `C:\swapi\enums\swSelectType_e.md` §IDs 逐字
#: 「swSelEDGES = 1」/「swSelFACES = 2」/「swSelVERTICES = 3」
TYPE_WANTED = {"EDGE": 1, "FACE": 2, "VERTEX": 3}
#: `SelectByID2` 的 `Type` 字符串 —— 同页逐字 "EDGE" / "FACE" / "VERTEX"
TYPE_STR = {"EDGE": "EDGE", "FACE": "FACE", "VERTEX": "VERTEX"}

#: 射线方向逐个试（官方 `SelectByRay` 要射线真的穿过实体；官方例子里向量是 `(1,0,0)`）
RAY_DIRECTIONS = ((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0),
                  (0.0, 1.0, 0.0), (0.0, -1.0, 0.0),
                  (0.0, 0.0, 1.0), (0.0, 0.0, -1.0))

#: ★ 射线半径（米）。官方例子用 `4.21383417784414E-04`（0.42 mm）；
#: ★ `SelectByRay.md` §Remarks 逐字「RayRadius ≤ 2.9 m」且
#: ★「**If selecting faces**, then the RayRadius parameter is **ignored**」⇒ 面不受它影响。
DEFAULT_RAY_RADIUS_M = 4.21383417784414e-4

#: 声明式「面选择器」的合法键 —— ★ **刻意与仓内 `sw_simulation.FACE_SELECTORS` 同一套**，
#: ★ 而那个集合已经由 `solidworks_select_face_selector` 这个工具对外暴露 ⇒ 不另立一套词汇。
FACE_DIRECTIONS = ("+x", "-x", "+y", "-y", "+z", "-z")

#: `__current_selection__`（仓内 `sw_selection_spec.CURRENT_SELECTION` 的同一约定）
CURRENT = "__current_selection__"


class PreCallError(RuntimeError):
    """`pre_call` 的前置未成立。★ 抛出去让 MCP 层看见，**不静默继续**（本项目一贯纪律）。"""


# ══════════════════════════════════════════════════════════════════════════════
# 1 · 共用底座
# ══════════════════════════════════════════════════════════════════════════════
def _model():
    """取**活动文档** —— ★ 优先走 `register_capabilities.RESOLVERS["model"]`，与注册器取**同一个对象**。

    ★★ **为什么必须这样**（`tool_specs_batch74.py` 注释里的实测结论，证据
    `output/selection-lifetime-evidence.json`）：★ `RESOLVERS["model"]` 会经
    `connect_solidworks()` **清空选区** ⇒ ★★ 任何 `pre_call` 都**不能**指望「进来之前有人选好了」。
    """
    try:
        import register_capabilities as _rc

        model = _rc.RESOLVERS["model"](None)
        if model is not None:
            return model
    except Exception:  # noqa: BLE001 —— 直调路径（探针 / 测试）走不通时退到 connect_solidworks
        pass
    from scripts.sw_connect import connect_solidworks

    _sw, model, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    if model is None:
        raise PreCallError("没有活动文档 —— 请先打开一个零件再调本工具")
    return model


def _callout():
    """空 Dispatch 作 `Callout`（★ 事实 12/33：传 `None` 会得「类型不匹配」）。"""
    from scripts.sw_part import _empty_callout

    return _empty_callout()


def _get(obj, member, *args):
    """薄封装 `sw_connect.get_com_member`，顺便把「读不到」这件事变成异常而不是 `None`。"""
    from scripts.sw_connect import get_com_member

    return get_com_member(obj, member, *args)


def _sel_mgr(model):
    return _get(model, "SelectionManager")


def _count_by_mark(model, mark) -> int:
    """**按 mark 回读**选区计数（`ISelectionMgr::GetSelectedObjectCount2(Mark)`）。

    ★★ 铁律（事实 8）：★ `SelectByID2` / `SelectByRay` / `Select4` 的 **bool 返回值不可信**
    （实测 12 次全 false 而计数 = 12）⇒ ★★ **判据永远是这个回读数**。
    """
    return int(_get(_sel_mgr(model), "GetSelectedObjectCount2", int(mark)) or 0)


def _clear(model) -> None:
    """清空选区（★ 六个 `pre_call` 都先调它，避免上一次残留的 mark 干扰计数回读）。"""
    try:
        _get(model, "ClearSelection2", True)
    except Exception:  # noqa: BLE001 —— 清不掉不算致命，后面的回读会自己把问题暴露出来
        pass


def _split(selector):
    """把 `"index:1,index:5"` 拆成 `["index:1", "index:5"]`；单个原样返回。"""
    return [s.strip() for s in str(selector or "").split(",") if s.strip()]


def _body_box_point(model, direction):
    """体 0 的**轴对齐包围盒**上「`direction` 那一面」的中心点（**米**）。

    ★ 刻意**复用仓内** `sw_simulation.resolve_face_selector`（它已经实现了这一层，且已经由
      `solidworks_select_face_selector` 对外暴露）⇒ ★ 不另立一套，也不重算一遍公式。
    ⚠ 官方 `IFace2.GetBox.md` §Remarks 逐字:「The values returned are **approximate** and should
      not be used for comparison or calculation purposes」⇒ ★ 对**非轴对齐/曲面**零件，
      这个点未必落在面上 ⇒ ★ 必须有回退（本文件的射线→按点→按对象三级回退就是为此）。
    """
    key = str(direction or "").strip().lower()
    if key not in FACE_DIRECTIONS:
        return None
    try:
        from scripts.sw_simulation import resolve_face_selector

        pt = resolve_face_selector(model, key)
        return tuple(float(v) for v in pt) if pt else None
    except Exception:  # noqa: BLE001 —— 直算兜底（与 resolve_face_selector 同公式）
        pass
    bodies = _get(model, "GetBodies2", 0, True)          # 0 = swSolidBody
    if not bodies:
        return None
    box = _get(bodies[0], "GetBodyBox")
    if not box or len(box) < 6:
        return None
    x1, y1, z1, x2, y2, z2 = (float(box[i]) for i in range(6))
    xmin, ymin, zmin = min(x1, x2), min(y1, y2), min(z1, z2)
    xmax, ymax, zmax = max(x1, x2), max(y1, y2), max(z1, z2)
    mid = {
        "+x": (xmax, (ymin + ymax) / 2.0, (zmin + zmax) / 2.0),
        "-x": (xmin, (ymin + ymax) / 2.0, (zmin + zmax) / 2.0),
        "+y": ((xmin + xmax) / 2.0, ymax, (zmin + zmax) / 2.0),
        "-y": ((xmin + xmax) / 2.0, ymin, (zmin + zmax) / 2.0),
        "+z": ((xmin + xmax) / 2.0, (ymin + ymax) / 2.0, zmax),
        "-z": ((xmin + xmax) / 2.0, (ymin + ymax) / 2.0, zmin),
    }
    return mid[key]


def _entity_point(model, selector, kind, body_index=0):
    """把 `index:<n>` 解析成**那个实体自己身上的一点**（**米**）。

    ★★ 本文件的核心手法：**不让调用方给坐标**（规则 3），★ 而是**从实体几何里读出一个点**，
      ★ 再拿这个点去做射线/按点选 ⇒ ★ 对外仍然只有**声明式选择器**。
    取点用**官方零参、返回数组**的成员（pywin32 下最稳的一种形状）:
      · `IVertex.GetPoint()` → 「Array of three doubles」
      · `IEdge.GetStartVertex()` → Vertex（★ §Remarks 逐字:「If no vertex exists for this edge
        (such as the edge of a newly created cylinder), then this method returns **null**」⇒ 退回
        `GetEndVertex()`）
      · `IFace2.GetBox()` → 「an array of 6 doubles」（★ 取 min/max 两对角的中点）
    """
    from scripts.sw_selection_spec import entities_on_body

    s = str(selector or "").strip()
    if not s.lower().startswith("index:"):
        return None
    try:
        idx = int(s.split(":", 1)[1])
    except ValueError:
        raise PreCallError("非法的 index 选择器 %r（应为 index:<整数>）" % selector)
    items = entities_on_body(model, kind, body_index=body_index)
    if idx < 0 or idx >= len(items):
        raise PreCallError("%s 序号 %d 越界（体 %d 上共 %d 个）"
                           % (kind, idx, body_index, len(items)))
    obj = items[idx]
    k = kind.upper()
    if k == "VERTEX":
        pt = _get(obj, "GetPoint")
    elif k == "EDGE":
        vtx = _get(obj, "GetStartVertex")
        if vtx is None:
            vtx = _get(obj, "GetEndVertex")
        if vtx is None:
            return None                      # ★ 官方明说这种情况会返回 null（圆柱的边）
        pt = _get(vtx, "GetPoint")
    else:                                    # FACE
        box = _get(obj, "GetBox")
        if not box or len(box) < 6:
            return None
        a = [float(v) for v in box[:6]]
        pt = ((min(a[0], a[3]) + max(a[0], a[3])) / 2.0,
              (min(a[1], a[4]) + max(a[1], a[4])) / 2.0,
              (min(a[2], a[5]) + max(a[2], a[5])) / 2.0)
    if pt is None:
        return None
    vals = tuple(float(v) for v in list(pt)[:3])
    return vals if len(vals) == 3 else None


def _select_named(model, name, type_str, mark, append):
    """**按名字**选**有名字的东西**（`SKETCH` / `PLANE` / `AXIS`）——带 mark。

    ★ 合法性的官方依据（`SelectByID2.md` 第 75 行逐字）:
      「**The Name parameter is not intended for selection of faces, edges, and so on.**」
      ⇒ ★ 名字**只**用于特征类（草图/基准面/基准轴），★ 面/边/顶点**绝不走这条**（事实 32）。
    ★ 第 83 行逐字还给了「按名字选**可以**把 x,y,z 传 (0,0,0)」⇒ ★ 这里就传 0。
    ★ 调用序范例 = 官方 `Insert_Wrap_Feature_Example_VB.md` 第 44 行（草图 mark 4）。
    """
    ext = _get(model, "Extension")
    _get(ext, "SelectByID2", str(name), str(type_str), 0.0, 0.0, 0.0,
         bool(append), int(mark), _callout(), 0)
    return _count_by_mark(model, mark)


def _select_by_ray(model, point, kind, mark, append, want_at_least,
                   radius_m=DEFAULT_RAY_RADIUS_M):
    """`IModelDocExtension::SelectByRay(WorldX/Y/Z, RayVecX/Y/Z, RayRadius,
    **TypeWanted**, Append, **Mark**, Option)` —— ★ **官方点名推荐的选法**。

    ★ 依据（`SelectByID2.md` §Remarks 逐字）:「**Otherwise, you can call
      IModelDocExtension::SelectByRay.** … SelectByRay is recorded when SelectByID2 relies on
      the selection coordinates and **prone to failure if the model view is altered**.」
    ★ 依据（扫描专文逐字）:「**Call IModelDocExtension::SelectByRay** to select the: Profile…
      Sweep path… Guide curves… Direction vector…」⇒ ★ 扫描那条官方**直接点名**用射线。
    ★ 依据（包覆官方例子）: 6 条 `SelectByRay(..., 2, True, 1, 0)` 给面用 **Mark=1**。

    ⚠⚠ **官方文档里的一条陷阱**（`SelectByID2.md` 第 26–32 行 `Append` 语义表逐字）:
      「True / **Already selected** / Entity is **removed** from the current selection list」
      ⇒ ★★ **`append=True` 打偏到「已选中的实体」会把它**反选掉**⇒ ★ 所以本函数
      **每试一次都回读 `want_at_least` 并逐个换方向**，★ 靠回读发现反选（事实 8 的纪律）。
    ★ 返回是否达到了 `want_at_least`；方向试完仍不足就返回 False（**由调用方决定要不要抛**）。
    """
    ext = _get(model, "Extension")
    tw = int(TYPE_WANTED[kind.upper()])
    x, y, z = float(point[0]), float(point[1]), float(point[2])
    for dx, dy, dz in RAY_DIRECTIONS:
        if _count_by_mark(model, mark) >= int(want_at_least):
            return True                      # ★ 已经够了就别再打（★ 免得触发上面的「反选」）
        _get(ext, "SelectByRay", x, y, z,
             float(dx), float(dy), float(dz), float(radius_m),
             tw, bool(append), int(mark), 0)
    return _count_by_mark(model, mark) >= int(want_at_least)


def _select_by_point(model, point, kind, mark, append, want_at_least):
    """`SelectByID2("", "<FACE|EDGE|VERTEX>", x, y, z, Append, **Mark**, Callout, Option)`。

    ★ 官方例子（逐字）: `Create_Cut-sweep_Feature_Using_Circular_Profile_Example_VB.md` 第 44 行
      `SelectByID2("", "EDGE", -3.7298e-2, 3.9390e-2, 4.9504e-2, True, **4**, Nothing, 0)`
      ⇒ ★★ **「按点选边 + mark 4」是官方逐字用法**。
    ★ 官方例子（逐字）: `Insert_Wrap_Feature_Example_VB.md` 第 46 行
      `SelectByID2("", "FACE", -2.013e-2, 2.480e-2, 5.803e-2, True, **1**, Nothing, 0)`
    ★ 本仓实测（`sw_selection_spec.select_face_at` 的来源块）: 给原点选不中任何面
      （计数 0）、给面上一点计数 1 ⇒ ★ **点必须真的在面上**。
    ⚠ `SelectByID2.md` 第 93 行逐字警告:「if the view changes from the original recorded size
      or orientation, then **the same IFace2 might not be selected next time**」
      ⇒ ★★ **这就是本文件把 `SelectByRay` 排在它前面**的理由（★ 也提醒真机复测要转视角）。
    """
    ext = _get(model, "Extension")
    _get(ext, "SelectByID2", "", TYPE_STR[kind.upper()],
         float(point[0]), float(point[1]), float(point[2]),
         bool(append), int(mark), _callout(), 0)
    return _count_by_mark(model, mark) >= int(want_at_least)


def _select_by_object(model, obj, mark, append):
    """`ISelectionMgr::CreateSelectData()` → 设 `.Mark` → `entity.Select4(Append, sd)`。

    ★★★ 这是**官方逐字给出的、按对象带 mark 的非废弃选法**:
      · `C:\swapi\types\ISelectionMgr\CreateSelectData.md` §Description 逐字
        「Creates a **SelectData** object to use as argument with Select methods.」（零参）
      · `C:\swapi\types\ISelectData\Mark.md` 签名逐字 `System.int Mark {get; set;}`
      · `C:\swapi\types\IEntity\Select4.md` 签名逐字 `Select4(System.bool Append, SelectData Data)`
      · 调用序逐字（`Select_Loop_of_Edges_Example_VB_.md`）:
        `Set swSelData = swSelMgr.CreateSelectData` → `bRet = swEnt.Select4(True, swSelData)`
      · 调用序逐字（`Select_Multiple_Objects_for_Selection_Boxes_Example_VB.md`）:
        `Set swSelectData = swSelMgr.CreateSelectData` → `swSelectData.mark = selectionBoxMark`
      · `C:\swapi\types\IFeatureManager\FeatureLinearPattern5.md` §Remarks 逐字也点名这条路:
        「IEntity::Select4 with ISelectData::Mark=1 to mark Direction 1」
    ⚠⚠ **本条标「未在本机实测」**：★ `CreateSelectData()` 在 **pywin32 迟到绑定**下能否拿到
      并把 `.Mark` 写进去，★ **本仓从未验证过**（事实 47 那一族的后端限制就在隔壁）。
      ★ 所以它只是**第三条兜底**，★ 前两条（射线/按点）不依赖它。
    """
    sm = _sel_mgr(model)
    try:
        sd = _get(sm, "CreateSelectData")
        if sd is not None:
            _get(sd, "Mark", int(mark))
            _get(obj, "Select4", bool(append), sd)
            return True
    except Exception:  # noqa: BLE001 —— 拿不到 SelectData 就退到下一条
        pass
    try:
        return bool(_get(obj, "Select2", bool(append), int(mark)))
    except Exception:  # noqa: BLE001
        return False
    # ⚠ 上面那一行走的是 `IEntity::Select2` —— ★ 官方标 **Obsolete**（`IEntity\Select2.md`
    #   第 12 行逐字「Obsolete. Superseded by IEntity::Select4」），★ 且它的 `Mark` 形参
    #   官方页面写的是「**No description**」⇒ ★★ **「Select2 的 mark 到底算不算数」= 未证实**。
    #   ★ 只作为最后的、几乎不可能被走到的一档，★ 且**上方注释如实标出**（铁律 5）。
    return False


def _resolve_object(model, selector, kind, body_index=0):
    """把 `index:<n>` / `__current_selection__` 解析成**实体对象**（走仓内已实测那条路）。"""
    from scripts.sw_selection_spec import resolve_entity

    return resolve_entity(model, selector, kind, body_index=body_index)


def _select_marked(model, selector, kind, mark, *, append=False, body_index=0,
                   min_count=1, label="项"):
    """★★ **本文件的通用选法**：把一个声明式选择器变成**带 `mark` 的选中**，并**回读计数**。

    三级顺序（每级都回读 `GetSelectedObjectCount2(mark)`；★ 判据永远是回读数 —— 事实 8）:
      1. **`SelectByRay`**（★ 官方点名推荐；★ 扫描专文与包覆官方例子都直接用它）
      2. **`SelectByID2` 按点**（★ 官方 cut-sweep / wrap 例子逐字用的就是它）
      3. **`CreateSelectData` + `Select4`**（★ 官方逐字的「有对象指针」那条路）

    支持的选择器语法（★ **全部声明式，没有裸坐标** —— 规则 3）:
      * `"+x"/"-x"/"+y"/"-y"/"+z"/"-z"` → 体 0 包围盒那一面的中心点
      * `"index:<n>"`                → 体 `body_index` 上第 n 个 `kind` 实体的**它自己的几何点**
      * `"__current_selection__"`     → 直接用选区里的对象（走第 3 级）
    """
    k = str(kind).upper()
    already = _count_by_mark(model, mark) if append else 0
    want = max(int(min_count), already + (0 if already else 1))
    if append:
        want = max(int(min_count), already + 1) - 1 + 1   # = max(min_count, already+1)
    tried = []

    def _enough():
        return _count_by_mark(model, mark) >= max(int(min_count), already)

    # ── 0 · 先清一次（避免上一次残留的同 mark 项把 want_at_least 骗过去）──────────
    if not append:
        _clear(model)
        want = max(int(min_count), 1)

    # ── 1 · `__current_selection__` —— 没有点可用，只能走对象那条 ────────────────
    s = str(selector or "").strip()
    if s == CURRENT:
        try:
            obj = _resolve_object(model, CURRENT, k, body_index=body_index)
            _select_by_object(model, obj, mark, append=_count_by_mark(model, -1) > 0)
        except Exception as exc:  # noqa: BLE001
            raise PreCallError("★ %s：选择器是 %r 但当前**没有任何选中项** —— %s"
                               % (label, CURRENT, exc))
        if not _enough():
            raise PreCallError("★ %s：用当前选中项打 mark=%d 后回读计数为 %d（要 ≥%d）"
                               % (label, mark, _count_by_mark(model, mark), min_count))
        return _count_by_mark(model, mark)

    # ── 2 · 射线 → 按点（都要点；点从选择器里算，★ 不接受调用方给坐标）────────────
    point = None
    if s.lower() in FACE_DIRECTIONS:
        point = _body_box_point(model, s)
    elif s.lower().startswith("index:"):
        point = _entity_point(model, s, k, body_index=body_index)
    if point is None:
        raise PreCallError(
            "★ %s：选择器 %r 解析不出「实体自己身上的一点」—— "
            "① 文档里没有该实体（体 %d 上没有 %s）；② 官方明说 %s::GetStartVertex "
            "对「新生成的圆柱的边」会返回 null；③ 面用近似包围盒取心点，曲面件可能取偏。"
            % (label, s, body_index, k, "IEdge"))

    if _select_by_ray(model, point, k, mark, append, want_at_least=want):
        tried.append("SelectByRay(mark=%d)=%d" % (mark, _count_by_mark(model, mark)))
        return _count_by_mark(model, mark)
    tried.append("SelectByRay(mark=%d)→%d" % (mark, _count_by_mark(model, mark)))

    if _select_by_point(model, point, k, mark, append, want_at_least=want):
        tried.append("SelectByID2(point,mark=%d)=%d" % (mark, _count_by_mark(model, mark)))
        return _count_by_mark(model, mark)
    tried.append("SelectByID2(point,mark=%d)→%d" % (mark, _count_by_mark(model, mark)))

    # ── 3 · 对象那条（`index:` / `FACE_SELECTORS` 都能拿到对象时才有意义）──────────
    if s.lower().startswith("index:"):
        try:
            obj = _resolve_object(model, s, k, body_index=body_index)
            _select_by_object(model, obj, mark, append=append)
        except Exception:  # noqa: BLE001
            pass
        if _enough():
            tried.append("Select4(ISelectData.Mark=%d)=%d"
                         % (mark, _count_by_mark(model, mark)))
            return _count_by_mark(model, mark)
        tried.append("Select4(ISelectData.Mark=%d)→%d" % (mark, _count_by_mark(model, mark)))

    raise PreCallError(
        "★ 前置未成立：%s 没能打上 mark=%d（官方要求 ≥%d 个）。试过：%s。"
        "★ 选不中就报错，不静默把前置未成立当成能力不成。"
        % (label, mark, min_count, " · ".join(tried)))


# ══════════════════════════════════════════════════════════════════════════════
# 2 · A 组
# ══════════════════════════════════════════════════════════════════════════════
def _pre_parting(params):
    """★★ **分型线 / 分型面共用的 `pre_call`**（两条工具官方形态完全相同 ⇒ 共用一份实现）。

    官方依据（两条**逐字**同形，所以共用）:
      · `IFeatureManager\InsertMoldPartingLine.md` §Remarks:
        「Before calling this method, you must select the direction of pull and the edges for
          the parting line by calling IModelDocExtension::SelectByID2 with the following Marks:」
        表 → **Direction of pull = 1** · **Parting line edges = 4**
      · `IFeatureManager\InsertMoldPartingSurface.md` §Remarks:
        「…**a face (direction of pull) has a mark of 1** and **edges (parting lines) a mark
          of 4**.」★ 并带条件「**If a parting line feature does not yet exist in the model**」。

    调用序：**先拔模/拉动方向（mark 1）· 再分型线边（mark 4）** —— ★ 与官方段落的行序一致。

    ⚠⚠ **未证实（三条，如实写明）**:
      · ① **官方没有「创建分型线」的完整例子**。我查过的 `Get_and_Set_Parting_Line_Feature_Data_
        Example_VB.md` 是**改**已有分型线（`AccessSelections` + `ModifyDefinition`），
        ★ **不构成创建时的调用序** ⇒ ★ 本文件的「先 1 后 4」只依据 Remarks 的**行序**。
      · ② Remarks 说「Direction of pull」但**没限定它必须是一个面**；分型面那条才逐字写
        「a **face** (direction of pull) has a mark of 1」⇒ ★ 基准面/轴能不能当拔模方向
        **未证实**（⇒ 选择器留了 `plane:` / `axis:` 两条路，但**默认只走面**）。
      · ③ 两条工具在**本仓都没有真机通过记录**（`scripts/sw_mold.py` 的两个函数只回 Feature 名，
        仓内 `output/` 里没有 parting-evidence）⇒ ★ 置信度只给到「中」。
    """
    model = _model()
    _clear(model)

    pull = str(getattr(params, "pull_direction", "") or "").strip()
    edges = str(getattr(params, "parting_line_edges", "") or "").strip()

    # ── 拔模/拉动方向（mark 1）────────────────────────────────────────────────
    if pull.lower().startswith("plane:") or pull.lower().startswith("axis:"):
        kind, _, name = pull.partition(":")
        type_str = "PLANE" if kind.lower() == "plane" else "AXIS"
        n = _select_named(model, name, type_str, PULL_MARK, append=False)
        if n < 1:
            raise PreCallError("★ 拔模方向：按名字选 %s %r 打 mark=%d 后回读计数为 0"
                               % (type_str, name, PULL_MARK))
    elif pull.lower().startswith("sketch:"):
        raise PreCallError("★ 拔模方向不该是草图（官方说的是 direction of pull）—— 收到 %r" % pull)
    elif pull:
        _select_marked(model, pull, "FACE", PULL_MARK, append=False, min_count=1,
                       label="拔模/拉动方向")

    # ── 分型线边（mark 4）· 可多条，★ 逗号分隔即「一组边」────────────────────────
    if edges:
        want = max(1, len(_split(edges)))
        picked = 0
        for i, one in enumerate(_split(edges)):
            picked = _select_marked(model, one, "EDGE", PARTING_EDGE_MARK,
                                    append=(i > 0), min_count=1 + i,
                                    label="分型线边 #%d" % (i + 1))
        got = _count_by_mark(model, PARTING_EDGE_MARK)
        if got < want:
            raise PreCallError("★ 分型线边：打上 mark=%d 的只有 %d 条（要 %d）"
                               % (PARTING_EDGE_MARK, got, want))
        del picked
    return {"pull_mark": _count_by_mark(model, PULL_MARK),
            "parting_edge_mark": _count_by_mark(model, PARTING_EDGE_MARK)}


def _pre_mold_parting_line(params):
    """`solidworks_mold_parting_line` 的 `pre_call` —— ★ 直接就是 `_pre_parting`。"""
    return _pre_parting(params)


def _pre_mold_parting_surface(params):
    """`solidworks_mold_parting_surface` 的 `pre_call` —— ★ 直接就是 `_pre_parting`。

    ★ 官方给了**条件**：「**If** a parting line feature **does not yet exist** in the model,
    you must **first** select …」⇒ ★ **模型里已经有分型线特征时，这两步选区是多余的**。
      ⇒ 集成时建议：**目标函数前先判断**（`FeatureByName` 找「分型线」特征），
      ★ 找得到就**跳过**本 `pre_call`（省一次多余的选区，也避免"多选反而干扰"）。
    """
    return _pre_parting(params)


def _pre_part_wrap(params):
    """`solidworks_part_wrap` 的 `pre_call` —— ★ **草图 mark 4 + 面 mark 1，两个都要选**。

    官方依据（★★ 本批 mark 证据最齐的一条：Remarks + **两个**官方例子）:
      · `IFeatureManager\InsertWrapFeature2.md` §Remarks: 面 → **1** · 拔模方向 → **2** ·
        草图 → **4**（且逐字「**3D sketches are not supported**」）
      · `Insert_Wrap_Feature_Example_VB.md` 43–46 行**逐字**:
        「**Mark the sketch to use for wrap feature as 4**」→ `SelectByID2("Sketch2","SKETCH",0,0,0,
        True,4,Nothing,swSelectOptionDefault)`；
        「**Mark the nonplanar face … as 1**」→ `SelectByID2("","FACE",…,True,1,Nothing,0)`
      · `Create_Wrap_Feature_on_Multiple_Faces_Example_VB.md` 53–59 行: 草图 mark 4 之后
        **6 条 `SelectByRay(..., TypeWanted=2, Append=True, Mark=1, Option=0)`**（多面）

    ★ 调用序与 `append`：**第一条 `Append=False`（它会清选区）、之后 `Append=True`**。
      ⚠ 官方那个例子把**第一条也写成 `Append=True`**（选区当时是空的）—— ★ 与
      `SelectByID2.md` §Parameters 第 26–32 行的 `Append` 语义表**不完全一致**；
      ★ 本文件按**语义表**写（首条 False），★ 并在此如实标出这处差异。
    ★ 拔模方向（mark 2）**只在 `wrap_type` 是 emboss/engrave 时**才需要
      （官方逐字「Pull direction entity **if Type is**: Emboss or Engrave」）⇒ 默认**不选**。
    """
    model = _model()
    _clear(model)

    sketch = str(getattr(params, "sketch", "") or "").strip()
    face = str(getattr(params, "face", "") or "").strip()
    pull_dir = str(getattr(params, "pull_direction", "") or "").strip()

    # ── ① 草图（mark 4）· ★ 有名字 ⇒ 走「按名字选」（官方逐字那条）──────────────
    if sketch.lower().startswith("sketch:"):
        name = sketch.split(":", 1)[1].strip()
    else:
        name = sketch
    if not name:
        raise PreCallError("★ 包覆必须给 `sketch`（官方 mark=4 的那一条：★ **2D** 草图，"
                           "官方原话「3D sketches are not supported」）")
    got = _select_named(model, name, "SKETCH", WRAP_SKETCH_MARK, append=False)
    if got < 1:
        raise PreCallError("★ 草图：SelectByID2(%r,\"SKETCH\",…,mark=4) 回读计数为 %d"
                           "★ ⇒ 草图名不对（中文 UI 是「草图1」，不是 \"Sketch1\" —— 事实 9）"
                           % (name, got))

    # ── ② 面（mark 1）· 可多条（官方：「One or more faces」）─────────────────────
    faces = _split(face)
    if not faces:
        raise PreCallError("★ 包覆必须给 `face`（官方 mark=1 的那一条）")
    for i, one in enumerate(faces):
        _select_marked(model, one, "FACE", WRAP_FACE_MARK, append=(i > 0),
                       min_count=i + 1, label="包覆面 #%d" % (i + 1))

    # ── ③ 拔模方向（mark 2）· ★ 只在 emboss / engrave 时才要 ────────────────────
    wrap_type = str(getattr(params, "wrap_type", "emboss") or "emboss").strip().lower()
    if pull_dir:
        _select_marked(model, pull_dir, "FACE", WRAP_PULLDIR_MARK, append=True,
                       min_count=1, label="包覆拔模方向")
    elif wrap_type in ("emboss", "deboss"):
        # ★ **不抛**：官方只说"可选/与 Type 有关"，★ 而仓内真机（轮 330/331）已在真机跑通过
        # emboss —— ★ 说明**这一台机器上缺 mark 2 也能成** ⇒ 只在返回值里如实记一笔。
        return {"sketch_mark": _count_by_mark(model, WRAP_SKETCH_MARK),
                "face_mark": _count_by_mark(model, WRAP_FACE_MARK),
                "pull_dir_mark": 0,
                "⚠": "wrap_type=%s 且没给 pull_direction ⇒ 未打 mark=2（官方把它列为 Emboss/"
                      "Engrave 的可选项；★ 仓内真机在缺它的情况下也建成了 Emboss）" % wrap_type}
    return {"sketch_mark": _count_by_mark(model, WRAP_SKETCH_MARK),
            "face_mark": _count_by_mark(model, WRAP_FACE_MARK),
            "pull_dir_mark": _count_by_mark(model, WRAP_PULLDIR_MARK)}


# ══════════════════════════════════════════════════════════════════════════════
# 3 · B 组（四条同型：都是「按官方 mark 把几样东西选上」）
# ══════════════════════════════════════════════════════════════════════════════
def _pre_part_sweep(params):
    """`solidworks_part_sweep` 的 `pre_call` —— ★ 轮廓 1 · 路径 4 · 引导线 2（· 方向向量 128）。

    官方依据（★★ 本批最齐的一条，**专文 + 例子 + `SelectByID2` §Remarks 三处点名同一组 mark**）:
      · `C:\swapi\docs\Programming with the SOLIDWORKS API\Sweep Features and SweepFeatureData
        Objects.md` 15–51 行逐字:「Call **IModelDocExtension::SelectByRay** to select the:
        1. **Profile** … **Mark = 1** 2. **Sweep path** using **Mark = 4** 3. **Guide curves**
        using **Mark = 2** 4. **Direction vector** using **Mark = 128**」
        ⇒ ★★ **官方对扫描直接点名 `SelectByRay`** ⇒ 本文件射线排第一有官方背书。
      · `SelectByID2.md` §Remarks 第 97 行逐字:「**Mark of 4** when selecting multiple edges or
        sketch segments and grouping them into one object for the **path for a sweep feature**」
      · 调用序（`Select_Multiple_Paths_for_Sweep_Path_Example_VB.md` 57–61 行）:
        轮廓 `SelectByID2("Sketch1","SKETCH",…,False,**1**,…)` → 路径两条 EXTSKETCHSEGMENT
        **mark=4** → ★★ `SelectByID2("Unknown","SELOBJGROUP",0,0,0,True,**4**,Nothing,0)`
        ⇒ ★ **多段路径要用 `"Unknown"/"SELOBJGROUP"` 收口**（官方逐字）。

    ⚠⚠ **「组」的收口**是本工具唯一一处 `_select_marked` 覆盖不到的地方:
      ★ `"SELOBJGROUP"` 那个 `Unknown` 实体**不在体上**、★ 也不在选区计数里（它是个虚拟对象）
      ⇒ ★ 本文件**如实不实现**这一步，★ 只在这里写明「要支持多段路径必须补这一步，
      ★ 且它的效果**未在本机实测**」。
    ⚠⚠ **本条有一条 `pre_call` 修不了的前置**（★ 必须让 Lead 知道）:
      `scripts/sw_sweep.py` 顶部记着 2026-10-03（轮 488）的 A/B 实测 ——
      `CreateDefinition(17)` 之后 `AccessSelections` 回 **`0x80010105`**（事实 47 的后端限制）
      ⇒ ★★ **选区补齐了也未必能建成扫描**。★ 本 `pre_call` 只保证"前置的 mark 到位"，
      ★ **不能**保证特征建成 ⇒ ★ 置信度只给到「高（选区）/ 中（端到端）」。
    """
    model = _model()
    _clear(model)

    profile = str(getattr(params, "profile", "") or "").strip()
    path = str(getattr(params, "path", "") or "").strip()
    guides = str(getattr(params, "guide_curves", "") or "").strip()
    dirvec = str(getattr(params, "direction_vector", "") or "").strip()

    # ── ① 轮廓（mark 1）· ★ 官方说可以是草图/面/边/曲线 ──────────────────────────
    if profile.lower().startswith("sketch:"):
        n = _select_named(model, profile.split(":", 1)[1].strip(), "SKETCH",
                          SWEEP_PROFILE_MARK, append=False)
        if n < 1:
            raise PreCallError("★ 扫描轮廓草图打 mark=%d 后回读计数为 0" % SWEEP_PROFILE_MARK)
    else:
        _select_marked(model, profile, "FACE", SWEEP_PROFILE_MARK, append=False,
                       min_count=1, label="扫描轮廓")

    # ── ② 路径（mark 4）· ★ 可多段，★ 但多段要官方那步 SELOBJGROUP 收口（见上）────
    if path.lower().startswith("sketch:"):
        n = _select_named(model, path.split(":", 1)[1].strip(), "SKETCH",
                          SWEEP_PATH_MARK, append=False)
        if n < 1:
            raise PreCallError("★ 扫描路径草图打 mark=%d 后回读计数为 0" % SWEEP_PATH_MARK)
    else:
        for i, one in enumerate(_split(path)):
            _select_marked(model, one, "EDGE", SWEEP_PATH_MARK, append=(i > 0),
                           min_count=i + 1, label="扫描路径 #%d" % (i + 1))

    # ── ③ 引导线（mark 2）· ★ 官方:「used only with sketch profiles」⇒ 可选 ────────
    for i, one in enumerate(_split(guides)):
        _select_marked(model, one, "EDGE", SWEEP_GUIDE_MARK, append=True,
                       min_count=i + 1, label="扫描引导线 #%d" % (i + 1))

    # ── ④ 方向向量（mark 128）· ★ 官方:「a plane, face, line, axis, edge, cylinder,
    #      or a pair of vertices」⇒ 给了就按名字/按点选，不给就不选 ────────────────
    if dirvec:
        if dirvec.lower().startswith(("plane:", "axis:", "sketch:")):
            kind, _, name = dirvec.partition(":")
            type_str = {"plane": "PLANE", "axis": "AXIS", "sketch": "SKETCH"}[kind.lower()]
            _select_named(model, name, type_str, SWEEP_DIRVEC_MARK, append=True)
        else:
            _select_marked(model, dirvec, "FACE", SWEEP_DIRVEC_MARK, append=True,
                           min_count=1, label="扫描方向向量")
    return {"profile_mark": _count_by_mark(model, SWEEP_PROFILE_MARK),
            "path_mark": _count_by_mark(model, SWEEP_PATH_MARK),
            "guide_mark": _count_by_mark(model, SWEEP_GUIDE_MARK),
            "dirvec_mark": _count_by_mark(model, SWEEP_DIRVEC_MARK)}


def _pre_part_loft(params):
    """`solidworks_part_loft` 的 `pre_call` —— ★ **轮廓 mark 1（★ 顺序 = 选择顺序）**。

    官方依据（Remarks **给的是完整表**，且例子逐字给出调用序）:
      · `IFeatureManager\InsertProtrusionBlend2.md` §Remarks 逐字:「1 = profile selections /
        2 = guide curve selections / 4 = centerline selection / 8 = start tangency vector /
        16 = …(not available) / 32 = end tangency vector / 64 = …(not available)」
        ★ 并逐字:「**you must select the profiles in an order consistent with the desired
          direction of the loft**」★ ⇒ ★★ **顺序是官方硬要求，不是本文件的发明**。
      · 调用序（`Insert_Protrusion_Blend_Example_VB.md` 75–81 行）:
        `SelectByID2("Sketch1","SKETCH",…,False,**1**,Nothing,0)` →
        `SelectByID2("Sketch2","SKETCH",…,True,**1**,Nothing,0)` →
        4 条 `REFERENCECURVES` mark = **4098 / 8194 / 12290 / 16386**（= 2×1…4）→
        `SelectByID2("Curve5","REFERENCECURVES",…,True,**4**,Nothing,0)`（中心线）
        ⇒ ★ **引导线按次序进位（2、4、6、8）**，★ 本文件默认只发 `mark=2`，
        ★ 多条时按 `2*(i+1)` 进位（**与官方例子的算式一致**）。

    ⚠ **本工具已有的两条既有事实**（决定我怎么写）:
      · `scripts/sw_loft.py::create_loft_report` 用
        `GetSelectedObjectCount2(1) < 2` 判"至少 2 个轮廓" ⇒ ★ **本 `pre_call` 必须 ≥2**。
      · 官方逐字:「**because a solid is being created, the section profiles must be closed**」
        —— ★ **闭合性 `pre_call` 管不了**（要读草图轮廓），★ 只在报错文案里提醒。
    ★ **`sketch:` 前缀**是本文件给轮廓用的主路径（草图**有名字**，★ 按名选是官方允许的
      ——`SelectByID2.md` 第 75 行的禁令只针对**面/边**）。
    """
    model = _model()
    _clear(model)

    profiles = _split(getattr(params, "profiles", "") or "")
    if len(profiles) < 2:
        raise PreCallError("★ 放样至少要 **2 个轮廓**（官方 Remarks；★ 而仓内 "
                           "`create_loft_report` 用 `GetSelectedObjectCount2(1) < 2` 判前置）"
                           "—— 收到 %d 个：%r" % (len(profiles), profiles))

    # ── 轮廓（mark 1）· ★★ **顺序即方向**（官方硬要求）──────────────────────────
    for i, one in enumerate(profiles):
        if one.lower().startswith("sketch:"):
            name = one.split(":", 1)[1].strip()
            n = _select_named(model, name, "SKETCH", LOFT_PROFILE_MARK, append=(i > 0))
            if n < 1:
                raise PreCallError("★ 第 %d 个轮廓草图 %r 打 mark=%d 回读计数为 0"
                                   "★ ⇒ 草图名不对（中文 UI 是「草图1」—— 事实 9）"
                                   % (i + 1, name, LOFT_PROFILE_MARK))
        else:
            _select_marked(model, one, "FACE", LOFT_PROFILE_MARK, append=(i > 0),
                           min_count=i + 1, label="放样轮廓 #%d" % (i + 1))

    # ── 引导线（mark 2 × k）· ★ 官方例子给的是 4098/8194/…（= 2 × 序号）──────────
    guides = _split(getattr(params, "guide_curves", "") or "")
    for i, one in enumerate(guides):
        mark = LOFT_GUIDE_MARK * (i + 1)      # ★ 与官方例子的 4098/8194/12290/16386 同算式
        _select_marked(model, one, "EDGE", mark, append=True, min_count=1,
                       label="放样引导线 #%d" % (i + 1))

    # ── 中心线（mark 4）· 可选 ─────────────────────────────────────────────────
    centerline = str(getattr(params, "centerline", "") or "").strip()
    if centerline:
        _select_marked(model, centerline, "EDGE", LOFT_CENTERLINE_MARK, append=True,
                       min_count=1, label="放样中心线")

    got = _count_by_mark(model, LOFT_PROFILE_MARK)
    if got < 2:
        raise PreCallError("★ 放样轮廓打上 mark=%d 的只有 %d 个（要 ≥2）"
                           % (LOFT_PROFILE_MARK, got))
    return {"profile_mark": got,
            "guide_marks": [LOFT_GUIDE_MARK * (i + 1) for i in range(len(guides))],
            "centerline_mark": _count_by_mark(model, LOFT_CENTERLINE_MARK)}


def _pre_part_axis(params):
    """`solidworks_part_axis` 的 `pre_call` —— ★★ **mark 查不到；按 0 试（★ 明标未证实）**。

    ★★ **官方依据的完整交代**（铁律 5：查不到就说查不到）:
      · `C:\swapi\types\IModelDoc2\InsertAxis2.md` **整页没有 `## Remarks` 段**
        ⇒ **官方文档层面查不到 mark**。（我逐段核过：只有 front-matter + Description +
        Signature + Parameters + Returns + Examples + See Also。）
      · 该页 **Examples** 指向 `Create_Revolve_Features_Example_{VBA,VB.NET,C#}.md`；
        ★ 三个例子的代码**完全相同**，唯一给出调用序的是
        `Create_Revolve_Features_Example_VB.md` 29–31 行**逐字**:
          `SelectByID2("Right Plane","PLANE",0,0,0,True,**0**,Nothing,swSelectOptionDefault)`  ×2
          → `swModel.InsertAxis2 True`
        ⇒ ★★ **例子层面：两个基准面、mark 均为 0** ⇒ 本文件取 `AXIS_MARK = 0`，
          ★ 并**明确标注这是「例子推断值」而不是「文档给定值」**。
      · ★ 我**没有**做的事：没有去猜「两点 ⇒ mark 0 / 圆柱面 ⇒ mark 0」等其它组合，
        ★ 因为**官方一个字都没写**（★ 猜出来的东西在文档里和「查不到」是同一种东西）。
      · ★ **仓内的真机证据只证明「先在界面选好圆柱面、mark 是多少都能建」**：
        `scripts/sw_part.py::create_axis_report` 只回读 `GetSelectedObjectCount2(-1)`（**全选区**）
        ⇒ ★ **它压根不看 mark** ⇒ ★★ 「mark 对 `InsertAxis2` 是否要紧」在本仓**未实测**。
        ★ 这反而说明取 0 的**风险很低**。

    ★ 选择器：`"index:<n>"` / `"+z"`… 定位被选的几何；★ 官方例子用的是**基准面**
      ⇒ 本文件额外支持 `"plane:<name>"` / `"axis:<name>"`（**有名字的才按名选**）。
    ★ **多条**时官方例子是两次 `SelectByID2` 都带 `Append=True` ⇒ ★ 本文件同样允许多条。
    """
    model = _model()
    _clear(model)

    selection = str(getattr(params, "selection", "") or "").strip()
    if not selection:
        raise PreCallError("★ 建参考轴要先选中几何（官方例子选的是**两个基准面**；"
                           "★ 仓内真机用的是圆柱面 —— 事实 32：面没有名字）")

    items = _split(selection)
    for i, one in enumerate(items):
        low = one.lower()
        if low.startswith(("plane:", "axis:", "sketch:")):
            kind, _, name = one.partition(":")
            type_str = {"plane": "PLANE", "axis": "AXIS", "sketch": "SKETCH"}[kind]
            _select_named(model, name, type_str, AXIS_MARK, append=(i > 0))
        else:
            _select_marked(model, one, "FACE", AXIS_MARK, append=(i > 0),
                           min_count=i + 1, label="建轴的几何 #%d" % (i + 1))
    return {"mark": AXIS_MARK,
            "selected": _count_by_mark(model, -1),
            "⚠": "★ mark=0 是**例子推断值**（`Create_Revolve_Features_Example_VB.md` 29–30 行）"
                  "—— `InsertAxis2.md` **没有 Remarks 段**，官方未给 mark（铁律 5）。"
                  "★ 而仓内 `create_axis_report` 只回读全选区计数、不看 mark ⇒ 风险低。"}


# ══════════════════════════════════════════════════════════════════════════════
# 4 · 集成说明（Lead 复核用；**本文件一个 spec 都没改**）
# ══════════════════════════════════════════════════════════════════════════════
# ── 4.1 六条 spec 的挂法（一行一行，可直接抄）────────────────────────────────
#   # ① mcp-server/tool_specs_batch1.py  ToolSpec(name="solidworks_mold_parting_line", …)
#   #    现在**零个选择参数** ⇒ ★ **必须同时加参数**，否则 `pre_call` 读不到任何东西：
#   param_alias={"pull_direction": None, "parting_line_edges": None},   # ★ None = pre_call 消费，不下传
#   pre_call=_pre_mold_parting_line,
#   params=[…, Param("pull_direction", str, default="+z",
#                    description="声明式拔模/拉动方向（官方 mark=1）。可选 '+z'/'-x'… 或 'index:<n>'"
#                                "（体 0 包围盒那一面 / 第 n 个面）或 'plane:<名>'。"),
#            Param("parting_line_edges", str, default="index:0",
#                    description="声明式分型线边（官方 mark=4）。逗号分隔多条，如 'index:0,index:3'。")],
#
#   # ② mcp-server/tool_specs_batch9.py  ToolSpec(name="solidworks_mold_parting_surface", …)
#   #    ★ **与 ① 同一组参数、同一份实现**：
#   param_alias={"pull_direction": None, "parting_line_edges": None},
#   pre_call=_pre_mold_parting_surface,
#   # ⚠ 官方有条件：「**If a parting line feature does not yet exist**」⇒ ★ 集成时建议
#   #   **先查有没有分型线特征**，有就**跳过** `pre_call`（见 `_pre_mold_parting_surface` 的文档串）。
#
#   # ③ mcp-server/tool_specs_batch50.py ToolSpec(name="solidworks_part_wrap", …)
#   #    ★ 必须加**两个**参数（官方要两个 mark）：
#   param_alias={"sketch": None, "face": None, "pull_direction": None},
#   pre_call=_pre_part_wrap,
#   params=[…, Param("sketch", str, description="草图**名字**（官方 mark=4，★ 必须是 2D 草图）；"
#                                               "中文 UI 传 '草图1'，不要传 'Sketch1'（事实 9）。"),
#            Param("face", str, default="+z", description="包覆面（官方 mark=1）。'+z'/'-x'… 或 "
#                                                     "'index:<n>'；多条逗号分隔。"),
#            Param("pull_direction", str, default="", description="拔模方向（官方 mark=2）"
#                                                     "★ 只在 emboss/engrave 时需要。")],
#   ⚠ 保持 `wrap_type` 仍然是**下传**参数（`_pre_part_wrap` 只读它判断要不要 mark 2，不下传 None）。
#
#   # ④ mcp-server/tool_specs_batch48.py ToolSpec(name="solidworks_part_sweep", …)
#   param_alias={"profile": None, "path": None, "guide_curves": None, "direction_vector": None},
#   pre_call=_pre_part_sweep,
#   params=[…, Param("profile", str, description="扫描轮廓（官方 mark=1）。'sketch:<名>' 或 '+z'… 或 'index:<n>'。"),
#            Param("path", str, description="扫描路径（官方 mark=4）。'sketch:<名>' 或 'index:<n>'；"
#                                          "★ 多段路径还差官方那步 SELOBJGROUP 收口（见下）。"),
#            Param("guide_curves", str, default="", description="引导线（官方 mark=2，可选）。"),
#            Param("direction_vector", str, default="", description="方向向量（官方 mark=128，可选）。")],
#   ★ `cut` 保持下传（目标函数 `create_sweep_report(model, cut=False)` 真收它）。
#
#   # ⑤ mcp-server/tool_specs_batch47.py ToolSpec(name="solidworks_part_loft", …)
#   param_alias={"profiles": None, "guide_curves": None, "centerline": None},
#   pre_call=_pre_part_loft,
#   params=[…, Param("profiles", str, description="轮廓（官方 mark=1），★ **逗号分隔、顺序即放样方向**；"
#                                                   "★ **至少 2 个**。例：'sketch:草图1,sketch:草图2'。"),
#            Param("guide_curves", str, default="", description="引导线（官方 mark 2/4/6/8 进位，可选）。"),
#            Param("centerline", str, default="", description="中心线（官方 mark=4，可选）。")],
#   ★ `closed` / `use_selected_profiles` 保持下传（目标函数真收这两个）。
#   ⚠ `use_selected_profiles=False` 时本 `pre_call` 就不该跑 ⇒ ★ 集成时写成
#   #   `pre_call=_skip_when(params, not params.use_selected_profiles, _pre_part_loft)`
#   #   或在 `_pre_part_loft` 开头加一行 `if not params.use_selected_profiles: return None`（★ 更省事）。
#
#   # ⑥ mcp-server/tool_specs_batch49.py ToolSpec(name="solidworks_part_axis", …)
#   param_alias={"selection": None},
#   pre_call=_pre_part_axis,
#   params=[…, Param("selection", str, description="建轴的几何（★ **官方没给 mark，按 0** —— "
#                                                   "见 `_pre_part_axis` 文档串）。官方例子选两个基准面；"
#                                                   "本仓真机用圆柱面。例：'plane:右视基准面,plane:上视基准面' "
#                                                   "或 '+z'。")],
#   ★ `reverse` 保持下传（目标函数 `create_axis_report(model, reverse=True)` 真收它）。
#
# ── 4.2 ★ 与仓内既有先例的**唯一分歧**（Lead 决断点）─────────────────────────
#   · `tool_specs_batch74.py::_select_faces_for` 走的是 `sw_part._select_com_object(face, mark=…)`；
#     ★ 而那个函数**先试** `obj.Select2(append, mark)` —— ★★ `C:\swapi\types\IEntity\Select2.md`
#     第 12 行逐字「**Obsolete. Superseded by IEntity::Select4**」，★ 且它的 `Mark` 形参
#     官方页面写的是「**No description**」⇒ ★★ **「`Select2` 的 mark 算不算数」= 未证实**。
#   · 本候选**不把 `Select2` 当主路**：主路是**官方点名推荐的 `SelectByRay` / `SelectByID2`
#     （两者第 7/10 参在签名里就是 `Int32 Mark`）**，★ `Select4(ISelectData)` 只作第三档兜底。
#   ⇒ ★ 若 Lead 想统一，**建议先在真机上做一次 A/B**：同一个面，
#     `SelectByRay(…,mark=1)` vs `Select2(append,1)` vs `Select4(CreateSelectData().Mark=1)`，
#     回读 `GetSelectedObjectCount2(1)` —— ★ 三条路的判据是**同一个回读数**。
#
# ── 4.3 ★★ 本文件**没有实现**的三处（**不糊过去**，逐条写清为什么）───────────────
#   ① **扫描多段路径的 `SELOBJGROUP` 收口**（官方 `Select_Multiple_Paths_for_Sweep_Path_
#      Example_VB.md` 第 61 行 `SelectByID2("Unknown","SELOBJGROUP",0,0,0,True,4,Nothing,0)`）——
#      ★ 那是个**虚拟对象**，★ 不在 `IBody2.GetEdges()` 上、★ 也不进选区计数 ⇒
#      ★ `_select_marked` 覆盖不到；★ 且它的效果**未在本机实测**。
#   ② **放样轮廓的"闭合"校验** —— 官方逐字「the section profiles must be closed」，
#      ★ 那要读 `ISketch` 的轮廓，★ 不在选择层 ⇒ 只在报错文案里提醒。
#   ③ **曲面件的取点精度** —— 官方 `IFace2.GetBox.md` §Remarks 逐字「approximate … should not be
#      used for comparison or calculation purposes」⇒ ★ 包围盒中点**可能不在曲面上** ⇒
#      ★ 这正是本文件设计**三级回退 + 六个射线方向**的原因，★ 但**兜底也兜不住时只能抛**。
#
# ── 4.4 置信度（**按"官方依据的强度"评，不是按代码好不好看**）──────────────────
#   · `solidworks_part_wrap`       **高** —— Remarks 给完整 mark 表 **且两个官方例子逐字给出
#                                    「先草图 mark4、后面 mark1」的调用序，★ 三源一致。
#   · `solidworks_part_sweep`      **高（选区）/ 中（端到端）** —— 扫描专文逐字点名
#                                    `SelectByRay` + 四个 mark，`SelectByID2.md` §Remarks 又点名
#                                    mark 4；★ 但仓内 `AccessSelections` 的 `0x80010105`（轮 488）
#                                    ★ 是 `pre_call` 修不了的 ⇒ 端到端只能给「中」。
#   · `solidworks_part_loft`       **高** —— Remarks **完整 mark 表**（1/2/4/8/32）+ 例子逐字给出
#                                    「轮廓按顺序 mark=1、引导线 4098/8194/…、中心线 mark=4」。
#   · `solidworks_mold_parting_line` / `_surface`  **中** —— mark 有 **Remarks 逐字**，
#                                    ★ **但官方没有任何「创建」的完整例子**（唯一相关例子是
#                                    `Get_and_Set_Parting_Line_Feature_Data_Example_VB.md`，
#                                    ★ 它是**改**已有分型线的 `AccessSelections`+`ModifyDefinition`）
#                                    ⇒ ★ 「先 1 后 4」只依据 Remarks 的**行序**，
#                                    ★ 且两条工具在仓内**都没有真机通过记录**。
#   · `solidworks_part_axis`       **低（mark）/ 中（功能）** —— ★★ `InsertAxis2.md`
#                                    **整页没有 Remarks 段** ⇒ **官方未给 mark**；★ `0` 是
#                                    `Create_Revolve_Features_Example_VB.md` 29–30 行的
#                                    **例子推断值**；★★ 但仓内 `create_axis_report` 只读全选区、
#                                    **压根不看 mark** ⇒ 功能上风险低，**只是 mark 无据**。
#
# ── 4.5 ★ 本文件**未在本机跑过**（真机由 Lead 独家执行）────────────────────────
#   ⇒ 凡"未证实"三处（4.3）**都必须真机过一遍**才能写进 `capabilities.yaml` 的 `verified`。
# ══════════════════════════════════════════════════════════════════════════════

__all__ = [
    "PreCallError",
    "AXIS_MARK", "LOFT_CENTERLINE_MARK", "LOFT_GUIDE_MARK", "LOFT_PROFILE_MARK",
    "PARTING_EDGE_MARK", "PULL_MARK", "SWEEP_DIRVEC_MARK", "SWEEP_GUIDE_MARK",
    "SWEEP_PATH_MARK", "SWEEP_PROFILE_MARK", "WRAP_FACE_MARK", "WRAP_PULLDIR_MARK",
    "WRAP_SKETCH_MARK",
    "_pre_mold_parting_line", "_pre_mold_parting_surface", "_pre_part_axis",
    "_pre_part_loft", "_pre_part_sweep", "_pre_part_wrap",
]
