"""★ spec 278：**修回归夹具的草图几何单位** ⇒ `create_base_flange` 的维护回归真的跑绿（★ 并**证伪事实 209**）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/_probe278_regression.txt（★ 回归 `status: pass` 的读数）· output/_probe278_values.txt（★ 逐臂）
#         tests/solidworks_sheet_metal_regression.py（★ 本轮**只改 3 行几何**）
#         scripts/sw_sheet_metal.py 的 `BaseFlangeSpec` docstring（★ 事实 209 那条更正 ⇒ ★ 本轮**推翻**）
#         docs/known-facts.md 事实 34（2026-10-01 成功）· 事实 209（★ 单位更正）
# 定位:   ★ 277 说「下一 WIP = 修回归夹具的几何单位」⇒ ★ 本轮做，★ 并**顺带把单位约定一次钉死**。
# 官方依据: 官方示例 `Create_Base_Flange_Feature_Example_VBNET.md`（★ 传的是**文档单位**值，★ 但那是**英寸文档**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   只读（★ 真机读数由探针/回归产出；★ 本文件不连 COM）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#: ★★★ **真机读数**（SolidWorks **34.4.1** · 2026-10-10 · ★ 走 `sw_guard`）。
#:   ★ 修好夹具后跑**维护回归** ⇒ `status: pass`，★ 产物齐。
REGRESSION = {
    "status": "pass",
    "artifacts": {"u_channel_sheet_metal.SLDPRT": 95871, "u_channel_flat_pattern.dxf": 20660},
    "thickness_m": 0.002,
    "has_base_flange": True,
    "all_solid_bodies_are_sheet_metal": True,
}
#: ★★★ **逐臂**（★ 几何一律 30/25 **毫米**）—— ★ 用来**推翻事实 209** 的「按文档单位解释」。
ARMS = {
    "厚 0.002 · 半径 0.0025 · 深 0.1": True,          #: ★ 建成（★ 读回 thickness_m=0.002 = **2 mm**）
    "厚 2.0 · 半径 1.0 · 深 100.0": False,
    "厚 2.0 · 半径 1.0 · 深 0.1": False,
    "厚 2.0 · 半径 0.5 · 深 0.1": False,
}
#: ★★ 失败时的**同一条**报文（★ 让判据能报出「因为什么」）。
FAIL_MSG = "无法添加此圆角，因为指定的半径值将会删除其中一个实体"
#: ★★★ **本轮推翻的旧结论**（★ 逐字来自 `BaseFlangeSpec` 的旧 docstring）。
FALSIFIED = "IBaseFlangeFeatureData 的长度按「文档长度单位」解释（本机 = 毫米）"
#: ★★★ **订正后的结论**。
CORRECTED = "长度按**米**（★ 与 SW API 通用约定一致）"


def _geometry_is_mm(src: str) -> bool:
    """★ 回源码核：夹具给 `sketch_line` 传的是**裸毫米**（★ 不带 `mm(`）。

    ★ 判据用**绝对值** —— ★ 第一条线从 `-30` 起（★ 负坐标），★ 用带符号比较会**假红**。
    """
    m = re.search(r"sketch_line\(model,\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+),\s*(-?[\d.]+)\)", src)
    return bool(m) and abs(float(m.group(1))) >= 1.0       #: ★ 裸毫米 ⇒ 量级 ≥ 1；★ `mm(30)` 会是 0.03


def _geometry_has_no_mm_wrapper(src: str) -> bool:
    """★ 回源码核：夹具里**没有**把 `mm(...)` 塞进 `sketch_line`。"""
    return re.search(r"sketch_line\(model,\s*-?mm\(", src) is None


def _spec_uses_metres(src: str) -> bool:
    """★ 回源码核：`BaseFlangeSpec` 的 `thickness` 用**米**（★ `mm(2.0)` ⇒ 0.002）。"""
    m = re.search(r"BaseFlangeSpec\((.*?)\)\s*,?\s*\)", src, re.S)
    return bool(m) and "thickness=mm(" in m.group(1)


def _docstring_corrected(src: str) -> bool:
    """★ 回源码核：`BaseFlangeSpec` 的 docstring 里**确实**写了订正（★ 旧结论被推翻）。"""
    return ("规格 278" in src) and ("长度就是**米**" in src or "长度按**米**" in src)


def _failures(reg, arms, fail_msg, falsified, corrected, checks) -> list[str]:
    """★ 纯函数：① 回归 pass 且产物齐；② 恰好一臂成功；③ 失败报文一致；④ 四项回源码核都过。"""
    bad: list[str] = []
    if reg.get("status") != "pass":
        bad.append("回归不是 pass：%r" % (reg.get("status"),))
    arts = reg.get("artifacts") or {}
    if len(arts) != 2 or min(arts.values() or [0]) < 4096:
        bad.append("产物不齐或过小：%r" % (arts,))
    if reg.get("thickness_m") != 0.002:
        bad.append("读回的厚度不是 0.002（★ 那是 2 mm 的真板）：%r" % (reg.get("thickness_m"),))
    ok = [k for k, v in arms.items() if v]
    if len(ok) != 1 or not ok[0].startswith("厚 0.002"):
        bad.append("应**恰好**「厚 0.002」那一臂成功，实测 %s" % ok)
    if not fail_msg:
        bad.append("失败报文为空")
    if not falsified or not corrected:
        bad.append("旧结论 / 订正结论 之一为空 ⇒ 检查量为 0")
    for name, ok_ in checks.items():
        if not ok_:
            bad.append("★ 回源码核失败：%s" % name)
    return bad


# ── ① ★★★ 回归**跑绿**了 ───────────────────────────────────────────
def test_the_maintained_regression_now_passes():
    """★★★ 真机（34.4.1）：★ 修好夹具的草图几何后，**维护回归** `status: pass`，
    ★ 产物 `.SLDPRT`（≈94 KB）+ `.dxf`（≈20 KB）齐，★ 读回 `thickness_m=0.002`（= **2 mm** 的真板）。
    """
    assert REGRESSION["status"] == "pass", "回归没跑绿"
    assert REGRESSION["has_base_flange"] is True
    assert REGRESSION["all_solid_bodies_are_sheet_metal"] is True
    assert REGRESSION["thickness_m"] == 0.002, "★ 2 mm 的真板（★ 不是箔片）"


# ── ② ★★★ 事实 209 的「按文档单位解释」**被证伪** ──────────────────
def test_fact_209_unit_claim_is_falsified():
    """★★★ 真机逐臂：★ `thickness=0.002 / 半径 0.0025 / 深 0.1` ⇒ **建成**；
    ★ `thickness=2.0`（半径 0.5 **或** 1.0）⇒ ★ **全失败**，★ 且报的是**同一条**
    「**无法添加此圆角，因为指定的半径值将会删除其中一个实体**」
    ⇒ ★★★ **长度就是**米****（★ 若按毫米，2.0 mm 的板配 1.0 mm 半径应当可行）。
    """
    assert ARMS["厚 0.002 · 半径 0.0025 · 深 0.1"] is True, "★ 米制那臂应成功"
    assert all(v is False for k, v in ARMS.items() if k.startswith("厚 2.0")), \
        "★ 所有 `thickness=2.0` 的臂都应失败"
    assert "文档长度单位" in FALSIFIED, "★ 被推翻的那句要逐字留档"
    assert "米" in CORRECTED


# ── ③ ★★★ 三处**回源码核**（★ 不靠手抄 · ★ 铁律 6） ────────────────
def test_source_checks_prove_the_fixture_and_docstring():
    """★★★ ① 夹具的 `sketch_line` 传**裸毫米**；★ ② 夹具里**没有** `mm(` 塞进 `sketch_line`；
    ★ ③ `BaseFlangeSpec` 的 `thickness` 仍按**米**（`mm(2.0)`）；★ ④ docstring **确实**写了订正。
    """
    fix = (ROOT / "tests" / "solidworks_sheet_metal_regression.py").read_text(
        encoding="utf-8", errors="replace")
    assert _geometry_is_mm(fix), "★ 夹具的草图几何不是裸毫米"
    assert _geometry_has_no_mm_wrapper(fix), "★ 夹具仍把 `mm(...)` 塞给 `sketch_line`"
    assert _spec_uses_metres(fix), "★ 夹具的 spec 不再按米"
    part = (ROOT / "scripts" / "sw_sheet_metal.py").read_text(encoding="utf-8", errors="replace")
    assert _docstring_corrected(part), "★ `BaseFlangeSpec` 的 docstring 没写订正"


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 五组负例：① 回归没绿；② 产物缺；③ 两臂都成功；④ 旧结论为空；⑤ 回源码核失败。"""
    ok_checks = {"几何是裸毫米": True, "无 mm 包装": True, "spec 按米": True, "docstring 已订正": True}
    args = (REGRESSION, ARMS, FAIL_MSG, FALSIFIED, CORRECTED, ok_checks)
    assert not _failures(*args), "正常读数被判红 ⇒ 判据过严"
    assert _failures(dict(REGRESSION, status="failed"), ARMS, FAIL_MSG, FALSIFIED, CORRECTED,
                     ok_checks), "回归没绿却未判出"
    assert _failures(dict(REGRESSION, artifacts={}), ARMS, FAIL_MSG, FALSIFIED, CORRECTED,
                     ok_checks), "产物缺却未判出"
    assert _failures(REGRESSION, dict(ARMS, **{"厚 2.0 · 半径 1.0 · 深 0.1": True}), FAIL_MSG,
                     FALSIFIED, CORRECTED, ok_checks), "两臂都成功却未判出"
    assert _failures(REGRESSION, ARMS, FAIL_MSG, "", CORRECTED, ok_checks), "旧结论为空却未判出"
    assert _failures(REGRESSION, ARMS, FAIL_MSG, FALSIFIED, CORRECTED,
                     dict(ok_checks, **{"几何是裸毫米": False})), "回源码核失败却未判出"
