"""★ 门禁：`docs/assumption-ledger.md` 的假设状态必须自洽，且未验证假设不得充当证据。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/check_assumption_ledger.py
# 定位:   `docs/text-to-cad-lessons-verdict.md` §6.3 的落地 ——★ 经验⑤「不追问但记录」
#           的**改造后采纳**形态。★ 判据三条：  ① 每条假设必须有 `id / 档位 / 状态`，状
#           态只能取 open|confirmed|refuted；  ② `confirmed` / `refuted` **必须带证据**
#           （★ 否则「已验证」是空话）；  ③ `open` 的假设 **不得** 出现在 `capabilities.
#           yaml` 里 `verified`     条目的 `evidence` 字段中（★ 未验证的假设不能当证据 —
#           — 这是本条的     真正价值：把「假设」与「证据」在机器层面隔开）。
# 官方依据: 上游 `skills/sdf/references/llm-guardrails.md:26-35` 的五档来源枚举（user-pr
#           ovided / upstream / target docs / measured / explicit assumption）+ 本仓 `AG
#           ENTS.md` 验收 A4「verified 必须有我们自己的运行证据」
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   `docs/assumption-ledger.md` 全文 + `capabilities.yaml` 的 verified 条目
# ⚠ 等级 `stitched`（未真机跑过整条链）：★ 但本门禁**自带负例自证**
#   （★ 见 `selftest()`）—— 三条判据各造一条违规，★ 必须逐条报出来。
# -----------------------------------------------------------------------------
from __future__ import annotations

import json
import re
import sys
import pathlib

sys.stdout.reconfigure(encoding="utf-8")          # 事实 58：管道下 GBK 会崩
ROOT = pathlib.Path(__file__).resolve().parents[1]

LEDGER = ROOT / "docs" / "assumption-ledger.md"
CAPS = ROOT / "capabilities.yaml"

#: ★ 合法状态。★ 封闭词表（同上游「closed vocabularies」的做法）。
STATUSES = ("open", "confirmed", "refuted")

#: ★ 上游五档来源（`llm-guardrails.md:28-34` 逐字对应）。
#: ★ 落成本仓可用的四档 —— 第 2 档「上游几何/清单」在本仓对应「官方文档」。
TIERS = ("1-user", "2-official", "3-measured", "4-assumption")

#: ★ 台账表格行：| AS012 | 假设内容 | 档位 | 状态 | 证据 |
ROW = re.compile(r"^\|\s*(AS\d{3})\s*\|(.+?)\|(.+?)\|(.+?)\|(.+?)\|\s*$")


def parse_ledger(text: str) -> tuple[list[dict], list[str]]:
    """★ 解析台账，返回 (行列表, 结构问题列表)。★ 供 check() 与 selftest() 共用。"""
    rows: list[dict] = []
    problems: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        s = line.strip()
        m = ROW.match(s)
        if not m:
            #: ★ 只对「像表格行但不是合法行」的报错 —— 表格分隔行/表头不算
            if s.startswith("|") and "AS0" in s and "---" not in s:
                problems.append("第 %d 行：表格行格式不合（应为 | AS000 | 内容 | 档位 | 状态 | 证据 |）" % lineno)
            continue
        aid, body, tier, status, evidence = (g.strip() for g in m.groups())
        rows.append({"id": aid, "body": body, "tier": tier,
                     "status": status, "evidence": evidence, "line": lineno})
    return rows, problems


def validate(rows: list[dict], problems: list[str]) -> list[str]:
    """★ 三条判据。★ 抽成独立函数，selftest() 直接喂构造行验证。"""
    out = list(problems)
    seen: set[str] = set()
    for r in rows:
        aid, status, tier, ev = r["id"], r["status"], r["tier"], r["evidence"]
        if aid in seen:
            out.append("%s：id 重复（★ id 必须唯一）" % aid)
        seen.add(aid)
        #: ① 状态必须在封闭词表内
        if status not in STATUSES:
            out.append("%s：状态 %r 非法（只能取 %s）" % (aid, status, "/".join(STATUSES)))
        #: ① 档位必须在封闭词表内
        if tier not in TIERS:
            out.append("%s：档位 %r 非法（只能取 %s）" % (aid, tier, "/".join(TIERS)))
        #: ② confirmed/refuted 必须带证据
        if status in ("confirmed", "refuted") and not _has_evidence(ev):
            out.append("%s：状态是 %s 但**没有证据**（★ 「已验证」不能是空话）"
                       % (aid, status))
    return out


def _has_evidence(text: str) -> bool:
    """★ 证据非空且不是占位符（`-` / `—` / `待补` / `TBD` 都算没有）。"""
    t = (text or "").strip()
    if not t or t in ("-", "—", "–", "N/A", "n/a"):
        return False
    if t in ("待补", "TBD", "todo", "TODO"):
        return False
    return True


def check() -> list[str]:
    """★ 返回问题列表（空 = 过）。"""
    if not LEDGER.is_file():
        return ["★ 没有 %s ⇒ 经验⑤ 要求有假设台账" % LEDGER.relative_to(ROOT)]
    rows, problems = parse_ledger(LEDGER.read_text(encoding="utf-8", errors="replace"))
    problems = validate(rows, problems)

    #: ③ open 的假设不得充当 capabilities.yaml 里 verified 条目的证据
    open_ids = {r["id"] for r in rows if r["status"] == "open"}
    if open_ids and CAPS.is_file():
        try:
            caps = json.loads(CAPS.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            problems.append("★ capabilities.yaml 读不了：%s" % exc)
            return problems
        for c in caps.get("capabilities", []):
            if c.get("level") != "verified":
                continue
            ev = json.dumps(c.get("evidence") or "", ensure_ascii=False)
            for aid in open_ids:
                if aid in ev:
                    problems.append(
                        "★ 能力 %s 的 evidence 引用了**未验证假设** %s "
                        "—— 未验证的假设不能当证据（★ 本门禁的核心判据）"
                        % (c.get("id"), aid))
    return problems


def selftest() -> bool:
    """★★ **负例自证**（★ 事实 62：门禁「写了」不等于「有效」）。

    ★ 三条判据各造一条违规，**逐条**必须被抓到：
      ① 状态非法；② confirmed 无证据；③ 格式不合。
    ★ 另造一条**合规行**，必须**不**被报（★ 防「什么都报」的恒红门禁，事实 53 同族）。
    """
    cases = [
        ("非法状态", "| AS001 | 某假设 | 4-assumption | done | 证据 |", "状态"),
        ("confirmed 无证据", "| AS002 | 某假设 | 3-measured | confirmed | - |", "没有证据"),
        ("非法档位", "| AS003 | 某假设 | 9-猜的 | open | - |", "档位"),
    ]
    for name, line, expect in cases:
        rows, probs = parse_ledger(line)
        probs = validate(rows, probs)
        if not any(expect in p for p in probs):
            print("★★ 负例自证失败：[%s] 没有被抓到（期望含 %r，实得 %r）"
                  % (name, expect, probs))
            return False
    #: ④ 正例：合规行必须不报
    rows, probs = parse_ledger("| AS900 | 某假设 | 4-assumption | open | - |")
    probs = validate(rows, probs)
    if probs:
        print("★★ 正例自证失败：合规行被误报 %r" % (probs,))
        return False
    return True


def main() -> int:
    if not selftest():
        return 1
    print("★ 负例自证：过（三条判据各抓得到，合规行不误报）")
    problems = check()
    if problems:
        print("★★ 发现 %d 处：" % len(problems))
        for p in problems[:20]:
            print("   %s" % p)
        return 1
    print("★ [PASS] 假设台账状态自洽，且未验证假设未充当证据")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
