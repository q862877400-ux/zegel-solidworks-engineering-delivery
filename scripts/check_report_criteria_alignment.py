r"""@brief 门禁：**所有**逐条自评表的 A 编号必须与 `AGENTS.md §一` 的 A1–A10 一致。

## 为什么（2026-10-01 轮 82 起 · 轮 100 推广）
`AGENTS.md §一` 定义 **A1–A10 十条交付判据**；仓库里有**若干份逐条自评**。
⚠ 轮 82 实测 `harvest-report.md §四` 用的是**另一套编号**（**同名不同事**）：
```
报告「A3」= COM 签名对齐      |  AGENTS.md 的 A3 = 五统一门禁
报告「A5」= 许可无越界        |  AGENTS.md 的 A5 = **COM 签名对齐**
```
⇒ 当时写了门禁，但**只扫 `harvest-report.md`**。

⚠⚠ **轮 100 发现第二份**：`docs/final-audit.md` 的 `## 逐条判定` 表**也**是另一套编号
（它的 `A3`=签名、`A5`=许可、`A6`=禁词、`A8`=fork），**而门禁扫不到它**。
★ **这正是已知事实 62 的又一例**：「一个门禁**写了**不等于它**有效**」——
判据对了，**作用范围**没跟上。

## 判据
1. 从 `AGENTS.md §一` 抽权威 `A\d+` 集合；
2. 扫 `docs/**.md` 与仓库根 `*.md`，找出所有**逐条自评表**
   （定义为：连续表格块里**出现 ≥3 个** `A\d+` 行 —— 这个阈值把"顺带提到 A5"排除掉）；
3. **每一张**表的编号集合都必须与权威集合**相同**（多、少、都算不一致）；
4. 表里**不许**出现非 `A\d+` 的编号行（「官方 API 覆盖」「目录结构」那类属于别的节）。

⚠ **便携性**：`AGENTS.md` 在**工作区**（不在本仓库）⇒ 拿不到就 **SKIP 并 exit 0**。

# ── 来源 ──
# 仓库:   本项目自身（元门禁）
# 文件:   scripts/check_report_criteria_alignment.py
# 定位:   守 `AGENTS.md §一`（判据定义）与仓库里**每一份**逐条自评之间的**编号一致性**。
# 官方依据: 不适用（本项目内部工具，不调 SolidWorks API）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
#: `AGENTS.md` 在**工作区**（不在本仓库）⇒ 可用环境变量覆盖；拿不到就 SKIP。
AGENTS = Path(os.environ.get("DSH_AGENTS_MD", Path(__file__).resolve().parents[1] / "AGENTS.md"))

CRIT_ROW = re.compile(r"^\|\s*\*{0,2}(A\d+)\*{0,2}\s*\|")
#: 一张表至少要有这么多 `A\d+` 行，才算「逐条自评表」（排除"顺带提到 A5"）
MIN_ROWS = 3


def _criteria_ids(text: str) -> set:
    """从 `AGENTS.md §一` 抽 A 编号（只在 §一 那节里找）。"""
    ids = set()
    inside = False
    for line in text.splitlines():
        if re.match(r"^##\s*一[、.]", line):
            inside = True
            continue
        if inside and re.match(r"^##\s*二[、.]", line):
            break
        if inside:
            m = CRIT_ROW.match(line)
            if m:
                ids.add(m.group(1))
    return ids


def _tables(text: str) -> list:
    """⇒ `[(块内 A 编号集合, 块内非 A 的首列文本列表, 起始行号)]`，只回 ≥MIN_ROWS 的块。

    ⚠ **表头行不算「混入」**：`| # | 判据 | …` 的首列是 `#`（或空），
      第一版漏了这个排除 ⇒ 把表头报成了"非 A 编号的行"（**假阳性**，轮 100 当场抓到）。
    """
    out: list = []
    ids: set = set()
    odd: list = []
    start = 0
    in_block = False

    def flush():
        if len(ids) >= MIN_ROWS:
            out.append((set(ids), list(odd), start))

    for i, line in enumerate(text.splitlines(), 1):
        if line.startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not cells or set(cells[0]) <= set("-: "):
                continue                      # 分隔行
            if not in_block:
                in_block, ids, odd, start = True, set(), [], i
            m = CRIT_ROW.match(line)
            if m:
                ids.add(m.group(1))
            elif cells[0] and cells[0] not in ("#", ""):
                odd.append(cells[0])
        else:
            if in_block:
                flush()
            in_block, ids, odd = False, set(), []
    if in_block:
        flush()
    return out


def _targets() -> list:
    """要扫的文件：`docs/**.md` + 仓库根 `*.md`。"""
    files = sorted((ROOT / "docs").rglob("*.md"))
    files += sorted(ROOT.glob("*.md"))
    return [f for f in files if f.is_file()]


def main() -> int:
    if not AGENTS.is_file():
        print("报告判据编号门禁 · **SKIP** —— 拿不到 `AGENTS.md`（%s）" % AGENTS)
        print("  （**便携性守卫**：判据定义在工作区，别的机器上不应无条件红）")
        return 0

    auth = _criteria_ids(AGENTS.read_text(encoding="utf-8"))
    if not auth:
        print("[FAIL] 从 `AGENTS.md §一` 抽不到任何 `A\\d+` 判据 —— 判据被改了？")
        return 1

    #: ⚑ **首行自带分母**（轮 192）：分母本来在下一行，而**只看首行的人会以为没有**
    #:   （本项目实测过一次这样的误判）。
    print("报告判据编号门禁 · 权威来自 `AGENTS.md §一`（权威判据 **%d** 条）" % len(auth))
    print("  权威判据 **%d** 条：%s" % (len(auth), sorted(auth, key=lambda s: int(s[1:]))))
    print()

    scanned = bad = 0
    for f in _targets():
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        rel = f.relative_to(ROOT)
        for ids, odd, start in _tables(text):
            scanned += 1
            missing = sorted(auth - ids, key=lambda s: int(s[1:]))
            extra = sorted(ids - auth, key=lambda s: int(s[1:]))
            if missing or extra or odd:
                bad += 1
                print("[FAIL] %s（表起始第 %d 行）" % (rel, start))
                if missing:
                    print("         **缺**判据：%s" % missing)
                if extra:
                    print("         有**定义里没有**的编号：%s" % extra)
                if odd:
                    print("         混入**非 `A\\d+`** 的行（属于别的节）：%s" % odd[:6])
            else:
                print("[PASS] %s（表起始第 %d 行）· %d 条逐条一致" % (rel, start, len(ids)))

    print()
    if scanned == 0:
        print("[FAIL] **一张逐条自评表都没扫到** —— 判据没作用到任何地方")
        print("  修法：自评表要有 `| **A1** | …` 这样以 `A\\d+` 开头的行，且**至少 %d 行**。" % MIN_ROWS)
        return 1
    if bad:
        print("  修法：让**每一张**自评表都**逐条对应 `AGENTS.md §一` 的 A1–A10** ——")
        print("        **编号、条数、含义三样都对齐**（同名不同事是这一类问题的根因）。")
        return 1
    print("[PASS] 扫了 **%d** 张自评表，**每一张**的编号都与 `AGENTS.md §一` 逐条一致" % scanned)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
