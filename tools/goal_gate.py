"""★ Stop hook 的**验收条件**：`output/AUTO_HANDOFF.md` ② 段没有编号待办 ⇒ exit 0（达成）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/GOAL.md（★ 本文件被它当 `- [ ] cmd:` 行引用）· output/AUTO_HANDOFF.md（
# 每轮交接单）
# skill `goal-handoff` 的 assets/goal-gate.sh（★ **门**在 `.codebuddy/hooks/goal-gate.sh
# `；
#         ★ 本文件只是它逐条执行的**其中一条验收命令**）
# 定位:   ★★ **条件**（本文件，exit 0/1）与**门**（`goal-gate.sh`，exit 0/2）**分开** ——
#         门负责安全阀与反馈，条件只管「达成没达成」。★ 这是 skill §2.3 与 §四 的架构。
# 判据:   `AUTO_HANDOFF.md` ② 段的**编号待办数 == 0**（★ **不是**自报「我做完了」）。
# 官方依据: WorkBuddy Hooks 参考（Stop 事件；`exit 2` = 阻止停止）
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读两个 md；★ 不碰仓库代码、不碰 SolidWorks
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

#: ★★ 必须强制 UTF-8 输出 —— ★ Windows 下 Python 默认按 **cp936** 写出，
#:   而 hook 的消费方按 **UTF-8** 解码 ⇒ ★ 反馈会**全变乱码**（★ 已实测踩过）。
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:  # noqa: BLE001
        pass

TODO = re.compile(r"^\s*\d+\.\s")
SEC2 = re.compile(r"^##\s*②", re.M)
SEC3 = re.compile(r"^##\s*③", re.M)


def count_todos(text: str) -> int:
    """★ 数 `AUTO_HANDOFF.md` ② 段里的**编号待办**（`1. ` / `2. ` …）。"""
    m2 = SEC2.search(text)
    if not m2:
        return 0
    rest = text[m2.end() :]
    m3 = SEC3.search(rest)
    body = rest[: m3.start()] if m3 else rest
    return sum(1 for line in body.splitlines() if TODO.match(line))


def main() -> int:
    root = Path(
        os.environ.get("CODEBUDDY_PROJECT_DIR") or Path(__file__).resolve().parents[1]
    ).resolve()
    handoff = root / "output" / "AUTO_HANDOFF.md"
    if not handoff.exists():
        print("output/AUTO_HANDOFF.md 不存在 ⇒ 本轮还没写交接单。", file=sys.stderr)
        return 1
    n = count_todos(handoff.read_text(encoding="utf-8", errors="replace"))
    if n == 0:
        return 0  # ★ 达成 ⇒ 该 cmd 通过 ⇒ 门放行
    print("`output/AUTO_HANDOFF.md` ② 段仍有 **%d** 条编号待办。" % n, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
