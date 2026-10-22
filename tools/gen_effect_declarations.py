"""★ 生成效应表（规格 210 · B1）：从底层成员动词机械初判每个工具改哪几类状态，落成生成物。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（生成器）
# 文件:   tools/gen_effect_declarations.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B1-2**。★ 产出 `docs/effect-decl
#           arations.json`，
#   由声明层（`mcp-server/tool_registry.py`）惰性读取 ⇒ ★ 于是 448 个工具**有了机器可读的 writes** ✓
#   ★★ 为什么做成「生成物」而不是逐个改 99 个声明文件：★ 一处生成、一处读取、一处门禁守着新鲜度 ——
#     这正是本仓已经用熟的形态（生成物 + 新鲜度门禁）✓
# 判据:   ★★ **判不出 ⇒ `writes: null`（未知）**，★ 绝不是 `[]`（那意思是「确认无写」）；
#   ★ 声明层的 `effective_read_only` 对「未知」返回 **假**（★ 绝不因为判不出就宣称只读）✓
# 官方依据: 动词规则在 `mcp-server/effect_rules.py`（★ 一处实现两处用）；七类状态由外部
#           评审给出
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

ROOT = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(ROOT / "mcp-server"))
sys.path.insert(0, str(ROOT / "scripts"))
OUT = ROOT / "docs" / "effect-declarations.json"

#: ★ 只跟**同模块**助手几层（★ 跟太多会把不相干的成员算进来 —— ★ 本仓事实 51 的同一族教训）✓
HELPER_DEPTH = 2


def _com_members(node: ast.AST) -> list[str]:
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


def _callees(node: ast.AST) -> set[str]:
    return {n.func.id for n in ast.walk(node)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def _members_of(func, module) -> list[str]:
    """★ 一个工具函数（★ 含它调用的同模块助手，最多 `HELPER_DEPTH` 层）里出现的 COM 成员名 ✓"""
    try:
        tree = ast.parse(inspect.getsource(func))
    except Exception:                                                   # noqa: BLE001
        return []
    members = list(_com_members(tree))
    seen = {getattr(func, "__name__", "")}
    frontier = _callees(tree)
    for _ in range(max(0, HELPER_DEPTH - 1)):
        nxt: set[str] = set()
        for name in frontier:
            if name in seen:
                continue
            seen.add(name)
            helper = getattr(module, name, None)
            if not callable(helper):
                continue
            try:
                htree = ast.parse(inspect.getsource(helper))
            except Exception:                                           # noqa: BLE001
                continue
            members += _com_members(htree)
            nxt |= _callees(htree)
        frontier = nxt
    return members


def _src_deep(fn, module=None) -> str:
    """★ 工具**自身 + 被调函数**的源码（★ `doc_type` 往往写在共用助手里）✓

    ★★ 为什么必须深扫：★ 第一版只扫工具自己 ⇒ ★ 7 条 `drawing_*` **一条都没中** ✗
      ★ 因为「不是工程图」那句检查在**共用助手**里 ✓
    ★ 限度：★ 只跟**本模块内**、**一层**的被调函数（★ 够用；★ 再深容易把无关的也算进来）✓
    """
    parts = [_src_of(fn)]
    try:
        import inspect
        src = inspect.getsource(fn)
        for name in _callees(ast.parse(_dedent(src))):
            sub = getattr(module, name, None)
            if callable(sub) and getattr(sub, "__module__", "") == getattr(module, "__name__", ""):
                parts.append(_src_of(sub))
    except Exception:                                                   # noqa: BLE001
        pass
    return "\n".join(p for p in parts if p)


def _dedent(src: str) -> str:
    """★ 去掉函数源码的公共缩进（★ 才能 `ast.parse`）✓"""
    import textwrap
    return textwrap.dedent(src)


def _src_of(fn) -> str:
    """★ 取函数的**源码文本**（★ `doc_type` 从它里面反推）✓"""
    try:
        import inspect
        return inspect.getsource(fn)
    except Exception:                                               # noqa: BLE001
        return ""


def build() -> dict:
    import register_capabilities as rc
    from effect_rules import (STATE_CLASSES, classify_members, derive_doc_type,
                          derive_needs, derive_requires, load_kind_index)
    specs = rc.all_specs()
    tools: dict = {}
    errors: list[str] = []
    hist = collections.Counter()
    for s in specs:
        mod = None
        #: ★ 本仓模块在 `scripts/` 下**按裸名**导入（★ 我第一版只试带前缀的名字 ⇒ 448 个全挂）✓
        for cand in (s.module, "scripts.%s" % s.module):
            try:
                mod = importlib.import_module(cand)
                break
            except Exception:                                           # noqa: BLE001
                continue
        if mod is None:
            errors.append("%s: 模块 %s 导入失败" % (s.name, s.module))
            continue
        fn = getattr(mod, s.function, None)
        if not callable(fn):
            errors.append("%s: 函数 %s 不存在" % (s.name, s.function))
            continue
        #: ★ 取注入名（★ `requires` 由它推）✓
        try:
            import tool_registry as _tr
            _inj = _tr.effective_inject(s)
        except Exception:                                       # noqa: BLE001
            _inj = getattr(s, "inject", "") or ""
        members = _members_of(fn, mod)
        #: ★★ 第二路：显式把官方成员种类索引传进去（规格 210 · B1-7）✓
        verdict = classify_members(members, kinds=load_kind_index())
        tools[s.name] = {
            #: ★★ `requires` —— ★ **机械初推**（★ 从 `inject` 的种类推，★ 见 `effect_rules`）✓
            #:   ★ 起因（真机）：★ `nonempty` 组的失败**全**是「声明注入 X 但没给对象」✓
            "requires": derive_requires(_inj),
            #: ★★ `doc_type` —— ★ 从**工具源码里的类型检查**机械初推 ✓
            #: ★★★ 2026-10-06 **第一版只扫了工具自己的源码** ⇒ ★ 7 条 `drawing_*`
            #:   ★ **一条都没中** ✗ —— ★ 因为那句「不是工程图」的检查写在**共用助手**里 ✓
            #:   ⇒ ★ 要把**被调函数（含传递）的源码一起扫**（★ `_callees` 已有）✓
            "doc_type": derive_doc_type(_src_deep(fn, mod)),
            #: ★★ `needs` —— ★ 宿主要处于什么**状态**（★ 编辑态/实体/选区）✓
            "needs": list(derive_needs(_src_deep(fn, mod))),
            "inject": _inj,
            "writes": verdict["writes"],            # ★ None = 未知（★ 不是「无写」）
            "destructive": verdict["destructive"],
            "members": len(members),
            "source": "static" if verdict["writes"] is not None else "unknown",
        }
        hist["unknown" if verdict["writes"] is None else
             ("pure_read" if not verdict["writes"] else "has_writes")] += 1
    return {
        "_": "★ 生成物（规格 210 · B1-2）：每个工具的 writes 由**底层成员动词**机械初判。★ 不要手改。",
        "_regenerate": "python tools/gen_effect_declarations.py",
        "_judge": "★ 判不出 = writes:null（未知）· ★ 不是 []（那意思是「确认无写」）",
        "_limitations": [
            "★ 只用动词这一路；★ 官方类型库的读写标记**未参与**",
            "★ 只跟**同模块**助手 %d 层；★ 跨模块调用的成员**扫不到**" % HELPER_DEPTH,
            "★ writes:null 的工具，★ 注册层按「未知」保守处理（不发只读、不开自动重试）",
        ],
        "state_classes": list(STATE_CLASSES),
        "counts": dict(hist),
        "errors": errors,
        "tools": tools,
    }


def main() -> int:
    data = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    c = data["counts"]
    print("工具数        : %d" % len(data["tools"]))
    print("★ 确认无写    : %d" % c.get("pure_read", 0))
    print("★ 确有写      : %d" % c.get("has_writes", 0))
    print("★ 未知（判不出）: %d  ← ★ 注册层会保守处理" % c.get("unknown", 0))
    print("取不到模块/函数: %d" % len(data["errors"]))
    print("产物：%s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
