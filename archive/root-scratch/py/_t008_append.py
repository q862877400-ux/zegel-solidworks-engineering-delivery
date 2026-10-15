

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**T-008 的契约测试**）+ `specs/001-topology-result-readout`
# 文件:   `tests/test_sw_topology_contract.py` —— 追加 `collect_topology_numbers` 的契约测试
# 官方签名依据: 反射 `D:\AI\SW\_raw\reflect\iface_cosworks.txt` 的 `## ICWResults` 段（裁决者）
# 定位:   做 `specs/001-topology-result-readout/tasks.md` 的 **T-008**。
#         spec 的 T-007 验收要求两条**形态契约**：
#           ① 有结果 ⇒ 返回读数，且**每个读数附来源成员名**（可复查）
#           ② **未跑过 ⇒ `{"status": "no_results", …}`，不抛未捕获异常、不静默空 dict**
#         本文件用**假对象**（无 COM）把这两条形态**钉死** ——
#         真机那一次由 `tools/capture_topology_evidence.py` 的闭环负责（003 已证）。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本文件**不连 SolidWorks**（沿用本文件既有约定：静态比对）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────


class _FakeResults:
    """`ICWResults` 的替身：只实现本模块**实际调用**的无参数成员。"""

    def __init__(self, plots=None, steps=None):
        self._plots = plots
        self._steps = steps

    GetPlotCount = property(lambda self: 0 if self._plots is None else len(self._plots))
    GetPlotNames = property(lambda self: (() if self._plots is None else tuple(self._plots)))
    GetMaximumAvailableSteps = property(lambda self: self._steps)


class _FakeStudy:
    """`ICWStudy` 的替身。`results=None` 表示**还没跑过**（合法状态，不是异常）。"""

    def __init__(self, results):
        self.Results = results


def _call(study):
    module = _load_module()
    return module.collect_topology_numbers(study)


def test_collect_numbers_without_results_reports_no_results() -> None:
    """★ T-007 形态②：`Results` 为 None ⇒ **明确报无结果**，不抛异常、不空 dict。"""
    got = _call(_FakeStudy(None))
    assert got["status"] == "no_results"
    assert "Results" in got["reason"], got
    assert got["source_members"]["results"] == "ICWStudy.Results"
    assert set(got) >= {"status", "reason", "source_members"}


def test_collect_numbers_with_zero_plots_reports_no_results() -> None:
    """`Results` 非 None 但**零张图** ⇒ 同样是「无结果」（**不用返回码判**）。"""
    got = _call(_FakeStudy(_FakeResults(plots=None)))
    assert got["status"] == "no_results"
    assert "GetPlotCount" in got["reason"], got


def test_collect_numbers_with_plots_reports_ok_and_source_members() -> None:
    """★ T-007 形态①：有图 ⇒ 返回读数，且**每个读数附来源成员名**（spec 硬要求）。"""
    got = _call(_FakeStudy(_FakeResults(plots=["品质1", "材料质量1"], steps=1)))
    assert got["status"] == "ok", got
    assert got["plot_count"] == 2
    assert got["plot_names"] == ["品质1", "材料质量1"]
    assert got["material_mass_plot"] == "材料质量1"
    assert got["max_available_steps"] == 1
    # **可复查性**：每个读数都要指得出是哪个官方成员给的
    assert got["source_members"] == {
        "results": "ICWStudy.Results",
        "plot_count": "ICWResults.GetPlotCount",
        "plot_names": "ICWResults.GetPlotNames",
        "max_available_steps": "ICWResults.GetMaximumAvailableSteps",
    }


def test_collect_numbers_matches_english_material_mass_name() -> None:
    """判据**不硬编码中文**（spec §Assumptions）：英文界面的 `Material Mass 1` 也要命中。"""
    got = _call(_FakeStudy(_FakeResults(plots=["Stress1", "Material Mass 1"], steps=3)))
    assert got["material_mass_plot"] == "Material Mass 1"


def test_collect_numbers_returns_none_when_material_mass_absent() -> None:
    """有图但**没有** Material Mass ⇒ `material_mass_plot` 为 `None`（不是报错）。"""
    got = _call(_FakeStudy(_FakeResults(plots=["应力1"], steps=1)))
    assert got["status"] == "ok"
    assert got["material_mass_plot"] is None


def test_unresolved_members_are_documented_with_reasons() -> None:
    """★ **事实 30/铁律 5 的守卫**：参数语义查不到的成员要**登记原因**，不能悄悄实现。

    ⚠ 6 条里每一条都必须给出「为什么没实现」，否则下一个人会以为「忘了写」。
    """
    module = _load_module()
    unresolved = module.TOPOLOGY_RESULTS_UNRESOLVED
    assert len(unresolved) == 6, sorted(unresolved)
    for name, why in unresolved.items():
        assert why.strip(), "%s 没有给原因" % name
        assert ("无文档" in why or "无官方" in why or "未给" in why or "一源" in why), (
            "%s 的原因没说清是「参数语义查不到」还是「只有一源」" % name)
    # 这几个**正是** T-004 逐个核过「不存在」之外的、反射里**存在**的那批
    assert "GetMinMaxDisplacement" in unresolved
    assert "SavePlotsAseDrawings" in unresolved
