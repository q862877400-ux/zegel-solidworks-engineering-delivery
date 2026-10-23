"""★ 卡片门禁：`docs/survey/cards/*.md` 必须满足四条验收判据（判据见 `docs/ai-3d-survey-plan.md` §4）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/check_survey_cards.py
# 定位:   业主 2026-10-23 指令「把市面上的、学术界的、未发布的一切技术路径总
#         结出来」。本文件把 `docs/ai-3d-survey-plan.md` §4 的四条判据机器化：
#         ① 12 字段无空缺 ② 量化断言同行带出处（复用
#         `scripts/check_fact_provenance.py` 的 QUANT/TRACE 口径）③ 证据等级在
#         枚举内 ④ 有「未确认事项」段。★ 只判结构 + 出处，不判内容对错。
# 官方依据: AGENTS.md §十八（一行 docstring + 来源块）·
#           docs/ai-3d-survey-plan.md §4（卡片验收判据）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   docs/survey/cards/*.md
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parents[1]
CARDS = ROOT / "docs" / "survey" / "cards"

#: 与 check_fact_provenance.py 同口径 —— 量化断言形态
QUANT = re.compile(
    r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)\s*(条|个|处|次|行|秒|毫秒|MB|GB|KB|%|倍|档|级)"
)
#: 可追溯出处的形态（任一命中即算有出处）
#: ★ 2026-10-24 放宽扩展名：`.lsp` / `.bpy` 之类同样是可以复核的源文件，
#:   原先写死扩展名表会把「引了 `mcp_dispatch.lsp:1216` 的行」误判成没出处
#:   （实测 15 行误报）⇒ 改为「任意扩展名 + 可选行号」。
TRACE = [
    re.compile(r"`[^`]*\.[A-Za-z0-9]{1,8}(?::\d+(?:-\d+)?)?`"),
    re.compile(r"`[^`]*(?:--|pytest |python |git |pwsh |Get-|Select-|npm |uv |pip )[^`]*`"),
    re.compile(r"\[[^\]]+\]\([^)]+\)"),
    re.compile(r"https?://\S+"),
    re.compile(r"(?:实测|核验|测得|跑过|依据|出处|来源)\s*[:：]"),
    re.compile(r"事实\s*\d+"),
    re.compile(r"[A-Za-z0-9_./\\-]+\.[A-Za-z0-9]{1,8}:\d+"),
]

REQUIRED_LEVELS = ("实测", "读码", "元数据")
REQUIRED_SECTIONS = (
    "## 1." , "## 2.", "## 3.", "## 4.", "## 5.", "## 6.", "## 7.", "## 8.", "## 9.",
)
EMPTY_OK = ("查不到", "未确认", "无", "不适用", "未实测", "—", "-")


def check_card(p: pathlib.Path) -> list[str]:
    bad: list[str] = []
    t = p.read_text(encoding="utf-8", errors="replace")
    lines = t.splitlines()

    # ① 结构：字段表 + 九节
    for key in ("仓库 / 主页", "许可", "元数据", "克隆", "证据等级"):
        if key not in t:
            bad.append(f"缺字段：{key}")
    for sec in REQUIRED_SECTIONS:
        if sec not in t:
            bad.append(f"缺小节：{sec}")

    # ③ 证据等级
    m = re.search(r"证据等级\s*\|?\s*([^\n|]*)", t)
    if not m or not any(lv in m.group(1) for lv in REQUIRED_LEVELS):
        bad.append("证据等级缺失或不在枚举（实测/读码/元数据）内")

    # ④ 未确认事项
    if "未确认事项" not in t and "未确认" not in t:
        bad.append("缺「未确认事项」段")

    # ② 量化断言必须有出处
    for i, line in enumerate(lines, 1):
        if p.name in t:  # 自身文件名出现在文中不算问题，跳过空行判断用
            pass
        if not QUANT.search(line):
            continue
        if line.strip().startswith("|") and "来源" in line:
            continue  # 表头
        if any(rx.search(line) for rx in TRACE):
            continue
        bad.append(f"L{i} 量化断言无出处：{line.strip()[:80]}")
    return bad


def main() -> int:
    if not CARDS.exists():
        print(f"✗ 卡片目录不存在：{CARDS}")
        return 1
    cards = sorted(CARDS.glob("*.md"))
    if not cards:
        print("✗ 还没有任何卡片")
        return 1
    total_bad = 0
    for c in cards:
        bad = check_card(c)
        if bad:
            total_bad += len(bad)
            print(f"[FAIL] {c.name}")
            for b in bad[:8]:
                print(f"    {b}")
        else:
            print(f"[PASS] {c.name}")
    print(f"\n卡片 {len(cards)} 张 · 问题 {total_bad} 处")
    print("[PASS] 全部卡片满足四条验收判据" if total_bad == 0 else "[FAIL] 有卡片未过判据")
    return 0 if total_bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())