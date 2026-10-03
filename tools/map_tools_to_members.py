"""★ **筛选器**：把 277 个工具映射到「它真正调的 COM 成员」⇒ 再投影到官方结构上。

★ 为什么需要它（★ 上一轮判据① = **100% 无处可放**，★ 根因已诊断清楚）：
  ★★ **工具名是**意图语言**（`fillet` / `part_shell`），★ 官方成员名是**实现语言**
    （`FeatureFillet3` / `InsertShellFeature`）** ⇒ ★★ **两套词汇不共享 token**
    ⇒ ★ **按名字分类必然 0 命中**。
  ⇒ ★★★ **但那条映射**已经存在于我们代码里**：★ 每个 ToolSpec 有 `module` + `function`，
    ★ 而那个函数体里就是真正的成员名 ⇒ **只是没被抽出来**。
★ 做法：★ 对每条 spec，★ 读 `scripts/<module>.py`，★ **AST 定位 `<function>`**，
  ★★ **跟一层调用图**（★ 事实 507：只看 spec 文档会漏，★ 要落到函数体），
  ★ 抽出 `get_com_member(x, "Member")` / `call_com_member(x, "Member")` 的**字符串字面量**。
★ 只读。产出 `output/tool-to-member-map.json`。
"""
from __future__ import annotations

import ast
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"D:\AI\SW")
SWAPI = Path(r"C:\swapi")
OUT = REPO / "output" / "tool-to-member-map.json"

#: ★ 取成员的两种调用形态（★ 本仓口径）
CALL_PAT = re.compile(r'\b(?:get_com_member|call_com_member|set_com_member)\s*\(\s*[^,]+,\s*"([A-Za-z_][A-Za-z0-9_]*)"')
#: ★ 取"点调用"形态：obj.Member(
DOT_PAT = re.compile(r"\.([A-Z][A-Za-z0-9_]{2,})\s*\(")


def _func_sources(mod_file: Path) -> dict:
    try:
        src = mod_file.read_text(encoding="utf-8", errors="replace")
    except Exception:                                                     # noqa: BLE001
        return {}
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return {}
    out = {}
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[n.name] = ast.get_source_segment(src, n) or ""
    return out


def main() -> int:
    started = time.time()
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "mcp-server"))
    sys.path.insert(0, str(REPO / "scripts"))
    import register_capabilities as rc
    specs = [s for s in rc.all_specs() if getattr(s, "name", None)]

    #: ★ 官方成员集合（★ 用来判"这个成员名是不是官方的"）
    official = set()
    for d in (SWAPI / "types").iterdir():
        if d.is_dir():
            official |= {p.stem for p in d.glob("*.md")}

    rows, cache = [], {}
    for s in specs:
        mod, fn = getattr(s, "module", "") or "", getattr(s, "function", "") or ""
        key = mod
        if key not in cache:
            cache[key] = _func_sources(REPO / "scripts" / ("%s.py" % mod))
        pool = cache[key]
        body = pool.get(fn, "")
        #: ★★ 跟**多层**调用图（★ 事实 507：只看 spec 文档会漏，★ 要落到函数体；
        #:   ★★ 而"落脚"往往在**第二、三层** —— ★ 第一版只跟一层 ⇒ ★ `fillet` / `chamfer` /
        #:   `extrude_boss` / `sketch_add_line` 这些**明明调 COM 的**被算成"无引用"（74 条）。
        #:   ★ 现改为**广度优先跟 3 层**，★ 并把每一层抓到的函数体拼起来抽成员名。
        seen, frontier, depth = {fn}, [fn], 0
        parts = [body]
        while frontier and depth < 3:
            nxt = []
            for cur in frontier:
                text_cur = pool.get(cur, "")
                for n in pool:
                    if n in seen:
                        continue
                    if re.search(r"\b%s\s*\(" % re.escape(n), text_cur):
                        seen.add(n)
                        nxt.append(n)
                        parts.append(pool.get(n, ""))
            frontier = nxt
            depth += 1
        called = [n for n in seen if n != fn]
        text = "\n".join(parts)
        members = sorted(set(CALL_PAT.findall(text)))
        #: ★★★ 2026-10-03 修：本仓**两种调用形态都有** ——
        #:   ① `get_com_member(x, "Member", …)`（★ 本仓新写法）
        #:   ② ★★ **点调用** `model.FeatureManager.FeatureFillet(…)`（★ `sw_part.fillet` 就是这种）
        #:   ★ 第一版**只统计 ①** ⇒ ★ `fillet` / `chamfer` / `sketch_add_line` 等**明明调 COM 的**
        #:   被算成"无引用"（64–74 条）⇒ ★★ **判据漏了一整种调用形态**（★ 与事实 51 同族：
        #:   判据的**分析范围**与代码的**组织单元**不匹配）。
        dotted = sorted({m for m in DOT_PAT.findall(text) if m in official})[:60]
        all_members = sorted(set(members) | set(dotted))
        rows.append({
            "tool": s.name,
            "module": mod, "function": fn,
            "com_members": all_members,
            "dot_members": dotted,
            "official_hits": [m for m in members if m in official],
            "non_official": [m for m in members if m not in official],
            "helpers_followed": called[:12],
        })

    tot_m = sum(len(r["com_members"]) for r in rows)
    with_m = [r for r in rows if r["com_members"]]
    R = {
        "at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "工具数": len(rows),
        "★_有成员的工具": len(with_m),
        "★_无成员的工具": len(rows) - len(with_m),
        "★_成员引用总数": tot_m,
        "★_官方成员命中": sum(len(r["official_hits"]) for r in rows),
        "★_非官方/自封装名": sum(len(r["non_official"]) for r in rows),
        "官方成员总数": len(official),
        "行": rows,
    }
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")

    print("★ 工具 **%d** 条 ⇒ ★★ **有 COM 成员引用的 %d 条（%.1f%%）** · 无的 %d 条"
          % (len(rows), len(with_m), 100.0 * len(with_m) / max(1, len(rows)), len(rows) - len(with_m)))
    print("★ 成员引用合计 **%d** 处 · ★ 其中**是官方成员名**的 **%d** 处 · 其余 %d 处（★ 自封装/参数名）"
          % (tot_m, R["★_官方成员命中"], R["★_非官方/自封装名"]))
    print()
    print("★ 样例（前 12 条，★ 看意图 → 实现是否接上了）：")
    print("%-34s %-16s %s" % ("工具", "目标函数", "★ 抽到的 COM 成员"))
    print("-" * 116)
    for r in rows[:12]:
        print("%-34s %-16s %s" % (r["tool"].replace("solidworks_", "")[:33], r["function"][:15],
                                  ", ".join(r["com_members"][:4])[:56]))
    print()
    print("★ 无成员引用的工具（前 16，★ 这些是纯数据/纯读表的）：")
    print("   " + ", ".join(r["tool"].replace("solidworks_", "")
                            for r in rows if not r["com_members"])[:400])
    print()
    print("★ 产出:", OUT, "（%.1f s）" % (time.time() - started))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
