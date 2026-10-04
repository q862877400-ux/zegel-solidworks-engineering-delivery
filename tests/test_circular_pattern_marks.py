"""★ T2-4 交集法的产物：把「圆阵前置」写成静态断言（★ 含负例）—— 全部依据来自官方页原文。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tests/test_circular_pattern_marks.py
# 定位:   规格 206 / **T2-4 的第 4 个样板**（前三个见事实 549/550/551）——
#         ★★ 与前三个的**区别**：这一个**来自那 102 条可机检清单**（★ 交集法筛出来的
#         **唯一**一个候选），而不是只来自本仓过去错误笔记 ⇒ ★ 它补上了
#         `docs/recon-206/t2-sample-vs-checkable.md` §三 记下的那半步缺口 ✓
# 官方依据（★ 逐字，全部从盘上查到，不凭记忆）：
#   · `C:\swapi\types\IFeatureManager\FeatureCircularPattern4.md` 的 `## Remarks` mark 表逐字：
#       「- **1** to mark the direction axis」·「- **4** to mark the features to pattern」
#     ⇒ ★ 期望：轴 = 1、被阵列的特征 = 4 ✓
#   · 同页 `## Parameters` 逐字：`Number`（★ 实例数，含原件）· `Spacing`
#       「Spacing between each instance of the circular pattern; total angle in radians
#        **if EqualSpacing is true**」
#     ⇒ ★ 期望：第 1 实参是 count、第 2 实参是**弧度角**（★ 见事实 517：官方"吃米"不普遍成立，
#       故本测试**只判顺序与 mark**，不判单位换算 —— ★ 单位那条另有 MCP 面 DocSpec 守）✓
#   · `C:\swapi\examples\Create_Circular_Pattern_Example_VB.md` 逐字（★ 全部四条）：
#       `SelectByID2("Cut-Extrude1", "BODYFEATURE", …, False, 4, …)`   ← ★ **先**，mark 4、append=False
#       `SelectByID2("", "EDGE",           …, True,  1, …)`            ← ★ **后**，mark 1、append=True
#       `SelectByID2("Fillet1",     "BODYFEATURE", …, True, 4, …)`    ← ★ 再追加一个特征，mark 4
#       `FeatureCircularPattern4(6, 0.174532925199434, True, "NULL", False, False, True)`
#     ⇒ ★★ **示例的序是「先特征、后轴」** ✓
#   · ★★★ **而我起初写反了**（★ 本轮真实发生，记在这里当反例）：
#       我按「同仓旋转那家要轴先于轮廓」**类推**出「圆阵也要轴先」⇒ ★ 断言**当场红**
#       ⇒ ★ 逐字核官方示例后发现**反了** ⇒ ★★ 定则（本规格第 12 条）：
#       **「同一族里一个成员的顺序」不能类推到另一个成员** —— 顺序要么读**该成员自己的**示例，
#       要么就别断言（★ 这正是「判据不许建立在类推上」）✓
#   · 同页 Remarks 另有一句逐字：「Using [[IModelDocExtension::SelectByID2]] to select features and
#     components, **ordered selection of the features and components is required**」
#     ⇒ ★★ **「不算什么」**：这句约束的是**特征与特征之间**的次序，
#       ★ 它**没有**规定「特征 vs 轴」谁先；★ 后者只能从示例读（★ 示例给的就是先特征）✓
#   · 我方实际：`circular_pattern` 先 `BODYFEATURE(mark=4)`、后 `AXIS(mark=1)` ⇒ ★ **与示例一致** ✓
# 依据:   `scripts/sw_part.py` 的 `circular_pattern`（L1428-1443）·
#         `mcp-server/tool_specs_batch17.py`（`solidworks_circular_pattern` 的 `angle_deg`）·
#         事实 8（mark 回读计数为准）· 事实 62（负例是唯一证明）· 事实 550（交集法）✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "scripts" / "sw_part.py"

#: ★★★ 期望值 —— 官方 Remarks mark 表（★ 逐字见上方来源块）
AXIS_MARK = 1
FEATURE_MARK = 4


def circular_body(text: str) -> str:
    """★ 取 `circular_pattern` 的函数体（★ 到下一个顶层 `def ` 为止）—— ★ 不做全文件匹配。

    ★★ 为什么必须限定函数体（事实 51）：本文件里 `_select_by_id` 有几十处调用，
      ★ 全文件匹配会把**别的特征**的 mark 也吞进来 ⇒ 假阳性 ✓
    """
    m = re.search(r"^def circular_pattern\(.*?\n(?=^def |\Z)", text, re.S | re.M)
    return m.group(0) if m else ""


def selections(body: str) -> list[tuple[str, str, int | None]]:
    """★ 抽出 `_select_by_id(...)` 调用序列 ⇒ `[(实体名, 类型, mark), …]`（★ 顺序保留）。"""
    out = []
    for call in re.findall(r"_select_by_id\((.*?)\)\s*$", body, re.M):
        parts = [p.strip() for p in call.split(",")]
        if len(parts) < 3:
            continue
        mm = re.search(r"mark\s*=\s*(\d+)", call)
        out.append((parts[1], parts[2].strip('"\''), int(mm.group(1)) if mm else None))
    return out


def call_args(body: str) -> list[str]:
    """★ 抽 `FeatureCircularPattern4(...)` 的实参（★ 按书写的顺序）。"""
    m = re.search(r"FeatureCircularPattern4\(\s*(.*?)\s*\)", body, re.S)
    if not m:
        return []
    raw, parts, depth, cur = m.group(1), [], 0, ""
    for ch in raw:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur.strip())
    return parts


# ── 守卫（★ 抽不出来就必须失败，别让下面的断言静默全通过）─────────────────
def test_source_is_reachable():
    """★ 守卫：源文件 / 函数体 / 选择序列 / 实参 四样都要真抽到。"""
    assert SRC.is_file(), "找不到 %s" % SRC
    body = circular_body(SRC.read_text(encoding="utf-8", errors="replace"))
    assert body, "抽不到 circular_pattern 的函数体"
    assert selections(body), "函数体里抽不到 _select_by_id 调用"
    assert call_args(body), "函数体里抽不到 FeatureCircularPattern4 的实参"


# ── 主断言 ①：mark（★ 官方 Remarks 表）──────────────────────────────────
def test_marks_match_official_remarks():
    """★★ 被阵列的特征 **mark=4**、方向轴 **mark=1**（★ 官方 Remarks 的 mark 表逐字）。"""
    body = circular_body(SRC.read_text(encoding="utf-8", errors="replace"))
    got = selections(body)
    marks = {kind: mark for _name, kind, mark in got}
    assert marks.get("BODYFEATURE") == FEATURE_MARK, (
        "被阵列特征的 mark 与官方 Remarks 不符: %r（★ 官方逐字「4 to mark the features to pattern」）" % got)
    assert marks.get("AXIS") == AXIS_MARK, (
        "方向轴的 mark 与官方 Remarks 不符: %r（★ 官方逐字「1 to mark the direction axis」）" % got)


# ── 主断言 ②：选区顺序（★ 官方示例的调用序）────────────────────────────
def test_feature_is_selected_before_axis():
    """★★ 官方示例的序：**先选种子特征（mark 4）、后选方向轴（mark 1）**。

    ★★ 这条断言的来历（★ 写下来免得下一个人再类推一次）：我**起初断言的是反的**
      （★ 按同仓「旋转：轴必须先于轮廓」类推）⇒ ★ **测试当场红** ⇒ 逐字核官方示例后
      ★★ 发现**示例就是先特征**、而**我方代码与示例一致** ⇒ ★ 我把断言改成示例的序 ✓
    ★★★ **⇒ 它守的不是"我的直觉"，而是"官方示例的序"** —— 而这正是 T2-4 要的东西：
      ★ 把**外部依据**固化成断言，而不是把**我的类推**固化进去（★ 事实 62 的用法要小心）✓
    ★★ 负例见 `test_negative_reversed_order_is_detected` ✓
    """
    body = circular_body(SRC.read_text(encoding="utf-8", errors="replace"))
    kinds = [kind for _name, kind, _mark in selections(body)]
    assert kinds.index("BODYFEATURE") < kinds.index("AXIS"), (
        "选区顺序与官方示例不符: %r（★ 示例：先 Cut-Extrude1/BODYFEATURE mark 4、"
        "后 EDGE mark 1）" % kinds)


# ── 主断言 ③：实参顺序（★ 官方 Parameters 的名单）──────────────────────
def test_first_two_args_are_count_then_angle():
    """★★ 第 1 实参 = 实例数、第 2 实参 = 角度（★ 官方 Parameters 的 `Number` / `Spacing`）。

    ★★ 这条是**真错过的**那一类：本仓 `linear_pattern` 曾经「前四项顺序颠倒 ⇒ 必然失败」
      （★ 见 `scripts/sw_part.py` 里 `linear_pattern` 的来源块逐字）⇒
      ★ 顺序类错在本仓**不止一次**（★ 事实 528 那一族）✓
    """
    body = circular_body(SRC.read_text(encoding="utf-8", errors="replace"))
    args = call_args(body)
    assert len(args) >= 2, "实参数 < 2: %r" % args
    assert "count" in args[0], "第 1 实参应是**实例数** count，实际是 %r（★ 官方 `Number`）" % args[0]
    assert "angle" in args[1], "第 2 实参应是**角度**（弧度），实际是 %r（★ 官方 `Spacing`）" % args[1]


# ── 负例（★ 事实 62：没有负例的守卫不算守卫）────────────────────────────
def test_negative_reversed_marks_are_detected():
    """★★ 负例①：**mark 调反** ⇒ 判据必须报出来。"""
    fake = ('def circular_pattern(model, feature_name, axis_name):\n'
            '    _select_by_id(model.Extension, feature_name, "BODYFEATURE", mark=1)\n'
            '    _select_by_id(model.Extension, axis_name, "AXIS", append=True, mark=4)\n'
            '    return model.FeatureManager.FeatureCircularPattern4(count, angle_rad)\n\n'
            'def next_one():\n    pass\n')
    body = circular_body(fake)
    assert body, "负例样本抽不出函数体"
    marks = {kind: mark for _n, kind, mark in selections(body)}
    assert not (marks.get("BODYFEATURE") == FEATURE_MARK and marks.get("AXIS") == AXIS_MARK), \
        "负例（mark 反了）没被抓到 ⇒ 主断言是空转的"


def test_negative_reversed_order_is_detected():
    """★★ 负例②：**反序**（先 AXIS 后 BODYFEATURE）⇒ 顺序判据必须报出来。"""
    fake = ('def circular_pattern(model, feature_name, axis_name):\n'
            '    _select_by_id(model.Extension, axis_name, "AXIS", mark=1)\n'
            '    _select_by_id(model.Extension, feature_name, "BODYFEATURE", append=True, mark=4)\n'
            '    return model.FeatureManager.FeatureCircularPattern4(count, angle_rad)\n\n'
            'def next_one():\n    pass\n')
    kinds = [k for _n, k, _m in selections(circular_body(fake))]
    assert not (kinds.index("BODYFEATURE") < kinds.index("AXIS")), "负例（反序）没被抓到"


def test_negative_swapped_args_are_detected():
    """★★ 负例③：**前两实参对调**（角度在前、数量在后）⇒ 顺序判据必须报出来。"""
    fake = ('def circular_pattern(model, feature_name, axis_name):\n'
            '    _select_by_id(model.Extension, feature_name, "BODYFEATURE", mark=4)\n'
            '    _select_by_id(model.Extension, axis_name, "AXIS", append=True, mark=1)\n'
            '    return model.FeatureManager.FeatureCircularPattern4(angle_rad, count)\n\n'
            'def next_one():\n    pass\n')
    args = call_args(circular_body(fake))
    assert not ("count" in args[0] and "angle" in args[1]), "负例（实参对调）没被抓到 ⇒ 判据空转"
