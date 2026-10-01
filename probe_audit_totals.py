r"""@brief 验算 `docs/signature-audit.md` 里所有「合计」行是否等于上方表体各行的列和。

## 为什么（A5 的可跑那一半，2026-10-01 轮 69）
`AGENTS.md §一 A5` 要「每个新增文件里每个 COM 调用的参数顺序与类型与官方签名对齐」，
判据是 `docs/signature-audit.md`。⚠ 而那份表里的**汇总数字是手工数出来的**：
```
**小计：7 不通过 · 9 通过**（批次 1）
| **合计** | **711** | **696** | **2** | **0** |
**累计查出并修复的签名缺陷：7 处**
```
⇒ **手工数字没有门禁** ⇒ 改一行表体，合计不会自己跟着变（**与 A8 的 harvest-report 同型缺口**）。

本探针只做**纯机器判**的那一件：**带「合计」/「小计」的行，必须是它上方表体的列和**。
⚠ 它**不判**「表体内容对不对」（那要人核），**只判「算术自洽」** —— 但算术自洽是**必要**条件，
且**它能抓到最常见的腐坏方式**（改了行数忘改合计）。

# ── 来源 ──
# 仓库:   本项目自身（只读验算，非第三方移植）
# 文件:   D:\AI\SW\probe_audit_totals.py
# 定位:   给 `check_signature_audit_freshness.py` 的「合计行校验」提供**独立的**事实核对
#         （先人工确认现状对不对，再把判据接进门禁）。
# 官方依据: 不适用（本项目内部文档的算术自洽检查）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DOC = Path(r"C:\swprojects\sw-skill-fork\docs\signature-audit.md")

#: 合计/小计行的识别（表格行里第一格含「合计」或「小计」）
TOTAL_ROW = re.compile(r"^\|\s*\*{0,2}(合计|小计)\*{0,2}\s*\|")


def _cells(line: str) -> list:
    """把 `| a | b |` 切成 `['a', 'b']`（去空白与粗体标记）。"""
    parts = line.strip().strip("|").split("|")
    return [p.strip().replace("**", "") for p in parts]


def _num(text: str):
    """能取出一个数就返回，否则 None（`—` / `新增即合规` 之类不算数）。"""
    t = text.replace(",", "").strip()
    m = re.fullmatch(r"(\d+)", t)
    return int(m.group(1)) if m else None


def main() -> int:
    lines = DOC.read_text(encoding="utf-8").splitlines()
    checked = 0
    bad = 0
    for i, line in enumerate(lines):
        if not TOTAL_ROW.match(line):
            continue
        total = _cells(line)
        # 往上找连续的表体行（以 `|` 开头、不是分隔行、不是合计行、不是表头）
        body = []
        j = i - 1
        while j >= 0:
            prev = lines[j]
            if not prev.startswith("|"):
                break
            # ⚠⚠ **分隔行的判据**（2026-10-01 轮 69 实测踩过）：
            #   不能写 `set(prev.strip().strip("|")) <= set("-: ")` ——
            #   `strip("|")` 只去**首尾**的 `|`，而分隔行**中间**全是 `|`
            #   ⇒ 集合里含 `'|'` ⇒ 判不出 ⇒ **分隔行被当成表体**（`---` 非数字）
            #   ⇒ 后面每一列都"有非数字格 ⇒ 跳过" ⇒ **探针静默地什么都没查**
            #   （正是本项目记录过的「量太少本身就是假绿」）。
            #   ⇒ 正解：**逐格判**「这一格只由 `-` / `:` 组成」。
            if prev.strip() and all(set(c) <= set("-:") for c in _cells(prev)):
                j -= 1
                continue
            if TOTAL_ROW.match(prev):
                break
            body.append(_cells(prev))
            j -= 1
        body.reverse()
        # 去掉表头（第一行通常是非数字的列名）
        if body and all(_num(c) is None for c in body[0]):
            body = body[1:]

        print("  L%d 合计行: %s" % (i + 1, total))
        print("        表体 %d 行" % len(body))
        ncols = min(len(total), max((len(r) for r in body), default=0))
        for c in range(1, ncols):
            tval = _num(total[c]) if c < len(total) else None
            if tval is None:
                print("      col%d: 合计格不是纯数字（%r）⇒ 跳过" % (c, total[c]))
                continue
            vals = [(_num(r[c]) if c < len(r) else None) for r in body]
            if any(v is None for v in vals):
                print("      col%d: 表体有非数字格 ⇒ 跳过" % c)
                continue
            s = sum(vals)
            ok = (s == tval)
            checked += 1
            if not ok:
                bad += 1
            print("      col%d: %s = %d vs 合计 %d  %s"
                  % (c, " + ".join(str(v) for v in vals), s, tval,
                     "✓" if ok else "**✗ 不一致**"))
        print()

    print("  ── 校验了 %d 个列和，不一致 %d 个 ──" % (checked, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
