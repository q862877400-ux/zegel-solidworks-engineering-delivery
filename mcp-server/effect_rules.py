"""★ 效应声明的**动词规则**（规格 210 · B1）：把底层成员名判成「改哪几类状态」。—— 一处实现，两处用。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（声明层的判据）
# 文件:   mcp-server/effect_rules.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B1-1/B1-2**。
#   ★★ 为什么单独成文件：★ 同一套动词规则**被两个地方用** ——
#     ① `tools/survey_effect_declarations.py`（只读普查，出报告）
#     ② `tools/gen_effect_declarations.py`（生成效应表，供注册层读）
#     ★ 本仓反复吃过的亏：**一个好用的规则只在一个地方用，另一处又抄一遍** ✓
# 判据:   ★★ **只按底层成员名的首个动词判**（外部评审逐字：「Create/Insert/Add/Delete/Set 这类判写，
#   是高可信的保守规则」）；★ 且**方向保守**：★ 宁可把读判成写，**绝不反过来** ✓
#   ★ 官方类型库那一路（`propget`/`propput`）**本版未参与** —— ★ 评审提醒「普通方法没有读写标记，
#     对方法仍只能靠名字」⇒ ★ 如实标注，不冒充用过 ✓
# 官方依据: 七类状态由外部评审给出：文档内容 · 文件系统 · 选区 · 激活文档 · 编辑态 · 视图 · 重建或解析
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

#: ★ 七类状态（★ 顺序固定，便于比对与显示）✓
STATE_CLASSES = ("document", "filesystem", "selection", "active_doc", "edit_mode", "view", "rebuild")

#: ★★ **判写的动词** —— ★ 保守表：宁可把读判成写，不许反过来 ✓
WRITE_VERBS = frozenset((
    "create", "insert", "add", "set", "delete", "remove", "modify", "edit", "update",
    "save", "export", "open", "close", "activate", "rebuild", "select", "unselect",
    "clear", "reset", "apply", "run", "start", "stop", "load", "import", "move", "copy",
    "rotate", "scale", "mirror", "pattern", "extrude", "revolve", "cut", "fillet", "chamfer",
))

#: ★ **判读的动词**（★ 只在**没有任何写动词**时才用于确认「读」）✓
READ_VERBS = frozenset((
    "get", "is", "has", "count", "list", "read", "query", "find", "show", "report",
    "check", "available", "name", "enum", "describe", "evaluate", "compute", "measure",
))

#: ★ 动词 → 状态类别（★ 命不中的写动词归 `document`，并**记下来**供复核）✓
VERB_TO_CLASSES = {
    "select": ("selection",), "unselect": ("selection",), "clear": ("selection",),
    "activate": ("active_doc",), "open": ("active_doc", "filesystem"),
    "close": ("active_doc",),
    "save": ("filesystem",), "export": ("filesystem",), "import": ("filesystem",),
    "load": ("filesystem",),
    "edit": ("edit_mode",), "modify": ("edit_mode",),
    "rebuild": ("rebuild",), "update": ("rebuild",), "reset": ("rebuild",),
}

#: ★ **破坏性**动词（★ 与「写」分开：删除 / 覆盖保存 / 清空 / 卸载）✓
DESTRUCTIVE_VERBS = ("delete", "remove", "clear", "saveas", "overwrite", "purge", "unload")


def first_verb(member: str) -> str:
    """★ 取成员名的**首个动词**（按大写驼峰切词；★ 取不到返回空串）。

    ★ 例：`GetSelectedObjectCount2` ⇒ `get`（读）· `InsertSketch` ⇒ `insert`（写）✓
    ★ `CreateDefinition` 这类「建一个定义对象」的 ⇒ `create` ⇒ **判写** —— ★ **偏保守，正合方向** ✓
    """
    if not member:
        return ""
    parts: list[str] = []
    cur = ""
    for i, ch in enumerate(member):
        if ch.isupper() and cur and not member[i - 1].isupper():
            parts.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        parts.append(cur)
    return parts[0].lower() if parts else ""


def classify_members(members) -> dict:
    """★ 一组 COM 成员名 ⇒ 效应结论。

    :returns: `{"writes": [类别…], "destructive": bool, "unclassified": [动词…]}`
    ★★ **空输入 ⇒ `writes` 返回 `None`（未知）**，★ 不是 `[]`（「确认无写」）——
      ★ 这个区分是本规格的**要害**：★ 判不出**不许**当成「无写」 ✓
    """
    ms = [m for m in (members or []) if m]
    if not ms:
        return {"writes": None, "destructive": False, "unclassified": []}
    writes: set[str] = set()
    destructive = False
    unclassified: list[str] = []
    for m in ms:
        v = first_verb(m)
        if v in WRITE_VERBS:
            for cls in VERB_TO_CLASSES.get(v, ("document",)):
                writes.add(cls)
            if any(d in m.lower() for d in DESTRUCTIVE_VERBS):
                destructive = True
        elif v not in READ_VERBS:
            unclassified.append(v or "(无首词)")
    return {
        #: ★★★ **有「认不出的成员」⇒ 判未知，不判「确认无写」** ——
        #:   ★ 一个成员既不是写动词也不是读动词（如 `FeatureManager`、`FirstFeature` 这类**属性访问**），
        #:     就**不能**因为"我没看见写动词"而说它无写 ⇒ ★ **那正是我们要防的方向** ✓
        #:   ★ 只有"**全部成员都认得、且没有一个是写动词**"才算 `[]`（确认无写）✓
        "writes": None if unclassified else sorted(writes),
        "destructive": destructive,
        "unclassified": sorted(set(unclassified)),
    }
