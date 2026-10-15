"""★ EC00 T026 补测判据 —— **实体几何**的保存重开持久性（★ 真机读数落盘）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `output/_probe_ec00_solid_persistence.json`（★ 真机读数）
#         `output/_probe_ec00_extrude_official.json`（★ 真因：★ 拉伸前必须选中草图）
# 定位:   ★ 补 **EC00 T026** 的**实体几何**部分。★★★ **判据**：★ 保存重开后
#         **体数一致** + **体积一致** + **特征数一致**（★ 三重 —— ★ 与草图几何那版同族）。
# 官方依据: `FeatureExtrusion3`（★ `D1` = meters）· `IPartDoc::GetBodies2`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 不连 COM · ★ 只读落盘读数）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "specs" / "302-ec00-trustworthy-tool-base"
PROBE = ROOT / "output" / "_probe_ec00_solid_persistence.json"
EXT_PROBE = ROOT / "output" / "_probe_ec00_extrude_official.json"


def _probe() -> dict:
    assert PROBE.is_file(), "★ 缺真机读数 `output/_probe_ec00_solid_persistence.json`"
    return json.loads(PROBE.read_text(encoding="utf-8"))


def test_solid_was_actually_built():
    """★★★ 补测前提：★ **实体真的建成了**（★ 否则「持久性」无从谈起）。

    ★★ 依据（★ 官方 Example 的调用序 + ★ 真机两臂）：★ 拉伸前**必须选中草图**。
    """
    d = _probe()
    assert d.get("selected") is True, "★ 没选中草图"
    assert d.get("selection_count") == 1, "★ 选中数不是 1：%r" % d.get("selection_count")
    assert d.get("extrude_returned_is_none") is False, (
        "★★ 拉伸返回 None ⇒ 没建成（★ 那会让「持久性」变成空谈）")
    before = d.get("before_save", {})
    assert before.get("body_count") == 1, "★★ 保存前体数不是 1：%r" % before.get("body_count")


def test_solid_persists_across_save_reopen():
    """★★★★★ 补测核心：★ **保存重开后实体三重一致**（★ 体数 + 体积 + 特征数）。

    ★★ 依据（★ 逐字承 T026 完成判据）：★「★ **重开效果与义务一致**」。
    """
    d = _probe()
    r = d.get("reopen", {})
    assert r.get("opened") is True, "★ 重开失败"
    assert r.get("body_count_match") is True, "★★ 体数不一致"
    assert r.get("feature_count_match") is True, "★★ 特征数不一致"
    assert r.get("volume_match") is True, "★★ 体积不一致"
    assert r.get("solid_persistence_ok") is True, (
        "★★★ `solid_persistence_ok` 不是 True ⇒ ★ 实体没持久")


def test_volume_is_physically_plausible():
    """★★ 补测：★ 体积必须**物理上说得通**（★ 不是只看「一致」）。

    ★ 几何：★ 矩形 `(-25,15)` → `(27,-15)` mm = **52 × 30 mm** ⇒ ★ 拉伸 10 mm
      ⇒ ★ 体积应为 **52 × 30 × 10 = 15600 mm³ = 1.56e-05 m³** ✓
    ★★ 依据（★ `output/_probe_ec00_extrude_official.json` 臂 A 的几何）：
      ★ `sketch_corner_rectangle(model, -25.0, 15.0, 27.0, -15.0)`。
    """
    d = _probe()
    v = (d.get("before_save") or {}).get("volume_m3")
    assert v is not None, "★ 读数里没有体积"
    expected = 52.0 * 30.0 * 10.0 * 1e-9        #: ★ mm³ → m³
    assert abs(v - expected) <= expected * 1e-3, (
        "★★ 体积 %r 与几何算出的 %r 差太多 ⇒ ★ 拉伸的**深度或单位**可能不对"
        % (v, expected))


def test_artifact_was_cleaned_up():
    """★★ 补测：★ 自有工件**必须删掉**（★ 不留残留 —— ★ 业主指令「无残留收口项」）。"""
    d = _probe()
    assert d.get("artifact_removed") is True, "★ 自有工件没删"
    assert not (ROOT / "output" / "_ec00_solid_persistence.SLDPRT").is_file(), (
        "★ 自有工件仍在盘上")


def test_acceptance_doc_records_the_solid_result():
    """★★ 补测：★ 结论必须**落档**（★ 不能只在探针里）。"""
    p = SPEC / "acceptance" / "T026-runtime.md"
    assert p.is_file(), "★ 缺 `acceptance/T026-runtime.md`"
    body = p.read_text(encoding="utf-8", errors="replace")
    assert "实体" in body, "★ T026 验收里没有「实体」那节"
    assert "solid_persistence_ok" in body or "体数" in body, (
        "★ T026 验收里没记实体持久性的读数")
