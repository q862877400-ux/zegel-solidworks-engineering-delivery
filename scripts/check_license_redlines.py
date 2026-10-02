r"""@brief **A6 许可红线门禁**：代码里声明的来源与许可必须在**白名单**内，且有据可查。

## A6 的原文（`AGENTS.md §一`）
> **A6** 许可无越界：AGPL / GPL / 无许可 / 全版权保留的代码**没被抄进来**；
> Apache-2.0 来源带 **NOTICE** 义务 —— **怎么验**：逐文件对照「许可判定表」

**⚠「逐文件对照」是**人工动作**，本项目此前**没有门禁**在这上面** ——
而它的性质与其它 A 级判据一样：**可以机器判一部分**。

## 本门禁判什么（**可机核的那部分**）
`AGENTS.md §四.3` 的来源标注制要求每个文件带来源块，其中两行与本判据直接相关：
```
# 仓库:   <谁>          ← 来源（可能是第三方，也可能是官方 API / 本项目自身）
# 许可:   <什么许可>     ← 声明
```
**三条判据**：
1. **来源块点名了第三方项目**（出现在一个**显式白名单**里或含 `owner/repo` 形状）
   ⇒ 该文件的 `# 许可:` **必须**出现白名单许可词（`MIT` / `Apache-2.0`）。
2. **任何来源块的 `# 许可:` 都不许把 AGPL / GPL / 无许可 / 全版权保留当作合法来源**
   （铁律 6：那几类**只读思想**，不抄代码）。
3. **一旦有文件声明 `Apache-2.0`** ⇒ `THIRD-PARTY-NOTICES.md` **必须存在**
   （分发时保留 `NOTICE` 是 Apache-2.0 的硬义务）。

## ⚠ 覆盖边界（**如实写明，不冒充全覆盖**）
* 它判的是**声明**是否自洽、是否越界 —— **不判声明本身是否属实**。
  「某个函数到底抄没抄」是**语义**判断，靠人核（本门禁只能保证**没有未声明的越界**）。
* 它**不扫** `docs/`、`references/` 里的散文（那些常有「只读思想」的讨论，属**合法**引用）。
* 许可词表是**显式**的（`ALLOWED` / `FORBIDDEN`），改它要在这里改 —— **不猜**。

# ── 来源 ──
# 仓库:   本项目自身（门禁实现）
# 文件:   scripts/check_license_redlines.py —— 本文件自身
#         tests/test_license_redlines_gate.py（契约测试 + 负例）
# 定位:   把 A6 的「逐文件对照许可判定表」做成**可跑的那一半**；
#         依据是 `AGENTS.md §二 铁律 6` 的许可表与 §四.3 的来源标注制。
# 官方签名依据: 不适用（纯静态：读来源块 + 查文件存在性，**不连 SolidWorks**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: ✅ **允许**作为来源的许可（`AGENTS.md` 铁律 6 的表里「能做什么」非「只读思想」的那两档）
ALLOWED = ("MIT", "Apache-2.0")

#: 🚫 **不许当作代码来源**的许可（只读思想）
FORBIDDEN = ("AGPL", "GPL", "无许可", "全版权保留", "All rights reserved", "专有")

#: 已知的第三方项目名（**显式表**，不靠猜）。新增来源时**在这里登记**。
THIRD_PARTIES = (
    "wzyn20051216", "microsoft/UFO", "UFO",
    "Eduardof0nt", "andrewbartels1", "vespo92", "Slacker-LLC",
    "alisamsam", "codestack", "Millwright", "kilwizac", "chatsw",
    "delancy827", "guoleizhen717", "pengxiaoan",
)

#: ⚠⚠ **已知是 Apache-2.0 的来源** —— 对它们，`# 许可:` **必须**出现 `Apache`
#: （**不能只写「本仓库 MIT」**）。
#:
#: ★ 这条是**实测逼出来的**（2026-10-01 轮 57）：第一版只判「许可里有没有白名单词」，
#:   而「**本仓库 MIT**」这个措辞**本身含 `MIT`** ⇒ 于是
#:   「来源：`Slacker-LLC/solidworks-mcp`（**Apache-2.0**）／ 许可：本仓库 MIT」
#:   这种**会把 Apache 义务漏掉**的组合**被判为通过**。
#:   ⇒ 那是**假阴性**，而且漏的正是**唯一带 NOTICE 硬义务**的那一档。
APACHE_ONLY = ("Slacker-LLC",)

#: 来源块里这两行（`# 仓库:` / `# 许可:`）的形态
REPO_LINE = re.compile(r"^#\s*仓库\s*[:：]\s*(.+?)\s*$", re.M)
LIC_LINE = re.compile(r"^#\s*许可\s*[:：]\s*(.+?)\s*$", re.M)

SCAN_DIRS = ("scripts", "tools", "tests", "mcp-server", "apps")
NOTICES = REPO / "THIRD-PARTY-NOTICES.md"


def source_blocks(path: Path) -> list:
    """⇒ ``[(repo_text, license_text)]`` —— 该文件里每一对来源块（仓库 + 许可）。

    ⚠ 按**顺序配对**（来源块是成组的：一个 `# 仓库:` 后面跟一个 `# 许可:`），
    允许多块（本项目确实有多块文件）。**配不上的不算**（那本身是来源门禁的事，
    不归本门禁管 —— 一个门禁只报它管的那类）。
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    repos = [m.group(1) for m in REPO_LINE.finditer(text)]
    lics = [m.group(1) for m in LIC_LINE.finditer(text)]
    return list(zip(repos, lics))


