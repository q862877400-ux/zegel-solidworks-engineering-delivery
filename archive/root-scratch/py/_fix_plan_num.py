import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"D:\AI\SW\docs\plan-10h.md")
NOTE = """> ★★ **编号顺移（2026-10-01 轮 228 发现并更正）**：原计划把 W4–W7 编成 134–137，
> 但 **`specs/134-static-simulation-reverified` 是已提交的真实特性**（5 件套、`79cdac1`）
> ⇒ 按 Spec Kit **flow-forward（完成的目录不可变、需求变了开新号）**，W4 起**顺移一号**：
> **W4=135 · W5=136 · W6=137 · W7=138**。
> ⚠ 这正是「编号必须现场核、不能照计划抄」的一个实例。

"""
t = p.read_text(encoding="utf-8")
if "编号顺移（2026-10-01 轮 228" in t:
    print("  已在，跳过")
else:
    anchor = "### W1 · 草图只读族"
    i = t.find(anchor)
    assert i > 0, "锚点不符"
    t = t[:i] + NOTE + t[i:]
    for a, b in (
        ("W4 · 零件特征族（`specs/134`）", "W4 · 零件特征族（`specs/135`）"),
        ("W5 · 检查 / 测量 / 反馈族（`specs/135`）", "W5 · 检查 / 测量 / 反馈族（`specs/136`）"),
        ("W6 · 装配族（`specs/136`）", "W6 · 装配族（`specs/137`）"),
        ("W7 · 仿真载荷包装层（`specs/137`）", "W7 · 仿真载荷包装层（`specs/138`）"),
    ):
        assert a in t, "锚点不符: %s" % a
        t = t.replace(a, b, 1)
    p.write_text(t, encoding="utf-8")
    print("  ✓ 计划编号已顺移并写明原因")
u = p.read_text(encoding="utf-8")
for k in ("编号顺移", "specs/135", "specs/136", "specs/137", "specs/138"):
    print("  含「%s」: %s" % (k, k in u))
