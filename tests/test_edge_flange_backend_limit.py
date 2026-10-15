"""★ spec 280：`create_edge_flange` 定案 —— ★ 三条候选全被证伪；★ 阻塞是「`AccessSelections` 族」的后端限制。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/_probe280_{edge_select,closed_profile,access_selections}.txt（★ 三轮真机读数原文）
#         C:/swapi/types/IEdgeFlangeFeatureData/AccessSelections.md（★ 官方页：`bool AccessSelections(TopDoc, Component)`）
#         docs/known-facts.md 事实 47 / 67 / 126（★ `IAccessSelections` 指针族 `0x80010105`）
# 定位:   ★ 279 把 `create_edge_flange` 的「Mark 1」假设证伪后，★ 本轮**逐条排除剩下的候选**，★ 并**定案**。
# 官方依据: 见上（★ 官方页 + 本仓事实）
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

#: ★★★ **真机读数 1**（SW **34.4.1** · 2026-10-10）：★ 六臂**全失败**，★ 且报文**恒定**。
ARMS = {
    "A Select4 + Mark 1（最长边）": False,
    "B SelectByID2 + Mark 1（最长边）": False,
    "C SelectByID2 + 不设 mark（最长边）": False,
    "D SelectByID2 + Mark 1（最短直边）": False,
    "E 开放折线（轮廓法兰）": False,
    "F 闭轮廓（平板基体）": False,
}
#: ★★★ **恒定报文**（★ 六臂一字不差）。
CONST_MSG = "无法为此特征找到适当的钣金实体"
#: ★★★ **真机读数 2**：★ `IEdgeFlangeFeatureData::AccessSelections` 逐形态。
ACCESS_SELECTIONS = {
    "AccessSelections(model, None)": -2147352571,          #: ★ `DISP_E_TYPEMISMATCH`
    "AccessSelections(model, False)": -2147352571,
    "AccessSelections(model, 空 Dispatch)": -2147417851,   #: ★★★ **`0x80010105`「服务器出现意外情况」**
}
#: ★★ **事实 47 族的十六进制**（★ 与上面那个十进制**同一个数**）。
FACT47_HEX = "0x80010105"
#: ★★ **被证伪的候选**（★ 逐条登记，★ 免得下一轮重试）。
RULED_OUT = ("选择方式（Select4 ↔ SelectByID2）", "换一条边（最长 ↔ 最短直边）", "轮廓类型（开放折线 ↔ 闭轮廓）")


def _failures(arms, msg, acc, hexs, ruled_out, table_ok) -> list[str]:
    """★ 纯函数：① 六臂全失败；② 报文恒定；③ 三形态错误码齐；④ 十进制与十六进制**是同一个数**；⑤ 表已订正。"""
    bad: list[str] = []
    ok = [k for k, v in arms.items() if v]
    if ok:
        bad.append("★ 六臂应**全失败**，实测成功的是 %s" % ok)
    if len(arms) != 6:
        bad.append("★ 应 6 臂，实测 %d" % len(arms))
    if not msg:
        bad.append("报文为空")
    if len(acc) != 3:
        bad.append("★ `AccessSelections` 应测 3 形态，实测 %d" % len(acc))
    if acc.get("AccessSelections(model, 空 Dispatch)") != -2147417851:
        bad.append("★ 空 Dispatch 那形态**应**回 -2147417851（`0x80010105`）")
    if (int(FACT47_HEX, 16)) != (-2147417851 + (1 << 32)):
        bad.append("★ `0x80010105` 与 -2147417851 **不是同一个数**（★ 后者是它的**有符号**形式）")
    if len(ruled_out) != 3:
        bad.append("★ 三条被证伪的候选都要登记")
    if not table_ok:
        bad.append("★ 回源码核失败：状态表那条**没有**写订正")
    return bad


# ── ① ★★★ 六臂全失败且报文**恒定** ─────────────────────────────────
def test_all_six_arms_fail_with_the_same_message():
    """★★★ 真机（34.4.1）：★ **选择方式 / 换边 / 轮廓类型** 六臂**全失败**，
    ★ 且报文**一字不差**：★「**无法为此特征找到适当的钣金实体**」
    ⇒ ★★ **这三条都不是因素**。
    """
    assert all(v is False for v in ARMS.values()), "★ 六臂应全失败"
    assert CONST_MSG == "无法为此特征找到适当的钣金实体"
    assert len(RULED_OUT) == 3


# ── ② ★★★ `AccessSelections` **不可调用** ⇒ 结构性阻塞 ─────────────
def test_access_selections_is_unavailable_on_this_machine():
    """★★★ 真机：★ `AccessSelections(model, 空 Dispatch)` ⇒ **`-2147417851`（`0x80010105`「服务器出现意外情况」）**，
    ★ 另两形态 ⇒ `-2147352571`（类型不匹配）
    ⇒ ★★ 与**事实 47 / 67 / 126** 的 `IAccessSelections` 指针族**同族** ⇒ ★★★ **结构性阻塞**。
    """
    assert ACCESS_SELECTIONS["AccessSelections(model, 空 Dispatch)"] == -2147417851
    assert int(FACT47_HEX, 16) & 0xFFFFFFFF == 0x80010105
    assert ACCESS_SELECTIONS["AccessSelections(model, None)"] == -2147352571


# ── ③ ★★ **十进制 ↔ 十六进制自洽**（★ 别把负数写错） ────────────────
def test_the_two_notations_are_the_same_number():
    """★★ 本仓记的是 `0x80010105`，★ 而 pywin32 回的是**有符号十进制** ⇒ ★ 两者必须自洽。"""
    assert int(FACT47_HEX, 16) == 0x80010105
    assert -2147417851 + (1 << 32) == 0x80010105, "★ -2147417851 的无符号形式应是 0x80010105"


# ── ④ ★★★ 状态表**确实**订正（★ 回源码核） ────────────────────────
def test_status_table_is_corrected():
    """★★★ 回源码核：★ `SHEET_METAL_RUNTIME_STATUS["create_edge_flange"]` 那条**确实**写了订正
    （★ 从「未查明」⇒ ★ **后端限制 `AccessSelections` 族**），★ 且**旧结论留档**。
    """
    src = (ROOT / "scripts" / "sw_sheet_metal.py").read_text(encoding="utf-8", errors="replace")
    m = re.search(r'"create_edge_flange":\s*\(', src)
    assert m, "★ 取不到 `create_edge_flange` 那一条"
    rest = src[m.end():]
    nxt = re.search(r'\n\s*"create_[a-z_]+":\s*\(', rest)
    block = rest[:nxt.start()] if nxt else rest
    assert "0x80010105" in block or "AccessSelections" in block, "★ 订正里要写明 `AccessSelections`"
    assert ("订正" in block) or ("被证伪" in block), "★ 要写明订正"
    assert ("Mark of 1" in block), "★ 旧结论要**留档**"


# ── ⑤ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 五组负例：① 某臂成功；② 臂数不对；③ 空 Dispatch 那形态码不对；④ 候选表不全；⑤ 表没订正。"""
    args = (ARMS, CONST_MSG, ACCESS_SELECTIONS, FACT47_HEX, RULED_OUT, True)
    assert not _failures(*args), "正常读数被判红 ⇒ 判据过严"
    assert _failures(dict(ARMS, **{"A Select4 + Mark 1（最长边）": True}), CONST_MSG,
                     ACCESS_SELECTIONS, FACT47_HEX, RULED_OUT, True), "某臂成功却未判出"
    assert _failures({"a": False}, CONST_MSG, ACCESS_SELECTIONS, FACT47_HEX, RULED_OUT, True), \
        "臂数不对却未判出"
    assert _failures(ARMS, CONST_MSG, dict(ACCESS_SELECTIONS,
                                           **{"AccessSelections(model, 空 Dispatch)": -1}),
                     FACT47_HEX, RULED_OUT, True), "错误码不对却未判出"
    assert _failures(ARMS, CONST_MSG, ACCESS_SELECTIONS, FACT47_HEX, (), True), "候选表不全却未判出"
    assert _failures(ARMS, CONST_MSG, ACCESS_SELECTIONS, FACT47_HEX, RULED_OUT, False), \
        "表没订正却未判出"
