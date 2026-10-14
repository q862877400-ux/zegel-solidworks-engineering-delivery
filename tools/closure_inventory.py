"""★ 批次⑱：**收口盘点** —— 全仓还剩什么没扫（★ 逐处给结论）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/closure_inventory.py
# 定位:   规格 `specs/332-known-facts-triage` 的**收口盘点**。
#           ★★ 业主 2026-10-14 的收口判据：「各批有明确的『已扫 / 已判断』结论」
#             + 「**连续 2 轮扫出新东西但全部判定为放过 ⇒ 认为已挖干净**」。
#           ★ 本工具逐处给「已扫 / 剩什么 / 结论」。
# 官方依据: 本仓文件系统 + 外部资源清单
# 许可:   本仓库 MIT。★ 外部资源只读。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]
HOME = pathlib.Path.home()

#: ★★ **已扫完的处**（★ 逐处带「扫了什么 / 吸收了多少 / 结论」）
DONE: list = [
    ("① `docs/known-facts.md`", "**557 条**逐条处置", "吸收 25 · 放过 532 · 未判定 0",
     "✅ 完成（★ 有门禁 `check_known_facts_triage.py`）"),
    ("② `examples/`", "16 个", "吸收 1（★ 已由别处覆盖）", "✅ 完成"),
    ("③ `apps/`", "512 个", "吸收 8（★ 全在 `workbench-ui`）", "✅ 完成"),
    ("④ `archive/`", "2727 个", "吸收 0（★ 三类理由已登记）", "✅ 完成"),
    ("⑤ 官方文档 `sldworksapi`", "2769 个", "吸收 0（★ 关键内容已在 A 阶段）",
     "✅ 完成"),
    ("⑥ `docs/`（排除①覆盖的）", "142 个", "吸收 2", "✅ 完成"),
    ("⑦ `references/`", "**22 篇**", "★ 吸收 17", "✅ 完成（★ 精度 39%）"),
    ("⑧ `subskills/`", "5 个 SKILL.md", "★ 吸收 12", "✅ 完成（★ 精度 41%）"),
    ("⑨ 官方文档其余目录", "28653 个", "吸收 0（★ 有明确原因）", "✅ 完成"),
    ("⑩–⑭ `specs`/`tests`/`mcp-server`/`tools`/`scripts`", "3823 个",
     "★ 绝大多数是**本仓自己的产出**（★ 自引）", "✅ 完成（★ 自引不算新知识）"),
    ("⑮ `mech-design` 全库", "**99 篇**逐篇处置",
     "吸收 39 · 放过 60 · 未判定 0", "✅ 完成（★ 有台账）"),
    ("⑯ `mech-design` 剩余 78 篇", "已含在⑮", "吸收 12", "✅ 完成"),
    ("⑰ `mech-design` 决策树 + 接口表", "2 篇", "★★★★★ 决策树 · 136 接口名",
     "✅ 完成"),
    ("⑱ `mech-design` 3 个 YAML", "225 行 + 13.5 KB", "★ 材料 14 种 + 设计规则",
     "✅ 完成（★ 含 YAML 错处置）"),
    ("⑲ `mech-design` 17 个数据表", "**1169 行**", "★ 全部接成 `standard_parts.py`",
     "✅ 完成"),
]

#: ★★ **还剩什么**（★ 逐处带「是什么 / 值不值得扫 / 结论」）
REMAIN: list = [
    ("`mech-design` 的 **24 个 .ps1 校核脚本**",
     "★ 齿轮/V带/弹簧/轴承/疲劳/焊缝/GD&T/图幅 的**可跑算例**",
     "⚠ **值得** —— ★ 它们是**已跑通的计算**（★ 索引逐条标「已跑通」）；"
     "★ 而本仓的选型计算**没有这些**",
     "★★ **下一轮该做**"),
    ("`mech-design/tools/sw_know.py`（25.8 KB）",
     "★ 该 skill 的**检索入口**（★ `AGENTS.md` §四也提到它）",
     "⚠ 它是**查自己知识库**的工具 ⇒ ★ 而本仓**已直接读文件** ⇒ 价值低",
     "★ 放过（★ 功能已被本仓的直读覆盖）"),
    ("`C:/swprojects/` 的 **20 个外部项目克隆**",
     "★ 四家已并入（★ `docs/sources.md`）；★ 其余 16 家",
     "⚠ 本仓 `docs/sources.md` 已有「逐项能补什么 + 许可判定表」⇒ "
     "★ 而**逐一重扫**成本高、★ 收益低（★ 已判过）",
     "★ 放过（★ 已由 `docs/sources.md` 判过）"),
    ("`AI Solidworks/` 的**模型/截图/手册**（★ 非 `官方文档`）",
     "★ 官方手册 + 模型库 + 截图",
     "⚠ **手册**可能含方法；★ **模型/截图**是素材",
     "⚠ **部分待查**（★ 手册目录）"),
    ("`output/`（8973 个 · 498 MB）",
     "★ 本仓**自己的构建产物/证据**",
     "★ 是产物 ⇒ ★ **不是知识源**",
     "★ 放过"),
    ("`.api-signatures/`（★ gitignore）",
     "★ 签名索引缓存",
     "★ 是缓存 ⇒ ★ 不是知识源",
     "★ 放过"),
]


def main() -> int:
    print("=" * 74)
    print("★ 收口盘点（规格 332 · 批次⑱）")
    print("=" * 74)
    print()
    print("## 一、已扫完的（★ 逐处带结论）")
    print()
    for what, scope, gain, verdict in DONE:
        print("★ %s" % what)
        print("   扫了：%s" % scope)
        print("   吸收：%s" % gain)
        print("   结论：%s" % verdict)
    print()
    print("## 二、还剩什么（★ 逐处带判断）")
    print()
    for what, iswhat, worth, verdict in REMAIN:
        print("★ %s" % what)
        print("   是什么：%s" % iswhat)
        print("   值不值得：%s" % worth)
        print("   结论：%s" % verdict)
    print()
    #: ★★ 落盘
    out = ROOT / "specs" / "332-known-facts-triage" / "closure-inventory.md"
    L = ["# 收口盘点（规格 332 · 批次⑱）", "",
         "**判据**（★ 业主 2026-10-14 的收口条件）：",
         "1. ★ 各批都有明确的「已扫 / 已判断」结论",
         "2. ★★ **连续 2 轮扫出新东西但全部判定为放过 ⇒ 认为已挖干净**",
         "", "---", "",
         "## 一、已扫完的（%d 处）" % len(DONE), "",
         "| 处 | 扫了什么 | 吸收 | 结论 |", "|---|---|---|---|"]
    for what, scope, gain, verdict in DONE:
        L.append("| %s | %s | %s | %s |" % (what, scope, gain, verdict))
    L += ["", "## 二、还剩什么（%d 处）" % len(REMAIN), "",
          "| 处 | 是什么 | 值不值得 | 结论 |", "|---|---|---|---|"]
    for what, iswhat, worth, verdict in REMAIN:
        L.append("| %s | %s | %s | %s |" % (what, iswhat, worth, verdict))
    L.append("")
    out.write_text("\n".join(L), encoding="utf-8")
    print("★ ⇒ %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
