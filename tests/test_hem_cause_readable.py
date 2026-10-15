"""★ spec 282：`create_hem` 的真因**读出来了** —— ★「您必须选择一边线」★ 而选择**类型是对的**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/_probe282_hem.txt（★ 四形态 + 消息栈）· output/_probe282_seltype.txt（★ 选中类型核查）
#         scripts/sw_sheet_metal.py 的 `SHEET_METAL_RUNTIME_STATUS["create_hem"]`（★ 逐字：「★ 正确前置**尚未查明**」）
#         specs/276-createfeature-error-entry/acceptance.md（★ 报错入口）
#         specs/281-sheet-metal-family-backend-limit/acceptance.md（★ hem 走 `Insert*` ⇒ 与 `CreateDefinition` 族**不同因**）
# 定位:   ★ 209 试了 5 形态但**没读消息栈** ⇒ ★ 本轮补上 ⇒ ★ 真因读出 ⇒ ★ 再量一层「为什么选了还说没选」。
# 官方依据: `ISelectionMgr::GetSelectedObjectType3` ⇒ `swSelectType_e`（★ `swSelEDGES`=1 · `swSelFACES`=2）
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

#: ★★★ **真机读数 1**（SW **34.4.1** · 2026-10-10）：★ 四形态**全回 `None`**，★ 且报文**恒定**。
HEM_ARMS = {
    "H1 index:0 · open/outside": (False, "您必须选择一边线"),
    "H2 index:4 · open/outside": (False, "您必须选择一边线"),
    "H3 index:4 · closed/inside": (False, "您必须选择一边线"),
    "H4 index:0 · 默认卸料槽": (False, "您必须选择一边线"),
}
#: ★★★ **真机读数 2**：★ 选中的对象**类型是对的**（★ `GetSelectedObjectType3` 逐条核过）。
SEL_TYPES = {
    "SS.select_entity_by_index(EDGE, 4)": 1,      #: ★ `swSelEDGES`
    "edges[4].Select4": 1,                        #: ★ `swSelEDGES`
    "faces[0].Select4": 2,                        #: ★ `swSelFACES`（★ 对照）
    "SS.select_entity_by_index(FACE, 0)": 2,      #: ★ `swSelFACES`
}
SW_SEL_EDGES, SW_SEL_FACES = 1, 2
#: ★★ 边/面数（★ 夹具形状的可复核读数）。
BODY = {"edges": 44, "faces": 22}
#: ★★★ **同形但不同因**（★ 本轮的结构性结论）。
SAME_SHAPE = {
    "create_hem": "走 `InsertSheetMetalHem2`（★ **无** `AccessSelections`）",
    "create_edge_flange": "走 `CreateDefinition` + `CreateFeature`（★ 卡在 `AccessSelections` ⇒ `0x80010105`）",
}
#: ★★ **本轮的**假说**（★ 只有 2 个样本支持 ⇒ ★ 如实标成假说，★ 不当结论）。
HYPOTHESIS = "本机的**特征创建 API 似乎吃不到「边 / 面」类选择**（★ 草图那类能建）"


def _failures(arms, sel, body, same_shape, hypothesis, hem_block) -> list[str]:
    """★ 纯函数：① 四形态全失败且报文一致；② 选中类型对；③ 实体读数对；④ 同形表 2 条；⑤ 假说非空；⑥ 表已订正。"""
    bad: list[str] = []
    if len(arms) != 4:
        bad.append("★ 应 4 形态，实测 %d" % len(arms))
    if any(v for v, _m in arms.values()):
        bad.append("★ 四形态应**全失败**")
    if len({m for _v, m in arms.values()}) != 1:
        bad.append("★ 四形态报文应**一致**")
    elif "您必须选择一边线" not in next(iter(arms.values()))[1]:
        bad.append("★ 报文不是「您必须选择一边线」")
    if sel.get("SS.select_entity_by_index(EDGE, 4)") != SW_SEL_EDGES:
        bad.append("★ 边选出来应是 `swSelEDGES`(%d)" % SW_SEL_EDGES)
    if sel.get("edges[4].Select4") != SW_SEL_EDGES:
        bad.append("★ `IEntity::Select4` 那条也应是 `swSelEDGES`(%d)" % SW_SEL_EDGES)
    if sel.get("faces[0].Select4") != SW_SEL_FACES:
        bad.append("★ 面选出来应是 `swSelFACES`(%d)" % SW_SEL_FACES)
    if body.get("edges", 0) < 10 or body.get("faces", 0) < 5:
        bad.append("★ 实体读数可疑：%r" % (body,))
    if len(same_shape) != 2:
        bad.append("★ 同形表应 2 条")
    if not hypothesis:
        bad.append("假说为空")
    if not hem_block:
        bad.append("★ 回源码核失败：取不到 `create_hem` 那一条")
    elif "尚未查明" in hem_block and "订正" not in hem_block:
        bad.append("★ `create_hem` 那条**仍写着「尚未查明」而没有订正**")
    return bad


# ── ① ★★★ `create_hem` 的真因**读出来了** ─────────────────────────
def test_hem_cause_is_now_readable():
    """★★★ 真机（34.4.1）：★ 四形态**全回 `None`**，★ 且报文**恒定**：
    ★「**褶边N: 您必须选择一边线。**」⇒ ★★ 209 那句「正确前置**尚未查明**」**可以撤了**。
    """
    assert len(HEM_ARMS) == 4
    assert all(v is False for v, _m in HEM_ARMS.values()), "★ 四形态应全失败"
    assert len({m for _v, m in HEM_ARMS.values()}) == 1, "★ 报文应一致"
    assert "您必须选择一边线" in HEM_ARMS["H1 index:0 · open/outside"][1]


# ── ② ★★★ 而**选择类型是对的**（★ 再量一层） ──────────────────────
def test_the_selection_type_is_correct():
    """★★★ 真机：★ `SelectionMgr.GetSelectedObjectType3(1, -1)` ⇒ ★ 边 = **`swSelEDGES`(1)** ·
    ★ 面 = **`swSelFACES`(2)**（★ 两条路都试过：★ 本仓的 `select_entity_by_index` 与 ★ `IEntity::Select4`）
    ⇒ ★★ **「选了却说没选」** ⇒ ★ 问题**不在选择登记**。
    """
    assert SEL_TYPES["SS.select_entity_by_index(EDGE, 4)"] == SW_SEL_EDGES
    assert SEL_TYPES["edges[4].Select4"] == SW_SEL_EDGES
    assert SEL_TYPES["faces[0].Select4"] == SW_SEL_FACES
    assert BODY == {"edges": 44, "faces": 22}


# ── ③ ★★★ **同形但不同因** ─────────────────────────────────────────
def test_same_shape_but_different_mechanism():
    """★★★ `create_hem` 与 `create_edge_flange` **症状同形**（★ 都是「选择登记了但特征 API 吃不到」），
    ★★ **但机制不同**：★ hem 走 `Insert*`（★ 无 `AccessSelections`）· ★ edge_flange 卡在 `AccessSelections`（`0x80010105`）
    ⇒ ★ **不能混为一谈**。
    """
    assert len(SAME_SHAPE) == 2
    assert "InsertSheetMetalHem2" in SAME_SHAPE["create_hem"], "★ hem 走的是 `Insert*` 那条路"
    assert "0x80010105" in SAME_SHAPE["create_edge_flange"]


# ── ④ ★★ **假说**要如实标成假说（★ 只有 2 个样本） ────────────────
def test_the_hypothesis_is_labelled_as_a_hypothesis():
    """★★ 由 2 个样本（★ 吃**边/面**选择的两个都失败 · ★ 吃**草图**的那个能建）只能提出**假说** ——
    ★ 不能写成结论（★ 本仓铁律：★ 不凭类推）。
    """
    assert "假说" in HYPOTHESIS or "似乎" in HYPOTHESIS


# ── ⑤ ★★★ 状态表**确实**订正（★ 回源码核） ────────────────────────
def test_hem_status_entry_is_corrected():
    """★★★ 回源码核：★ `create_hem` 那条**不再**以「尚未查明」收尾，★ 而写明了真报文与「选择类型是对的」。"""
    src = (ROOT / "scripts" / "sw_sheet_metal.py").read_text(encoding="utf-8", errors="replace")
    m = re.search(r'"create_hem":\s*\(', src)
    assert m, "★ 取不到 `create_hem` 那一条"
    rest = src[m.end():]
    nxt = re.search(r'\n\s*"[a-z_]+":\s*\(', rest)
    block = rest[:nxt.start()] if nxt else rest
    assert "您必须选择一边线" in block, "★ 订正里要写**真报文**"
    assert "swSelEDGES" in block, "★ 订正里要写**选择类型核查**"


# ── ⑥ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 六组负例：① 形态数不对；② 某形态成功；③ 报文不一致；④ 选择类型不对；⑤ 同形表不全；⑥ 表仍写「尚未查明」。"""
    good = "…您必须选择一边线…swSelEDGES…订正…"
    args = (HEM_ARMS, SEL_TYPES, BODY, SAME_SHAPE, HYPOTHESIS, good)
    assert not _failures(*args), "正常读数被判红 ⇒ 判据过严"
    assert _failures({"a": (False, "您必须选择一边线")}, SEL_TYPES, BODY, SAME_SHAPE, HYPOTHESIS, good), \
        "形态数不对却未判出"
    assert _failures({**HEM_ARMS, "H1 index:0 · open/outside": (True, "您必须选择一边线")},
                     SEL_TYPES, BODY, SAME_SHAPE, HYPOTHESIS, good), "某形态成功却未判出"
    assert _failures({**HEM_ARMS, "H4 index:0 · 默认卸料槽": (False, "另一种")},
                     SEL_TYPES, BODY, SAME_SHAPE, HYPOTHESIS, good), "报文不一致却未判出"
    assert _failures(HEM_ARMS, {**SEL_TYPES, "edges[4].Select4": 2}, BODY, SAME_SHAPE,
                     HYPOTHESIS, good), "选择类型不对却未判出"
    assert _failures(HEM_ARMS, SEL_TYPES, BODY, {}, HYPOTHESIS, good), "同形表不全却未判出"
    assert _failures(HEM_ARMS, SEL_TYPES, BODY, SAME_SHAPE, HYPOTHESIS, "…尚未查明…"), \
        "表仍写「尚未查明」却未判出"
