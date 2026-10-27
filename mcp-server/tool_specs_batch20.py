"""第二十批 MCP 工具声明：**读文件自定义属性** 2 个（砌墙 W3）。

## ★★★ 本批补的是一个**真空白**：能写却不能读
```
· `solidworks_set_custom_properties`（**写**）—— 上游 45 个工具之一，早就在。
· ★ 能力层里**没有任何"读文件自定义属性"的实现**：
    `sw_pdm.get_custom_property_names_and_values` 要 **PDM 许可证**（`sw_pdm` 模块头自述
    「域 14 · 路由 / Composer / PDM（**需许可证**）」），不是这条路。
⇒ ★★ **结果：能写不能读** ⇒ 写了属性**没法验**。本批补的就是它。
★ 而它走的是 `IModelDocExtension.CustomPropertyManager`（**不需要 PDM**）。
```

## ★★★ 调用形态由**真机探针**定死（`tools/probe_custom_property_reads.py`，轮 227）
```
① ★★ `model.Extension.CustomPropertyManager` **必须当方法调用**：
     正确：  mgr = model.Extension.CustomPropertyManager("")      ← 传配置名，"" = 默认
     错误：  mgr = model.Extension.CustomPropertyManager          ← 拿到 **method 对象**，
             之后每个调用都报 `AttributeError: 'function' object has no attribute 'Count'`
   ⚠ 本探针**第一版**判据是 `not isinstance(v, (str,int,float))` ⇒ **判不出函数** ⇒ 假阳性，
     真机上第一轮全是 AttributeError。⇒ 判据改成**行为**："它有没有 Count"。

② ★★ 读值**只能**用 `Get(name)`（**单返回值**，实测能读 ✓）：
     `Get2..Get6(name, …, out Val, out ResolvedVal)` 实测报 **`类型不匹配`**
     （`com_error: (-2147352571)`）—— ★ 与**已知事实 8 / 33** 同族：
     **pywin32 迟到绑定下 by-ref 出参不通**。⇒ 能力层一律不用 `Get2+`。

③ 真机决定性用例：`Add3(名, 30, 值, True)` 写入后 `Count` **28 → 29** 且 `Get(名)` **读回写入值** ✓
   （本批**只读**，不做写 —— 写已由上游工具承担。）
```

## ★ 为什么只有 **2** 个工具（不凑数）
能力层还有 `custom_property_count` 与 `custom_property_names`，但
**它们的结果已被「读全部」包含**（`custom_properties` 同时回 `count` 与逐条 `name`）⇒
★ 单独挂出去只会让 AI 多调一次拿同一件事 ⇒ **不挂**。

| 工具 | 用途 |
|---|---|
| `solidworks_custom_property_get` | 读**一个**属性的值 + 类型（AI 问"这个零件的零件号是什么"）|
| `solidworks_custom_property_list` | 读**全部**属性（AI 问"这个零件有哪些属性"）|

★ 两者都带 `config_name`（留空 = 默认配置）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（不是第三方移植；被包装的函数各自的来源块在其源码里）
# 文件:   mcp-server/tool_specs_batch20.py
# 定位:   「孤立能力暴露」第二十批 / 砌墙 W3（Spec Kit `133`）。
# 官方签名依据: 不适用（只做参数搬运）；取管理器与读值的形态依据是真机探针
#          `tools/probe_custom_property_reads.py`（见上）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

from tool_registry import Param, ToolSpec

__all__ = ["SPECS_BATCH20"]

_CONFIG = (
    "Configuration name to read from. Leave empty for the default configuration "
    '(""). ⚠ Custom properties can be configuration-specific.'
)
_WHY = (
    "★ Reading only — writing is solidworks_set_custom_properties. The API's by-ref "
    "getters (Get2..Get6) do NOT work under pywin32 (they raise a type-mismatch error), "
    "so these tools use the single-return Get(name); that shape is verified on a real machine."
)


SPECS_BATCH20 = [
    ToolSpec(
        name="solidworks_custom_property_get",
        title="Get One Custom Property",
        module="sw_custom_property",
        function="custom_property",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** —— 真机证据：未声明注入时包装拿到 0
        #:  个实参 ⇒
        #: `TypeError: … missing 1 required positional argument: 'model'`。同族 `solidwo
        #: rks_part_bounding_box` 写着 `inject='model'` ✓
        params=[
            Param(
                "name",
                str,
                description=(
                    "Exact custom property name as stored; names follow the UI language and are case sensitive."
                ),
            ),
            Param("config_name", str, default="", description=(
                                                      "Configuration to read from; empty reads the default configuratio"
                                                      "n. Defaults to empty."
                                                  )),
        ],
        evidence=(
            "Read ONE file custom property: its value, its type (swCustomInfoType_e) and whether it is editable. ★ Read"
            "ing only — writing is solidworks_set_custom_properties. The API's by-ref getters (Get2..Get6) do NOT work "
            "under pywin32 (they raise a type-mismatch error), so these tools use the single-return Get(name); that sha"
            "pe is verified on a real machine."
        ),
        doc=(
            "Read one file custom property value together with its type and whether it is editable. Read-only; writing "
            "is a different tool, and property names follow the UI language and are case sensitive."
        ),
    ),
    ToolSpec(
        name="solidworks_custom_property_list",
        title="List All Custom Properties",
        module="sw_custom_property",
        function="custom_properties",
        inject="model",
        #: ★ 2026-10-03（轮 461）**补漏掉的 inject** —— 真机证据：未声明注入时包装拿到 0
        #:  个实参 ⇒
        #: `TypeError: … missing 1 required positional argument: 'model'`。同族 `solidwo
        #: rks_part_bounding_box` 写着 `inject='model'` ✓
        params=[Param("config_name", str, default="", description=(
                                                          "Configuration to read from; empty reads the default configur"
                                                          "ation. Defaults to empty."
                                                      ))],
        evidence=(
            "Read ALL file custom properties of the active document: every name with its value and type, plus how many "
            "were read. ★ Reading only — writing is solidworks_set_custom_properties. The API's by-ref getters (Get2..G"
            "et6) do NOT work under pywin32 (they raise a type-mismatch error), so these tools use the single-return Ge"
            "t(name); that shape is verified on a real machine."
        ),
        doc=(
            "Read every file custom property of the active document with its value and type. Read-only; writing is a di"
            "fferent tool, and the reply also says how many properties were read."
        ),
    ),
]
