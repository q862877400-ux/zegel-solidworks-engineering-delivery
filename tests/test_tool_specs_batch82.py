"""★ 批次 82 的契约测试：**第二坡扇出 + FR-006 语义去重**后的 13 个真的挂上了、且重复的没夹带。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch82.py`（由 `tools/build_toolspec_batch_from_rows.py` 生成）·
#         `output/bunny2-gate-report.json`（逐行门禁结论）·
#         `output/_drop_refused.py`（主线删重复用的名单）
# 定位:   规格 `specs/205-tool-ramp/` 的 SC-002/SC-004；★ 两条本批特有契约：
#         ① ★ **FR-006 删掉的那 6 个不许夹带**（含两个"未护栏的原始网格旋钮" —— 事实 526）
#         ② ★ 13 个都要**能解析到真实函数**、且**没有裸坐标**（规则 3）
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

#: ★ 本批**明确删掉**的（FR-006 语义重复 + 两个安全旋钮）
#: ★★★ 2026-10-07（规格 213 · B1）**订正一处**：★ `solidworks_export_flat_pattern_dxf`
#:   **从本表移出** ✓ —— ★ 而它的 `_report` 兄弟**仍留在表里** ✓
#:   ★★ 事由：★ batch82 把它俩当 **FR-006 语义重复**删掉（★ 两个名字指同一能力 ✓），
#:     ★ 而**另有一条硬理由**：★ 官方真前置是「**已保存**的钣金件」✗，★ 而本仓硬约束⑦
#:       原先是「**一律不保存文档**」⇒ 那时它**到不了建成** ✓
#:   ★★★ **用户 2026-10-07 授权**（★ 原话「**D 我允许你做**」✓）⇒ ★ 本仓把它做成
#:     **受控例外**（★ `allow_temporary_save` **默认 `False`** ⇒ ★ 行为与从前完全一致 ✓），
#:     ★ 并**真机建成**（★ 回读 DXF **20219 字节** ✓）⇒ ★ 于是**挂且只挂一个** ✓
#:   ★★★★ **为什么只挂一个是对的**（★ 与本规格 B4-6 的终检结论一致 ✓）：
#:     ★★ **一个能力挂两个工具 = "大杂烩"** ✗（★ 违反本仓定位 ✓）⇒
#:     ★ **`solidworks_export_flat_pattern_dxf_report` 有意仍不挂** ✓ ——
#:     ★ 它作为**内部入口**留着（★ 返回更富的证据字典 ✓）✓
DROPPED = ("solidworks_export_pdf",
           "solidworks_export_flat_pattern_dxf_report",
           "solidworks_assembly_add_distance_mate_by_name",
           "solidworks_simulation_configure_mesh_settings",
           "solidworks_simulation_mesh_safety_apply")
#: ★ 本批留下的 13 个
KEPT = ("solidworks_assembly_add_mate_checked", "solidworks_assembly_suppress_component",
        "solidworks_assembly_unsuppress_component", "solidworks_assembly_replace_component",
        "solidworks_assembly_dissolve", "solidworks_assembly_exit_edit_part_in_context",
        "solidworks_appearance_delete_render_material", "solidworks_simulation_ensure_addin",
        "solidworks_simulation_get_study_manager", "solidworks_simulation_create_study_by_type",
        "solidworks_simulation_default_solve_memory_budget_gb",
        "solidworks_simulation_mesh_settings_report", "solidworks_assembly_add_parallel_mate")


def test_batch82_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch82"' in t


def test_thirteen_kept_tools_present():
    names = {getattr(s, "name", "") for s in rc.all_specs()}
    missing = [n for n in KEPT if n not in names]
    assert not missing, "★ 没挂上: %r" % (missing,)


def test_dropped_six_are_absent():
    """★★ FR-006：删掉的真重复与**两个未护栏的原始网格旋钮**都不许夹带（事实 526）。"""
    names = {getattr(s, "name", "") for s in rc.all_specs()}
    leaked = [n for n in DROPPED if n in names]
    assert not leaked, "★ 夹带了本该删掉的: %r" % (leaked,)


def test_every_kept_tool_resolves():
    specs = {getattr(s, "name", ""): s for s in rc.all_specs()}
    for n in KEPT:
        s = specs[n]
        m = importlib.import_module("scripts.%s" % s.module)
        assert callable(getattr(m, s.function, None)), "%s → %s.%s" % (n, s.module, s.function)


def test_no_bare_coordinates():
    specs = {getattr(s, "name", ""): s for s in rc.all_specs()}
    for n in KEPT:
        for p in (getattr(specs[n], "params", None) or []):
            assert p.name.lower() not in ("x", "y", "z", "point", "coord", "center", "origin"), \
                (n, p.name)
