"""工具定义契约门禁：模型可见的 `doc` 与参数说明必须是「看一遍就能调对」的成品。

判据（规格 352 §二）：模型在 **lean 档**下只看得到 `firstLine(doc)`（≤120 字符），
在 **native / index 档**下看到整段 `doc` ⇒ 两档都要治：
首句必须自足，整段必须无考古记录。工程证据搬到 `ToolSpec.evidence`（非模型可见）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（把「工具描述写成变更日志」这件事接成硬门禁）
# 文件:   `scripts/check_tool_contract.py`（本文件自身）
#         `tests/test_tool_contract_gate.py`（双侧负例）
#         `specs/352-tool-definition-contract/spec.md` §二（判据与实测基线）
# 定位:   ★ 业主 2026-10-26：「你现在都是半成品…光看一下里面的参数，
#         你可能不懂它到底是干什么的」⇒ 把「描述能不能让人调对」变成机器判据。
# 官方依据: ① DSH `agent-experience`（`@deepseek-ai/dsh-agent-preset/skills/agent-experience/SKILL.md`）
#           逐字：「**Describe behavior, not implementation.** State what the tool does and
#           returns; omit internal mechanisms … and enforcement details」·
#           「**Put parameter rules on the parameter.**」
#         ② `@local/dsh-lean-mode/index.mjs` L130-131 逐字：
#           `description: firstLine(t.description)` ⇒ lean 下只保留首句、≤120 字符
#         ③ DSH 官方 n=72 工具实测（`docs/tool-description-style.md` §一）：
#           82% 动词开头、99% 句号收尾、参数描述 100% 句号收尾
# 许可:   本仓库 MIT。无第三方代码引入。★ 纯静态：读 `ToolSpec`，不连 SolidWorks。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

#: ★ 本门禁会 print 中文与 `★`/`⇒` 这类符号，而 stdout 是管道时默认按 locale（本机 GBK）
#: 编码 ⇒ `UnicodeEncodeError`（known-facts 58 那一族，病灶在输出侧）⇒ 强制 UTF-8 ✓
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "docs" / "tool-contract-baseline.json"

#: ★ lean 的硬上限（与 `index.mjs` 的 `firstLine()` 同口径）✓
LEAN_CHARS = 120
#: ★ 整段 `doc` 的上限：现状 p90=539、仅 36 条 >600 ⇒ 不逼人删真信息（spec D5）✓
DOC_CHARS = 600

CJK = re.compile(r"[\u4e00-\u9fff]")

#: ★★ 元数据标记：现行 274 条元数据首句里出现的正是这些（`output/_audit_tool_docs.json`）✓
#:   ★ 它们**不是不许存在**，而是**不许出现在首句** —— 搬到 `ToolSpec.evidence` ✓
META_MARKS = ("★", "⚠", "⇒", "✓", "✅", "✗", "官方签名", "查不到", "逐字")
META_PATTERNS = (re.compile(r"事实\s*\d+"), re.compile(r"规格\s*\d+"), re.compile(r"已知事实"))

#: ★ 首句动词白名单：取 DSH 官方 72 工具实测的动词句（`docs/tool-description-style.md` §一）
#:   ＋本仓 216 条已合规英文首句的动词。★ 扩充要写理由（spec §2.4）✓
VERBS = frozenset(
    """
    Create Read List Get Set Add Delete Remove Apply Export Import Run Check Insert Update
    Open Close Save Start Stop Select Measure Compute Find Report Validate Convert Generate
    Activate Suppress Unsuppress Move Copy Rotate Zoom Refresh Clear Build Write Draw Mesh
    Solve Query Search Inspect Describe Confirm Cancel Undo Redo Split Trim Extend Offset
    Mirror Pattern Annotate Dimension Attach Detach Enable Disable Load Unload Register
    Return Extract Rename Reorder Sort Count Hide Show Toggle Interrupt Wait Send Spawn
    Extrude Resolve Configure Collect Revolve Assign Switch Summarise Summarize Detect
    Enter Leave Chamfer Round Look Decide Hollow Join Explode Collapse Display Call Turn
    Release Block Replace Untrim Flatten Sweep Loft
    Skip Map Pull Choose Reuse Avoid Prefer Wrap Reset Normalize Scan Walk Stamp Derive
    Project Press
    """.split()
)

#: ★ 副作用词（K9 棘轮用）：DSH **不转发 MCP annotations**
#:   （`mcp-client/src/tools.ts` 只转 `name/description/parameters/output`）
#:   ⇒ ★★ 副作用**只能写在描述里**，否则模型看不见 ✓
SIDE_EFFECT_WORDS = (
    "Writes",
    "write",
    "Modifies",
    "modifies",
    "Creates",
    "creates",
    "Deletes",
    "deletes",
    "Clears",
    "clears",
    "Overwrites",
    "overwrites",
    "Saves",
    "saves",
    "Does not save",
    "does not save",
    "Read-only",
    "read-only",
)


def first_sentence(doc: str) -> str:
    """⇒ **英文意义上的第一句**（按 `.` / `!` / `?` + 空白断句）。

    ★★ 为什么**不**用 `split(/[。\\n]/)` 来取「首句」—— 这条是 `specs/215` 已经踩过的坑，
    本门禁再踩一次就会把判据定错：
      · `firstLine()` 的断句符只有 **`。`（中文句号）与换行**，**ASCII `.` 不算**；
      · 但英文 doc **没有** `。` 也没有换行 ⇒ `firstLine()` 取到的「第一段」= **整段 doc**，
        然后**整体截到 120 字符**。
      ⇒ ★ 所以英文 doc 在 lean 下真正的失败条件是「**第一个英文句子超过 120 字符**
         ⇒ 模型读到的是从中间被切断的半句**」，而不是「首句之后的内容看不到」✓
    ★ 断句是纯静态的近似（`e.g.` 这类缩写会被误切）；误切只会让判据**更严**、不会放过坏样本。
    """
    sents = _sentences(doc)
    return sents[0].strip() if sents else str(doc or "").strip()




def _first_word(text: str) -> str:
    """⇒ 首词（去掉 `Auto-` / `Re-` / `De-` / `Un-` / `Pre-` 这类前缀再比）。"""
    m = re.match(r"[A-Za-z][A-Za-z-]*", text.strip())
    if not m:
        return ""
    word = m.group(0)
    #: ★ `Auto-create` / `Re-run` / `Unsuppress` 都是合法祈使句 ⇒ 去掉可识别前缀再进白名单 ✓
    for pre in ("Auto-", "auto-", "Re-", "re-", "De-", "de-"):
        if word.startswith(pre) and len(word) > len(pre):
            return word[len(pre) :]
    return word


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def judge_spec(spec) -> list[tuple[str, str]]:
    """⇒ `[(判据代号, 说明)]`：这个 spec 违反了**哪些**契约条款（空列表 = 合规）。

    ★ 纯函数（不碰文件、不碰 COM）⇒ 负例可以直接喂假 spec ✓
    """
    out: list[tuple[str, str]] = []
    doc = str(getattr(spec, "doc", "") or "")
    name = getattr(spec, "name", "?")

    # ── K1：整段 doc 的形态 ────────────────────────────────────────────
    if not doc.strip():
        out.append(("doc-empty", "doc 为空 ⇒ 模型看不到任何说明"))
        return out
    if CJK.search(doc):
        out.append(("doc-cjk", "doc 含中文 ⇒ lean 的 firstLine 会在第一个 `。` 处断句，"
                               "中文首句通常只剩 30–50 字符（英文能活 120）"))
    if "。" in doc:
        out.append(("doc-cn-period", "doc 含中文句号 `。` ⇒ lean 会在那里断句"))
    if "\n" in doc:
        out.append(("doc-newline", "doc 里有换行 ⇒ lean 在第一行处断句"))
    if not doc.rstrip().endswith((".", "!", "?")):
        out.append(("doc-no-period", "doc 不以句号收尾（官方实测 99% 收尾）"))

    # ── K2 / K3：首句 ────────────────────────────────────────────────
    first = first_sentence(doc)
    if not first:
        out.append(("first-empty", "首句为空"))
    else:
        if len(first) > LEAN_CHARS:
            out.append(
                ("first-too-long",
                 "首句 %d 字符 > %d ⇒ lean 下这句话会被从第 %d 字符处切断，模型读到半句"
                 % (len(first), LEAN_CHARS, LEAN_CHARS))
            )
        hit = [m for m in META_MARKS if m in first]
        hit += [p.pattern for p in META_PATTERNS if p.search(first)]
        if hit:
            out.append(
                ("first-meta", "首句是**元数据**（命中 %s）⇒ 模型第一眼看到的是出处而不是它干什么"
                 % "/".join(hit[:4]))
            )
        else:
            #: ★ 元数据首句必然也不是动词开头 ⇒ **一个病根只报一条**（否则同一处被数两次，
            #:   棘轮会把「改好了」读成「降了两条」，进度虚高）✓
            verb = _first_word(first)
            if verb.lower() not in {v.lower() for v in VERBS}:
                out.append(
                    ("first-not-verb", "首句不是动词开头（首词 %r）⇒ 官方的 82%% 是祈使句" % verb)
                )

    # ── K4：整段 doc 的体量与句数 ────────────────────────────────────
    if len(doc) > DOC_CHARS:
        out.append(("doc-too-long", "doc %d 字符 > %d ⇒ 考古记录应搬进 evidence" % (len(doc), DOC_CHARS)))
    if len(_sentences(doc)) < 2:
        out.append(("doc-one-sentence", "只有一句 ⇒ 缺「何时用 / 前置 / 副作用 / 返回什么」"))

    # ── K5：参数说明 ────────────────────────────────────────────────
    for p in getattr(spec, "params", None) or []:
        d = str(getattr(p, "description", "") or "")
        tag = "%s.%s" % (name, p.name)
        if not d.strip():
            out.append(("param-no-desc", "%s 没有说明" % tag))
            continue
        if CJK.search(d):
            out.append(("param-desc-cjk", "%s 的说明是中文（模型可见文本统一英文）" % tag))
        if not d.strip().endswith("."):
            out.append(("param-desc-no-period", "%s 的说明不以句号收尾（官方 100%% 收尾）" % tag))

    # ── K9（棘轮）：副作用必须在描述里说 ─────────────────────────────
    read_only = getattr(spec, "read_only", None)
    writes = getattr(spec, "writes", None)
    if read_only is True or (writes is not None and len(writes) == 0):
        if not any(w in doc for w in ("Read-only", "read-only", "Does not modify")):
            out.append(("side-effect-unstated", "只读工具的描述里没有 `Read-only`"))
    elif read_only is False or (writes is not None and len(writes) > 0):
        if not any(w in doc for w in SIDE_EFFECT_WORDS):
            out.append(("side-effect-unstated", "会改状态的工具，描述里没有副作用词"))

    # ── K10（棘轮）：有默认值的参数，说明里要有默认值 ────────────────
    for p in getattr(spec, "params", None) or []:
        d = str(getattr(p, "description", "") or "")
        default = getattr(p, "default", ...)
        if default is ... or getattr(p, "required", None) is True:
            continue
        if "default" not in d.lower():
            out.append(
                ("param-default-unstated",
                 "%s.%s 有默认值而说明里没写 defaults to" % (name, p.name))
            )

    return out


def scan(only: set[str] | None = None) -> tuple[list[dict], int]:
    """⇒ `(rows, checked)`：`rows` 每条 = 一处违规。

    字段：`name` / `code` / `subject`（参数级违规的参数名，否则空串）/ `why` /
    `first` / `first_len` / `doc_chars`。
    """
    sys.path.insert(0, str(ROOT / "mcp-server"))
    sys.path.insert(0, str(ROOT / "scripts"))
    sys.path.insert(0, str(ROOT))
    import register_capabilities as rc  # noqa: PLC0415
    from check_lean_first_line_caveat import lean_first as _lean  # noqa: PLC0415

    specs = rc.all_specs()
    rows: list[dict] = []
    for s in specs:
        if only and s.name not in only:
            continue
        doc = str(getattr(s, "doc", "") or "")
        first = first_sentence(doc)
        visible = _lean(doc)
        for code, why in judge_spec(s):
            rows.append(
                {
                    "name": s.name,
                    "code": code,
                    #: ★ 参数级违规必须带参数名 —— 否则同一工具的两个坏参数会**塌成一个键**，
                    #:   修掉其中一个就被判「已收敛」（棘轮会误判为进步）✓
                    "subject": why.split(" ")[0].split(".")[-1] if code.startswith("param-") else "",
                    "why": why,
                    "first": first,
                    "first_len": len(first),
                    "doc_chars": len(doc),
                    #: ★ 模型在 lean 档下**真正看到**的那一段（证据用；判据不直接读它）✓
                    "visible": visible,
                }
            )
    return rows, len([s for s in specs if not only or s.name in only])


def counts_by_code(rows: list[dict]) -> dict:
    out: dict = {}
    for r in rows:
        out[r["code"]] = out.get(r["code"], 0) + 1
    return out


def _key(r: dict) -> tuple:
    return (r.get("name", ""), r.get("code", ""), r.get("subject", ""))


def compare_with_baseline(rows: list[dict], baseline: dict) -> list[dict]:
    """⇒ 比基线**新增**的违规（★ 棘轮：只许降不许升）。

    ★★ 为什么**全部**判据都进基线（而不是只让语义判据走棘轮）：
      迁移期 498 条要分 8 批改，若硬判据当场红，`release_check` 在这几批之间**一直是红的**
      ⇒ 收尾链无法通过、每批都没法单独提交。基线承载「还没改到的那些」，
      ★ 判据变成「**一处都没多**」；改完的条目从基线里删掉 ⇒ **基线只降** ✓
    ★ 迁移结束时基线应为**空**（A1：498/498 零违反），用 `--strict` 复核 ✓
    """
    if not baseline:
        return rows
    base_keys = {_key(r) for r in baseline.get("rows", [])}
    return [r for r in rows if _key(r) not in base_keys]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="工具定义契约门禁（规格 352）")
    ap.add_argument("--report", action="store_true", help="只报表，退出码仍按判据给")
    ap.add_argument("--only", default="", help="只查这些工具（逗号分隔）")
    ap.add_argument("--json", default="", help="把逐条读数写到这个路径（供交叉核对）")
    ap.add_argument("--baseline", default=str(BASELINE), help="棘轮基线路径")
    ap.add_argument("--write-baseline", action="store_true", help="把当前违规写进基线（只许降）")
    ap.add_argument("--strict", action="store_true", help="忽略基线：所有违规都算（验收 A1 用）")
    args = ap.parse_args(argv)

    only = {x.strip() for x in args.only.split(",") if x.strip()} or None
    rows, checked = scan(only)

    #: ★ 防假绿：一条都没看就等于没判（与旧门禁的 `checked < 300` 同型）✓
    if checked < (1 if only else 300):
        print("★ 只看到 %d 条 spec ⇒ 注册表可能没加载全，**这个绿不可信**" % checked)
        return 2

    baseline: dict = {}
    bp = Path(args.baseline)
    if bp.exists():
        try:
            baseline = json.loads(bp.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            print("★ 基线读不出来（%s: %s）⇒ 本门禁无法判定" % (type(exc).__name__, exc))
            return 2

    if args.write_baseline:
        prev = int(baseline.get("count", len(baseline.get("rows", []))))
        #: ★ 仅**首次立基线**允许从 0 涨上来（文件不存在 = 还没有基线）；
        #:   一旦存在，**只许降**（棘轮）✓
        if bp.exists() and len(rows) > prev:
            print(
                "✗ 拒绝写基线：当前 %d 条 > 既有基线 %d 条 —— **棘轮只许降不许升**"
                "（要放宽先改 spec 并说明理由）" % (len(rows), prev)
            )
            for r in compare_with_baseline(rows, baseline)[:30]:
                print("   新增 [%s] %s —— %s" % (r["code"], r["name"], r["why"]))
            return 1
        bp.write_text(
            json.dumps(
                {"count": len(rows), "counts": counts_by_code(rows), "rows": rows},
                ensure_ascii=False,
                indent=1,
            )
            + "\n",
            encoding="utf-8",
        )
        print("★ 已写基线：%s（%d 条，上一版 %d 条）" % (bp.name, len(rows), prev))
        return 0

    if args.strict or not baseline:
        new_rows = rows
    else:
        new_rows = compare_with_baseline(rows, baseline)

    if args.json:
        Path(args.json).write_text(
            json.dumps(
                {
                    "checked": checked,
                    "counts": counts_by_code(rows),
                    "rows": rows,
                    "measure": [
                        {
                            "name": r["name"],
                            "first": r["first"],
                            "first_len": r["first_len"],
                            "doc_chars": r["doc_chars"],
                        }
                        for r in _dedup_by_name(rows)
                    ],
                },
                ensure_ascii=False,
                indent=1,
            )
            + "\n",
            encoding="utf-8",
        )

    bad = new_rows
    if args.report:
        mode = "strict（忽略基线）" if args.strict else "基线模式"
        print(
            "★ [%s] 看了 %d 条 spec；违规合计 **%d** 条（基线 %d 条；**本次新增 %d**）"
            % (mode, checked, len(rows), int(baseline.get("count", 0)), len(bad))
        )
        for code, n in sorted(counts_by_code(rows).items(), key=lambda kv: -kv[1]):
            print("   %-26s %d" % (code, n))
        for r in bad[:60]:
            print("   [%s] %s —— %s" % (r["code"], r["name"], r["why"]))
        return 1 if bad else 0

    if bad:
        print("★ 工具定义契约门禁未通过（%d 条）：" % len(bad))
        for r in bad:
            print("   [%s] %s" % (r["code"], r["name"]))
            print("        %s" % r["why"])
        print("\n★ 修法：见 `specs/352-tool-definition-contract/spec.md` §二；")
        print("   ★ 首句 = `<动词> <对象> <关键限定>.`（≤120 字符、英文、无 ★/官方签名/查不到）")
        print("   ★ 第二句 = 何时用 / 前置 / 副作用 / 返回什么；工程证据搬进 `ToolSpec.evidence`")
        return 1

    print(
        "★ 工具定义契约门禁通过：看了 %d 条 spec，**相对基线没有新增违规**（基线 %d 条待收敛）"
        % (checked, int(baseline.get("count", 0)))
    )
    return 0


def _dedup_by_name(rows: list[dict]) -> list[dict]:
    seen: dict = {}
    for r in rows:
        seen.setdefault(r["name"], r)
    return list(seen.values())


if __name__ == "__main__":
    raise SystemExit(main())
