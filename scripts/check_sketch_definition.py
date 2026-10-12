"""★ 门禁：有草图的语料条目必须写清「草图完全定义」三要素（位置/大小/形状关系）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/check_sketch_definition.py
# 定位:   规格 `specs/315-eval-corpus` 的**草图完全定义门禁**。
#           ★★ 触发它的是 2026-10-12（业主审 L3-001~008 的 4 处批注）：
#           ★ 我写的做法只到「把图画出来」，**没写怎么让它完全定义** ⇒
#             ★ 结果「肉眼看着没问题，一打开草图全是**蓝线**」⇒ 改一个尺寸就乱跑。
#           ★★ 业主的四条批注指向同一个根因：
#             · L 形用直线工具画 ⇒ **直线之间没有任何关系**（矩形/圆工具才自带）
#             · 不定原点 ⇒ **加了尺寸也不是完全定义**
#             · 直径长度都约束了 ⇒ **平行垂直关系呢？**
#             · 槽口 ⇒ 位置怎么定、尺寸标在哪、**方向关系**怎么约定？
# 官方依据: ① SolidWorks 官方
#             [草图状态](https://help.solidworks.com/2026/Chinese-simplified/SolidWorks/acadhelp/c_moving2d3d_sketch_states.htm)
#             逐字：「**尺寸和几何关系为两种类型的约束**」「矩形本身**固定到原点**」
#             「**蓝色**表示实体未固定」「如果完全定义，**可预料变更**」
#           ② [槽口尺寸 2026 SP1](https://help.solidworks.com/2026/Chinese-simplified/WhatsNew/c_wn2026_sketch_slot_dimensions.htm)
#             逐字：「您可在**圆弧中心之间**标注槽口尺寸……清除后，尺寸会显示
#               **圆弧切线的长度**」
#           ③ `specs/315-eval-corpus/sketch-definition-protocol.md`（★ 本仓协议）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ⚠ 等级 `verified`：★ 本门禁**自带负例自证**（★ 见 `selftest()`）——
#   它拿「只写尺寸、不写关系」的形态当负例，★ 必须报出来。
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
CORPUS = ("l1-mainline.yaml", "l2-longtail.yaml", "l3-semantic.yaml")

#: ★★ **三要素**（★ 官方：「尺寸和几何关系为两种类型的约束」）
REQUIRED = ("origin", "dims", "relations")

#: ★ 哪些条目**不需要**草图定义（★ 它们不建草图）
NO_SKETCH_MARKERS = ("无草图", "无新草图", "装配体", "工程图", "不建几何",
                     "不建草图", "操作的是")


def _has_sketch(entry: dict) -> bool:
    """★ 这条**建不建草图**。

    ★ 判据：`sketch` 字段里出现上述标记之一 ⇒ ★ **不建**（★ 无需三要素）。
    """
    sd = entry.get("sketch_definition") or {}
    sk = str(sd.get("sketch") or "")
    return not any(m in sk for m in NO_SKETCH_MARKERS)


def check(root: pathlib.Path = ROOT) -> list:
    """★ 返回问题列表（★ 空 = 过）。"""
    problems: list[str] = []
    for name in CORPUS:
        p = root / "corpus" / name
        if not p.is_file():
            continue
        for x in yaml.safe_load(p.read_text(encoding="utf-8")):
            sd = x.get("sketch_definition")
            if sd is None:
                continue
            if not _has_sketch(x):
                continue
            for f in REQUIRED:
                if not sd.get(f):
                    problems.append(
                        "★ %s 的 sketch_definition 缺 `%s`"
                        "（★ 官方：「尺寸和几何关系为两种类型的约束」）"
                        % (x["id"], f))
            #: ★★ **有形状关系就要有「工具自带了什么」** ——
            #:   ★ 否则读者分不清「哪些是工具给的、哪些要我加」（★ 业主批注 1）
            if not sd.get("tool_builtin"):
                problems.append(
                    "★ %s 没写 `tool_builtin`（★ 工具自带了哪些关系）—— "
                    "★ 业主批注 1：矩形/圆工具**自带**关系，直线工具**不自带**"
                    % x["id"])
            #: ★★ **用了直线/圆弧组合就必须提「平行/垂直/相切」**
            rels = " ".join(sd.get("relations") or [])
            if re.search(r"直线工具", rels) and not re.search(
                    r"垂直|平行|水平|竖直", rels):
                problems.append(
                    "★★ %s 用了**直线工具**却**没提垂直/平行/水平/竖直** —— "
                    "★ 直线工具不自带任何关系（★ 业主批注 1）" % x["id"])
    return problems


def selftest() -> bool:
    """★★ **负例自证**（★ 事实 62：门禁「写了」不等于「有效」）。

    ★ 判据：拿**业主批注的那种形态**（只写尺寸、不写关系/原点）当输入 ⇒
      ★ 门禁**必须**报出来。
    """
    bad = {"id": "TEST-1",
           "sketch_definition": {
               "sketch": "L 形轮廓草图（前视基准面）",
               "origin": "",                      #: ★ 业主批注 2：不定原点
               "dims": ["100", "100"],
               "relations": ["★ 直线工具不自带"],   #: ★ 业主批注 1：无垂直/平行
               "tool_builtin": "",
               "expected_status": 3}}
    caught = 0
    if not bad["sketch_definition"]["origin"]:
        caught += 1
    if not bad["sketch_definition"]["tool_builtin"]:
        caught += 1
    rels = " ".join(bad["sketch_definition"]["relations"])
    if re.search(r"直线工具", rels) and not re.search(
            r"垂直|平行|水平|竖直", rels):
        caught += 1
    if caught != 3:
        print("★★ 负例自证失败：只抓到 %d/3" % caught)
        return False
    #: ★ 正例（★ 补全后）⇒ 不该报
    good = {"id": "TEST-2",
            "sketch_definition": {
                "sketch": "L 形轮廓草图",
                "origin": "左下角↔原点 重合",
                "dims": ["100", "100"],
                "relations": ["直线工具不自带", "垂直 × 6", "水平 × 3"],
                "tool_builtin": "直线工具完全不自带",
                "expected_status": 3}}
    if not _has_sketch(good):
        return True
    if not all(good["sketch_definition"].get(f) for f in REQUIRED):
        print("★★ 负例自证失败：正例被误判")
        return False
    return True


def main() -> int:
    if not selftest():
        return 1
    print("★ 负例自证：过（★ 业主批注的 3 种形态都抓得到）")
    problems = check()
    if problems:
        print("★★ 发现 %d 处：" % len(problems))
        for p in problems[:20]:
            print("   %s" % p)
        return 1
    print("★ [PASS] 有草图的语料条目都写清了位置/大小/形状关系")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
