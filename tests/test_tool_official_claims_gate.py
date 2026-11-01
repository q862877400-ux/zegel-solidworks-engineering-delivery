"""★ 官方依据台账门禁的契约测试 + **双侧负例**（该报的报、不该报的不报）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/check_tool_official_claims.py`（被测门禁）
#         `specs/353-mcp-tool-official-audit/spec.md` §二（判据）
# 定位:   ★ 这张表的每一行都对应一个**真实犯过的错**（业主 2026-11-01：
#         「不能根据记忆和印象」）—— 门禁的价值不是「它说有」，而是
#         **「它拒绝了我实际写错的那几句」**（`dsh-mcp-builder/references/
#         claim-verification.md` §2.4 反例自检：`killed[]` 必须全部被拒）。
# 官方依据: 官方页 front-matter 的 `type:` / `member:`（`C:\\swapi\\types\\**`）；
#         锚点逐字比对口径见门禁的 `normalize()`。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件（**不依赖 C:\\swapi**：夹具自带假官方页，逐条构造）
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "scripts" / "check_tool_official_claims.py"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


G = _load("tool_official_claims_gate_under_test", GATE)

PAGE = """---
type: IFeatureManager
member: FeatureRevolve2
kind: method
assembly: SolidWorks.Interop.sldworks
---

# IFeatureManager.FeatureRevolve2

Creates a base-, boss-, or cut-revolve feature.

**Signature**: `Feature FeatureRevolve2( System.bool SingleDir, System.bool IsSolid )`

## Parameters
- **SingleDir**: True if the revolve is in one direction, false if in two directions (see **Remarks**)
"""

IMPL = '''
def revolve_boss(model, angle):
    model.ClearSelection2(True)
    return model.FeatureManager.FeatureRevolve2(True, True, angle)
'''

DOC = "Create a revolved boss from an existing profile sketch. It writes a boss feature."

PAGE2 = """---
type: IModelDoc2
member: ClearSelection2
kind: method
---

# IModelDoc2.ClearSelection2

