"""★ spec 281：同族的 `AccessSelections` 逐个测 —— ★★ **整族后端限制**（4 个 `CreateDefinition` 族成员同一个因）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/_probe281_family_access.txt（★ 真机读数原文）
#         specs/280-edge-flange-backend-limit/acceptance.md（★ 常量 37 的定案）
#         scripts/sw_sheet_metal.py:433-449（★ 常量：35 / 37 / 117 / 118）
#         C:/swapi/types/{ISketchedBendFeatureData,ISMGussetFeatureData}/（★ 官方页**有** `AccessSelections`）
# 定位:   ★ 280 只验了常量 37 ⇒ ★ 本轮把**同族的其余常量**逐个测 ⇒ ★★ **整族同一个因**。
# 官方依据: 见上（★ 官方页）
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

#: ★★★ **真机读数**（SW **34.4.1** · 2026-10-10 · ★ 走 `sw_guard`）：★ 常量 → `AccessSelections` 的 hresult。
HRESULTS = {
    37: -2147417851,      #: `create_edge_flange`  · `IEdgeFlangeFeatureData`（★ 280 已定案）
    35: -2147417851,      #: `create_one_bend`     · `ISketchedBendFeatureData`
    118: -2147417851,     #: `create_gusset`      · `ISMGussetFeatureData`
    117: -2147417851,     #: `create_swept_flange`· `ISweptFlangeFeatureData`
}
#: ★★ `hasattr(data, "AccessSelections")` ⇒ ★ **方法在**（★ 不是「没有这个方法」）。
HASATTR = {35: True, 117: True, 118: True}
#: ★★★ **`0x80010105`**（★ 事实 47 / 67 / 126 的 `IAccessSelections` 指针族）。
FACT47_HEX = 0x80010105
#: ★★★ **路径分层**（★ 这是本轮的**结构性**结论）。
BY_PATH = {
    "CreateDefinition + CreateFeature": ("create_one_bend", "create_edge_flange",
                                         "create_swept_flange", "create_gusset"),
    "直接 Insert*（★ 不走这条路）": ("create_hem", "create_draft", "create_base_flange"),
}
#: ★★ 要被订正的状态表条目（★ 逐条）。
TO_CORRECT = ("create_one_bend", "create_gusset", "create_swept_flange")


def _failures(hr, hasattr_, hexs, by_path, to_correct, blocks) -> list[str]:
    """★ 纯函数：① 四个常量**全部**同一个 hresult；② 那个 hresult **就是** `0x80010105`；③ 路径分层非空；④ 表已订正。"""
    bad: list[str] = []
    if len(hr) != 4:
        bad.append("★ 应测 4 个常量，实测 %d" % len(hr))
    if len(set(hr.values())) != 1:
        bad.append("★ 四个常量应回**同一个** hresult，实测 %s" % sorted(set(hr.values())))
    elif next(iter(hr.values())) != -2147417851:
        bad.append("★ 那个 hresult 应是 -2147417851")
    if hexs != 0x80010105:
        bad.append("★ `0x80010105` 写错了")
    if (-2147417851 + (1 << 32)) != hexs:
        bad.append("★ 十进制与十六进制**不自洽**")
    if not hasattr_ or not all(hasattr_.values()):
        bad.append("★ `hasattr` 应全为 True（★ 方法**在**）")
    if len(by_path) != 2:
        bad.append("★ 路径分层应两档")
    if len(to_correct) != 3:
        bad.append("★ 要订正的条目应是 3 条")
    for name, text in blocks.items():
        if not text:
            bad.append("★ 回源码核失败：取不到 %s" % name)
        elif "0x80010105" not in text and "AccessSelections" not in text:
            bad.append("★ 回源码核失败：%s **没有**写「后端限制」的理由" % name)
    return bad


def _entry_block(src: str, key: str) -> str:
    """★ 取 `SHEET_METAL_RUNTIME_STATUS` 里 `key` 那一条的块。"""
    m = re.search(r'"%s":\s*\(' % re.escape(key), src)
    if not m:
        return ""
    rest = src[m.end():]
    nxt = re.search(r'\n\s*"create_[a-z_]+":\s*\(', rest)
    return rest[:nxt.start()] if nxt else rest


# ── ① ★★★ 四个常量**同一个** hresult ───────────────────────────────
def test_all_four_constants_share_one_hresult():
    """★★★ 真机（34.4.1）：★ `CreateDefinition` 的**四个**常量（35 / 37 / 117 / 118）
    ⇒ `AccessSelections(model, 空 Dispatch)` **全部**回 `-2147417851`
    ⇒ ★★ **整族**同一个因****（★ 不是「每个都要单独查」）。
    """
    assert len(HRESULTS) == 4
    assert len(set(HRESULTS.values())) == 1, "★ 应同一个 hresult"
    assert HRESULTS[35] == HRESULTS[118] == HRESULTS[117] == HRESULTS[37] == -2147417851


# ── ② ★★★ 那个 hresult **就是** `0x80010105` ──────────────────────
def test_the_hresult_is_the_known_pointer_family():
    """★★★ `-2147417851` 的**无符号**形式 = **`0x80010105`** ⇒ ★★ 与**事实 47 / 67 / 126** 的
    `IAccessSelections` 指针族**同族** ⇒ ★ **后端限制**。
    """
    assert FACT47_HEX == 0x80010105
    assert -2147417851 + (1 << 32) == FACT47_HEX


# ── ③ ★★ 方法**在**（★ 不是「没有这个方法」） ─────────────────────
def test_the_method_exists_but_cannot_be_called():
    """★★ `hasattr(data, "AccessSelections")` ⇒ **True** ⇒ ★ 方法**在**（★ pywin32 拿得到）
    ⇒ ★ **不是「没有这个方法」**，★ 而是**调用时**回 `0x80010105`（★ 官方页也有 ⇒ ★ 不是路径错）。
    """
    assert all(HASATTR.values()), "★ `hasattr` 应全 True"
    assert set(HASATTR) == {35, 117, 118}


# ── ④ ★★★ **路径分层**（★ 结构性结论） ────────────────────────────
def test_the_two_paths_are_separated():
    """★★★ 走 **`CreateDefinition` + `CreateFeature`** 的 4 个 ⇒ ★ **受限**；
    ★ 而 `create_hem` 走 **`InsertSheetMetalHem2`**（★ 直接 `Insert*`）⇒ ★ **不在这一族**
    ⇒ ★★ **它的 5 形态 None 是**另一个**原因**（★ 不要混为一谈）。
    """
    assert len(BY_PATH) == 2
    assert "create_hem" in BY_PATH["直接 Insert*（★ 不走这条路）"], "★ hem 走的是 `Insert*`"
    assert "create_hem" not in BY_PATH["CreateDefinition + CreateFeature"]
    assert len(BY_PATH["CreateDefinition + CreateFeature"]) == 4


# ── ⑤ ★★★ 状态表**确实**订正（★ 回源码核 · ★ 三条） ───────────────
def test_status_table_entries_are_corrected():
    """★★★ 回源码核：★ `create_one_bend` / `create_gusset` / `create_swept_flange` 三条**都**写明了
    ★「后端限制（`AccessSelections` / `0x80010105`）」。
    """
    src = (ROOT / "scripts" / "sw_sheet_metal.py").read_text(encoding="utf-8", errors="replace")
    blocks = {k: _entry_block(src, k) for k in TO_CORRECT}
    assert len(TO_CORRECT) == 3
    for name, text in blocks.items():
        assert text, "★ 取不到 %s 那一条" % name
    assert all(("0x80010105" in t) or ("AccessSelections" in t) for t in blocks.values()), \
        "★ 三条都要写明理由"


# ── ⑥ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 六组负例：① 常量数不对；② hresult 不齐；③ 十六进制写错；④ `hasattr` 有 False；
    ⑤ 要订正的条目数不对；⑥ 某块没写理由。"""
    good = {k: "…AccessSelections…0x80010105…" for k in TO_CORRECT}
    args = (HRESULTS, HASATTR, FACT47_HEX, BY_PATH, TO_CORRECT, good)
    assert not _failures(*args), "正常读数被判红 ⇒ 判据过严"
    assert _failures({37: -2147417851}, HASATTR, FACT47_HEX, BY_PATH, TO_CORRECT, good), "常量数不对"
    assert _failures({**HRESULTS, 35: -1}, HASATTR, FACT47_HEX, BY_PATH, TO_CORRECT, good), \
        "hresult 不齐却未判出"
    assert _failures(HRESULTS, HASATTR, 0x80010104, BY_PATH, TO_CORRECT, good), "十六进制写错却未判出"
    assert _failures(HRESULTS, {**HASATTR, 35: False}, FACT47_HEX, BY_PATH, TO_CORRECT, good), \
        "`hasattr` 有 False 却未判出"
    assert _failures(HRESULTS, HASATTR, FACT47_HEX, BY_PATH, ("create_one_bend",), good), \
        "要订正的条目数不对却未判出"
    assert _failures(HRESULTS, HASATTR, FACT47_HEX, BY_PATH, TO_CORRECT,
                     dict(good, **{"create_gusset": "没写"})), "某块没写理由却未判出"
