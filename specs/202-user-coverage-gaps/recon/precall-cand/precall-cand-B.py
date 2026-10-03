"""★ 候选：part_sweep / part_loft / part_axis / part_wrap 四条工具的 `pre_call`（可直接粘进各自 ToolSpec）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（候选实现产物；★ 未接入任何 spec，★ 仓内其它文件零改动）
# 文件:   specs/202-user-coverage-gaps/recon/precall-cand/precall-cand-B.py —— 本文件
# 定位:   `preselect-family-b.md` L113–L116 判定的「真危险」四条（batch47/48/49/50）补 `pre_call`。
#         机制前提 = `mcp-server/tool_registry.py::make_tool_function._impl` 的顺序（L507/510/513）
#         `kwargs[inject]=resolver(params)` → `spec.pre_call(params)` → `derived_args` → 调目标函数；
#         ★ 而 `RESOLVERS["model"] → connect_solidworks()` **会清空选区**
#         （证据 `output/selection-lifetime-evidence.json`，由 `tool_specs_batch74.py` L90–L102 引述）
#         ⇒ ★ 唯一能让"选择"活到第 4 步的地方就是 `pre_call`。
# 官方依据（★ 本文件里每个 mark 的出处，逐条可复核）:
#   · loft    `C:\swapi\types\IFeatureManager\InsertProtrusionBlend2.md` §Remarks
#             「Set the mark for: 1 = profile / 2 = guide curve / 4 = centerline / 8 = start tangency vector」
#             ＋ 例子 `C:\swapi\examples\Insert_Protrusion_Blend_Example_VB.md` L75–L81（★ 调用序）：
#             `SelectByID2("Sketch1","SKETCH",x,y,0,False,1,Nothing,0)` + `SelectByID2("Sketch2",...,True,1,...)`
#   · sweep   `C:\swapi\types\IFeatureManager\InsertProtrusionSwept3.md` §Remarks（★ 该族已被 Obsolete，
#             mark 表仍逐字适用）:「1 = Profile selection / 2 = Guide curve / 4 = Sweep path」
#             ＋ 例子 `C:\swapi\examples\Select_Multiple_Paths_for_Sweep_Path_Example_VB.md` L57–L60：
#             轮廓 `SelectByID2("Sketch1","SKETCH",x,y,z,False,**1**,…)`；路径 `Line1@Sketch2` mark=**4**
#   · wrap    `C:\swapi\types\IFeatureManager\InsertWrapFeature2.md` §Remarks：面 **1** · 拔模方向 **2** ·
#             草图 **4**；＋ 例子 `C:\swapi\examples\Create_Wrap_Feature_on_Multiple_Faces_Example_VB.md` L53–L59：
#             `SelectByID2("Sketch30","SKETCH",0,0,0,False,**4**,…)` ＋ 逐个 `SelectByRay(...,True,**1**,…)`
#   · axis    `C:\swapi\types\IModelDoc2\InsertAxis2.md` —— ★★ **整页没有 `## Remarks`**（唯一非空段落是
#             `## Examples`）⇒ ★ 官方**没给 mark 表**；★ 但同页 Examples 指向的例子
#             `C:\swapi\examples\Create_Revolve_Features_Example_VB.md` L29–L31 逐字是
#             `SelectByID2("Right Plane","PLANE",0,0,0,True,**0**,…)` ×2 后 `Model.InsertAxis2 True`
#             ⇒ ★ mark **0** 有**官方例子**背书（不是从 Remarks 推的）。
# 选法依据（★ 为什么不用仓内最常见的 `resolve_selection`）:
#   · `scripts/sw_part.py:106 _select_by_id` 包装 `SelectByID2(name, type, 0,0,0, append, mark, callout, 0)`
#   · ★ `Select4` **没有 mark 参数**（只有 `Append, Callout`）⇒ 走对象选择的 mark 会丢；
#     `scripts/sw_part.py:294 _select_com_object` 的 `Select4` 回退分支就是这一害处
#     （★ `tools/prove_sweep_surface.py` L105–L119 已把这条写成真机教训：「若 Select2 失败而 Select4 成功
#       ⇒ 那一次没有 mark」⇒ 真机形态 `{1:1, 4:0}`）。
#   · ★ 而 `SelectByID2` 的 mark **真会落到对应桶** —— 本仓真机证据 `output/mark-semantics.json`：
#     `mark_arg=0→桶0` · `mark_arg=1→桶1` · `mark_arg=2→桶2` · `"mark_lands": true`（SW 2026 SP4.1）。
#   · 面没有名字（事实 32）⇒ 带 mark 的面只能走 `IModelDocExtension::SelectByRay`
#     （★ `C:\swapi\types\IModelDocExtension\SelectByRay.md` 的签名第 10 个形参就是 `Mark`；
#       ★ `SelectByID2.md` L93 官方明说「Otherwise, you can call SelectByRay」）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ **未在本机实测**（候选文件，★ 不许跑 SolidWorks）—— 铁律 2。
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

__all__ = [
    "PRE_PART_SWEEP", "PRE_PART_LOFT", "PRE_PART_AXIS", "PRE_PART_WRAP",
    "_clear", "_count", "_select_named", "_select_face_at",
]


# ═══════════════════════════════════════════════════════════════════════════
# 内部底座（★ 抄 `tool_specs_batch74.py::_select_faces_for` 的形状：
#    按对象遍历 → 选 → **回读计数** → 不够就抛；★ 判据永远不用 SelectByID2/Select4 的 bool）
# ═══════════════════════════════════════════════════════════════════════════

#: ★ `swSelectType_e.swSelFACES = 2`（★ `scripts/sw_hole_features.py:1062` 已定的仓库常量；
#:   ★ 官方包覆例子 `Create_Wrap_Feature_on_Multiple_Faces_Example_VB.md` L54 的 TypeWanted 也是 `2` ✓ 两源一致）
_SW_SEL_FACES = 2

#: ★ 射线半径（米）—— ★ 照 `scripts/sw_hole_features.py:1119` 的既有用值 `1e-4`
_RAY_RADIUS_M = 1e-4


def _model():
    """★ 取**注册器那个**活动文档（★ 与 `tool_specs_batch74.py:115` 完全同源）。

    ★ 为什么不用 `connect_solidworks()` 直接连：`pre_call` 跑在 `RESOLVERS["model"]` **之后**
      （`tool_registry.py:507` → `:513`），★ 再自己连一次会**第二次清选区** ⇒ 把前一步的选择抹掉。
    """
    import register_capabilities as _rc

    model = _rc.RESOLVERS["model"](None)
    if model is None:
        raise RuntimeError("没有活动文档 —— 请先打开一个零件")
    return model


def _clear(model) -> None:
    """★ 清选区。★ 必须在 `pre_call` 里做：目标函数（如 `sw_part._select_sketch_feature_by_name`）
    自带 `append=False`，★ 而残留选区会让"追加"语义失真（★ 事实 383 第 ② 条：`append=False` 调两次只剩第二次）。"""
    from scripts.sw_connect import get_com_member

    try:
        get_com_member(model, "ClearSelection2", True)
    except Exception:                                              # noqa: BLE001
        pass


def _count(model, mark: int) -> int:
    """★ **回读**某个 mark 桶里的选中数（`ISelectionMgr::GetSelectedObjectCount2(mark)`）。

    ★ 这是本文件唯一的判据（★ 事实 8：`Select4` / `SelectByID2` 的 bool 返回值不可信）。
    """
    from scripts.sw_connect import get_com_member

    try:
        return int(get_com_member(get_com_member(model, "SelectionManager"),
                                  "GetSelectedObjectCount2", mark) or 0)
    except Exception:                                              # noqa: BLE001
        return -1


def _select_named(model, name: str, kind: str, mark: int, append: bool) -> bool:
    """★ 按**名字**选一个实体并带上 mark —— 走官方 `SelectByID2`（★ 经 `sw_part._select_by_id`）。

    ★ 为什么"名字"这条路对**特征**成立：`SelectByID2` 是本仓唯一能同时给出**名字**与**mark**的入口
      （事实 32：「按名字选只对特征成立」）⇒ ★ 草图 / 基准面 / 参考轴 / 参考曲线都有名字 ✓。
    ★ 语言无关：草图名与基准面名随 UI 语言变（事实 9 / 158）⇒ 先过仓库既有的候选名表。
    ★ 返回值**不作为判据**（调用方一律回读 `_count`）。
    """
    from scripts.sw_part import _select_by_id
    from scripts.sw_connect import get_com_member

    if kind == "SKETCH":
        from scripts.sw_part import _get_sketch_name_candidates as _cands
    elif kind == "PLANE":
        from scripts.sw_part import _get_plane_name_candidates as _cands
    else:
        def _cands(n):
            return [n]

    ext = get_com_member(model, "Extension")
    for cand in _cands(str(name)):
        try:
            if _select_by_id(ext, cand, kind, append=append, mark=mark):
                return True
        except Exception:                                          # noqa: BLE001
            continue
    return False


def _select_face_at(model, selector: str, mark: int, append: bool) -> bool:
    """★ 按**声明式面选择器**选一个面并带上 mark —— 走官方 `IModelDocExtension::SelectByRay`。

    ★ 形状逐字照 `scripts/sw_hole_features.py:1103–1129`（★ 本仓唯一已跑通的 `SelectByRay` 用法）：
      ① 用 `sw_simulation.resolve_face_selector` 把选择器解析成**面上一点（米）** ——
      ★ **坐标只在能力层内部算**，★ 对外参数只有选择器（规则 3 的书面例外，
         与 `sw_hole_features` / `sw_simulation.select_face_by_selector_report` 同一处理）；
      ② 从该点**沿外法向反向抬起**再打射线 ⇒ 保证射线从体外进来；
      ③ `SelectByRay(x,y,z, dx,dy,dz, 1e-4, swSelFACES=2, Append, Mark, 0)`。

    :param selector: `+x`/`-x`/`+y`/`-y`/`+z`/`-z`（★ `resolve_face_selector` 的合法值）
    :param mark:     官方要求的 mark（★ 包覆的面是 **1**）
    """
    from scripts.sw_connect import get_com_member
    from scripts.sw_simulation import resolve_face_selector

    pt = resolve_face_selector(model, selector)
    if pt is None:
        raise RuntimeError(
            "面选择器 %r 解析不了（★ 合法值：+x/-x/+y/-y/+z/-z；★ 而它**只对轴对齐的实体可靠** —— "
            "斜面/曲面上包围盒那面中心未必落在表面上，此时回读计数会是 0）" % (selector,))
    x, y, z = float(pt[0]), float(pt[1]), float(pt[2])           #: ★ 已是**米**
    ext = get_com_member(model, "Extension")
    ok = get_com_member(ext, "SelectByRay",
                        x, y, z,                # 起点：面上那点（沿 -法向 抬 1 mm）
                        0.0, 0.0, -1.0,         # 方向：从上往下打（★ 覆盖 ±z 那一面）
                        _RAY_RADIUS_M, _SW_SEL_FACES, bool(append), int(mark), 0)
    if not ok:
        # ↑ 射线没打中：退回按该方向的反向再试一次（覆盖轴对齐零件的任意一面）
        ok = get_com_member(ext, "SelectByRay",
                            x, y, z,
                            0.0, 0.0, 1.0,
                            _RAY_RADIUS_M, _SW_SEL_FACES, bool(append), int(mark), 0)
    return bool(ok)


# ═══════════════════════════════════════════════════════════════════════════
# ① solidworks_part_sweep   （mcp-server/tool_specs_batch48.py · sw_sweep.create_sweep_report）
# ═══════════════════════════════════════════════════════════════════════════
def _pre_part_sweep(params):                                       # noqa: ANN001
    """★ 扫描：**轮廓 mark=1** → **路径 mark=4**（→ 可选 **引导线 mark=2**），逐个按官方顺序。

    官方依据:
      · `C:\\swapi\\types\\IFeatureManager\\InsertProtrusionSwept3.md` §Remarks 逐字：
        「Use IModelDocExtension::SelectByID2 to select the profile and sweep curves. The mark for:
        **1 = Profile selection / 2 = Guide curve selection, if provided / 4 = Sweep path**」
        （★ 仓库走的是现代入口 `CreateDefinition(swFmSweep=17)`，★ 而这一族虽被标 Obsolete，
          ★ **mark 表是同一条语义**、★ 且仓内 `scripts/sw_sweep.py` L14–L21 引的官方专文
          `…\\Sweep Features and SweepFeatureData Objects.md` 给的是同一张表）
      · 例子 `C:\\swapi\\examples\\Select_Multiple_Paths_for_Sweep_Path_Example_VB.md` L57–L60（★ 调用序）：
        轮廓 `SelectByID2("Sketch1","SKETCH",x,y,z,False, 1, Nothing, 0)`
        路径 `SelectByID2("Line1@Sketch2","EXTSKETCHSEGMENT",x,y,z,True, 4, Nothing, 0)`
    ★ 目标函数 `scripts/sw_sweep.py:77–86` 回读 `GetSelectedObjectCount2` 的 **1 / 4 / 2** 三个桶，
      ★ 本 pre_call 的判据与它**逐字对齐**（★ 不引入它不认的 mark）。
    ★ 官方硬约束（本 pre_call **管不了**、如实写在报错里）：**路径的起点必须落在轮廓所在平面上**。
    """
    model = _model()
    _clear(model)
    picked = {}
    #: ① 轮廓（mark 1，★ 第一个 ⇒ append=False，★ 官方例子第 75 行的 `False`）
    for sel in _as_list(getattr(params, "profile_sketch", None)):
        if _select_named(model, sel, "SKETCH", 1, append=bool(picked)):
            picked["profile"] = sel
    #: ② 路径（mark 4，★ 追加）
    for sel in _as_list(getattr(params, "path_sketch", None)):
        if _select_named(model, sel, "SKETCH", 4, append=True):
            picked["path"] = sel
    #: ③ 引导线（mark 2，★ **官方标 optional** ⇒ 缺省不选，★ 不算失败）
    guides = _as_list(getattr(params, "guide_sketch", None))
    if guides:
        for sel in guides:
            if _select_named(model, sel, "SKETCH", 2, append=True):
                picked["guide"] = sel
    #: ★★ 回读判据（★ 不用任何返回值 —— 事实 8）
    m1, m4 = _count(model, 1), _count(model, 4)
    if m1 < 1 or m4 < 1:
        raise RuntimeError(
            "★ 扫描前置未成立：mark=1（轮廓）=%d · mark=4（路径）=%d（★ 官方各要求 ≥1）。"
            "已选上：%r。★ 提示：路径**必须是草图**（官方例子用 `Line1@Sketch2` 这种草图线）；"
            "★ 且**路径起点必须落在轮廓所在平面上**，★ 否则即使选上也不会建出来。"
            % (m1, m4, picked))
    return {"picked": picked, "mark1": m1, "mark4": m4, "mark2": _count(model, 2)}


# ═══════════════════════════════════════════════════════════════════════════
# ② solidworks_part_loft    （mcp-server/tool_specs_batch47.py · sw_loft.create_loft_report）
# ═══════════════════════════════════════════════════════════════════════════
def _pre_part_loft(params):                                        # noqa: ANN001
    """★ 放样：**全部轮廓 mark=1**，★ 且**按给定顺序**（官方明写顺序决定放样方向）。

    官方依据:
      · `C:\\swapi\\types\\IFeatureManager\\InsertProtrusionBlend2.md` §Remarks 逐字：
        「Set the mark for: **1 = profile selections** / 2 = guide curve selections / 4 = centerline selection」
        ＋「you must select the profiles **in an order consistent with the desired direction of the loft**」
        ＋「**Selection of guide curves and centerline is optional**」
      · 例子 `C:\\swapi\\examples\\Insert_Protrusion_Blend_Example_VB.md` L75–L81（★ 调用序）：
        `Sketch1` mark=1 `Append=False` → `Sketch2` mark=1 `Append=True` → 4 条引导线 → `Curve5` mark=4（中心线）
    ★ 判据与目标函数 `scripts/sw_loft.py:76–82` 对齐：★ 它要 **mark=1 的计数 ≥ 2**，★ 本 pre_call 同。
    ⚠ **未证实**（如实记）：官方例子给 4 条引导线的 mark 是 **4098 / 8194 / 12290 / 16386**
      （= 4096·k + 2 的高位组合），★ 而 §Remarks 那一栏写的是 **2**；★ 我**没查到**那个高位位的官方定义
      ⇒ ★ 本候选**只按 §Remarks 的 2**（★ 不猜），★ 并把差异写在这里。
    """
    model = _model()
    _clear(model)
    picked = []
    #: 轮廓（★ 全是 mark=1；★ append=(i>0) ⇒ 第一个 False、其余 True，★ 与官方例子 L75/76 逐位一致）
    for i, sel in enumerate(_as_list(getattr(params, "profile_sketches", None))):
        if _select_named(model, sel, "SKETCH", 1, append=(i > 0 or bool(picked))):
            picked.append(sel)
    #: 引导线（mark 2）· 中心线（mark 4）—— ★ 官方标 optional，★ 缺省不选、★ 不算失败
    for sel in _as_list(getattr(params, "guide_sketches", None)):
        _select_named(model, sel, "SKETCH", 2, append=True)
    center = getattr(params, "centerline_sketch", None)
    if center:
        _select_named(model, str(center), "SKETCH", 4, append=True)
    #: ★★ 回读判据（★ 目标函数 `sw_loft.create_loft_report` 自己卡 `sel_n < 2`，★ 这里前置就卡）
    m1 = _count(model, 1)
    if m1 < 2:
        raise RuntimeError(
            "★ 放样前置未成立：mark=1（轮廓）只选上 %d 个（★ 官方与 `create_loft_report` 都要 **≥2**）。"
            "已选上：%r。★ 提示：轮廓**必须按放样方向给定顺序**，★ 且每个都选中在 **mark=1** 桶里。"
            % (m1, picked))
    return {"picked": picked, "mark1": m1, "mark2": _count(model, 2), "mark4": _count(model, 4)}


# ═══════════════════════════════════════════════════════════════════════════
# ③ solidworks_part_axis    （mcp-server/tool_specs_batch49.py · sw_part.create_axis_report）
# ═══════════════════════════════════════════════════════════════════════════
def _pre_part_axis(params):                                        # noqa: ANN001
    """★ 参考轴：★ **mark = 0**，★ 选中一或多个"建轴源"（**官方没给 mark 表 —— 见下面两条 ⚠**）。

    ⚠⚠ **官方依据的准确边界（铁律 5：查不到就说查不到）**：
      · `C:\\swapi\\types\\IModelDoc2\\InsertAxis2.md` **整页没有 `## Remarks`**
        （★ 只有签名 + 一句 `Returns` + `## Examples` + `## See Also`）
        ⇒ ★★ **官方没有给 `InsertAxis2` 的 mark 表**，★ 下面的 0 **不是从 Remarks 推的**。
      · ★ 但**同页 `## Examples` 指向的例子**给了调用序（★ 官方例子给的是"调用序"，★ 这是它的本职）：
        `C:\\swapi\\examples\\Create_Revolve_Features_Example_VB.md` L29–L31 逐字：
        ```
        SelectByID2("Right Plane", "PLANE", 0,0,0, True, 0, Nothing, swSelectOptionDefault)
        SelectByID2("Top Plane",  "PLANE", 0,0,0, True, 0, Nothing, swSelectOptionDefault)
        Model.InsertAxis2 True
        ```
        ⇒ ★ **mark = 0 有官方例子背书**（两个面各一个交叉出轴），★ 且 **Append = True**。
      · ⚠ **未证实**：圆柱面 / 圆锥面 / 两点 / 线+点 这些**其它**建轴源同样用 mark 0 吗？
        ★ 官方**没写**，★ 我**没试过**（★ 本轮不许跑 SolidWorks）。
        ★ 间接旁证：`tools/prove_sweep_surface.py` L105–L119 记录「`Select4` 走的那一次**没有 mark**」
        ⇒ ★ 不带 mark 的选择落在 **0 号桶**，★ 而目标函数 `sw_part.create_axis_report:1557`
          回读的恰好是 **`GetSelectedObjectCount2(-1)`（全部）**，★ 对 mark 本来就不敏感 ⇒ ★ **这反而降低了风险**。
    """
    model = _model()
    _clear(model)
    picked = []
    #: 形式一：`id:<TYPE>:<Name>` —— ★ 有名字的实体（基准面 / 参考轴 / 草图 / 参考曲线）⇒ 官方 `SelectByID2`
    #:        （★ 这是官方例子的形态，★ 也是唯一能**显式**给 mark 的形态）
    #: 形式二：`index:<n>` —— ★ 按序号取**面 / 边**对象后走 `IEntity.Select4`
    #:        （★ 面没有名字 —— 事实 32；⚠ `Select4` **无 mark 参数** ⇒ 那次落在 0 号桶，
    #:   ★ 而 0 正是本例要用的 mark ⇒ ★ 在 mark 0 这条路上**两者等价** ★ 这也是我把整条设成 mark 0 的原因之一）
    for sel in _as_list(getattr(params, "sources", None)):
        sel = str(sel).strip()
        if not sel:
            continue
        if sel.lower().startswith("id:"):
            _, kind, name = sel.split(":", 2)
            if _select_named(model, name, kind.strip().upper(), 0, append=bool(picked)):
                picked.append(sel)
        elif sel.lower().startswith("index:"):
            if _select_by_index_any(model, sel, append=bool(picked)):
                picked.append(sel)
        else:
            #: 裸名字 ⇒ 猜不出来是面还是边 ⇒ ★ 明确要求调用方写 `id:<TYPE>:<Name>`，★ 不猜
            raise RuntimeError(
                "建轴源 %r 写法不认。★ 合法形式：`id:<TYPE>:<Name>`（TYPE ∈ PLANE/AXIS/SKETCH/…）"
                "或 `index:<n>`（按序号取面/边）。★ 官方例子用的是 `id:PLANE:Front Plane` 这种形态。" % (sel,))
    total = _count(model, -1)
    if total < 1:
        raise RuntimeError(
            "★ 建轴前置未成立：当前选区为空。★ 官方例子给的是**两个基准面**（`id:PLANE:Front Plane` + "
            "`id:PLANE:Top Plane`，★ 两者交叉出一条轴）；★ 官方也接受圆柱面 / 圆锥面 / 两点（★ 但那几条**没给 mark**，"
            "★ 本工具一律按 **mark 0**）。")
    return {"picked": picked, "total": total, "mark0": _count(model, 0)}


# ═══════════════════════════════════════════════════════════════════════════
# ④ solidworks_part_wrap    （mcp-server/tool_specs_batch50.py · sw_wrap.create_wrap_report）
# ═══════════════════════════════════════════════════════════════════════════
def _pre_part_wrap(params):                                        # noqa: ANN001
    """★ 包覆：**草图 mark=4** → **面 mark=1**（→ 可选 **拔模方向 mark=2**），★ 顺序与官方例子逐行一致。

    官方依据:
      · `C:\\swapi\\types\\IFeatureManager\\InsertWrapFeature2.md` §Remarks 逐字（★ 官方把三档排成一列）：
        「One or more **faces** on which to place the wrap feature」→ **1**
        「**Pull direction** entity if Type is Emboss or Engrave」→ **2**
        「2D sketch containing no open contours; 3D sketches are not supported」→ **4**
      · 例子 `C:\\swapi\\examples\\Create_Wrap_Feature_on_Multiple_Faces_Example_VB.md` L53–L59（★ 调用序）：
        `SelectByID2("Sketch30","SKETCH",0,0,0, False, **4**, Nothing, 0)`   ← ★ **草图在前**
        `SelectByRay(..., True, **1**, 0)`  ×6                               ← ★ **面在后，且必须按射线选**
        ★ 而 L52 的注释逐字：「Because the type of wrap feature to create is Scribe,
          **no pull direction entity is selected**」⇒ ★ 拔模方向**只对 Emboss/Engrave 需要**。
    ★ 判据与目标函数 `scripts/sw_wrap.py:93–104` 对齐：★ 它要 **mark4 ≥1 且 mark1 ≥1**。
    ★ 面**必须走 `SelectByRay`**（★ 事实 32：面没有名字；★ 且 `Select4` 无 mark 参数 ⇒ 落不到 1 号桶）。
    """
    model = _model()
    _clear(model)
    picked = {}
    #: ① 草图（mark 4，★ 官方例子第 53 行是 `Append=False`，★ 所以这里必须是 False）
    sketch = getattr(params, "sketch", None)
    if sketch and _select_named(model, sketch, "SKETCH", 4, append=False):
        picked["sketch"] = sketch
    #: ② 面（mark 1，★ **追加**，★ 官方例子第 54–59 行全是 `Append=True`）
    faces = _as_list(getattr(params, "faces", None))
    for fsel in faces:
        _select_face_at(model, fsel, mark=1, append=True)
    #: ③ 拔模方向（mark 2）—— ★ 仅 `wrap_type ∈ {emboss, deboss}` 时官方才要（★ Scribe 不要）
    pull = getattr(params, "pull_direction", None)
    if pull:
        _select_named(model, str(pull), "PLANE", 2, append=True)
    #: ★★ 回读判据
    m4, m1 = _count(model, 4), _count(model, 1)
    if m4 < 1 or m1 < 1:
        raise RuntimeError(
            "★ 包覆前置未成立：mark=4（草图）=%d · mark=1（面）=%d（★ 官方各要求 ≥1）。已选上：%r。"
            "★ 提示：草图**必须是 2D**（官方原话 \"3D sketches are invalid\"）；"
            "★ 面用 `SelectByRay` 选，★ 而它**只对轴对齐的实体可靠**（斜面上射线会落空 ⇒ 回读 0）。"
            % (m4, m1, picked))
    return {"picked": picked, "mark4": m4, "mark1": m1, "mark2": _count(model, 2)}


# ═══════════════════════════════════════════════════════════════════════════
# 两个小助手（★ 不值得单开文件；★ 也都不是新发明 —— 形状照仓内既有写法）
# ═══════════════════════════════════════════════════════════════════════════
def _as_list(value):                                               # noqa: ANN001
    """★ 把 `Param` 的值（`None` / 单串 / 逗号串 / 序列）统一成**去掉空项的字符串列表**。

    ★ 为什么自己收一手：MCP 客户端给 `Param(str)` 的可能是 `"A,B"`、给 `Param(list)` 的可能是 `["A","B"]`，
      ★ 而两条工具的参数类型不一致 ⇒ ★ 在 pre_call 里归一、★ 不要求调用方记住逗号规则。
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        raw = list(value)
    else:
        raw = str(value).split(",")
    return [str(v).strip() for v in raw if str(v).strip()]


