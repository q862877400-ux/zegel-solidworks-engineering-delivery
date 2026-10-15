"""★ 批次 91 的契约测试：弹窗护栏 / 焦点 / 倒角几何 / 曲面运行时（11 个）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch91.py` · `scripts/sw_gui_modal.py` ·
#         `scripts/sw_gui_focus.py` · `scripts/sw_chamfer_geometry.py` · `scripts/sw_surface.py`
# 定位:   规格 `specs/205-tool-ramp/` 的 SC-002/SC-004；★ 本批四条契约：
#         ① 11 个都能解析到真实函数；② ★ **没有裸坐标**（规则 3）——
#            ★★ 本批有 GUI 工具，**必须把"窗口句柄"与"几何坐标"分开**：
#            句柄参数叫 `main_hwnd` / `hwnd` / `want`（★ 不是 x/y/z/point）✓
#         ③ ★ 「给解析器读的参数」用 `param_alias=None`；④ ★ 规则 2 的改名要配 `param_alias` ✓
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
import tool_specs_batch91 as b91                              # noqa: E402

EXPECTED = 8  # ★ 2026-10-10：11 → 8 —— ★ 业主架构指令移出 3 个**倒角几何方法**
# ★ 判据：★「那个数字错了，回读能不能查出来」⇒ ★ 不能 ⇒ 方法 ✗
# ★ 原件在 `archive/inherited-methods/scripts/sw_chamfer_geometry.py`（只搬不删）
#: ★ 窗口句柄类参数（★ 句柄**不是**几何坐标 ⇒ 不违反规则 3；★ 但要与 x/y/z 明确区分）
HWND_PARAMS = ("main_hwnd", "hwnd", "want")
GEOM = ("x", "y", "z", "point", "coord", "center", "origin")


def test_batch91_registered():
    t = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    assert '"tool_specs_batch91"' in t


def test_eight_specs_declared_and_resolve():
    assert len(b91.SPECS_BATCH91) == EXPECTED, len(b91.SPECS_BATCH91)
    for s in b91.SPECS_BATCH91:
        m = importlib.import_module("scripts.%s" % s.module)
        fn = getattr(m, s.function, None)
        assert callable(fn), "%s → %s.%s" % (s.name, s.module, s.function)
        #: ★ 本批全部 `inject=""`（首参是标量或句柄）⇒ 目标函数**不应**有注入形参差异
        assert getattr(s, "inject", "") == "", (s.name, getattr(s, "inject", ""))


def test_no_geometric_coordinates_but_handles_are_allowed():
    """★★ 规则 3 的要害是**几何坐标**；★ 本批的 GUI 工具收的是**窗口句柄** ⇒ 两者必须分得清 ✓"""
    for s in b91.SPECS_BATCH91:
        for p in (getattr(s, "params", None) or []):
            low = p.name.lower()
            assert low not in GEOM, "★ 收了几何坐标: %s.%s" % (s.name, p.name)
            if low in HWND_PARAMS:
                #: ★ 句柄类参数的说明里要**明说它不是坐标**（★ 否则读者会误判成违反规则 3）
                assert "句柄" in (p.description or ""), (s.name, p.name)


def test_renamed_param_has_alias():
    """★ 规则 2 的改名（`settle` → `settle_seconds`）必须配 `param_alias` 指回真形参 ✓"""
    s = next(x for x in b91.SPECS_BATCH91 if x.name == "solidworks_gui_ensure_focus")
    alias = getattr(s, "param_alias", None) or {}
    assert alias.get("settle_seconds") == "settle", alias


#: ★★★ 2026-10-10 **`test_missing_required_param_was_added` 已移除**（★ 业主架构指令）：
#:   ★ 那个测试守的是 `solidworks_chamfer_volume_report` 的必填形参 ——
#:   ★★ 而**那个工具已按业主指令移出**（★ 倒角体积公式 = **方法**）⇒
#:     ★ 判据守一个不存在的东西 ⇒ ★ **跟着走** ✓
#:   ★ 原件：★ `archive/inherited-methods/`（★ 只搬不删）
#:   ★★ **不是丢判据** —— ★ 是那个判据的**被测对象合法移出**了（★ 判据本身没错）✓
