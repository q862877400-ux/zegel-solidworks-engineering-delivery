"""★ 官方源缺陷门禁的契约测试（★ 含负例 —— 事实 62）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tests/test_official_source_defects_gate.py
# 定位:   规格 206 / T3-3 的验收：门禁能挑出「引用了不存在的官方页」，且**判据的否定面**成立。
# 依据:   `scripts/check_official_source_defects.py` · `docs/known-facts.md` 事实 516（判据过宽）
#         与 517 定则二（判据要写「不算什么」）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import check_official_source_defects as G                          # noqa: E402


def test_local_name_sets_are_nonempty():
    """★ 判据依赖本机真名集合；它空掉时门禁会「静默全通过」⇒ 必须先证明非空。"""
    ifaces, members, enums = G._real()
    assert len(ifaces) > 100, "接口目录集合太小: %d" % len(ifaces)
    assert len(members) > 100, "成员表太小: %d" % len(members)


def test_negative_fabricated_missing_interface_is_detected(tmp_path, monkeypatch):
    """★★ 负例 1：构造一段引用**故意不存在**的接口的源码 ⇒ 门禁必须报出来。

    ★ 这是「门禁是否真的在工作」的唯一证明（事实 62）。
    """
    d = tmp_path / "scripts"
    d.mkdir()
    (d / "fake.py").write_text('# 来源: [[ZZZNoSuchInterface::SomeMember]]\n', encoding="utf-8")
    monkeypatch.setattr(G, "ROOT", tmp_path)
    monkeypatch.setattr(G, "SCAN_DIRS", ("scripts",))
    hits = G.scan()
    assert any("ZZZNoSuchInterface" in h[2] for h in hits), hits


def test_negative_existing_page_is_not_reported(tmp_path, monkeypatch):
    """★★ 负例 2（反向）：引用一个**确实存在**的官方接口 ⇒ 门禁**不该**报（否则是永久失败）。"""
    ifaces, _m, _e = G._real()
    if not ifaces:
        return
    real = sorted(ifaces)[0]
    d = tmp_path / "scripts"
    d.mkdir()
    (d / "ok.py").write_text('# 来源: C:\\swapi\\types\\%s\\x.md\n' % real, encoding="utf-8")
    monkeypatch.setattr(G, "ROOT", tmp_path)
    monkeypatch.setattr(G, "SCAN_DIRS", ("scripts",))
    hits = [h for h in G.scan() if h[0].endswith("ok.py")]
    assert not hits, hits


def test_gate_is_report_only_for_now():
    """★ 记录本批的**限度**：门禁暂只报告（★ 接进 release_check 的前置写在输出里）。

    ★★ 这条测试是**有意的**：它把「还没接闸」这件事写死，防止后人误以为已拦。
    """
    src = (ROOT / "scripts" / "check_official_source_defects.py").read_text(encoding="utf-8")
    assert "暂只报告、不拦（exit 0）" in src
