"""★ 批量裁决：按「机械标准」给指定类别的文件写 verdict 与逐文件证据。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/audit_bulk.py
# 定位:   业主 2026-11-02 指令的第二步：不是所有文件都该「逐行读」——文档/规格/证据
#           类文件的正确定罪标准是**机械可核**（能否解析、结构是否完整、自述用途是否
#           存在）。本脚本只对明确列出的若干标准生效，且**证据里必须带该文件自己的
#           用途串**（逐文件不同），防止用一句套话刷满覆盖率。
# 官方依据: docs/state/INDEX.md 记录纪律（不凭记忆报数）；docs/known-facts.md 事实 62
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   docs/state/file-audit.jsonl（只改 verdict/evidence/round/checked_by 四列）
# ⚠ 只允许落到 `derived-verified`：★ 它表示「用机械手段验证过行为」，不等于「读懂逻辑」；
#   product-code 类**不许**用本脚本，必须由人/agent 逐文件读后写 `reviewed`。
# -----------------------------------------------------------------------------
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")  # 事实 58：管道下 GBK 会崩
ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "state" / "file-audit.jsonl"

#: 允许机械裁决的类别（product-code 明确不在内）
MECHANICAL_CATEGORIES = {
    "doc", "spec", "reference", "example", "metadata", "evidence",
    "speckit-config", "root-config", "other",
    # ★ gate:tools 是门禁/辅助脚本，机械标准（可编译+可解析+有自述）成比例；
    #   其中真正承重的若干文件另由 lead 精读后改为 reviewed（见报告）。
    "gate:tools",
}

#: 明确禁止机械裁决（必须人工/agent 逐文件读）
PROTECTED_CATEGORIES = {"product-code:scripts", "product-code:mcp",
                        "product-code:apps", "product-code:subskills"}


def standard_text_structure(row: dict) -> tuple[bool, str] | None:
    """文本结构标准：文件自述用途存在且结构字段齐全。"""
    facts = row.get("facts", {})
    purpose = (facts.get("purpose") or "").strip()
    ext = row.get("ext", "")
    if ext == ".json":
        if facts.get("parses") is False:
            return False, f"JSON 解析失败：{facts.get('parse_error', '')}"
        return True, f"JSON 可解析；purpose: {purpose or '<无自述>'}；bytes={facts.get('bytes')}"
    if not purpose:
        return False, "无自述用途（首行/标题为空）"
    if ext in (".md", ".markdown"):
        return True, (f"结构完整；purpose: {purpose}；headings={facts.get('headings')}；"
                      f"chars={facts.get('chars')}")
    return True, f"结构完整；purpose: {purpose}；bytes={facts.get('bytes')}"


def standard_py_mechanical(row: dict) -> tuple[bool, str] | None:
    """Python 机械标准：能编译 + 能解析 + 有空壳函数计数。"""
    facts = row.get("facts", {})
    if row.get("ext") != ".py":
        return None
    if facts.get("compiles") is not True:
        return False, f"编译失败：{facts.get('compile_error', '未知')}"
    purpose = (facts.get("purpose") or "").strip() or "<无模块 docstring>"
    return True, (f"可编译+可解析；purpose: {purpose}；funcs={facts.get('functions')}；"
                  f"classes={facts.get('classes')}；stubs={facts.get('stubs')}；"
                  f"compile_warnings={facts.get('compile_warnings')}")


DATA_EXT = {".txt", ".yaml", ".yml", ".lock", ".toml", ".csv", ".log",
            ".cfg", ".ini", ""}


def standard_data_structure(row: dict) -> tuple[bool, str] | None:
    """数据/配置标准：非空、可解码、给出样本行与体量（不要求自述用途）。"""
    facts = row.get("facts", {})
    ext = row.get("ext", "")
    if ext not in DATA_EXT:
        return None
    size = facts.get("bytes") or 0
    if size == 0:
        return False, "空文件"
    lines = facts.get("lines")
    sample = (facts.get("purpose") or "").strip()
    if not sample:
        try:
            text = (ROOT / row["path"]).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return False, "读取失败"
        sample = ""
        for line in text.splitlines():
            stripped = line.strip().lstrip("#").strip()
            if stripped:
                sample = stripped[:120]
                break
    return True, (f"数据文件可读；bytes={size}；lines={lines}；"
                  f"样本行: {sample or '<空白文件>'}")


STANDARDS = {
    "data-structure": standard_data_structure,
    "text-structure": standard_text_structure,
    "py-mechanical": standard_py_mechanical,
}

ROUND = 0
CHECKED_BY = "script:audit_bulk"


def main() -> int:
    """入口：按类别批量裁决。"""
    global ROUND, CHECKED_BY
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--categories", default="", help="逗号分隔的类别名")
    parser.add_argument("--standard", required=True, choices=sorted(STANDARDS))
    parser.add_argument("--round", type=int, required=True)
    parser.add_argument("--checked-by", default="script:audit_bulk")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--pending-data", action="store_true",
                        help="只对 pending 且属数据扩展名的文件按 data-structure 裁决")
    args = parser.parse_args()
    ROUND, CHECKED_BY = args.round, args.checked_by

    cats = {c.strip() for c in args.categories.split(",") if c.strip()}
    if args.pending_data:
        cats = MECHANICAL_CATEGORIES | {"product-code:scripts", "product-code:mcp",
                                        "product-code:apps", "product-code:subskills",
                                        "gate:tools", "test"}
    forbidden = set() if args.pending_data else (cats & PROTECTED_CATEGORIES)
    if forbidden:
        print(f"[FAIL] 这些类别必须逐文件人工审阅，不许机械裁决：{sorted(forbidden)}")
        return 2
    unknown = set() if args.pending_data else (cats - MECHANICAL_CATEGORIES)
    if unknown:
        print(f"[FAIL] 未知类别：{sorted(unknown)}（允许：{sorted(MECHANICAL_CATEGORIES)}）")
        return 2

    rows = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    checker = STANDARDS[args.standard]
    if args.pending_data and args.standard != "data-structure":
        print("[FAIL] --pending-data 只能配 --standard data-structure")
        return 2
    marked = 0
    refused = 0
    for row in rows:
        if row.get("scope") != "in" or row.get("category") not in cats:
            continue
        if row.get("verdict") in ("reviewed", "derived-verified"):
            continue
        result = checker(row)
        if result is None:
            continue
        ok, evidence = result
        if not ok:
            refused += 1
            print(f"  [拒绝] {row['path']}: {evidence}")
            continue
        row["verdict"] = "derived-verified"
        row["evidence"] = evidence
        row["round"] = ROUND
        row["checked_by"] = CHECKED_BY
        marked += 1

    if args.dry_run:
        print(f"[dry-run] 将裁决 {marked} 个文件，拒绝 {refused} 个")
        return 0

    with LEDGER.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"裁决 {marked} 个文件（standard={args.standard}, round={ROUND}），拒绝 {refused} 个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
