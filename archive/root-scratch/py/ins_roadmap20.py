"""把 `_roadmap_20.md` 插到 ROADMAP 的 `阻塞:` 行**之前**（复用轮 48 验证过的方法）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（记录本轮游标）
# 文件:   D:\\AI\\SW\\docs\\ROADMAP.md（§一 游标）
# 定位:   按**事实 48**（长内容走独立文件 + 最短脚本）+ **事实 61**（跑完先看 `git diff --stat`）。
#         ⚠ 轮 48 用同样方法成功；`edit` 工具在 ROADMAP 上会拒（原因未明），故沿此法。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
BLOCK = Path(r"D:\AI\SW\_roadmap_20.md").read_text(encoding="utf-8")

lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
if i is None:
    print("  ✗ 找不到 `阻塞:` 行"); raise SystemExit(1)
before = "".join(lines)
if "`converge` 步已对 002 跑通" in before:
    print("  ⚠ 已经插过了"); raise SystemExit(0)

new = "".join(lines[:i]) + BLOCK + "".join(lines[i:])

# ★ 事实 61 式核对：**只应是插入**（原内容一行不改、一行不删）
assert len(new) > len(before), "新内容应更长"
assert new.replace(BLOCK, "") == before, "**除了插入的块，其余必须逐字节相同**"

R.write_text(new, encoding="utf-8")
print("  ✓ 已插入（%d 行 → %d 行）" % (len(before.splitlines()), len(new.splitlines())))
print("  ✓ 核对通过：删掉插入块后与原内容**逐字节相同**")
