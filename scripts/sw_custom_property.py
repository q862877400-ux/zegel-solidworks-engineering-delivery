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
# 官方依据: `IModelDocExtension.CustomPropertyManager` · `ICustomPropertyManager.Get` / `GetNames` /
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
    3: "number",        #: VT_I4
    11: "yes_or_no",    #: VT_BOOL
    30: "text",         #: VT_LPSTR
    64: "date",         #: VT_FILETIME
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
    mgr = get_com_member(ext, "CustomPropertyManager", str(config_name))
    if mgr is None or not hasattr(mgr, "Count"):
        #: 兜底：个别环境下把它当属性取反而可用 ⇒ 再试一次（但判据仍是行为）
        alt = get_com_member(ext, "CustomPropertyManager")
        if hasattr(alt, "Count"):
            return alt
        raise RuntimeError(
            "取不到 CustomPropertyManager（当方法调用与当属性取都不像管理器；"
            "★ 判据是它有没有 Count）")
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


def custom_property(model, name: str, config_name: str = "") -> dict[str, Any]:
    """读**一个**属性的值 + 类型 + 是否可编辑。

    ★★ 值走 `Get(name)`（**单返回值**）；**不用** `Get2..Get6` ——
      它们带 by-ref out，实测在 pywin32 下报 `类型不匹配`（见模块头 ②）。
    """
    if not str(name or "").strip():
        raise ValueError("name 不能为空")
    mgr = custom_property_manager(model, config_name)
    value = get_com_member(mgr, "Get", str(name))
    try:
        tcode = int(get_com_member(mgr, "GetType2", str(name)))
    except Exception:                                          # noqa: BLE001
        tcode = -1
    editable = None
    try:
        editable = bool(get_com_member(mgr, "IsCustomPropertyEditable", str(name)))
    except Exception:                                          # noqa: BLE001
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
        value = get_com_member(mgr, "Get", n)
        try:
            tcode = int(get_com_member(mgr, "GetType2", n))
        except Exception:                                      # noqa: BLE001
            tcode = -1
        items.append({"name": n, "value": "" if value is None else str(value),
                      "type_code": tcode,
                      "type": SW_CUSTOM_INFO_TYPES.get(tcode, "unknown(%d)" % tcode)})
    return {
        "config": str(config_name),
        "count_reported": int(get_com_member(mgr, "Count")),
        "count_read": len(items),
        "properties": items,
    }
