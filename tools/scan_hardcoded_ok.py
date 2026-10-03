"""★ 扫「**`ok` 是不是被写死的**」—— ★ 一次找出全部同类（★ 而不是逐个工具人眼找）。

★★ 起因（★ `JUDGE-C_D_E.md` 的 🔴 #1 逐字）：
  > ★ 「**E-5 全部 6 类（11 个工具）**：★ doc 承诺的判据**没进 `ok`** ⇒ ★ **特征没建成也报成功**，
  > 直接违反仓库规则 6（不静默成功）」✓
  ★★ 而六类的**共同形态**是：★ **`"ok": True` 写死**、★ 或**判据算了但没进 `ok`** ✓

★★★ 本扫描器**只报不动**（★ 本项目纪律）—— ★ 它产出**候选清单**，
  ★★ 而**判不判得成**要逐条回原文（★ 那是 Lead 的活）✓

★★★★ 判据（★ **可核、可复核**）：
  ★ **A 类 · 写死成功**：★ `"ok": True`（★ 字面量）或 `"ok": <常量表达式>` ⇒
    ★★ **报告**（★ 但**同时报出**同一函数里有没有 before/after 取样，★ 那决定它是"真写死"还是"已验过"）✓
  ★ **B 类 · 判据未进 ok**：★ 函数里算了 `xxx_ok` / `added` / `delta` 之类，★ 而 `"ok"` 那一行**不带**它 ⇒
    ★★ **报告** ✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tools/scan_hardcoded_ok.py
# 定位:   ★ 阶段 1 的 `JUDGE-C_D_E` 🔴 #1（E-5 · 6 类 · 11 工具）的**全仓版**：
#   ★ 找出所有「ok 被写死」或「判据没进 ok」的地方 ⇒ ★ 供逐条回原文判 ✓
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
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OUT = REPO / "output" / "hardcoded-ok-scan.json"
#: ★ 取样类调用的名字（★ 有它才说明"前后比过"）
SAMPLERS = ("_tree(", "_body_face_count(", "_volume_mm3(", "_delta(", "_new_features(",
            "before", "after", "_sample", "_count(", "snapshot")
#: ★ 判据类局部名（★ 算了但可能没进 ok）
JUDGE_HINT = re.compile(r"\b(\w*(?:ok|added|delta|changed|passed|exists|created)\w*)\s*=")


def _scan_file(path: Path) -> list:
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
    except Exception:                                                     # noqa: BLE001
        return []
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        seg = ast.get_source_segment(src, node) or ""
        #: ★ 只看返回 dict 的函数
        if '"ok"' not in seg and "'ok'" not in seg:
            continue
        hard, judge_vars = [], set(JUDGE_HINT.findall(seg))
        for n in ast.walk(node):
            if not isinstance(n, ast.Dict):
                continue
            for k, v in zip(n.keys, n.values):
                if not (isinstance(k, ast.Constant) and k.value == "ok"):
                    continue
                #: ★ `"ok": True` / `"ok": False` ⇒ 字面量
                #: ★★★★ 2026-10-04（接手轮）**收窄：只报 `True`** —— ★ 病因是「**静默成功**」⇒
                #:   形态必然是 `ok: True`；★ 而 `ok: False` 是**安全的**（★ 把失败报成失败）✓
                #:   实测依据：★ 第一版把 `sw_costing.py` 的 6 个函数都报成"最可疑"，
                #:   ★★ 而它们报的全是**错误路径**的 `"ok": False` ⇒ 假阳性 ✓
                if isinstance(v, ast.Constant):
                    if v.value is True:
                        hard.append("字面量 True")
                #: ★ `"ok": bool(xxx)` / `"ok": xxx and ...` ⇒ 看它用没用判据变量
                else:
                    used = re.findall(r"\b(\w+)\b", ast.unparse(v))
                    miss = {j for j in judge_vars if j not in used}
                    if miss and ("bool" in ast.unparse(v) or "and" in ast.unparse(v)
                                 or " or " in ast.unparse(v)):
                        hard.append("候选未用判据: %s" % ", ".join(sorted(miss)[:3]))
        if not hard:
            continue
        sampled = [s for s in SAMPLERS if s in seg]
        out.append({
            "file": str(path.relative_to(REPO)).replace("\\", "/"),
            "function": node.name,
            "line": node.lineno,
            "ok_forms": hard[:4],
            "sampled": bool(sampled),
            "samplers": sampled[:4],
            "judge_vars": sorted(judge_vars)[:6],
        })
    return out


def main() -> int:
    rows = []
    for d in ("scripts", "mcp-server"):
        for f in sorted((REPO / d).rglob("*.py")):
            rows += _scan_file(f)
    for f in sorted((REPO / "subskills").rglob("scripts/*.py")):
        rows += _scan_file(f)
    #: ★ 分开两类：★ **无取样**（最可疑）· ★ **有取样**（可能已验过）
    risky = [r for r in rows if not r["sampled"]]
    maybe = [r for r in rows if r["sampled"]]
    R = {
        "★_判据": "★ 找 `\"ok\"` 是字面量 / 或没用到判据变量的函数；"
                  "★★ 再按『函数里有没有 before/after 取样』分成两档",
        "★_合计": len(rows),
        "★★_最可疑（无任何取样）": len(risky),
        "★_有取样（可能已验过）": len(maybe),
        "最可疑明细": risky[:80],
        "有取样明细": maybe[:40],
    }
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")
    print("★ 扫到 %d 个『ok 可能是写死的』函数" % len(rows))
    print("★★ 最可疑（★ 函数里**没有任何 before/after 取样**）: %d" % len(risky))
    print("★ 有取样（★ 可能已验过）: %d" % len(maybe))
    print()
    print("★★ 最可疑的前 24 个（★ 逐个回原文判）:")
    print("%-52s %-34s %s" % ("文件", "函数", "ok 形态"))
    print("-" * 116)
    for r in risky[:24]:
        print("%-52s %-34s %s" % (r["file"][-51:], r["function"][:33], str(r["ok_forms"])[:44]))
    print()
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
