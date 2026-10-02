

# ── 24h 计划 段 6 续（Spec Kit `161`）：**比例成员名的更正（`Scale` → `ScaleRatio`）** ────
# ★★★★★ 2026-10-01（轮 293）**真机抓到三处同类错**（而这是**三源互证**该抓的那种）：
#   · `get_view_scale` / `set_view_scale` 都调 **`Scale`** —— ★ **而 `IView` 上**没有那个成员****
#     （★ 真机表现：`AttributeError: <unknown>.Scale` ⇒ ★ **那是事实 36 的形态**）。
#   · ★★ 而**同文件的 `get_scale_decimal` 的 docstring 早就写着**：
#       「⚑⚑ **更正**：初稿调的是 `GetScaleDecimal`，该成员在 `IView` 上**不存在** ——
#        反射实测的真实成员是 `ScaleDecimal`（零参属性），★ **与同族的 `ScaleRatio` / `UseSheetScale` /
#        `UseParentScale` 同形**」⇒ ★★★ **即：真名 `ScaleRatio` 早就被记下，只是那两个函数没跟着改**。
#   · ★★★ **官方（`C:\swapi\types\IView\ScaleRatio.md`）**：
#       「Gets or sets the scale of the drawing view, **returning the results in ratio format (n:n)**」
#       · **Returns: Array of 2 doubles** · ★「This property and `IView::ScaleDecimal` contain
#       **the same information**, but use the value in a different way」
#     ⇒ ★★ **所以**：① 真名是 **`ScaleRatio`**；② 它回**两个 double**（★ 不是单个 float）。
#
# ★ 判据：★ **`ScaleRatio` 回 2 个数 ⇒ 比例 = 第 1 个 / 第 2 个**；★ 取不到就**如实抛**（★ 原样）。
# ★ ⚠ 本段**只更正成员名与取值形态**，★ **不改行为语义**（★ 不给默认值兜底）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_drawing_view.py —— 本段
# 定位:   段 6 续：把"视图比例"的成员名从**臆造的 `Scale`** 更正为官方真名 `ScaleRatio`。
# 官方依据: `C:\swapi\types\IView\ScaleRatio.md`（★ 真名 + "Array of 2 doubles" + ratio 语义）·
#          ★ 与 `ScaleDecimal` 同族（★ 本文件 docstring 里的那条已存在的更正经）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面 3 个函数
# ─────────────────────────────────────────────────────────────────────────────


def get_view_scale_ratio(view):
    """★ **取视图比例（官方形态：两个数）** —— `IView.ScaleRatio` ⇒ `Array of 2 doubles`。

    ★ 回 `(numerator, denominator)`；★ **取不到就抛**（★ 不兜底 —— 兜底会把"成员名错"盖成"比例是 0"）。
    """
    if view is None:
        raise ValueError("view 为 None")
    raw = call_com_member(view, "ScaleRatio")
    if raw is None:
        raise RuntimeError("IView.ScaleRatio 回 None（★ 本机取不到 ⇒ 别用 0 兜底）")
    try:
        vals = [float(x) for x in raw]
    except TypeError:
        vals = [float(raw)]
    if len(vals) >= 2 and vals[1]:
        return vals[0], vals[1]
    return (vals[0] if vals else None), None


def get_view_scale(view) -> float:
    """★ **取视图比例（便利形态：一个 float）** = `ScaleRatio` 的第 1 个 / 第 2 个。

    ⚑⚑ **2026-10-01 更正**：本函数原调 `Scale` —— ★ **那是臆造的成员名**（`IView` 上没有；
    ★ 真机报 `<unknown>.Scale`）。★ 官方真名是 **`ScaleRatio`**（★ 回两个 double）。
    """
    n, d = get_view_scale_ratio(view)
    if n is None:
        raise RuntimeError("ScaleRatio 不可用 ⇒ 比例取不到")
    return float(n) / float(d) if d else float(n)


def set_view_scale(view, scale: float) -> bool:
    """★ **设视图比例** —— 走官方真名 `IView.ScaleRatio`（★ 按 `n:1` 形态写两个数）。

    ⚑⚑ **2026-10-01 更正**：本函数原调 `Scale`（★ 同样是不存在的成员名）。
    """
    if view is None:
        raise ValueError("view 为 None")
    s = float(scale)
    get_com_member(view, "ScaleRatio", (s, 1.0))
    return True
