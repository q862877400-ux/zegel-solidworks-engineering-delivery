"""★ 判据 —— **`configure_force` 必须用 `set_com_member` 写属性**（★ 2026-10-10 真机修）。

★★★★★ **这是什么 bug**（★ 真机实测 · 由弹窗分级器读出根因）：
  ★ `sw_simulation_loadprops.configure_force()` 原本用
    `get_com_member(force, "NormalForceOrTorqueValue", 值)` 去**设**力的大小 ✗
  ★★ 而 `get_com_member` 的语义是「★ **取或调**」（★ **有实参 ⇒ 一定调用**）——
    `NormalForceOrTorqueValue` 是**可写属性**（★ 不是方法）⇒
    ★★ 它**不是「找不到成员」**，而是**取回来是个 `float`、不可调用** ⇒
    ★ **抛 `TypeError`** ⇒ ★★ **力的大小从来没设上** ✗
  ★★★ **后果（★ 真机）**：★ 求解弹窗报
    「★ **未定义载荷或规定的位移**」+「固定-刚性零件上的载荷将不处于活动状态」
    ⇒ ★ **求解被前置检查拦住**（★ 返回码 `19`）✓
  ★★★★ **正解在本仓早已写明** —— `sw_connect.set_com_member` 的 docstring 逐字：
    「★★ 与已知事实 4（读用 `get_com_member`）成对：★ **读走 `get_com_member`，
      ★ 写走本函数**」✓
  ★★★ **修后真机**：★ `配力结果={'NormalForceOrTorqueValue': 100.0}` ⇒
    ★★ **求解 `return_code 0` · `results_present=true` · 4 个图**（`位移1`/`应力1`/`应变1`/`品质1`）✓

★★ **判据分层**：★ 本文件**纯离线**（★ AST 扫源码 —— ★ 不连 COM）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_simulation_loadprops.py`（★ `configure_force`）
#         `scripts/sw_connect.py`（★ `get_com_member` = 取或调 · `set_com_member` = 只写）
#         `output/_probe_ec09_fea.json`（★ 真机证据：修后求解成功）
# 定位:   ★ 守卫「**写 COM 属性必须走 `set_com_member`**」这条纪律。
# 官方依据: `ICWForce` 的 `set_*` 方法族在 pywin32 迟到绑定下取不到；
#         ★ `obj.<名> = 值` 是**唯一被真机验证通过**的形态（见 `set_com_member` 的 docstring）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 纯离线 —— ★ 用 AST 扫，★ 不碰 COM）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LOADPROPS = ROOT / "scripts" / "sw_simulation_loadprops.py"

#: ★★★ **`ICWForce` 上那几个「可写属性」**（★ 不是方法）
#:   ★ 依据：`set_com_member` 的 docstring 逐字点名 `ForceType` / `Unit` /
#:     `NormalForceOrTorqueValue`；★ 下面几个同族（★ 官方是 `set_` 前缀方法，
#:     ★ 而 pywin32 迟到绑定下取不到 ⇒ **必须走属性赋值**）
FORCE_WRITABLE_PROPS = (
    "NormalForceOrTorqueValue", "PhaseAngle", "PhaseAngleUnit",
    "EquationLinearUnit", "EquationAngularUnit",
    "EquationCoordinateSystemType", "IncludeNonUniformDistribution2",
)


@pytest.fixture(scope="module")
def src() -> str:
    return LOADPROPS.read_text(encoding="utf-8")


def test_configure_force_never_gets_a_writable_property(src):
    """★★★★★ **`configure_force` 里不许用 `get_com_member` 写那几个属性**（★ 本判据的全部意义）。

    ★★ 判据：★ 源码里**不得出现**
      `get_com_member(force, "<可写属性>", …)`（★ 带实参 = **会调用**）✗
    ★★★ **红基线已验**：★ 把修好的 `set_com_member` 改回 `get_com_member` ⇒ 本判据**立刻红** ✓
    """
    tree = ast.parse(src)
    offenders: list[str] = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "get_com_member"):
            continue
        #: ★★★ **判据的精确形态（★ 第一版写错了，★ 本判据自己抓出来的）**：
        #:   `get_com_member(obj, name)` = **2 参** ⇒ ★ **无实参的"取"** ⇒ **合法** ✓
        #:   `get_com_member(obj, name, value)` = **3 参** ⇒ ★ **带实参 = 会调用** ⇒ ✗
        #:   ⚠ 我第一版写 `len(node.args) < 2: continue` ⇒ ★ **把 2 参的读也算了进来**
        #:     ⇒ ★ 报了 4 处**假阳性**（`collect_load_property_evidence` 里的**读**）✗
        if len(node.args) < 3:
            continue                      #: ★ 2 参 = 纯读 ⇒ 允许
        arg1 = node.args[1]
        if isinstance(arg1, ast.Constant) and arg1.value in FORCE_WRITABLE_PROPS:
            offenders.append("L%d: get_com_member(force, %r, …)"
                             % (node.lineno, arg1.value))
    assert not offenders, (
        "★★★ 用 `get_com_member` **写**了可写属性 ⇒ ★ 它会**当方法调用** ⇒ 抛 `TypeError` "
        "⇒ ★★ **属性从来没设上**（★ 真机后果：求解报「未定义载荷」）：\n    %s"
        % "\n    ".join(offenders))


def test_configure_force_uses_set_com_member_for_those_props(src):
    """★★★★ **必须**用 `set_com_member` 写它们**（★ 逐字承 `set_com_member` 的 docstring：

    ★「★ **读走 `get_com_member`，写走本函数**」）。
    """
    tree = ast.parse(src)
    written: set[str] = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "set_com_member" and len(node.args) >= 2):
            arg1 = node.args[1]
            if isinstance(arg1, ast.Constant):
                written.add(str(arg1.value))
    #: ★ 至少那三个被真机点名的必须在（★ 其余可选 —— ★ 只查「有没有用对形态」）
    for prop in ("NormalForceOrTorqueValue", "PhaseAngle", "PhaseAngleUnit"):
        assert prop in written, (
            "★★ `%s` 没用 `set_com_member` 写 ⇒ ★ 它设不上" % prop)


def test_magnitude_reaches_the_applied_dict(src):
    """★★★ **`applied` 必须记下 `NormalForceOrTorqueValue`**（★ 那是**回读依据**）。

    ★★ 依据：★ `configure_force` 的契约是「★ **返回实际设置了的项**」——
      ★★ 若它报了这个键，★ 调用方就能**据以判**「力的大小设上了」✓
    """
    tree = ast.parse(src)
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if (isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name)
                        and t.value.id == "applied"):
                    if isinstance(t.slice, ast.Constant) and \
                            t.slice.value == "NormalForceOrTorqueValue":
                        found = True
    assert found, "★★ `applied` 里没记 `NormalForceOrTorqueValue` ⇒ ★ 调用方无从判"


def test_repo_documents_the_get_vs_set_rule():
    """★★★★ **本仓必须写明那条纪律**（★ 它是修法的依据 —— ★ 不是我的发明）。

    ★★ 依据（★ `sw_connect.set_com_member` 的 docstring 逐字）：
      ★「★★ 与已知事实 4（读用 `get_com_member`）成对：★ **读走 `get_com_member`，
        ★ 写走本函数**」✓
    """
    t = (ROOT / "scripts" / "sw_connect.py").read_text(encoding="utf-8")
    assert "读走 get_com_member" in t or "读走 ``get_com_member``" in t, (
        "★★ 本仓没写明「读走 get_com_member、写走 set_com_member」这条纪律")


def test_real_machine_evidence_shows_solve_succeeded():
    """★★★★★ **真机证据：修后求解成功**（★ 判据不是我说了算，★ 是证据）。

    ★★ 依据（★ `output/_probe_ec09_fea.json` 真机读数）：
      · ★ `配力结果 = {'NormalForceOrTorqueValue': 100.0}`（★ **力的大小设上了**）
      · ★ `run_report.return_code = 0` · ★ `results_present = true`
      · ★ `plot_count = 4`（★ `位移1`/`应力1`/`应变1`/`品质1`）
    """
    ev = ROOT / "output" / "_probe_ec09_fea.json"
    if not ev.is_file():
        pytest.skip("★★ 缺真机证据 ⇒ 跑 `sw_guard` 探针后再判")
    import json
    d = json.loads(ev.read_text(encoding="utf-8"))
    conf = d.get("force_configured") or {}
    if not conf:
        pytest.skip("★ 该次证据是修前的 ⇒ 跳过（★ 修后重跑即生效）")
    assert conf.get("NormalForceOrTorqueValue") == 100.0, (
        "★★ 力的大小没设上：%r" % conf)
    run = d.get("run_report") or {}
    assert run.get("return_code") == 0, "★★ 求解返回码 %r ≠ 0" % run.get("return_code")
    assert run.get("results_present") is True, "★★ 没有结果"
    assert run.get("plot_count", 0) >= 1, "★★ 图数为 0"
    #: ★★ 且**不许**有「未定义载荷」那个弹窗（★ 那正是根因的症状）
    for dlg in (d.get("dialogs_seen") or []):
        joined = " ".join(dlg.get("texts") or [])
        assert "未定义载荷" not in joined, (
            "★★★ 仍然弹出「未定义载荷」⇒ ★ 力还是没设上：%r" % joined[:160])
