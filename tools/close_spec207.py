"""★ 规格 207 的收尾链（一条命令）：重跑聚合件 → SC 复检 → 采纳清单 → 打印裁决输入。"""

# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/close_spec207.py
# 定位:   ★ **为什么把它做成一条命令**：收尾要按顺序跑三件（聚合件 → SC → 采纳清单），
#           而 deep 档是**外部节奏**（bunny 交货）⇒ ★ 若收尾时上下文/回合被打断，下一次
#           只需跑这一条，不必重新回忆顺序与参数 ✓
#         ★ 它**不改任何东西**（除了重跑聚合件那个生成器，那是它的产物），
#           且**不代替判据** —— 每步都把判据原样打出来 ✓
#         ★★ **不替我叫好**：它**只报事实**；"能不能收尾"的判据是 SC 检查器的退出码
#            （★ 只有全绿才 0）✓
# 官方依据: 不适用（本仓工序）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(__file__).resolve().parents[1]


def run(title: str, *cmd: str, tail: int = 14) -> int:
    print("=" * 72)
    print("★ %s" % title)
    print("   $ %s" % " ".join(cmd))
    print("-" * 72)
    p = subprocess.run(
        [sys.executable, *cmd],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=900,
    )
    lines = (p.stdout or "").strip().splitlines()
    for ln in lines[-tail:]:
        print("   " + ln)
    print("   ⇒ exit %d" % p.returncode)
    return p.returncode


def main() -> int:
    #: ① 重跑聚合件（★ 必须**先**跑：它是 SC-1/SC-5 的判据输入）
    run(
        "① 重跑聚合件（SC-1 / SC-5 的判据输入）",
        "tools/build_union_verify_349.py",
        tail=6,
    )
    #: ② SC 复检（★ 判据在这里：只有全绿才 exit 0）
    sc = run(
        "② SC-1..SC-8 复检（★ 只有全绿才 exit 0）", "tools/check_spec207_sc.py", tail=18
    )
    #: ③ 采纳清单（V8 的输入）
    run("③ 采纳清单（V8 裁决的输入）", "tools/list_adoptable.py", tail=8)
    #: ④ 两档记录数（供人一眼看覆盖）
    vf = len(list((ROOT / "output" / "bunny-records-verify").glob("*.json")))
    dp = len(list((ROOT / "output" / "bunny-records-deep").glob("*.json")))
    print("=" * 72)
    print(
        "★ 逐条记录实况：verify %d/273 · deep %d/76 ⇒ 合计 %d/349" % (vf, dp, vf + dp)
    )
    #: ★★ 结论行照 SC 检查器的口径说，不另立一套（免得两处判据打架）✓
    if sc == 0:
        print("★ 结论：**SC 全绿** ⇒ 可以收尾（补汇总定案值 + 勾掉 tasks.md 最后一项）")
    else:
        print("★ 结论：**未全绿** ⇒ ★ 别收尾；先把 SC 检查器列出的缺项补掉")
    return sc


if __name__ == "__main__":
    raise SystemExit(main())
