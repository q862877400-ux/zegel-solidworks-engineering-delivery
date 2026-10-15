import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_hole_features.py")
t = P.read_text(encoding="utf-8")

OLD = '''def _hole_standards_data(sw, hole_type_id: int):
    """取 `IHoleStandardsData`（官方 `ISldWorks.GetHoleStandardsData(HoleTypeID)`）。

    :raises RuntimeError: 返回 `None` —— 官方写明**HoleTypeID = 5（`swWzdLegacy`）时返回 `null`**。
    """
    data = get_com_member(sw, "GetHoleStandardsData", int(hole_type_id))
    if data is None:
        raise RuntimeError(
            "ISldWorks.GetHoleStandardsData(%r) 返回 None ⇒ 拿不到 IHoleStandardsData。"
            "官方写明：**HoleTypeID = 5（swWzdLegacy）时返回 null**。" % hole_type_id
        )
    return data'''

NEW = '''def _hole_standards_data(sw, hole_type_id: int, *, initialize: bool = True):
    """取 **并初始化** `IHoleStandardsData`（官方 `ISldWorks.GetHoleStandardsData`）。

    ⚑⚑ **2026-10-01（轮 125）真机查出的行为约束：这个对象必须"先热身"。**
    拿到它之后**直接**调 `GetFastenerTypes` ⇒ **返回 `False`**；
    **先调一次 `GetHoleStandards`** 再调 ⇒ **返回 `True`**。
    实测排除了两种替代解释（同一个未热身对象**再调也不会变 True**；换个标准名也一样）。
    ⇒ ★ 所以本函数默认**顺手调一次 `GetHoleStandards` 当初始化**，
    让后面几个查询成员**不必各自记住这个顺序**。
    ⚠ 官方文档**没有**写这个约束（它只写了各方法自己的前置）。

    :param initialize: 默认 `True`；`False` 时只取不热身（给"只想列标准"的调用方省一次调用）。
    :raises RuntimeError: 返回 `None` —— 官方写明 **HoleTypeID = 5（`swWzdLegacy`）时返回 `null`**。
    """
    data = get_com_member(sw, "GetHoleStandardsData", int(hole_type_id))
    if data is None:
        raise RuntimeError(
            "ISldWorks.GetHoleStandardsData(%r) 返回 None ⇒ 拿不到 IHoleStandardsData。"
            "官方写明：**HoleTypeID = 5（swWzdLegacy）时返回 null**。" % hole_type_id
        )
    if initialize:
        # ⚑ 真机查出的热身步骤（见 docstring）；⚠ 结果丢弃，只是为了让对象进入可用状态
        get_com_member(data, "GetHoleStandards", _out_container(), _out_container())
    return data'''

assert OLD in t, "锚点不符"
t = t.replace(OLD, NEW, 1)
P.write_text(t, encoding="utf-8")
ast.parse(t)
print("  ok _hole_standards_data 已加热身步骤")
