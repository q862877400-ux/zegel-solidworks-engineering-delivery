"""★ 抽**官方枚举的规模** —— ★ 矩阵第三轴「种类」的官方来源（★ 不是猜的）。

★ 为什么需要它（★ 业主的问题：★「你这个矩阵是否就是要包含所有『工具』分母的矩阵」）：
  ★★ 两轴矩阵（操作 × 对象）**不足以当分母** —— ★ 因为「建 × 特征」一格里有**几十个**工具，
    ★ 拿格子数当分母会把那一格算成 1。
  ⇒ ★★★ 所以缺**第三轴「种类」**。★ 而好消息：★ **官方自己在枚举里给了它** ——
    ★ `C:\\swapi\\enums\\*.md` 的 front-matter 有 **`enum_member_count`**（★ 官方自己数的）。
★ 产出 `output/official-enum-scale.json`：★ 每个枚举的名字 · 成员数 · 描述（★ 用来判它是不是"种类轴"）。
★ 只读官方文档。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/build_enum_scale.py
# 定位:   抽**官方枚举的规模** —— ★ 矩阵第三轴「种类」的官方来源（★ 不是猜的）。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
E = Path(r"C:\swapi\enums")
OUT = Path(Path(__file__).resolve().parents[1] / "output" / "official-enum-scale.json")

#: ★★ 与「种类轴」直接相关的枚举（★ 它们枚举的是"东西的种类"，★ 不是状态/标志）
KIND_PATTERNS = [
    ("特征种类", r"^swFeatureNameID_e$"),
    ("草图图元种类", r"^swSketchSegments?_e$|^swSketchPoint|^swSketchConstraint"),
    ("孔/槽种类", r"swWzdGeneralHoleTypes|swWzdHoleStandards|swHole"),
    ("标注/注释种类", r"swAnnotationType|swDisplayDimension|swDimensionType|swNote|swBalloon"),
    ("视图种类", r"swDrawingViewTypes|swViewType|swDetViewStyle|swBreakLineStyle|swSectionView"),
    ("阵列/镜像种类", r"swPattern|swMirror"),
    ("圆角/倒角种类", r"swFillet|swChamfer|swSimpleFillet"),
    ("装配配合种类", r"swMateType|swMateAlign|swMateEntityType|swAddMateError"),
    ("几何实体种类", r"swSelectType|swBodyType|swSurfaceType|swCurveType|swTopology"),
    ("导出/交付种类", r"swExport|swSaveAs|swFileSave|swPDF|swDXF|swSTL"),
    ("仿真/校核种类", r"swsStudy|swsMesh|swsUnit|swsResult|swsLoad|swsRestraint|swsTopology"),
    ("钣金种类", r"swSheetMetal|swBend|swFlange|swRip|swCorner"),
    ("焊件种类", r"swWeldment|swStructuralMember|swCutList|swGusset|swEndCap"),
    ("模具种类", r"swMold|swPartingLine|swPartingSurface|swCoreCavity|swShutOff"),
    ("材料/属性种类", r"swMaterial|swCustomInfo|swConfiguration|swEquation|swDesignTable"),
    ("错误/状态（★ 非种类轴）", r"swError|swWarning|swStatus|swResult\b|swReturn"),
]


def main() -> int:
    started = time.time()
    rows = []
    for f in sorted(E.glob("*.md")):
        try:
            head = f.read_text(encoding="utf-8", errors="replace").split("\n## ", 1)[0]
        except Exception:                                                 # noqa: BLE001
            continue
        m = re.search(r"enum_member_count:\s*(\d+)", head)
        if not m:
            continue
        desc = ""
        dm = re.search(r"^# .*?\n\n## Description\n(.*?)(?=\n## )", f.read_text(
            encoding="utf-8", errors="replace"), re.S | re.M)
        if dm:
            desc = dm.group(1).strip().splitlines()[0][:120]
        rows.append({"enum": f.stem, "members": int(m.group(1)), "desc": desc})

    total = sum(r["members"] for r in rows)
    #: ★ 按"种类轴"归类
    buckets: dict = {}
    for r in rows:
        tag = "（未归类）"
        for name, pat in KIND_PATTERNS:
            if re.search(pat, r["enum"], re.I):
                tag = name
                break
        b = buckets.setdefault(tag, {"enums": 0, "members": 0, "top": []})
        b["enums"] += 1
        b["members"] += r["members"]
        b["top"].append((r["members"], r["enum"]))
    for b in buckets.values():
        b["top"] = [n for _, n in sorted(b["top"], reverse=True)[:6]]

    OUT.write_text(json.dumps({
        "at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "enums_with_count": len(rows),
        "total_enum_members": total,
        "buckets": buckets,
        "all": sorted(rows, key=lambda r: -r["members"]),
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print("★ 官方枚举：**%d** 个带 `enum_member_count` ⇒ 成员合计 **%d**" % (len(rows), total))
    print()
    print("%-26s %-8s %-8s %s" % ("★ 种类轴（归类）", "枚举数", "成员数", "最大的几个"))
    print("-" * 118)
    for tag, b in sorted(buckets.items(), key=lambda kv: -kv[1]["members"]):
        print("%-26s %-8d %-8d %s" % (tag[:25], b["enums"], b["members"],
                                      ", ".join(b["top"])[:58]))
    print()
    print("★ 单枚举最大的 12 个（★ 这些才是「一种东西有几种」的直接读数）：")
    for r in sorted(rows, key=lambda r: -r["members"])[:12]:
        print("   %-46s %4d  %s" % (r["enum"][:45], r["members"], r["desc"][:44]))
    print()
    print("★ 产出:", OUT, "（%.1f s）" % (time.time() - started))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