Clears the selection list.
"""


def _fixture(tmp_path: Path) -> tuple[dict, Path]:
    """⇒ `(合法记录, 官方页路径)`：临时目录里造一份「假官方页 + 假实现」。

    ★ 夹具自带页面而不是读 `C:\\swapi` ⇒ 本测试**可在没有官方文档树的机器上跑**。

    :param tmp_path: pytest 的临时目录。
    """
    page = tmp_path / "FeatureRevolve2.md"
    page.write_text(PAGE, encoding="utf-8")
    page2 = tmp_path / "ClearSelection2.md"
    page2.write_text(PAGE2, encoding="utf-8")
    impl = tmp_path / "impl_mod.py"
    impl.write_text(IMPL, encoding="utf-8")
    rec = {
        "tool": "solidworks_revolve_boss",
        "impl": str(impl) + ":revolve_boss",
        "claim": "Create a revolved boss from an existing profile sketch.",
        "claim_evidence": {
            "kind": "official",
            "path": str(page),
            "anchor": "Creates a base-, boss-, or cut-revolve feature.",
        },
        "members": [
            {
                "interface": "IFeatureManager",
                "member": "FeatureRevolve2",
                "path": str(page),
                "anchor": "**SingleDir**: True if the revolve is in one direction, false if in two directions",
            },
            {
                "interface": "IModelDoc2",
                "member": "ClearSelection2",
                "path": str(page2),
                "anchor": "Clears the selection list.",
            },
        ],
        "allowed_non_com": [],
        "verified": {"by": "test", "at": "2026-11-01", "method": "fixture"},
    }
    return rec, page


def _judge(rec: dict, doc: str = DOC, known: set[str] | None = None) -> list[str]:
    codes = [
        c
        for c, _ in G.judge_record(
            rec, doc, known if known is not None else {"FeatureRevolve2", "ClearSelection2"}
        )
    ]
    return codes


# ══════════════════════════════════════════════════════════════════════
# 反例自检：每条都是**真实写错过的形态**，必须全部被拒
# ══════════════════════════════════════════════════════════════════════
KILLED = [
    (
        "伪造引文：凭记忆写了一句官方页里没有的话",
        lambda r: r["claim_evidence"].update({"anchor": "Creates a revolved feature or returns None."}),
        "claim-unanchored",
    ),
    (
        "指错页：把 FeatureCut4 的说明挂到 FeatureRevolve2 的成员上",
        lambda r: r["members"][0].update({"anchor": "Creates a cut extrude feature."}),
        "anchor-not-found",
    ),
    (
        "漏查：实现里调了 ClearSelection2，台账只登记了 FeatureRevolve2",
        lambda r: r.update({"members": r["members"][:1]}),
        "member-uncited",
    ),
    (
        "台账说的 ≠ 模型看到的：claim 与 doc 首句不一致",
        lambda r: r.update({"claim": "Delete a revolved feature."}),
        "claim-mismatch",
    ),
    (
        "指错接口：页 front-matter 的 type 与登记不符",
        lambda r: r["members"][0].update({"interface": "IPartDoc"}),
        "page-mismatch",
    ),
    (
        "没核验人：只抄了页，没写谁/何时读的",
        lambda r: r.update({"verified": None}),
        "unverified",
    ),
    (
        "给了豁免却说不出理由",
        lambda r: r.update({"allowed_non_com": [{"name": "ClearSelection2", "why": ""}]}),
        "member-uncited",
    ),
]


def test_good_record_passes(tmp_path):
    """不该报的：完整、逐字、覆盖全的记录必须零违规。"""
    rec, _ = _fixture(tmp_path)
    assert _judge(rec) == []


def test_killed_counterexamples_are_rejected(tmp_path):
    """★★ 反例自检：每条真实错法都必须被门禁拒绝（否则说明对应判据失效）。"""
    for title, mutate, want in KILLED:
        rec, _ = _fixture(tmp_path)
        mutate(rec)
        codes = _judge(rec)
        assert want in codes, "%s ⇒ 期望 %s，实际 %s" % (title, want, codes)


def test_impl_missing_function(tmp_path):
    """实现函数改名/删除后，台账必须报 impl-missing（不许静默当零成员）。"""
    rec, _ = _fixture(tmp_path)
    rec["impl"] = rec["impl"].replace(":revolve_boss", ":no_such_fn")
    assert "impl-missing" in _judge(rec)


def test_official_tree_unavailable_skips_page_judgments(tmp_path):
    """官方文档树不可用时：页/锚点判据**跳过**（宁可说「没验」也不许假绿）。

    ★ 剩下的判据（claim 一致、成员覆盖、核验人）仍然照判 ——
      「没页可读」不等于「什么都别查」。
    """
    rec, _ = _fixture(tmp_path)
    rec["members"][0]["anchor"] = "这句话在页里不存在"
    codes = [c for c, _ in G.judge_record(rec, DOC, None)]
    assert "anchor-not-found" not in codes
    assert "page-mismatch" not in codes
    #: 剩下的判据照判：claim 一致、成员覆盖、核验人
    assert "claim-mismatch" not in codes
    assert "unverified" not in codes


def test_normalize_keeps_words_drops_markup():
    """归一化只去掉排版（`**`/反引号/列表符），不丢词 —— 否则「真引文」会被判伪造。"""
    page = "- **D1**: Depth of extrusion for first end **in meters**"
    assert G.normalize("D1: Depth of extrusion for first end in meters") in G.normalize(page)
    assert G.normalize("Depth of extrusion") in G.normalize(page)


def test_first_sentence_has_single_home():
    """首句口径**只有一个家**：本门禁 import 契约门禁的那一个（不许再写第二份）。

    ★ 来历：本门禁第一版自带一份逐字相同的 `first_sentence`，被仓库统一化门禁的
      「跨文件同函数体」判据当场抓到（组数 76 → 77）⇒ 改成 import，并留这条断言防复发。
    """
    other = _load("tool_contract_for_parity", ROOT / "scripts" / "check_tool_contract.py")
    #: ★ 判「它来自哪个模块」而不是对象同一性：测试用两条独立 import 链加载同一个 .py，
    #:   对象必然不同名不同体，但 `__module__` 能证明**没有第二份实现** ✓
    assert G.first_sentence.__module__ == "check_tool_contract"
    assert G.first_sentence.__name__ == other.first_sentence.__name__


def test_ledger_skips_underscore_drafts(tmp_path):
    """以 `_` 开头的草稿文件不进台账读音（机器抄的锚点不算人核过）。"""
    ledger = tmp_path / "claims"
    ledger.mkdir()
    (ledger / "_draft.json").write_text('{"records":[{"tool":"x"}]}', encoding="utf-8")
    (ledger / "batch.json").write_text('{"records":[{"tool":"y"}]}', encoding="utf-8")
    records, broken = G.load_ledger(ledger)
    assert set(records) == {"y"}
    assert broken == []


def test_normalize_does_not_eat_python_source(tmp_path):
    """★ 回归：归一化**不许**对 .py 跑 HTML 标签剥除。

    实测踩过：`re.sub(r"<[^>]+>", " ")` 对 Python 源码会把 `list[str]` 到下一个 `>`
    整段吞掉（31 KB 的 `sw_drawing_view.py` 归一化后只剩 25 KB），于是
    `def <函数名>(` 这种**实现锚点**永远判「找不到」——假红。
    """
    src = "def list_drawing_views_report(model) -> dict:\n    rows: list[str] = []\n"
    assert "def list_drawing_views_report(" in G.normalize(src)


def test_read_page_strips_html_only_for_html(tmp_path):
    """HTML 页（cosworks 帮助）读进来要剥标签/解实体；markdown 页原样返回。"""
    html = tmp_path / "ICWStudy~RunAnalysis.html"
    html.write_text("<html><body><p>Gets the results &amp; names.</p></body></html>", encoding="utf-8")
    md = tmp_path / "FeatureRevolve2.md"
    md.write_text("---\ntype: IFeatureManager\n---\n\nCreates a feature.\n", encoding="utf-8")
    assert "Gets the results & names." in (G.read_page(html) or "")
    assert "<p>" not in (G.read_page(html) or "")
    assert "type: IFeatureManager" in (G.read_page(md) or "")
