"""★ 批次①·续：把 221 条「该吸收」的事实**按主题聚类**，找出与 L3 相关的。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/cluster_known_facts.py
# 定位:   规格 `specs/332-known-facts-triage` —— 把粗筛出的「该吸收」条目**按主题聚类*
#           *，★ 优先看**与 L3 那 24 条做法直接相关**的。
# 官方依据: `output/known-facts-index.json`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import collections
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]
IDX = ROOT / "output" / "known-facts-index.json"

#: ★★ **主题词表**（★ 与我的 L3 24 条做法直接对应的排在前面）
TOPICS = {
    "① 草图/约束/完全定义": r"(草图|几何关系|完全定义|约束|关系|sg[A-Z]|SketchAdd)",
    "② 倒角/圆角": r"(倒角|圆角|Chamfer|Fillet)",
    "③ 孔/螺纹": r"(孔|螺纹|Thread|沉头|沉孔|底孔|tap)",
    "④ 槽/键槽": r"(槽|键槽|Slot|keyway)",
    "⑤ 拉伸/旋转/切除": r"(拉伸|旋转|回转|切除|Extrus|Revolv|Cut)",
    "⑥ 阵列/镜像": r"(阵列|镜像|Pattern|Mirror)",
    "⑦ 特征顺序/依赖": r"(顺序|特征树|依赖|父|子特征|SubFeature)",
    "⑧ 判据/回读/验证": r"(判据|回读|验证|证据|持久化|ForceRebuild|None)",
    "⑨ 选择/选边/选面": r"(选择|选边|选面|Select|Entity)",
    "⑩ 单位": r"(单位|毫米|米|mm|换算)",
    "⑪ 工程图/标注": r"(工程图|标注|尺寸|视图|Drawing|Dimension)",
    "⑫ 装配/配合": r"(装配|配合|Mate|自由度)",
    "⑬ 导出/交付": r"(导出|STEP|STL|DXF|PDF|交付)",
}


def main() -> int:
    d = json.loads(IDX.read_text(encoding="utf-8"))
    facts = d["facts"]
    absorb = d["buckets"]["absorb"]
    print("★ 「该吸收」%d 条 · 按主题聚类：" % len(absorb))
    print()
    grouped: dict[str, list] = collections.defaultdict(list)
    for k in absorb:
        b = facts[k]["body"]
        for topic, pat in TOPICS.items():
            if re.search(pat, b):
                grouped[topic].append(k)
                break
        else:
            grouped["⑭ 其他"].append(k)
    for topic in list(TOPICS) + ["⑭ 其他"]:
        ks = grouped.get(topic, [])
        print("★ %-24s %3d 条" % (topic, len(ks)))
    print()
    #: ★★ 落盘逐主题清单
    out = ROOT / "output" / "known-facts-topics.json"
    out.write_text(
        json.dumps({k: v for k, v in grouped.items()}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print("★ ⇒ %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
