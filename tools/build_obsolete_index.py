"""★ 建**官方废弃成员索引**：把 `C:\\swapi\\types\\**\\*.md` 里带 `Obsolete` 的都收进来。

★ 为什么要它（★ 这是"批量推进"的第一台机器）：
  bunny 的 30 路对比里，**「用了废弃成员」占 12/60 = 20%**（★ 第二大类），
  ★ 而这一类的**判据是纯机械的**：★ 官方页上有 `Obsolete` 行 + 点名了后继 ⇒ ★ 拿我们的成员名去对即可。
  ★★ 所以**不必一条条读**：★ 先把官方那份名单建成索引，★ 再拿全仓的成员名去比。
★ 产出：`specs/202-user-coverage-gaps/recon/official-obsolete-index.json`
  （★ 每条：接口 · 成员 · 后继（官方点名的那句原文）· 所在文件）
★ 只读官方文档；★ 不动仓内任何文件。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/build_obsolete_index.py
# 定位:   建**官方废弃成员索引**：把 `C:\swapi\types\**\*.md` 里带 `Obsolete` 的都收进
#           来。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
SWAPI = Path(r"C:\swapi\types")
OUT = Path(
    Path(__file__).resolve().parents[1]
    / "specs"
    / "202-user-coverage-gaps"
    / "recon"
    / "official-obsolete-index.json"
)

#: ★ 官方页里"废弃"的写法（★ 逐字见过这几种）
OBS = re.compile(r"Obsolete|已废弃|Superseded by", re.I)
#: ★ 后继的名字（★ 官方那句里通常在 `[[Iface::Member]]` 或反引号里）
SUCC = re.compile(
    r"(?:Superseded by|obsolete[^.]*?use)\s*\[\[([^\]]+)\]\]|`([A-Za-z_][A-Za-z0-9_]*)`"
)


def main() -> int:
    started = time.time()
    rows = []
    pages = 0
    for iface_dir in sorted(p for p in SWAPI.iterdir() if p.is_dir()):
        for page in sorted(iface_dir.glob("*.md")):
            pages += 1
            try:
                txt = page.read_text(encoding="utf-8", errors="replace")
            except Exception:  # noqa: BLE001
                continue
            if not OBS.search(txt):
                continue
            #: ★★★ 2026-10-03（接手轮）**标定后改对**（★ 事实 510：判据先标定再接线）：
            #:   ★ 官方页（例 `C:\swapi\types\IEntity\Select2.md`）的布局逐行是：
            #:     ```
            #:     10 |# IEntity.Select2
            #:     11 |
            #:     12 |Obsolete. Superseded by [[IEntity::Select4]].
            #:     13 |
            #: 14 |**Signature**: `System.bool Select2( System.bool Append, System.int M
            #: ark )`
            #:     16 |## Parameters
            #:     ```
            #:   ⇒ ★★ **废弃那句是"标题之后、第一个 `## ` 之前"的独立一段**。
            #:   ★ 我第一版写成 `txt.split("## ", 1)[-1]`（取第一个 `## ` **之后**）
            #:     ⇒ ★ **正好把它切掉** ⇒ 于是 `obsolete_line` **全空**、后继只找到 1 个、
            #: ★★ 而 `OBS.search(txt)` 又会在正文里别处匹配到 "Obsolete" ⇒ **1718 个假阳
            #: 性**。
            #:   ★ 现按**真实位置**取：★ 在 `# 标题` 与第一个 `## ` 之间找。
            head = txt.split("\n## ", 1)[0]  #: ★ 「标题之后、第一个 `## ` 之前」那一段
            line = ""
            for l in head.splitlines():
                s = l.strip()
                if (
                    s
                    and not s.startswith(
                        (
                            "#",
                            "---",
                            "type:",
                            "member:",
                            "kind:",
                            "assembly:",
                            "namespace:",
                            "category:",
                        )
                    )
                    and OBS.search(s)
                ):
                    line = s
                    break
            if not line:
                continue  #: ★★ 没在那一段里 ⇒ **不算废弃**（★ 不猜）
            #: ★★★ spec 251：**同名链接优先** —— 多链接里「**与被废弃成员同名**」的那个
            #: 才是真后继。
            #: ★ 官方用它表达**接口迁移**（★ 实测：`IModelDoc2::SketchTrim` → `ISketchMa
            #: nager::SketchTrim`
            #: 而旧规则取的是 `ISketchManager::SketchExtend`，语义是「延伸」**不是**「剪
            #: 裁」）。
            #: ★ **先量**（`output/_probe251_rule_impact.py`）：全 **1671** 条里只有 **6
            #: ** 条会变，
            #:     且**恰好**等于 244 登记的 `_KNOWN_WRONG` ⇒ ★ 修法安全。
            #:   ★ 规则来源：244（`specs/244-multi-successor-rule/`）的裁决。
            links = re.findall(r"\[\[([^\]]+)\]\]", line)
            succ = links[0].strip() if links else ""
            for _lk in links:
                if _lk.split("::")[-1].strip() == page.stem:
                    succ = _lk.strip()
                    break
            rows.append(
                {
                    "interface": iface_dir.name,
                    "member": page.stem,
                    "successor": succ,
                    "obsolete_line": line[:220],
                    "page": str(page),
                }
            )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "scanned_pages": pages,
                "obsolete_count": len(rows),
                "entries": rows,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print("★ 扫了官方页 **%d** 篇 ⇒ 带 Obsolete 的成员 **%d** 个" % (pages, len(rows)))
    print(
        "★ 有官方点名后继的：**%d** 个（%.0f%%）"
        % (
            sum(1 for r in rows if r["successor"]),
            100.0 * sum(1 for r in rows if r["successor"]) / max(1, len(rows)),
        )
    )
    print("★ 索引写到:", OUT)
    print()
    print("%-40s %-34s %s" % ("接口.成员", "官方点名的后继", "那句话（截断）"))
    print("-" * 132)
    for r in rows[:14]:
        print(
            "%-40s %-34s %s"
            % (
                ("%s.%s" % (r["interface"], r["member"]))[:39],
                (r["successor"] or "（官方没写）")[:33],
                r["obsolete_line"][:70],
            )
        )
    print("..." if len(rows) > 14 else "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
