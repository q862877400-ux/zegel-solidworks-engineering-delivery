"""★ 批次 78 的负例：**安全链必须真的挂在工具层**（★ 而不只是"能力层有那个函数"）。

（★ 事实 62：判据要能被机器守住 —— 「建成了能力」与「能力能被调」是**两件事**）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch78.py`（★ 被测）· `scripts/sw_simulation.py`（被包装的实现）
#         `docs/known-facts.md` 事实 526（网格爆内存）· 528（求解不出结果的**空选区**根因）·
#         529（内存换算只对 FFEPlus 成立）
# 定位:   ★★★ 三条契约：
#     ① ★ **工具真的注册进 `all_specs()`**（★ 只在 `scripts/` 里有函数**不算**）；
#     ② ★ **能解析到目标函数**（`module`/`function` 拼错 = 运行期才炸）；
#     ③ ★★ **`model` 由 `derived_args` 补**，且**不得覆盖已直传的参数名**
#        —— ★ 2026-10-04 真机踩过：把 **`study`** 传进量预算闸 ⇒ ★ 那道闸**静默失效**（事实 40）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import register_capabilities as rc                            # noqa: E402

BATCH = ROOT / "mcp-server" / "tool_specs_batch78.py"

#: ★ 本批两条（★ 名字一旦改了，这条测试就是要你去更新的地方）
EXPECTED = {
    "solidworks_simulation_create_mesh_safely": ("sw_simulation", "create_mesh_safely"),
    "solidworks_simulation_solver_type": ("sw_simulation", "static_solver_type_report"),
}


def test_batch78_is_registered():
    """★ 批次模块必须进 `BATCH_MODULES`（★ 否则声明了也到不了运行期）。"""
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch78"' in t, "★ batch78 没进 BATCH_MODULES"


def test_both_tools_reach_all_specs():
    """★★★ 核心断言：★ 两条都**出现在 `all_specs()` 里** ✓"""
    names = {getattr(s, "name", "") for s in rc.all_specs()}
    missing = sorted(set(EXPECTED) - names)
    assert not missing, "★ 这些工具没进 all_specs()：%r" % (missing,)


def test_target_functions_actually_exist():
    """★ `module`/`function` 要**真的能解析到**（★ 拼错的话只有运行期才炸）。"""
    for name, (mod, fn) in EXPECTED.items():
        m = importlib.import_module("scripts.%s" % mod)
        assert callable(getattr(m, fn, None)), "★ %s → %s.%s 解析不到" % (name, mod, fn)


def test_safe_tool_supplies_model_via_derived_args():
    """★★ `model` 必须由 `derived_args` 补 —— ★ 量预算闸要它读包围盒。

    ★★ 真机教训（2026-10-04）：★ 第一版把 **`study`** 传进那道闸 ⇒ ★ 它在**错误的对象**上
      取包围盒 ⇒ ★★ **静默失效**（内部 `except` 收成"判据自身出错、不因此阻断"）✓
    """
    spec = next((s for s in rc.all_specs()
                 if getattr(s, "name", "") == "solidworks_simulation_create_mesh_safely"), None)
    assert spec is not None, "★ 找不到安全入口那条 spec"
    assert getattr(spec, "derived_args", None), "★ 没有 derived_args ⇒ 量预算闸会静默失效"
    #: ★ 而 `model` **不能**同时出现在对外参数里（★ 会与 derived_args 撞名 ⇒ 注册器 GateError）
    params = {getattr(p, "name", "") for p in (getattr(spec, "params", None) or [])}
    assert "model" not in params, "★ `model` 不该作为对外参数（由 derived_args 补）"


def test_safe_tool_defaults_to_metric_units():
    """★★ 默认 `units=2`（Metric = **毫米**）—— ★ 真机实测：`units=2` 才是毫米口径。

    ★ 依据：`units=-1/0` 回 `4930.5017`（米口径），`units=2` 回 `4.9305`（**毫米**）✓
      ★★ 而**值与其单位口径必须配套** —— 否则 `CreateMesh` 会**静默退回默认**或网格退化 ✓
    """
    spec = next(s for s in rc.all_specs()
                if getattr(s, "name", "") == "solidworks_simulation_create_mesh_safely")
    units = next(p for p in spec.params if p.name == "units")
    assert units.default == 2, "★ 默认不是 units=2 ⇒ 调用方很容易喂出错口径"


def test_solver_type_tool_is_read_only_and_documented():
    """★ 求解器读数那条：★ 只读（`inject="study"`、无写参数）· ★ doc 说清"为什么重要"。"""
    spec = next(s for s in rc.all_specs()
                if getattr(s, "name", "") == "solidworks_simulation_solver_type")
    assert getattr(spec, "inject", "") == "study", spec
    assert [p.name for p in spec.params] == ["study_name"], spec.params
    doc = getattr(spec, "doc", "") or ""
    assert "FFEPlus" in doc, "★ doc 必须点明那条内存换算的出处求解器（★ 免得被过度外推）"
