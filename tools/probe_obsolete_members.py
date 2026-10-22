r"""@brief 探针：我们**调用**的 COM 成员里，有几个官方已标 **Obsolete**。

## 为什么（2026-10-01 轮 110，Spec Kit `029`）
连着两轮撞上同一类坑（`024` 的 `SketchChamfer` · `028` 的 `Add`）：
```
官方把旧入口标 Obsolete、并给了后继，而我们照抄了旧的那个
```
★ 而 `025` 那道门禁只管**值**，**管不了「你用的是不是废弃入口」**。

## 做法
1. 从代码里抽 `get_com_member(..., "<成员>", ...)` 的**成员名字符串**（这是我们真正调的东西）；
2. 去 `C:\swapi\types\<接口>\<成员>.md` 找同名文档；
3. 文档正文里带 **`Obsolete`** 的 ⇒ 列出来（并把它 `Superseded by` 指向谁一起打出来）。

⚠ **只读探针**，不改任何东西。⚠ 先量，再决定要不要做成门禁。

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_obsolete_members.py
# 定位:   给 Spec Kit `029` 取证：我们调用的成员里有多少已被官方废弃。
# 官方依据: `C:\swapi\types\**\*.md`（官方结构化文档，**带 Obsolete 标记**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

TYPES = Path(r"C:\swapi\types")
#: `get_com_member(<目标>, "<成员>"…)` —— 我们真正调用的成员名
CALL = re.compile(r'get_com_member\(\s*[^,]+,\s*"([A-Za-z_]\w*)"')


def called_members() -> dict:
    """⇒ `{成员名: [出现的文件]}`。"""
    got: dict = defaultdict(list)
    for p in sorted((ROOT / "scripts").glob("sw_*.py")):
        for m in CALL.finditer(p.read_text(encoding="utf-8", errors="replace")):
            got[m.group(1)].append(p.name)
    return got


def doc_index() -> dict:
    """⇒ `{成员名: [文档路径]}`。"""
    idx: dict = defaultdict(list)
    if not TYPES.is_dir():
        return idx
    for p in TYPES.rglob("*.md"):
        idx[p.stem].append(p)
    return idx


def main() -> int:
    if not TYPES.is_dir():
        print("探针 · **SKIP** —— 拿不到官方结构化文档目录（%s）" % TYPES)
        return 0

    called = called_members()
    idx = doc_index()
    print('代码里 `get_com_member(..., "成员")` 调到的成员：**%d** 个' % len(called))
    print("官方文档索引里的成员名：**%d** 个" % len(idx))
    print()

    obsolete, no_doc, ok = [], [], 0
    for name in sorted(called):
        docs = idx.get(name)
        if not docs:
            no_doc.append(name)
            continue
        hit = None
        for d in docs:
            head = d.read_text(encoding="utf-8", errors="replace")[:1200]
            if "Obsolete" in head:
                m = re.search(r"Obsolete\.\s*(?:Superseded by\s*(.+?)\.)?", head)
                hit = (d, (m.group(1) if m and m.group(1) else "（未写后继）"))
                break
        if hit:
            obsolete.append((name, hit[0], hit[1], called[name]))
        else:
            ok += 1

    print("=== ★ 官方已标 **Obsolete** 的成员 ===")
    if not obsolete:
        print("  （无）")
    for name, d, sup, files in obsolete:
        print("  **%s**" % name)
        print("      文档: %s" % d.relative_to(TYPES))
        print("      后继: %s" % sup)
        print("      用在哪: %s" % ", ".join(sorted(set(files))[:4]))
    print()
    print("  有文档且**未**标废弃：**%d** 个" % ok)
    print("  文档里**查不到**同名成员：**%d** 个" % len(no_doc))
    if no_doc:
        print("      例：%s" % ", ".join(sorted(no_doc)[:10]))
    print()
    print("⚠ 口径提醒：同名成员可能分属**多个接口**，其中**一个**标了废弃 ——")
    print("   本探针'有一个标废弃就算废弃'，**偏保守**（可能误报）。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
