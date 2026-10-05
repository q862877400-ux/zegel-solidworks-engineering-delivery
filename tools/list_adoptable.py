"""★ 规格 207 · V7-3：从 bunny 的 deep 档记录里出**采纳候选清单**（SC-3）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/list_adoptable.py
# 定位:   ★ 规格 207 的 SC-3（②③档 76 条逐条学透 + 官方对照 ⇒ 产出候选）✓
#         ★★ 输入是 `output/bunny-records-deep/<index>.json`（bunny 逐条手写，含 official/proposed/
#           recommendation）⇒ 本工具**只做汇总与排序**，**不替主裁判下结论** ✓
#         ★★★ 判据口径：★ 采纳与否是**主裁判（Lead）的事**（spec.md 的 D-4）⇒ 本工具的输出是
#           **给裁判看的一览**，不是裁决本身 ✓
# 官方依据: 不适用（本仓工序）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
RECORDS = ROOT / "output" / "bunny-records-deep"
WORKLOAD = ROOT / "output" / "union-workload-349.json"


def load(records_dir: Path) -> tuple[list[dict], list[str]]:
    """★ 容错读：非 dict 的记录（实测出现过 list）与坏 JSON 都**计数并跳过**，不静默吞掉。"""
    out: list[dict] = []
    bad: list[str] = []
    for f in sorted(records_dir.glob("*.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception as exc:                                      # noqa: BLE001
            bad.append("%s（%s）" % (f.name, type(exc).__name__))
            continue
        if not isinstance(r, dict):
            bad.append("%s（顶层是 %s，不是对象）" % (f.name, type(r).__name__))
            continue
        out.append(r)
    return out, bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records-dir", default=str(RECORDS))
    ap.add_argument("--json-out", default=str(ROOT / "output" / "union-adoptable.json"))
    a = ap.parse_args()

    recs, bad = load(Path(a.records_dir))
    wl = json.loads(WORKLOAD.read_text(encoding="utf-8"))
    deep_total = sum(1 for x in wl["items"] if x.get("task") == "deep")

    print("=" * 74)
    print("★ 规格 207 · V7-3 采纳候选清单（SC-3）")
    print("=" * 74)
    print("deep 档记录 %d / %d 条" % (len(recs), deep_total))
    if bad:
        print("★ 跳过 %d 份（%s）" % (len(bad), "; ".join(bad[:3])))

    buckets: dict[str, list[dict]] = {}
    for r in recs:
        buckets.setdefault(str(r.get("recommendation") or "（未填）"), []).append(r)

    order = ["采纳", "缓办", "不做"]
    for key in order + [k for k in buckets if k not in order]:
        items = buckets.get(key)
        if not items:
            continue
        print("\n=== recommendation = %s（%d 条）===" % (key, len(items)))
        for r in sorted(items, key=lambda x: int(x.get("index") or 0)):
            off = r.get("official") or {}
            prop = r.get("proposed") or {}
            member = (off.get("member") if isinstance(off, dict) else "") or "查不到"
            print("  #%-4s %-26s %-16s" % (r.get("index"), r.get("op"), r.get("domain")))
            print("        官方成员 : %s" % member)
            if key == "采纳":
                print("        建议工具 : %s  @ %s" % (prop.get("name"), prop.get("module")))
                sig = (off.get("signature") if isinstance(off, dict) else "") or ""
                if sig:
                    print("        签名(逐字): %s" % str(sig)[:110])
                risks = str(prop.get("risks") or "")[:130]
                if risks:
                    print("        风险     : %s" % risks)

    out = {"deep_records": len(recs), "deep_total": deep_total,
           "recommendation_counts": {k: len(v) for k, v in buckets.items()},
           "adopt": [{"index": r.get("index"), "op": r.get("op"), "domain": r.get("domain"),
                      "official_member": (r.get("official") or {}).get("member"),
                      "official_signature": (r.get("official") or {}).get("signature"),
                      "proposed": r.get("proposed"), "confidence": r.get("confidence"),
                      "classifier_was_right": r.get("classifier_was_right")}
                     for r in buckets.get("采纳", [])],
           "defer": [{"index": r.get("index"), "op": r.get("op")} for r in buckets.get("缓办", [])],
           "skip": [{"index": r.get("index"), "op": r.get("op")} for r in buckets.get("不做", [])]}
    Path(a.json_out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n★ 已写：%s" % a.json_out)
    print("★ 分布：%s" % json.dumps(out["recommendation_counts"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
