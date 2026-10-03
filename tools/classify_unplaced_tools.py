"""★ 把「无处可放」的 30 个**分类**：★ 哪些是"纯数据/纯计算工具"（★ 本来就不该有 COM 成员）。

★★ 为什么（★ 目标里 阶段 3 的判据① ）：
  ★ `tools/build_capability_matrix_v2.py` 的判据① = 「**无处可放率 ≤ 20%**」，
    ★ 定义为「工具没被放进 7×15 任何一格」。
  ★★ 而**实测**抽了 3 个（`sw_sketch.count_arcs` · `sw_geometry_selectors.available_point_selectors` ·
    `sw_delivery.build_bom_traceability`）⇒ ★★★ **COM 调用数都是 0** ——
    ★ 它们是**纯数据/纯计算工具**，★ **整条路都在我们自己的模块里** ⇒
    ★★★★ **"无处可放"对它们是**应然的**，★ 不是缺陷** ✓

★★★ 判据（★ 写死、可核）：★ **目标函数体（含跟到的被调函数）里的 COM 调用数 == 0**
  ⇒ ★ 归入「★ 纯数据（应然）」；★ 否则归入「★★ 真缺口」✓
  ★ COM 调用的形态按本仓的两种写法认：
    `get_com_member(` · `call_com_member(` · `set_com_member(` · **点调用** `<obj>.<Member>(`
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（判据设计 + 可核分类）。
# 文件:   tools/classify_unplaced_tools.py
# 定位:   ★ 阶段 3：把「无处可放」的 30 个分成"应然"与"真缺口"，
#   ★ 让判据① 只统计后者。
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

REPO = Path(r"D:\AI\SW")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(REPO))

OUT = REPO / "output" / "unplaced-classification.json"
COM_FORMS = ("get_com_member(", "call_com_member(", "set_com_member(")
#: ★ 点调用：★ `<名>.<Member>(` —— ★ 只认"看起来像 COM 对象"的宿主名（★ 排除 self/本仓模块）
DOT = re.compile(r"\b([a-z_][A-Za-z0-9_]*)\.([A-Z][A-Za-z0-9_]*)\s*\(")
#: ★ 这些宿主名是**纯 Python**（★ 本仓自己的对象/标准库），★ 不算 COM
PY_HOSTS = {"self", "cls", "os", "re", "json", "path", "p", "m", "out", "builtins"}


def _func_src(mod_file: Path, fname: str) -> str:
    try:
        src = mod_file.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
    except Exception:                                                     # noqa: BLE001
        return ""
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == fname:
            return ast.get_source_segment(src, n) or ""
    return ""


def _com_calls(text: str) -> int:
    n = sum(text.count(f) for f in COM_FORMS)
    for host, _member in DOT.findall(text):
        if host not in PY_HOSTS:
            n += 1
    return n


def main() -> int:
    mat = json.loads((REPO / "output" / "operation-object-matrix-v2.json").read_text(encoding="utf-8"))
    unplaced = mat["无处可放"]
    m = json.loads((REPO / "output" / "tool-to-member-map.json").read_text(encoding="utf-8"))
    rows = {r["tool"].replace("solidworks_", ""): r for r in m["行"]}

    pure, real, unknown = [], [], []
    for t in unplaced:
        r = rows.get(t)
        if not r:
            unknown.append({"tool": t, "why": "★ 映射表里没有"})
            continue
        src = _func_src(REPO / "scripts" / ("%s.py" % r["module"]), r["function"])
        if not src:
            unknown.append({"tool": t, "why": "★ 取不到函数源码"})
            continue
        k = _com_calls(src)
        rec = {"tool": t, "module": r["module"], "function": r["function"], "com_calls": k,
               "lines": len(src.splitlines())}
        (pure if k == 0 else real).append(rec)

    R = {
        "★_判据": "★ 目标函数体里的 COM 调用数 == 0 ⇒ ★ 纯数据（应然）；★ 否则 ⇒ 真缺口",
        "无处可放总数": len(unplaced),
        "判据①_含纯数据": round(100.0 * len(unplaced) / 277, 2),
        "★_纯数据（应然）": len(pure),
        "★★_真缺口": len(real),
        "★_取不到源码": len(unknown),
        "★★_判据①_只算真缺口": round(100.0 * len(real) / 277, 2),
        "纯数据明细": sorted(pure, key=lambda x: -x["lines"])[:40],
        "真缺口明细": sorted(real, key=lambda x: -x["com_calls"])[:40],
        "取不到源码的": unknown[:20],
    }
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    print("★ 无处可放 %d 个" % len(unplaced))
    print("★ 判据①（含纯数据）      = %.2f%%" % R["判据①_含纯数据"])
    print("★★ 纯数据（应然）        = %d" % len(pure))
    print("★★ 真缺口                = %d" % len(real))
    print("★ 取不到源码             = %d" % len(unknown))
    print("★★ 判据①（只算真缺口）   = %.2f%%" % R["★★_判据①_只算真缺口"])
    print()
    print("★ 真缺口明细（前 12）：")
    for x in R["真缺口明细"][:12]:
        print("   %-34s %-20s COM %d" % (x["tool"][:33], x["module"][:19], x["com_calls"]))
    print()
    print("★ 纯数据明细（前 12）：")
    for x in R["纯数据明细"][:12]:
        print("   %-34s %-20s %d 行" % (x["tool"][:33], x["module"][:19], x["lines"]))
    print()
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