def scan_file(path: Path) -> list:
    """⇒ ``[(kind, detail)]`` —— 该文件违反 A6 的地方。"""
    out = []
    for repo_text, lic_text in source_blocks(path):
        named = [t for t in THIRD_PARTIES if t in repo_text]
        has_allowed = any(a.lower() in lic_text.lower() for a in ALLOWED)
        has_forbidden = [f for f in FORBIDDEN if f.lower() in lic_text.lower()]
        # ① 点名第三方 ⇒ 必须声明白名单许可
        if named and not has_allowed:
            out.append(("third-party-without-allowed-license",
                        "来源点名 %s，而许可写的是 %r（须含 %s）"
                        % (", ".join(named), lic_text[:70], " / ".join(ALLOWED))))
        # ①b ⚠ **已知 Apache-2.0 的来源** ⇒ 必须**明写** Apache（见 APACHE_ONLY 的注释）
        apache_only = [t for t in named if t in APACHE_ONLY]
        if apache_only and "apache" not in lic_text.lower():
            out.append(("apache-source-without-apache-notice-line",
                        "来源 %s **是 Apache-2.0**，而许可写的是 %r —— "
                        "光写「本仓库 MIT」会**漏掉 Apache 的 NOTICE 义务**"
                        % (", ".join(apache_only), lic_text[:70])))
        # ② 不许把禁类许可当来源
        if has_forbidden:
            out.append(("forbidden-license-claimed",
                        "许可声明含禁类词 %s：%r" % (has_forbidden, lic_text[:70])))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="A6 许可红线门禁（来源声明 vs 白名单）")
    ap.add_argument("--repo", default=str(REPO))
    a = ap.parse_args(argv)
    repo = Path(a.repo)

    files = []
    for d in SCAN_DIRS:
        p = repo / d
        if p.is_dir():
            files.extend(sorted(p.rglob("*.py")))
    files = [f for f in files
             if "__pycache__" not in f.parts and "resources" not in f.parts]

    bad, n_blocks, n_third = [], 0, 0
    apache_seen = []
    for f in files:
        blocks = source_blocks(f)
        n_blocks += len(blocks)
        for rt, lt in blocks:
            if any(t in rt for t in THIRD_PARTIES):
                n_third += 1
                if "Apache" in lt:
                    apache_seen.append(f)
        probs = scan_file(f)
        if probs:
            bad.append((f.relative_to(repo), probs))

    print("A6 许可红线门禁 · 扫 %d 个 .py" % len(files))
    print("  来源块 **%d** 对（其中点名第三方的 **%d** 对）" % (n_blocks, n_third))
    print("  白名单: %s ｜ 禁类: %s" % (" / ".join(ALLOWED), " / ".join(FORBIDDEN)))
    print()

    if bad:
        print("  [FAIL] %d 个文件有 A6 问题：" % len(bad))
        for f, probs in bad:
            print("    %s" % f)
            for kind, detail in probs:
                print("      · [%s] %s" % (kind, detail))
        return 1

    # ③ Apache-2.0 ⇒ NOTICES 必须在
    if apache_seen and not NOTICES.is_file():
        print("  [FAIL] 有 %d 个文件声明 Apache-2.0，而 `THIRD-PARTY-NOTICES.md` **不存在**"
              % len(set(apache_seen)))
        print("    Apache-2.0 的 `NOTICE` 义务紧跟**分发** ⇒ 该文件是硬要求（铁律 6）")
        return 1

    print("  [PASS] 0 个文件越界")
    if apache_seen:
        print("    ✓ 有 %d 个文件声明 Apache-2.0，且 `THIRD-PARTY-NOTICES.md` 在"
              % len(set(apache_seen)))
    print()
    print("  ⚠ 覆盖边界：本门禁判**声明是否自洽/越界**，**不判声明是否属实**")
    print("    （「某函数到底抄没抄」是语义判断，靠人核）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
