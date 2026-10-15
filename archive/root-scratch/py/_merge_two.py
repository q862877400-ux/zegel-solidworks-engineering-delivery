"""★ 合并两个仓库时手工处理的 2 个同名文件。"""

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
A = Path(r"D:\AI\SW")
B = Path(r"C:\swprojects\sw-skill-fork")

#: ── ① .gitignore = A 的规则 + B 的规则（★ 并集；★ B 的 `!` 例外保持在其父规则之后的原序）──
ga = (A / ".gitignore").read_text(encoding="utf-8").rstrip()
gb = (B / ".gitignore").read_text(encoding="utf-8").rstrip()
head = ("# ─────────────────────────────────────────────────────────────────────\n"
        "# ★ 2026-10-03 合并：本文件是**两份** .gitignore 的并集\n"
        "#   上半 = 原 D:\\AI\\SW（工作区）的规则 —— 排除 AI Solidworks/(314MB) · _raw/ 等大东西\n"
        "#   下半 = 原 sw-skill-fork（代码仓）的规则 —— Python / 构建 / CAD 产物\n"
        "#   ⚠ 上半**不可删**：删了那 314 MB 官方文档会变成入库。\n"
        "# ─────────────────────────────────────────────────────────────────────\n\n")
(A / ".gitignore").write_text(head + ga + "\n\n" + gb + "\n", encoding="utf-8")
print("  ① .gitignore 已合并：A %d 行 + B %d 行" % (len(ga.splitlines()), len(gb.splitlines())))

#: ── ② README：门面用 B 的（产品说明）；A 的原文另存，不丢 ──
old_a = (A / "README.md").read_text(encoding="utf-8")
(A / "README-workspace.md").write_text(
    "# ⚠ 本文件是**合并前**的工作区 README（历史存档）\n"
    "\n"
    "> ★ 2026-10-03：`D:\\AI\\SW` 与 `C:\\swprojects\\sw-skill-fork` 已合并为一个仓库，\n"
    "> 故下面这段原文里「代码本体在 `C:\\swprojects\\sw-skill-fork\\`（独立 git 仓库）」**已过时** ——\n"
    "> 现在**代码与本工作区在同一个仓库里**。原文保留，作为当时的设计记录。\n"
    "\n---\n\n" + old_a, encoding="utf-8")
(A / "README.md").write_text((B / "README.md").read_text(encoding="utf-8"), encoding="utf-8")
print("  ② README.md ← 代码仓的产品说明；A 的原文另存为 README-workspace.md（%d 字节）" % len(old_a))
