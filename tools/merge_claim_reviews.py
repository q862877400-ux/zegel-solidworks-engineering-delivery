"""把「人工复核档」合并回批次台账（`B1…B8.json`）。

用途（规格 353 · T-353-21）：63 条工具被自动门槛拦下（首句与官方描述零词干重叠 /
锚点空 / 草稿缺）。逐条读页复核后，复核人把记录写进 `review-*.json`（一批一个文件、
写者不相交），本工具把它们**按工具名覆盖**回对应批次文件。

★ 为什么不让复核人直接改 `B*.json`：多批并行时同一文件会被两个写者改 ——
  文件级不相交才不会有覆盖事故（`specs/352` D7 的教训）。合并只由本工具做。

校验（不合格就整条拒绝并报错，不静默跳过）：
  · `tool` 必须存在、`impl` 必须能解析、`claim` 必须等于工具 `doc` 首句；
  · `verified.by` / `verified.at` 必填；★ 复核档的 `verified.level` 一律写 `"human"`；
  · `members[]` 里 `documented:false` 的必须带非空 `gap`。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 353 P2c 的合并器）
# 文件:   `scripts/check_tool_official_claims.py`（判据与解析，复用不重写）
#         `docs/tool-official-claims/B*.json`（批次台账，自动档）
#         `docs/tool-official-claims/review-*.json`（复核档，人读的）
#         `docs/tool-official-claims/README.md`（记录格式）
# 定位:   ★ `specs/353-mcp-tool-official-audit/spec.md` §六 P2c ——
#         自动档落 479 条后，剩下的 63 条靠人读官方页；本工具负责把它们合回台账。
# 官方依据: 不适用（只做文件合并与格式校验，不读官方页）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件；**不连 SolidWorks**
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "tool-official-claims"
sys.path.insert(0, str(ROOT / "scripts"))

from check_tool_official_claims import first_sentence, resolve_impl  # noqa: E402


def tool_docs() -> dict[str, str]:
    """⇒ `{工具名: 模型可见描述}`（真握手那份，手写工具也有）。

    """
    sys.path.insert(0, str(ROOT / "mcp-server"))
    sys.path.insert(0, str(ROOT / "tools"))
    import register_capabilities as rc  # noqa: PLC0415
    from mcp_tools_list import tools_list  # noqa: PLC0415

    out = {t["name"]: str(t.get("description") or "") for t in tools_list()}
    for s in rc.all_specs():
        out[s.name] = str(s.doc or "")
    return out


def validate(rec: dict, docs: dict[str, str]) -> list[str]:
    """⇒ 这条复核记录的问题清单（空 = 可用）。

    :param rec: 复核档里的一条记录。
    :param docs: 工具名 → 模型可见描述。
    """
    bad: list[str] = []
    tool = str(rec.get("tool") or "")
    if tool not in docs:
        return ["工具不存在：%r" % tool]
    impl = str(rec.get("impl") or "")
    rel, _, func = impl.rpartition(":")
    if not rel or not func or not resolve_impl(rel).is_file():
        bad.append("impl 解析不到：%r" % impl)
    if str(rec.get("claim") or "").strip() != first_sentence(docs[tool]).strip():
        bad.append("claim ≠ 工具 doc 首句（台账 %r / 可见 %r）" % (rec.get("claim"), first_sentence(docs[tool])))
    ev = rec.get("claim_evidence") or {}
    if not str(ev.get("path") or "").strip() or not str(ev.get("anchor") or "").strip():
        bad.append("claim_evidence 缺 path/anchor")
    ver = rec.get("verified") or {}
    if not str(ver.get("by") or "").strip() or not str(ver.get("at") or "").strip():
        bad.append("verified.by / verified.at 缺")
    elif str(ver.get("level") or "") != "human":
        bad.append("复核档的 verified.level 必须是 human（实际 %r）" % ver.get("level"))
    for m in rec.get("members") or []:
        if m.get("documented") is False and not str(m.get("gap") or "").strip():
            bad.append("成员 %s 标了 documented:false 但没写 gap" % m.get("member"))
    return bad


def main(argv=None) -> int:
    """命令行入口：`--write` 才真正合并。

    :param argv: 命令行参数。
    """
    ap = argparse.ArgumentParser(description="合并人工复核档到批次台账（规格 353 P2c）")
    ap.add_argument("--dir", default=str(LEDGER))
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    ledger = Path(args.dir)
    docs = tool_docs()
    incoming: dict[str, tuple[str, dict]] = {}  # 工具名 → (来源文件, 记录)
    problems: list[str] = []
    for path in sorted(ledger.glob("review-*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append("%s 读不了：%s" % (path.name, exc))
            continue
        for rec in data.get("records") or []:
            bad = validate(rec, docs)
            if bad:
                problems.append("%s / %s：%s" % (path.name, rec.get("tool"), "；".join(bad)))
                continue
            incoming[str(rec["tool"])] = (path.name, rec)

    #: ★ `drop` 名单：复核人判定「这条自动记录不该存在」（首句与官方/实现不符）时，
    #:   合并器要把该工具从台账里**删掉**，否则台账会继续断言一条已被否掉的描述。
    #:   ★ 只接受 review-* 文件里的 `drop`，且必须写明 `why`。
    drops: dict[str, str] = {}
    for path in sorted(ledger.glob("review-*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for item in data.get("drop") or []:
            tool = str(item.get("tool") or "")
            why = str(item.get("why") or "").strip()
            if tool and why:
                drops[tool] = why

    if problems:
        print("✗ %d 条复核记录不合格，**整条不合并**：" % len(problems))
        for p in problems[:30]:
            print("   %s" % p)
        return 1

    if not incoming:
        print("★ 没有 review-*.json（或全部为空）⇒ 无事可做")
        return 0

    #: ★ 每条只进**它自己那一批**的文件；★ 不能"每条写进每个 B*.json" ——
    #:   那会把同一工具复制到 8 个文件里，门禁按工具名去重，绿得莫名其妙（实测踩过）
    sys.path.insert(0, str(ROOT / "tools"))
    from apply_tool_official_claims import batch_of  # noqa: PLC0415

    per_batch: dict[str, dict[str, dict]] = {}
    for tool, (src, rec) in incoming.items():
        per_batch.setdefault(batch_of(tool), {})[tool] = rec

    dropped = 0
    if drops and args.write:
        for batch_file in sorted(ledger.glob("B*.json")):
            data = json.loads(batch_file.read_text(encoding="utf-8"))
            records = data.get("records") or []
            keep = [r for r in records if r["tool"] not in drops]
            if len(keep) != len(records):
                dropped += len(records) - len(keep)
                data["records"] = keep
                batch_file.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    merged = 0
    for batch, tools in sorted(per_batch.items()):
        batch_file = ledger / ("%s.json" % batch)
        data = json.loads(batch_file.read_text(encoding="utf-8")) if batch_file.is_file() else {"batch": batch, "records": []}
        records = data.get("records") or []
        by_tool = {r["tool"]: i for i, r in enumerate(records)}
        for tool, rec in tools.items():
            if tool in by_tool:
                records[by_tool[tool]] = rec
            else:
                records.append(rec)
            merged += 1
        data["records"] = records
        if args.write:
            batch_file.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if drops:
        print("   ★ 按 `drop` 名单删除 %d 条旧记录（%s）" % (dropped, "、".join(sorted(drops)[:6])))
    print("★ %s %d 条复核记录进批次台账（%s）"
          % ("已合并" if args.write else "预览（未写盘）", merged, "、".join("%s %d" % (b, len(v)) for b, v in sorted(per_batch.items()))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
