"""★ 三源检索入口：官方 CHM 正文树（.html + .htm）+ 我们解出来的 `_raw` 文本。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/swdoc_search.py
# 定位:   ★ 2026-10-03（轮 440）承**事实 355** —— ★ 那轮查明「查不到」有两个**检索陷阱
#           **。
#   ★★★ **背景（★ 那是一条会让一批结论过期的发现）**：
#     ```
#     ★ CHM 正文树：★ `.html` **25,738** + `.htm` **2,915**（★ 其中 **2,745** 个是**示例页**）
#     ★ `_raw`（我们解出来的）：★ 只有 **143** 个 txt ⇒ ★ **覆盖约 0.36%** ⚠⚠
#     ```
#   ★★ **两个陷阱**：
#     ① ★ **扩展名**：★ 官方**示例**在 **`.htm`**（★ 而我只搜过 `.html`）⇒
#        ★ 于是得出过**假的**"CHM 里查不到示例"（★ 而树里有 **2,745** 个）⚠
#     ② ★ **覆盖率**：★ `_raw` 只解出 143 个 ⇒ ★★ **"`_raw` 里没有" ≠ "官方文档里没有"**
#   ★★★ **故本工具的判据是**：**同时查三处**（CHM `.html` · CHM `.htm` · `_raw` 文本），
#     并**如实报"命中在哪一处"** ⇒ ★ 修法照**铁律 5**：★ **"查不到"要写清查的是哪一层** ✓
# ★ 用法：
#     python tools/swdoc_search.py AddPinConnector          # 到处找这个名字
#     python tools/swdoc_search.py --grep "DispArrayComp"   # 找**内容**（★ 在正文里搜）
# 官方依据: 不适用（本仓自有的检索工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 三处**都报**（★ 含"0 命中"的那几处 —— ★ 因为"哪一处没有"本身是信息）。
# ⚠ 便携性：★ CHM 树不在 ⇒ 那一处报 `[SKIP]`，★ 其余照查。

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
#: ★ CHM 正文树（★ 官方原文，★ 全的）—— ★ 可用 `DSL_SWHELP` 覆盖
SWHELP = Path(os.environ.get("DSL_SWHELP", Path(__file__).resolve().parents[1] / "AI Solidworks" / "官方文档" / "SWhelp"))
#: ★ 我们解出来的文本（★ 不全 —— ★ 见事实 355）
RAW = Path(os.environ.get(
    "DSL_RAW", str(Path(os.environ.get("DSL_WORKSPACE", Path(__file__).resolve().parents[1])) / "_raw")))

#: ★ 只收这几类后缀 —— ★★ **`.htm` 必须在列**（★ 官方示例就在它里面）
PAGE_SUFFIXES = (".html", ".htm")


def search_names(needle: str, limit: int = 25) -> int:
    """★ 按**文件名**搜（★ 三处都搜）。"""
    low = needle.lower()
    print("  ① 按文件名搜 %r" % needle)
    found = 0
    if SWHELP.is_dir():
        hits = [p for p in SWHELP.rglob("*") if p.is_file()
                and low in p.name.lower() and p.suffix.lower() in PAGE_SUFFIXES]
        ex = [p for p in hits if "_Example" in p.name]
        print("     CHM 正文树：命中 **%d** 个页（★ 其中**示例页 %d** 个）" % (len(hits), len(ex)))
        for p in hits[:limit]:
            print("       %-58s %d" % (p.name, p.stat().st_size))
        found += len(hits)
    else:
        print("     CHM 正文树：[SKIP] 不在 %s" % SWHELP)
    if RAW.is_dir():
        hits2 = [p for p in RAW.rglob("*") if p.is_file() and low in p.name.lower()]
        print("     `_raw`（★ 只覆盖约 0.36%%）：命中 **%d** 个" % len(hits2))
        for p in hits2[:limit]:
            print("       %s" % p.relative_to(RAW))
        found += len(hits2)
    else:
        print("     `_raw`：[SKIP] 不在 %s" % RAW)
    return found


def search_content(needle: str, limit: int = 12) -> int:
    """★ 按**内容**搜（★ 在三处的正文里搜）。"""
    print("  ② 按内容搜 %r" % needle)
    rx = re.compile(re.escape(needle), re.I)
    total = 0
    for label, root in (("CHM 正文树", SWHELP), ("`_raw`", RAW)):
        if not root.is_dir():
            print("     %-14s [SKIP]" % label)
            continue
        n = 0
        shown = 0
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in (*PAGE_SUFFIXES, ".txt"):
                continue
            try:
                t = p.read_text(encoding="utf-8", errors="replace")
            except Exception:                                  # noqa: BLE001
                continue
            if rx.search(t):
                n += 1
                if shown < limit:
                    print("       %s" % p.name)
                    shown += 1
        print("     %-14s 命中 **%d** 个文件" % (label, n))
        total += n
    return total


def main(argv: list) -> int:
    args = [a for a in argv if not a.startswith("--")]
    mode_grep = "--grep" in argv
    if not args:
        print("  用法：python tools/swdoc_search.py <名字>      # 按文件名找")
        print("        python tools/swdoc_search.py --grep <串>  # 按内容找")
        return 2
    needle = args[0]
    print("  ★ 三源检索 —— ★ 判据：**三处都报**（★ 因为「哪一处没有」本身是信息）")
    print("  ★★ 事实 355 的两个陷阱：① 示例在 `.htm`（★ 不在 `.html`）· ② `_raw` 只覆盖约 0.36%")
    print()
    found = search_content(needle) if mode_grep else search_names(needle)
    print()
    if found == 0:
        print("  ⚠★ **三处都没有** —— ★ 而按铁律 5，★ 现在可以说的是：")
        print("       「**这两套源里查不到**」—— ★★ 而**不是**「官方 API 里没有」")
        print("       （★ 因为 `_raw` 只覆盖约 0.36%；★ 而 CHM 树也**未必全** —— ★ 见事实 355）")
    else:
        print("  ✓ 命中 %d 处 —— ★ 而**报的时候要写清是哪一处**（★ 三处的可信度不同）" % found)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
