"""★ 批次 81 的契约测试：**Bunny 扇出 + 机器门禁**这条路的产出真的挂上了，且没夹带"不做"的东西。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch81.py`（★ 由 `tools/build_toolspec_batch_from_rows.py` **生成**）·
#         `tools/check_bunny_toolspec_rows.py`（★ 那条路用的门禁）·
#         `output/bunny-gate-report.json`（逐行结论）
# 定位:   规格 `specs/205-tool-ramp/` 的 SC-002/SC-004/SC-009；★ 三条本批特有的契约：
#         ① ★ 生成物里的每个工具都要**能解析到真实函数**（生成器不可能保证这一点 ⇒ 测试守）
#         ② ★ **主线明确不做的两个不许夹带**（`send_message` / `is_type_mismatch`）
#         ③ ★ 本批工具**没有裸坐标**（规则 3）
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

REFUSED = ("solidworks_dialog_send_message", "solidworks_com_is_type_mismatch")


def _specs():
    return {getattr(s, "name", ""): s for s in rc.all_specs()}


def test_batch81_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch81"' in t


def test_every_batch81_tool_resolves_to_a_real_function():
    """★★ 生成物的核心风险：`module`/`function` 拼错看着像工具、跑起来才炸 ⇒ 测试逐条解析 ✓"""
    specs = _specs()
    mods = {s.module for s in specs.values() if getattr(s, "module", "")}
    n = 0
    for name, s in specs.items():
        if getattr(s, "module", "") not in mods:
            continue
        #: ★ 只测"本批可能引入的"那些模块（用生成器写过的模块名）
        if s.module not in ("sw_review", "sw_feature_readback", "sw_import_mesh_reference",
                            "sw_preflight", "sw_sketch_dimensions", "sw_misumi",
                            "sw_automation_knowledge", "sw_com_traps"):
            continue
        m = importlib.import_module("scripts.%s" % s.module)
        assert callable(getattr(m, s.function, None)), "%s → %s.%s" % (name, s.module, s.function)
        n += 1
    assert n >= 18, "★ 本批相关工具少于 18 个（实得 %d）" % n


def test_refused_two_are_absent():
    """★ 主线明确不做的两个**不许夹带**（FR-002/D-5）。"""
    leaked = [n for n in REFUSED if n in _specs()]
    assert not leaked, "★ 夹带了不做的东西: %r" % (leaked,)


def test_no_bare_coordinates():
    specs = _specs()
    for n in REFUSED:                                            # 占位：确保变量被用到
        assert n not in specs
    for name, s in specs.items():
        if getattr(s, "module", "") not in ("sw_review", "sw_feature_readback",
                                            "sw_import_mesh_reference", "sw_preflight",
                                            "sw_sketch_dimensions", "sw_misumi"):
            continue
        for p in (getattr(s, "params", None) or []):
            assert p.name.lower() not in ("x", "y", "z", "point", "coord", "center", "origin"), \
                (name, p.name)
