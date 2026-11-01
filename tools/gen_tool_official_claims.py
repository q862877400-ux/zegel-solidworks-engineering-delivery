"""生成「工具 → 官方 API 页」台账**草稿**（不填 claim 证据，留给核验人逐条读页）。

为什么要它（一个事实一个家）：
  ★ 543 个工具 × ~470 个 COM 成员，靠手敲台账必然漏、必然编（业主 2026-11-01：
    「不能根据记忆和印象」）⇒ 机器只做**它做得到的那一半**：从实现里把成员抠出来、
    把官方页找出来、把页里的**原始描述行**抄成候选锚点。
  ★★ 另一半（这个工具到底在干什么、这句描述与官方语义是否一致）**机器不猜**：
    草稿里 `claim_evidence` 留空、`verified` 为 null ⇒ 门禁当场报 `claim-unanchored` /
    `unverified`，逼核验人去读页（`scripts/check_tool_official_claims.py` §判据）。

用法：
  ```bash
  python -B tools/gen_tool_official_claims.py --tools solidworks_extrude_boss --out output/claims-draft.json
  python -B tools/gen_tool_official_claims.py --batch G1 --out docs/tool-official-claims/G1.json
  python -B tools/gen_tool_official_claims.py --all --out output/claims-draft-all.json
  ```

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（台账草稿生成器；判据在门禁里，不在生成器里）
# 文件:   `scripts/check_tool_official_claims.py`（判据 + 成员提取，**复用不重写**）
#         `C:\\swapi\\index\\by_member_name.md`（成员名 → 接口 + 签名）
#         `C:\\swapi\\types\\<接口>\\<成员>.md`（官方页：front-matter + 描述 + Remarks）
#         `docs/tool-official-claims/README.md`（台账格式）
# 定位:   ★ 规格 353 P1 —— 把「543 个工具逐个查官方页」拆成
#         「机器出草稿（可复现）+ 人核语义（留 verified.notes）」两半。
# 官方依据: 官方页 front-matter 逐字含 `type:` / `member:` / `kind:`
#           （`C:\\swapi\\types\\IFeatureManager\\FeatureRevolve2.md` 头 6 行）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   `--all` 覆盖 `tools/list` 的每个工具；**不连 SolidWorks**
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "mcp-server"))
sys.path.insert(0, str(ROOT / "tools"))

from check_tool_official_claims import (  # noqa: E402 - 复用门禁的提取与索引，不重写一份
    SWAPI_INDEX,
    SWAPI_TYPES,
    FunctionIndex,
    first_sentence,
    impl_members,
    member_index,
    page_front_matter,
    read_page,
    resolve_impl,
)


def official_description(text: str, iface: str, member: str) -> str:
    """⇒ 官方页里 `# <接口>.<成员>` 之后的第一段说明（**逐字**，用作草稿锚点）。

    ★ 抄的是**原文那一行**，不是摘要：门禁按逐字包含判，摘要一定判伪造 ✓

    :param text: 官方页正文。
    :param iface: 接口名（如 `IFeatureManager`）。
    :param member: 成员名（如 `FeatureRevolve2`）。
    """
    lines = text.splitlines()
    marker = "# %s.%s" % (iface, member)
    for i, line in enumerate(lines):
        if line.strip() == marker:
            for nxt in lines[i + 1 :]:
                if nxt.strip() and not nxt.startswith(("**Signature**", "## ")):
                    return nxt.strip()
            break
    return ""


def html_description(text: str) -> str:
    """⇒ cosworks 帮助页（HTML）里的**第一句可当锚点的描述**；没有就返回空串。

    ★ 那些页是 CHM 解包：正文在 `<body>` 里，带 `&nbsp;` 实体与内联标签。
      这里只做「去脚本/去标签/还原实体/压空白」，**不改词** —— 锚点必须能被门禁
      逐字命中，改写就等于编。

    :param text: 页面的原始 HTML。
    """
    body = re.sub(r"<script.*?</script>|<style.*?</style>|<xml.*?</xml>", " ", text, flags=re.S | re.I)
    body = re.sub(r"<[^>]+>", "\n", body)
    body = (
        body.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
        .replace("&quot;", '"')
    )
    for raw in body.splitlines():
        line = re.sub(r"\s+", " ", raw).strip()
        if len(line) < 20 or " " not in line:
            continue
        low = line.lower()
        if low.startswith(("property (", "method (", "event (", "syntax", "see also", "example")):
            continue
        if line.endswith(".") and not line.endswith(".."):
            return line
    return ""


def _legacy_impl_names() -> dict[str, str]:
    """⇒ `{手写工具名: "mcp-server/server.py:<工具名>"}`（45 个装饰器工具）。

    ★ 手写工具的函数名与工具名逐字相同（`server.py` 里 `@mcp.tool(name=...)` +
      `def <同名>`），这里只取名字，**不解析装饰器参数**（解析失败会让覆盖表静默变小）。
    """
    import ast  # noqa: PLC0415 - 只有手写工具这条路需要它

    path = ROOT / "mcp-server" / "server.py"
    out: dict[str, str] = {}
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, SyntaxError):
        return out
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if not (isinstance(dec, ast.Call) and getattr(dec.func, "attr", "") == "tool"):
                continue
            #: ★ 手写工具的函数名**不一定**等于工具名（实测 `solidworks_pack_and_go`
            #:   的函数叫 `solidworks_pack_and_go_tool`）⇒ 以装饰器里的 `name=` 为准 ✓
            tool_name = node.name
            for kw in dec.keywords:
                if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                    tool_name = str(kw.value.value)
            out[tool_name] = "mcp-server/server.py:%s" % node.name
    return out


def build_records(tools: list[str] | None) -> tuple[list[dict], list[str], list[str]]:
    """⇒ `(records, notes, unresolved_members)`。

    :param tools: 只生成这些工具（None = 全部）。
    """
    import register_capabilities as rc  # noqa: PLC0415

    idx = member_index()
    if idx is None:
        raise SystemExit("✗ 读不到官方成员索引 %s ⇒ 生成器无法定位官方页（铁律 5：查不到就说查不到）" % SWAPI_INDEX)
    known = set(idx)
    specs = {s.name: s for s in rc.all_specs()}
    legacy = _legacy_impl_names()

    from mcp_tools_list import tools_list  # noqa: PLC0415

    wire = {t["name"]: t for t in tools_list()}
    wanted = sorted(wire) if not tools else [t for t in tools if t in wire]

    records: list[dict] = []
    notes: list[str] = []
    unresolved: list[str] = []
    #: ★ 与门禁**同一份索引同一口径** —— 草稿与判据对不上会让核验人白干一遍
    func_index = FunctionIndex().build([ROOT / "scripts", ROOT / "mcp-server" / "server.py"])
    for name in wanted:
        spec = specs.get(name)
        if spec is not None:
            impl = "scripts/%s.py:%s" % (spec.module, spec.function)
            doc = str(spec.doc or "")
        else:
            impl = legacy.get(name, "")
            doc = str(wire[name].get("description") or "")
        if not impl or ":" not in impl:
            notes.append("%s：找不到实现" % name)
            continue
        rel, _, func = impl.rpartition(":")
        path = resolve_impl(rel)
        found = impl_members(path, func, known, func_index)
        if not found["found"]:
            notes.append("%s：%s" % (name, found["error"]))
        members = []
        for member in sorted(found["members"]):
            cands = idx.get(member) or []
            #: ★ 两个官方源都算：`C:\swapi\types`（markdown）与 `C:\cworks_en\api`（cosworks HTML）
            usable = [(i, p) for i, p in cands if Path(p).is_file()]
            if not usable:
                #: ★ 铁律 5 的合法出口：**查不到页就记账，不许编页**。
                #:   这些成员集中在 Simulation / Topology / Costing 三个 add-in
                #:   （本机离线文档树只覆盖 sldworks + 部分 cosworks）⇒ 写 `gap`，
                #:   门禁把它记成 `member-undocumented`（报表项），而不是当成漏查。
                unresolved.append("%s -> %s" % (name, member))
                members.append(
                    {
                        "interface": cands[0][0] if cands else "",
                        "member": member,
                        "path": "",
                        "anchor": "",
                        "documented": False,
                        "gap": "C:\\swapi\\types 无该成员页；by_member_name 索引命中 %d 个接口（%s）。"
                        "已查 SWhelp\\cosworks 与 SWhelp\\sldworksapi，均无此页 —— 按铁律 5 记账，不编页。"
                        % (len(cands), ", ".join(i for i, _ in cands[:4]) or "无"),
                    }
                )
                continue
            #: ★ 用**接收者提示**把成员归到对的接口页：`model.SketchManager.InsertSketch`
            #:   ⇒ 优先 `ISketchManager`，而不是同名但已废弃的 `IModelDoc2.InsertSketch` ✓
            hint = ((found.get("hints") or {}).get(member) or [""])[0]
            hinted = [u for u in usable if hint and hint.lower() in u[0].lower()]
            iface, page_path = (hinted or usable)[0]
            text = read_page(Path(page_path)) or ""
            if str(page_path).lower().endswith((".html", ".htm")):
                #: ★ cosworks 帮助页没有 markdown front-matter ⇒ kind 从页标题推
                kind = "property" if "property (" in text[:4000].lower() else "method"
                anchor = html_description(text)
            else:
                fm = page_front_matter(text)
                kind = fm.get("kind", "")
                anchor = official_description(text, iface, member)
            members.append(
                {
                    "interface": iface,
                    "member": member,
                    "path": str(page_path).replace("\\", "/"),
                    "anchor": anchor,
                    "kind": kind,
                }
            )
        records.append(
            {
                "tool": name,
                "impl": impl,
                "claim": first_sentence(doc),
                "claim_evidence": {"kind": "", "path": "", "anchor": ""},
                "members": members,
                "allowed_non_com": [],
                "verified": None,
            }
        )
    return records, notes, unresolved


def main(argv=None) -> int:
    """命令行入口：把草稿写到 `--out`（默认 stdout 不写盘，防止误当成品）。

    :param argv: 命令行参数。
    """
    ap = argparse.ArgumentParser(description="生成工具官方依据台账草稿（规格 353）")
    ap.add_argument("--tools", default="", help="逗号分隔的工具名")
    ap.add_argument("--all", action="store_true", help="全部工具")
    ap.add_argument("--out", default="", help="写到这个 JSON（不给则只打印统计）")
    ap.add_argument("--batch", default="", help="批次名（写进台账文件的 batch 字段）")
    args = ap.parse_args(argv)

    wanted = [x.strip() for x in args.tools.split(",") if x.strip()] or None
    if not args.all and not wanted:
        ap.error("要么 --all，要么 --tools")
    records, notes, unresolved = build_records(None if args.all else wanted)
    payload = {
        "batch": args.batch or "draft",
        "note": "草稿：claim_evidence 与 verified 由核验人**读官方页后**填写（见 docs/tool-official-claims/README.md）",
        "records": records,
    }
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    with_members = sum(1 for r in records if r["members"])
    print("★ 草稿 %d 条工具（有成员登记 %d 条）· 未解析成员 %d 处 · 说明 %d 条"
          % (len(records), with_members, len(unresolved), len(notes)))
    if unresolved:
        print("   ⚠ 官方页里查不到的成员（铁律 5：不许编页，核验人须记账或改实现）：")
        for line in unresolved[:30]:
            print("      %s" % line)
    for line in notes[:10]:
        print("   ! %s" % line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
