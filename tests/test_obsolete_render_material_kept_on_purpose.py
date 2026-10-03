"""★ 测 `DeleteRenderMaterial` 的「记档保留」按**逐条读数**判（★ 阶段 2 · T1 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 本机三套源
# 文件:   `scripts/sw_render_material.py::delete_render_material` ·
#         `output/render-material-family-evidence.json`（★ 证据）·
#         `tools/probe_render_material_family.py`（★ 探针、★ 只报不动）
# 定位:   ★ 阶段 2 · T1 的逐条流程 ①（查官方）与 ②（真机验证）✓
#   ★★ **三源互证的结果**：
#     · ★ **官方页** `IModelDocExtension/DeleteRenderMaterial.md` ⇒ **没有** `Obsolete` 行 ✓
#     · ★★ **而名单** `official-members-index.json` 的 `obsolete_line` 逐字：
#       ★ 「**Not supported in SOLIDWORKS 2011 and later. Superseded by…**」⇒
#       ★★★ **那比 `Obsolete` **更强**（★ "不支持"）** ✓
#     · ★★★ **反射**（★ 铁律 4 的裁决者）⇒ `_raw/reflect_sldworks/iface_sldworks.txt` L10899
#       `Boolean DeleteRenderMaterial(Int32, Boolean)` ⇒ ★ **成员在、参数对**；
#       ★★ **⚠ 而反射**只有签名、★ 没有"废弃位"** ⇒ **它裁不了"废没废"、★ 只能裁"在不在"** ✓
#   ★★★★ **逐条读数**（★ 证据文件里）：★ 旧入口 `ok: true`（`ret: True`）·
#     ★★ **新入口 `ok: false`**（`TypeError: …不可调用（`getattr` 回了 `bool`）`）⇒
#     ★★★ **要换的那个**恰好调不了** ✓
#   ★★★★★ **而那份证据的 `verdict` 逐字是**「★ 新旧都能调 ⇒ **可以换**」**** ——
#     ★ **那句过于乐观**（★ 把 `3/4` 读成了"都能调"）⇒ ★★ **本函数按分项读数判、★ 不按 verdict 判** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_render_material.py"
EVID = REPO / "output" / "render-material-family-evidence.json"
OFF = Path(r"C:\swapi\types\IModelDocExtension\DeleteRenderMaterial.md")


def test_official_page_has_no_plain_obsolete_line() -> None:
    """★★★ **前提断言**：★ 官方那页**没有** `Obsolete` 行（★ 判据的锚点之一）✓"""
    if not OFF.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t = OFF.read_text(encoding="utf-8", errors="replace")
    assert "Obsolete" not in t, "★ 官方页现在有 `Obsolete` 行了 ⇒ 判据要重看"


def test_evidence_new_entry_is_not_callable() -> None:
    """★★★ 核心断言：★ 证据里**新入口调不了、★ 旧入口能调** ✓"""
    if not EVID.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(EVID.read_text(encoding="utf-8", errors="replace"))
    old = d.get("旧_DeleteRenderMaterial") or {}
    new = d.get("新_DeleteDisplayStateSpecificRenderMaterial") or {}
    assert old.get("ok") is True, "★ 旧入口的证据变了：%r" % old
    assert new.get("ok") is False, "★ 新入口竟然能调 ⇒ 那就可以换了 ⇒ 判据要重看"
    assert "不可调用" in str(new.get("err")), "★ 新入口的失败形态变了"


def test_code_still_calls_the_callable_member() -> None:
    """★★★ 核心断言：★ 记档期间**仍要调旧的**（★ 而**不许**调那个调不了的）✓

    ⚠★ **判据的取法（★ 我先走错一版，记下来）**：★ 我最初想「剥注释 + 剥 docstring 后取**代码**」——
      ★★ 而那个 AST 剥法在有**模块级 docstring** 的仓库里**不稳**（★ 我连续试了三种写法，
        ★★★ **每次都有残留**）⇒ ★ **改用**只取那一个函数的源码段**、★ 并**只认"调用的字面量"** ✓
      ★★★ **这正是**事实 53**：★★★ **同一个启发式连续修补 ≥3 次就该停下换做法** ✓
      ⇒ ★★★★ **换成**精确到那一行**的判据：★ 找 `get_com_member(` 后面紧跟的那个名字 ✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    #: ★★ 判据：★ 只看**调用形态** `get_com_member(<obj>, "<名字>", …)` ⇒
    #:    ★ 从**函数体**那一段里取（★ 从 `def delete_render_material` 到下一个 `\ndef `）✓
    i = t.find("def delete_render_material(")
    assert i != -1, "★ 找不到那个函数"
    j = t.find("\ndef ", i + 10)
    body = t[i:j if j != -1 else len(t)]
    #: ★ 再剔掉那段里的**注释行**（★ 注释里引旧名是「补正而不删除」）
    code_lines = [ln for ln in body.splitlines() if not ln.lstrip().startswith("#")]
    code = "\n".join(code_lines)
    called = re.findall(r'get_com_member\(\s*[A-Za-z_][\w\.]*\s*,\s*"([A-Za-z_]\w*)"', code)
    assert called, "★ 那段里找不到 `get_com_member(obj, \"名字\", …)` 调用"
    assert "DeleteRenderMaterial" in called, (
        "★ 能调的那个没被调：%r" % called)
    assert "DeleteDisplayStateSpecificRenderMaterial" not in called, (
        "★ 竟然去调那个调不了的（★ 会 `TypeError`）：%r" % called)


def test_negative_case_the_verdict_was_flagged_as_optimistic() -> None:
    """★★★ **负例 · 逐条优先于 verdict**：★ docstring 里必须指出那句 `verdict` 过于乐观 ✓

    ★★ **本条的判据**：★★★ **证据文件里的 `verdict` 是**结论**、★ 而逐条 `ok` 才是**事实** ——
      两者打架时**以逐条为准**** ✓
      ★ 与**事实 519** 同族：★ **"表里有"≠"它做到了"** ✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find("def delete_render_material")
    seg = t[i:i + 4200]
    assert "verdict" in seg, "★ 没提那处 verdict"
    assert "过于乐观" in seg, "★ 没指出那句 verdict 过于乐观"
    assert "逐条" in seg, "★ 没写明「以逐条为准」这条判据"
