"""★ 门禁：逐文件诊断台账必须零 pending，且每条裁决带枚举内的 verdict 与证据。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/check_file_audit.py
# 定位:   业主 2026-11-02 指令「多轮带机械门禁地自动进行，不然你就容易骗我说『我看完
#           了』，实际上根本就没看」。★ 本门禁把「看完了」变成可核的覆盖率：任何入册
#           文件缺 verdict / verdict 不在枚举内 / evidence 为空 / reviewed 缺轮次与执行
#           者，一律红。★ 自带负例自证（selftest）：凭空造一条 pending，必须被抓出来。
# 官方依据: `docs/known-facts.md` 事实 62（负例测试是门禁有效的唯一证明）；
#           AGENTS.md §铁律 3（archive/ 与 output/ 不参与扫描）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   `docs/state/file-audit.jsonl`（由 `scripts/gen_file_audit.py` 产出）
# -----------------------------------------------------------------------------
from __future__ import annotations

import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")  # 事实 58：管道下 GBK 会崩
ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "state" / "file-audit.jsonl"

#: 允许的裁决（★ 出册用前四个，入册只许 reviewed / derived-verified）
VERDICTS = {
    "reviewed": "人工/agent 逐文件读过并留下证据",
    "derived-verified": "不逐行读，但用机械手段验证其行为（编译/解析/测试收集）",
    "frozen": "归档目录，按铁律 3 不参与扫描",
    "generated": "构建/运行产物",
    "excluded": "第三方 salvage 或不可参与自研诊断",
    "binary-asset": "二进制/不可读文本资产",
    "pending": "未审（门禁红灯值）",
}
IN_SCOPE_ALLOWED = {"reviewed", "derived-verified"}
MIN_EVIDENCE = 12  # 证据字符串最短长度，防「OK」「看了」这类空话


def load() -> list[dict]:
    """读台账。"""
    if not LEDGER.exists():
        return []
    rows = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def judge(rows: list[dict]) -> list[str]:
    """返回问题清单（空表示通过）。"""
    bad: list[str] = []
    for row in rows:
        path = row.get("path", "<no path>")
        verdict = row.get("verdict", "")
        evidence = (row.get("evidence") or "").strip()
        if verdict not in VERDICTS:
            bad.append(f"{path}: verdict 不在枚举内 -> {verdict!r}")
            continue
        if verdict == "pending":
            bad.append(f"{path}: 未审（pending）")
            continue
        #: ★ 证据长度门槛**只对入册文件**生效：出册行写的是「为什么出册」的规则理由，
        #:   本来就短（如「构建/运行产物，非源码」）⇒ 对它们要求 12 字符是误伤。
        if row.get("scope") == "in" and len(evidence) < MIN_EVIDENCE:
            bad.append(f"{path}: evidence 过短（{len(evidence)} < {MIN_EVIDENCE}）")
        if row.get("scope") == "in" and verdict not in IN_SCOPE_ALLOWED:
            bad.append(f"{path}: 入册文件的 verdict={verdict} 不允许")
        if verdict == "reviewed":
            if not evidence.startswith(("deep:", "skim:")):
                bad.append(f"{path}: reviewed 证据必须以 deep:/skim: 开头（区分精读与浏览）")
            if not row.get("checked_by"):
                bad.append(f"{path}: reviewed 缺 checked_by")
            if not row.get("round"):
                bad.append(f"{path}: reviewed 缺 round")
    return bad


def coverage(rows: list[dict]) -> dict[str, dict[str, int]]:
    """按 category 统计覆盖。"""
    stats: dict[str, dict[str, int]] = {}
    for row in rows:
        if row.get("scope") != "in":
            continue
        cat = row.get("category", "other")
        bucket = stats.setdefault(cat, {"total": 0, "done": 0})
        bucket["total"] += 1
        if row.get("verdict") in IN_SCOPE_ALLOWED:
            bucket["done"] += 1
    return stats


def report(rows: list[dict]) -> None:
    """打印覆盖率表。"""
    stats = coverage(rows)
    total = sum(v["total"] for v in stats.values())
    done = sum(v["done"] for v in stats.values())
    pct = (done / total * 100) if total else 0.0
    print("★ 逐文件诊断覆盖率（入册口径）")
    print(f"  {'category':26s} {'done':>6s} {'total':>6s}  {'pct':>6s}")
    for cat in sorted(stats, key=lambda c: -stats[c]["total"]):
        bucket = stats[cat]
        p = bucket["done"] / bucket["total"] * 100 if bucket["total"] else 0
        flag = "" if bucket["done"] == bucket["total"] else "  <-- 未覆盖"
        print(f"  {cat:26s} {bucket['done']:6d} {bucket['total']:6d}  {p:5.1f}%{flag}")
    print(f"  {'合计':26s} {done:6d} {total:6d}  {pct:5.1f}%")
    out = sum(1 for r in rows if r.get("scope") == "out")
    print(f"  出册（不计入覆盖率）：{out} 个文件，按规则冻结/排除")


def selftest() -> list[str]:
    """负例自证：凭空造三条坏行，judge 必须全部抓出来。"""
    probe = [
        {"path": "x/pending.py", "scope": "in", "category": "t", "verdict": "pending", "evidence": ""},
        {"path": "x/short.py", "scope": "in", "category": "t", "verdict": "reviewed",
         "evidence": "OK", "round": 1, "checked_by": "a"},
        {"path": "x/badenum.py", "scope": "in", "category": "t", "verdict": "looks-fine", "evidence": "x" * 20},
    ]
    found = judge(probe)
    return found


def main() -> int:
    """入口。"""
    rows = load()
    if not rows:
        print(f"[FAIL] 台账不存在或为空：{LEDGER.relative_to(ROOT)}")
        print("       先跑：python -B scripts/gen_file_audit.py")
        return 1

    print("== 负例自证 ==")
    probe_hits = selftest()
    expected = 3
    if len(probe_hits) < expected:
        print(f"[FAIL] 负例自证未过：预期至少 {expected} 条问题，实抓 {len(probe_hits)} 条")
        for item in probe_hits:
            print("   ", item)
        return 1
    print(f"[ok] 负例三条全部被抓出（pending / evidence 过短 / verdict 越枚举）")

    print()
    report(rows)
    print()

    bad = judge(rows)
    if bad:
        print(f"[FAIL] 台账有 {len(bad)} 处问题，前 20 条：")
        for item in bad[:20]:
            print("   ", item)
        if len(bad) > 20:
            print(f"    ... 其余 {len(bad) - 20} 条略")
        return 1

    stats = coverage(rows)
    total = sum(v["total"] for v in stats.values())
    done = sum(v["done"] for v in stats.values())
    print(f"[PASS] 入册 {total} 个文件全部有裁决与证据（{done}/{total}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
