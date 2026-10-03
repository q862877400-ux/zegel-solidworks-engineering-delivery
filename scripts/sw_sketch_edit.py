"""
草图编辑操作（Sketch Edit）—— 倒角 / 镜像。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   **本项目自建**（不是从外部项目移植）。
#
# ⚠ 本模块补 `docs/union-gap-triage.md`「**真缺**」档里的两条：
#   `sketch_chamfer` · `sketch_mirror`（`022` 核出该档确实没有这两条实现）。
#
# ## 一、草图标倒角 —— **走非废弃入口**
# 官方文档明写 `IModelDoc2.SketchChamfer` 是 **Obsolete**，被 `ISketchManager::CreateChamfer` 取代。
# ⇒ 本模块用**后继**：
#   反射 : `SketchSegment CreateChamfer(Int32, Double, Double)`
#   swapi: `SketchSegment CreateChamfer(int Type, double Distance, double AngleORdist)`
#   ⚠ **两源签名一致**（3 参，顺序与类型相同）。
#
# ## 二、★★ 枚举值**两源冲突** —— 按铁律 4 取**出厂类型库**
#   `swSketchChamferType_e`：
#   ```
#   成员                                swapi    出厂反射（**采用**）
#   swSketchChamfer_DistanceAngle        0        0
#   swSketchChamfer_DistanceDistance    **-1**   **1**      ← 冲突
#   swSketchChamfer_DistanceEqual        2        2
#   ```
#   ★ **铁律 4：冲突以出厂类型库为准** ⇒ 本模块取 **1**。
#   ⚠ 这是铁律 4 那条规矩的**活例**（此前它更像一条预防性条款）。
#
# ## 三、草图标镜像
#   反射 : `Void SketchMirror()`          （**0 参**，在 `IModelDoc2` 上）
#   swapi: `void SketchMirror()`，并写明**选中标记**：
#          · 要镜像的是**草图线段** ⇒ mark = **1**
#          · 是**中心线**       ⇒ mark = **2**
#   ⚠ 两源一致（都不收参）⇒ **标记是"选中时定的"，不是传参定的**。
#     本模块**不代选**（保持"不猜"），由调用方按上述标记自行选中。
#
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠⚠ **验证等级：`stitched`，且其中一半已确认「到不了」**（2026-10-01 轮 122 真机实测）：
#   ```
#   convert_entities       ⚠ **未实测**（需要选中的边/环/面，本轮未造出前置）
#   create_sketch_chamfer  ❌ **到不了** —— 已确认选中 2 条仍报
#                             `0x80010105「服务器出现意外情况」`（= 事实 47 / 28 的错误码）
#   sketch_mirror          ⚠ **未实测**（需要中心线 mark=2 + 线段 mark=1 的选中标记）
#   ```
#   ⇒ **`CreateChamfer` 在本后端到不了**，属「需要真实指针接口」那一族，**不是参数没调对**。
#   ⚠ 按**事实 53** 停手，不再试别的类型/参数组合。
# ⚠ **验证等级：`stitched`** —— 只有**静态**证据（签名两源互核 + 契约测试），
#   **没有本机运行证据**（未在真机上做过草图倒角/镜像）⇒ **不得标 `verified`**。
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from pathlib import Path as _Path

#: ★★ 本仓库 `scripts/` 的绝对路径（★ 供 `_active_sketch_segment_count` 按顶层路径 import `sw_sketch`）
_REPO_SCRIPTS = _Path(__file__).resolve().parent

try:
    from .sw_connect import get_com_member, mm
except ImportError:      # pragma: no cover - 直接以 scripts/ 为根导入时
    from sw_connect import get_com_member, mm          # type: ignore

#: `swSketchChamferType_e` —— ★ **取出厂反射的值**（与 `C:\swapi` 的 md 在
#: `DistanceDistance` 上冲突：md 写 -1、反射写 1 ⇒ 按铁律 4 用反射）。
SKETCH_CHAMFER_TYPE = {
    "distance_angle": 0,        # swSketchChamfer_DistanceAngle
    "distance_distance": 1,     # swSketchChamfer_DistanceDistance（⚠ md 写 -1，反射写 1，采用 1）
    "distance_equal": 2,        # swSketchChamfer_DistanceEqual
}

#: 官方 `SketchMirror` 的**选中标记**（不是参数，是选实体时的 mark）。
SKETCH_MIRROR_MARK = {
    "segment": 1,       # 要镜像的是草图线段
    "centerline": 2,    # 要镜像的是中心线
}


def create_sketch_chamfer(model, *, chamfer_type: int = SKETCH_CHAMFER_TYPE["distance_angle"],
                          distance_mm: float, angle_or_distance: float = 0.0):
    """在**已选中的两条草图实体**之间做倒角。

    ⚠ **调用前置条件**：官方写明「creates a chamfer **between two selected sketch entities**」
    ⇒ 调用方必须先选中**两条**草图实体（本模块**不代选**，保持"不猜"）。

    :param chamfer_type: `swSketchChamferType_e` 的数值；用 `SKETCH_CHAMFER_TYPE` 里的名字。
    :param distance_mm: 倒角距离，**毫米**（官方 `Distance` 是米，这里换算）。
    :param angle_or_distance: 官方 `AngleORdist` ——
        按 `chamfer_type` 解释：距离-距离时是**第二个距离（毫米）**、
        距离-角度时是**角度（度）**、距离-相等时**被忽略**。
        ⚠ 官方**没写这一参的单位**（取决于类型）⇒ 本模块**不做换算**，按原样传，
        并在 docstring 里点明这一处含糊。
    ⚠⚠ **本函数当前「不可用」（2026-10-01 轮 122 真机实测）** ——
    在**新零件**上画两条相接直线、**已确认选中 2 条**，然后调 `CreateChamfer`：
    ```
    type=2(distance_equal)  ⇒ **pywintypes.com_error: (-2147417851, '服务器出现意外情况')**
    ```
    ★ `0x80010105` **正是已知事实 47 / 28 那个错误码** ——
    即「**pywin32 迟到绑定到不了需要真实指针的接口**」这一**架构性限制**。
    ⚠ **按事实 53 停手**（不再试别的类型/参数组合）；本模块保留该函数作**可复算的证据**。

    :returns: 倒角产生的草图线段（官方返回 `SketchSegment`）。
    :raises RuntimeError: 返回 `None`（最常见原因：**没有选中两条草图实体**）。
    """
    skm = get_com_member(model, "SketchManager")
    if skm is None:
        raise RuntimeError("IModelDoc2.SketchManager 为 None ⇒ 当前不在草图编辑态？")

    #: ⚠⚠⚠ **2026-10-01（轮 164）更正上一段那段定性** —— 它是**误判**。
    #: 上一段说「`0x80010105` ⇒ 架构性限制、到不了」，依据只是**看到异常**。
    #: ★ 轮 164 用 `tools/probe_chamfer_forms.py` **逐类型试 + 回读线段数**：
    #: ```
    #:   type=0（默认 distance_angle）⇒ 段数 2 → 2（**没变**）· 返回 None
    #:   type=1（distance_distance） ⇒ 段数 2 → 2（**没变**）· 返回 None
    #:   type=2（distance_equal）     ⇒ 段数 **2 → 3**（**变了 ✚**）· com_error 0x80010105
    #: ```
    #: ⇒ ★★★ **`type=2` 的倒角其实建成了** —— 那个 `com_error` 是在**取返回值**
    #:   （`SketchSegment`）那一步抛的，**不影响倒角本身**。
    #: ⇒ ★★ 真正的限制是「**拿不到返回对象**」，**不是**「做不了倒角」。
    #: ★ 根因：上一版**只看异常、没回读副作用** —— 与已知事实 94 那一族
    #:   （**不信返回值/异常，回读状态**）同源。
    def _seg_count():
        """回读活动草图的线段数（判「倒角建成了没有」的**状态量**）。"""
        try:
            sk = get_com_member(model, "GetActiveSketch2")
            if sk is None:
                sk = get_com_member(get_com_member(model, "SketchManager"), "ActiveSketch")
            segs = get_com_member(sk, "GetSketchSegments") if sk is not None else None
            return len(list(segs)) if segs else 0
        except Exception:      # noqa: BLE001
            return -1

    before = _seg_count()
    try:
        seg = get_com_member(skm, "CreateChamfer",
                             int(chamfer_type), mm(float(distance_mm)), float(angle_or_distance))
    except Exception as exc:      # noqa: BLE001
        #: ★ **建成但拿不到返回对象** ⇒ 不算失败（回读线段数确认）
        if _seg_count() > before >= 0:
            return None
        raise RuntimeError(
            "ISketchManager.CreateChamfer 失败：%s\n"
            "⚠ 已**回读线段数**（%s → %s）确认**没有建成**。"
            "★ 实测：**只有 `distance_equal`(2) 能成**（type=0/1 段数不变）。"
            "官方前置：**必须选中两条草图实体**。" % (exc, before, _seg_count())
        ) from exc
    if seg is None:
        if _seg_count() > before >= 0:
            return None      #: 同上：建成了，只是没有返回对象
        raise RuntimeError(
            "ISketchManager.CreateChamfer 返回 None 且**线段数没变**（%s → %s）⇒ 没建成。"
            "★ 实测：**只有 `distance_equal`(2) 能成**；官方前置是**选中两条草图实体**。"
            % (before, _seg_count())
        )
    return seg


def _active_sketch_segment_count(model):
    """★ 活动草图的**实体计数**（★ 线段 + 圆弧/圆）；★ 取不到 ⇒ `None`（★ 不许当成 0）。

    ★★ 复用本仓既有读法（★ 不发明）：`sw_sketch.get_lines` / `get_arcs` ——
      ★ 它们各自回**坐标数组**（★ 每条线 12 个 float、每个弧 16 个）⇒ 除以宽度即条数 ✓

    ★★★★★ 2026-10-04（接手轮 · 轮 5）**修掉一个真 bug —— ★ 参数传错了对象**：
      ★ **真机证据**（★ `tools/probe_sketch_edit_pending_evidence.py` ·
      `output/sketch-edit-pending-evidence.json`）：★ 走这条路径取数时
      `segments_before` / `segments_after` **都回 `null`** ⇒
      ★★ 让 `convert_entities` 的**三态判据**保守地判 `ok=false`
      （★ 它的规则逐字是「取不到时不算通过」）——
      ★★★ **而几何其实变了**（★ 同一次真机里，另一条路径读到 **段数 0 → 1**）✓
      ★★★★ **真因**：★ `sw_sketch.get_lines(sketch)` / `get_arcs(sketch)` 的**第一个形参是
        `ISketch` 对象**（★ 它们内部第一句就是 `_require(sketch)`）——
        ★★ **而这里原来把 `model`（`IModelDoc2`）直接传了进去** ⇒ **类型不对 ⇒ 取不到** ✓
      ⇒ **修法**：★ 先从 `ISketchManager.ActiveSketch` 取**活动草图对象**、★ 再传给它 ✓
      ★★★★★ **可复用判据**：★★★ **「取数为 `None`」与「真的没变」是两件事** ——
        ★ 而**三态判据**（★ 变了 True · ★ 没变 False · ★ **量不到 None**）的价值就在这里：
        ★★ **它没把"量不到"骗成 False**，★ 才让这次的真因（**传错对象**）被查出来 ✓
    """
    #: ★★★ 先取**活动草图对象**（★ 而不是把 model 传下去 —— 见 docstring 的修因）✓
    sketch = None
    try:
        sketch = get_com_member(get_com_member(model, "SketchManager"), "ActiveSketch")
    except Exception:                                                     # noqa: BLE001
        sketch = None
    if sketch is None:
        return None                                                       #: ★ 取不到 ⇒ None（★ 不许当成 0）✓
    try:
        import sys as _sys
        if str(_REPO_SCRIPTS) not in _sys.path:
            _sys.path.insert(0, str(_REPO_SCRIPTS))
        from sw_sketch import get_arcs, get_lines                        # noqa: PLC0415
    except Exception:                                                     # noqa: BLE001
        return None
    try:
        n_lines = len(get_lines(sketch) or []) // 12
    except Exception:                                                     # noqa: BLE001
        n_lines = None
    try:
        n_arcs = len(get_arcs(sketch) or []) // 16
    except Exception:                                                     # noqa: BLE001
        n_arcs = None
    if n_lines is None and n_arcs is None:
        return None
    return int((n_lines or 0) + (n_arcs or 0))


def sketch_mirror(model):
    """把**已选中的草图实体**镜像（生成新的镜像实体）。

    ⚠ **调用前置条件（选中标记，官方写明）**：
    * 要镜像的是**草图线段** ⇒ 选中时用 **mark = 1**；
    * 要镜像的是**中心线**   ⇒ 选中时用 **mark = 2**。

    ⇒ 本模块**不代选**；标记是"选中时定的"，不是传参定的（官方签名 **0 参**）。

    :returns: ★★ **2026-10-04 起改为回 dict**（★ 见下）—— 原来是裸 `True`。
    :raises RuntimeError: 无法确认草图处于可镜像状态。

    ★★★★ **2026-10-04（接手轮）修掉一处「doc 承诺了判据、而代码写死 `True`」** ——
      处置 `JUDGE-C_D_E.md` 的 🔴 **#3**（★ `E-3 #1`）—— ★ 裁判逐字：
      「★ doc 承诺的判据（**草图实体计数变化**）在目标函数里**明写着做不到**，
       且函数体**无条件 `return True`**」✓
      ★★ **实测复核**：★ 对外契约（`mcp-server/tool_specs_batch41.py`）逐字写
        「★ The criterion is that the sketch entity count changes.」；
        ★★★ 而本函数原 docstring **自己承认**「回读草图的线段数变化**无法可靠判定**，故返回 `True`」，
        ★ 函数体只有 `model.SketchMirror()` + `return True` ⇒ **全函数没有任何计数回读** ✓
      ★★★ **而那个「无法可靠判定」的说法不成立**：★ 本仓 `sw_sketch` 里**早就有** `get_lines` /
        `get_arcs` / `count_segments`（★ 我在同一批的 E5-1 里刚用过它们读草图几何）⇒
        ★★ **判据是可行的，★ 只是当年没去接** ✓
      ⇒ ★ 修法：★ **接上真实的计数回读**，★ 并按**三态**报（★ 与 E5-1 的做法一致）：
        · ★ **变了** ⇒ `ok=True`；★ **没变** ⇒ `ok=False`；★★ **取不到** ⇒ `ok=None`（★ **不报成功**）✓
    """
    skm = get_com_member(model, "SketchManager")
    if skm is None:
        raise RuntimeError("IModelDoc2.SketchManager 为 None ⇒ 当前不在草图编辑态？")
    sketch = get_com_member(skm, "ActiveSketch")
    if sketch is None:
        raise RuntimeError(
            "ISketchManager.ActiveSketch 为 None ⇒ 当前不在草图编辑态。"
            "官方 SketchMirror 需要先进入草图并选中要镜像的实体"
            "（线段 mark=1 / 中心线 mark=2）。"
        )
    #: ★★★★ 2026-10-04：调用前后各取一次**草图实体计数**（★ 那正是 doc 承诺的判据）✓
    before_segments = _active_sketch_segment_count(model)
    model.SketchMirror()
    after_segments = _active_sketch_segment_count(model)
    delta = None
    if before_segments is not None and after_segments is not None:
        delta = int(after_segments) - int(before_segments)
    #: ★ 三态：★ 变了 True · ★ 没变 False · ★★ 取不到 None（★ 不许把"取不到"当"变了"）
    if delta is None:
        ok = None
    else:
        ok = bool(delta != 0)
    return {
        "ok": ok,
        "op": "sketch_mirror",
        "segments_before": before_segments,
        "segments_after": after_segments,
        "new_segments": delta,
        "verified_by": "★ 草图实体计数变化（★ doc 承诺的判据；★ 取不到时 ok 为 None，不报成功）",
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自建（**不是**从四家外部 MCP 项目移植）。
# 文件:   `scripts/sw_sketch_edit.py` 的 `convert_entities`
# 定位:   补 `docs/union-gap-triage.md`「真缺」档里的 `convert_entities`。
# 官方签名依据（**两源互证**）:
#   ① 出厂反射 `iface_*.txt`：`Boolean SketchUseEdge3(Boolean, Boolean)`（在 `ISketchManager` 上）
#   ② `C:\swapi\types\ISketchManager\SketchUseEdge3.md`：
#        `System.bool SketchUseEdge3(System.bool Chain, System.bool InnerLoops)`
#   ⇒ 两源一致。
# ⚑ **为什么不用 `SketchUseEdge2`**：官方 md 明写 `IModelDoc2.SketchUseEdge2` 是
#   **`Obsolete. Superseded by ISketchManager::SketchUseEdge.`** ⇒ 走**当前入口**。
# ⚠ `ISketchManager.ConvertEntities()`（**零参**）**未废弃**、也能用；
#   本模块取 `SketchUseEdge3`，因为它**两个参数都有官方说明**、语义更明确。
# 覆盖:   本函数
# ⚠ 等级 `stitched`：**无本机运行证据**，不得标 `verified`。
# ─────────────────────────────────────────────────────────────────────
def convert_entities(model, *, chain: bool = True, inner_loops: bool = False):
    """把**已选中的边/环/面/曲线/外部草图轮廓**投影成本草图的实体（转换实体引用）。

    ⚠ **调用前置条件**：官方写明「projects **selected** edges, loops, faces, curves,
    and external sketch contours」⇒ 调用方必须**先选中**要转换的东西并**进入草图**
    （本模块**不代选**，保持"不猜"）。

    :param chain: 官方 `Chain` —— `True` 连**整条链**一起转（同一草图轮廓/链上
        相邻的几何）；`False` 只转**选中的那些**。
    :param inner_loops: 官方 `InnerLoops` —— `True` 把所选面的**内环**也转过来。
    :returns: ★★ **2026-10-04 起改为回 dict**（★ 见下）—— 原来是裸 `True`。
    :raises RuntimeError: 不在草图编辑态，或官方返回 `False`（**不静默成功**）。

    ★★★★ **2026-10-04（接手轮）修掉同一处「doc 承诺了判据、而代码写死 `True`」** ——
      处置 `JUDGE-C_D_E.md` 的 🔴 **#3**（★ `E-3 #2`）—— ★ 裁判逐字：
      「★ 同一条 doc 承诺，★ 这条**同样没有实现**」✓
      ★★ **实测复核**：★ 对外契约逐字「Convert the selected model edges into the active sketch.
        ★ The criterion is that the **sketch entity count changes**.」；
        ★★★ 而本函数原判据**只是 `SketchUseEdge3` 的布尔返回值**（★ 失败才抛）+ 裸 `return True` ⇒
        ★★ **没有任何计数回读** ✓
      ⇒ ★ 修法：★ **接上真实的计数回读**（★ 与 `sketch_mirror` 同一套三态判据）✓
        ★★ **而官方的 `bool` 返回值也保留**（★ 它是**另一层**判据：★ 官方自己说失败会回 False）⇒
        ★★★ **两层都要**（★ 跨种类 ⇒ `and`，★ 与 E5-3/E5-4 那条规则一致）✓
    """
    skm = get_com_member(model, "SketchManager")
    if skm is None:
        raise RuntimeError("IModelDoc2.SketchManager 为 None ⇒ 当前不在草图编辑态？")
    #: ★★★ 调用前后各取一次**草图实体计数**（★ doc 承诺的判据）✓
    before_segments = _active_sketch_segment_count(model)
    got = get_com_member(skm, "SketchUseEdge3", bool(chain), bool(inner_loops))
    if not got:
        raise RuntimeError(
            "ISketchManager.SketchUseEdge3 返回 False（失败）—— 常见原因："
            "**没有选中要转换的边/环/面/曲线**，或当前不在草图编辑态。"
            "官方：它投影的是「**selected** edges, loops, faces, curves, and "
            "external sketch contours」。"
        )
    after_segments = _active_sketch_segment_count(model)
    delta = None
    if before_segments is not None and after_segments is not None:
        delta = int(after_segments) - int(before_segments)
    if delta is None:
        geom_ok = None
    else:
        geom_ok = bool(delta != 0)
    #: ★★ 跨种类 ⇒ `and`：★ 官方布尔（对象类）**且** 计数变化（结构类）✓
    #:   ★ 而"计数取不到"（★ `geom_ok is None`）⇒ **不算通过**（★ 与 sketch_mirror 的三态一致）
    return {
        "ok": bool(bool(got) and geom_ok is True),
        "op": "convert_entities",
        "segments_before": before_segments,
        "segments_after": after_segments,
        "new_segments": delta,
        "official_return": got,
        "verified_by": "★ `SketchUseEdge3` 回非假 **and** 草图实体计数变化"
                       "（★ doc 承诺的判据；★ 取不到时不算通过）",
    }


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自建（**不是**从四家外部 MCP 项目移植）。
# 依据:   ① 出厂类型库反射 `iface_sldworks.txt` / `iface_sketchmanager.txt`：
#            `Void SketchMirror()` · `SketchSegment CreateChamfer(Int32, Double, Double)`
#            · `Boolean SketchUseEdge3(Boolean, Boolean)`
#         ② `C:\swapi\types\ISketchManager\CreateChamfer.md`（参数名与逐条说明）
#         ③ `C:\swapi\types\IModelDoc2\SketchMirror.md`（**选中标记 1 / 2** 的说明）
#         ④ `C:\swapi\types\IModelDoc2\SketchChamfer.md`（明写 **Obsolete**）⇒ 走后继
#         ⑤ `C:\swapi\types\ISketchManager\SketchUseEdge3.md`（`Chain` / `InnerLoops` 的说明）
#         ⑥ `C:\swapi\types\IModelDoc2\SketchUseEdge2.md`（明写 **Obsolete**）⇒ 走后继
#         ⚠ 枚举 `swSketchChamferType_e` **两源冲突**，按铁律 4 取反射（见文件头）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `stitched`：**无本机运行证据**，不得标 `verified`。
# ─────────────────────────────────────────────────────────────────────
