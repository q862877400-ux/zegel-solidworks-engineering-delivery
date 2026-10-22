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
# 官方依据: 七类状态由外部评审给出：文档内容 · 文件系统 · 选区 · 激活文档 · 编辑态 · 视
#           图 · 重建或解析
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

from pathlib import Path
from typing import Optional

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


def classify_members(members, kinds=()) -> dict:
    """★ 一组 COM 成员名 ⇒ 效应结论。

    :returns: `{"writes": [类别…], "destructive": bool, "unclassified": [动词…]}`
    ★★ **空输入 ⇒ `writes` 返回 `None`（未知）**，★ 不是 `[]`（「确认无写」）——
      ★ 这个区分是本规格的**要害**：★ 判不出**不许**当成「无写」 ✓
    """
    ms = [m for m in (members or []) if m]
    if not ms:
        return {"writes": None, "destructive": False, "unclassified": []}
    #: ★ 默认**不用**索引（★ 保证干净机器与测试的行为是确定的）；
    #:   ★★ 要用第二路就**显式传入**（★ 生成器传 `load_kind_index()`）✓
    writes: set[str] = set()
    destructive = False
    unclassified: list[str] = []
    #: ★ 第二路（官方类型库）把成员判成了写的，★ 也要归进状态类别 ——
    #:   ★ 属性式写入默认归 **document**（★ 保守：我们不假装知道它更细的归属）✓
    for m in ms:
        v = first_verb(m)
        verdict = classify_member(m, kinds)
        if v in WRITE_VERBS or verdict == "write":
            for cls in VERB_TO_CLASSES.get(v, ("document",)):
                writes.add(cls)
            if any(d in m.lower() for d in DESTRUCTIVE_VERBS):
                destructive = True
        elif verdict is None:
            unclassified.append(v or "(无首词)")
    return {
        #: ★★★ **有「认不出的成员」⇒ 判未知，不判「确认无写」** ——
        #:   ★ 一个成员既不是写动词也不是读动词（如 `FeatureManager`、`FirstFeature` 这类**属性访问**），
        #:     就**不能**因为「我没看见写动词」而说它无写 ⇒ ★ **那正是我们要防的方向** ✓
        #:   ★ 只有「**全部成员都认得、且没有一个是写动词**」才算 `[]`（确认无写）✓
        "writes": None if unclassified else sorted(writes),
        "destructive": destructive,
        "unclassified": sorted(set(unclassified)),
    }

#: ★★ 官方**成员种类索引**（规格 210 · B1-7）：成员名 ⇒ `{"kind": property|method, "settable": bool}`。
#:   ★ 由 `tools/gen_member_kind_index.py` 从官方类型库派生（★ 缓存、不入库）；
#:   ★★ **读不到索引 ⇒ 只有动词这一路**（★ 保守：判不出的仍判未知，绝不因此宣称只读）✓
_KIND_INDEX_PATH = Path(__file__).resolve().parents[1] / ".api-signatures" / "member-kinds.json"
_KIND_CACHE: Optional[dict] = None


def load_kind_index() -> dict:
    """★ 惰性加载成员种类索引；★ 读不到就回空（⇒ 退化成「只有动词一路」，保守）✓"""
    global _KIND_CACHE
    if _KIND_CACHE is None:
        try:
            import json as _json
            _KIND_CACHE = _json.loads(
                _KIND_INDEX_PATH.read_text(encoding="utf-8")).get("members", {})
        except Exception:                                               # noqa: BLE001
            _KIND_CACHE = {}
        if not isinstance(_KIND_CACHE, dict):
            _KIND_CACHE = {}
    return _KIND_CACHE


def classify_member(member: str, kinds: Optional[dict] = None) -> Optional[str]:
    """★ 单个成员判成 `"write"` / `"read"` / `None`（**判不出**）—— ★ 三态，`None` 不是「读」 ✓

    ★ 判序（★ **任一来源说「写」就不许标只读**，这是外部评审给的裁决规则）：
      ① 动词说写 ⇒ 写；② 动词说读 ⇒ 读；
      ③ 动词认不出 ⇒ 查官方类型库：★ **属性且可设（`{get; set;}`）⇒ 写** ·
         ★ **属性且只读（`{get;}`）⇒ 读** · ★ **方法 ⇒ 判不出**（★ 评审：方法没有读写标记）✓
    """
    v = first_verb(member)
    if v in WRITE_VERBS:
        return "write"
    if v in READ_VERBS:
        return "read"
    rec = (kinds or {}).get(member)
    if not rec:
        #: ★ 动词认不出、类型库也没有 ⇒ **判不出**（★ 不是「读」）✓
        return None
    if rec.get("kind") == "property":
        if rec.get("settable") is True:
            return "write"                      # ★ `{get; set;}` ⇒ 可写 ✓
        if rec.get("settable") is False:
            return "read"                       # ★ `{get;}` ⇒ 只读 ✓
        return None                             # ★ 属性但签名没标 ⇒ 判不出
    return None                                 # ★ 方法 ⇒ 官方无读写标记 ⇒ 判不出 ✓

