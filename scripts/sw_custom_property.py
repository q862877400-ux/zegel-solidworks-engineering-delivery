"""文件自定义属性的**读取**（砌墙 W3 / Spec Kit `133`）。

## ★★★ 为什么需要它：本仓库能**写**却**读不回来**
```
· `solidworks_set_custom_properties`（**写**）—— 上游 45 个工具之一，早就在。
· ★ 而能力层里**没有任何"读文件自定义属性"的实现**：
    `sw_pdm` 那一族（`get_custom_property_names_and_values`）要 **PDM 许可证**，不是这条路。
⇒ ★★ **结果：能写不能读** ⇒ 写了属性**没法验**。这正是本模块要补的那个空白。
```

## ★★★ 调用形态由**真机探针**定死（`tools/probe_custom_property_reads.py`，轮 227）
```
① ★★ `model.Extension.CustomPropertyManager` **必须当方法调用**：
     正确：  mgr = model.Extension.CustomPropertyManager("")      ← ★ 传配置名，"" = 默认配置
     错误：  mgr = model.Extension.CustomPropertyManager          ← ★ 拿到的是 **method 对象**，
             之后每个调用都报 `AttributeError: 'function' object has no attribute 'Count'`
   （⚠ 我第一版的探针判据 `not isinstance(v, (str,int,float))` **判不出函数** ⇒ 假阳性，
     所以真机上第一轮全是 AttributeError。★ 判据要用**行为**："它有没有 Count"。）

② ★★ 读值只能用 `Get(name)`（**单返回值**）：
     · `Get(name)` → `System.string`                          ⇒ ★ **实测能读** ✓
     · `Get2..Get6(name, …, out Val, out ResolvedVal)`         ⇒ ★ **实测报 `类型不匹配`**
       （`com_error: (-2147352571, '类型不匹配。')`）—— ★ 与**已知事实 8 / 33** 同一族：
       **pywin32 迟到绑定下 by-ref 出参不通**。⇒ 本模块**一律不用 `Get2+`**。
    ★★★★ **2026-10-04（接手轮）更正上面这条结论的一半**（★ 处置阶段 2 · T1）——
      ★ **哪一半仍成立**：★ **不包 `VARIANT(VT_BYREF | …)` 的出参，确实报 `类型不匹配`** ✓
      ★★ **哪一半被推翻**：★ **`Get2+` 不是"不通"** —— ★ 包对了就能用 ✓
      ★ **而官方那半也变了**：★ `Get` / `Get2` / `Get3` / `Get4` / `Get5` **现在全标 `Obsolete`**、
        ★★ **只有 `Get6` 是现行的** ⇒ ★ **继续用 `Get` 就是用一个废弃成员** ✓
      ★★ **现成的反例就在同一个仓**：★ `scripts/sw_document_data.py::read_custom_property`
        用 `VARIANT(VT_BYREF | VT_BSTR, "")` 包四个出参、★ 再调 `Get6` ⇒
        ★★★ **而它**工作**（★ 轮 78 真机验过：`raw` 逐条读回 `alpha` / `beta` / `gamma`）** ✓
      ★★★ **⇒ 本模块现在也走 `_read_value_via_get6`**（★ 包法与那条一致）✓
      ★★★★ **可复用判据**：★★★ **「by-ref 出参不通」这个结论**要带包法才有意义** ——
        ★ 不包 `VT_BYREF` 必然报错、★ **包了就能用**；★ 而**「废弃」是另一件事**（★ 不因包法改变）✓

③ `Count {get;}` · `GetNames()` · `GetType2(name)` 都实测可用；
   `GetType2` 回 `swCustomInfoType_e`（实测 30 = `swCustomInfoText` = `VT_LPSTR`）。

④ 真机决定性用例：`Add3(名, swCustomInfoTypeText, 值, True)` 写入后
   `Count` 28 → 29，且 `Get(名)` **读回了写入的值** ✓
   ⇒ ★ 但本模块**只读**（不做写；写已由上游工具承担）。
```

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植）
# 文件:   scripts/sw_custom_property.py
# 定位:   砌墙 W3（Spec Kit `133`）的能力层：读文件自定义属性（**不需要 PDM**）。
# 官方依据: `IModelDocExtension.CustomPropertyManager` · `ICustomPropertyManager.Get` /
#           `GetNames` /
#          `Count` / `GetType2`；官方示例 `C:\\swapi\\examples\\Add_and_Get_Custom_Properties_Example_VB.md`
#          （那里 `swCustPropMgr.Get(vName)` 被当**单返回值**用，与实测一致）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 真机验证状态见 `output/custom-property-evidence.json`（铁律 2）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from typing import Any

from sw_connect import get_com_member

__all__ = [
    "SW_CUSTOM_INFO_TYPES",
    "custom_property_manager",
    "custom_property_names",
    "custom_property_count",
    "custom_property",
    "custom_properties",
]

#: `swCustomInfoType_e`（官方示例 `Get_Custom_Properties_Example_VB` 逐字列出）
SW_CUSTOM_INFO_TYPES = {
    0: "unknown",
    3: "number",  #: VT_I4
    11: "yes_or_no",  #: VT_BOOL
    30: "text",  #: VT_LPSTR
    64: "date",  #: VT_FILETIME
}


def custom_property_manager(model, config_name: str = ""):
    """取 `ICustomPropertyManager`。

    ★★ **必须把它当方法调用**（传配置名；`""` = 默认配置）——
      实测：当属性取会拿到一个 **method 对象**，之后每个调用都报
      `AttributeError: 'function' object has no attribute 'Count'`。
    ★ 判据用**行为**（它有没有 `Count`），不用类型 —— 见模块头的 ①。
    """
    if model is None:
        raise ValueError("model 为 None")
    ext = get_com_member(model, "Extension")
    if ext is None:
        raise RuntimeError("取不到 model.Extension —— 无法读自定义属性")
    #: ★★ 2026-10-03（轮 470）**修正一次过度替换（同族第 4 处）** ——
    #:   官方 `IModelDocExtension.CustomPropertyManager` 是**方法**（★ 收一个配置名参数、
    #: 返回 `ICustomPropertyManager`）⇒ ★ 这里**必须**走 `get_com_member`（★ 它会**调用*
    #: *）
    #:   ★ 判据：**返回值被使用**（`mgr`）⇒ 那是**取/调**，不是"写属性"。
    mgr = get_com_member(ext, "CustomPropertyManager", str(config_name))
    if mgr is None or not hasattr(mgr, "Count"):
        #: 兜底：个别环境下把它当属性取反而可用 ⇒ 再试一次（但判据仍是行为）
        alt = get_com_member(ext, "CustomPropertyManager")
        if hasattr(alt, "Count"):
            return alt
        raise RuntimeError(
            "取不到 CustomPropertyManager（当方法调用与当属性取都不像管理器；"
            "★ 判据是它有没有 Count）"
        )
    return mgr


def custom_property_count(model, config_name: str = "") -> int:
    """自定义属性**条数**（`ICustomPropertyManager.Count`）。"""
    return int(get_com_member(custom_property_manager(model, config_name), "Count"))


def custom_property_names(model, config_name: str = "") -> list[str]:
    """自定义属性**名字清单**（`GetNames`）。空 ⇒ 回空表。"""
    raw = get_com_member(custom_property_manager(model, config_name), "GetNames")
    if raw is None:
        return []
    try:
        return [str(x) for x in raw]
    except TypeError:
        return [str(raw)]


def _read_value_via_get6(mgr, name: str) -> str:
    """★ 用**现行的** `ICustomPropertyManager.Get6` 读一个属性值（★ 处置阶段 2 · T1）✓

    ★★★★ 2026-10-04（接手轮）**换掉 `Get`（官方标 Obsolete）** ——
      ★ **官方逐字**（★ `C:\\swapi\\types\\ICustomPropertyManager\\Get.md`）：
        ★ `System.string Get(System.string FieldName)` ⇒ ★ 而它**在**废弃名单里 ✓
      ★★ **整族只有 `Get6` 未废弃**：★ `Get` / `Get2` / `Get3` / `Get4` / `Get5` **全标 Obsolete**；
        ★★★ `Get6` 逐字 ⇒ `int Get6(string FieldName, bool UseCached, out string ValOut,
          out string ResolvedValOut, out bool WasResolved, out bool IsLinked)` ✓
    ★★★★ **而本模块那段"不能用 `Get2+`"的结论**要**更正**（★ 补正而不删除）——
      ★ 它当时实测报 `类型不匹配`（`com_error: -2147352571`）⇒ ★★ **真因不是"by-ref 不通"**、
      ★★★ **而是**出参没有用 `VARIANT(VT_BYREF | …)` 包**** ✓
      ★ **现成的反例就在同一个仓**：`scripts/sw_document_data.py::read_custom_property`
        （★ L410-414）**用 `VARIANT(VT_BYREF | VT_BSTR, "")` 包了四个出参、
        再调 `Get6`** ⇒ ★★ **而它**工作**（★ 轮 78 真机验过：`raw` 逐条读回）** ✓
      ★★★ **⇒ 可复用判据**：★★★ **"by-ref 出参不通"这个结论要**带包法**才有意义** ——
        ★ **不包 `VT_BYREF` 必然报"类型不匹配"**、★ 而**包了就能用** ✓
    """
    import pythoncom  # noqa: PLC0415
    from win32com.client import VARIANT  # noqa: PLC0415

    val = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")
    resolved = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BSTR, "")
    was_resolved = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
    is_linked = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_BOOL, False)
    #: ★ 官方：`Get6` 回 `swCustomInfoGetResult_e`（★ **`status != 1` ⇒ 存在**）
    mgr.Get6(str(name), False, val, resolved, was_resolved, is_linked)
    return str(val.value or "")


def custom_property(model, name: str, config_name: str = "") -> dict[str, Any]:
    """读**一个**属性的值 + 类型 + 是否可编辑。

    ★★ 值走 `Get6(name, False, …)`（★ **现行的那个** —— 官方已把 `Get`~`Get5` 全标废弃）✓
      ★★★ **而出参必须用 `VARIANT(VT_BYREF | …)` 包** —— ★ 不包就报 `类型不匹配`（见下）✓
    """
    if not str(name or "").strip():
        raise ValueError("name 不能为空")
    mgr = custom_property_manager(model, config_name)
    value = _read_value_via_get6(mgr, name)
    try:
        tcode = int(get_com_member(mgr, "GetType2", str(name)))
    except Exception:  # noqa: BLE001
        tcode = -1
    editable = None
    try:
        editable = bool(get_com_member(mgr, "IsCustomPropertyEditable", str(name)))
    except Exception:  # noqa: BLE001
        editable = None
    return {
        "name": str(name),
        "value": "" if value is None else str(value),
        "type_code": tcode,
        "type": SW_CUSTOM_INFO_TYPES.get(tcode, "unknown(%d)" % tcode),
        "editable": editable,
    }


def custom_properties(model, config_name: str = "") -> dict[str, Any]:
    """读**全部**自定义属性：`{count, config, properties: [{name,value,type,…}, …]}`。

    ★ 逐个走 `Get`（单返回值）；名字顺序照 `GetNames` 给的顺序（不重排）。
    """
    mgr = custom_property_manager(model, config_name)
    raw = get_com_member(mgr, "GetNames")
    names: list[str] = []
    if raw is not None:
        try:
            names = [str(x) for x in raw]
        except TypeError:
            names = [str(raw)]
    items = []
    for n in names:
        #: ★★ 同上：★ 换现行的 `Get6`（★ 出参用 `VT_BYREF` 包）✓
        value = _read_value_via_get6(mgr, n)
        try:
            tcode = int(get_com_member(mgr, "GetType2", n))
        except Exception:  # noqa: BLE001
            tcode = -1
        items.append(
            {
                "name": n,
                "value": "" if value is None else str(value),
                "type_code": tcode,
                "type": SW_CUSTOM_INFO_TYPES.get(tcode, "unknown(%d)" % tcode),
            }
        )
    return {
        "config": str(config_name),
        "count_reported": int(get_com_member(mgr, "Count")),
        "count_read": len(items),
        "properties": items,
    }
