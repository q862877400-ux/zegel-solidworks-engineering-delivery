r"""@brief 扫「**缺源时静默返回假值**」的兜底 —— 把「我不知道」写成「它有错」的那一族。

## 为什么（轮 198）
轮 197 在 `tests/test_notice_consistency.py` 里修了一处：
```python
if not REFLECT.is_file():
    return False      # ← ★ 把「无从判定」写成了「查不到」
```
★ 而那**不是孤例** —— 它是本项目反复记录的一族（事实 113 兜底 `IObject` · 114 散文猜接口 ·
115 长度倒序 · 116 变量名猜接口 · 137 缺源返回 False）。
⇒ ★★ 本轮**全仓扫**一遍，把同类兜底**列出来**（★ **只列候选**，不下结论）。

## 判据（**窄而强**，且能区分"合法返回"与"悄悄返回"）
```
① 找形如 `if not <X>.is_file():` / `if not <X>.exists():` 的守卫；
② 其**直接函数体**里有 `return <假值>`（`[]` / `False` / `None` / `set()` / `""` / `{}` / `0`）⇒ **候选**；
③ ★ **但本项目的既有写法允许**「**写明理由的**合法返回**」（例：
   `if not NOT_DOING_PATH.is_file(): return bad  # 不存在 = 空清单，合法`）
   ⇒ 若该 return 行**同行有注释**、或**函数 docstring 里提到**便携性/SKIP/合法/空清单/守卫/absent/
     不存在我们**视为已说明**，不计入候选；
④ ★ **两个数都要报**（候选数 + 已说明数）—— 否则"0 候选"可能是判据没生效（事实 46 的假绿）。
```

## ⚠ 安全
**纯静态**：只读源码；不连 SolidWorks、不改任何文件。

# ── 来源 ──
# 仓库:   本项目自身
# 文件:   tools/scan_silent_source_fallbacks.py
# 定位:   给 Spec Kit `118` 把「缺源 ⇒ 静默假值」这一类**扫出来**（事实 113–116 / 137 的推广）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(r"D:\AI\SW\output\silent-source-fallbacks.json")
SCAN = [ROOT / "scripts", ROOT / "tools", ROOT / "tests", ROOT / "mcp-server"]
#: 缺源守卫的形态
GUARD = re.compile(r"^\s*if\s+not\s+.{0,80}?(?:\.is_file\(\)|\.exists\(\)|\.is_dir\(\))\s*:")
#: 视为「已说明理由」的词
#: ⚠⚠ **2026-10-01（轮 198）补词表** —— 第一版没有「拿不到 / 回空」这类说法，
#:   于是把 4 处**docstring 里已写明**的合法返回也报成了候选（候选数被高估）。
#:   ★ 这是"判据太窄"的又一例（事实 51 / 185 / 190 / 192 / 193 / 196）。
EXPLAINED = ("便携性", "SKIP", "合法", "空清单", "守卫", "absent", "不存在", "哨兵", "允许",
             "拿不到", "回空", "没有", "尽力", "不确定", "无法判定", "报错")
FALSY = (ast.List, ast.Dict, ast.Set, ast.Constant, ast.Tuple)


def _is_falsy(node) -> bool:
    """`return` 的值是不是"空的"（`[]` / `False` / `None` / `""` / `{}` / `set()` / `()`）。

    ⚠⚠ **2026-10-01（轮 198）第一版在这里崩了**：`ast.Dict` **没有 `.elts`**
      （它用 `.keys` / `.values`）—— 而我把 `List/Dict/Set/Tuple` 写在同一支里。
      ⇒ ★ 又一次"我以为的 AST 形状"与实际不符（与事实 114/115/116/135/137 同族）。
    """
    if isinstance(node, ast.List):
        return not node.elts
    if isinstance(node, ast.Dict):
        return not node.keys            #: ⚠ Dict 用 keys/values，**没有 elts**
    if isinstance(node, (ast.Set, ast.Tuple)):
        return not node.elts
    if isinstance(node, ast.Constant):
        return node.value in (False, None, "", 0)
    if isinstance(node, ast.Call):                       #: set() / list() / dict() / tuple()
        f = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
        return f in ("set", "list", "dict", "tuple") and not node.args
    return False


def _rel(p: Path) -> str:
    """把路径显示成「相对 ROOT」——**但路径可能不在 ROOT 下**（测试会把 `SCAN` 指到临时目录）。

    ⚠⚠ **2026-10-01（轮 198）**：第一版直接 `p.relative_to(ROOT)` ⇒ 对临时目录**抛 `ValueError`**
      ⇒ ★ **正是轮 68 记过的那个**：「**生成器对"OUT/SCAN 在哪"不能做假设**，
      因为它的调用者会改这些变量」（而**负例自证**恰恰必须改它们 —— 事实 62）。
    """
    try:
        return p.relative_to(ROOT).as_posix()
    except ValueError:
        return p.name


def main() -> int:
    rows, explained = [], 0
    n_guard = 0
    for base in SCAN:
        if not base.is_dir():
            continue
        for p in sorted(base.glob("*.py")):
            src = p.read_text(encoding="utf-8", errors="replace")
            lines = src.splitlines()
            tree = ast.parse(src)
            #: 每个函数/模块的 docstring（用于「已说明」判定）
            docs = {}
            for n in ast.walk(tree):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
                    docs[id(n)] = ast.get_docstring(n) or ""
            for n in ast.walk(tree):
                if not isinstance(n, ast.If) or n.orelse:
                    continue
                head = lines[n.lineno - 1]
                if not GUARD.match(head):
                    continue
                n_guard += 1
                owner = next((f for f in ast.walk(tree)
                              if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))
                              and f.lineno <= n.lineno <= (f.end_lineno or f.lineno)), None)
                doc = docs.get(id(owner), "") if owner else docs.get(id(tree), "")
                #: 直接函数体里第一个 return
                ret = next((s for s in n.body if isinstance(s, ast.Return)), None)
                if ret is None or not _is_falsy(ret.value):
                    continue
                ret_line = lines[ret.lineno - 1]
                #: 「已说明」= 同行注释 / 上一行注释 / docstring 里的说明词
                ctx = ret_line + (lines[ret.lineno - 2] if ret.lineno >= 2 else "")
                if "#" in ret_line or any(k in ctx or k in doc for k in EXPLAINED):
                    explained += 1
                    continue
                rows.append({"file": _rel(p), "line": n.lineno,
                             "guard": head.strip()[:70], "ret": ret_line.strip()[:70]})
    print("  ── 扫了 %d 个文件 · 缺源守卫 **%d** 处 ──"
          % (sum(1 for b in SCAN if b.is_dir() for _ in b.glob("*.py")), n_guard))
    print("  ★ **已写明理由**的合法返回: **%d** 处" % explained)
    print("  ★★ **候选**（缺源 ⇒ 返回假值，且未见说明）: **%d** 处" % len(rows))
    print()
    for r in rows[:20]:
        print("    %-34s L%-5d %s" % (r["file"], r["line"], r["ret"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"guards": n_guard, "explained": explained, "candidates": rows},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  证据: %s" % OUT)
    print("  ⚠ **只列候选** —— 每个都要回代码看它到底该不该抛（本项目纪律：静态候选 ≠ 缺陷）。")
    if n_guard == 0:
        print("  ✗ 守卫数为 0 ⇒ 判据没生效（事实 46 的假绿）⇒ 非 0 退出")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
