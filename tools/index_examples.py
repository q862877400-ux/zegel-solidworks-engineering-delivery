#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 C:\\swapi 的官方示例按 14 个功能域归类，产出「域 × 官方示例」索引。

为什么需要这个
--------------
capability-matrix.md 回答的是「有哪些成员、参数什么顺序」（接口清单）。
本脚本回答的是另一半：「**这个功能官方怎么用**」——AGENTS.md §四 4.1 写明
「★ Example 页比方法页有用 10 倍」，而此前只用了 member/type/enum/find/domain，
**examples 这条路一次都没走过**。

输入：C:\\swapi\\examples\\*.md（2,839 个官方示例）
输出：_raw\\examples_by_domain.txt  +  _raw\\example_domain_index.json

⚠ 本脚本只做文件名的关键词归类与体积统计，**不执行任何示例代码**，
  不导入任何 CAD 模块、不连接 SolidWorks（见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

EXAMPLES = Path(r"C:\swapi\examples")

#: 14 个功能域 -> 命中该域的关键词。顺序即匹配优先级，���靠前越具体。
DOMAIN_KEYWORDS: list[tuple[str, list[str]]] = [
    ("孔与螺纹", ["holewizard", "hole", "thread", "tap", "countersink", "cskhole",
              "weldmenthole", "straightpipe", "cosmeticthread"]),
    ("钣金", ["sheetmetal", "sheet_metal", "hem", "flange", "bend", "gusset",
            "louver", "bead", "draft", "ruleline", "wrangle"]),
    ("焊件", ["structure_system", "structuremember", "weldment", "weldbead",
            "weld", "cutlist", "profile"]),
    ("曲面", ["surface", "loft", "sweep", "knit", "trim", "refill", "radiate",
            "lofted", "offset"]),
    ("工程图", ["drawing", "sheet", "view", "annotation", "dimension", "bomtable",
              "balloon", "sectionview", "detailview", "titleblock", "drawview",
              "insertmodelannotations", "tableannotation", "hightlight"]),
    ("装配", ["assembly", "component", "mate", "explode", "mirror", "sketchblock",
            "insertcomponent", "fixcomponent", "lightweight"]),
    ("零件特征", ["extrusion", "revolve", "fillet", "chamfer", "pattern", "rib",
              "shell", "draft", "mirror", "straighten", "boundary", "delete",
              "directedit", "boss", "loft", "swept", "knit", "thicken"]),
    ("草图", ["sketch", "constraint", "dimension", "spline", "slot", "arc",
            "circle", "rectangle", "polygon", "offsetentity"]),
    ("几何与拓扑", ["body", "face", "edge", "vertex", "loop", "curve", "surface",
               "boundingbox", "midsurface", "topology", "closestpt", "measure"]),
    ("质量属性与导出", ["masspropert", "export", "step", "iges", "stl", "dxf",
                   "pdf", "3d_pdf", "packandgo", "saveas", "print", "convert"]),
    ("配置·材料·自定义属性", ["configuration", "designtable", "custompropert",
                     "material", "render", "displaystate", "appearance", "config"]),
    ("应用与会话", ["opensave", "template", "macro", "preference", "userpref",
                "addin", "application", "document", "isvisible", "activate"]),
    ("仿真(需许可证)", ["simulation", "study", "cosworks", "cw", "load", "restraint",
                  "fixture", "mesh", "stress", "displacement", "fatigue"]),
    ("路由/Composer/PDM", ["routing", "composer", "pdm", "vault", "costing",
                    "toolbox", "sustainability", "checkin", "checkout"]),
]

#: 落到多个域时的归属提示（同一示例可服务多个域，此处只记首个命中域）
_LANG = re.compile(r"_Example_(CSharp|VBNET|VB|CPlusPlus_COM|Java|ObjC)")


def classify(stem: str) -> tuple[str, str]:
    """返回 (域, 语言)。未命中任何域则归入「未分类」。"""
    lang_m = _LANG.search(stem)
    lang = lang_m.group(1) if lang_m else "?"
    low = stem.lower()
    for domain, keys in DOMAIN_KEYWORDS:
        if any(k in low for k in keys):
            return domain, lang
    return "未分类", lang


def main() -> int:
    if not EXAMPLES.is_dir():
        print(f"[FATAL] 找不到示例目录: {EXAMPLES}", file=sys.stderr)
        return 2

    files = sorted(p.stem for p in EXAMPLES.glob("*.md"))
    by_domain: dict[str, list[str]] = defaultdict(list)
    langs: dict[str, int] = defaultdict(int)
    for stem in files:
        domain, lang = classify(stem)
        by_domain[domain].append(f"{stem} [{lang}]")
        langs[lang] += 1

    out_txt = Path(Path(__file__).resolve().parents[1] / "_raw" / "examples_by_domain.txt")
    out_json = Path(Path(__file__).resolve().parents[1] / "_raw" / "example_domain_index.json")

    lines = [
        f"# 官方示例按域归类（共 {len(files)} 个）",
        "",
        "生成方式：对 C:\\swapi\\examples\\*.md 的**文件名**做关键词归类，",
        "不解析正文、不执行任何示例代码（AGENTS.md 铁律 2）。",
        "",
        "## 语言分布",
    ]
    for lang, n in sorted(langs.items(), key=lambda kv: -kv[1]):
        lines.append(f"  {lang:<16} {n}")
    lines.append("")
    lines.append("## 各域示例数")
    for domain, _ in DOMAIN_KEYWORDS:
        n = len(by_domain.get(domain, []))
        lines.append(f"  {domain:<24} {n}")
    n_miss = len(by_domain.get("未分类", []))
    lines.append(f"  {'未分类':<24} {n_miss}")
    lines.append("")
    lines.append("=" * 78)
    for domain, _ in DOMAIN_KEYWORDS + [("未分类", [])]:
        items = by_domain.get(domain, [])
        if not items:
            continue
        lines.append(f"\n## {domain}（{len(items)} 个）")
        for it in items:
            lines.append(f"  {it}")

    out_txt.write_text("\n".join(lines), encoding="utf-8")
    out_json.write_text(
        json.dumps(
            {"total": len(files), "languages": dict(langs),
             "by_domain": {k: v for k, v in sorted(by_domain.items())}},
            ensure_ascii=False, indent=2),
        encoding="utf-8")

    print(f"示例总数 {len(files)} -> {out_txt}")
    print("语言分布: " + ", ".join(f"{k}={v}" for k, v in sorted(langs.items(), key=lambda kv: -kv[1])))
    print("各域示例数:")
    for domain, _ in DOMAIN_KEYWORDS:
        print(f"  {domain:<24} {len(by_domain.get(domain, []))}")
    print(f"  {'未分类':<24} {n_miss}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
