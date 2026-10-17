"""★ 给 F/G/H/I/J 那 15 份对账稿各加**一行口径图例**（★ 处置 `JUDGE-F_G_H_I_J` 🔴 #1）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tools/add_polarity_legend.py
# 定位:   ★ `JUDGE-F_G_H_I_J.md` 的 🔴 **#1** 逐字：「★ **全组口径分裂**：「成立」= bug 还是 = pass，
#   ★ 15 份稿分成两派**且无一处声明**」· ★ 建议动作：「★ 在 15 份稿各加**一行图例**，
#   ★ 或统一改写为「判为缺陷 / 判为达标 / 存疑」」·
#   ★★ 而它**自己已给出极性表**（§〇）：★ 极性 **A**（★ 成立 = 缺陷成立）**11 份** ·
#   ★ 极性 **B**（★ 成立 = 达标）**4 份** ✓
#   ★★★ **为什么值得做**（★ 裁判逐字）：「★ **不做这一条，任何跨文件的「成立率」都不可比**」✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
Q = REPO / "specs" / "202-user-coverage-gaps" / "recon" / "verify50"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ★★ 裁判 §〇 的极性表（★ **逐字取自裁判稿**，★ 不是我判的）
POLARITY_A = ["vd50-F-1.md", "vd50-F-3.md", "vd50-F-4.md", "vd50-F-5.md",
              "vd50-H-2.md", "vd50-H-3.md", "vd50-H-4.md",
              "vd50-I-1.md", "vd50-I-2.md", "vd50-I-3.md", "vd50-J-1.md"]
POLARITY_B = ["vd50-G-1.md", "vd50-G-2.md", "vd50-G-3.md", "vd50-J-2.md"]

LEGEND_A = (
    "> 🏷 **口径图例（★ 2026-10-04 接手轮补，★ 处置 `JUDGE-F_G_H_I_J` 🔴 #1）**：\n"
    "> ★ 本稿里「**成立**」= **缺陷成立 = 对不上**（★ 极性 A）；\n"
    "> ★★ 与裁判稿统一的说法对照：**成立 → 判为缺陷** · **不成立 → 判为达标** · **存疑 → 存疑**。\n"
    "> ★★★ **原稿用词一律保留**（★ 便于回查），★ 本行只是**声明口径**。\n"
    "> ★★★★ 依据：`JUDGE-F_G_H_I_J.md` §〇 的极性表 —— ★ 本稿属**极性 A**（★ 11 份之一）✓\n"
)
LEGEND_B = (
    "> 🏷 **口径图例（★ 2026-10-04 接手轮补，★ 处置 `JUDGE-F_G_H_I_J` 🔴 #1）**：\n"
    "> ★★ **注意：本稿的「成立」极性与其他多数稿相反** —— 本稿里「**成立**」= **达标 = 不构成问题**（★ 极性 B）；\n"
    "> ★ 与裁判稿统一的说法对照：**成立 → 判为达标** · **不成立 → 判为缺陷** · **存疑 → 存疑**。\n"
    "> ★★★ **原稿用词一律保留**（★ 便于回查），★ 本行只是**声明口径**。\n"
    "> ★★★★ 依据：`JUDGE-F_G_H_I_J.md` §〇 的极性表 —— ★ 本稿属**极性 B**（★ 仅 4 份）✓\n"
)
MARK = "🏷 **口径图例"


def _insert(path: Path, legend: str) -> str:
    if not path.is_file():
        return "★ 不存在"
    text = path.read_text(encoding="utf-8", errors="replace")
    if MARK in text:
        return "★ 已有图例（跳过）"
    lines = text.splitlines(keepends=True)
    #: ★ 插在**第一个标题行之后**（★ 若是 `# 标题`，插在它下面；★ 否则插在文件头）
    idx = 0
    for i, l in enumerate(lines[:6]):
        if l.lstrip().startswith("#"):
            idx = i + 1
            break
    lines.insert(idx, "\n" + legend)
    path.write_text("".join(lines), encoding="utf-8")
    return "★ 已加"


def main() -> int:
    n_a = n_b = 0
    for name in POLARITY_A:
        r = _insert(Q / name, LEGEND_A)
        print("   %-18s %s" % (name, r))
        n_a += 1
    print()
    for name in POLARITY_B:
        r = _insert(Q / name, LEGEND_B)
        print("   %-18s %s（★ 极性 B）" % (name, r))
        n_b += 1
    print()
    print("★ 极性 A: %d 份 · ★ 极性 B: %d 份 ⇒ 共 %d 份" % (n_a, n_b, n_a + n_b))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
