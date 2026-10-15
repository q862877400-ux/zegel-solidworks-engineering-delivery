"""★ EC05 判据（离线部分）—— 五项回读 / 独立参考值 / 冻结扰动集 / 缺载荷。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/engineering/part_loop.py`（★ EC05 的离线部分）
#         `specs/307-ec05-first-part-loop/spec.md`（★ 8 FR · ★ **冻结的扰动集**）
# 定位:   ★ EC05 的**离线判据**（★ 真机部分见 `acceptance/` 的 runtime 记录）。
# 官方依据: 不适用（本仓的工程闭环层）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ **纯离线** —— ★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from engineering import part_loop as P
from engineering import rules as R


# ══════════════════════════════════════════════════════════════════════
# V1 · 五项独立回读
# ══════════════════════════════════════════════════════════════════════

def test_v1_five_readback_items_are_declared():
    """★★★ V1：★ **五项必须齐**（★ 逐字承 EC05-T05：★「★ 独立回读**孔径/位置/轮廓/体数/材料**」）。"""
    assert set(P.READBACK_ITEMS) == {
        "hole_diameter", "hole_position", "outline", "body_count", "material"}, (
        "★ 五项不齐：%r" % (P.READBACK_ITEMS,))


def test_v1_missing_readback_is_unknown_not_pass():
    """★★★★★ V1：★ **缺读数 ⇒ `unknown`**（★ **绝不 `pass`**）。

    ★★ 依据（★ 承 EC00 的 `contracts/effects.md` §三 逐字）：
      ★「★★ **`readback_ok == False` ⇒ `effect_status` 必须是 `unknown`**，★ **不得 `pass`**」。
    """
    out = P.readback_verdict({"hole_diameter": 0.01}, {"hole_diameter": 0.01})
    assert out["overall"] == "unknown", (
        "★★ 缺四项读数却判了 %r ⇒ ★ 缺读数被当成通过" % out["overall"])
    assert out["releasing"] is False, "★★ `unknown` 竟然放行"


def test_v1_all_five_within_tolerance_is_pass():
    """★★ V1：★ **五项都在容差内 ⇒ `pass`**（★ 不是一律 unknown）。"""
    m = {"hole_diameter": 0.0100, "hole_position": 0.0500, "outline": 0.2000,
         "body_count": 1, "material": "Q235"}
    e = {"hole_diameter": 0.0101, "hole_position": 0.0500, "outline": 0.2002,
         "body_count": 1, "material": "Q235"}
    out = P.readback_verdict(m, e, tolerances={"hole_diameter": 0.0005,
                                               "outline": 0.001})
    assert out["overall"] == "pass", "★ 容差内却判 %r" % out
    assert out["releasing"] is True


def test_v1_out_of_tolerance_is_fail():
    """★★ V1：★ **超出容差 ⇒ `fail`**（★ 且**整体**也是 fail）。"""
    m = {"hole_diameter": 0.0200, "hole_position": 0.0500, "outline": 0.2000,
         "body_count": 1, "material": "Q235"}
    e = {"hole_diameter": 0.0100, "hole_position": 0.0500, "outline": 0.2000,
         "body_count": 1, "material": "Q235"}
    out = P.readback_verdict(m, e, tolerances={"hole_diameter": 0.0005})
    assert out["overall"] == "fail", "★ 超差却判 %r" % out
    assert out["items"]["hole_diameter"]["status"] == "fail"


def test_v1_unknown_beats_fail_in_overall():
    """★★ V1：★ **有 `unknown` ⇒ 整体 `unknown`**（★ 比 fail 更保守 —— ★ 缺证据优先）。"""
    m = {"hole_diameter": 0.0200, "hole_position": 0.0500, "outline": 0.2000,
         "body_count": 1}                      #: ★ 缺 material
    e = {"hole_diameter": 0.0100, "hole_position": 0.0500, "outline": 0.2000,
         "body_count": 1, "material": "Q235"}
    out = P.readback_verdict(m, e, tolerances={"hole_diameter": 0.0005})
    assert out["overall"] == "unknown", (
        "★★ 既有超差又缺读数时判了 %r ⇒ ★ 缺证据该优先" % out["overall"])


# ══════════════════════════════════════════════════════════════════════
# V2 · 独立参考值
# ══════════════════════════════════════════════════════════════════════

def test_v2_reference_volume_is_independent():
    """★★★ V2：★ **参考体积独立算**（★ 手写 —— ★ 不共享被测实现）。"""
    v = P.reference_plate_volume(0.200, 0.150, 0.010)
    #: ★★ **手写**独立核算
    expected = 0.200 * 0.150 * 0.010
    assert abs(v - expected) < 1e-15, "★ 参考体积不对：%r vs %r" % (v, expected)


def test_v2_reference_hole_positions_are_evenly_spaced():
    """★★ V2：★ **参考孔位等距**（★ 手写核算）。"""
    pos = P.reference_hole_positions(4, 0.030, start_x=0.0, y=0.0)
    assert len(pos) == 4
    xs = [p["x"] for p in pos]
    assert xs == [0.0, 0.030, 0.060, 0.090], "★ 孔位不对：%r" % xs
    #: ★★ 边界：0 孔 ⇒ 空表（★ 不崩）
    assert P.reference_hole_positions(0, 0.030) == []


def test_v2_reference_does_not_call_the_implementation_under_test():
    """★★★ V2：★ 参考值**不取自被测实现**（★ 用 AST 核 —— ★ 本文件不许 import COM 或 sw_*）。"""
    import ast
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8", errors="replace"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
    bad = [m for m in imported if m.startswith("sw_") or "win32com" in m]
    assert not bad, "★★ 判据 import 了被测实现/COM：%r" % bad


# ══════════════════════════════════════════════════════════════════════
# V3 · 冻结的扰动集
# ══════════════════════════════════════════════════════════════════════

def test_v3_disturbance_set_has_at_least_three():
    """★★★ V3：★ **至少三组**扰动（★ 逐字承验收）。"""
    assert len(P.DISTURBANCE_SET) >= 3, "★ 不足三组：%d" % len(P.DISTURBANCE_SET)


def test_v3_disturbance_kinds_are_all_distinct():
    """★★★★★ V3：★ **三组**类型不同****（★ 逐字承验收：「★ 至少三组**不同类型**参数扰动」）。

    ★★ 判据：★ 类型必须**互异** —— ★ 三组都是「改尺寸」**不算** ✓
    """
    cov = P.check_disturbance_coverage()
    assert cov["kinds_all_distinct"] is True, (
        "★★★ 扰动类型有重复（%r）⇒ ★ 不满足「不同类型」" % cov["kinds"])
    assert cov["ok"] is True, "★ 覆盖检查没过：%r" % cov
    #: ★★ 且类型必须是那三种**语义不同**的
    assert set(cov["unique_kinds"]) == {"dimension", "position", "relation"}, (
        "★ 三种类型不对：%r" % cov["unique_kinds"])


def test_v3_duplicate_kinds_are_rejected():
    """★★★ V3 **负例**：★ **三组同类型 ⇒ 不满足**（★ 判据要真能拒）。"""
    same = (
        P.Disturbance("A", "dimension", "改厚", "thickness"),
        P.Disturbance("B", "dimension", "改宽", "width"),
        P.Disturbance("C", "dimension", "改长", "length"),
    )
    cov = P.check_disturbance_coverage(same)
    assert cov["kinds_all_distinct"] is False, "★★ 三组同类型被判成「类型不同」"
    assert cov["ok"] is False


def test_v3_every_disturbance_states_why():
    """★★ V3：★ 每组扰动必须写**为什么选它**（★ 可复核 —— ★ 不是随手挑）。"""
    for d in P.DISTURBANCE_SET:
        assert d.why, "★ 扰动 `%s` 没写为什么" % d.id
        assert d.kind, "★ 扰动 `%s` 没写类型" % d.id


def test_v3_disturbance_set_is_frozen_in_spec():
    """★★ V3：★ **扰动集必须在 spec 里冻结**（★ 逐字承验收：「★ 具体扰动集合由 spec 冻结」）。"""
    spec = (ROOT / "specs" / "307-ec05-first-part-loop" / "spec.md").read_text(
        encoding="utf-8", errors="replace")
    assert "冻结的扰动集合" in spec, "★ spec 里没有冻结扰动集那节"
    for d in P.DISTURBANCE_SET:
        assert d.id in spec, "★ 扰动 `%s` 不在 spec 的冻结集里" % d.id


# ══════════════════════════════════════════════════════════════════════
# V4 · 缺载荷不给强度结论
# ══════════════════════════════════════════════════════════════════════

def test_v4_missing_load_case_blocks_strength():
    """★★★★★ V4：★ **缺载荷 ⇒ 不给强度结论**（★ 逐字承 EC05-T01）。"""
    out = P.load_case_allows_strength([])
    assert out["may_give_strength_conclusion"] is False, (
        "★★★ 缺载荷却允许给强度结论 ⇒ ★ 违反 EC05-T01")
    assert "缺载荷" in out["reason"], "★ 原因没写明"


def test_v4_missing_flagged_load_case_also_blocks():
    """★★ V4：★ **标了 `is_missing` 的工况**不算可用。"""
    import engineering_contract as ec
    lc = ec.LoadCase("工况A", "static", magnitude=None, is_missing=True)
    out = P.load_case_allows_strength([lc])
    assert out["may_give_strength_conclusion"] is False


def test_v4_real_load_case_allows_strength():
    """★★ V4 负例：★ **有真载荷 ⇒ 允许**（★ 不是一律拒）。"""
    import engineering_contract as ec
    lc = ec.LoadCase("工况A", "static",
                     magnitude=ec.normalize_quantity(ec.Quantity(100.0, "N", "force")))
    out = P.load_case_allows_strength([lc])
    assert out["may_give_strength_conclusion"] is True
    assert out["usable_load_cases"] == ["工况A"]


# ══════════════════════════════════════════════════════════════════════
# V5 · 绑同一版本 + 失败点不删
# ══════════════════════════════════════════════════════════════════════

def test_v5_all_items_must_share_one_version():
    """★★★★ V5：★ **所有通过项绑同一模型版本**（★ 逐字承验收）。"""
    from engineering import jobs as J
    b = J.VersionBinding("c1", "p1", "m1")
    ok = P.PartLoopResult(binding=b, baseline={"binding": b},
                          disturbances=[{"binding": b}, {"binding": b}])
    assert ok.all_items_share_one_version() is True
    #: ★★★ **有一个不同版本 ⇒ 整体不成立**
    other = J.VersionBinding("c1", "p1", "m2")
    bad = P.PartLoopResult(binding=b, baseline={"binding": b},
                           disturbances=[{"binding": b}, {"binding": other}])
    assert bad.all_items_share_one_version() is False, (
        "★★★ 有项绑了**不同模型版本**却判成「同一版本」⇒ ★ 违反验收")


def test_v5_failures_are_kept_not_deleted():
    """★★★★ V5：★ **失败点不许删**（★ 逐字承验收：「★ **不在验收时删掉失败点**」）。"""
    r = P.PartLoopResult(binding=object(), failures=["P2 孔距超差"])
    out = r.keep_failures()
    assert out["count"] == 1, "★ 失败点被丢了"
    assert out["deleted"] is False, "★★ 失败点被删了"
    assert "P2 孔距超差" in out["failures"], "★ 失败点内容变了"


# ══════════════════════════════════════════════════════════════════════
# V6 · 与 EC02 的接线（★ 制造可达性）
# ══════════════════════════════════════════════════════════════════════

def test_v6_reuses_ec02_hole_margin_rule():
    """★★★ V6：★ **制造工具可达性复用 EC02 的规则**（★ 铁律 1 —— ★ 不另建一套）。"""
    out = R.hole_edge_margin(hole_d=0.010, hole_x=0.050, part_half_width=0.100)
    assert out["ok"] is True
    assert "tool_accessible" in out, "★ EC02 的孔边距没给可达性读数"
    #: ★★ 本判据**就是**「EC05 复用了 EC02」的证据（★ 不是重复实现）
    assert R.hole_edge_margin(hole_d=0.010, hole_x=0.0995,
                              part_half_width=0.100)["tool_accessible"] is False, (
        "★ 边距不足时却说工具可达")
