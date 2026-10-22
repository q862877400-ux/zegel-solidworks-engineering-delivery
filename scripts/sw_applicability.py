"""★ 适用性与重试：结构化的「不适用」码集 · 按 requires 生成的预检 · 重试门控与指纹保险。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力实现，铁律 3 的 `scripts/`）
# 文件:   scripts/sw_applicability.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B4**。★ 外部评审的判决（四条，逐
#           条落地）：
#     ① ★★ **工具层返回结构化的「不适用」**，★ **不要抛字符串异常** ——
#        形如 `not_applicable{code, needs, better:[…]}`，★ **码集必须封闭且小**（**6–8 个**）✓
# ② ★ **预检由共享装饰器按声明的 `requires` 自动生成**（★ 作者不手写，★ 复杂性留在一处）
# ✓
#     ③ ★★ **自动重试只在「静态 ∩ 实证一致」时开** —— ★ 不一致进人工复核，★ **不用多数决** ✓
#     ④ ★★ **独立于标签的运行时保险**：★ **重试前先比对指纹** ——
#        没变才重试；★ 变了 ⇒ **不重试**、先对账 ✓（★ 即使标签错了也不会无条件重复写）✓
#   ★ 另有评审给的一条边界：★ **编排层只做「代码 → 动作」映射**，★ 不许含工具专属知识 ✓
# 判据:   ★ 码集**封闭且小**（★ 有测试钉住「不许长大」）· ★ **码由工具自己报**，★ 不靠 L
# LM 猜 ✓
#   ★★ 重试门控**不对称**：★ 只有「两边都说安全」才开；★ 任一侧存疑 ⇒ **不开** ✓
# 官方依据: 无 —— ★ 这是我方编排口径，如实标注 ✓
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EFFECTS = REPO_ROOT / "docs" / "effect-declarations.json"
OBSERVED = REPO_ROOT / "docs" / "effect-observed.json"

#: ★★★ **封闭且小**的「不适用」码集（★ 评审给的 7 个 —— ★ **不许随手加**）✓
#:   ★★ 判据：★ 每个码都要能**映射到一个动作**（★ 否则编排层没得做，★ 那它就只是噪音）✓
CODES = {
    "no_document": "★ 没有活动文档 ⇒ 动作：**先建/先开**一个",
    "wrong_doc_type": "★ 文档类型不对 ⇒ 动作：**换/建**对类型的文档",
    "missing_selection": "★ 缺少某类选区 ⇒ 动作：**先选**一个",
    "wrong_edit_mode": "★ 编辑态不对 ⇒ 动作：**进/退**编辑态",
    "invalid_param": "★ 参数无效 ⇒ 动作：**让调用方改**参数（★ 编排层不改）",
    "unsupported_here": "★ 本版本/本后端不支持 ⇒ 动作：**换做法或放弃**",
    "wrong_tool": "★ 不是这个工具 ⇒ 动作：**改用 `better` 里那个**",
}


class NotApplicable(Exception):
    """★ 结构化的「不适用」 —— ★★ **不是**字符串异常（★ 评审明确要求）✓"""

    def __init__(self, code: str, needs=(), better=(), detail: str = ""):
        if code not in CODES:
            #: ★★ 码集**封闭** ⇒ 认不出的码**当场报出**（★ 不许悄悄流通）✓
            raise ValueError("★ 不在封闭码集里的码：%r（★ 码集见 CODES）" % code)
        self.code = code
        self.needs = list(needs)
        self.better = list(better)
        self.detail = detail
        super().__init__("not_applicable: %s" % code)

    def to_dict(self) -> dict:
        """★ 工具层要返回的形状（★ 编排层据此做「代码 → 动作」映射）✓"""
        return {
            "ok": False,
            "not_applicable": True,
            "code": self.code,
            "needs": self.needs,
            "better": self.better,
            "detail": self.detail,
            "action_hint": CODES[self.code],
        }


#: ★★ **「代码 → 动作」映射**（★ 编排层**只有这一张表**，★ 不含任何工具专属知识）✓
ACTION_MAP = {
    "no_document": "create_or_open_document",
    "wrong_doc_type": "switch_or_create_doc_type",
    "missing_selection": "establish_selection",
    "wrong_edit_mode": "enter_or_exit_edit_mode",
    "invalid_param": "ask_caller_to_fix_param",
    "unsupported_here": "abandon_or_switch_approach",
    "wrong_tool": "reselect_tool",
}


def _table(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("tools", {}) or {}
    except Exception:  # noqa: BLE001
        return {}


def declared_requires(tool_name: str) -> str:
    """★ 从静态表取 `requires`（★ 没记到 ⇒ `「unknown」`，★ 不猜）✓"""
    row = _table(EFFECTS).get(tool_name) or {}
    return str(row.get("requires") or "unknown")


def observed_writes(tool_name: str):
    """★ 从**实证覆盖层**取观察到的效应（★ 没有记录 ⇒ `None`）✓"""
    return (_table(OBSERVED).get(tool_name) or {}).get("writes")


def static_writes(tool_name: str):
    """★ 从静态表取 `writes`（★ `[]` = 确认无写 · `None` = 未知）✓"""
    return (_table(EFFECTS).get(tool_name) or {}).get("writes")


def retry_allowed(tool_name: str) -> dict:
    """★★ **自动重试的门控**：★ 只在「**静态 ∩ 实证一致**」时开 ✓

    :returns: `{"allowed": bool, "why": str, "static": …, "observed": …}`
    ★★ 评审的原话：★「两者都通过才开；★ **不一致进人工复核，不用多数决**」✓
    ★ 判序（★ **不对称** —— ★ 任一侧存疑就不开）：
      ① ★ 实证**观察到有写** ⇒ **不开**（★ 哪怕静态说无写 —— ★ 实证确凿）✓
      ② ★ 静态**有写** ⇒ **不开**（★ 保守：★ 别自动重试可能改状态的调用）✓
      ③ ★ 静态**未知**（`None`）⇒ **不开**（★ 未知不冒充已知）✓
      ④ ★ 两侧都「确认无写」（★ 静态 `[]`、★ 实证无记录）⇒ ★ **开** ✓
    """
    st = static_writes(tool_name)
    ob = observed_writes(tool_name)
    if ob:
        return {
            "allowed": False,
            "why": "★★ 实证**观察到有写** ⇒ 不开（★ 实证确凿）",
            "static": st,
            "observed": ob,
        }
    if st:
        return {
            "allowed": False,
            "why": "★ 静态说**有写** ⇒ 不开（★ 保守）",
            "static": st,
            "observed": ob,
        }
    if st is None:
        return {
            "allowed": False,
            "why": "★ 静态**未知**（`None`）⇒ 不开（★ 未知不冒充已知）",
            "static": st,
            "observed": ob,
        }
    return {
        "allowed": True,
        "why": "★ 两侧都「确认无写」⇒ 开 ✓",
        "static": st,
        "observed": ob,
    }


def fingerprint_allows_retry(before, after) -> dict:
    """★★ **独立于标签的运行时保险**：★ **重试前先比对指纹** ✓

    ★★ 评审的原话：★「没变：★ 该调用**大概率没生效**，可以重试。★ 变了：★ **部分生效，
      ★ 不重试**，★ 先对账（★ 读出实际状态，★ 对照意图补完或回滚）」✓
    ★ 于是这条保险**即使标签错了**，★ 也不会无条件重复写 ✓
    ★⚠ 限度（★ 评审自己点出的）：★ 指纹有**盲区**（★ 如 `display` 是本后端限定、
      ★ 自定义属性/材料/视图不覆盖）⇒ ★ 变了**一定**能看出来，★ 没变**不保证**真没变 ✓
    """
    import sw_fingerprint as FP

    diff = FP.compare_detailed(before or {}, after or {})
    changed = [c["class"] for c in diff.get("changed", [])]
    if changed:
        return {
            "retry": False,
            "changed": changed,
            "why": "★★ 指纹**变了**（%s）⇒ **不重试**，先对账 ✓「 % 」、".join(changed),
        }
    return {
        "retry": True,
        "changed": [],
        "why": "★ 指纹没变 ⇒ 该调用**大概率没生效**，可以重试 ✓",
        "caveat": "★ 指纹有盲区（★ %s 等）⇒ 没变**不保证**真没变"
        % "、".join(sorted(FP.KNOWN_UNAVAILABLE)),
    }


# ── 预检装饰器（规格 210 · B4 第 ② 条）──────────────────────────────────
# ★★ 评审的原话：★「**预检由共享装饰器按声明的 `requires` 自动生成**，
#   ★ **作者不手写**，★ 复杂性就留在一处」✓
# ★ 判据：★ 从**静态表**读 `inject` / `requires` + 从**真机枚举**读「打开的文档是什么类
# 型」 ⇒
#   ★ 自动造出检查，★ **没有一个工具需要手写预检** ✓

#: ★ `inject` 名 → 需要的文档类型（★ `None` = 不需要特定类型但不许为空）✓
_DOC_TYPE_BY_INJECT = {
    "model": None,
    "doc": None,
    "asm_model": "assembly",
    "component": "assembly",
    "drawing_model": "drawing",
}

#: ★ SolidWorks 文档类型码（`swDocumentTypes_e`：1=零件 · 2=装配体 · 3=工程图）✓
_DOC_CODE_TO_KIND = {1: "part", 2: "assembly", 3: "drawing"}


def doc_kind(doc) -> str:
    """★ 读一个文档是**哪种类型**（★ 取不到 ⇒ `「unknown」` —— ★ 不猜）✓"""
    try:
        from sw_connect import get_com_member

        return _DOC_CODE_TO_KIND.get(int(get_com_member(doc, "GetType")), "unknown")
    except Exception:  # noqa: BLE001
        return "unknown"


def precheck(inject_name: str, obj, *, tool_name: str = "") -> dict:
    """★★ **按声明自动生成的预检** —— ★ 通过回 `{"ok": True}`；★ 不适用则抛 `NotApplicable` ✓

    ★★ 这是「作者不手写」的落点：★ 检查**完全由 `inject` 决定**，★ 没有一行是逐工具写的 ✓
    ★ 判序（★ 都用**已有码集**，★ 不加码）：
      `model`/`doc` ⇒ 没有活动文档 ⇒ `no_document` ✓
      `asm_model` / `component` ⇒ 空 ⇒ `no_document`；★ 不是装配体 ⇒ `wrong_doc_type` ✓
      `drawing_model` ⇒ 空 ⇒ `no_document`；★ 不是工程图 ⇒ `wrong_doc_type` ✓
      `sldworks`/`sw_app`/… ⇒ 空 ⇒ `no_document`（★ `needs` 里写明要的是哪个对象）✓
      ★ 其余（`view`/`study`/`cost_manager`/`selection`）⇒ ★ **还没建对应的检查** ⇒
        ★ 返回 `{"ok": True, "unchecked": True, "why": …}` —— ★ **如实说「没查」**，
        ★ **不假装查过** ✓（★ 与「判不出就写未知」同一条纪律）
    """
    name = str(inject_name or "")
    if obj is None:
        raise NotApplicable(
            "no_document",
            needs=[name or "host"],
            detail="★ 声明注入 %r 但拿到的是空对象" % name,
        )
    if name in ("sldworks", "sw_app", "sw", "manager", "defaults", "options"):
        return {"ok": True, "checked": "app"}
    want = _DOC_TYPE_BY_INJECT.get(name, "__none__")
    if want == "__none__":
        #: ★ 还没建对应检查的那几类 ⇒ ★ **如实说「没查」** ✓
        return {
            "ok": True,
            "unchecked": True,
            "why": "★ 这一类（`%s`）的预检**还没建** ⇒ 如实记「没查」，★ 不假装查过"
            % name,
        }
    got = doc_kind(obj)
    if want and got != want:
        raise NotApplicable(
            "wrong_doc_type",
            needs=[want],
            detail="★ 需要 `%s`，★ 拿到的是 `%s`" % (want, got),
        )
    return {"ok": True, "checked": "doc", "kind": got}


def precheck_tool(tool_name: str, inject_objects: dict) -> dict:
    """★ 对一个工具**按它声明的 `inject`** 跑预检（★ 调用方只需给 `inject_objects`）✓"""
    inj = (_table(EFFECTS).get(tool_name) or {}).get("inject") or ""
    return precheck(inj, (inject_objects or {}).get(inj))