def _select_by_index_any(model, selector: str, append: bool) -> bool:
    """★ `index:<n>` —— 按序号取**面**（先试）再试**边**的**对象**，走 `IEntity.Select4`。

    ★ 复用 `scripts/sw_selection_spec.py::select_object`（★ 那里**自己回读计数、0 就抛**）——
      ★ 就是 `tool_specs_batch23/26` 那族 `pre_call` 用的底座。
    ⚠ **`Select4` 没有 mark 参数**（只有 `Append, Callout`）⇒ ★ 那次选择落在 **0 号桶**。
      ★ 在 `part_axis`（mark 0）这条路上**正好够用**；★ 在别的工具上**不够**（★ 会静默丢 mark）。
    ⚠ **未证实**：面与边同序号时"先面后边"这个次序是我定的，★ 官方对 `InsertAxis2` **没写**任何次序要求
      ⇒ ★ 这里只作兜底，★ 不作为首选路径。
    """
    from scripts.sw_selection_spec import select_object, entities_on_body

    for kind in ("FACE", "EDGE"):
        try:
            items = entities_on_body(model, kind)
            idx = int(str(selector).split(":", 1)[1])
            if 0 <= idx < len(items):
                return select_object(model, items[idx], append=append) > 0
        except Exception:                                          # noqa: BLE001
            continue
    return False


