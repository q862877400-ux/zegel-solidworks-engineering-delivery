"""A 组三个「要求调用方先选」工具的 `pre_call` 候选（模具分型线 / 分型面 / 包覆）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**候选**；由 Lead 复核后集成，★ 本文件未挂到任何 ToolSpec 上）
# 文件:   specs/202-user-coverage-gaps/recon/precall-cand/precall-cand-A.py
# 定位:   为 ① `solidworks_mold_parting_line` ② `solidworks_mold_parting_surface`
#         ③ `solidworks_part_wrap` 各写一个可直接粘进 `ToolSpec(pre_call=…)` 的函数。
#         ★ 范围只有 A 组三条（B 组 part_sweep / loft / axis 不在本文件）。
# 官方依据（mark 与前置只在这里 —— 逐条给出可 grep 的原文）:
#   · `C:\swapi\types\IFeatureManager\InsertMoldPartingLine.md` §Remarks **整段逐字**:
#       「Before calling this method, you must select the direction of pull and the
#         edges for the parting line by calling IModelDocExtension::SelectByID2
#         with the following Marks:」随后表格 **Direction of pull → 1** /
#         **Parting line edges → 4**
#   · `C:\swapi\types\IFeatureManager\InsertMoldPartingSurface.md` §Remarks 逐字:
#       「…you must first select the direction of pull and the edges for the parting
#         line…For example, **a face (direction of pull) has a mark of 1** and **edges
#         (parting lines) a mark of 4**.」★ 与上一条**完全同形**
#         ⇒ 本文件让两条**共用同一个 `_pre_parting` 实现**。
#   · `C:\swapi\types\IFeatureManager\InsertWrapFeature2.md` §Remarks 的 mark 表:
#       「One or more faces on which to place the wrap feature → **1**」/
#       「Pull direction entity if Type is Emboss or Engrave → **2**」/
#       「2D sketch containing no open contours; 3D sketches are not supported → **4**」
#   · `C:\swapi\examples\Create_Wrap_Feature_on_Multiple_Faces_Example_VB.md`
#     （**调用序**）逐字: `SelectByID2("Sketch30","SKETCH",0,0,0,False,4,Nothing,0)`
#     之后六条 `SelectByRay(…,2,True,1,0)` —— 末位那个 `1` 是 **Mark**
#     （`C:\swapi\types\IModelDocExtension\SelectByRay.md` 第 10 参逐字「Value to use as
#     a mark; this value is used by other functions that require ordered selection」），
#     ⇒ **官方例子自己给面用了 Mark = 1**。
#   · ★★ **「mark 怎么真正写进去」**：官方字面推荐的是 `SelectByID2`，★ 而本仓**事实 32**
#     实测 `SelectByID2("Edge1","EDGE")` / `SelectByID2("Face1","FACE")` 计数**均为 0**
#     ⇒ **官方那条路对边/面在本仓走不通**。⇒ 本文件改走 **`Select4` + `ISelectData`**：
#       · `C:\swapi\types\IModelDocExtension\SelectByID2.md` 之外的后继成员
#         `C:\swapi\types\IEntity\Select4.md` 签名逐字 `Select4(bool Append, SelectData Data)`
#       · `C:\swapi\types\ISelectionMgr\CreateSelectData.md`「Creates a **SelectData** object
#         to use as argument with Select methods.」
#       · ★ 官方例子逐字（`C:\swapi\examples\Exclude_Faces_Before_Flattening_Example_CSharp.md`）:
#         `SelectData data = ((SelectionMgr)Part.SelectionManager).CreateSelectData();`
#         `data.Mark = 1; entity.Select4(true, data);`   ← **选一个「面」并打 mark 1**
#       · 反射（第三源）`scripts/sw_api_sldworks.py:15284` 的 `ISelectData` 属性元组
#         逐字含 `Mark`（同元组还有 `Callout / View / X / Y / Z`）
#       ⇒ **文档 + 官方例子 + 反射 三源互证**（铁律 4）。
#   · ★ **刻意不用** `IEntity.Select2(Append, Mark)`：`C:\swapi\types\IEntity\Select2.md`
#     第 12 行逐字「**Obsolete. Superseded by IEntity::Select4**」⇒ 取后继，不取废弃成员。
#     （⚠ 但**仓内现成的** `sw_part._select_com_object` / `tool_specs_batch74._select_faces_for`
#     **走的是 Select2(mark)** 那条 —— 本文件**不照抄那一点**，理由见「与仓内先例的唯一分歧」。）
#   · 仓内 `pre_call` 先例（**形状照抄**）:
#       `mcp-server/tool_specs_batch23.py::_select_edge`（声明式 `selection` + 回读计数）
#       `mcp-server/tool_specs_batch74.py::_select_faces_for`（按 mark 选 + 回读 + 不够就抛）
# 许可:   本仓库 MIT。**无第三方代码引入**（solidpilot-salvage 的 `sdP.Mark = 1` 写法
#         只在**核对时**看过，未抄文本 —— 本文件用的是上面那条**官方例子**）。
# 覆盖:   全文件
# ⚠ **未在本机实测**（真机由 Lead 独家执行）。凡**没有官方依据**的地方逐条写「未证实」。
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

# ── 官方 mark 常量（每个都注明出处，别再散落字面量）─────────────────────────
PULL_MARK = 1     # InsertMoldPartingLine.md §Remarks 表格「Direction of pull」行
LINE_MARK = 4     # InsertMoldPartingLine.md §Remarks 表格「Parting line edges」行
FACE_MARK = 1     # InsertWrapFeature2.md §Remarks「One or more faces …」行
PULLDIR_MARK = 2  # InsertWrapFeature2.md §Remarks「Pull direction entity …」行（Emboss/Engrave 才要）
SKETCH_MARK = 4   # InsertWrapFeature2.md §Remarks「2D sketch … 3D sketches are not supported」行

CURRENT = "__current_selection__"
_MULTI_HINT = '多条用逗号，如 "index:1,index:5"'


# ── 共用底座 ────────────────────────────────────────────────────────────────
def _model():
    """取活动文档（照 `mcp-server/tool_specs_batch23.py::_model` 的既有形状）。

    ★ 注册器的调用序（`mcp-server/tool_registry.py:499-513`）是
      `kwargs[inject] = resolver(params)` → `spec.pre_call(params)` → `fn(**kwargs)`
      ⇒ **`pre_call` 里重新取一次 model 是安全的**（拿到的仍是同一个活动文档）。
    """
    from scripts.sw_connect import connect_solidworks

    _sw, model, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    if model is None:
        raise RuntimeError("没有活动文档 —— 请先打开一个零件")
    return model


def _clear(model):
    """清空选区。★ batch74 实测：`RESOLVERS['model']` 会清掉选区
    （证据 `output/selection-lifetime-evidence.json`）⇒ **`pre_call` 必须自己先清一次**。
    """
    from scripts.sw_connect import get_com_member

    try:
        get_com_member(model, "ClearSelection2", True)
    except Exception:                                              # noqa: BLE001
        pass


def _count_by_mark(model, mark):
    """回读**某个 mark** 上的选区计数。

    ★ 判据永远是这个回读数（事实 8：`SelectByID2` / `Select4` 的 bool 实测 12 次全 false
      而计数 12）。`GetSelectedObjectCount2(mark)` 就是 `sw_wrap.create_wrap_report`
      自己用来判「草图 mark4 / 面 mark1」的那一个成员（`scripts/sw_wrap.py:94-99`）。
    """
    from scripts.sw_connect import get_com_member

    sm = get_com_member(model, "SelectionManager")
    return int(get_com_member(sm, "GetSelectedObjectCount2", int(mark)) or 0)


def _entity_objects(model, selector, kind, *, body_index=0):
    """把声明式选择器解析成 **COM 实体对象列表（★ 先不选）**。

    ★★ **与 `sw_selection_spec.resolve_entity` 的唯一差别（本文件刻意偏离的那一点）**：
      `resolve_entity` 内部会 `select_object(obj)` ⇒ `Select4(append=False)`
      ⇒ ★ **它会把之前选好的东西清掉** ⇒ **多 mark 工具不能用它选第二次**。
      ⇒ 这里只借它两个**不产生副作用**的底座：`current_selection` 与 `entities_on_body`
      （两者都在 `scripts/sw_selection_spec.py::__all__` 里）。

    支持的选择器（与仓内既有 `selection` 参数同一约定）：
      * ``"__current_selection__"`` —— 用当前已选中项的第一个
      * ``"index:<n>"``            —— 体上第 n 个实体（0 基）
      * ``"index:<n>,index:<m>"``  —— 多个（分型线常常不止一条边）
      （★ 序号顺序官方未承诺稳定 —— 同一句警告见 `sw_selection_spec.entities_on_body`。）

    :raises RuntimeError: 选择器非法 / 越界 / 空选区（**选不到就报错，不静默**）。
    """
    from scripts.sw_selection_spec import current_selection, entities_on_body

    sel = str(selector or "").strip()
    if sel == CURRENT:
        found = current_selection(model)
        if not found:
            raise RuntimeError(
                "选择器是 %r，但当前**没有任何选中项** —— 用 index:<n>，或先在界面上选中一个实体"
                % CURRENT
            )
        return [found[0]]
    if not sel.startswith("index:"):
        raise RuntimeError(
            "非法的实体选择器 %r；合法形式：%r、'index:<n>'、'index:<n>,index:<m>'"
            % (selector, CURRENT)
        )
    items = entities_on_body(model, kind, body_index=int(body_index))
    out = []
    for chunk in sel.split(","):
        chunk = chunk.strip()
        if not chunk.startswith("index:"):
            raise RuntimeError("非法的实体选择器片段 %r（应为 'index:<整数>'）" % chunk)
        try:
            idx = int(chunk.split(":", 1)[1])
        except ValueError:
            raise RuntimeError("非法的 index 选择器 %r（应为 index:<整数>）" % chunk) from None
        if idx < 0 or idx >= len(items):
            raise RuntimeError(
                "%s 序号 %d 越界（体 %d 上共 %d 个）"
                % (kind, idx, int(body_index), len(items))
            )
        out.append(items[idx])
    if not out:
        raise RuntimeError("选择器 %r 没解析出任何实体" % selector)
    return out


def _select_one_with_mark(model, obj, mark, append, expected_min=1):
    """按官方 mark 选中**一个对象**（`ISelectData` 路），返回该 mark 的回读计数。

    官方依据（三源互证，见文件头来源块）：`ISelectionMgr.CreateSelectData` → `data.Mark`
    → `IEntity.Select4(Append, Data)`；官方例子逐字见 `Exclude_Faces_Before_Flattening_Example_CSharp.md`。

    :param expected_min: 本次调用后**该 mark 至少**要有的计数 —— 用它抓「append 没生效」。
    :raises RuntimeError: `CreateSelectData` 回 None / `Select4` 抛错 / 回读计数不足。
    """
    from scripts.sw_connect import get_com_member, set_com_member

    sm = get_com_member(model, "SelectionManager")
    data = get_com_member(sm, "CreateSelectData")
    if data is None:
        raise RuntimeError(
            "ISelectionMgr.CreateSelectData 回 None ⇒ 「按对象带 mark 选」这条路在本机走不通"
        )
    set_com_member(data, "Mark", int(mark))
    try:
        ret = obj.Select4(bool(append), data)
    except Exception as exc:                                       # noqa: BLE001
        raise RuntimeError(
            "Select4(Append, ISelectData) 报错（mark=%d）：%s: %s"
            % (int(mark), type(exc).__name__, str(exc)[:150])
        ) from exc
    count = _count_by_mark(model, mark)
    if count < int(expected_min):
        raise RuntimeError(
            "按 mark=%d 选完**回读计数 %d < %d**（Select4 自己回 %s）⇒ 没选中"
            "（★ 判据是回读不是返回值 —— 事实 8）" % (int(mark), count, int(expected_min), ret)
        )
    return count


def _select_marked(model, selector, kind, mark, *, append=False, body_index=0, min_count=1):
    """声明式选择器 → 按 `mark` 选区 → **回读计数**（形状同 `batch74::_select_faces_for`）。"""
    objs = _entity_objects(model, selector, kind, body_index=body_index)
    count = 0
    for i, obj in enumerate(objs):
        count = _select_one_with_mark(
            model, obj, mark,
            append=bool(append) or i > 0,      # ★ 第 2 个起用 append（照 batch74）
            expected_min=i + 1,                # ★ append 生效 ⇒ 该 mark 计数应递增
        )
    if count < int(min_count):
        raise RuntimeError(
            "前置未成立：按 mark=%d 只选上 %d/%d 个 %s（官方要求的对象没备齐）"
            % (int(mark), count, int(min_count), kind)
        )
    return count


def _select_named_with_mark(model, name, type_name, mark, *, append=False):
    """按**名字**选实体并打 mark —— ★ **官方字面写的那条路**
    （`InsertMoldPartingLine.md` / `InsertMoldPartingSurface.md` 的 Remarks 都逐字说
    「by calling IModelDocExtension::SelectByID2」）。

    ★ **只对有名字的实体成立**（基准面 / 轴 / **草图**）—— 本仓**事实 32** 实测
      `SelectByID2("Edge1","EDGE")` 与 `SelectByID2("Face1","FACE")` 计数**均为 0**
      ⇒ **边与面必须走 `_select_marked`**。

    ⚠ 复用 `sw_part._select_by_id`（它内部就是
      `SelectByID2(name, type, 0,0,0, append, mark, _empty_callout(), 0)`，
      ★ Callout 必须是 `VARIANT(VT_DISPATCH, None)` —— 事实 33）。
    """
    from scripts.sw_connect import get_com_member
    from scripts.sw_part import _select_by_id

    ext = get_com_member(model, "Extension")
    ret = bool(_select_by_id(ext, str(name), str(type_name), append=bool(append), mark=int(mark)))
    count = _count_by_mark(model, mark)
    if count < 1:
        raise RuntimeError(
            "SelectByID2(%r, %r, mark=%d) 回读计数 0（它自己回 %s）⇒ 没选中"
            "（★ 事实 32：边/面按名字选不中 ⇒ 这条路只适用于**有名字**的实体）"
            % (name, type_name, int(mark), ret)
        )
    return count


# ── ① + ② 模具：分型线 / 分型面（★ 同形 ⇒ 共用）────────────────────────────────
def _pull_direction(model, params):
    """选**拔模方向**（官方 mark = **1**）。

    两条路，按 `params` 里有没有名字分流：
      · `pull_direction_name` 非空 ⇒ `SelectByID2(name, type, mark=1)`
        （基准面 / 轴等**有名字**的实体；★ 仓内 `sw_mold.insert_parting_line` 的文档串
        也把「边线/基准面/轴」列为候选）
      · 否则 ⇒ `_select_marked(..., kind="FACE")`。★ 官方 `InsertMoldPartingSurface.md`
        逐字把拔模方向的例子写成「**a face** (direction of pull) has a mark of 1」。
    """
    named = str(getattr(params, "pull_direction_name", "") or "").strip()
    if named:
        return _select_named_with_mark(
            model, named,
            str(getattr(params, "pull_direction_type", "PLANE") or "PLANE"),
            PULL_MARK, append=False,
        )
    return _select_marked(
        model, getattr(params, "pull_direction_selection"),
        "FACE", PULL_MARK, append=False,
        body_index=int(getattr(params, "body_index", 0) or 0),
    )


def _pre_parting(model, params):
    """**分型线 / 分型面共用**的建选区流程：拔模方向 mark 1 → 分型线边 mark 4。

    ★ 官方两条 Remarks 的 mark 表**逐字相同** ⇒ 共用这一个实现（总表判「边际成本≈0」，
      本文件把它落成真代码）。

    ⚠ **官方 §Remarks 与本文件唯一的不一致（未证实，如实登记）**：
      官方把「怎么选」写成 `SelectByID2`；★ 本仓**事实 32** 说那条路对**边/面按名字**无效
      ⇒ 本文件对边/面改走 `Select4` + `ISelectData.Mark`（官方例子逐字，见来源块）。
      ★★ **未证实**：SolidWorks 的 `InsertMoldPartingLine` 究竟吃的是「`ISelectData` 写进去的
      mark」还是只认 `SelectByID2` 通道的 mark —— ★ **两者写的是同一个 `ISelectionMgr` 的
      mark 空间，理论上同源，但本仓没有真机证据**。
      ⇒ **Lead 真机验证时，第一件事就是量 `GetSelectedObjectCount2(1)` 与 `(4)`。**
    """
    _clear(model)
    got_pull = _pull_direction(model, params)
    got_line = _select_marked(
        model, getattr(params, "parting_edge_selection"),
        "EDGE", LINE_MARK, append=True,
        body_index=int(getattr(params, "body_index", 0) or 0),
    )
    return {"pull_mark1": got_pull, "parting_edges_mark4": got_line}


def _pre_mold_parting_line(params):
    """`pre_call` for `solidworks_mold_parting_line`（`sw_mold.insert_parting_line`）。

    官方依据：`C:\swapi\types\IFeatureManager\InsertMoldPartingLine.md` §Remarks
    「Before calling this method, you must select the direction of pull and the edges for
    the parting line … Marks: Direction of pull **1** / Parting line edges **4**」。
    目标函数 `scripts/sw_mold.py::insert_parting_line` 函数体只有一句
    `InsertMoldPartingLine(...)`，**一个实体都不选** ⇒ 缺选区时是**静默失败**（回 None）。

    :returns: `{"pull_mark1": n, "parting_edges_mark4": m}`（`pre_call` 的返回值被忽略，
      这里返回只是为了**测试时能断言**；`tool_registry.py:513` 明确 `spec.pre_call(params)`
      的结果不进 `kwargs`）。
    """
    model = _model()
    return _pre_parting(model, params)


def _pre_mold_parting_surface(params):
    """`pre_call` for `solidworks_mold_parting_surface`（`sw_mold.insert_parting_surface`）。

    官方依据：`C:\swapi\types\IFeatureManager\InsertMoldPartingSurface.md` §Remarks
    「**f a parting line feature does not yet exist in the model**, you must first select
    the direction of pull and the edges for the parting line … a face (direction of pull)
    has a mark of **1** and edges (parting lines) a mark of **4**.」
    ⇒ ★ mark 表与 `_pre_mold_parting_line` **完全同形**，故**共用 `_pre_parting`**。

    ★★ **分档「条件」的落地方式**：官方那句前置是**有条件的**（模型里还没有分型线时）。
      本文件**不替官方发明「如何判断分型线已存在」**（官方与 CHM 都没给；
      特征类型名 `IPartingLineFeatureData` 的字符串值本仓也**未实测**）
      ⇒ ★ **改成一个由调用方显式声明的 `has_parting_line` 布尔**：
      - `True`  ⇒ **跳过选择**（官方说这时不需要）
      - `False`（默认）⇒ 走与分型线完全相同的两步选择
    ⇒ 这样「条件」是**调用方声明的事实**，而不是本文件猜的。

    ⚠ 另一个**未证实**：`sw_mold.insert_parting_surface` 的 8 个形参名
      （`surface_type/flip/use_trim/distance/angle/option/tolerance/alternate`）与官方
      `InsertMoldPartingSurface(Radiate, ReverseAlignment, ReverseOffset, OffsetDistance,
      Angle, Smooth, SmoothDistance, Knit)` **名字不同**（位置对）。本文件**不碰**它。
    """
    model = _model()
    if bool(getattr(params, "has_parting_line", False)):
        #: 官方说这时不需要选 —— 但仍**清一次选区**，免得带上别的调用残留的选中项。
        _clear(model)
        return {"skipped": True, "reason": "has_parting_line=True（官方：已有分型线时不需要选）"}
    return _pre_parting(model, params)


# ── ③ 包覆（草图 mark 4 + 面 mark 1）──────────────────────────────────────────
def _pre_part_wrap(params):
    """`pre_call` for `solidworks_part_wrap`（`sw_wrap.create_wrap_report`）。

    官方依据：
      · `C:\swapi\types\IFeatureManager\InsertWrapFeature2.md` §Remarks mark 表：
        面 → **1** · 拔模方向实体（Emboss/Engrave 才要）→ **2** · 2D 草图 → **4**
        （逐字「**3D sketches are invalid**」）
      · `C:\swapi\examples\Create_Wrap_Feature_on_Multiple_Faces_Example_VB.md`
        **调用序**：先 `SelectByID2("Sketch30","SKETCH",0,0,0,False,4,Nothing,0)`
        ⇒ ★ **草图有名字** ⇒ 走官方字面那条路（事实 32：按名字选对**特征**成立）；
        再六条 `SelectByRay(…,2,True,1,0)` ⇒ 面 **Mark = 1**（见来源块里 `SelectByRay.md`
        第 10 参的逐字）⇒ ★ 面**没有名字** ⇒ 本文件改走 `Select4` + `ISelectData`。

    目标函数 `scripts/sw_wrap.py::create_wrap_report` 自己会读
    `GetSelectedObjectCount2(4)` 与 `(1)`，不足就
    `return {"ok": False, "stage": "selection", …}` ⇒ 这是「**显式拒**」那一档：
    经工具层**必然失败**、且失败原因明确。★ 本 `pre_call` 的作用是让它**根本不会走到那一步**。

    ★ **拔模方向（mark 2）是可选的**：官方逐字「To wrap the sketch normal to the sketch
    plane, **do not select** a pull direction entity」⇒ 本文件**只在调用方显式给出**
    `pull_direction_selection` / `pull_direction_name` 时才选，默认**不选**。
    ⚠ **未证实**：仓内 `tool_specs_batch50` 已记真机结论「传 deboss/scribe 建出来的类型名
    仍是 `Emboss`」⇒ ★ 本工具**只有 `emboss` 被真机证实过**；`wrap_type` 不影响本 `pre_call`。

    ⚠ **草图「必须是 2D」这一点本函数无法静态保证** —— 3D 草图在工具面上没有声明位。
      ⇒ **建议 Lead 在 `create_wrap_report` 侧或本 `pre_call` 的报错里加一句 3D 提示**；
      本文件只把**它写在这里**，不替目标函数改行为。
    """
    model = _model()
    _clear(model)

    #: ── ① 草图 mark = 4（官方字面 SelectByID2 路；草图是**特征**⇒ 有名字）
    sketch_name = str(getattr(params, "sketch_name", "") or "").strip()
    if not sketch_name:
        raise RuntimeError(
            "包覆需要**草图**（官方 mark=4，且必须是 2D 草图）—— 请给 sketch_name"
            "（草图特征名，如 '草图1' / 'Sketch1'）"
        )
    from scripts.sw_connect import get_com_member
    from scripts.sw_part import _get_sketch_name_candidates, _select_first_candidate

    ext = get_com_member(model, "Extension")
    got_sketch = _select_first_candidate(
        ext, _get_sketch_name_candidates(sketch_name), "SKETCH",
        append=False, mark=SKETCH_MARK,
    )
    if not got_sketch or _count_by_mark(model, SKETCH_MARK) < 1:
        raise RuntimeError(
            "草图 %r 没选中（SelectByID2(…, 'SKETCH', mark=4) 回读 mark4 计数为 0）"
            % sketch_name
        )

    #: ── ② 面 mark = 1（面**没有名字** ⇒ Select4 + ISelectData；官方例子 Mark=1）
    got_face = _select_marked(
        model, getattr(params, "face_selection"),
        "FACE", FACE_MARK, append=True,
        body_index=int(getattr(params, "body_index", 0) or 0),
    )

    #: ── ③ 拔模方向 mark = 2（**可选**；官方：不要就**别选**）
    pulldir = None
    named = str(getattr(params, "pull_direction_name", "") or "").strip()
    if named:
        pulldir = _select_named_with_mark(
            model, named,
            str(getattr(params, "pull_direction_type", "PLANE") or "PLANE"),
            PULLDIR_MARK, append=True,
        )
    elif str(getattr(params, "pull_direction_selection", "") or "").strip():
        pulldir = _select_marked(
            model, getattr(params, "pull_direction_selection"),
            "FACE", PULLDIR_MARK, append=True,
            body_index=int(getattr(params, "body_index", 0) or 0),
        )
    return {"sketch_mark4": 1, "faces_mark1": got_face, "pull_dir_mark2": pulldir}


# ═══════════════════════════════════════════════════════════════════════════
# 集成说明（给 Lead；★ 本文件**没有**改任何已有文件）
# ═══════════════════════════════════════════════════════════════════════════
#
# ── 0. 为什么必须落在 `pre_call`（不是 `derived_args`）────────────────────────
# `mcp-server/tool_registry.py::make_tool_function._impl` 的调用序（实测行号）：
#   499-498 `kwargs[inject] = resolver(params)`   ← ①**这一步会清空选区**
#   510-513 `spec.pre_call(params)`                ← ②**唯一能建选区且活到第 4 步的钩子**
#   514-523 `extra = spec.derived_args(params)`    ← ③ 产出实参，不是副作用钩子
#   525     `mod.fn(**kwargs)`                     ← ④ 目标函数
# ★ `RESOLVERS['model']` 经 `connect_solidworks()` 清空选区，真机证据
#   `output/selection-lifetime-evidence.json`（见 `tool_specs_batch74.py:90-100` 的转述）
#   ⇒ ★★ **`pre_call` 里必须自己 `ClearSelection2` 一次**（本文件三个函数都做了）。
#
# ── 1. `solidworks_mold_parting_line` — spec 在 `mcp-server/tool_specs_batch1.py:109-121`
#     现有参数：**只有** `draft_analysis`（bool, 默认 True）· inject="model" · 无 param_alias
#     目标函数：`scripts/sw_mold.py::insert_parting_line(model, *, draft_analysis=True)`
#
#     要**同时加参数**（★ 都由 `pre_call` 消费 ⇒ `param_alias` 映射到 `None`，
#     这样它们**不进目标函数** —— 与 `tool_specs_batch23._consumed` 同一约定）：
#         param_alias={"pull_direction_selection": None,
#                      "pull_direction_name": None,
#                      "pull_direction_type": None,
#                      "parting_edge_selection": None,
#                      "body_index": None},
#         pre_call=_pre_mold_parting_line,
#         params=[ Param("pull_direction_selection", str,
#                        description="拔模方向：**面**（官方 InsertMoldPartingSurface.md 逐字
#                            「a face (direction of pull) has a mark of 1」）。"
#                            "'index:<n>'；" + _MULTI_HINT + "（0 基，体上第 n 个面）"),
#                  Param("parting_edge_selection", str,
#                        description="分型线**边**（官方 mark = 4）。'index:<n>'；" + _MULTI_HINT),
#                  Param("pull_direction_name", str, default="",
#                        description="★ 可选：改用**有名字**的实体当拔模方向（基准面/轴）。"
+                            "给了就走官方字面那条 SelectByID2 路。★ 留空则用上面的面路线。"
+                            "⚠ 边与面**按名字选不中**（本仓事实 32）—— 只对基准面/轴/草图这类"
+                            "**有名字**的实体有效。"),
#                  Param("pull_direction_type", str, default="PLANE",
#                        description="`pull_direction_name` 的官方类型串（'PLANE' / 'AXIS' / …）。"
+                            "只在给了名字时才有意义。"),
#                  Param("body_index", int, default=0,
#                        description="第几个实体体（0 基）。⚠ 序号顺序官方未承诺稳定。") ]
#     ★ 为什么**必须**加参数：MCP 客户端**没有机会**在调工具前操作 SolidWorks 选区，
#       而官方前置**逐字**要求先选 ⇒ 不加参数就等于「这条工具经 MCP 永远建不出来」。
#     ★ 置信度：**高** —— 官方 Remarks 给的是**整张 mark 表 + 明确的调用序**，
#       本仓事实 8（回读计数）+ 事实 32（按名字选不行）也都有真机证据。
#       ★ 唯一的「未证实」已写在 `_pre_parting` 的 docstring 里（ISelectData 那条路）。
#
# ── 2. `solidworks_mold_parting_surface` — spec 在 `mcp-server/tool_specs_batch9.py:54-71`
#     现有参数：`surface_type / flip / use_trim / distance / angle / option / tolerance /
#     alternate`（8 个）· inject="model" · `param_alias={}`
#     目标函数：`scripts/sw_mold.py::insert_parting_surface(model, *, …8 个)`（位置对齐官方）
#
#     要**同时加参数**：与第 1 条**完全相同的 5 个**（外加第 6 个）：
#         param_alias={"has_parting_line": None,
#                      "pull_direction_selection": None,
#                      "pull_direction_name": None,
#                      "pull_direction_type": None,
#                      "parting_edge_selection": None,
#                      "body_index": None},
#         pre_call=_pre_mold_parting_surface,
#         params=[ …第 1 条那 5 个 Param…,
#                  Param("has_parting_line", bool, default=False,
#                        description="模型里**是否已有分型线特征**。官方 §Remarks 的前置是"
+                            "**有条件的**（「f a parting line feature does not yet exist…」）；"
+                            "★ 官方与 CHM 都**没给**「如何判断分型线已存在」⇒ 本工具**不猜**，"
+                            "改由调用方声明。False ⇒ 按官方做两步选择；True ⇒ 跳过选择。") ]
#     ★ 置信度：**中** —— mark 本身**高**（与第 1 条同一段官方表述，逐字给了 1 与 4），
#       但「**什么时候该跳过**」这一步需要调用方声明 `has_parting_line`，
#       ★ 而**本仓没有**一个经过验证的「判断分型线特征是否存在」的实现
#       （候选做法是遍历特征树比 `GetTypeName2()`，但**类型名字符串未实测** ⇒ 未证实）。
#       ⇒ 这是它比第 1 条低一档的**唯一**原因。
#
# ── 3. `solidworks_part_wrap` — spec 在 `mcp-server/tool_specs_batch50.py:31-54`
#     现有参数：`wrap_type`（str, 默认 emboss）· `thickness_mm`（float）· `reverse`（bool）
#     inject="model" · 无 param_alias
#     目标函数：`scripts/sw_wrap.py::create_wrap_report(model, wrap_type, thickness_mm, reverse)`
#
#     要**同时加参数**（★ 全由 `pre_call` 消费 ⇒ `param_alias` 全映射到 `None`）：
#         param_alias={"sketch_name": None, "face_selection": None,
#                      "pull_direction_selection": None, "pull_direction_name": None,
#                      "pull_direction_type": None, "body_index": None},
#         pre_call=_pre_part_wrap,
#         params=[ Param("sketch_name", str,
#                        description="★ **必需**：包覆草图的特征名（官方 mark = **4**；官方逐字"
+                            "「**3D sketches are invalid**」）。官方例子逐字走 "
+                            "`SelectByID2(\"Sketch30\",\"SKETCH\",0,0,0,False,4,…)`。"
+                            "★ 草图是**特征** ⇒ 有名字 ⇒ 事实 32 的「按名字选不通」不适用。"),
#                  Param("face_selection", str,
#                        description="★ **必需**：包覆所在**面**（官方 mark = **1**；官方例子用 "
+                            "`SelectByRay(…, Mark=1)`）。面**没有名字** ⇒ 走 Select4+ISelectData。"
+                            "'index:<n>'；" + _MULTI_HINT),
#                  Param("pull_direction_selection", str, default="",
#                        description="★ 可选：拔模方向实体（官方 mark = **2**，只有 Emboss/Engrave "
+                            "才需要）。★ 官方逐字「To wrap the sketch normal to the sketch plane,"
+                            " **do not select** a pull direction entity」⇒ 默认**不选**。"),
#                  Param("pull_direction_name", str, default="",
#                        description="★ 可选：同上，但用**有名字**的实体（基准面/轴）走 SelectByID2。"),
#                  Param("pull_direction_type", str, default="PLANE",
#                        description="`pull_direction_name` 的官方类型串。只在给了名字时才有意义。"),
#                  Param("body_index", int, default=0,
#                        description="第几个实体体（0 基，选面时用）。⚠ 序号顺序官方未承诺稳定。") ]
#     ★ 为什么**必须**加参数：`sw_wrap.create_wrap_report` 自己读
#       `GetSelectedObjectCount2(4)` 与 `(1)`，不足就 `return {"ok": False, "stage": "selection"}`
#       ⇒ ★ **经工具层必然失败**（`output/wrap-evidence.json` 那次真机 PASS 是因为**界面里
#       已经选好了**；走 MCP 时客户端**做不到**）。
#     ★ 置信度：**高** —— mark 表**逐字**在官方页上，**调用序**由官方例子给出
#       （先草图 `SelectByID2 mark=4`，再面 `Mark=1`），
#       而两条路各自的可行性也都有依据（草图按名字 ✓ 事实 32；面按对象 ✓ 事实 32 + 官方例子）。
#       ★ 唯一「未证实」：3D 草图这个非法情形**在工具面上无法静态拦**（已写在 docstring 里）。
#
# ── 与仓内先例的**唯一**分歧（请 Lead 复核这一条）────────────────────────────
# `mcp-server/tool_specs_batch74.py::_select_faces_for` 走的是
# `sw_part._select_com_object(face, append=…, mark=mark)`，而那个函数**先试
# `Select2(append, mark)`** —— 也就是说**它把 mark 交给了官方已标 Obsolete 的 `Select2`**
# （`C:\swapi\types\IEntity\Select2.md` 第 12 行逐字「Obsolete. Superseded by
# IEntity::Select4」），`Select2` 失败才退到 `Select4(append, callout)`（**不带 mark**）。
# ⇒ ★ **本文件不照抄那一点**：三个候选统一走**后继** `Select4` + `ISelectData.Mark`
#   （官方例子逐字 + 反射确认 `ISelectData` 有 `Mark` 属性）。
# ⇒ ★ 若 Lead 更看重「与 batch74 完全一致」而不是「不碰 Obsolete 成员」，
#   把 `_select_one_with_mark` 的函数体换成
#   `return sw_part._select_com_object(obj, append=append, mark=mark)` 即可 —— 那样就与
#   `_select_faces_for` 同源；★ **但那样 mark 的写入路径是官方已废弃的成员**，请明确取舍。
#
# ── 真机验证清单（★ 交给 Lead；判据一律是 `GetSelectedObjectCount2(mark)` 的回读）────
#   ① 分型线：`GetSelectedObjectCount2(1)` ≥1 **且** `(4)` ≥1，然后
#      `insert_parting_line` 不再回 None（★ 现在必回 None —— 函数体只有一句 COM 调用）
#   ② 分型面：同上；再验 `has_parting_line=True` 时**跳过**选择也不报错
#   ③ 包覆：`mark4` ≥1（草图）**且** `mark1` ≥1（面），然后
#      `create_wrap_report` 的 `stage` 不再是 `"selection"`
#   ④ ★ **单独验一次 `ISelectData` 那条路本身**：`CreateSelectData` → `Mark` → `Select4`
#      —— ★ 若它在本机不通（回 None 或 `Select4` 报错），**三个候选全部要退回
#      `_select_com_object` 的 `Select2(mark)` 路线**，请在集成前先跑这一条。
# ═══════════════════════════════════════════════════════════════════════════