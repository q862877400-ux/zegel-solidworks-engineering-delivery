"""★ EC00 残留 ③ 审计 —— 逐份核 `output/ENGINEERING_*.md` 的「来源+许可+可运行验收」三项。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/DSH_DECISIONS.md` **D8**（★ 逐字：「正式 spec 要求**来源 + 许可 + 可运
# 行验收**
#           三项齐；★ 本轮**未逐份核对**这三项」）
#         `output/ENGINEERING_*.md`（★ 待审计的草案）
# 定位:   ★ 清 **EC00 残留 ③**。★★★ **D8 的关键区分**：· ★ 那是**事实缺口**（★ 「未逐
#           份核对」）—— ★ **不是决策缺口**· ★★ 所以业主授权**不能**用来「拍板判达标」✗·
#            ★★★ **正解 = 把事实核出来**（★ 逐份查那三项）
# 官方依据: 不适用（本仓自产的审计器）
# 许可:   本仓库自产（无外部来源）
# 覆盖:   只读 `output/ENGINEERING_*.md` 与 `DSH_*.md`；★ **只写** 一份读数 JSON
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "_probe_ec00_drafts_audit.json"

#: ★★ 三项判据（★ 逐条给**可指认**的正则 —— ★ 不是「看着像」）
#:   ★★★ **2026-10-10 订正**：★ 第一版把「可运行验收」写成 `\.py` 太宽（★ 命中**散文里的
#: `scripts/sw_fingerprint.py`** ⇒ ★ 假达标）★ 又把 `→ 验收` 当判据（★ 那是**声明**不是*
#: *命令**）
#:   ⇒ ★★ **收紧成「必须有一条**可跑的命令行**」**（★ 解释器 + 脚本/`-m pytest`）。
CHECKS = {
    #: ① 来源：★ 必须**指认真实路径**（★ 本仓路径或官方源路径）
    "provenance": (
        r"(?:D:\\AI\\SW|C:\\swapi|C:\\swprojects|\.specify/|scripts/|mcp-server/|tools/|tests/|specs/)",
        "★ 指认了**真实路径**（本仓或官方源）",
    ),
    #: ② 许可：★ 必须**明写** license（★ 本仓 MIT 或外部来源的许可）
    "license": (
        r"(?:MIT|Apache-2\.0|AGPL|GPL|本仓.{0,4}MIT|license|许可)",
        "★ 明写了 license / 许可",
    ),
    #: ③ 可运行验收：★★ **必须有一条可跑的命令行**（★ 解释器 + 脚本，★ 或 `-m pytest`）
    #:   ★★ 依据（★ D8 逐字）：★「**可运行验收**」—— ★ 「验收清单」那种**标题**不算。
    "runnable_acceptance": (
        r'(?:"[^"]*python[^"]*"|python3?)\s+(?:-B\s+)?(?:-m\s+pytest|["\']?[A-Za-z]:[/\\][^"\'\s]*\.py|output[/\\][^"\'\s]*\.py|tools[/\\][^"\'\s]*\.py|scripts[/\\][^"\'\s]*\.py)',
        "★ 给了**可跑的命令行**（解释器 + 脚本 / `-m pytest`）",
    ),
}


def audit(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    row: dict = {"file": path.name, "bytes": len(text.encode("utf-8")),
                 "lines": text.count("\n") + 1}
    for key, (pattern, desc) in CHECKS.items():
        hits = re.findall(pattern, text)
        row[key] = {"ok": bool(hits), "hits": len(hits), "desc": desc}
    #: ★★ 三项齐 = 达标（★ 那是**事实结论**，★ 不是拍板）
    row["three_of_three"] = all(row[k]["ok"] for k in CHECKS)
    #: ★★ 额外：★ 「草案」自称（★ D8 说它们是草案 —— ★ 自查是否自认）
    row["self_declares_draft"] = bool(re.search(r"DRAFT|草案|待评审", text))
    return row


def main() -> int:
    files = sorted((ROOT / "output").glob("ENGINEERING_*.md"))
    rows = [audit(p) for p in files]
    #: ★ 另算 DSH_* 那批（★ D8 只提 ENGINEERING_*，★ 但那批也需同样口径）
    dsh = sorted((ROOT / "output").glob("DSH_*.md"))
    dsh_rows = [audit(p) for p in dsh]

    ok = [r for r in rows if r["three_of_three"]]
    bad = [r for r in rows if not r["three_of_three"]]
    dsh_ok = [r for r in dsh_rows if r["three_of_three"]]

    result = {
        "probe": "ec00-drafts-three-item-audit",
        "criterion": "来源 + 许可 + 可运行验收（★ D8 逐字）",
        "engineering_total": len(rows),
        "engineering_three_of_three": len(ok),
        "engineering_not_qualified": len(bad),
        "dsh_total": len(dsh_rows),
        "dsh_three_of_three": len(dsh_ok),
        "engineering_rows": rows,
        "dsh_rows": dsh_rows,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("★ ENGINEERING_*.md 共 %d 份 · 三项齐 **%d** · 不齐 %d"
          % (len(rows), len(ok), len(bad)))
    for r in rows:
        marks = "".join("✓" if r[k]["ok"] else "✗" for k in CHECKS)
        print("   %s  %-46s %d 行 · 自称草案=%s"
              % (marks, r["file"], r["lines"], r["self_declares_draft"]))
    print("   （★ 列序：来源 · 许可 · 可运行验收）")
    print("★ DSH_*.md 共 %d 份 · 三项齐 **%d**" % (len(dsh_rows), len(dsh_ok)))
    for r in dsh_rows:
        marks = "".join("✓" if r[k]["ok"] else "✗" for k in CHECKS)
        print("   %s  %s" % (marks, r["file"]))
    print("产物：%s" % OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