#: ★ 可直接贴进 ToolSpec 的三个引用名（★ 名字与各 spec 的语义对齐，★ 便于 grep）
PRE_PART_SWEEP = _pre_part_sweep
PRE_PART_LOFT = _pre_part_loft
PRE_PART_AXIS = _pre_part_axis
PRE_PART_WRAP = _pre_part_wrap


# ═══════════════════════════════════════════════════════════════════════════
# 集成说明
# ═══════════════════════════════════════════════════════════════════════════
INTEGRATION_NOTES = r"""
================================================================================
集成说明（四条；★ 每条都标了「要加什么参数」与「pre_call= 怎么写」）
================================================================================

【共同的机制前提】`tool_registry.py::make_tool_function._impl` 的顺序是
  `kwargs[inject] = resolver(params)`（L507）→ `spec.pre_call(params)`（L513）
  → `derived_args`（L514）→ 调目标函数（L524-525）。
★ 而 `RESOLVERS["model"]` 内部 `connect_solidworks()` **会清空选区**
  （`tool_specs_batch74.py` L90–L102 引 `output/selection-lifetime-evidence.json`：
  选完 2 个面 mark1=2 ⇒ 调过 resolver 之后变 mark1=0）
⇒ ★ **这四条的"选择"必须写在 `pre_call` 里**，★ 否则经工具层必然拿不到。
★ 反过来，★ `pre_call` **不需要**再自己连一次 SolidWorks ——
  ★ 必须走 `register_capabilities.RESOLVERS["model"](None)` 拿**同一个** model（★ 见 `_model()`）。

--------------------------------------------------------------------------------
① solidworks_part_sweep —— mcp-server/tool_specs_batch48.py
--------------------------------------------------------------------------------
  现状：params 只有 `cut`(bool)；无 pre_call；无任何 selection 参数。
  要加的参数（★ 都由 pre_call 消费，★ 用 param_alias 挡掉不进目标函数）：
      Param("profile_sketch", str,
            description="轮廓草图名（官方：SelectByID2(..., \"SKETCH\", ..., mark=1)）。"
                        "★ 必须是闭合草图；★ 扫描切除的轮廓也可以是实体轮廓（官方专文另给 1+2048，本候选未实现）。")
      Param("path_sketch", str,
            description="路径草图名（官方 mark=4；官方例子用 \"Line1@Sketch2\" 这种草图线）。"
                        "⚠ 官方硬约束：路径起点必须落在轮廓所在平面上。")
      Param("guide_sketch", str, default="",
            description="引导线草图名（官方 mark=2，★ 官方标 optional；留空就不选）。")
  pre_call 怎么写：
      pre_call=PRE_PART_SWEEP,                       # ★ 或直接 pre_call=_pre_part_sweep
      param_alias={"cut": "cut",
                   "profile_sketch": None, "path_sketch": None, "guide_sketch": None},
      params=[ ...上面三个... , Param("cut", bool, default=False, ...), ],
  ★ `param_alias` 里那三个 `None` 是**必须的**：★ `tool_registry.py:495` 逐字
    「`param_alias` 里 None = 由解析器消费，不进目标函数」⇒ ★ 否则 `create_sweep_report(**kwargs)`
    会收到它不接受的 `profile_sketch=`。
  ★ 形状先例：`mcp-server/tool_specs_batch23.py:68 _consumed()` + `:104 _ALIAS_SEL()`。

--------------------------------------------------------------------------------
② solidworks_part_loft —— mcp-server/tool_specs_batch47.py
--------------------------------------------------------------------------------
  现状：params 只有 `closed`(bool) / `use_selected_profiles`(bool)；无 pre_call。
  要加的参数：
      Param("profile_sketches", list,          # ★ 顺序 = 放样方向（官方明写顺序有意义）
            description="轮廓草图名列表，★ 按放样方向给定顺序；★ 官方要求全部 mark=1、且 ≥2 个。")
      Param("guide_sketches", list, default=[],
            description="引导线草图名列表（官方 mark=2，optional）。")
      Param("centerline_sketch", str, default="",
            description="中心线草图名（官方 mark=4，optional）。")
  pre_call 怎么写：
      pre_call=PRE_PART_LOFT,
      param_alias={"closed": "closed", "use_selected_profiles": "use_selected_profiles",
                   "profile_sketches": None, "guide_sketches": None, "centerline_sketch": None},
  ⚠ 若 `Param` 暂不支持 `list` 类型：★ 退化成 `Param("profile_sketches", str)` 用逗号串
    （★ `_as_list()` 已经两种都收，★ 不用改 pre_call）。
  ★ 现存的 `use_selected_profiles`(bool) 建议**保留**但改成只读语义：★ 传 False 时本 pre_call
    **直接不选、直接抛**（★ `create_loft_report` 自己也会拒），★ 别让它变成"静默跳过后置"。

--------------------------------------------------------------------------------
③ solidworks_part_axis —— mcp-server/tool_specs_batch49.py
--------------------------------------------------------------------------------
  现状：params 只有 `reverse`(bool)；无 pre_call。
  要加的参数：
      Param("sources", list,
            description="建轴源。★ 两种写法："
                        "`id:<TYPE>:<Name>`（TYPE ∈ PLANE/AXIS/SKETCH/…，★ 官方例子的形态）"
                        "或 `index:<n>`（按序号取面/边）。★ 默认给官方例子的那一对基准面。")
      Param("sources", str, default="id:PLANE:Front Plane,id:PLANE:Top Plane", ...)   # ★ 二选一
  pre_call 怎么写：
      pre_call=PRE_PART_AXIS,
      param_alias={"reverse": "reverse", "sources": None},
  ⚠★ **mark 是 0，而官方没给 mark 表** —— 依据只有**官方例子**
    （`Create_Revolve_Features_Example_VB.md` L29–L31 两个 PLANE、Append=True、mark=0）。
    ★ `InsertAxis2.md` **整页无 `## Remarks`** ⇒ ★ 若 Lead 认为"无 Remarks 背书"就不能落 mark，
      ★ 则本条只能标 `stitched`、★ 且 pre_call 应只回读总数（`GetSelectedObjectCount2(-1)`）、
      ★ 不去区分桶 —— ★ 但那样它对 `create_axis_report` 的行为**没有任何改变**
      （★ 目标函数本来就是回读 `-1`），★ 收益只剩"不用调用方手动选"。
  ★ 另一条已知的现状问题（★ 本候选**没有**修，★ 只报）：`scripts/sw_sweep.py:117–120`
    ★ `create_sweep_report` **成功路径没有 `return`**（`except` 里有 return，★ 正常路径直接掉到函数尾）
    ⇒ ★ 即便 pre_call 把前置做对了，★ `solidworks_part_sweep` 也会回 `None`。
    ★★ **这一条必须在集成时单独处理**，★ 否则"pre_call 接上了、工具还是不通"。

--------------------------------------------------------------------------------
④ solidworks_part_wrap —— mcp-server/tool_specs_batch50.py
--------------------------------------------------------------------------------
  现状：params 只有 `wrap_type`(str) / `thickness_mm`(float) / `reverse`(bool)；无 pre_call。
  要加的参数：
      Param("sketch", str,
            description="草图名（官方：SelectByID2(...,\"SKETCH\", ..., mark=4)，★ 且必须是 2D）。")
      Param("faces", list,
            description="要包覆的面，★ 只能是 +x/-x/+y/-y/+z/-z 这类声明式面选择器"
                        "（官方用 SelectByRay 按射线选；★ 只对轴对齐实体可靠）。")
      Param("pull_direction", str, default="",
            description="拔模方向（官方 mark=2）★ 只在 wrap_type ∈ {emboss, deboss} 时需要；留空不选。")
  pre_call 怎么写：
      pre_call=PRE_PART_WRAP,
      param_alias={"wrap_type": "wrap_type", "thickness_mm": "thickness_mm",
                   "reverse": "reverse",
                   "sketch": None, "faces": None, "pull_direction": None},
  ⚠★ **本条是四条里最脆的一条**：官方例子选 6 个面用的是**射线**，★ 而射线起点必须是**面上一点**
    ⇒ ★ 通用做法只能先解析出一个点。★ 本候选用 `sw_simulation.resolve_face_selector`（包围盒那面中心），
    ★ 而它**只对轴对齐的实体可靠** ⇒ ★ 斜面/曲面上会回读 0 ⇒ ★ pre_call **显式抛错**（★ 不静默）。
    ★ 若 Lead 要覆盖斜面：★ 需要一个"面 → 面上一点"的真解（★ 本轮**未证实**，
      ★ 我没查到官方给的 `IFace2` 取点成员怎么用，★ 按铁律 5 不猜）。

================================================================================
置信度
================================================================================
  part_sweep   ★ 高   —— mark 表有 Remarks + 官方例子两处逐字；仓内 `output/mark-semantics.json`
                         已真机证明 `SelectByID2` 的 mark 真会落桶；`tools/prove_feature_toolbar.py`
                         L113–L128 用的就是本候选这条一模一样的调用序。
  part_loft    ★ 高   —— mark 表有 Remarks + 官方例子 L75/L76 两处逐字（两个 Sketch 都 mark=1、
                         Append 依次 False/True）；★ 目标函数自己的门禁（mark1 ≥ 2）也是明写的。
  part_wrap    ★ 中   —— ★ mark 与调用序**高置信**（Remarks + 官方例子 L53–L59 逐字）；
                         ★ 扣分全在**面的定位**：★ 用 `SelectByRay` + 包围盒中心只能覆盖轴对齐实体
                         （★ 官方例子的 6 个面是逐个射线打出来的，★ 不是包围盒能给的）⇒ ★ 曲面/斜面必失败。
  part_axis    ★ 中   —— ★ mark=0 **只有官方例子背书**、★ `InsertAxis2.md` **整页没有 Remarks**
                         （★ 严格说这是"查不到 mark 表"）；★ 圆柱面/圆锥面/两点这几类源**未证实**。
                         ★ 但目标函数回读的是 `-1`（总数）★ 对 mark 不敏感 ⇒ ★ 实际风险比低。
================================================================================
"""
