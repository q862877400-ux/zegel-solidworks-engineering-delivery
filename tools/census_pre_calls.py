"""★ 普查 2.0：**跟调用图**再判 pre_call 有没有回读（★ 上一版只看一个函数的文本 ⇒ 假阳性 3 个）。

★★ 教训（★ 三轮内第二次）：给 `pre_call=_pre_edge_flange` 判"没回读"是错的 ——
  它的函数体里只有 `_select(params, "EDGE")`，★ **回读发生在被调用的 `_select` 里**
  （而 `_select` 又委派给 `scripts/sw_selection_spec.resolve_selection`）。
  ⇒ ★★ **静态判据必须跟调用图**：只看**一个函数的文本**会把"薄包装"全判错。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/census_pre_calls.py
# 定位:   普查 2.0：**跟调用图**再判 pre_call 有没有回读（★ 上一版只看一个函数的文本 ⇒
#            假阳性 3 个）。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import inspect
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import register_capabilities as RC  # noqa: E402

#: 回读的"信号词"（★ 事实 8 的纪律：只信回读计数；`resolve_selection` 内建回读+报错）
READ_TOKENS = ("GetSelectedObjectCount", "resolve_selection", "SelectionManager",
               "_selection_marks", "GetSelectedObject6")


def _module_funcs(path: Path):
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
    except Exception:                                                     # noqa: BLE001
        return {}
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[n.name] = ast.get_source_segment(src, n) or ""
    return out


def gather(pc, depth: int = 3) -> str:
    """★ 递归收集 `pre_call` 及其在本模块内**被调用函数**的源码（跟调用图）。"""
    try:
        seed = inspect.getsource(pc)
    except Exception:                                                     # noqa: BLE001
        return ""
    mod = sys.modules.get(getattr(pc, "__module__", "") or "")
    fpath = Path(getattr(mod, "__file__", "") or "")
    pool = _module_funcs(fpath) if fpath.is_file() else {}
    seen, todo, text = set(), [getattr(pc, "__name__", "")], seed
    while todo and depth > 0:
        depth -= 1
        cur = todo.pop()
        for name, body in pool.items():
            if name in seen or name == cur:
                continue
            #: ★ 只看"当前文本里被调用到的"名字
            if ("%s(" % name) in text:
                seen.add(name)
                text += "\n" + body
                todo.append(name)
    return text


rows, nocl = [], []
for s in RC.all_specs():
    pc = getattr(s, "pre_call", None)
    if pc is None:
        continue
    text = gather(pc)
    reads = [t for t in READ_TOKENS if t in text]
    row = (getattr(s, "name", "?"), getattr(pc, "__name__", "?"),
           "★回读:" + ",".join(sorted(set(reads)))[:44] if reads else "★★ 没回读")
    rows.append(row)
    if not reads:
        nocl.append(row)

print("★ 有 `pre_call` 的工具：**%d** 个（总 %d）—— ★ 本版**跟了调用图**" % (len(rows), len(RC.all_specs())))
print("★ **没回读的**：%d 个" % len(nocl))
for r in nocl:
    print("   %-52s %s" % (r[0].replace("solidworks_", "")[:51], r[1]))
print()
print("★ 回读方式分布：")
kinds: dict = {}
for r in rows:
    kinds[r[2]] = kinds.get(r[2], 0) + 1
for k, v in sorted(kinds.items(), key=lambda kv: -kv[1]):
    print("   %-58s %d" % (k[:57], v))
