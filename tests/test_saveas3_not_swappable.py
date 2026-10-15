"""★ spec 284：`SaveAs3` **真机静默失败** ⇒ ★★ **不换**（★ 换了会**静默坏掉写盘**）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/_probe284_saveas3.txt · output/_probe284_saveas3_opt.txt（★ 真机读数原文）
#         scripts/sw_connect.py:1153-1180（★ `save_document` **仍走** `Extension.SaveAs(…, 6 参)`）
#         C:/swapi/types/IModelDocExtension/{SaveAs,SaveAs2,SaveAs3}.md（★ 取代链）
# 定位:   ★ 待办原话是「`Extension.SaveAs` → `SaveAs3`（★ **改错会直接坏掉写盘**）」
#         ⇒ ★★ **实测正好证明确实会** ⇒ ★ **不换**（★ 「先量」救了一次）。
# 官方依据: 见上（★ `SaveAs` → `Obsolete. Superseded by SaveAs2` → `Obsolete. Superseded by SaveAs3` ⇒ ★ 链终点是 `SaveAs3`）
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

#: ★★★ **真机读数**（SW **34.4.1** · 2026-10-10 · ★ 走 `sw_guard`）：
#:   ★ `SaveAs3` 逐 `Options`（0/1/2/3）⇒ ★ **全部**：返回 **True** · `errors=0` · ★★ **文件不存在**。
SAVEAS3 = {0: (True, False), 1: (True, False), 2: (True, False), 3: (True, False)}
#: ★★ **对照**：`SaveAs`（★ 现状 · ★ 官方已标 Obsolete）⇒ ★ **文件真的写出来了**。
CONTROL = {"return": True, "file_exists": True, "size_bytes": 48696}
#: ★★★ **官方取代链**（★ 逐字）。
CHAIN = {"SaveAs": "Obsolete. Superseded by SaveAs2", "SaveAs2": "Obsolete. Superseded by SaveAs3",
         "SaveAs3": ""}
#: ★★★ **结论**：★ **不换**。
VERDICT = "不换 —— SaveAs3 在本机**静默失败**（返回 True 却不落盘）"


def _failures(saveas3, ctrl, chain, verdict, src) -> list[str]:
    """★ 纯函数：① 四个 Options **都**回 True 却**都不落盘**；② 对照**落盘**；③ 官方链对；④ 结论是「不换」；⑤ 源码仍走 `SaveAs`。"""
    bad: list[str] = []
    if len(saveas3) != 4:
        bad.append("★ 应测 4 个 Options，实测 %d" % len(saveas3))
    if not all(r is True for r, _f in saveas3.values()):
        bad.append("★ 四个 Options 都应**返回 True**")
    if any(f for _r, f in saveas3.values()):
        bad.append("★ 四个 Options 都应**不落盘**（★ 那才是「静默失败」）")
    if not (ctrl.get("return") and ctrl.get("file_exists")):
        bad.append("★ 对照 `SaveAs` 应**真的落盘**")
    if ctrl.get("size_bytes", 0) < 4096:
        bad.append("★ 对照文件太小：%r" % (ctrl.get("size_bytes"),))
    if "Superseded by SaveAs2" not in chain.get("SaveAs", ""):
        bad.append("★ `SaveAs` 的官方取代句不见了")
    if "Superseded by SaveAs3" not in chain.get("SaveAs2", ""):
        bad.append("★ `SaveAs2` 的官方取代句不见了")
    if chain.get("SaveAs3", "x"):
        bad.append("★ `SaveAs3` **不该**有取代句（★ 它是链终点）")
    if "不换" not in verdict:
        bad.append("★ 结论必须是**不换**")
    if not src:
        bad.append("★ 回源码核失败：取不到 `save_document`")
    elif re.search(r"\bSaveAs3\s*\(", src):
        bad.append("★★★ `save_document` **不该**出现 `SaveAs3(` 调用（★ 那会静默坏掉写盘）")
    elif not re.search(r"\bSaveAs\s*\(", src):
        bad.append("★ `save_document` 里找不到 `SaveAs(` 调用")
    return bad


# ── ① ★★★ `SaveAs3` **四个 Options 全静默失败** ────────────────────
def test_saveas3_silently_fails_for_every_option():
    """★★★ 真机：★ `GetAdvancedSaveAsOptions(0/1/2/3)` + `SaveAs3` ⇒ ★ **四个都返回 `True`、`errors=0`，
    而文件**一个都没写出来** ⇒ ★★ **静默失败**（★ 比「报错」更危险）。
    """
    assert len(SAVEAS3) == 4
    assert all(r is True for r, _f in SAVEAS3.values()), "★ 四个都应回 True"
    assert not any(f for _r, f in SAVEAS3.values()), "★ 四个都应不落盘"


# ── ② ★★ 对照：`SaveAs` **真的落盘** ─────────────────────────────
def test_the_current_saveas_actually_writes():
    """★★ 对照（★ 同一次运行）：★ `SaveAs` ⇒ ★ **文件存在 · 48696 B** ⇒ ★ **现状是好的**。"""
    assert CONTROL["return"] is True and CONTROL["file_exists"] is True
    assert CONTROL["size_bytes"] == 48696


# ── ③ ★★★ 官方链：★ 官方**说要换**，★ 而本机**不能换** ─────────────
def test_official_chain_says_switch_but_machine_says_no():
    """★★★ 官方页逐字：★ `SaveAs` → `Superseded by SaveAs2` → `Superseded by SaveAs3`（★ **链终点**）
    ⇒ ★★ **官方**确实**要我们换**；★ 而真机**证明换了会静默坏掉写盘**
    ⇒ ★★★ **本仓的处置：★ 保持 `SaveAs` + 把这条实测登记下来**（★ 不照官方链硬换）。
    """
    assert "Superseded by SaveAs2" in CHAIN["SaveAs"]
    assert "Superseded by SaveAs3" in CHAIN["SaveAs2"]
    assert CHAIN["SaveAs3"] == "", "★ `SaveAs3` 是链终点（无 Obsolete）"
    assert "不换" in VERDICT


# ── ④ ★★★ 回源码核：★ `save_document` **仍走 `SaveAs`** ───────────
def test_save_document_still_uses_saveas():
    """★★★ 回源码核：★ `scripts/sw_connect.py` 的 `save_document` **不许**出现 `SaveAs3`
    ⇒ ★ 否则就是**把静默失败接进写盘路径**（★ 正是本待办担心的那件事）。
    """
    src = (ROOT / "scripts" / "sw_connect.py").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"def save_document\(.*?\n(.*?)(?=\ndef )", src, re.S)
    assert m, "★ 取不到 `save_document`"
    body = m.group(1)
    #: ★ 查**调用形态**（`SaveAs3(`）—— ★ 注释/文档串里**允许**出现这个词（★ 它正是本条的结论）
    assert not re.search(r"\bSaveAs3\s*\(", body), "★★★ `save_document` 里出现了 `SaveAs3(` 调用"
    assert re.search(r"\bSaveAs\s*\(", body), "★ 找不到 `SaveAs(` 调用"


# ── ⑤ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 六组负例：① Options 数不对；② 某个回 False；③ 某个落了盘；④ 对照没落盘；⑤ 结论不是「不换」；⑥ 源码里出现 `SaveAs3`。"""
    good = "success = model.Extension.SaveAs(...)"
    args = (SAVEAS3, CONTROL, CHAIN, VERDICT, good)
    assert not _failures(*args), "正常读数被判红 ⇒ 判据过严"
    assert _failures({0: (True, False)}, CONTROL, CHAIN, VERDICT, good), "Options 数不对却未判出"
    assert _failures({**SAVEAS3, 0: (False, False)}, CONTROL, CHAIN, VERDICT, good), \
        "某个回 False 却未判出"
    assert _failures({**SAVEAS3, 0: (True, True)}, CONTROL, CHAIN, VERDICT, good), \
        "某个落了盘却未判出"
    assert _failures(SAVEAS3, dict(CONTROL, file_exists=False), CHAIN, VERDICT, good), \
        "对照没落盘却未判出"
    assert _failures(SAVEAS3, CONTROL, CHAIN, "照官方链换掉", good), "结论不是「不换」却未判出"
    assert _failures(SAVEAS3, CONTROL, CHAIN, VERDICT, "model.Extension.SaveAs3(...)"), \
        "★ 源码里出现 `SaveAs3` 却未判出"
