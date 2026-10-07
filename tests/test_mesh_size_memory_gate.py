"""★ 网格尺寸**双侧**合理性闸的负例测试（★ 含今天那场「把米当毫米 ⇒ 40 GB」的事故）。

★ 事实 62：**没有负例的判据不算数** —— ★ 本测试的正例就用**真机事故里那个数**。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SOLIDWORKS Simulation 官方手册（本机解包 `C:\cworks_manual\`）
# 文件:   `scripts/sw_simulation.py`（★ 被测的 `check_mesh_size_sane` /
#         `default_solve_memory_budget_gb` / `DOF_PER_GB` / `DOF_PER_ELEMENT`）
# 官方依据: `C:\cworks_manual\c_Analysis_Solvers.htm` 与 `IDC_HELP_PRESTATIC_OPTIONS.htm` 逐字
#           「FFEPlus … For every 2,000,000 degrees of freedom, you need 1GB of RAM.」
#           · 同页逐字「If a solver requires more memory than available on the computer,
#             then the solver uses disk space … the solution progress can be extremely slow.」
#           · 同页逐字「the Large Problem Direct Sparse solver can handle simulation problems
#             that exceed the physical memory of your computer.」
# 实测依据: 事实 293 的求解进度窗：「自由度: 30,456 · 单元数: 7,250」⇒ DOF/单元 = 4.20
# 定位:   ★★★ **为什么写它**（2026-10-04 真机事故）：本闸原来**只判一侧**（单元尺寸大于零件
#   最大边 ⇒ 网格退化）⇒ ★★ 而探针的"自校准"把 `units=2` 回的**米**级值（0.0049）
#   喂进 `create_mesh`（★ 那个参数吃**毫米**）⇒ 网格单元数按包围盒估 ~1e12
#   ⇒ 求解进程 `cwbcbfmesh.exe` 实际吃到 **38.5 GB 工作集 / 52.6 GB 提交**（整机 63.8 GB）
#   ⇒ **整机卡死**。★ 故本测试的正例逐字是**那个数**：`0.0049` 必须被拒 ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

import sw_simulation as sim  # noqa: E402

#: ★ 真机夹具的尺寸（探针造的那块板）—— 100 × 60 × 20 mm
PLATE = (100.0, 60.0, 20.0)


def _fake_model_bbox(monkeypatch, size=PLATE):
    """把 `sw_part.get_bounding_box` 换掉 —— ★ 判据只读 `size`，故无需真 COM。

    ★★ 2026-10-07（接手轮 · 规格 214 T-214-12）**从"裸赋值"改成 `monkeypatch.setattr`** ——
      ★ 原来那句 `sw_part.get_bounding_box = _bb` **用完不会还原** ⇒ ★★ 同进程里**后面所有测试**
      看到的都是这个假函数 ⇒ ★ 实测把两个文件带红（★ 都是 bbox 相关，因果关系最干净）：
        · `test_sw_part_sketch_selection::BBoxTests` **×2** —— ★ 它们**正是**在测
          `get_bounding_box` 的边界行为（"没体/长度不对 ⇒ 必须抛 `RuntimeError`"），
          而假函数**不抛** ⇒ 断言「RuntimeError not raised」✗
        · `test_tool_specs_batch92` **×2** —— ★ `body_state` 与 `move_copy_body` 都要读 bbox ✗
      ★★ ⇒ **`monkeypatch` 在用例结束自动还原** ⇒ ★ 一处改、四个受害者一起好 ✓
      ⚠ 与本仓另外两处污染**同型**（`importlib.reload` · 假 `sw_connect` 不撤）⇒
        ★★ **定则：凡改**共享模块的属性**，一律走 `monkeypatch`，★ 不许裸赋值** ✓
    """
    import sw_part

    def _bb(_model):
        return {} if size is None else {"size": tuple(size)}

    monkeypatch.setattr(sw_part, "get_bounding_box", _bb)
    return object()


def test_the_official_constants_are_the_documented_ones() -> None:
    """★ 判据的两个系数必须**等于出处里那个数**（★ 改它就要改这条测试并说明依据）。"""
    assert sim.DOF_PER_GB == 2_000_000, "★ 官方逐字：每 2,000,000 自由度 1 GB RAM"
    assert abs(sim.DOF_PER_ELEMENT - 4.2) < 1e-9, (
        "★ 事实 293 的进度窗：30,456 自由度 / 7,250 单元 = 4.20")
    b = sim.default_solve_memory_budget_gb()
    assert 1.0 <= b <= 16.0, "★ 预算默认值必须在 (1, 16] GB 内，实测 %r" % b


def test_positive_todays_accident_value_is_rejected(monkeypatch) -> None:
    """★★★ 核心正例：**事故里那个数**（0.0049 mm，本意是 4.9 米的"米"口径）必须被拒。"""
    m = _fake_model_bbox(monkeypatch)
    r = sim.check_mesh_size_sane(m, 0.0049)
    assert r["ok"] is False, "★ 0.0049 mm 没被拦住 ⇒ 那道闸抓不到今天这场事故"
    assert "内存" in r["reason"] or "太小" in r["reason"], r["reason"]
    assert r["est_ram_gb"] > 16.0, r
    assert r["est_elements"] > 1e9, "★ 包围盒估出的单元数应当是个天文数字：%r" % r["est_elements"]


def test_negative_the_value_that_worked_is_accepted(monkeypatch) -> None:
    """★ 反例：**跑通过的那个值**（4.9339 mm ⇒ 7310 单元）不许被拒 —— ★ 否则闸太紧。"""
    for good in (4.9339, 4.9305, 5.0, 10.0):
        r = sim.check_mesh_size_sane(_fake_model_bbox(monkeypatch), good)
        assert r["ok"] is True, "★ 误伤：%r ⇒ %s" % (good, r.get("reason"))
    r = sim.check_mesh_size_sane(_fake_model_bbox(monkeypatch), 4.9339)
    assert r["est_elements"] < 1e6, "★ 合理网格的单元数估计不该是天文数字：%r" % r["est_elements"]


def test_existing_behaviour_too_large_still_rejected(monkeypatch) -> None:
    """★ 原有那一侧（太大 ⇒ 网格退化）**不能被这次改动弄丢**（★ 事实 61 同族）。"""
    r = sim.check_mesh_size_sane(_fake_model_bbox(monkeypatch), 4930.5)
    assert r["ok"] is False and "网格必然退化" in r["reason"], r
    for bad in (0.0, -1.0):
        assert sim.check_mesh_size_sane(_fake_model_bbox(monkeypatch), bad)["ok"] is False


def test_budget_parameter_is_honoured(monkeypatch) -> None:
    """★ 预算可调：★ 把预算压到极小 ⇒ **连合理值也被拒**（★ 否则那个参数是摆设 · 事实 40）。"""
    m = _fake_model_bbox(monkeypatch)
    assert sim.check_mesh_size_sane(m, 4.9339)["ok"] is True
    tight = sim.check_mesh_size_sane(m, 4.9339, memory_budget_gb=1e-9)
    assert tight["ok"] is False, "★ 预算参数没被用上 ⇒ 它就是个没人用的守卫"
    assert tight["memory_budget_gb"] == 1e-9


def test_no_bbox_means_record_only_do_not_judge(monkeypatch) -> None:
    """★ 量不到包围盒 ⇒ **只记不判**（★ 不因为没有参照就误拒）。"""
    r = sim.check_mesh_size_sane(_fake_model_bbox(monkeypatch, None), 0.0049)
    assert r["ok"] is True and "只记不判" in r["reason"], r


# ── 第二道闸（★ 建完网格、跑求解之前 · 用**真实单元数**）────────────────────

def test_preflight_rejects_a_giant_mesh() -> None:
    """★★ 第二道闸：真实单元数过大 ⇒ 必须拒（★ 它是"跑求解"前的最后一关）。"""
    r = sim.solve_memory_preflight(50_000_000)
    assert r["ok"] is False, r
    assert r["est_ram_gb"] > r["memory_budget_gb"]
    assert "别跑" in r["reason"], r["reason"]


def test_preflight_allows_the_mesh_that_worked() -> None:
    """★ 反例：真机跑通过的那个网格（**7,310 个单元**）不许被拒。"""
    for good in (7_250, 7_310):
        r = sim.solve_memory_preflight(good)
        assert r["ok"] is True, "★ 误伤 %r：%s" % (good, r.get("reason"))
        assert r["est_ram_gb"] < 1.0, r


def test_preflight_rejects_a_missing_mesh() -> None:
    """★ `element_count` 不是正整数（网格没建成）⇒ 拒 —— ★ 否则会拿空网格去求解。"""
    for bad in (0, -3, None):
        assert sim.solve_memory_preflight(bad)["ok"] is False


def test_preflight_budget_is_honoured() -> None:
    """★ 预算参数必须真的生效（★ 事实 40：没人用的参数 = 没有它）。"""
    assert sim.solve_memory_preflight(7_310)["ok"] is True
    tight = sim.solve_memory_preflight(7_310, memory_budget_gb=1e-9)
    assert tight["ok"] is False and tight["memory_budget_gb"] == 1e-9


def test_preflight_prefers_the_real_node_count() -> None:
    """★★ 给了 `node_count` 就用**第一性原理**那档（3×节点数），★ 且它是**上界**。

    ★ 真机标定：事实 293 的「30,456 自由度 / 11,301 节点」= 2.69 ⇒ ★ 3× 是保守侧 ✓
    """
    r = sim.solve_memory_preflight(7_250, node_count=11_301)
    assert r["est_dof"] == 11_301 * sim.DOF_PER_NODE, r
    assert "节点数" in r["★_算式"], r["★_算式"]
    assert r["est_dof"] > 30_456, "★ 3× 必须是实测值 30,456 的**上界**"
    #: ★ 只有单元数时回落到标定档
    r2 = sim.solve_memory_preflight(7_250)
    assert "单元数" in r2["★_算式"], r2["★_算式"]


def test_preflight_with_node_count_can_still_refuse() -> None:
    """★ 节点数**很大**时第二道闸照样要拦（★ 用节点数不是放松判据）。"""
    r = sim.solve_memory_preflight(1, node_count=50_000_000)
    assert r["ok"] is False and r["est_ram_gb"] > r["memory_budget_gb"], r


# ── 网格侧旋钮（★ 官方给的那几条"降规模"的路）────────────────────────────

class FakeMesh:
    """★ 假 CWMesh：行为要**像 COM 属性**（★ `set_com_member` 走的是 `obj.<名> = 值`）。

    ⚠★ 第一版把它写成"方法 `_set`" ⇒ `set_com_member` 的 `setattr` **绕过了它**
      ⇒ 于是"设不上"那条负例**永远不触发**（★ 由负例当场抓出）✓
    """

    def __init__(self):
        object.__setattr__(self, "values", {
            "Quality": 1, "MesherType": 2, "ElementSize": 4.93,
            "MinElementSize": 0.5, "MaxElementSize": 20.0,
            "ElementSizeFactorForEachLoop": 1.0, "MinElementsInCircle": 12,
            "NumberOfLoops": 3, "AutomaticLooping2": True,
            "ElementCount": 7_250, "NodeCount": 11_301})
        object.__setattr__(self, "fail_for", set())

    def __getattr__(self, name):
        values = object.__getattribute__(self, "values")
        if name in values:
            return values[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in object.__getattribute__(self, "fail_for"):
            raise RuntimeError("设不上 %s" % name)
        object.__getattribute__(self, "values")[name] = value


class FakeStudy:
    def __init__(self, mesh=None):
        self.Mesh = mesh if mesh is not None else FakeMesh()


def test_mesh_settings_report_reads_the_scale_knobs() -> None:
    """★ 只读报告：规模相关的旋钮都要读到（★ 那是"改动前后"对照的前提）。"""
    rep = sim.mesh_settings_report(FakeStudy())
    assert rep["ok"] is True
    for k in ("Quality", "MesherType", "MinElementSize", "MaxElementSize",
              "MinElementsInCircle", "NumberOfLoops", "ElementCount", "NodeCount"):
        assert k in rep, "★ 少了 %s" % k
    assert rep["NodeCount"] == 11_301


def test_configure_mesh_settings_reads_back_and_only_touches_what_it_is_given() -> None:
    """★★ 两条契约：① 每项**回读核对**；② **没给的不碰**（★ 不顺手改用户的网格偏好）。"""
    study = FakeStudy()
    rep = sim.configure_mesh_settings(study, quality=0, min_element_size=2.0,
                                      min_elements_in_circle=6)
    assert rep["ok"] is True, rep
    names = {c["name"] for c in rep["changed"]}
    assert names == {"Quality", "MinElementSize", "MinElementsInCircle"}, names
    assert study.Mesh.values["Quality"] == 0 and study.Mesh.values["MinElementSize"] == 2.0
    #: ★ 没给的三项必须**原样不动**
    assert study.Mesh.values["MesherType"] == 2 and study.Mesh.values["NumberOfLoops"] == 3
    assert study.Mesh.values["MaxElementSize"] == 20.0


def test_configure_mesh_settings_reports_set_failures() -> None:
    """★★ 设不上 ⇒ `failed` 里可见（★ 不把"set 没报错"当成"设上了" —— 规则 6）。"""
    study = FakeStudy()
    study.Mesh.fail_for.add("Quality")
    rep = sim.configure_mesh_settings(study, quality=0)
    assert rep["ok"] is False and rep["failed"], rep
    assert "Quality" not in {c["name"] for c in rep["changed"]}


def test_configure_mesh_settings_says_what_draft_costs() -> None:
    """★★★ `Quality=Draft` 的**代价必须随返回值一起给**（★ 官方逐字：draft 是"快评"用）。"""
    rep = sim.configure_mesh_settings(FakeStudy(), quality=0)
    assert "代价" in rep["★_代价"] or "Draft" in rep["★_代价"]
    assert "quick evaluation" in rep["★_代价"], rep["★_代价"]


# ── 直接运行 ──────────────────────────────────────────────────────────────

def _main() -> int:
    fails = []
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("  [ok] %s" % name)
            except AssertionError as exc:
                fails.append(name)
                print("  [FAIL] %s: %s" % (name, exc))
    print("★ %d 条失败" % len(fails))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(_main())
