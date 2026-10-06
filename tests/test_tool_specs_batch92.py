"""★ 批次 92 的契约测试：规格 209 · B1 批（重建 / 构造几何 / 显示状态 / 引用文档，5 个）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch92.py` · `scripts/sw_session.py` ·
#         `scripts/sw_sketch_edit_ops.py` · `scripts/sw_render_material.py` ·
#         `scripts/sw_document_data.py`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 SC-2/SC-3；★ 本文件四条契约 + **两条负例**：
#         ① 5 个都能解析到真实函数；② ★ **必填形参**必须全都声明（门禁口径）；
#         ③ ★★ **裁决书点名的两个陷阱要有回归测试**（**不靠"我记得写了"**）：
#            · `EditRebuild3` 是**方法** ⇒ 拿它当属性读会得到 **bound method（恒真）**
#              ⇒ 本测试用**假模型记调用**证明 `rebuild_report` **真的调了它** ✓
#            · `ambiguous`：装配（`swDocASSEMBLY=2`）里**不许**替调用方猜活动显示状态 ✓
#         ④ `GetDocumentDependencies2` 的**步长**判据：官方 Returns 是"每个文档 2 个串"
#            ⇒ ★ 长度**除不尽**必须报错（★ 不硬凑、不猜哪个串是谁的）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as rc                            # noqa: E402
import tool_specs_batch92 as b92                              # noqa: E402

EXPECTED = 6


def test_batch92_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch92"' in t


def test_six_specs_declared_and_resolve():
    assert len(b92.SPECS_BATCH92) == EXPECTED, len(b92.SPECS_BATCH92)
    for s in b92.SPECS_BATCH92:
        m = importlib.import_module("scripts.%s" % s.module)
        fn = getattr(m, s.function, None)
        assert callable(fn), "%s → %s.%s" % (s.name, s.module, s.function)


def test_required_params_are_all_declared():
    """★ 判据按**门禁的口径**：**必填**形参（无默认值）必须全都声明（有默认值的可省略）✓"""
    for s in b92.SPECS_BATCH92:
        m = importlib.import_module("scripts.%s" % s.module)
        fn = getattr(m, s.function)
        sig = inspect.signature(fn)
        declared = {p.name for p in s.params}
        inj = getattr(s, "inject", "") or ""
        required = [n for n, p in sig.parameters.items()
                    if p.default is inspect.Parameter.empty and n != inj]
        missing = [n for n in required if n not in declared]
        assert not missing, "★ %s 漏了必填形参: %r（声明=%r）" % (s.name, missing, sorted(declared))


def test_no_bare_coordinates_and_readonly_flags():
    """★ 规则 3：本批**不收裸坐标**（★ 所有几何类参数都带 `_mm`/`_deg`）✓"""
    for s in b92.SPECS_BATCH92:
        for p in (getattr(s, "params", None) or []):
            low = p.name.lower()
            if low.endswith(("_mm", "_deg")):
                continue
            assert low not in ("x", "y", "z", "point", "coordinate"), (s.name, p.name)
            assert not low.endswith(("_x", "_y", "_z")), (s.name, p.name)
    ro = {s.name: bool(s.read_only) for s in b92.SPECS_BATCH92}
    assert ro["solidworks_config_list_display_states"] is True
    assert ro["solidworks_document_dependencies"] is True
    assert ro["solidworks_config_apply_display_state"] is False
    assert ro["solidworks_part_move_copy_body"] is False


# ── 负例 / 契约 ②③④（★ 用假对象，**不连 SolidWorks**）────────────────────────────────

class _Ext:
    """`IModelDocExtension` 的假身（`NeedsRebuild2` 是**属性**）。"""

    def __init__(self, state=0):
        self.NeedsRebuild2 = state
        self.force_all_called = 0

    def ForceRebuildAll(self):
        self.force_all_called += 1
        return True


class _Model:
    """`IModelDoc2` 的假身 —— ★ **记下 `EditRebuild3` 真被调了没有**。"""

    def __init__(self, state=0):
        self.Extension = _Ext(state)
        self.calls: list = []

    def EditRebuild3(self):                                    # ★ 是**方法**，不是属性
        self.calls.append("EditRebuild3")
        return True

    def ForceRebuild3(self, top_only):
        self.calls.append(("ForceRebuild3", bool(top_only)))
        return True


def _patch_feature_names(monkeypatch):
    import sw_session
    monkeypatch.setattr(sw_session, "feature_names", lambda model, limit=400: ["A", "B"])


def test_rebuild_edit_really_calls_the_method(monkeypatch):
    """★★ 裁决书硬约束的回归测试：**照抄外部项目当属性读会拿到 bound method（恒真）** ——
    ★ 本用例证明 `rebuild_report` **真的调用了它**（★ 而"读"也会被记成调用，故再看返回值）✓"""
    import sw_session
    _patch_feature_names(monkeypatch)
    doc = _Model(state=0)
    r = sw_session.rebuild_report(doc, "edit")
    assert doc.calls == ["EditRebuild3"], doc.calls
    assert r["ok"] is True, r
    assert r["entry_used"] == "IModelDoc2::EditRebuild3()"


def test_rebuild_force_passes_top_only_and_rejects_bad_mode(monkeypatch):
    import sw_session
    _patch_feature_names(monkeypatch)
    doc = _Model(state=0)
    r = sw_session.rebuild_report(doc, "force", top_only=True)
    assert doc.calls == [("ForceRebuild3", True)], doc.calls
    assert r["ok"] is True and r["top_only_applied"] is True, r
    bad = sw_session.rebuild_report(doc, "nonsense")
    assert bad["ok"] is False and "未知的 mode" in (bad["error"] or ""), bad
    assert sw_session.rebuild_report(None, "edit")["ok"] is False


def test_rebuild_all_uses_extension():
    import sw_session
    doc = _Model(state=0)
    r = sw_session.rebuild_report(doc, "all")
    assert doc.Extension.force_all_called == 1, doc.Extension.force_all_called
    assert r["entry_used"] == "IModelDocExtension::ForceRebuildAll()", r


def test_rebuild_fails_when_state_not_cleared(monkeypatch):
    """★ 判据是**回读**：`NeedsRebuild2` 没归零 ⇒ `ok=False`（★ 不信返回值）✓"""
    import sw_session
    _patch_feature_names(monkeypatch)
    doc = _Model(state=1)                                       # ★ 永远"需要重建"
    r = sw_session.rebuild_report(doc, "edit")
    assert r["ok"] is False and "回读判据未过" in (r["error"] or ""), r


# ── 显示状态（idx 97）────────────────────────────────────────────────────────

class _Cfg:
    Name = "默认"

    def __init__(self, names=None):
        self._names = list(names if names is not None else ["A", "B"])
        self.applied = []

    def GetDisplayStates(self):
        return list(self._names)

    def GetDisplayStatesCount(self):
        return len(self._names)

    def ApplyDisplayState(self, name):
        self.applied.append(name)
        if name not in self._names:
            return False
        self._names = [name] + [n for n in self._names if n != name]
        return True


class _CfgMgr:
    def __init__(self, cfg):
        self.ActiveConfiguration = cfg


class _Doc:
    def __init__(self, cfg, dtype=1):
        self.ConfigurationManager = _CfgMgr(cfg)
        self._dtype = dtype

    def GetType(self):
        return self._dtype


def test_list_display_states_part_is_unambiguous():
    import sw_render_material as RM
    doc = _Doc(_Cfg(["A", "B"]), dtype=1)                       # 1 = swDocPART
    r = RM.list_display_states(doc)
    assert r["ok"] is True and r["display_states"] == ["A", "B"], r
    assert r["ambiguous"] is False and r["active"] == "A", r


def test_list_display_states_assembly_is_ambiguous():
    """★★ 裁决书硬约束：装配里「第一个名字即活动」**不保证成立** ⇒ 必须给 `ambiguous` ✓"""
    import sw_render_material as RM
    doc = _Doc(_Cfg(["A", "B"]), dtype=2)                       # 2 = swDocASSEMBLY
    r = RM.list_display_states(doc)
    assert r["ambiguous"] is True and r["ambiguous_reason"], r
    assert "ReferencedDisplayState" in r["ambiguous_reason"], r


def test_display_state_count_mismatch_is_reported():
    """★ 规则 6：两个官方入口读数不一致 ⇒ **不许挑一个当结论** ✓"""
    import sw_render_material as RM
    cfg = _Cfg(["A", "B"])
    cfg.GetDisplayStatesCount = lambda: 7
    r = RM.list_display_states(_Doc(cfg))
    assert r["ok"] is False and r["count_mismatch"] is True, r


def test_apply_display_state_reads_back():
    import sw_render_material as RM
    cfg = _Cfg(["A", "B"])
    r = RM.apply_display_state(_Doc(cfg, dtype=1), "B")
    assert r["ok"] is True and r["active_after"] == "B", r
    assert r["changed"] is True, r


def test_apply_display_state_refuses_unknown_name():
    """★ 铁律 5：名字不在清单里 ⇒ **报错不猜**（★ 也不替调用方新建显示状态）✓"""
    import sw_render_material as RM
    cfg = _Cfg(["A", "B"])
    r = RM.apply_display_state(_Doc(cfg), "no_such_state")
    assert r["ok"] is False and "不在这份清单里" in (r["error"] or ""), r
    assert cfg.applied == [], cfg.applied
    assert RM.apply_display_state(None, "A")["ok"] is False


# ── 引用文档（idx 244）────────────────────────────────────────────────────────

class _Sw:
    def __init__(self, ret):
        self._ret = ret
        self.seen = None

    def GetDocumentDependencies2(self, document, traverse, search, add_read_only):
        self.seen = (document, bool(traverse), bool(search), bool(add_read_only))
        return self._ret


def test_dependencies_parses_official_pairs():
    """★ 官方 Returns 逐字：每个文档 **2** 个串（名字 + 全路径）⇒ 按步长还原成记录 ✓"""
    import sw_document_data as DD
    sw = _Sw(["Part1", r"C:\temp\Part1.SLDPRT", "SubAssem1", r"C:\temp\SubAssem1.SLDASM"])
    r = DD.document_dependencies(sw, r"C:\temp\asm.SLDASM")
    assert r["ok"] is True and r["count"] == 2, r
    assert r["entries"][0] == {"name": "Part1", "path": r"C:\temp\Part1.SLDPRT",
                               "read_only": None, "read_only_flag": None}, r["entries"][0]
    assert sw.seen[1:] == (True, False, False), sw.seen


def test_dependencies_read_only_info_is_three_per_document():
    """★ 官方例子逐字：开了 `AddReadOnlyInfo` ⇒ **非只读**的那个是**空串**（不是「未知」）✓"""
    import sw_document_data as DD
    sw = _Sw(["Part1", r"C:\temp\Part1.SLDPRT", "Read-Only",
              "SubAssem1", r"C:\temp\SubAssem1.SLDASM", ""])
    r = DD.document_dependencies(sw, r"C:\temp\asm.SLDASM", add_read_only_info=True)
    assert r["ok"] is True and r["count"] == 2, r
    assert r["entries"][0]["read_only_flag"] is True, r["entries"][0]
    assert r["entries"][1]["read_only_flag"] is False, r["entries"][1]


def test_dependencies_read_only_false_literal_from_real_machine():
    """★★★ **官方例子与真机读数不一致**（本能力实测抓到）—— 官方例子说**非只读**的跟的是**空串**，
    ★ 而**本机实测（2026-10-06）回的是字符串 `"FALSE"`** ⇒ ★ **按「非空即只读」写判据会判反**
    （`bool("FALSE")` 是 `True`）⇒ ★ 本用例把这条**钉住**：`"FALSE"` 必须判成 `False`，
    ★ 而**认不出**的串必须回 `None`（**不猜**）✓"""
    import sw_document_data as DD
    sw = _Sw(["P", r"C:\P.SLDPRT", "FALSE"])
    r = DD.document_dependencies(sw, "a.SLDASM", add_read_only_info=True)
    assert r["entries"][0]["read_only"] == "FALSE", r["entries"][0]
    assert r["entries"][0]["read_only_flag"] is False, r["entries"][0]
    sw2 = _Sw(["P", r"C:\P.SLDPRT", "WHO-KNOWS"])
    r2 = DD.document_dependencies(sw2, "a.SLDASM", add_read_only_info=True)
    assert r2["entries"][0]["read_only_flag"] is None, r2["entries"][0]


def test_dependencies_odd_length_is_refused():
    """★★ 长度除不尽 ⇒ **不硬凑、不猜哪个串是谁的**（★ 这是本能力的核心判据）✓"""
    import sw_document_data as DD
    r = DD.document_dependencies(_Sw(["A", r"C:\A.SLDPRT", "B"]), "x.SLDASM")
    assert r["ok"] is False and "除不尽" in (r["error"] or ""), r
    assert r["entries"] == [], r


def test_dependencies_empty_array_is_explicitly_ambiguous():
    """★ 空数组**是合法读数**，但本函数**不区分**「确实没依赖」与「文档名不对」—— 如实记 ✓"""
    import sw_document_data as DD
    r = DD.document_dependencies(_Sw([]), "x.SLDASM")
    assert r["ok"] is True and r["count"] == 0 and r["note"], r
    assert DD.document_dependencies(_Sw([]), "  ")["ok"] is False


def test_dependencies_carries_the_library_feature_blind_spot():
    """★★ 裁决书硬约束：**库特征不会返回** ⇒ 盲区必须**随返回值**带出去（不写就是静默的错答案）✓"""
    import sw_document_data as DD
    r = DD.document_dependencies(_Sw(["A", r"C:\A.SLDPRT"]), "x.SLDASM")
    blob = " ".join(r["limitations"])
    assert "Library features" in blob, blob
    assert "Suppressed components" in blob, blob


# ── 移动 / 复制实体（idx 209）──────────────────────────────────────────────────

class _Body:
    def __init__(self, box, owner=None):
        self._box = box
        self.owner = owner
        self.selected_with = None

    def GetBodyBox(self):
        return list(self._box)

    def Select2(self, append, data):
        self.selected_with = getattr(data, "Mark", None)
        if self.owner is not None:                              # ★ 模拟"选中被记进选区"
            self.owner.SelectionManager.count += 1
        return True


class _SelData:
    Mark = 0


class _SelMgr:
    def __init__(self):
        self.count = 0

    def CreateSelectData(self):
        return _SelData()

    def GetSelectedObjectCount2(self, mark):
        return self.count


class _BodyModel:
    """★ 假零件：`GetBodies2` / `ClearSelection2` / `SelectionManager` / `FeatureManager`。"""

    def __init__(self, n_bodies=1):
        self.SelectionManager = _SelMgr()
        self.bodies = [_Body([0.0, 0.0, 0.0, 60.0, 40.0, 20.0], self) for _ in range(n_bodies)]
        self.calls = []
        self.move_geometry = True

    def GetBodies2(self, kind, visible_only):
        return list(self.bodies)

    def ClearSelection2(self, flag):
        self.SelectionManager.count = 0

    @property
    def FeatureManager(self):
        return self

    def InsertMoveCopyBody2(self, *args):
        self.calls.append(args)
        self.SelectionManager.count = len(self.bodies)      # ★ 特征建完后 SW 会清掉选择
        if len(args) >= 11 and args[10]:                    # BCopy
            self.bodies.append(_Body([100.0, 0.0, 0.0, 160.0, 40.0, 20.0], self))
        elif self.move_geometry:
            self.bodies[0] = _Body([25.0, 0.0, 0.0, 85.0, 40.0, 20.0], self)
        return object()                                     # IFeature 指针（★ 不当判据）


def test_move_copy_body_passes_millimetres_raw():
    """★★ 规则 2 的要害是**单位对**，不是"换算了就算数" —— 实测这几个长度参数按**文档长度单位
    （mm）**解释（★ 与官方页没写单位、与本仓绝大多数 COM 几何接口的"米"**相反**）⇒
    ★ 本用例钉住：**原样传毫米，不做 mm→m 换算** ✓"""
    import sw_body_ops as BO
    m = _BodyModel()
    r = BO.move_copy_body(m, "all", translate_x_mm=25.0)
    assert r["ok"] is True and r["moved"] is True, r
    args = m.calls[0]
    assert args[0] == 25.0 and args[3] == 0.0, args       # ★ 25.0 原样，不是 0.025
    assert len(args) == 12, args
    assert any("文档长度单位" in x for x in r["unit_findings"]), r["unit_findings"]


def test_move_copy_body_copy_increases_body_count():
    """★ 判据是**回读**：复制档要**实体个数增加**（★ 不看它回的 IFeature 指针）✓"""
    import sw_body_ops as BO
    m = _BodyModel()
    r = BO.move_copy_body(m, "all", translate_x_mm=40.0, copy=True, num_copies=1)
    assert r["ok"] is True and r["copied"] is True, r
    assert r["after"]["body_count"] == r["before"]["body_count"] + 1, r


def test_move_copy_body_reports_the_official_both_given_trap():
    """★★ 官方 Remarks 的坑：**平移与旋转不能同时生效**、同时给**只应用旋转** ⇒
    ★ 本工具必须**说出来**（`both_given=True` + 写明官方逐字），★ 不静默 ✓"""
    import sw_body_ops as BO
    m = _BodyModel()
    r = BO.move_copy_body(m, "all", translate_x_mm=5.0, rotate_angle_z_deg=30.0)
    assert r["both_given"] is True, r
    assert "only the rotation parameters are applied" in (r["note"] or ""), r
    #: ★ 实测：COM 侧角度是**弧度**（★ 而同一调用的长度是**毫米** —— 一个接口混两种口径）
    #:   ⇒ 本仓在边界 `deg()` 换算**一次**（规则 2 的原话）
    #: ★★ 且实测**官方参数名与作用轴不一致（X↔Z 互换）** ⇒ 要"绕 Z 转"就得放进**第 1 个角槽**
    #:   ⇒ 本用例把补偿钉住（`args[7]` = RotAngleX 槽 = π/6，`args[9]` = RotAngleZ 槽 = 0）✓
    assert abs(m.calls[0][7] - 0.5235987755982988) < 1e-12, m.calls[0]
    assert m.calls[0][9] == 0.0, m.calls[0]
    assert m.calls[0][0] == 5.0, m.calls[0]              # ★ 长度原样（不换算）


def test_move_copy_body_rejects_bad_selection_and_copies():
    import sw_body_ops as BO
    m = _BodyModel()
    bad = BO.move_copy_body(m, "index:99", translate_x_mm=1.0)
    assert bad["ok"] is False and "越界" in (bad["error"] or ""), bad
    assert BO.move_copy_body(m, "all", num_copies=0)["ok"] is False
    assert BO.move_copy_body(None, "all")["ok"] is False


def test_body_state_keeps_unreadable_bbox_distinct_from_unchanged():
    """★★ `None`（读不到 ⇒ 判据不可用）与 `False`（读了 ⇒ 没变）**必须分得开** ——
    ★ 否则"读不到"会被当成"没变"（★ 这是本轮自查抓到的真实静默失效）✓"""
    import sw_body_ops as BO
    m = _BodyModel()
    good = BO.body_state(m)
    assert good["bbox_comparable"] is True and good["bbox_mm"]["max"][0] == 60.0, good
    empty = BO.body_state(_BodyModel(n_bodies=0))
    assert empty["bbox_comparable"] is False and empty["bbox_mm"] is None, empty


def test_rebuild_bbox_criterion_is_not_vacuous(monkeypatch):
    """★★ 回归：`get_bounding_box` 回的是**字典** —— 第一版按可迭代对象写 ⇒
    `float("min")` 抛异常被吞 ⇒ **`bbox_changed` 永远 False（判据空转）** ⇒ 本用例钉住修好的形态 ✓"""
    import sw_session
    import sw_part
    _patch_feature_names(monkeypatch)
    monkeypatch.setattr(sw_part, "get_bounding_box",
                        lambda model, **kw: {"min": [0.0, 0.0, 0.0], "max": [60.0, 40.0, 20.0],
                                             "size": [60.0, 40.0, 20.0]})
    doc = _Model(state=0)
    r = sw_session.rebuild_report(doc, "edit")
    assert r["bbox_comparable"] is True, r
    assert r["bbox_before"] == ((0.0, 0.0, 0.0), (60.0, 40.0, 20.0)), r["bbox_before"]
    assert r["bbox_changed"] is False, r
