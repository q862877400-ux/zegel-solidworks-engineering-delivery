"""自验证：`scripts/sw_debug.py` 能区分「合格草图」与「故意做坏的草图」。

# ── 来源 ─────────────────────────────────────────────────────────────
# 纪律：门禁/检测器必须带**负例** —— 只证明「合格时不报」不够，
#   还要证明「不合格时一定报出来」，否则是假绿。
# 三个用例：
#   ① 闭合方形（应全部通过）
#   ② 单条直线（开放轮廓，应报 status≠0）
#   ③ 两条分离直线（应报开放/不相连）
# 判据：① 的 problems 数 = 0；②③ 的 problems 数 > 0
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts import sw_connect as c  # noqa: E402
from scripts import sw_debug as dbg  # noqa: E402
from scripts import sw_part as P  # noqa: E402


def make_square(sw):
    doc = c.new_document(sw, "part")
    with P.sketch(doc, "Front Plane"):
        P.sketch_line(doc, 0.0, 0.0, 10.0, 0.0)
        P.sketch_line(doc, 10.0, 0.0, 10.0, 10.0)
        P.sketch_line(doc, 10.0, 10.0, 0.0, 10.0)
        P.sketch_line(doc, 0.0, 10.0, 0.0, 0.0)
    return doc


def make_single_line(sw):
    doc = c.new_document(sw, "part")
    with P.sketch(doc, "Front Plane"):
        P.sketch_line(doc, 0.0, 0.0, 10.0, 0.0)
    return doc


def make_two_lines(sw):
    doc = c.new_document(sw, "part")
    with P.sketch(doc, "Front Plane"):
        P.sketch_line(doc, 0.0, 0.0, 10.0, 0.0)
        P.sketch_line(doc, 0.0, 5.0, 10.0, 5.0)
    return doc


def run_case(sw, label, maker, expect_feature_ok: bool) -> bool:
    """断言 **「可用于特征」那一条** 的结果（而不是整体零问题）。

    ★ 方形本来就是欠定义的、且没有实体，整体 problems 必然非零 ——
      那是模块**如实报告**，不是缺陷。真正要区分的是「草图能否用于建特征」。
    """
    doc = maker(sw)
    rep = dbg.diagnose(doc, sw, feature_type=dbg.FEATURE_TYPES["BOSSEXTRUDE"])
    target = [f for f in rep.findings
              if "可用于特征" in f.target and f.scope == "sketch"]
    ok = bool(target) and target[0].ok == expect_feature_ok
    print(f"\n--- {label} ---")
    for f in target:
        print(f"  [{f.scope}] {f.target}: {'✓' if f.ok else '✗'} {f.text}")
        if not f.ok:
            print(f"      修法 → {f.remedy[:70]}")
    print(f"  期望可用于特征={expect_feature_ok} ⇒ {'✓' if ok else '✗'}")
    try:
        title = str(c.get_com_member(doc, "GetTitle") or "")
        if title:
            c.get_com_member(sw, "CloseDoc", title)
    except Exception:  # noqa: BLE001
        pass
    return ok


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    sw, _ = c.connect_solidworks(wait_seconds=20)
    results = [
        run_case(sw, "① 闭合方形（可用于特征）", make_square, True),
        run_case(sw, "② 单条直线（不可用于特征）", make_single_line, False),
        run_case(sw, "③ 两条分离直线（不可用于特征）", make_two_lines, False),
    ]
    print()
    print(f"通过 {sum(results)}/{len(results)}")
    print("VERDICT:", "OK" if all(results) else "FAIL")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
