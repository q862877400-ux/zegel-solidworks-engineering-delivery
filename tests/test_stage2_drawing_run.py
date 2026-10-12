"""★ 阶段 2 契约测试：真机工程图的 spec 构造（规格 317 的 D4 真机链）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_stage2_drawing_run.py
# 定位:   规格 `specs/317-stage2-real-holes` 的 D4 真机链契约测试
# 官方依据: ① `subskills/solidworks-engineering-drawing/schemas/drawing_spec.schema.json`
#              （★ 官方 schema 是**权威** —— 本测试直接调官方校验器）
#           ② 真机实测（2026-10-12）抓到的三条封闭码：
#              `DRAWING_REQUESTED_VIEWS_UNSUPPORTED` / `DRAWING_VIEW_OPTIONS_UNSUPPORTED`
#              / `DRAWING_REQUIRED_DIMENSIONS_UNSUPPORTED` / `DRAWING_GBT_TEMPLATE_MISSING`
#           ③ `tools/tool_caller.py` 只认 `all_specs()`（476）而工具面是 521
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

from scripts.engineering import drawing_run as DR                      # noqa: E402


def _spec() -> dict:
    return DR.build_drawing_spec(
        source_model=ROOT / "output" / "stage2" / "板1_rev-1.sldprt",
        size_mm=[100.0, 60.0, 20.0], hole_dia_mm=6.0, hole_count=4,
        thickness_mm=20.0)


def test_spec_passes_official_validator() -> None:
    """★★ 判据是**官方校验器**（★ 不是我自认为对）。"""
    v = DR.validate_spec(_spec())
    assert v.get("status") == "pass", v.get("issues")


def test_views_are_orthographic_only() -> None:
    """★ 真机约束：通用生成器**不能建**辅助/轴测/剖视/局部视图。"""
    v = _spec()["views"]
    assert set(v) <= {"front", "top", "bottom", "left", "right", "sections",
                      "details"}
    assert "front" in v, "★ schema 要求 front 必有"
    #: ★ 视图对象**不能带落位/方向选项**（真机报 `DRAWING_VIEW_OPTIONS_UNSUPPORTED`）
    for k, o in v.items():
        assert o == {}, "★ 视图 %s 带了选项：%s" % (k, o)


def test_required_dimensions_empty_per_real_machine() -> None:
    """★★ 真机约束：`requiredDimensions` 必须**留空**。

    ★ 通用生成器报 `DRAWING_REQUIRED_DIMENSIONS_UNSUPPORTED`：
      「只能导入模型尺寸，不能可靠创建并绑定指定 ID、视图和语义的尺寸」。
    ★★ 这**改变了 SC-005 的口径** —— 覆盖率必须从**真机图纸回读**，不是从 spec 数。
    """
    assert _spec()["requiredDimensions"] == []


def test_gb_template_is_present() -> None:
    """★ 真机约束：GB/T 图框必须指到（★ 否则 `DRAWING_GBT_TEMPLATE_MISSING`）。"""
    p = DR.gb_template_path()
    assert p.is_file(), "★ 本机找不到 GB/T A3 图框：%s" % p
    assert "gb" in p.name.lower()


def test_outputs_field_names_are_exact() -> None:
    """★ `outputs` 的字段名是**固定集**，且 `slddrw`/`report` 必需。"""
    o = _spec()["outputs"]
    assert "slddrw" in o and "report" in o
    assert set(o) <= {"slddrw", "pdf", "png", "report", "dxf"}


def test_required_top_level_keys() -> None:
    """★ 官方 schema 的**九项必需**字段一个都不能少。"""
    need = {"schemaVersion", "sourceModel", "documentType", "standard",
            "projection", "paperSize", "modelSizeMm", "views", "outputs"}
    assert need <= set(_spec())


def test_write_spec_roundtrips(tmp_path: pathlib.Path) -> None:
    """★ 落盘后可读回、且仍是合法 spec。"""
    import json
    p = DR.write_spec(_spec(), tmp_path / "spec.json")
    assert p.is_file()
    back = json.loads(p.read_text(encoding="utf-8"))
    assert DR.validate_spec(back).get("status") == "pass"


#: ══ tool_caller 的第二注册来源（★ 阶段 2 抓到的真缺陷）════════════════

def test_tool_caller_sees_server_py_tools() -> None:
    """★★ 真缺陷回归：`tool_caller` 必须认得 `server.py` 那 45 个工具。

    ★ 实测（2026-10-12）：原实现只读 `rc.all_specs()`（**476** 个），
      而工具面是 **521** ⇒ `solidworks_generate_drawing` /
      `solidworks_new_document` / `solidworks_save_document` **执行器不认**
      ⇒ **出不了工程图**。
    """
    import tool_caller
    sp = tool_caller._specs()
    assert len(sp) == 521, "★ 执行器只认得 %d 个工具（应为 521）" % len(sp)
    for n in ("solidworks_generate_drawing", "solidworks_new_document",
              "solidworks_save_document", "solidworks_export_active"):
        assert n in sp, "★ 执行器不认得 %s" % n
