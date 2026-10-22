"""★ T2-4 的交集法：把「102 条可机检前置」与「本仓自己的过去错误笔记」交叉，挑出下一批该写断言的。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/t2_intersect_past_errors.py
# 定位:   规格 206 / **T2-4 的交集法**（`docs/recon-206/t2-sample-vs-checkable.md` §四
#            定的形状）——
#         判据三条：① 在 102 条可机检清单里 ② 有「真错过」的记录 ③ 现在没有断言守着 ✓
# 官方依据: 不适用（这是**我们自己的**筛选手法，不是 API 调用）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
SRC = ROOT / "output" / "t2-preconditions-checkable.json"
NOTES = [ROOT / "docs" / "known-facts.md", ROOT / "specs" / "206-c1c6-harvest" / "tasks.md"]
TESTS = ROOT / "tests"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ★ 判据②：本仓自己的「过去错误」标记（★ 事实 549/550 用的那套，逐字沿用）
PAST_ERR = re.compile(r"原本是|原本为|曾错|写反|反了|静默回|轮 \d+ 修|差 1000 倍|1000 倍|mark 反")

#: ★ 判据①：能从一条前置里抽出「可去源码里找的标识符」——API 成员名 / 常量 / mark 值
IDENT = re.compile(r"\b([A-Z][A-Za-z0-9]{4,})\b")
MARK = re.compile(r"mark\s*(?:=|为|number of)?\s*(\d{1,8})", re.I)

#: ★ 判据③：一个标识符要算「已被守着」，它得**真的出现在测试源码里**（★ 不是出现在任何文件里）
#:   ★★ 口径：本轮实测发现「命中测试」的 2 条里，标识符出现在**测试文件的注释**里也算命中 ⇒
#:     ★ 那与「有断言守着」**不是一件事**；本工具**只报 `guarded` 与否**，★ 判读留给人 ✓

#: ★ 泛词黑名单：命中了也说明不了是**同一条**前置 ⇒ ★ 判据要写「不算什么」
STOP = {"SolidWorks", "Visual", "Studio", "Immediate", "Nothing", "True", "False", "Boolean",
        "System", "Int32", "String", "Double", "Object", "Workbook", "CommandInProgress"}

#: ★★ 判据①的**收紧**（★ 本轮实测加的）：前置文本里必须出现**真 API 成员名**，
#:   才算「可去源码里找的那一类」—— ★ 否则「已运行 SolidWorks」这种也带着大写词，
#:   会在 102 条里制造噪音（★ 本工具只关心「某成员的某个前置」）✓
MEMBERISH = re.compile(r"^[A-Z][A-Za-z0-9]*(?:2|3|4|5|6)$|^[A-Z][a-z]+[A-Z][A-Za-z0-9]+$")


def load_checkable() -> list[dict]:
    d = json.loads(SRC.read_text(encoding="utf-8"))
    return d["checkable"]


def notes_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in NOTES if p.is_file())


def tests_text() -> str:
    parts = []
    for p in sorted(TESTS.glob("test_*.py")):
        parts.append(p.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def identifiers(text: str) -> set[str]:
    out = {m for m in IDENT.findall(text) if m not in STOP and not m.isdigit()}
    out |= {"mark=%s" % v for v in MARK.findall(text)}
    return out


def main() -> int:
    if not SRC.is_file():
        print("★ 先跑 tools/t2_filter_checkable_preconditions.py（缺 %s）" % SRC)
        return 1
    rows = load_checkable()
    notes, tests = notes_text(), tests_text()
    print("★ 可机检前置: **%d** 条" % len(rows))

    a = b = c = 0
    hits = []
    for r in rows:
        ids = identifiers(r["text"])
        #: ★ 收紧①：至少一个标识符要**像个真成员名**（★ 见 MEMBERISH）
        if not any(MEMBERISH.match(i) for i in ids):
            continue
        if not ids:
            continue
        hit_notes = sorted(i for i in ids if i in notes and PAST_ERR.search(
            notes[max(0, notes.find(i) - 400): notes.find(i) + 400]))
        if not hit_notes:
            continue
        b += 1
        guarded = sorted(i for i in hit_notes if i in tests)
        if guarded:
            continue
        c += 1
        cap = r["cap"].rsplit("/", 1)[-1]
        hits.append({"cap": cap, "text": r["text"], "ids": hit_notes, "from": r.get("from", "")})
        if cap and cap in notes and PAST_ERR.search(notes[max(0, notes.find(cap) - 600): notes.find(cap) + 600]):
            a += 1

    print("   ① ★ 与「过去错误笔记」有词面交集: **%d** 条" % b)
    print("   ② ★ 而那交集**未被任何测试提到**（= 现在没断言守着）: **%d** 条" % c)
    print("   ③ 其中 ★ 能力名本身就在错误笔记附近的: **%d** 条" % a)
    print()
    print("★ 候选（★ 按「交集标识符个数」降序，前 20）:")
    for h in sorted(hits, key=lambda x: -len(x["ids"]))[:20]:
        print("   [%-20s] %s" % (h["cap"][:20], h["text"][:76].replace("\n", " ")))
        print("        ★ 交集: %s" % ", ".join(h["ids"][:6]))

    out = ROOT / "output" / "t2-intersect-past-errors.json"
    out.write_text(json.dumps({"n_checkable": len(rows), "n_intersect_notes": b,
                              "n_unguarded": c, "n_cap_near_error": a, "hits": hits},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print("★ 写出: %s" % out)
    print()
    print("★ 本表「不算什么」：① 词面交集是粗判（命中 ≠ 同一条前置）；② 它只筛**候选**，")
    print("   ★ 判「该不该写断言」还要人读那一条前置与那段笔记；③ 泛词已过滤，但英文缩写仍可能误命中 ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
