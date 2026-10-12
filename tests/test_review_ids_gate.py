"""★ 规格 315 契约测试：评审稿编号门禁（★ 含**负例自证**）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_review_ids_gate.py
# 定位:   `scripts/check_review_ids.py` 的契约测试。
#           ★★ 触发它的是 2026-10-12（业主「那 60 条语料的标签给我打开」）：
#           `owner-review.md` §5「我明确不确定的 6 条」里 **6 条全引错了编号**。
# 官方依据: `corpus/l1-mainline.yaml` · `l2-longtail.yaml` · `l3-semantic.yaml`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

import check_review_ids as C                                            # noqa: E402


def test_corpus_loads_all_three_layers() -> None:
    """★ 三份语料都要读进来（★ 186 条）。"""
    cps = C.corpus()
    assert len(cps) >= 180, "★ 只读到 %d 条" % len(cps)
    assert any(k.startswith("L1-") for k in cps)
    assert any(k.startswith("L2-") for k in cps)
    assert any(k.startswith("L3-") for k in cps)


def test_corpus_handles_two_field_names() -> None:
    """★★ L1/L2 用 `task`、L3 用 `requirement` ⇒ 两种都要读得到。

    ⚠ 实测：第一版只取 `requirement` ⇒ 读到 L1 就 `KeyError`
      （★ 而「字段名不一致」看起来像「语料坏了」）。
    """
    cps = C.corpus()
    assert cps.get("L1-001"), "★ L1 的 `task` 没读到"
    assert cps.get("L3-001"), "★ L3 的 `requirement` 没读到"


def test_the_review_has_no_bad_id_references() -> None:
    """★★★ 评审稿里的编号引用**全部对得上**（★ 这是本门禁的主判据）。"""
    problems = C.check()
    assert problems == [], "★★ 评审稿里有 %d 处编号问题：\n%s" % (
        len(problems), "\n".join(problems[:5]))


def test_selftest_passes() -> None:
    """★★ 负例自证：★ 修复前的错编号**必须**被抓到。"""
    assert C.selftest() is True


#: ══ ★★ 负例（★ 事实 62：门禁「写了」不等于「有效」）══════════════════

def test_catches_the_six_wrong_ids_found_on_2026_10_12() -> None:
    """★★★ **修复前 §5 的 6 条错编号** —— 门禁**必须**每一条都报出来。

    | 稿子原写 | 实际是 | 该是 |
    |---|---|---|
    | `L1-031` | 建固定钳体 | `L1-033` 建梯形螺杆 |
    | `L2-001` | 给草图加几何关系 | `L1-050` 静力仿真 |
    | `L3-025` | 台式平口钳 | `L3-037` 鼠标外壳 |
    | `L3-031` | 给我建一个零件 | `L3-046` 梯形螺纹 |
    | `L3-050` | 安装板 + 机架 | `L3-060` 换另一种材料 |
    | `L3-060` | 换另一种材料 | `L3-053` 随便做个好看的 |
    """
    cps = C.corpus()
    before = [("L1-031", "平口钳螺杆"), ("L2-001", "仿真组"),
              ("L3-025", "鼠标外壳"), ("L3-031", "真实梯形螺纹"),
              ("L3-050", "换个材料"), ("L3-060", "随便做个好看的")]
    missed = [(q, c) for q, c in before
              if q in cps and C._matches(c, cps[q])]
    assert missed == [], "★★ 这些错编号没被抓到：%s" % missed


def test_accepts_the_corrected_ids() -> None:
    """★★ 修复**后**的正确编号 ⇒ **不该**误报（★ 防误报把门禁变成噪声）。"""
    cps = C.corpus()
    after = [("L1-033", "平口钳螺杆"), ("L1-050", "仿真组"),
             ("L3-037", "鼠标外壳"), ("L3-046", "真实梯形螺纹"),
             ("L3-060", "换个材料"), ("L3-053", "随便做个好看的")]
    bad = [(q, c) for q, c in after
           if q not in cps or not C._matches(c, cps[q])]
    assert bad == [], "★★ 正确编号被误报：%s" % bad


def test_matches_is_paraphrase_tolerant() -> None:
    """★★ 概括性描述**要放过**（★ 第一版就是因为这个误报的）。

    ⚠ 实测：用「任一段是子串」判 ⇒
      「真实梯形螺纹」vs「给零件做**真实的**梯形螺纹几何」（★ 中间插了个「的」）
      ⇒ 匹配不上 ⇒ **误报**。
      ⇒ ★ 判据改成 **2-gram 滑窗**（★ 对中间插字免疫）。
    """
    assert C._matches("真实梯形螺纹", "给零件做真实的梯形螺纹几何") is True
    assert C._matches("鼠标外壳", "给我建模一个鼠标外壳") is True
    assert C._matches("换个材料", "做一个和这个一模一样的，但用另一种材料") is True


def test_matches_rejects_a_genuinely_wrong_id() -> None:
    """★★ 真正引错（★ 描述与需求毫无共同词）⇒ **必须**报。"""
    assert C._matches("鼠标外壳", "给我设计一台台式平口钳") is False
    assert C._matches("真实梯形螺纹", "给我建一个零件") is False


def test_gate_is_registered_in_the_classification() -> None:
    """★★ 元门禁 `check_gate_wiring` 要求：★ 每个调用点都要**登记分类**。"""
    import json                                                         # noqa: PLC0415
    p = ROOT / "docs" / "gate-classification.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    runners = {e.get("runner") for e in d["classification"]}
    assert "_run_review_ids_gate" in runners, (
        "★★★ 没登记 ⇒ `check_gate_wiring` 会红")
    entry = next(e for e in d["classification"]
                 if e.get("runner") == "_run_review_ids_gate")
    for f in ("gate", "kind", "reason", "environment", "owner", "runs_in"):
        assert entry.get(f), "★ 缺字段 %s" % f
    assert entry["kind"] == "release_static"
    assert entry["runs_in"] == "release_check"


def test_gate_result_is_in_the_return_body() -> None:
    """★★ 元门禁要求：★ 门禁结果必须进 `_gate_results`（★ 静默跳过与没跑等价）。"""
    t = (ROOT / "scripts" / "release_check.py").read_text(encoding="utf-8")
    assert '"rev_ids": rev_ids' in t, (
        "★★ 结果没进返回体 ⇒ 「它跳过了/它没跑」在外面看不见")
