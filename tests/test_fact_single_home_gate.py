"""★ 契约测试：`fact-single-home` 告警门禁（★ 含负例 —— 事实 62）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tests/test_fact_single_home_gate.py
# 定位:   规格 206 / **T5-1** 的验收：门禁能挑出「别的文档逐字复述事实正文」，且**判据的否定面**成立。
# 依据:   `scripts/check_fact_single_home.py` · 事实 538/539（两处写同一个数就会漂）·
#         事实 62（负例是门禁有效的唯一证明）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import check_fact_single_home as G                                  # noqa: E402


def test_home_and_body_extraction_are_nonempty():
    """★ 守卫：家里抽不出正文时门禁会「静默全通过」⇒ 必须先证明抽取非空。"""
    bodies = G.fact_bodies()
    assert len(bodies) > 100, "抽到的事实正文太少: %d" % len(bodies)
    assert all(len(b) >= G.MIN_LEN for _n, b in bodies)


def test_norm_ignores_markup_and_whitespace():
    """★ 判据的归一：强调符与空白差异**不该**影响「逐字」判定。"""
    assert G._norm("**甲方** 乙方") == G._norm("甲方乙方")
    assert G._norm("a\n  b") == G._norm("a b")


def test_negative_verbatim_copy_is_detected(monkeypatch, tmp_path):
    """★★ 负例：在「别的文档」里**逐字**抄一段事实正文 ⇒ 门禁**必须**报出来。

    ★ 这是「门禁是否真在工作」的唯一证明（事实 62）✓
    """
    body = "★" * 5 + "这是一个足够长的事实正文 " * 8          #: ★ 造一段 ≥80 字符的正文
    monkeypatch.setattr(G, "fact_bodies", lambda: [("999", body)])
    d = tmp_path / "docs"
    d.mkdir()
    (d / "other.md").write_text("# 别的文档\n\n" + body + "\n", encoding="utf-8")
    monkeypatch.setattr(G, "ROOT", tmp_path)
    hits = G.offenders()
    assert any(h[1] == "999" for h in hits), hits


def test_negative_citation_is_not_reported(monkeypatch, tmp_path):
    """★★ 反向负例：**只引用编号**（不抄正文）⇒ **不该**报 —— 否则正确写法会被惩罚。"""
    body = "★" * 5 + "另一个足够长的事实正文 " * 8
    monkeypatch.setattr(G, "fact_bodies", lambda: [("998", body)])
    d = tmp_path / "docs"
    d.mkdir()
    (d / "other.md").write_text("# 别的文档\n\n★ 见事实 **998**（家 = known-facts.md）\n",
                                encoding="utf-8")
    monkeypatch.setattr(G, "ROOT", tmp_path)
    assert not G.offenders(), "只引用编号被误报了"


def test_gate_is_warning_level_for_now():
    """★ 记录本批的**限度**：门禁为**告警级**（exit 0），★ 按 D-1 未达标前不接硬门禁。

    ★★ 这条测试是**有意的**：防止后人以为它已在拦。
    """
    src = (ROOT / "scripts" / "check_fact_single_home.py").read_text(encoding="utf-8")
    assert "告警级" in src and "return 0" in src
