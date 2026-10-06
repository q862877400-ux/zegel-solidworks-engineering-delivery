"""★ 规格 211 · B8 收口：自动生成**21 项逐项结论表**（★ 台账终判 × `capabilities.yaml` 的 level）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B8 的收口工具）
# 文件:   tools/gen_spec211_final_table.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B8 收口**。★ 规格的**完成判据**是
#   「**21 项每一项都有结论** ∈ {`verified` · `stitched` · `不做（附理由+证据）`}」✓
#   ⇒ ★ 本工具把两处**机器可读**的来源合成一张表：
#     ★ ① `tools/spec211_manual_verdicts.py`（★ 21 项**人工终判** ✓）
#     ★ ② `capabilities.yaml`（★ 每条的 `level` + `evidence` + `limitations` ✓）
#   ★★ **为什么不手写**：★ 手写会与两处真源脱节 ✗ —— ★ 而"表里写的"与"台账记的"
#     不一致，★ 正是本规格反复吃过的那类错（★ 覆盖表过时两次、台账判错两次 ✓）
# 判据:   ★★ 每项输出：★ **域 · 项 · 台账终判 · 对应能力 id · 能力 level · 真机证据有无**
#   ★ 并**如实标注**三类"非完成"：★ `不做`（★ 附依据 ✓）· ★ `待实测`（★ 没做 ✓）·
#     ★ **`未处理`**（★ 连台账都还没给它结论 —— ★ 本工具**照样列出来**，★ 不藏 ✓）
# 官方依据: 无（本规格的完成判据）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "mcp-server"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★ **项 → 能力 id** 的映射（★ 人工建，★ 21 项逐条可核 ✓）
ITEM_TO_CAP = {
    "截面属性": "section_properties",
    "缩放/变形": "scale_feature",
    "扫描曲面": "sweep_surface",
    "剪裁曲面": None,                     #: ★ 判"不做"（事实 419）⇒ 无能力 ✓
    "边界曲面": "surface_ruled",          #: ★ 仓里已有（直纹曲面 ✓）
    "取消剪裁": "untrim_surface",
    "裁剪/延伸焊件": "weldment_trim",
    "角撑板（焊件）": "weldment_gusset",
    "圆角焊缝": "fillet_weld_bead",
    "焊接符号": None,                     #: ★ 台账判"可做"，★ 但**尚未真机验** ⇒ 待处理 ✓
    "曲线驱动阵列": "curve_driven_pattern",   #: ★★ B8 翻案：改判「可做」⇒ stitched ✓
    "边界凸台": None,                     #: ★ 判"不做"（要 ACL）✓
    "特征识别/Instant3D": None,           #: ★ 判"不做"（官方无 API 入口）✓
    "成形工具": "forming_tool",             #: ★★★ 真机建成 ⇒ verified ✓
    "展开/折叠": None,                    #: ★ 已覆盖（`specs/209` 收口 ✓）
    "平板型式/导出 DXF": None,
    "爆炸直线": None,
    "零部件阵列": None,
    "SpeedPak": None,
    "序列 / 说明书（Assembly Visualization）": None,
    "装配体性能分析": None,
    "PDM": None,
}


def main() -> int:
    import spec211_manual_verdicts as MV

    caps = json.loads((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))["capabilities"]
    by_id = {c.get("id"): c for c in caps}

    rows = []
    for item, (domain, verdict, why) in MV.VERDICTS.items():
        cid = ITEM_TO_CAP.get(item)
        cap = by_id.get(cid) if cid else None
        rows.append({
            "domain": domain, "item": item, "ledger_verdict": verdict,
            "capability_id": cid,
            "capability_level": (cap or {}).get("level"),
            "has_evidence": bool((cap or {}).get("evidence")),
            "why": why[:120],
        })
    #: ★★ **21 项之外还有"未处理"的**（★ 台账没给它结论的）⇒ ★ 照样列出来，不藏 ✓
    missing = [i for i in ITEM_TO_CAP if i not in MV.VERDICTS]

    #: ★ 生成 markdown 表 ✓
    lines = ["| 域 | 项 | 台账终判 | 能力 id | 能力 level | 真机证据 |",
             "|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda x: (x["domain"], x["item"])):
        lines.append("| %s | %s | **%s** | %s | %s | %s |" % (
            r["domain"], r["item"], r["ledger_verdict"],
            ("`%s`" % r["capability_id"]) if r["capability_id"] else "—",
            ("`%s`" % r["capability_level"]) if r["capability_level"] else "—",
            ("★ 有" if r["has_evidence"] else "—")))
    table = "\n".join(lines)

    out = ROOT / "output" / "spec211-final-table.json"
    out.write_text(json.dumps({"rows": rows, "unhandled": missing}, ensure_ascii=False,
                              indent=1) + "\n", encoding="utf-8")
    md = ROOT / "output" / "spec211-final-table.md"
    md.write_text(table + "\n", encoding="utf-8")

    import collections
    c = collections.Counter(r["ledger_verdict"] for r in rows)
    print("★ 台账里的项 = **%d** 项 · 终判分布 = %s" % (len(rows), dict(c)))
    print("★★ 台账**没有**结论的项 = %d 项 ⇒ %s" % (len(missing), missing))
    print("★★ 其中**有能力条目**的 = %d 项 · `verified` = %d · `stitched` = %d"
          % (sum(1 for r in rows if r["capability_id"]),
             sum(1 for r in rows if r["capability_level"] == "verified"),
             sum(1 for r in rows if r["capability_level"] == "stitched")))
    print("★ 表 → %s" % md)
    print(table)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