#: ★★★ **`requires` 的机械初推规则**（★ 规格 210 · B3 的「分组基数」）。
#:   ★★ 起因（真机读数）：★ `nonempty` 组抽样 20 里，★ 剩余的失败**全部**是
#:     「**声明注入 X 但没给对应对象**」（`asm_model` · `view` · `sldworks`）或环境/取值类 ⇒
#:     ★★ **分组要按「需要什么宿主对象」来分**，★ 而那个信息**声明里已经有了**（`inject`）✓
#:   ★ 判据：★ 直接**从 `inject` 的种类**推 —— ★ 这是**声明里的事实**，★ 不是我猜的 ✓
#:   ★★ 为什么值得机械推：★ 评审说「耗时随**不同前置的数量**增长，不随工具数增长」——
#:     ★ 而 `requires` 的种类数就是那个「不同前置的数量」 ✓
INJECT_REQUIRES = {
    "": "none",                       # ★ 不需要宿主对象（★ 如纯静态查询）✓
    "model": "part",
    "doc": "part",
    "asm_model": "assembly",
    "component": "assembly",
    "drawing_model": "drawing",
    "view": "view",
    "sldworks": "app",
    "sw_app": "app",
    "sw": "app",
    "manager": "app",
    "defaults": "app",
    "options": "app",
    "selection": "selection",
    "study": "study",
    "mesh": "study",
    "results": "study",
    "motion_study": "study",
    "cost_manager": "costing",
    "cost_part": "costing",
    "cost_body": "costing",
    "cost_analysis": "costing",
}


def derive_requires(inject: str) -> str:
    """★ 从 `inject` 推**这一条需要什么宿主**（★ 未知的注入名 ⇒ 原样带回并加前缀，★ 不吞）✓"""
    key = str(inject or "").strip()
    if key in INJECT_REQUIRES:
        return INJECT_REQUIRES[key]
    return "host:" + (key or "unknown")

#: ★★★ **`doc_type` 的机械初推规则**（★ 规格 210 · B3 的第二次拆解产物）。
#:   ★★ 起因（真机）：★ 存活普查里 **7 条 `drawing_*`** 报
#:     `当前文档不是工程图（GetType()=1；swDocPART=1 / swDocASSEMBLY=2 …）` ✗
#:     ⇒ ★★ 而它们的 `inject` 声明是 **`model`** —— ★ `inject` **没表达"文档类型"这一维** ✓
#:   ★ 判据：★ **从工具源码里"文档类型检查"的那句话反推**（★ 这是**机械的**，
#:     ★ 因为它读的是**工具自己写的检查**，★ 不是我猜的）✓
#:   ★★ 为什么值得推：★ 推出来之后，★ 普查就能**建对类型的文档**给它们，
#:     ★ 而 B4 的预检也能**提前**报 `wrong_doc_type`（★ 而不是等工具内部抛）✓
#:   ★⚠ 限度：★ 只认**文本里出现的那几种说法**；★ 认不出 ⇒ `None`（★ 不许瞎猜）✓
_DOC_TYPE_MARKERS = (
    ("drawing", ("不是工程图", "swDocDRAWING", "swDocDRAWING", "GetType()=3", "GetType() = 3")),
    ("assembly", ("不是装配体", "swDocASSEMBLY", "GetType()=2", "GetType() = 2")),
    ("part", ("不是零件", "swDocPART", "GetType()=1", "GetType() = 1")),
)


def derive_doc_type(source: str) -> Optional[str]:
    """★ 从**工具源码**推它要哪种文档；★ 认不出 ⇒ `None`（★ 不许瞎猜）✓

    ★ 判序：★ 先看"不是 X"这类**直白说法**，★ 再看枚举名 —— ★ 两者都是**工具自己写的** ✓
    """
    text = str(source or "")
    for kind, marks in _DOC_TYPE_MARKERS:
        if any(m in text for m in marks):
            return kind
    return None

#: ★★★ **`needs` 的机械初推规则**（★ 规格 210 · B3 的第三次拆解产物）。
#:   ★★ 起因（真机）：★ 存活普查里那几条 `sketch_*` 报
#:     `没有活动草图` / `不在草图编辑态`，★ 而 `part_bounding_box` 报 `零件里可能没有实体` ✗
#:   ⇒ ★★ 它们要的**不是"宿主对象"**，★ 而是**宿主处于某种状态** ——
#:     ★ **编辑态（草图中）** 或 ★ **有实体** ✓
#:   ★ 判据：★ 从**工具源码（含被调函数）里的报错话与成员名**反推 ——
#:     ★ 读的是**工具自己写的检查**，★ 不是我猜的 ✓
#:   ★★ 为什么值得推：★ 推出来之后，★ 普查就能**先把状态推到位**再调它们 ✓
#:   ★⚠ 限度：★ 只认**文本里出现的说法**；★ 认不出 ⇒ **空元组**（★ 不许瞎猜）✓
_NEEDS_MARKERS = (
    ("edit:sketch", ("没有活动草图", "不在草图编辑态", "ActiveSketch", "GetActiveSketch",
                     "ActiveSketch 为 None")),
    ("body", ("没有实体", "零件里可能没有实体", "GetBodies2(0", "GetBodies2(-1")),
    ("selection", ("__current_selection__", "必须已选中", "没有选中")),
)


def derive_needs(source: str) -> tuple:
    """★ 从**工具源码**推它需要宿主**处于什么状态**；★ 认不出 ⇒ `()`（★ 不许瞎猜）✓"""
    text = str(source or "")
    out = []
    for token, marks in _NEEDS_MARKERS:
        if any(m in text for m in marks):
            out.append(token)
    return tuple(out)

