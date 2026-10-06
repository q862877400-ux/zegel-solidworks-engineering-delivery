"""★ 只读普查：为 448 个工具机械初判「效应声明」（改哪些状态类别），产出报告而不改声明。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具/一次性施工脚本）
# 文件:   tools/survey_effect_declarations.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B1-1**（见 plan.md 的 B1）。
#   ★★ 为什么要有它：外部评审判决「448 个工具无法一个一个真机验，成本主项是**建立前置状态**而不是调用」，
#     并给出两步：① 先给每个工具补**机器可读**的效应声明（改哪些状态类别）② 再按前置签名分组做存活普查。
#     本脚本只做 ① 的**机械初判**，★ 且**只读**（不改任何声明）✓
# 判据:   ★ 来源一：**底层成员动词**（评审逐字：「Create/Insert/Add/Delete/Set 这类判写，是高可信的保守规则」）·
#   ★ 来源二：官方类型库的读写标记 —— ★ 评审同时提醒：「普通方法没有读写标记，对方法仍只能靠名字」⇒
#     本脚本**只用动词**，并在报告里如实写明「类型库那一路未参与初判」（★ 不冒充用过）✓
#   ★★ 裁决规则（保守方向）：**任一来源说「写」 ⇒ 不许标只读** ✓
# 官方依据: 状态七分类由评审给出：文档内容 · 文件系统 · 选区 · 激活文档 · 编辑态 · 视图 · 重建或解析
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import collections
import importlib
import inspect
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
sys.path.insert(0, str(ROOT / "mcp-server"))
sys.path.insert(0, str(ROOT / "scripts"))
OUT = ROOT / "output" / "spec210-effect-survey.json"

#: ★ 七类状态（评审给的分类；★ 顺序固定，便于比对）
STATE_CLASSES = ("document", "filesystem", "selection", "active_doc", "edit_mode", "view", "rebuild")

#: ★★ **动词表**（本脚本的核心判据；★ 刻意写成显式表，不搞隐式规则）
#:   ★ 判「写」的动词 —— 保守：★ 宁可把读判成写，也不许反过来 ✓
WRITE_VERBS = (
    "create", "insert", "add", "set", "delete", "remove", "modify", "edit", "update",
    "save", "export", "open", "close", "activate", "rebuild", "select", "unselect",
    "clear", "reset", "apply", "run", "start", "stop", "load", "import", "move", "copy",
    "rotate", "scale", "mirror", "pattern", "extrude", "revolve", "cut", "fillet", "chamfer",
)
#: ★ 判「读」的动词（★ 只在**没有任何写动词**时才用于确认「读」）✓
READ_VERBS = (
    "get", "is", "has", "count", "list", "read", "query", "find", "show", "report",
    "check", "available", "name", "enum", "describe", "evaluate", "compute", "measure",
)

#: ★ 动词 → 状态类别的粗略映射（★ 一个动词可以命中多类；★ 命不中的归 `document` 并**记下来**）
VERB_TO_CLASSES = {
    "select": ("selection",), "unselect": ("selection",), "clear": ("selection",),
    "activate": ("active_doc",), "open": ("active_doc", "filesystem"),
    "close": ("active_doc",),
    "save": ("filesystem",), "export": ("filesystem",), "import": ("filesystem",),
    "load": ("filesystem",),
    "edit": ("edit_mode",), "rebuild": ("rebuild",), "modify": ("edit_mode",),
    "update": ("rebuild",), "reset": ("rebuild",),
}

#: ★ 破坏性动词（★ 与「写」**分开**：删除 / 覆盖保存 / 清空）✓
DESTRUCTIVE_VERBS = ("delete", "remove", "clear", "saveas", "overwrite", "purge", "unload")


def _first_verb(member: str) -> str:
    """★ 取成员名的**首个动词**（★ 按大写驼峰切词；★ 取不到返回空串）。

    ★ 为什么取首个：★ `GetSelectedObjectCount2` 首词是 `Get`（读）；★ `InsertSketch` 首词是 `Insert`（写）✓
    ★ 而像 `CreateDefinition` 这种「建一个定义对象」的，首词 `Create` 判写 —— ★ **偏保守，正合我们要的方向** ✓
    """
    if not member:
        return ""
    #: ★ 驼峰切词：在大写字母前断开（★ 连续大写如 `ICW` 不切）
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


def _com_members_in(node: ast.AST) -> list[str]:
    """★ 收集一个 AST 子树里所有 `get_com_member` / `safe_get_com_member` / `call_com_member(obj, "X")` 的成员名。"""
    out: list[str] = []
    for n in ast.walk(node):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
        if name not in ("get_com_member", "safe_get_com_member", "call_com_member"):
            continue
        if len(n.args) >= 2 and isinstance(n.args[1], ast.Constant) and isinstance(n.args[1].value, str):
            out.append(n.args[1].value)
    return out


def _callee_names(node: ast.AST) -> set[str]:
    """★ 一个函数体里**调用了哪些本模块内的名字**（★ 用来自动跟一层同模块助手）✓"""
    out: set[str] = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            out.add(n.func.id)
    return out


def _members_for(func, module, depth: int = 2) -> tuple[list[str], list[str]]:
    """★ 取一个工具函数（★ 含它调用的同模块助手，最多 `depth` 层）里出现的 COM 成员名。

    :returns: `(成员名列表, 读不到的说明列表)`
    """
    notes: list[str] = []
    try:
        src = inspect.getsource(func)
        tree = ast.parse(inspect.cleandoc(src) if False else src)
    except Exception as exc:                                            # noqa: BLE001
        return [], ["源码取不到：%s" % type(exc).__name__]
    seen_funcs = {getattr(func, "__name__", "")}
    members = list(_com_members_in(tree))
    frontier = _callee_names(tree)
    for _ in range(max(0, depth - 1)):
        nxt: set[str] = set()
        for name in frontier:
            if name in seen_funcs:
                continue
            seen_funcs.add(name)
            helper = getattr(module, name, None)
            if not callable(helper):
                continue
            try:
                hsrc = inspect.getsource(helper)
                htree = ast.parse(hsrc)
            except Exception:                                           # noqa: BLE001
                continue
            members += _com_members_in(htree)
            nxt |= _callee_names(htree)
        frontier = nxt
    return members, notes


def survey() -> dict:
    import register_capabilities as rc
    specs = rc.all_specs()
    rows = []
    unclassified: collections.Counter = collections.Counter()
    for s in specs:
        #: ★ 本仓的模块在 `scripts/` 下**按裸名**导入（`import sw_part`，不是 `scripts.sw_part`）——
        #:   ★ 我第一版只试了带前缀的名字 ⇒ **448 个全部 ModuleNotFound** ✓（已改成两个都试）
        mod = None
        for cand in (s.module, "scripts.%s" % s.module):
            try:
                mod = importlib.import_module(cand)
                break
            except Exception:                                           # noqa: BLE001
                continue
        if mod is None:
            rows.append({"tool": s.name, "error": "模块导入失败：%s" % s.module})
            continue
        fn = getattr(mod, s.function, None)
        if not callable(fn):
            rows.append({"tool": s.name, "error": "函数不存在：%s" % s.function})
            continue
        members, notes = _members_for(fn, mod)
        writes: set[str] = set()
        destructive = False
        for m in members:
            v = _first_verb(m)
            if v in WRITE_VERBS:
                for cls in VERB_TO_CLASSES.get(v, ("document",)):
                    writes.add(cls)
                if any(d in m.lower() for d in DESTRUCTIVE_VERBS):
                    destructive = True
            elif v not in READ_VERBS:
                unclassified[v or "(无首词)"] += 1
        rows.append({
            "tool": s.name,
            "module": s.module, "function": s.function,
            "member_count": len(members),
            "members_sample": sorted(set(members))[:8],
            "declared_read_only": bool(getattr(s, "read_only", False)),
            "proposed_writes": sorted(writes),
            "proposed_read_only": not writes,
            "proposed_destructive": destructive,
            "notes": notes,
        })
    ok = [r for r in rows if "error" not in r]
    with_members = [r for r in ok if r["member_count"]]
    no_members = [r for r in ok if not r["member_count"]]
    return {
        "_": "规格 210 · B1-1 只读普查：机械初判每个工具的 writes（★ 不改任何声明）",
        "judge": "来源=底层成员动词（★ 官方类型库的读写标记未参与，见 limitations）",
        "total": len(specs),
        "surveyed": len(ok), "errors": len(rows) - len(ok),
        "with_members": len(with_members), "no_members_found": len(no_members),
        "proposed_read_only": sum(1 for r in with_members if r["proposed_read_only"]),
        "declared_read_only_now": sum(1 for r in with_members if r["declared_read_only"]),
        "mismatch_declared_read_but_proposed_write":
            [r["tool"] for r in with_members if r["declared_read_only"] and not r["proposed_read_only"]],
        "mismatch_proposed_read_but_declared_write_count":
            sum(1 for r in with_members if r["proposed_read_only"] and not r["declared_read_only"]),
        "writes_class_histogram": dict(collections.Counter(
            c for r in with_members for c in r["proposed_writes"])),
        "destructive_proposed": sum(1 for r in with_members if r["proposed_destructive"]),
        "unclassified_verbs": dict(unclassified.most_common(15)),
        "limitations": [
            "★ 只用了**底层成员动词**这一路；★ 评审提到的第二路（官方类型库读写标记）**未参与初判**",
            "★ 动词表是显式的、偏保守：**宁可把读判成写**，不许反过来 ✓",
            "★ 判不出成员名的工具（无显式取成员调用）已单列计数，★ 不代表它没有副作用",
        ],
        "rows": rows,
    }


def main() -> int:
    ev = survey()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("工具总数            : %d" % ev["total"])
    print("成功普查            : %d（模块/函数取不到 %d）" % (ev["surveyed"], ev["errors"]))
    print("含显式 COM 成员的   : %d" % ev["with_members"])
    print("★ 取不到成员名的    : %d  ← 「判不出」的就是这批" % ev["no_members_found"])
    print("★ 初判为只读        : %d   （现在声明的只读是 %d）"
          % (ev["proposed_read_only"], ev["declared_read_only_now"]))
    print("★ 声明只读但初判为写: %d 个" % len(ev["mismatch_declared_read_but_proposed_write"]))
    for t in ev["mismatch_declared_read_but_proposed_write"][:8]:
        print("      %s" % t)
    print("★ 初判只读但声明为写: %d 个（★ 这方向修掉就是「76 个」那件事）"
          % ev["mismatch_proposed_read_but_declared_write_count"])
    print("writes 类别直方图   : %s" % ev["writes_class_histogram"])
    print("初判为破坏性        : %d" % ev["destructive_proposed"])
    print("未归类动词（前 15） : %s" % ev["unclassified_verbs"])
    print("产物：%s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
