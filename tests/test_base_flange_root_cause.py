"""★ spec 277：**族现象的真因** —— ★ 草图几何被 `mm()` 缩了 1000 倍（★ 并证伪 276 的假设）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/_probe277_mm_geometry.txt（★ 决定性读数原文）· output/_probe277_instrumented.txt（★ 仪表化 A/B）
#         scripts/sw_part.py:560-565（★ `sketch_line` **逐字** `x1 * _MM_TO_M` ⇒ 单位是**毫米**）
#         tests/solidworks_sheet_metal_regression.py:74-90（★ 它传 `mm(30)` = **0.03 毫米**）
#         docs/known-facts.md 事实 34（2026-10-01 成功）· 事实 73（★ 该模块单位是毫米）· 事实 209（★ 长度按文档单位）
# 定位:   ★ 262/263/264/265 四轮都把这当**产品回归**；★ 本轮实测 ⇒ ★★ **是**测试夹具**的缺陷**。
# 官方依据: 官方示例的草图是 0.14 m（140 mm）量级 ⇒ ★ 与本仓夹具差 **1000 倍**
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   只读（★ 真机读数由探针产出；★ 本文件不连 COM）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#: ★★★ **真机读数**（SolidWorks **34.4.1** · 2026-10-10 · ★ 走 `sw_guard` · ★ 临时零件用完关闭不保存）。
#:   ★ 三臂**只改一个变量**（★ 几何尺寸）。
ARMS = {
    "① 几何 30mm + 厚 2.0": (False, "无法添加此圆角，因为指定的半径值将会删除其中一个实体"),
    "② 几何 30mm + 厚 0.002": (True, "基体-法兰1"),
    "③ 几何 0.03mm（回归现状）": (False, "所选的草图对此操作无效"),
}
#: ★★★ **276 的假设 ② 被证伪**：★ 仪表化 A/B —— ★ 「关草图前先 `ClearSelection2`」**两臂结果一致**。
FALSIFIED = {
    "claim": "官方靠 `InsertSketch(True)` 关草图后「草图特征**自带选中**」",
    "arm1_repo": "选中 1 个（`草图1`）",
    "arm2_official": "选中 1 个（`草图1`）",     #: ★ 关草图后是 0 个 ⇒ ★ 必须靠 `_ensure_sketch_selected` 重选
    "selected_after_close": 0,                  #: ★★ 关草图后 `GetSelectedObject6(1,-1)` ⇒ **None**
    "both_arms_same": True,                     #: ★ 两臂**同样失败** ⇒ ★ 这一步**不影响**
}
#: ★★ **已排除**（★ 真机逐条量过）。
RULED_OUT = {
    "草图未关": "`ActiveSketch` ⇒ **None**（★ 确实关了）",
    "选错对象": "选中**恰好 1 个** · `'草图1'` · type=CDispatch（★ 就是草图特征）",
    "平面": "`Front Plane` 与 `Top Plane` **都失败**",
    "厚度/深度单位": "★ 米（`mm(2.0)`）与**文档单位**（`2.0`）**都失败**（★ 只是**错误信息不同**）",
}


def _uses_mm_to_m(src: str) -> bool:
    """★ 回源码核：`sketch_line` 的体里**确实**乘了 `_MM_TO_M` ⇒ ★ 它的单位是**毫米**。"""
    m = re.search(r"def sketch_line\(.*?\n(.*?)(?=\ndef |\Z)", src, re.S)
    return bool(m) and "_MM_TO_M" in m.group(1)


def _fixture_passes_mm_values(src: str) -> bool:
    """★ 回源码核：★ 回归夹具给 `sketch_line` 的实参**已是裸毫米**（★ 规格 278 订正后）。

    ★★★ **2026-10-10（规格 301）订正：判据**反转**（★ 随规格 278）** ——
      ★★ **原文**（已作废）逐字是：
        「★ 回源码核：回归夹具给 `sketch_line` 的实参**带 `mm(`** ⇒ ★ 它传的是 **0.03 毫米**。」
        （★ 正则 `sketch_line\\(model,\\s*-mm\\(`）
      ★★★ **而规格 278 把那个 bug **修好了** —— 它逐字记：
        「★★★ **维护回归跑绿了** —— ★ 只改夹具的 **3 行**草图几何（`mm(30)` ⇒ **裸毫米** `30`）」
        ★ 且夹具自己写了订正注释：「⚠ 原写 `mm(30)` ⇒ ★ `sketch_line` 把它当 **0.03 毫米**」。
      ★★ **⇒ 本条判据改成守「**已订正**」**：★ 存在**裸毫米**的 `sketch_line` 调用、
        ★ 且**不许**再有被 `mm()` 缩 1000 倍的写法 ✓
      ★★ **依据**（`MEMORY.md` 规则 28）：「改实现前先搜『有没有测试钉住旧行为』——
        ★ 不同步改就等于**在断言错的东西**」✓
    """
    #: ★ 正例：★ 存在**裸毫米**的 `sketch_line` 调用（★ 规格 278 后的形态）
    bare = re.search(r"sketch_line\(model,\s*-?\d", src)
    #: ★ 负例：★ **不许**再有 `sketch_line(model, -mm(` 这种**被 mm() 缩了 1000 倍**的写法
    scaled = re.search(r"sketch_line\(model,\s*-mm\(", src)
    return bool(bare) and not scaled


def _failures(arms, falsified, ruled_out, uses_mm_to_m, fixture_mm) -> list[str]:
    """★ 纯函数：① 三臂三态齐；② 假设被证伪；③ 排除表非空；④ 两处回源码核都过。"""
    bad: list[str] = []
    if len(arms) != 3:
        bad.append("三臂不齐（★ 应 3 个）")
    ok_arms = [k for k, (ok, _d) in arms.items() if ok]
    if len(ok_arms) != 1:
        bad.append("**恰好一臂**成功才对，实测 %d 个：%s" % (len(ok_arms), ok_arms))
    elif not ok_arms[0].startswith("②"):
        bad.append("成功的那臂不是 ②：%s" % ok_arms)
    if arms.get("③ 几何 0.03mm（回归现状）", (True,))[0]:
        bad.append("★ 对照组（几何 0.03mm）**不该**成功")
    if not falsified.get("both_arms_same"):
        bad.append("★ 两臂应**同样失败**（★ 这才证伪 276 的假设）")
    if falsified.get("selected_after_close") != 0:
        bad.append("★ 关草图后应为 **0 个**选中")
    if not ruled_out:
        bad.append("排除表为空 ⇒ 检查量为 0")
    if not uses_mm_to_m:
        bad.append("★ 回源码核失败：`sketch_line` 体里没找到 `_MM_TO_M` ⇒ 单位结论失去依据")
    if not fixture_mm:
        bad.append("★ 回源码核失败：夹具没给 `sketch_line` 传 `mm(...)` ⇒ 真因结论失去依据")
    return bad


# ── ① ★★★ 三臂三态：★ **只有「毫米几何」那一臂成功** ──────────────
def test_only_the_millimetre_geometry_arm_succeeds():
    """★★★ 真机（34.4.1）：★ 几何 **30 mm** ⇒ **成功**（`'基体-法兰1'`）；
    ★ 几何 **0.03 mm**（回归现状）⇒ 「**所选的草图对此操作无效**」。
    """
    assert ARMS["② 几何 30mm + 厚 0.002"][0] is True, "★ 毫米几何那一臂应成功"
    assert ARMS["③ 几何 0.03mm（回归现状）"][0] is False
    assert "所选的草图对此操作无效" in ARMS["③ 几何 0.03mm（回归现状）"][1]
    assert "无法添加此圆角" in ARMS["① 几何 30mm + 厚 2.0"][1], \
        "★ 臂①的错误应是**圆角**那条（★ 复现事实 209 的单位语义）"


# ── ② ★★★ 276 的假设 ② **被证伪** ─────────────────────────────────
def test_276_hypothesis_is_falsified():
    """★★★ 仪表化 A/B：★ 「关草图前先 `ClearSelection2`」**两臂结果一致**；
    ★ 且关草图后 `GetSelectedObject6(1,-1)` ⇒ **None**（★ 选中个数 **0**）
    ⇒ ★★ **「官方靠自带选中」在本机不成立** ⇒ ★ `_ensure_sketch_selected` **本来就是必需的**。
    """
    assert FALSIFIED["both_arms_same"] is True, "★ 两臂必须一致"
    assert FALSIFIED["selected_after_close"] == 0, "★ 关草图后应为 0 个选中"
    assert FALSIFIED["arm1_repo"] == FALSIFIED["arm2_official"], "★ 两臂选中的东西应一样"


# ── ③ ★★ 四条已被**真机排除** ─────────────────────────────────────
def test_four_candidates_are_ruled_out():
    """★★ 真机逐条量过：★ 草图**确实关了** · ★ 选中的**就是**草图特征（恰好 1 个）·
    ★ `Front`/`Top` **都失败** · ★ 米制与文档单位**都失败**（★ 只是错误信息不同）。
    """
    assert len(RULED_OUT) == 4, "排除表应 4 条"
    assert "ActiveSketch" in RULED_OUT["草图未关"]
    assert "恰好 1 个" in RULED_OUT["选错对象"]


# ── ④ ★★★ 两处**回源码核**（★ 不靠手抄 · ★ 铁律 6） ────────────────
def test_source_checks_prove_the_unit_mismatch():
    """★★★ ① `sw_part.sketch_line` 的体里**确实**乘 `_MM_TO_M` ⇒ ★ 单位是**毫米**；
    ★ ② 回归夹具**确实**给 `sketch_line` 传 `mm(...)` ⇒ ★ 传进去的是 **0.03**（★ 差 **1000 倍**）。
    """
    src_part = (ROOT / "scripts" / "sw_part.py").read_text(encoding="utf-8", errors="replace")
    assert _uses_mm_to_m(src_part), "`sketch_line` 的单位结论失去依据"
    src_fix = (ROOT / "tests" / "solidworks_sheet_metal_regression.py").read_text(
        encoding="utf-8", errors="replace")
    assert _fixture_passes_mm_values(src_fix), "夹具的 `mm(...)` 用法不见了"


# ── ⑤ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 五组负例：① 三臂不齐；② 两臂都成功；③ 对照组也成功；④ 假设未被证伪；⑤ 回源码核失败。"""
    args = (ARMS, FALSIFIED, RULED_OUT, True, True)
    assert not _failures(*args), "正常读数被判红 ⇒ 判据过严"
    assert _failures({"a": (True, "x")}, FALSIFIED, RULED_OUT, True, True), "三臂不齐却未判出"
    assert _failures(dict(ARMS, **{"① 几何 30mm + 厚 2.0": (True, "x")}), FALSIFIED, RULED_OUT,
                     True, True), "两臂都成功却未判出"
    assert _failures(dict(ARMS, **{"③ 几何 0.03mm（回归现状）": (True, "x")}), FALSIFIED, RULED_OUT,
                     True, True), "对照组也成功却未判出"
    assert _failures(ARMS, dict(FALSIFIED, both_arms_same=False), RULED_OUT, True, True), \
        "假设未被证伪却未判出"
    assert _failures(ARMS, FALSIFIED, RULED_OUT, False, True), "回源码核失败却未判出"
