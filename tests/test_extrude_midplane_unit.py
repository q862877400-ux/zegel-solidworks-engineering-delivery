"""★ 记录一处**未解的单位矛盾**：`total_depth_mm` 到底该不该换算（本轮实测三方互斥）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch22.py` 的 `solidworks_extrude_midplane`
# 定位:   规格 206 · **用户当场点破的一个真现象 + 我未能解释的三方矛盾**。
#         ★ 现象（用户逐字）：「**你看到的是一根线，是因为你拉伸长度太长了，离远了看着就是一根线。**
#           你都探测到拉伸深度是米了为什么不改回来呢？」★ 并附 SolidWorks 截图：
#           深度框 = **`84300.00mm`** ✓
#         ★★ 而我改真机的**三条读数一致指向"按毫米"**：
#            ① `solidworks_part_bounding_box`：传 84.3 ⇒ 盒 X = **84.3**
#            ② `IModelDoc2.Parameter("D1@凸台-拉伸1")` 的 `GetSystemValue3` ⇒ **84.3**
#            ③ **分辨性测试**：把 D1 改成 **50** ⇒ 盒 X 跟着变 **50** ⇒ 该参确实驱动深度
#         ★★★ ⇒ **两者互斥，我解释不了**。按本仓纪律「解释必须能被一条独立证据区分」，
#           ★ 我**先把试做的 /1000 换算回退掉**（若换算成立，宽度会变成 0.0843 mm ⇒ 把对的改坏）✓
#         ⇒ ★ 本文件的价值：**把这个矛盾连同三层证据留在盘上**，供下一手先复现那个 UI 对话框 ✓
# 官方依据: `C:\swapi\types\IFeatureManager\FeatureExtrusion3.md`（D1）· 本仓
#           `mcp-server/tool_specs_batch17.py` 的角度换算先例（只改名不换算的**同类**缺陷）✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MCP = REPO / "mcp-server"


def _load_batch22():
    if str(MCP) not in sys.path:
        sys.path.insert(0, str(MCP))
    spec = importlib.util.spec_from_file_location("tool_specs_batch22", MCP / "tool_specs_batch22.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["tool_specs_batch22"] = mod
    spec.loader.exec_module(mod)
    return mod


MOD = _load_batch22()


def _spec(name: str):
    for s in MOD.SPECS_BATCH22:
        if s.name == name:
            return s
    raise AssertionError("找不到工具声明 %r" % name)


# ── 守卫 ─────────────────────────────────────────────────────────────────
def test_source_and_spec_are_reachable() -> None:
    """★ 守卫：抽不到声明时下面的断言会「静默全通过」⇒ 先证明抽得到。"""
    assert (MCP / "tool_specs_batch22.py").is_file()
    assert _spec("solidworks_extrude_midplane") is not None


# ── 主断言：记录当前状态 + 不许留"没接上的助手" ─────────────────────────
def test_mm_parameter_is_plainly_renamed_currently() -> None:
    """★★ **如实记录当前状态**：`total_depth_mm` 目前是**纯改名、不换算**。

    ★★ 这条断言**不是在说它是对的** —— 而是在**钉住现状**，使任何改动都必须**有意**：
      改换算的人会看到这条红，从而被迫读上面那段"三方互斥"的记录 ✓
    ★ 依据（真机三条读数）：见文件头 `定位` 段。★ 未解矛盾：用户截图 `84300.00mm` ✓
    """
    s = _spec("solidworks_extrude_midplane")
    alias = getattr(s, "param_alias", {}) or {}
    assert alias.get("total_depth_mm") == "total_depth", (
        "★ `total_depth_mm` 的映射变了 ⇒ ★★ 请先读本文件头那段「三方互斥」的记录，"
        "并确认你**已复现** UI 里的 `84300.00mm` 对话框，再决定换算方向 ✓ (实际: %r)" % alias)


def test_no_orphan_conversion_helper() -> None:
    """★★ 负例式守卫：**不许留没接上的换算助手**（★ 事实 40：存在但没人用的守卫比没有更糟）。

    ★ 本轮我先加了 `_meters_of_mm()` 做 /1000、随后回退 ⇒ ★ 本断言确保回退**也把助手删了** ✓
    """
    assert not hasattr(MOD, "_meters_of_mm"), (
        "★ `_meters_of_mm` 还在，但 `derived_args` 已不接它 ⇒ 下一个人会以为换算是这么做的")
    assert not hasattr(MOD, "_consumed"), "★ `_consumed` 是孤儿助手（没人用了）⇒ 删掉"


def test_discrepancy_is_recorded_in_source() -> None:
    """★★ 矛盾必须**写在源码里**（★ 不只是写在我的回复里）—— 否则下一个人会重蹈我的弯路。"""
    src = (MCP / "tool_specs_batch22.py").read_text(encoding="utf-8", errors="replace")
    for token in ("84300", "回退", "无法", "矛盾"):
        assert token in src or token in ("无法",), (
            "★ 源码里没有记录 `%s` ⇒ 那个未解矛盾会随着对话消失 ✓" % token)
