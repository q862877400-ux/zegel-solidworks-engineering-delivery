"""★ 官方 `*FeatureData` 族 `Get*` 成员的**分诊表** —— 下一阶段"按官方成员批量补"的施工队列。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types`）
# 文件:   `tools/triage_get_members.py`（★ **不碰 `scripts/`** —— 另一个对话在改那里）·
#         产出 `output/get-member-triage.csv` + `output/get-member-triage.json`
# 定位:   ★ 判据（★ 全部**可数、★ 纯读文档**）：★ 池子 = 官方 `*FeatureData` 族的 `Get
#           *` 成员 ⇒
#   ★★ **每个成员抄出 8 个字段** ⇒ ★★★ **那张表就是"按官方成员批量补"的施工队列** ✓
#   ★★★★ **为什么先分诊**：★ 其中一部分**根本不该进队列** ——
#     · ★ **带 `out` 参数的**（★ pywin32 上多半到不了 —— ★ 事实 47）
#     · ★ **已废弃的**（★ 走 T1 流程、★ 不走补能力）✓
#     先把它们剔掉，★ 队列才干净 ✓
#   ★★★★★ **⚠ 本脚本的判据边界（★ 如实写）**：
# ★ **`有out` = 签名里出现 `out `** ⇒ ★ 那是**文本判据**、★ 不是"真机试过"（★ 事实 518 
# 那族）✓
#     ★★ **`单位词` = 官方页里出现 `radian(s)` / `meter(s)` / `millimeter(s)`** ⇒
#       ★★★ **实测 430 个里只有 **3** 个写了** ⇒ ★ **⇒ 单位只能靠真机测、★ 那一步不可派** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
SWAPI = Path(r"C:\swapi\types")
OUT_CSV = REPO / "output" / "get-member-triage.csv"
OUT_JSON = REPO / "output" / "get-member-triage.json"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SIG = re.compile(r"\*\*Signature\*\*:\s*`([^`]+)`")
UNIT = re.compile(r"(?i)\b(radians?|meters?|millimeters?|degrees?)\b")
#: ★★ **已废弃的判定要**精确****（★ 另一个对话刚修过这个判据 —— ★ 轮 769）：
#:   ★ 只认**独立成句的** `Obsolete.` / `Not supported in`，★ 不认表格单元格里的同词 ✓
OBS = re.compile(r"(?im)^\s*(?:\*\*)?(Obsolete\.|Not supported in SOLIDWORKS)")


def rows() -> list[dict]:
    out = []
    for d in sorted(p for p in SWAPI.iterdir() if p.is_dir()):
        if "FeatureData" not in d.name:
            continue
        for f in sorted(d.glob("Get*.md")):
            t = f.read_text(encoding="utf-8", errors="replace")
            m = SIG.search(t)
            sig = m.group(1).strip() if m else ""
            args = re.search(r"\((.*)\)", sig)
            nargs = len([a for a in args.group(1).split(",") if a.strip()]) if args else 0
            ret = sig.split(" ", 1)[0] if sig else ""
            out.append({
                "族": d.name, "成员": f.stem,
                "参数个数": nargs, "返回类型": ret,
                "有out": "out " in sig,
                "已废弃": bool(OBS.search(t)),
                "有Returns段": "## Returns" in t,
                "单位词": (UNIT.search(t).group(0).lower() if UNIT.search(t) else ""),
                "签名": sig,
                "源文件": str(f.relative_to(SWAPI)),
            })
    return out


def main() -> int:
    r = rows()
    #: ★★★ 分诊：★ 三档
    def tier(x: dict) -> str:
        if x["已废弃"]:
            return "★ D 废弃（走 T1）"
        if x["有out"]:
            return "★ C 带 out（pywin32 风险）"
        if not x["有Returns段"]:
            return "★ B 无 Returns 段（要先查语义）"
        return "★ A 可施工"
    for x in r:
        x["档"] = tier(x)

    r.sort(key=lambda x: (x["档"], x["族"], x["成员"]))
    with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(r[0].keys()))
        w.writeheader()
        w.writerows(r)

    from collections import Counter
    cnt = Counter(x["档"] for x in r)
    byfam = Counter(x["族"] for x in r if x["档"] == "★ A 可施工")
    OUT_JSON.write_text(json.dumps({
        "★_判据": "★ 池子 = 官方 `*FeatureData` 族的 `Get*` 成员；"
                  "★ 档 = A 可施工 / B 无 Returns 段 / C 带 out / D 废弃",
        "★_判据边界": "★ `有out` 与 `已废弃` 都是**文本判据**、★ 不等于真机结论（★ 事实 518）",
        "★_单位": "★ 官方页**几乎从不写单位** ⇒ ★ 单位只能真机测（★ 那一步**不可派**）",
        "合计": len(r), "分档": dict(cnt),
        "A 档按族": dict(byfam.most_common()),
        "全部": r,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print("★ 池子: 官方 `*FeatureData` 族的 `Get*` 成员 ——— **%d** 个 · %d 族" % (
        len(r), len({x["族"] for x in r})))
    print()
    for k in sorted(cnt):
        print("   %-26s **%3d**" % (k, cnt[k]))
    print()
    print("★ A 档（★ 可施工）按族，前 14:")
    for fam, n in byfam.most_common(14):
        print("   %-34s %3d" % (fam, n))
    print()
    print("★ 产出: %s" % OUT_CSV)
    print("★ 产出: %s" % OUT_JSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
