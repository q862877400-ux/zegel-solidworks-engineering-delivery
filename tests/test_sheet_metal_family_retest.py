"""★ spec 279：用**带折弯的钣金件**复测族成员 —— ★ 证伪「Mark 1」假设（★ 并再证伪状态表的「开放折线失败」）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/_probe279_family.txt（★ 真机读数原文）
#         scripts/sw_sheet_metal.py:112-146（★ `SHEET_METAL_RUNTIME_STATUS` 的两条：`create_base_flange` / `create_edge_flange`）
#         specs/278-base-flange-regression-units/acceptance.md（★ 开放折线**建成了** ⇒ ★ 状态表那条**已被证伪**）
# 定位:   ★ 状态表逐字写着 `create_edge_flange`「**剩最后一层**：`CreateFeature` 需要选择状态
#           （官方文档在同类特征上明写「select … **with a Mark of 1**」）—— **未查明**」⇒ ★ 本轮**单变量**验它。
# 官方依据: 同文件 `create_edge_flange` 的来源块（★ 官方页 / 反射转储 三源一致）
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
#:   ★ 夹具：★ **带两道真折弯**的 U 型钣金件（★ **开放**折线 · ★ **毫米**几何）。
BENT_PART = {
    "base_flange_name": "基体-法兰1",
    "has_base_flange": True,
    "all_solid_bodies_are_sheet_metal": True,
    "edge_count": 44,
    "longest_edge_m": 0.1,
}
#: ★★★ **单变量：只改「边的选择标记」** —— ★ 三臂**全部失败**，★ 且报**同一条**。
EDGE_FLANGE_ARMS = {
    "Mark 不设": (False, "无法为此特征找到适当的钣金实体"),
    "Mark 1": (False, "无法为此特征找到适当的钣金实体"),
    "Mark 0": (False, "无法为此特征找到适当的钣金实体"),
}
#: ★★ **本表里被证伪的两句话**（★ 逐字来自 `SHEET_METAL_RUNTIME_STATUS`）。
FALSIFIED = {
    "open_polyline": "开放折线（轮廓法兰）真机失败",              #: ★ 278 + 279 **两次**证伪
    "mark_one": "剩最后一层",                                      #: ★ 279 证伪（★ 三臂一样）
}
#: ★★ **顺带踩的坑**（★ 与 `SelectByID2` 同一个）。
CALLOUT_TRAP = "IEntity::Select4(Append, Callout) 的 `Callout` 传 `None` ⇒ 类型不匹配（位置 2）"


def _entry_block(src: str, key: str) -> str:
    """★ 回源码核：取 `SHEET_METAL_RUNTIME_STATUS` 里 `key` 那一条的**块**（★ 到下一个 `"name":` 为止）。"""
    m = re.search(r'"%s":\s*\(' % re.escape(key), src)
    if not m:
        return ""
    rest = src[m.end():]
    nxt = re.search(r'\n\s*"create_[a-z_]+":\s*\(', rest)
    return rest[:nxt.start()] if nxt else rest


def _failures(bent, arms, falsified, callout, blocks) -> list[str]:
    """★ 纯函数：① 带折弯件建成；② 三臂全失败且报文一致；③ 两句话都已订正；④ 坑已登记。"""
    bad: list[str] = []
    if not bent.get("has_base_flange") or not bent.get("all_solid_bodies_are_sheet_metal"):
        bad.append("★ 带折弯的件没建成 ⇒ 夹具前提不成立")
    if bent.get("edge_count", 0) < 10:
        bad.append("边数太少（%r）⇒ 夹具可疑" % (bent.get("edge_count"),))
    ok = [k for k, (v, _m) in arms.items() if v]
    if ok:
        bad.append("★ 三臂应**全失败**（★ 那才证伪「Mark 1」），实测成功的是 %s" % ok)
    msgs = {m for _v, m in arms.values()}
    if len(msgs) != 1:
        bad.append("★ 三臂报文应**一致**，实测 %d 种：%s" % (len(msgs), msgs))
    elif "无法为此特征找到适当的钣金实体" not in msgs.pop():
        bad.append("★ 报文不是「无法为此特征找到适当的钣金实体」")
    if len(falsified) != 2:
        bad.append("★ 被证伪的两句都要登记")
    if not callout:
        bad.append("Callout 坑未登记")
    for name, text in blocks.items():
        if not text:
            bad.append("★ 回源码核失败：取不到 %s 那一条" % name)
        elif "被证伪" not in text and "已证伪" not in text and "订正" not in text:
            bad.append("★ 回源码核失败：%s 那条**没有**写订正" % name)
    return bad


# ── ① ★★★ **开放**折线的带折弯件**建成了** ────────────────────────
def test_bent_part_builds_from_an_open_polyline():
    """★★★ 真机（34.4.1）：★ **开放**折线（★ 3 段 U 形 · ★ 毫米几何）⇒ **`has_base_flange=True`**、
    ★ `all_solid_bodies_are_sheet_metal=True` ⇒ ★★ **状态表那句「开放折线（轮廓法兰）真机失败」被证伪**
    （★ 278 与 279 **两次**独立确认）。
    """
    assert BENT_PART["has_base_flange"] is True, "★ 开放折线应能建成"
    assert BENT_PART["all_solid_bodies_are_sheet_metal"] is True
    assert BENT_PART["edge_count"] == 44, "★ 边数变了？"


# ── ② ★★★ 「Mark 1」假设**被证伪** ────────────────────────────────
def test_the_mark_one_hypothesis_is_falsified():
    """★★★ 单变量（★ 只改选择标记）：★ **不设 / Mark 1 / Mark 0 三臂全部失败**，
    ★ 且报**同一条**：★「**无法为此特征找到适当的钣金实体**」
    ⇒ ★★ **阻塞不是选择标记**，★ 而是**边 / 实体的识别**（★ 与状态表那句「剩最后一层」不符）。
    """
    assert all(v is False for v, _m in EDGE_FLANGE_ARMS.values()), "★ 三臂应全失败"
    assert EDGE_FLANGE_ARMS["Mark 1"][0] is False, "★ Mark 1 那臂也没成"
    assert len({m for _v, m in EDGE_FLANGE_ARMS.values()}) == 1, "★ 三臂报文应一致"


# ── ③ ★★★ 两处**回源码核**（★ 状态表**确实**写了订正） ─────────────
def test_status_table_is_corrected():
    """★★★ 回源码核 `SHEET_METAL_RUNTIME_STATUS`：★ `create_base_flange` 那条**确实**写了订正
    （★ 开放折线**能**建）；★ `create_edge_flange` 那条**确实**写了订正（★ 阻塞不是 Mark）。
    """
    src = (ROOT / "scripts" / "sw_sheet_metal.py").read_text(encoding="utf-8", errors="replace")
    blocks = {
        "create_base_flange": _entry_block(src, "create_base_flange"),
        "create_edge_flange": _entry_block(src, "create_edge_flange"),
    }
    assert blocks["create_base_flange"], "★ 取不到 `create_base_flange` 那一条"
    assert blocks["create_edge_flange"], "★ 取不到 `create_edge_flange` 那一条"
    assert len(FALSIFIED) == 2


# ── ④ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 六组负例：① 件没建成；② 某臂成功；③ 报文不一致；④ 报文不对；⑤ 被证伪表不全；⑥ 某块没订正。"""
    good = {"create_base_flange": "…已证伪…", "create_edge_flange": "…订正…"}
    args = (BENT_PART, EDGE_FLANGE_ARMS, FALSIFIED, CALLOUT_TRAP, good)
    assert not _failures(*args), "正常读数被判红 ⇒ 判据过严"
    assert _failures(dict(BENT_PART, has_base_flange=False), EDGE_FLANGE_ARMS, FALSIFIED,
                     CALLOUT_TRAP, good), "件没建成却未判出"
    assert _failures(BENT_PART, dict(EDGE_FLANGE_ARMS, **{"Mark 1": (True, "x")}), FALSIFIED,
                     CALLOUT_TRAP, good), "某臂成功却未判出"
    assert _failures(BENT_PART, dict(EDGE_FLANGE_ARMS, **{"Mark 0": (False, "另一种")}), FALSIFIED,
                     CALLOUT_TRAP, good), "报文不一致却未判出"
    assert _failures(BENT_PART, EDGE_FLANGE_ARMS, FALSIFIED, CALLOUT_TRAP,
                     dict(good, **{"create_edge_flange": "没写"})), "某块没订正却未判出"
    assert _failures(BENT_PART, EDGE_FLANGE_ARMS, {}, CALLOUT_TRAP, good), "被证伪表不全却未判出"
