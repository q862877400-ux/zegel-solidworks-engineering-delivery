import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_hole_features.py")
t = P.read_text(encoding="utf-8")

HELPERS = '''

def _hole_standards_data(sw, hole_type_id: int):
    """取 `IHoleStandardsData`（官方 `ISldWorks.GetHoleStandardsData(HoleTypeID)`）。

    :raises RuntimeError: 返回 `None` —— 官方写明**HoleTypeID = 5（`swWzdLegacy`）时返回 `null`**。
    """
    data = get_com_member(sw, "GetHoleStandardsData", int(hole_type_id))
    if data is None:
        raise RuntimeError(
            "ISldWorks.GetHoleStandardsData(%r) 返回 None ⇒ 拿不到 IHoleStandardsData。"
            "官方写明：**HoleTypeID = 5（swWzdLegacy）时返回 null**。" % hole_type_id
        )
    return data


def _pair(ids_v, names_v, what: str):
    """把**两个出参**按位配成 `[{"id", "name"}, …]`。

    ⚠ 长度不一致时**抛** —— 不静默截断、不猜配对（铁律 5）。
    """
    a, b = _as_list(ids_v), _as_list(names_v)
    if len(a) != len(b):
        raise RuntimeError(
            "%s 的两个出参长度不一致（%d vs %d）⇒ 无法按位配对，**不猜**" % (what, len(a), len(b))
        )
    return [{"id": i, "name": str(n)} for i, n in zip(a, b)]

'''
if "_hole_standards_data" not in t.split("# ── 来源")[0]:
    i = t.index("\n\ndef list_hole_standards")
    t = t[:i] + HELPERS + t[i:]
    print("  ok 已加 _hole_standards_data / _pair")
else:
    print("  已有 helpers")

# list_hole_standards 改用共享 helper（避免两份实现）
OLD_BODY = '''    data = get_com_member(sw, "GetHoleStandardsData", int(hole_type_id))
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
    return [{"id": i, "name": str(n)} for i, n in zip(a, b)]'''
NEW_BODY = '''    data = _hole_standards_data(sw, hole_type_id)
    ids, names = _out_container(), _out_container()
    ok = get_com_member(data, "GetHoleStandards", ids, names)
    if not ok:
        raise RuntimeError(
            "IHoleStandardsData.GetHoleStandards 返回 False（失败）—— "
            "两个出参必须是 `VARIANT(VT_BYREF|VT_VARIANT, None)`"
        )
    return _pair(ids, names, "GetHoleStandards")'''
if OLD_BODY in t:
    t = t.replace(OLD_BODY, NEW_BODY, 1)
    print("  ok list_hole_standards 已改用共享 helper")
else:
    print("  ⚠ list_hole_standards 主体锚点不符（继续）")

P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  语法 OK")
