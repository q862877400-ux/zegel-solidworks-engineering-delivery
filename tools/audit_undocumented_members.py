"""把台账里「查不到官方页」的成员**再查一遍全部离线源**，并把结论写回 `gap`。

为什么要有它（规格 353 · 业主 2026-11-01：「没查到的那些进一步查询」）：
  台账里有 `documented:false` 的成员。它们**不是**一句「查不到」就完事 ——
  必须给出「查过哪几棵源、每棵树的结果形态」：① 有描述页（可升级成正式证据）；
  ② 只有签名页（没有散文说明，不能当语义锚点）；③ 全树未命中。
  ⇒ 本工具扫 `check_tool_official_claims.HTML_DOC_ROOTS` + `C:\\swapi` 的全部成员页，
     能升级的升级，升不了的把**逐源结论**写进 `gap`。

用法：
  ```bash
  python -B tools/audit_undocumented_members.py            # 只报表
  python -B tools/audit_undocumented_members.py --write    # 写回 docs/tool-official-claims/B*.json
  ```

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 353 P2d：把「查不到」变成「逐源查过的结论」）
# 文件:   `scripts/check_tool_official_claims.py`（成员索引与页面读取，复用不重写）
#         `docs/tool-official-claims/B*.json`（批次台账）
#         `specs/353-mcp-tool-official-audit/spec.md` §二（判据）与 §六（批次）
# 定位:   ★ 铁律 5 的落地：查不到要写清"查到哪一步"，而不是一句"没有"。
# 官方依据: 各离线帮助树的成员页（`C:\\swapi\\types\\*.md` · `C:\\cworks_en\\api\\*.html` ·
#           `AI Solidworks\\官方文档\\SWhelp\\**\\*.html` · `C:\\cworks_vb6` · `C:\\cworks_manual`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件；**不连 SolidWorks**
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
LEDGER = ROOT / "docs" / "tool-official-claims"
sys.path.insert(0, str(ROOT / "scripts"))

sys.path.insert(0, str(ROOT / "tools"))
from gen_tool_official_claims import official_description  # noqa: E402 - 首句口径只有一处

from check_tool_official_claims import (  # noqa: E402 - 索引与读页只有一处实现
    HTML_DOC_ROOTS,
    SWAPI_TYPES,
    html_member_index,
    member_index,
    page_front_matter,
    read_page,
)


def html_description(text: str) -> str:
    """⇒ HTML 帮助页里第一句可当锚点的描述；没有（只有签名/语言过滤行）返回空串。

    :param text: `read_page()` 已剥过标签的页面文本。
    """
    for raw in text.splitlines():
        line = " ".join(raw.split())
        if len(line) < 20 or " " not in line:
            continue
        low = line.lower()
        if low.startswith(("property (", "method (", "event (", "syntax", "see also", "example",
                            "language filter", "solidworks.interop", ":")):
            continue
        if line.endswith(".") and not line.endswith(".."):
            return line
    return ""


def probe(member: str, want_iface: str, idx: dict) -> tuple[str, dict | None, list[str]]:
    """⇒ `(结论, 可升级的证据, 只找到签名的页)`。

    结论取值：`description`（有描述页，可升级）/ `signature-only`（只有签名页）/ `none`。

    :param member: 成员名。
    :param want_iface: 台账里登记的接口（用来在多个同名页里挑对的那个）。
    :param idx: `member_index()` 的返回。
    """
    override = PROJECT_FACT_OVERRIDES.get(member)
    if override and override[0].lower() != (want_iface or "").lower():
        want_iface = override[0]
    cands = idx.get(member) or []
    same = [c for c in cands if want_iface and c[0].lower() == want_iface.lower()]
    distinct = {c[0].lower() for c in cands}
    if same:
        cands = same
    elif len(distinct) == 1:
        #: ★ 登记接口错了、但**这个成员只属于一个接口** ⇒ 可以改名归位
        #:   （实测：`GetPartingLinesCount` 登记成 `IFeatureManager`，真身在
        #:   `IDraftFeatureData2` —— 这类纠正是可判的，不算猜）✓
        cands = list(cands)
    else:
        #: ★★ **不跨接口兜底**：`Name` / `Count` / `GetName` 这种名字在十几个接口上都有页，
        #:   按名字取第一个会把「Costing 实体名」升级成 `IBody2.Name`（语义完全不是一回事）⇒ 不猜 ✓
        cands = []
    sig_only: list[str] = []
    for iface, path in cands:
        text = read_page(Path(path))
        if text is None:
            continue
        if path.lower().endswith((".md",)):
            anchor = official_description(text, iface, member)
        else:
            anchor = html_description(text)
        if anchor:
            return "description", {"interface": iface, "member": member, "path": path.replace("\\", "/"),
                                   "anchor": anchor, "documented": True}, sig_only
        sig_only.append("%s（%s）" % (path, iface))
    return ("signature-only" if sig_only else "none"), None, sig_only


REFLECT_DIRS = (ROOT / "_raw" / "reflect", ROOT / "_raw" / "reflect_sldworks", ROOT / "_raw" / "topo-reflect")

#: ★★ **本仓已经查证过的归属**（先查项目文件这一步的产物）。
#:   来源不是印象，是 `docs/known-facts.md` 的事实条目 —— 逐条带出处，
#:   只在「台账登记的接口与这里不一致」时用来**纠错**，不用来猜新成员。
PROJECT_FACT_OVERRIDES: dict[str, tuple[str, str]] = {
    # 事实 112：真机 `IFeatureManager.GetPartingLinesCount` 等全 AttributeError；
    #   反射/swapi 给出的真实宿主如下（从 FeatureManager/model 上读永远是 None）。
    "GetPartingLinesCount": ("IPartingLineFeatureData", "known-facts 112"),
    "GetPartingSurfacesCount": ("IToolingSplitFeatureData", "known-facts 112"),
    "GetCavitySurfacesCount": ("IToolingSplitFeatureData", "known-facts 112"),
    "GetCoreSurfacesCount": ("IToolingSplitFeatureData", "known-facts 112"),
    "PartingType": ("IPartingSurfaceFeatureData", "known-facts 112"),
    "CoreCavitySplit": ("IPartingLineFeatureData", "known-facts 112"),
    # 事实 897 附近：`GetModelDoc` 的宿主是 `IView`（曾作为"假命中"的例子记下来）
    "GetModelDoc": ("IView", "known-facts 895"),
    # 视图变换矩阵在 `IModelView`（`docs/family-coverage.md` 的 `IModelView.Xform`）
    "Xform": ("IModelView", "family-coverage / IModelView.Xform"),
}


def reflection_evidence(member: str, want_iface: str = "") -> str:
    """⇒ 出厂类型库转储里该成员的签名行（`文件:行号: 原文`）；没有返回空串。

    ★ 这是「签名可得、语义不可得」的最后一级证据：反射是**冲突裁决者**（铁律 4），
      但它只给类型，不给 Remarks —— 所以它进 `gap`，不进 `anchor`。

    :param member: 成员名。
    """
    for root in REFLECT_DIRS:
        if not root.is_dir():
            continue
        for path in root.glob("iface_*.txt"):
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            #: ★ **必须词边界精确匹配**：`member in line` 会把 `Name` 匹配到
            #:   `get_FixtureNameInSelectedExcitation()`、把 `Xform` 匹配到 `ISetXform()`
            #:   —— 那就成了"编证据"（实测踩过）。COM 访问器要认 `get_/set_/put_` 前缀，
            #:   且前后都不能再接单词字符 ✓
            pattern = re.compile(r"(?<![A-Za-z0-9_])(?:get_|set_|put_)?%s(?![A-Za-z0-9_])" % re.escape(member))
            #: ★ 反射转储按 `## <接口>` 分段；**只认登记接口那一段**——
            #:   否则 `ISketch.Name` 会拿到 `iface_cosworks.txt` 里 CWStudy 的 `get_Name()`
            #:   （名字撞车，不是同一个成员）✓
            section = ""
            hits: dict[str, str] = {}
            for i, line in enumerate(text.splitlines(), 1):
                if line.startswith("## "):
                    section = line[3:].strip()
                    continue
                if not pattern.search(line) or "(" not in line:
                    continue
                hits.setdefault(section, "%s:%d: %s" % (path.name, i, line.strip()[:120]))
            if want_iface:
                for sec, hit in hits.items():
                    if sec.lower() == want_iface.lower():
                        return hit
            elif len(hits) == 1:
                #: 没登记接口时，只有「全文件只在一个接口段里出现」才敢引 —— 否则是撞名 ✓
                return next(iter(hits.values()))
    return ""


def gap_text(member: str, want_iface: str, verdict: str, sig_only: list[str]) -> str:
    """⇒ 写进台账的 `gap`：查过哪些根、每棵树的结论形态。

    ★ 这是铁律 5 的**可复核形态**：下一个人不必重查一遍同一堵墙。

    :param member: 成员名。
    :param want_iface: 台账登记的接口。
    :param verdict: `probe()` 的结论。
    :param sig_only: 只找到签名的页。
    """
    roots = ["C:\\swapi\\types"] + [str(r) for r in HTML_DOC_ROOTS]
    head = "%s 在 %s 上无描述页" % (member, want_iface or "（未登记接口）")
    if member in PROJECT_FACT_OVERRIDES:
        head += "；本仓已查证真实宿主为 %s（%s）" % PROJECT_FACT_OVERRIDES[member]
    if verdict == "signature-only":
        tail = "；只有签名页、无散文说明：" + "；".join(sig_only[:3])
    else:
        tail = "；全部 %d 棵离线源未命中成员页" % len(roots)
    reflected = reflection_evidence(member, want_iface)
    if reflected:
        tail += "；出厂类型库有签名（无描述）：" + reflected
    return "%s%s。已查：%s。" % (head, tail, " · ".join(roots))


def main(argv=None) -> int:
    """命令行入口：`--write` 才把结论写回台账。

    :param argv: 命令行参数。
    """
    ap = argparse.ArgumentParser(description="再查台账里所有「未登记官方页」的成员（规格 353 P2d）")
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    idx = member_index() or {}
    stats = {"description": 0, "signature-only": 0, "none": 0}
    upgraded: list[str] = []
    written = 0
    for batch in sorted(LEDGER.glob("B*.json")):
        data = json.loads(batch.read_text(encoding="utf-8"))
        changed = False
        for rec in data.get("records") or []:
            for m in rec.get("members") or []:
                if m.get("documented") is not False:
                    continue
                verdict, evidence, sig_only = probe(m["member"], str(m.get("interface") or ""), idx)
                stats[verdict] += 1
                if evidence:
                    m.clear()
                    m.update(evidence)
                    m["resolved_by"] = "audit-undocumented"
                    upgraded.append("%s -> %s.%s" % (rec["tool"], evidence["interface"], evidence["member"]))
                else:
                    m["gap"] = gap_text(m["member"], str(m.get("interface") or ""), verdict, sig_only)
                changed = True
        if changed:
            written += 1
            if args.write:
                batch.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("★ 未登记成员复核：有描述页可升级 **%d** · 只有签名页 **%d** · 全树未命中 **%d**（台账文件 %d 个）"
          % (stats["description"], stats["signature-only"], stats["none"], written))
    for line in upgraded[:20]:
        print("   ↑ %s" % line)
    if upgraded and not args.write:
        print("   （加 --write 才会写回台账）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
