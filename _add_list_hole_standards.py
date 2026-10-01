import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_hole_features.py")
t = P.read_text(encoding="utf-8")

NEW = '''# ── 可用入口：把"孤儿包装"接成能用的 API（2026-10-01 轮 124）──────────
#
# ⚑ **为什么加这一段**：`get_hole_standards` 等 4 个包装**在仓库里没有调用方** ——
#   它们把**出参甩给调用方**，而调用方得自己造 by-ref VARIANT，**没人愿意这么用**。
#   ⇒ 本节提供「**自己造容器、自己读回来**」的高层入口，**调用方只拿结果**。
#
# ★★ **出参的正确传法**（真机裁断，见已知事实 68）：
#     裸 `None` / `VARIANT(VT_BYREF|VT_DISPATCH, None)` 都报「类型不匹配」
#     **`VARIANT(VT_BYREF|VT_VARIANT, None)` 才行**
#
# ★★ **读回来是 `tuple`**（真机量到）：
#     `GetHoleStandards` 的两个出参各是一个 **15 元的 tuple** ——
#     一个是 ID（`(0, 1, 16, …)`）、一个是名称（`('ANSI Inch', 'ANSI Metric', …)`），
#     **一一对应**。⇒ 本节的入口把它们配对成 `[{id, name}, …]`。

def _out_container():
    """造一个**容器出参**（`Object&` / `Variant&` 用）。

    ★ 真机裁断：`VARIANT(VT_BYREF|VT_VARIANT, None)` 是唯一能用的形态
    （裸 `None` 与 `VT_BYREF|VT_DISPATCH` 都报「类型不匹配」，见已知事实 68）。
    """
    import pythoncom
    from win32com.client import VARIANT
    return VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, None)


def _out_value(v):
    """从容器出参里**把值读出来**（真机量到的是 `tuple`）。

    ⚠ 用 `try/except AttributeError` 而不是 `hasattr` —— 后者的属性描述符
    在某些 COM 对象上会**掩盖真实异常**。
    """
    try:
        return v.value
    except AttributeError:
        return None


def _as_list(v):
    """把出参的值规整成 `list`（`None` → `[]`；标量 → 单元素表）。"""
    val = _out_value(v)
    if val is None:
        return []
    if isinstance(val, (list, tuple)):
        return list(val)
    return [val]


def list_hole_standards(sw, hole_type_id: int = 0):
    """列出某类孔向导孔可用的**孔标准**（官方 `ISldWorks.GetHoleStandardsData` +
    `IHoleStandardsData.GetHoleStandards`）。

    :param sw: `ISldWorks` 对象。
    :param hole_type_id: `swWzdGeneralHoleTypes_e`；⚠ 官方写明
        **HoleTypeID = 5（`swWzdLegacy`）时返回 `null`**。
    :returns: `[{"id": int, "name": str}, …]`（两组出参**按位配对**）。
    :raises RuntimeError: 拿不到 `IHoleStandardsData`，或官方返回 `False`。
    """
    data = get_com_member(sw, "GetHoleStandardsData", int(hole_type_id))
    if data is None:
        raise RuntimeError(
            "ISldWorks.GetHoleStandardsData(%r) 返回 None ⇒ 拿不到 IHoleStandardsData。"
            "官方写明：**HoleTypeID = 5（swWzdLegacy）时返回 null**。" % hole_type_id
        )
    ids, names = _out_container(), _out_container()
    ok = get_com_member(data, "GetHoleStandards", ids, names)
    if not ok:
        raise RuntimeError(
            "IHoleStandardsData.GetHoleStandards 返回 False（失败）—— "
            "两个出参必须是 `VARIANT(VT_BYREF|VT_VARIANT, None)`"
        )
    a, b = _as_list(ids), _as_list(names)
    if len(a) != len(b):
        raise RuntimeError(
            "两个出参长度不一致（%d vs %d）⇒ 无法按位配对，**不猜**" % (len(a), len(b))
        )
    return [{"id": i, "name": str(n)} for i, n in zip(a, b)]


'''

ANCHOR = "# ── 来源 ─"
i = t.index(ANCHOR)
if "def list_hole_standards" not in t:
    t = t[:i] + NEW + t[i:]
    P.write_text(t, encoding="utf-8")
    print("  ok 已加 _out_container / _out_value / _as_list / list_hole_standards")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
