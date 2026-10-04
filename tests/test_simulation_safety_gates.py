"""★ 仿真"别把机器算爆 / 别把会话卡死"三处根因的负例（★ 事实 526/527）。

（① SW 忙就别发调用 ② 隔离层杀得掉且不无界等待 ③ 网格安全档可还原）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SOLIDWORKS Simulation 官方手册（本机解包 `C:\cworks_manual\`）
# 文件:   `scripts/sw_busy.py`（SW 忙检）· `scripts/sw_isolate.py`（隔离加固）·
#         `scripts/sw_simulation.py`（`mesh_safety_apply` / `mesh_safety_restore`）·
#         `scripts/sw_simulation_worker.py`（★ **每个入口都先过忙检**）
# 定位:   ★★★ 三条判据，每条都要**能响**（★ 事实 62：没有负例的判据不算数）：
#     ① ★ **忙检不许误报**：★ 只读实测抓到过**孤儿** `进度` 窗（属 Explorer、SW 早关了）
#        ⇒ ★ 若判据不要求"**SolidWorks 应用本体在跑**"，它会**永远回忙**、把正常工作全挡住 ✓
#     ② ★ **隔离层**：★ 超时后要**用 `taskkill /T /F` 杀树**、且**不做无界等待** ——
#        ★ 这两条都是真机实测逼出来的（`subprocess.run` 的超时**没杀掉**卡在跨进程 COM 里的子进程；
#        而它的超时分支里那句 `communicate()` 会**无限期**等 ⇒ 现场就是"父进程一直不返回"）✓
#     ③ ★ **网格安全档**：★ 只碰 `Quality`/`MesherType` 两个 **Int32**（★ 无单位风险）·
#        ★ **原值读不到的项不写回** · ★ 还原后**逐项读回校验** ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_busy as busy                                    # noqa: E402
import sw_isolate as iso                                  # noqa: E402
import sw_simulation as sim                               # noqa: E402

SW_APP = r"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\SLDWORKS.exe"
SW_BG = (r"C:\Program Files (x86)\Common Files\SOLIDWORKS 安装管理程序"
         r"\BackgroundDownloading\sldBgDwld.exe")


def _w(pid, title, cls, exe=""):
    return {"pid": pid, "title": title, "cls": cls, "exe": exe}


# ── ① 忙检 ────────────────────────────────────────────────────────────────

def test_busy_ignores_the_orphan_progress_window():
    """★★★ 核心负例：**SolidWorks 本体不在时，孤儿 `进度` 窗不算忙**。

    ★ 真机实录：SW 关掉之后那个 `OperationStatusWindow`（**属 Explorer**）还在
      ⇒ ★ 第一版判据因此**永远回忙**（会把所有正常工作挡死 —— ★ 比不判更坏）✓
    """
    r = busy.solidworks_busy([_w(14488, "进度", "OperationStatusWindow", r"C:\Windows\Explorer.EXE")])
    assert r["busy"] is False, r
    assert r["★_孤儿进度窗"], "★ 孤儿窗要**如实留证据**（只是不判忙）"


def test_busy_ignores_family_processes_that_are_not_the_app():
    """★★ 「家族进程」**不等于**「SolidWorks 在跑」：★ 安装管理器的后台下载器就有窗口。"""
    r = busy.solidworks_busy([_w(29360, "sldBgDwld", "Afx:00400000:0", SW_BG)])
    assert r["busy"] is False, r


def test_busy_detects_progress_window_when_it_belongs_to_the_family():
    """★ 家族进程的 `进度` 窗 ⇒ **忙**；★ 而 shell 残留的那个 ⇒ **不忙**（★ 当场抓到的误报）。

    ★★ 真机实录（2026-10-04）：本机有个 `OperationStatusWindow`（`进度`、**属 Explorer**）
      从 9:53 挂到 12:47、SW 关掉都还在 ⇒ ★ 只认类名会让判据**一直回忙**、
      把探针的三次读数**全拒掉**（实测发生）⇒ ★ 故判据要求**可归属给家族** ✓
    """
    armed = busy.solidworks_busy([
        _w(9, "零件1", "Afx:1", SW_APP),
        _w(2, "进度", "OperationStatusWindow", SW_APP)])          # ★ 属家族 ⇒ 忙
    assert armed["busy"] is True and armed["reasons"], armed

    orphan = busy.solidworks_busy([
        _w(9, "零件1", "Afx:1", SW_APP),
        _w(14488, "进度", "OperationStatusWindow", r"C:\Windows\Explorer.EXE")])
    assert orphan["busy"] is False, orphan
    assert orphan["★_不可归属的进度窗"], "★ 不可归属的窗要**如实留证据**（只是不判忙）"


def test_busy_detects_not_responding_ghost_and_title():
    """★ 两条"不响应"的判据都要响（★ 鬼窗 + 家族标题兜底 —— ★ 免得类名变了就瞎）。"""
    ghost = busy.solidworks_busy([_w(9, "零件1", "Afx:1", SW_APP),
                                  _w(3, "SOLIDWORKS 2026 (Not Responding)", "swPM_GhostWindow")])
    assert ghost["busy"] is True, ghost
    titled = busy.solidworks_busy([_w(9, "SOLIDWORKS 2026 (无响应)", "Afx:1", SW_APP)])
    assert titled["busy"] is True, titled


def test_busy_is_false_when_idle():
    """★ 正常在跑 ⇒ **不忙**（★ 判据不许把正常工作也挡住）。"""
    assert busy.solidworks_busy([_w(9, "零件1", "Afx:1", SW_APP)])["busy"] is False


# ── ② 隔离层 ──────────────────────────────────────────────────────────────

def test_kill_tree_reports_failure_without_raising():
    """★ 杀不存在的 pid ⇒ **如实回失败**，★ **不抛**（★ 杀不掉也要能被处理）。"""
    r = iso.kill_tree(999_999_999)
    assert r["ok"] is False and r["error"], r
    assert "seconds" in r


def test_timeout_uses_taskkill_and_returns_bounded():
    """★★★ 超时 ⇒ ★ **走 `taskkill /T /F`** · ★ 回 `timed_out` · ★ 且在**有界时间**内返回。

    ★ 真机教训（事实 526）：★ `subprocess.run` 的超时**没杀掉**卡在跨进程 COM 里的子进程，
      ★ 而它的超时分支会**无限期**等 ⇒ 现场"父进程一直不返回" ✓
    """
    r = iso.run_isolated("tools._stall_fixture", "forever", timeout=3, drain_timeout=5)
    assert r["timed_out"] is True, r
    assert r["seconds"] <= 40, "★ 有界返回没做到（用时 %s）" % r["seconds"]
    assert "kill" in r, "★ 缺 `kill` 交代 ⇒ 调用方看不出用什么杀的"
    assert r["kill"].get("ok") in (True, False), r["kill"]


def test_run_isolated_signature_keeps_the_contract():
    """★ 契约（★ 调用方按位置/关键字都用过它）：★ `timeout` 仍在、★ 新增 `drain_timeout` 有默认值。"""
    sig = inspect.signature(iso.run_isolated)
    assert sig.parameters["timeout"].default == 180.0
    assert sig.parameters["drain_timeout"].default == 10.0


# ── ③ 网格安全档 ──────────────────────────────────────────────────────────

class FakeMesh:
    """★ 假 CWMesh（★ 属性式：`set_com_member` 走的是 `obj.<名> = 值`）。"""

    def __init__(self, **over):
        vals = {"Quality": 1, "MesherType": 2, "ElementSize": 0.0, "MinElementSize": 0.0,
                "MaxElementSize": 0.0, "ElementSizeFactorForEachLoop": 0.8,
                "MinElementsInCircle": 8, "NumberOfLoops": 3, "AutomaticLooping2": False,
                "ElementCount": 0, "NodeCount": 0}
        vals.update(over)
        object.__setattr__(self, "values", vals)

    def __getattr__(self, name):
        vals = object.__getattribute__(self, "values")
        if name in vals:
            return vals[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        object.__getattribute__(self, "values")[name] = value


class FakeStudy:
    def __init__(self, mesh=None):
        self.Mesh = mesh if mesh is not None else FakeMesh()


def test_preflight_says_which_solver_the_rule_belongs_to():
    """★★★ **那条内存换算是"哪把尺子"必须写在结果里**（★ 2026-10-04 · 我自己留下的漏洞）。

    ★ 事实：那条换算「每 2,000,000 自由度 1 GB」**逐字出自 FFEPlus 那一页** ✓
    ★★ 而真机那次**成功**的求解，求解器自己写的是 **`Intel Direct Sparse`**
      ⇒ ★ 直接法**不能**用 FFEPlus 的尺子（★ 而本仓**没有**直接法的官方换算 —— 铁律 5）✓
    ⚠ ★ 第一版按**精确名**匹配 ⇒ ★ `Intel Direct Sparse` **落进了 else 分支**（★ 当场发现）⇒
      现在按**子串**匹配 ✓
    """
    #: ★ FFEPlus ⇒ 正适用
    assert "正适用" in sim.solve_memory_preflight(100, solver_name="FFEPlus")["★_适用性"]
    #: ★★ 真机上那个名字（带空格的组合名）⇒ **必须进直接法那一支**
    v = sim.solve_memory_preflight(100, solver_name="Intel Direct Sparse")["★_适用性"]
    assert "直接法" in v and "同一把尺子" in v, v
    for name in ("Direct Sparse", "INTEL", "intel_cluster"):
        assert "直接法" in sim.solve_memory_preflight(100, solver_name=name)["★_适用性"], name
    #: ★ 没告知 ⇒ **适用性未定**（★ 不许默认成"适用"）
    assert "未告知" in sim.solve_memory_preflight(100)["★_适用性"]
    #: ★★ `automatic` ⇒ **SW 自选**（★ 真机实测选的是 Intel Direct Sparse）⇒ 也别用 FFEPlus 的尺子
    for name in ("automatic", "Automatic", 0):
        v = sim.solve_memory_preflight(100, solver_name=name)["★_适用性"]
        assert "自选" in v and "别用 FFEPlus" in v, (name, v)
    #: ★ 不认识的 ⇒ 未查证（★ 不猜）
    assert "未查证" in sim.solve_memory_preflight(100, solver_name="ZZZ")["★_适用性"]


def test_solver_type_report_never_invents_a_default():
    """★ 读不到求解器类型 ⇒ **`ok=False` + 原因**（★ **不许默认成 FFEPlus** —— 铁律 5）。"""
    class _Boom:
        def __getattr__(self, n):
            raise RuntimeError("no such member")

    r = sim.static_solver_type_report(_Boom())
    assert r["ok"] is False and r["reason"], r
    assert r["value"] is None and r["name"] is None, r
    #: ★ 枚举映射本身要是**逐条可核**的（出处写在常量上方）
    assert sim.SWS_SOLVER_TYPES["ffeplus"] == 2 and sim.SWS_SOLVER_TYPES["direct_sparse"] == 1


def test_mesh_safety_apply_only_touches_the_two_int32_knobs():
    """★★ 安全档**只碰** `Quality`/`MesherType`（★ 两个 `Int32`，★ 无单位风险）。

    ★ 为什么重要（★ 事实 526）：★ 带单位的 `MinElementSize` **口径未定**，
      ★ 我按毫米写过一次 ⇒ **探针卡 13 分钟** ⇒ ★ 安全档**不许**碰它 ✓
    """
    study = FakeStudy()
    r = sim.mesh_safety_apply(study)
    assert r["ok"] is True, r
    names = {c["name"] for c in r["changed"]}
    assert names == {"Quality", "MesherType"}, names
    assert study.Mesh.values["Quality"] == 0 and study.Mesh.values["MesherType"] == 0
    #: ★ 带单位的那三个必须**原样不动**
    assert study.Mesh.values["MinElementSize"] == 0.0
    assert study.Mesh.values["MaxElementSize"] == 0.0
    assert r["token"] == {"Quality": 1, "MesherType": 2}, r["token"]


def test_mesh_safety_restore_puts_the_originals_back():
    """★★ 还原：★ 逐项写回 + **读回校验**（★ 不把"设了"当成"还原了"）。"""
    study = FakeStudy()
    token = sim.mesh_safety_apply(study)["token"]
    r = sim.mesh_safety_restore(study, token)
    assert r["ok"] is True, r
    assert study.Mesh.values["Quality"] == 1 and study.Mesh.values["MesherType"] == 2
    assert {c["name"] for c in r["restored"]} == {"Quality", "MesherType"}, r


def test_mesh_safety_restore_writes_nothing_when_originals_are_unreadable():
    """★★★ **原值读不到 ⇒ 一个字都不写**（★ 免得把"读不到"变成"写了个错的旧值"）。"""
    study = FakeStudy()
    r = sim.mesh_safety_restore(study, {"Quality": None, "MesherType": None})
    assert r["ok"] is False and r["restored"] == [], r
    assert study.Mesh.values["Quality"] == 1, "★ 不该写"
    assert len(r["skipped"]) == 2, r


def test_mesh_safety_restore_without_token_refuses():
    """★ 没凭据 ⇒ **拒绝**（★ 不猜该还原成什么）。"""
    r = sim.mesh_safety_restore(FakeStudy(), None)
    assert r["ok"] is False and "不猜" in r["reason"], r


# ── ③b `create_mesh_safely`（★ 那条链，★ 也是我刚修掉一个真 bug 的地方）────────

def test_create_mesh_safely_passes_the_MODEL_not_the_study_to_the_size_gate(monkeypatch):
    """★★★ **锁住那个真 bug**（2026-10-04 真机跑出来的）：

    ★ 第一版我把 **`study`** 传给了 `check_mesh_size_sane(model, …)` ⇒
      ★ 那道闸在**错误的对象**上取包围盒 ⇒ ★★ **静默失效**（内部 `except` 收成"判据自身出错、
      不因此阻断"）⇒ ★ "量预算前置闸"**看起来在跑、实际没判** ✓
    ⇒ ★ 这条测试要求：★ **第一个位置参数必须是 `model`**（★ 不是 study）。
    """
    seen = {}

    def _fake_gate(model, element_size, **kw):
        seen["model"] = model
        seen["element_size"] = element_size
        return {"ok": False, "reason": "★ 测试：假装不放行"}

    monkeypatch.setattr(sim, "check_mesh_size_sane", _fake_gate)
    study, model = FakeStudy(), object()
    r = sim.create_mesh_safely(study, model=model, element_size=4.93)
    assert seen["model"] is model, "★ 闸门收到的不是 model ⇒ 它会静默失效"
    assert seen["model"] is not study, "★ 传成 study 就是那个 bug"
    assert r["blocked"] == "MESH_SIZE_UNSANE" and r["ok"] is False, r
    #: ★ 闸门不放行 ⇒ **不许碰网格**（连安全档都不该设：证书里没有 safety 的改动）
    assert study.Mesh.values["Quality"] == 1, "★ 闸门拒了却改了设置"


def test_create_mesh_safely_without_model_records_the_skip_honestly():
    """★★ 不给 `model` ⇒ `size_gate` **如实记"跳过"**（★ `ok=None` + `skipped`），★ **不假装判过**。"""
    study = FakeStudy()
    r = sim.create_mesh_safely(study, element_size=4.93)          # ★ 故意不给 model
    assert r["size_gate"]["skipped"] is True and r["size_gate"]["ok"] is None, r["size_gate"]
    assert "跳过" in r["size_gate"]["reason"], r["size_gate"]
    #: ★ 假 study 建不了网格 ⇒ 那一步要**如实失败**（★ 不许报成功）
    assert r["ok"] is False, r
    assert r["mesh"]["ok"] is False, r.get("mesh")
    #: ★★ 而且**设置必须被还原**（★ 连失败路径也不许把改动留下 —— 事实 526/525 同纪律）
    assert study.Mesh.values["Quality"] == 1 and study.Mesh.values["MesherType"] == 2, \
        study.Mesh.values


def test_create_mesh_safely_restores_even_when_meshing_raises(monkeypatch):
    """★★ 建网格**抛异常** ⇒ 也要**还原**（★ `finally` 那条路，★ 同事实 525 的纪律）。"""
    def _boom(*a, **k):
        raise RuntimeError("★ 测试：网格炸了")

    monkeypatch.setattr(sim, "create_mesh_report", _boom)
    study = FakeStudy()
    r = sim.create_mesh_safely(study, element_size=4.93)
    assert "网格炸了" in (r.get("mesh_exception") or ""), r
    assert study.Mesh.values["Quality"] == 1, "★ 异常路径没还原设置"
    assert r["restored"]["ok"] is True, r["restored"]


# ── ④ "将来别人用也生效"：每个 worker 入口都必须先过忙检 ──────────────────

@pytest.mark.parametrize("entry", ["mesh_size_by_name", "create_mesh_by_name",
                                   "run_analysis_by_name", "mesh_settings_by_name",
                                   "configure_mesh_settings_by_name"])
def test_every_worker_entry_checks_busy_first(entry):
    """★★★ **这道是"未来别人用也生效"的那道**（★ 事实 62 的形态：判据要能被机器守住）。

    ★ 做法：★ 读 `sw_simulation_worker` 的源码，要求该入口函数体里**出现 `_busy_guard()`**
      ⇒ ★ 以后**新增**一个 worker 入口而忘了加忙检 ⇒ **这条测试红** ✓
    ★ 为什么值得单独守：★ 忙检是唯一"**不发调用就没得卡**"的根因处置（事实 526）——
      ★ 漏一个入口，就漏一个能卡死整条链的地方 ✓
    """
    import sw_simulation_worker as worker

    src = inspect.getsource(worker)
    fn = getattr(worker, entry)
    body = inspect.getsource(fn)
    assert "_busy_guard()" in body, (
        "★ `%s` 没有先过忙检 —— ★ 新增 worker 入口必须调 `_busy_guard()` 并 return 它的拒绝" % entry)
    assert "_busy_guard" in src and "SETTINGS" not in body          # 防呆：确保不是同名空函数


def test_busy_guard_returns_none_when_idle(monkeypatch):
    """★ 不忙 ⇒ `_busy_guard()` 回 `None`（★ 不许把正常路径挡掉）。"""
    import sw_simulation_worker as worker

    assert worker._busy_guard() is None


def test_busy_guard_blocks_and_does_not_touch_com(monkeypatch):
    """★★★ 忙 ⇒ 回**结构化拒绝**（★ `blocked=SOLIDWORKS_BUSY`），★ **且一个 COM 调用都不发**。

    ★ 判据：★ 我把 `connect_solidworks` 换成一个**一旦被调就炸**的替身 ——
      ★ 忙检若没先挡住，这条测试会以"连了 COM"失败 ✓
    """
    import sw_busy
    import sw_simulation_worker as worker

    #: ★ 把"忙时等待"压到 0 —— ★ 否则 5 个入口各等一轮默认值（实测 80 s，★ 那是测试在替真机等待）
    monkeypatch.setattr(worker, "BUSY_IDLE_WAIT_S", 0.0)
    monkeypatch.setattr(sw_busy, "solidworks_busy",
                        lambda *a, **k: {"busy": True, "reasons": ["★ 测试：假装在忙"]})

    def _boom(*a, **k):
        raise AssertionError("★ 忙的时候**不许连 COM**（事实 526）")

    monkeypatch.setattr(worker, "connect_solidworks", _boom)
    for entry in (worker.mesh_settings_by_name, worker.mesh_size_by_name,
                  worker.create_mesh_by_name, worker.run_analysis_by_name,
                  worker.configure_mesh_settings_by_name):
        r = entry("AnyStudy") if entry is not worker.create_mesh_by_name else entry("AnyStudy")
        assert r["ok"] is False and r["blocked"] == sw_busy.BUSY_BLOCKED_CODE, (entry, r)
        assert r["busy_detail"]["reasons"], r
