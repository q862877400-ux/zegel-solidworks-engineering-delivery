"""★ 状态指纹的契约与负例（规格 210 · B2）：读不到 ≠ 没变，且读数必须**只读**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_fingerprint.py`
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B2**。★ 评审原话：
#   ★「整套方案的**量具是指纹**，所以要**校准它**，与你们『**回读的量具要校准**』是同一个思路」✓
#   ★★ 本文件钉三件事：
#     ① ★ 九类状态**逐个能读**（拿不到 ⇒ **记 `None` + 原因**，★ 绝不假装读到）✓
#     ② ★★ **差分分三桶**：`changed` / **`unknown`（有一侧读不到 ⇒ 不知道）** / `same` ——
#        ★ 把「读不到」混进 `same` ⇒ ★ **会把盲区报成「声明一致」** ✗（本规格要防的正是这类假结论）✓
#     ③ ★ 读数**只读**：★ 连读两次、中间不做任何事 ⇒ ★ 两次必须相等 ✓
# 官方依据: 每类的官方成员写在 `sw_fingerprint.OFFICIAL` 里（★ 铁律 4：读数要能指认出处）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_fingerprint as FP                                    # noqa: E402


class _Obj:
    """★ 假 COM 对象：读法放在 `_d` 里（★ 与真机同一调用形状，但不碰 COM）✓"""

    def __init__(self, **kw):
        self._d = kw


@pytest.fixture(autouse=True)
def _patch(monkeypatch):
    """★ 把 `get_com_member` 与重建读数都换成假件 ⇒ **不连 SolidWorks** ✓"""
    def fake_get(obj, member, default=None, *a, **kw):
        table = getattr(obj, "_d", None)
        if isinstance(table, dict) and member in table:
            return table[member]
        return default
    monkeypatch.setattr(FP, "get_com_member", fake_get)
    monkeypatch.setattr(FP, "_REBUILD_READER", lambda model: (False, ""))


def _model(**over):
    """★ 一个「健康」的假模型：九类都能读到 ✓"""
    feat2 = _Obj(GetNextFeature=None)
    feat1 = _Obj(GetNextFeature=feat2)
    base = dict(
        SelectionManager=_Obj(GetSelectedObjectCount2=1),
        GetActiveSketch2=None,
        GetSaveFlag=False,
        FirstFeature=feat1,
        GetBodies2=[_Obj(GetFaceCount=6)],
        #: ★ 真机踩过：`GetDisplayStateSetting(Option)` 要吃实参、且回的是**对象** ⇒
        #:   ★ 假件也要照这个形状来（★ 读它里面的 `Names`）
        Extension=_Obj(GetDisplayStateSetting=_Obj(Names=["默认<按加工>", "另一个"])),
        GetActiveConfiguration=_Obj(Name="默认"),
    )
    base.update(over)
    return _Obj(**base)


# ── ① 九类都能读到 ────────────────────────────────────────────────────────
def test_all_nine_classes_are_read():
    fp = FP.read(_model())
    assert set(fp["readings"]) == set(FP.STATE_CLASSES)
    assert fp["missing"] == {}, fp["missing"]
    assert fp["readings"]["selection"] == 1
    assert fp["readings"]["features"] == 2
    assert fp["readings"]["bodies"] == 1
    assert fp["readings"]["faces"] == 6
    assert fp["readings"]["config"] == "默认"
    assert fp["readings"]["edit_mode"] == "none"
    #: ★ 归成**排序后的名字元组**（★ 可比、稳定）✓
    #: ★ 注意：`jsonable` 只放行标量 ⇒ ★ 元组会被**字符串化**（★ 仍是可比、稳定的）✓
    assert fp["readings"]["display"] == str(("另一个", "默认<按加工>")), \
        fp["readings"]["display"]


def test_every_class_cites_an_official_member():
    """★ 铁律 4：★ 每一类读数都要能**指认官方成员**（★ 不许凭印象）✓"""
    assert set(FP.OFFICIAL) == set(FP.STATE_CLASSES)
    assert all(v.strip() for v in FP.OFFICIAL.values())


# ── ② ★★ 读不到 ⇒ 记原因，且差分归入 `unknown`（不许当成「没变」）─────────
def test_unreadable_reading_is_reported_with_a_reason():
    """★ 拿不到 ⇒ ★ **记 `None` 并写原因**，★ 绝不假装读到 ✓"""
    fp = FP.read(_model(EnableSelectionManager=None, SelectionManager=None))
    assert fp["readings"]["selection"] is None
    assert "SelectionManager" in fp["missing"]["selection"], fp["missing"]


def test_compare_separates_unknown_from_same():
    """★★★ **最要紧的负例**：一侧读不到 ⇒ ★ 归 `unknown`，★ **不许归 `same`** ——
    ★ 因为把盲区报成「没变」，★ 就会让 B3 把「**我看不见**」当成「**声明与观察一致**」 ✗
    """
    before = {"readings": {"selection": 1, "features": None, "dirty": False}}
    after = {"readings": {"selection": 1, "features": 5, "dirty": True}}
    d = FP.compare_detailed(before, after)
    #: ★ 注意：差分**遍历全部九类** ⇒ 我合成里没给的类按 `None` 归 `unknown`（★ 那是对的）⇒
    #:   ★ 所以断言只看**我设过的那几个类**，不要求列表完全相等 ✓
    assert [c["class"] for c in d["changed"] if c["class"] == "dirty"] == ["dirty"], d["changed"]
    assert [c["class"] for c in d["unknown"] if c["class"] == "features"] == ["features"], d["unknown"]
    assert "selection" in d["same"]
    #: ★★ 并且钉住要点：`features` **绝不出现在** `same` 里（那会把盲区报成「没变」）✗
    assert "features" not in d["same"], "★ 读不到的类被当成「没变」了" + str(d)


def test_compare_reports_real_changes_with_before_and_after():
    before = FP.read(_model())
    after = FP.read(_model(GetSaveFlag=True, GetBodies2=[_Obj(GetFaceCount=6), _Obj(GetFaceCount=6)]))
    d = FP.compare_detailed(before, after)
    got = {c["class"]: (c["before"], c["after"]) for c in d["changed"]}
    assert got["dirty"] == (False, True)
    assert got["bodies"] == (1, 2)
    assert got["faces"] == (6, 12)


# ── ③ 读数必须只读：连读两次必须相等 ──────────────────────────────────────
def test_reads_have_no_side_effects_on_a_fake_model():
    """★ 同一状态连读两次 ⇒ ★ 两次必须**完全相等**（★ 这是「读数只读」的最小证据）✓

    ★ 在真机上这一步由 `tools/probe_fingerprint_sensitivity.py` 的第 0 格做
      （★ 那里还要求**中间什么都不做**）✓
    """
    m = _model()
    a, b = FP.read(m), FP.read(m)
    assert a["readings"] == b["readings"], (a["readings"], b["readings"])


def test_feature_walk_stops_at_the_cap_instead_of_lying():
    """★ 特征遍历到上限 ⇒ ★ 记 `None` + 原因，★ **不把「数到一半」当数完** ✓"""
    class _Loop:
        def __init__(self):
            self._d = {}
        def __getattr__(self, item):
            return None
    loop = _Loop()
    loop._d["GetNextFeature"] = loop            # ★ 自环 ⇒ 永远数不完
    loop._d["FirstFeature"] = None
    m = _Obj(FirstFeature=loop, SelectionManager=_Obj(GetSelectedObjectCount2=0),
             GetActiveSketch2=None, GetSaveFlag=False, GetBodies2=[],
             Extension=_Obj(GetDisplayStateSetting=0), GetActiveConfiguration=_Obj(Name="c"))
    fp = FP.read(m)
    assert fp["readings"]["features"] is None
    assert "上限" in fp["missing"]["features"], fp["missing"]


# ── ★★ 按文档类型分「适用格」（★ 真机：图纸上的 config）────────────────
def test_config_is_not_applicable_on_a_drawing():
    """★★★ **真机拆出来的「指纹语义缺口」**：★ 七条 `drawing_*` 调用**成功**，
    ★ 而**唯一读不到的格是 `config`** ⇒ ★★ 图纸**没有零件那种「配置」** ⇒
    ★ 它**不适用**，★ **不是「读不到」** ✓
    ★★ 若不这样分，会把**本该 `agree`** 的七条压成 `undecided` ✗（★ 真机实测过）✓
    """
    import sw_fingerprint as FP
    before = {"readings": {"config": None, "dirty": False, "features": 0,
                           "bodies": 0, "faces": 0, "selection": 0,
                           "edit_mode": "none", "rebuild": False, "display": "()"},
              "doc_kind": "drawing", "usable": True}
    after = dict(before)
    diff = FP.compare_detailed(before, after)
    assert [c["class"] for c in diff["not_applicable"]] == ["config"], diff
    assert diff["unknown"] == [], "★ `config` 不许落进「未知」（★ 那是两件事）"


def test_the_same_class_is_still_compared_on_a_part():
    """★ **负例**：★ 同一个 `config` 在**零件**上**照常比较**（★ 不适用只对图纸）✓"""
    import sw_fingerprint as FP
    base = {"readings": {"config": "默认", "dirty": False, "features": 0,
                         "bodies": 0, "faces": 0, "selection": 0,
                         "edit_mode": "none", "rebuild": False, "display": "()"},
            "doc_kind": "part", "usable": True}
    same = FP.compare_detailed(base, base)
    assert same["not_applicable"] == [] and "config" in same["same"]
    changed = dict(base)
    changed["readings"] = dict(base["readings"], config="新配置")
    d2 = FP.compare_detailed(base, changed)
    assert [c["class"] for c in d2["changed"]] == ["config"], d2
