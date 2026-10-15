

# ── 24h 计划 段 5「修地基」**D2**（Spec Kit `149`）：**画几何前必须有活动草图** ──────────
# ★★★ 依据（★ 本项目自己的记载，**不是发明**）：
#   · `specs/135-*` 的 `converge.md` L76：「L2 | ★ **「不 start 就画几何」没有机器守卫** |
#     实测是**静默的**；**要加守卫应在能力层/工具层** ⇒ ★ **另开特性（不顺手改）**」
#     ⇒ ★ 本段就是**那个「另开的特性」**。
#   · 同一份的 `checklist.md` L15 记着一条纪律：「★ 用实测记录（**静默**），
#     ★ **不假称它该抛错**」—— ★ 因为**官方文档没说**"不先 start 会怎样"。
#   ⇒ ★★★ **所以本守卫的定性是**：★ **本项目的工程选择**（防静默失败），
#     ★ **不是**"官方要求抛错"**。★ 报错信息里要把这一点说清。
#
# ⚠ 覆盖范围：**画几何**的那些函数（不是 `start_sketch` / `end_sketch` 自己）。
#   而**为什么不逐个改函数体**：★ 8 个函数各加一行 = 8 处改动、
#   ★ 而**统一包装一处搞定** —— ★ 且**新增画几何函数时容易被漏掉**，
#   所以下面**显式列名**（★ 列名本身就是「哪些函数算画几何」的记录）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_part.py —— 本段
# 定位:   修地基 D2：给"画几何"的函数统一加"必须先有活动草图"的守卫。
# 官方依据: `IModelDoc2.GetActiveSketch2`（★ 读活动草图；★ 只用于**判在不在**）·
#          `ISketchManager.CreateLine` 等（★ 那些是被守卫的函数）
#          ⚠ **官方文档没说**"不先 start 会怎样" ⇒ ★ 守卫的定性见上。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面这个包装器与它的应用循环
# ─────────────────────────────────────────────────────────────────────────────


def _require_active_sketch(fn):
    """★ 包装一个**画几何**的函数：先确认有活动草图，没有就**报错**（而不是静默）。

    ★★ 定性：★ **本项目的工程选择**（防静默失败）—— ★ **不是**官方语义
    （★ 官方文档没说"不先 `sketch_start` 会怎样"；★ `specs/135` 实测为**静默**）。
    """
    import functools

    @functools.wraps(fn)
    def _wrapped(model, *args, **kwargs):
        try:
            sk = get_com_member(model, "GetActiveSketch2")
        except Exception:                                      # noqa: BLE001
            sk = None                                          #: ★ 取不到 ⇒ 走下面的报错（不静默放过）
        if sk is None:
            raise RuntimeError(
                "%s() 被调用时**没有活动草图** ⇒ 画几何会**静默无效**（几何画到不存在的地方）。"
                "★ 先调 `sketch_start(model, plane_name=...)` 再画。"
                "⚠ 本守卫是**本项目的工程选择**（防静默失败）—— "
                "官方文档未规定「不先 start 会怎样」，本项目实测为**静默**（见 specs/135）。"
                % getattr(fn, "__name__", "?")
            )
        return fn(model, *args, **kwargs)

    return _wrapped


#: ★ **哪些函数算"画几何"**（★ 显式列名 —— 它同时是这份名单的记录；
#:   ⚠ 新增画几何函数时**要往这里加**，否则守卫覆盖不到它）。
_SKETCH_DRAWING_FUNCS = (
    "sketch_line", "sketch_rectangle", "sketch_circle", "sketch_arc",
    "sketch_polygon", "sketch_slot", "sketch_spline", "sketch_ellipse",
    "sketch_centerline",
)

for _fn in _SKETCH_DRAWING_FUNCS:
    if _fn in globals():
        globals()[_fn] = _require_active_sketch(globals()[_fn])
