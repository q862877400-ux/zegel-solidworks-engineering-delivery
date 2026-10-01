"""把 ROADMAP 的「最近三次交接」段整体替换为 `_handover_new.md` 的内容。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（维护交接段）
# 文件:   D:\\AI\\SW\\docs\\ROADMAP.md 的「最近三次交接」段
# 定位:   轮 49 发现该段**陈旧**：标题说「最近三次」而实际只有 2 条有日期，
#         且都早于当前 HEAD（`caecffa` / `570c373` / `3df8670` vs `e26baea`）
#         ⇒ 它正是**上下文重置后用来恢复的那个东西**，陈旧等于失效。
# ⚠ 这是一次**替换**（有 deletions）⇒ 按**事实 61**：**逐条核对删掉的是不是那三条旧的**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
NEW = Path(r"D:\AI\SW\_handover_new.md").read_text(encoding="utf-8")

t = R.read_text(encoding="utf-8")
head = "最近三次交接:"
i = t.find(head)
if i < 0:
    print("  ✗ 找不到「最近三次交接:」"); raise SystemExit(1)
# 段尾：下一个「━━━」分隔行
j = t.find("━", i)
if j < 0:
    print("  ✗ 找不到段尾分隔行"); raise SystemExit(1)

old = t[i:j]
REMOVED = [l for l in old.splitlines() if l.strip() and not l.startswith("最近三次交接:")]

# ★ 事实 61 式核对：删掉的**必须是那三条旧交接**（按 commit 短哈希判）
EXPECTED = {"caecffa", "570c373", "3df8670"}
found = {h for h in EXPECTED if h in old}
print("  ── 删除前核对 ──")
print("    旧段里找到的旧 commit: %r（应含全部 3 个）" % sorted(found))
if found != EXPECTED:
    print("  ✗ 旧段内容与预期不符 ⇒ **停下**（按事实 61）"); raise SystemExit(1)
print("    旧段行数: %d" % len(REMOVED))

R.write_text(t[:i] + NEW + t[j:], encoding="utf-8")

after = R.read_text(encoding="utf-8")
print()
print("  ── 落盘核对 ──")
for h in EXPECTED:
    print("    旧 commit %s 已移出: %s" % (h, h not in after[i:i + 3000]))
for h in ("e26baea", "eadbd3a", "924407b"):
    print("    新 commit %s 已在: %s" % (h, h in after))
print("    文件行数: %d" % len(after.splitlines()))
