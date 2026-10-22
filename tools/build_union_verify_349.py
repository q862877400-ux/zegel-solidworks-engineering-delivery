"""★ 聚合 349 条逐条记录成一份**合法 JSON 且 < 256 KB** 的产物（规格 207 的 SC-1 / SC-5）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/build_union_verify_349.py
# 定位:   ★ 规格 207 的 **SC-1 + SC-5** 的落地件 —— 前几轮只有**逐条**记录（`output/bu
#           nny-records-verify/` 273 份 · `output/bunny-records-deep/` N 份），而 SC-1
#           要的是「**349 个操作每个都有一条记录**」、SC-5 要的是「**返回体必须是合法 JS
#           ON 且 < 256 KB**（枚举化）」⇒ ★ 这两条评的是**聚合件** ✓
#         ★★ **为什么用生成器而不是手写**：deep 档还在长（57/76）⇒ 收齐后**重跑即定案**，
#           而不是再手改一遍（手改就会两处漂移，事实 538/539）✓
# ★★★ **枚举化的落地**：机判字段（`verdict` / `recommendation` / `task`）**必须取自固定
# 枚举**，
#           越界的值**不静默接受** —— 收进 `enum_violations` 并让它可见（★ 上一轮 1.8 MB 的
#           workflow 返回体就是因为把机判字段写成了自由字符串，被截断后 JSON 非法）✓
#         ★ 长证据（逐字签名 / Remarks / 风险）**不进聚合件** —— 它们留在各自的逐条文件里；
#           聚合件只放**短字段**，这既保 < 256 KB，也保住「长证据在哪儿」的唯一住所 ✓
# 官方依据: 不适用（本仓工序）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "output" / "union-gap-v3.json"
OUT = ROOT / "output" / "union-verify-349.json"
LIMIT_BYTES = 256 * 1024

#: ★ 机判字段的**固定枚举**（SC-5 的「枚举化」；D-7）—— 越界值不许静默通过 ✓
ENUMS = {
    "verdict": {"已有等价物", "其实没有", "查不到"},
    "recommendation": {"采纳", "缓办", "不做"},
    "task": {"verify", "deep"},
    "confidence": {"高", "中", "低"},
}
#: 两个口径都必须出现（SC-4）—— 且**禁止相减**（分母不同）
CALIBERS = {
    "classifier_self_report": {
        "value": 0.782,
        "numerator": 273,
        "denominator": 349,
        "meaning": "分类器把多少条打成了「①已有等价物」（★ 它的**自述**，不是实测）",
    },
    "per_item_measured": {
        "value": 0.2296,
        "numerator": 62,
        "denominator": 270,
        "meaning": "逐条读完，「已有」这一标**错**了几条（62/270）",
    },
    "★_禁止相减": "两个分母不是同一件事（一个算打了多少标、一个算标错几条）⇒ 只并列，不做减法",
}


def _load_records(d: Path) -> dict[str, dict]:
    """⇒ `{op: record}`；★ 坏件/非对象**计数并跳过**，不静默吞（与 list_adoptable 同纪律）。"""
    out: dict[str, dict] = {}
    for f in sorted(d.glob("*.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except Exception:  # noqa: BLE001
            print("  ★ 坏 JSON（跳过）：%s" % f.name)
            continue
        if not isinstance(r, dict):
            print("  ★ 非对象（跳过）：%s" % f.name)
            continue
        op = r.get("op")
        if isinstance(op, str) and op:
            out[op] = r
    return out


def main() -> int:
    #: ★★ 事实 62：**一个门禁没有负例就不算门禁** ⇒ 给上限做成可注入的，
    #:   这样「超限拒绝落盘」这条分支**能被当场证伪**（`--limit-bytes 1000`）✓
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--limit-bytes",
        type=int,
        default=LIMIT_BYTES,
        help="★ 上限（默认 256 KiB）；★ 调小即可验证「超限拒绝落盘」这条分支",
    )
    a = ap.parse_args()
    limit = a.limit_bytes
    ref = json.loads(REF.read_text(encoding="utf-8"))
    rows = ref["rows"]
    print("★ 参照集 %s：%d 行" % (REF.name, len(rows)))

    vf = _load_records(ROOT / "output" / "bunny-records-verify")
    dp = _load_records(ROOT / "output" / "bunny-records-deep")
    print("★ 已到：verify %d 条 · deep %d 条" % (len(vf), len(dp)))

    viol: list[str] = []
    records: list[dict] = []
    missing: list[str] = []
    for i, row in enumerate(rows, 1):
        op = row.get("operation")
        r = vf.get(op) or dp.get(op)
        if r is None:
            missing.append(op)
            continue
        rec = {
            "i": i,
            "op": op,
            "domain": row.get("domain"),
            "tier": row.get("tier"),
            "best_cov": row.get("best_cov"),
            "task": r.get("task") or ("verify" if op in vf else "deep"),
            "verdict": r.get("verdict") or r.get("has_equivalent"),
            "recommendation": r.get("recommendation"),
        }
        rec["confidence"] = r.get("confidence")
        #: ★ 枚举校验：机判字段越界 ⇒ 记进 violations（**不静默接受、也不替它改**）
        for k, allowed in ENUMS.items():
            v = rec.get(k)
            if v is None:
                continue
            if v not in allowed:
                viol.append("%s: %s=%r" % (op, k, v))
        #: ★ 只留短字段：长证据留在逐条文件里（保 < 256 KB）
        records.append(rec)

    payload = {
        "spec": "207-union-gap-verify",
        "generated_by": "tools/build_union_verify_349.py",
        "reference": "output/union-gap-v3.json",
        "totals": {
            "expected": len(rows),
            "landed": len(records),
            "verify": len(vf),
            "deep": len(dp),
            "missing": len(missing),
        },
        "calibers": CALIBERS,
        "enum_violations": viol,
        "missing_ops": missing,
        "records": records,
    }
    text = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    n = len(text.encode("utf-8"))

    #: ★★ SC-5 的硬判据：**合法 JSON + < 256 KB**（这次是**断言**，不是"看着不大"）✓
    json.loads(text)
    print("★ 字节数 %d （上限 %d）⇒ %s" % (n, limit, "OK" if n < limit else "★ 超限"))
    if n >= limit:
        print("  ★ 不许落盘：超限会让下游截断 ⇒ JSON 非法（上一轮就是这么栽的）")
        return 1
    OUT.write_text(text, encoding="utf-8")
    print("★ 已写 %s" % OUT)
    print("★ 覆盖：%d / %d（缺 %d）" % (len(records), len(rows), len(missing)))
    if viol:
        print("★★ 枚举越界 %d 处（**未静默接受**）：" % len(viol))
        for v in viol[:8]:
            print("   ", v)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
