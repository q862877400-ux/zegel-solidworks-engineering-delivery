"""按批把「官方依据台账草稿」落成**台账记录**（自动核验档），并挑出需要人读的条目。

它做什么（机器能证明的那一半）：
  1. 把 543 个工具按域切成 8 批（B1…B8），**每批一个文件、写者不相交**；
  2. 每条记录填 `claim` = 工具 `doc` 首句（逐字）、`members[]` = 实现里实际调用的成员
     + **官方页原文锚点**（草稿里已经是逐字抄的）；
  3. `claim_evidence`：有官方成员 ⇒ 取与首句**词干重叠最多**的那条官方描述；
     无官方成员（编排/门面工具）⇒ 取实现文件里的函数定义行（`kind: impl`）；
  4. `verified.level = "auto"` —— **明确标注这是机器核的**，不是人读的；
     `scripts/check_tool_official_claims.py --report` 会把「人工 / 自动」分开报。
  5. **过不了语义门槛的不落地**：首句与任一成员官方描述**零词干重叠**、或成员锚点为空
     ⇒ 进 `output/claims-needs-review.json`，工具保持 `no-record`（真缺口，不许蒙混）。

★ 为什么要有「自动档」而不是直接写 `verified`：
  门禁只能证明**引用真实**（页对、锚点真、覆盖全）。语义那一关是人的判断，
  机器代劳时必须**留痕**（`level: auto` + `notes` 写清比对方式），否则就是假绿。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 353 P2 的批次落地器）
# 文件:   `scripts/check_tool_official_claims.py`（判据与成员提取，复用不重写）
#         `tools/gen_tool_official_claims.py`（草稿；`_draft-all.json`）
#         `docs/tool-official-claims/README.md`（台账格式）
#         `specs/353-mcp-tool-official-audit/spec.md` §六（批次划分与收工判据）
# 定位:   ★ 业主 2026-11-01：「一批一批来」「全自动进行」⇒ 机器先把它能证明的做完，
#         把需要读页才能判断的条目**显式留在待核清单里**，不假装核过。
# 官方依据: 官方页 Description 段（`C:\\swapi\\types\\<接口>\\<成员>.md`）——
#         锚点由 `gen_tool_official_claims.official_description()` 逐字抄取自该段
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件；**不连 SolidWorks**
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "mcp-server"))
sys.path.insert(0, str(ROOT / "tools"))

from check_tool_official_claims import (  # noqa: E402 - 判据只有一处实现
    LEDGER_DIR,
    first_sentence,
    resolve_impl,
)

DRAFT = LEDGER_DIR / "_draft-all.json"
REVIEW = ROOT / "output" / "claims-needs-review.json"

#: 停用词（只用于「词干重叠」这条**保守**门槛：宁可多送人核，不可放过假的）
STOP = frozenset(
    "a an the of to in for on with and or by from is are be as at into that this it its "
    "does do not no if when then than so such via one two all any each".split()
)

#: 批次划分：**按工具名里的域词**，顺序即优先级（先命中先归批）
BATCHES: list[tuple[str, tuple[str, ...]]] = [
    ("B1", ("solidworks_extrude_", "solidworks_revolve_", "solidworks_hole_", "solidworks_chamfer",
            "solidworks_fillet", "solidworks_pattern", "solidworks_mirror", "solidworks_rib",
            "solidworks_dome", "solidworks_sweep", "solidworks_loft", "solidworks_scale_feature")),
    ("B2", ("solidworks_sketch_", "solidworks_add_sketch_relation", "solidworks_delete_sketch",
            "solidworks_count_sketch", "solidworks_sketch")),
    ("B3", ("solidworks_assembly_", "solidworks_add_component", "solidworks_add_mate",
            "solidworks_add_coincident", "solidworks_add_concentric", "solidworks_add_distance",
            "solidworks_add_parallel", "solidworks_add_angle", "solidworks_add_tangent",
            "solidworks_add_perpendicular", "solidworks_add_lock", "solidworks_unsuppress_component",
            "solidworks_edit_component")),
    ("B4", ("solidworks_drawing_", "solidworks_insert_balloon", "solidworks_insert_center",
            "solidworks_insert_hole_table", "solidworks_insert_datum", "solidworks_insert_surface")),
    ("B5", ("solidworks_sheet_metal_", "solidworks_weldment_", "solidworks_weld_",
            "solidworks_mold_", "solidworks_surface_")),
    ("B6", ("solidworks_simulation_", "solidworks_topology_", "solidworks_costing_",
            "solidworks_mesh_", "solidworks_feasibility")),
    ("B7", ("solidworks_export_", "solidworks_view_", "solidworks_mass_", "solidworks_custom_property_",
            "solidworks_document_", "solidworks_file_", "solidworks_feature_readback",
            "solidworks_read", "solidworks_get_", "solidworks_configuration")),
]


def batch_of(tool: str) -> str:
    """⇒ 该工具属于哪一批（`B1`…`B8`；默认 `B8` 编排/门面）。

    :param tool: 工具名。
    """
    for name, prefixes in BATCHES:
        if any(tool.startswith(p) for p in prefixes):
            return name
    return "B8"


def stem(word: str) -> str:
    """⇒ 粗糙词干（只用于重叠门槛：`-ing/-ed/-es/-s` 三个后缀，够用且不会放过太多）。

    :param word: 单个英文词。
    """
    w = word.lower().strip(".,;:()[]`'\"*")
    for suf in ("ing", "ed", "es", "s"):
        if len(w) > len(suf) + 3 and w.endswith(suf):
            return w[: -len(suf)]
    return w


def stems(text: str) -> set[str]:
    """⇒ 文本里的实词词干集合（去停用词与短词）。

    :param text: 任意英文文本。
    """
    return {
        stem(w)
        for w in re.findall(r"[A-Za-z][A-Za-z_-]+", str(text or ""))
        if len(w) > 2 and w.lower() not in STOP
    }


def pick_primary(claim: str, members: list[dict]) -> tuple[dict | None, list[str]]:
    """⇒ `(与首句最贴的成员, 共同词干)`：重叠为 0 时返回 `(None, [])`。

    :param claim: 工具 `doc` 首句。
    :param members: 草稿里的成员登记。
    """
    want = stems(claim)
    best: tuple[dict | None, list[str]] = (None, [])
    for m in members:
        shared = want & stems(m.get("anchor", ""))
        if len(shared) > len(best[1]):
            best = (m, sorted(shared))
    return best


def impl_evidence(rec: dict) -> tuple[dict, str] | None:
    """⇒ `(claim_evidence, note)`：以**实现文件里的函数定义行**为证据；找不到返回 None。

    ★ 用在两类工具上：① 没有 COM 成员的薄封装/编排；② 成员**全部**在离线文档树里
      查不到页（Simulation/Topology/Costing）—— 此时按铁律 5 记账，并明说证据是实现。

    :param rec: 草稿记录（至少含 `impl`）。
    """
    rel, _, func = rec["impl"].rpartition(":")
    impl_path = resolve_impl(rel)
    try:
        impl_text = impl_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    anchor = "def %s(" % func
    if anchor not in impl_text:
        return None
    ev_rel = impl_path.relative_to(ROOT).as_posix() if impl_path.is_absolute() else str(impl_path)
    return (
        {"kind": "impl", "path": ev_rel, "anchor": anchor},
        "无官方成员页可对照（已按铁律 5 记账）⇒ 以实现文件里的函数定义行为证据",
    )


def build_batch(tools: list[str], drafts: dict[str, dict]) -> tuple[dict, list[dict]]:
    """⇒ `(可落地的记录, 需人工复核的条目)`。

    :param tools: 本批工具名。
    :param drafts: 草稿记录（工具名 → 记录）。
    """
    records: list[dict] = []
    review: list[dict] = []
    for tool in tools:
        rec = drafts.get(tool)
        if rec is None:
            review.append({"tool": tool, "why": "草稿里没有（实现找不到？）"})
            continue
        members = [m for m in rec.get("members") or []]
        empty = [
            m["member"]
            for m in members
            if not str(m.get("anchor") or "").strip() and m.get("documented") is not False
        ]
        if empty:
            review.append({"tool": tool, "why": "成员锚点为空（官方页 Description 段抄不到）：%s" % ",".join(empty)})
            continue
        documented = [m for m in members if m.get("documented") is not False]
        if documented:
            primary, shared = pick_primary(rec["claim"], documented)
            if primary is None:
                review.append({"tool": tool, "why": "首句与成员官方描述零词干重叠（需要人判断它到底干什么）"})
                continue
            evidence = {"kind": "official", "path": primary["path"], "anchor": primary["anchor"]}
            note = "成员 %s.%s 的官方 Description 与首句共享词干 %s" % (
                primary["interface"], primary["member"], "/".join(shared[:4]) or "-")
        else:
            fallback = impl_evidence(rec)
            if fallback is None:
                review.append({"tool": tool, "why": "成员无官方页、实现也找不到函数定义行"})
                continue
            evidence, note = fallback
        records.append(
            {
                "tool": tool,
                "impl": rec["impl"],
                "claim": rec["claim"],
                "claim_evidence": evidence,
                "members": members,
                "allowed_non_com": [],
                "verified": {
                    "by": "auto-pipeline",
                    "at": date.today().isoformat(),
                    "method": "official-page anchor + 词干重叠门槛",
                    "level": "auto",
                    "notes": note,
                },
            }
        )
    return {"batch": "", "note": "", "records": records}, review


def main(argv=None) -> int:
    """命令行入口：`--write` 才落盘（默认只打印分配与门槛统计）。

    :param argv: 命令行参数。
    """
    ap = argparse.ArgumentParser(description="把台账草稿按批落成记录（规格 353 P2）")
    ap.add_argument("--draft", default=str(DRAFT))
    ap.add_argument("--write", action="store_true", help="真的写 docs/tool-official-claims/<批>.json")
    ap.add_argument("--batch", default="", help="只处理这一批（B1…B8）")
    args = ap.parse_args(argv)

    draft_path = Path(args.draft)
    if not draft_path.is_file():
        print("✗ 没有草稿：%s（先跑 tools/gen_tool_official_claims.py --all）" % draft_path)
        return 2
    drafts = {r["tool"]: r for r in json.loads(draft_path.read_text(encoding="utf-8"))["records"]}

    buckets: dict[str, list[str]] = {}
    for tool in sorted(drafts):
        buckets.setdefault(batch_of(tool), []).append(tool)

    all_review: list[dict] = []
    total_ok = 0
    for batch, tools in sorted(buckets.items()):
        if args.batch and batch != args.batch:
            continue
        payload, review = build_batch(tools, drafts)
        payload["batch"] = batch
        payload["note"] = (
            "自动核验档（verified.level=auto）：成员与锚点由实现提取 + 官方页原文抄取；"
            "首句须与成员官方描述有词干重叠。★ 语义仍需人复核的条目见 output/claims-needs-review.json"
        )
        total_ok += len(payload["records"])
        all_review.extend(review)
        print("  %s：可落地 %d / %d（需人工 %d）" % (batch, len(payload["records"]), len(tools), len(review)))
        if args.write:
            out = LEDGER_DIR / ("%s.json" % batch)
            out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    REVIEW.parent.mkdir(parents=True, exist_ok=True)
    REVIEW.write_text(
        json.dumps({"count": len(all_review), "items": all_review}, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8",
    )
    print("★ 合计可落地 %d 条 · 需人工 %d 条（已写 %s）" % (total_ok, len(all_review), REVIEW.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
