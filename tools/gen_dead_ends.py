"""★ 从 `capabilities.yaml` 生成 **`docs/dead-ends.md`** —— 「这条路已经走死」的清单。

★ 为什么要有它（2026-10-02 轮 363）：轮 359–362 我在 `revolve_boss` 的轴上**重走了一遍**
  前人早已走死的路 —— 而结论**就在 `capabilities.yaml` 的 `limitations` 里**（轮 153/155 记的
  「6 种选法全部失败」）。★ 我当时只查了 `known-facts.md` 与 `git log`，**没读那条能力的 limitations**。
⇒ ★★ **本脚本把"该先读的东西"从 23 个能力里抽出来、按"死路"排序** ⇒ 生成一份**开工前该扫一遍**的表。

# ## ★ 判据（★ 什么样的措辞算"死路"）
#```
★ 只挑**表示"试完了 / 走不通 / 有硬限制"**的措辞（见 `DEAD` 正则）——
   ★ 而不是所有 limitations（★ 那有几百条，★ 读不完）。
★ 输出按能力分组，★ 每条带**等级**（`verified`/`stitched`/…）与**原文**（★ 不摘要 —— 摘要会丢掉关键条件）。
#```

# ## 用法
#```
python tools/gen_dead_ends.py            # 写 docs/dead-ends.md 并打印统计
python tools/gen_dead_ends.py --check    # 只比对（★ 供门禁用）：文件过期则 exit 1
#```

"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（生成器）
# 文件:   tools/gen_dead_ends.py
# 定位:   把"已走死的路"从 capabilities.yaml 抽成一张开工前该扫的表（防止重走）。
# 官方依据: 不适用（★ 读的是本项目自己的能力清单）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CAPS = REPO_ROOT / "capabilities.yaml"
OUT = REPO_ROOT / "docs" / "dead-ends.md"

#: ★ "走死了 / 有硬限制"的措辞（★ 只挑这些，不把全部 limitations 抄进来）
#: ─────────────────────────────────────────────────────────────────────
#: ★★★★ 2026-10-04（接手轮）**补 7 条漏抓的措辞** —— 处置 `JUDGE-F_G_H_I_J.md` 的
#: 🔴 **#2**（★ 裁判逐字：「★ `tools/gen_dead_ends.py` 的 `DEAD` 正则是**中文措辞白名单*
#: *
#:   ⇒ ★ I 组 11 条里至少 **7 条自动消解**」· ★ 并实测列出漏抓的措辞：
#:   `静默不成` · `全败` · `不抛但特征树不变` · `没建成` · `不可达` · `取不到`；
#:   ★★ 裁判判定：「★ **本组投入产出比最高的一条**」）✓
#:   ★★★ **为什么值得做**：★ 这个正则是 `docs/dead-ends.md` 的**唯一判据**，
#:     而 `AGENTS.md` 把该文件列为「**动手前先扫已走死的路**」的第 ① 步 ⇒
#:     ★★ **白名单漏一个措辞，就等于那条死路对后人不显示** ✓
#:   ★★ **改前的基线（★ 可复核）**：★ **46 条 / 29 个能力** ✓
#: ★★★ 加词的原则（★ 不许放宽成"什么都抓"）：★ **新词必须本身就表示"试完了 / 走不通"** —
#: —
#:     ★ 所以只加**结论性**的词（★ 不加"试了"这种中性词）✓
DEAD = re.compile(
    r"(强停止|全部失败|都失败|不可调用|穷尽|已穷尽|到不了|走不通|停手|停止试|"
    r"次全部|无法|不可行|此路不通|验不过|框架性|架构性|后端限制|"
    r"降为 stitched|需要用户提供|本机没有|失败点.*漂移|未被?穷尽验证|"
    #: ★★★ 2026-10-04 补的 7 条（★ 每条都出自裁判的实测漏抓清单）——
    r"静默不成|全败|不抛但特征树不变|没建成|不可达|取不到|"
    #: ★★ 顺带补的同族"结论性"措辞（★ 都是"试完了没成"的意思，★ 不是中性词）
    r"不注册|保持不注册|验不了|没法验|不适用|不存在这个成员)")


def collect() -> list[tuple[str, str, str]]:
    """⇒ `[(能力 id, 等级, 该条 limitation 原文)]`（★ 只含"死路"措辞那些）。"""
    data = json.loads(CAPS.read_text(encoding="utf-8"))
    out = []
    for cap in data.get("capabilities") or []:
        for lim in cap.get("limitations") or []:
            if DEAD.search(lim):
                out.append((cap["id"], cap.get("level", "?"), " ".join(lim.split())))
    return out


def render(rows: list[tuple[str, str, str]]) -> str:
    by_cap: dict[str, list[tuple[str, str]]] = {}
    for cid, lvl, txt in rows:
        by_cap.setdefault(cid, []).append((lvl, txt))
    body = [
        "# 已走死的路（★ 开工前该扫一遍）",
        "",
        "> ⚑ **本文件由 `tools/gen_dead_ends.py` 从 `capabilities.yaml` 生成** —— 不要手改。",
        "> ★ 它只挑**表示「试完了 / 走不通 / 有硬限制」**的 `limitations`，按能力分组。",
        "> ★★ **为什么有它**：2026-10-02 轮 359–362 我在 `revolve_boss` 的轴上**重走了一遍**",
        "> 前人早已走死的路（轮 153/155 记的「6 种选法全部失败」）—— 而结论**就在那份清单里**。",
        "> 轮 35 的定则：**动手核一条路之前，先读该能力的 `limitations`**。",
        "",
        "## 统计",
        "",
        "| 口径 | 数 |",
        "|---|---|",
        "| 「死路」条目 | **%d** |" % len(rows),
        "| 涉及能力 | **%d** |" % len(by_cap),
        "",
        "## 逐条（★ 按能力分组；等级 = 该能力当前等级）",
        "",
    ]
    for cid in sorted(by_cap):
        lvls = {lvl for lvl, _ in by_cap[cid]}
        body.append("### `%s`（%s）" % (cid, " / ".join(sorted(lvls))))
        body.append("")
        for _lvl, txt in by_cap[cid]:
            body.append("- %s" % txt)
        body.append("")
    return "\n".join(body) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只比对，不写（过期则 exit 1）")
    args = ap.parse_args()

    rows = collect()
    text = render(rows)
    caps = len({r[0] for r in rows})
    if args.check:
        old = OUT.read_text(encoding="utf-8") if OUT.is_file() else ""
        if old != text:
            print("  ✗ `docs/dead-ends.md` 与 `capabilities.yaml` 不一致 ⇒ 跑 tools/gen_dead_ends.py")
            return 1
        print("  ✓ `docs/dead-ends.md` 是最新的（%d 条 / %d 能力）" % (len(rows), caps))
        return 0
    OUT.write_text(text, encoding="utf-8")
    print("  「死路」条目 **%d** · 涉及能力 **%d**" % (len(rows), caps))
    print("  产物: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
