"""量清楚一件事：**官方 15,466 个成员里，我们真机试过多少个？**

方法（2026-10-01 轮 214）：
  ① 官方成员名清单 = `C:\\swapi\\types\\<接口>\\*.md` 的**文件名**（一个成员一个文件）
     ⇒ 这是**权威**的名字集合，不用猜名字形态（上一版按"首字母大写"猜，把 AGENTS/AISI 也抓进来了）。
  ② 真机脚本 = `D:\\AI\\SW\\probe*.py`（探针）+ 代码仓库 `tools/capture_*.py`（证据）
  ③ 逐个脚本，看它的文本里出现了哪些**官方成员名** ⇒ 那些就是它可能调过的成员。★ 这是**上界**
     （提到名字 ≠ 一定调过），所以再给一个 **下界**：只在"带调用的行"里出现的。

⚠ 本脚本只读；产物落 `D:\\AI\\SW\\output\\`。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（分析工具，工作区仓库）
# 文件:   D:\\AI\\SW\\tools\\measure_realmachine_members.py
# 定位:   回答「15,466 个成员里真机试过多少」——把"静态出现过"与"真机跑过"分开量。
# 官方依据: `C:\\swapi\\types\\` 的成员文件（权威名字集合）
# 许可:   本仓库 MIT。
# ⚠ 只做静态文本比对，不连 SolidWorks。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SWAPI = Path(r"C:\swapi\types")
PROBES = Path(r"D:\AI\SW")
CAPTURES = Path(r"C:\swprojects\sw-skill-fork\tools")
OUT = Path(r"D:\AI\SW\output\realmachine-members.json")


def official_members() -> dict:
    """⇒ {成员名: 所属接口}。一个成员一个 md 文件，文件名就是成员名。"""
    out = {}
    for d in SWAPI.iterdir():
        if not d.is_dir():
            continue
        for p in d.glob("*.md"):
            if p.name == "_overview.md":
                continue
            out.setdefault(p.stem, d.name)
    return out


def main() -> int:
    mem = official_members()
    print("  官方成员名（去重后）: **%d**" % len(mem))

    scripts = sorted(PROBES.glob("probe*.py")) + sorted(CAPTURES.glob("capture_*.py"))
    print("  真机脚本: %d 个（工作区 probe*.py + 仓库 capture_*.py）" % len(scripts))

    #: 只有"带调用/带引号"的行才算（下界）；整个文件算（上界）
    lo, hi = set(), set()
    per_file = []
    CALLISH = re.compile(r"[\"']([A-Za-z_]\w*)[\"']|\.([A-Z]\w+)\s*\(|([A-Z]\w+)\s*\(")
    for p in scripts:
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        hi |= {m for m in mem if m in t}
        found_lo = set()
        for line in t.splitlines():
            for g in CALLISH.findall(line):
                for name in g:
                    if name in mem:
                        found_lo.add(name)
        lo |= found_lo
        per_file.append((p.name, len(found_lo)))

    print("")
    print("  ★ 官方 %d 个成员里：" % len(mem))
    print("     **下界（出现在带调用的行里）: %d 个（%.2f%%）**" % (len(lo), 100.0 * len(lo) / len(mem)))
    print("     上界（名字在任何真机脚本里出现过）: %d 个（%.2f%%）" % (len(hi), 100.0 * len(hi) / len(mem)))
    print("")
    print("  贡献最大的脚本（下界口径）：")
    for n, c in sorted(per_file, key=lambda x: -x[1])[:10]:
        if c:
            print("    %-46s %4d" % (n, c))
    OUT.write_text(json.dumps(
        {"official_members": len(mem), "low": sorted(lo), "high": sorted(hi)}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print("")
    print("  产物:", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
