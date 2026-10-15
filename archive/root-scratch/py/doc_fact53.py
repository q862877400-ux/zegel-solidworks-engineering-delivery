"""把已知事实 53 追加进 AGENTS.md（**短的单行字符串** —— 事实 48 定则①）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（纪律记录）
# 文件:   D:\\AI\\SW\\docs\\T-040-unmapped-constants-evidence.md（证据，**独立文件**）
#         scripts/check_interface_member_ownership.py（**已回退到 e4794cc**）
# 定位:   轮 40 在「11 条未映射常量」上**连续改了 6 版启发式**，每版都在同一处打补丁
#         ⇒ **回退** + 把证据留在文档里。本补丁只记这条纪律。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 事实 48 定则：跑完**核对落盘**。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
AGENTS = Path(r"D:\AI\SW\AGENTS.md")

A = "| 53 | **「调到看起来对」的识别信号：同一个启发式**连续修补 ≥3 次**还没稳定，就该停下回退**"
B = " —— 2026-10-01 实例：为攻掉 `CONST → 接口` 映射表的 11 条未映射，我给检查器加「名字回退」，"
C = "**连续改了 6 版**（30/4/1 ⇒ 词重叠过滤无效 ⇒ 末词过滤仍错 ⇒ 去首词变体跌到 29/0/**6** ⇒ "
D = "改词级匹配回到 24/0/11 ⇒ 改名字子串又错成 29/6/0），**每版都在同一处打补丁**，最后**回退**到 `e4794cc` 的 **24/0/11**。"
E = "**⇒ 根因不是「还没调对」**：① `swFmSweepThread` 那类（\"sweep thread\" 是**螺纹**）**需要领域知识**，"
F = "文本匹配永远得不到；② 名字匹配的**假阳性**（`swFmSolidToSheetMetal` ⇒ `ISheetMetalFeatureData`、"
G = "`swFmMirrorComponent` ⇒ `IComponent2`）**压不住**。**⇒ 正解：把证据留在**文档**里"
H = "（`docs/T-040-unmapped-constants-evidence.md`，11 条逐条带官方依据），**不接进工具**。**"
I = "⇒ 定则：启发式需要连续 ≥3 次修补才「看起来对」时，回退 + 记证据，不要继续调。** | "
J = "`docs/T-040-unmapped-constants-evidence.md`；`git log --oneline scripts/check_interface_member_ownership.py`（含回退）；"
K = "已知事实 52（名字是弱信号）与 51（分析范围要贴合组织单元）|"

FACT53 = A + B + C + D + E + F + G + H + I + J + K


def main() -> int:
    src = AGENTS.read_text(encoding="utf-8").splitlines(keepends=True)
    if any(l.lstrip().startswith("| 53 |") for l in src):
        print("  ⚠ 事实 53 已存在")
    else:
        i = next((k for k, l in enumerate(src) if l.lstrip().startswith("| 52 |")), None)
        if i is None:
            print("  ✗ 找不到 | 52 | 行")
            return 1
        src = src[:i + 1] + [FACT53 + "\n"] + src[i + 1:]
        AGENTS.write_text("".join(src), encoding="utf-8")
        print("  ✓ 已加已知事实 53")

    # 落盘核对（事实 48 定则②）
    t = AGENTS.read_text(encoding="utf-8")
    print()
    print("  ── 落盘核对 ──")
    print("    AGENTS.md | 53 |: %d 行" % t.count("\n| 53 |"))
    print("    含「回到回退」相关字样: %s" % ("是 ✓" if "e4794cc" in t else "**否**"))
    ks = [k for k, l in enumerate(t.splitlines()) if l.lstrip().startswith("| 41 |")]
    if ks:
        bad = [l[:36] for l in t.splitlines()[ks[0]:ks[0] + 15]
               if l.strip() and not l.lstrip().startswith("|")]
        print("    事实 41 起 15 行的非表格行: %s" % ("无 ✓" if not bad else "**有 %r**" % bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
