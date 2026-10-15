"""★ spec 276：**给「`CreateFeature` 回 `None`」找到能报错的入口** —— 真机读出真因 = **草图选择/状态**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/_probe276_error_entry.txt（★ 真机读数原文）
#         output/_probe276_error_entry.py（★ 探针 · ★ 走 `tools/sw_guard.py`）
#         specs/263-base-flange-failure-layers/acceptance.md（★ 留的下一步：「先找能报错的入口」）
#         C:/swapi/types/ISldWorks/GetErrorMessages.md · C:/swapi/types/IFeatureManager/GetCreateFeatureErrors.md
#         C:/swapi/examples/Create_Base_Flange_Feature_Example_VBNET.md（★ 官方序列逐字）
# 定位:   ★ 263/264/265 **三轮都在猜**（★ 因为 `CreateFeature` 回 `None` 时**读不到错误码**）⇒ ★ 本轮把入口找到。
# 官方依据: 见上（★ 入口是**先读官方页**选出来的，★ 不是猜的）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   只读（★ 真机读数由探针产出；★ 本文件不连 COM）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#: ★★★ **真机读数**（SolidWorks **34.4.1** · 2026-10-10 · ★ 只读探针 + 一个临时零件）。
#:   ★ 复刻 `tests/solidworks_sheet_metal_regression.py` 的 setup ⇒ `create_base_flange` 失败后**立刻**读。
MACHINE_N = 3
MACHINE_IDS = (909, 1124, 1124)
MACHINE_MSGS = ("选择失败。", "零件11 - 重建模型错误", "基体-法兰1: 所选的草图对此操作无效。")
#: ★★★ **真因的关键子串**（★ 文档序号会变 ⇒ 只钉**稳定**的部分）。
CAUSE_SUBSTR = "所选的草图对此操作无效"
SELECT_FAIL_SUBSTR = "选择失败。"
REBUILD_SUBSTR = "重建模型错误"

#: ★★★ **入口适用性表** —— ★ `(入口, 可用?, 依据)`；★ 依据是**官方页逐字**或**实测**。
ENTRIES = {
    "ISldWorks::GetErrorMessages": (True, "会话级最近 20 条 · 读完即清（官方页逐字）"),
    "IFeatureManager::GetCreateFeatureErrors": (False, "官方 Remarks：valid only after attempting to create Mate Controller features"),
    "IModelDocExtension::GetWhatsWrong": (False, "文档级 What's Wrong ⇒ 无特征则空（实测 Features=None）"),
}
#: ★★★ **与官方示例的差异**（★ `Create_Base_Flange_Feature_Example_VBNET.md`）—— ★ 两条**都必须登记**。
OFFICIAL_DIFFS = (
    "官方**不调** `AccessSelections` ⇒ 排除「我们漏调」",
    "官方靠 `InsertSketch(True)` 关草图后**草图特征自带选中** ⇒ 直接 `GetSelectedObject6(1,-1)`；本仓走 `_ensure_sketch_selected` **重选**",
)


def _failures(n, ids, msgs, cause, entries, diffs) -> list[str]:
    """★ 纯函数：① 真因文本在；② 两个 MsgID 在；③ 入口表**恰有一个可用**；④ 差异表非空。"""
    bad: list[str] = []
    joined = " ".join(msgs)
    if cause not in joined:
        bad.append("真因子串 %r **不在**读数里 ⇒ 入口没读对" % cause)
    if SELECT_FAIL_SUBSTR not in joined:
        bad.append("缺 `选择失败。`（★ MsgID 909 那条）")
    if REBUILD_SUBSTR not in joined:
        bad.append("缺 `重建模型错误`（★ MsgID 1124 那条）")
    if n != len(ids) or n != len(msgs):
        bad.append("n=%r 与 ids/msgs 长度不符" % (n,))
    usable = [k for k, (ok, _why) in entries.items() if ok]
    if len(usable) != 1:
        bad.append("可用的入口应**恰有 1 个**，实测 %d 个：%s" % (len(usable), usable))
    if usable and usable[0] != "ISldWorks::GetErrorMessages":
        bad.append("可用的那个不是 `GetErrorMessages`：%s" % usable)
    if not entries:
        bad.append("入口表为空 ⇒ 检查量为 0")
    if not diffs:
        bad.append("差异表为空 ⇒ 检查量为 0")
    return bad


# ── ① ★★★ 报错入口**找到了** ────────────────────────────────────────
def test_error_entry_is_found_and_readable():
    """★★★ 真机（34.4.1）：`ISldWorks::GetErrorMessages` **读到了 3 条** ⇒ ★ 真因**可读**（★ 263 要的入口）。"""
    assert MACHINE_N == 3, "真机读数变了？"
    assert len(MACHINE_IDS) == 3 and len(MACHINE_MSGS) == 3
    assert MACHINE_IDS == (909, 1124, 1124), "MsgID 变了：%r" % (MACHINE_IDS,)


# ── ② ★★★ **真因**是「草图选择/状态」 ──────────────────────────────
def test_the_recorded_cause_is_about_the_sketch():
    """★★★ **四轮里第一次读到真因**：★ **「选择失败。」+「基体-法兰1: 所选的草图对此操作无效。」**
    ⇒ ★★ 根因在**草图选择/状态**，★ **不是环境/许可/加载项**（★ 推翻 265 的猜测）。
    """
    assert CAUSE_SUBSTR in " ".join(MACHINE_MSGS), "真因文本变了"
    assert "基体-法兰" in " ".join(MACHINE_MSGS), "★ 失败的是**基体法兰**那条"


# ── ③ ★★ 另两个入口**被排除**（★ 带官方依据） ──────────────────────
def test_two_entries_are_ruled_out():
    """★★ `GetCreateFeatureErrors` 的官方 Remarks 逐字写「**only** … **Mate Controller**」⇒ ★ 不适用；
    ★ `GetWhatsWrong` 是**文档级** What's Wrong ⇒ ★ 无特征则空（★ 实测 `Features=None`）。
    """
    assert ENTRIES["ISldWorks::GetErrorMessages"][0] is True
    assert ENTRIES["IFeatureManager::GetCreateFeatureErrors"][0] is False
    assert "Mate Controller" in ENTRIES["IFeatureManager::GetCreateFeatureErrors"][1], \
        "★ 排除理由必须逐字引官方 Remarks"
    assert ENTRIES["IModelDocExtension::GetWhatsWrong"][0] is False


# ── ④ ★★★ 与官方示例的差异**已登记** ──────────────────────────────
def test_official_sequence_diff_is_registered():
    """★★★ 官方示例**不调 `AccessSelections`**（★ 排除一条猜想）· ★ 官方靠**关草图后的自带选择**
    ⇒ ★ 本仓「重选」可能丢了选择状态/标记（★ 与事实 384 同族）。
    """
    assert len(OFFICIAL_DIFFS) == 2, "两条差异都要在"
    assert any("AccessSelections" in d for d in OFFICIAL_DIFFS), "★ 缺「官方不调 AccessSelections」这条"
    assert any("GetSelectedObject6" in d for d in OFFICIAL_DIFFS), "★ 缺「官方自带选中」这条"


# ── ⑤ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 五组负例：① 真因文本不符；② 缺 MsgID；③ 入口表空；④ 两个可用；⑤ 差异表空。"""
    args = (MACHINE_N, MACHINE_IDS, MACHINE_MSGS, CAUSE_SUBSTR, ENTRIES, OFFICIAL_DIFFS)
    assert not _failures(*args), "正常读数被判红 ⇒ 判据过严"
    assert _failures(MACHINE_N, MACHINE_IDS, ("选择失败。", "重建模型错误"), CAUSE_SUBSTR,
                     ENTRIES, OFFICIAL_DIFFS), "真因文本不符却未判出 ⇒ 空判据"
    assert _failures(MACHINE_N, (909, 1124, 1124), ("选择失败。", "重建模型错误"), CAUSE_SUBSTR,
                     ENTRIES, OFFICIAL_DIFFS), "缺 `所选的草图…` 却未判出 ⇒ 空判据"
    assert _failures(MACHINE_N, MACHINE_IDS, MACHINE_MSGS, CAUSE_SUBSTR, {}, OFFICIAL_DIFFS), \
        "入口表空却未判出 ⇒ 空判据"
    two_ok = dict(ENTRIES)
    two_ok["IModelDocExtension::GetWhatsWrong"] = (True, "假装")
    assert _failures(MACHINE_N, MACHINE_IDS, MACHINE_MSGS, CAUSE_SUBSTR, two_ok, OFFICIAL_DIFFS), \
        "两个可用却未判出 ⇒ 空判据"
    assert _failures(MACHINE_N, MACHINE_IDS, MACHINE_MSGS, CAUSE_SUBSTR, ENTRIES, ()), \
        "差异表空却未判出 ⇒ 空判据"
