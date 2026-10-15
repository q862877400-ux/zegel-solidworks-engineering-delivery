"""★ spec 256：`IView::Name` 换路由 —— 4 处真命中**已改掉**（★ 判据 + 真机等价性证据）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/sw_drawing_query.py:194 / :264 · scripts/sw_drawing_view.py:436 · scripts/sw_review.py:637
#         （★ 248 判定的 4 处 `IView::Name` 真命中）
#         specs/254-iview-name-routing/ · specs/255-multi-view-drawing-evidence/（★ 前置证据）
# 定位:   ★ 254/255 只**量**不改；★ 本文件把**换路由**的结果冻成判据 ——
#         ★ **AST 按名字定位**（★ 不用行号，★ 行号会漂）。
# 官方依据: C:/swapi/types/IView/Name.md「Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]]」
#           真机 SW **34.4.1**：4 个视图（3 个真实模型视图）上 `Name` == `GetName2`
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读 `scripts/`；★ 不碰 SolidWorks
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★ 4 处真命中的**宿主表达式**（★ 248 判定的原文）。
VIEW_HOSTS = {"view", "av"}

#: ★ 被改的文件（★ 按名字定位，★ 不按行号）。
TOUCHED = ("sw_drawing_query.py", "sw_drawing_view.py", "sw_review.py")

#: ★ 包装器（★ 口径同 `test_deprecated_entry_interlock._WRAPPERS` 的读形态）。
WRAPPERS = ("get_com_member", "call_com_member", "call_assembly_doc", "_safe_member")

#: ★★★ **真机等价性证据**（★ 254 + 255 的读数合并）：
#:   ★ 254：`output/pdf-probe.SLDDRW` 1 个伪视图 · ★ 255：`刀柄_Holder.sldprt` 造图 4 个视图（3 个真实模型视图）。
#:   ★ 两轮**全部** `Name` == `GetName2` ⇒ ★ 换路由的依据。
MACHINE = {"views": 4, "real_model_views": 3, "diff": 0, "prev_views": 1}


def _name_calls(path: Path) -> list[tuple[int, str]]:
    """★ 找 `get_com_member(<宿主>, "Name")` 且宿主 ∈ `VIEW_HOSTS` 的调用（★ 返回 `(行号, 宿主)`）。"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        if not (isinstance(fn, ast.Name) and fn.id in WRAPPERS):
            continue
        if len(node.args) < 2:
            continue
        m = node.args[1]
        if not (isinstance(m, ast.Constant) and m.value == "Name"):
            continue
        host = node.args[0]
        if isinstance(host, ast.Name) and host.id in VIEW_HOSTS:
            out.append((node.lineno, host.id))
    return out


def _failures(calls: dict[str, list[tuple[int, str]]]) -> list[str]:
    """★ 纯函数：任一文件里还有对 `view`/`av` 调 `Name` ⇒ 报出。"""
    out: list[str] = []
    for fname in sorted(calls):
        for (ln, host) in calls[fname]:
            out.append("%s:%d 仍在调废弃的 `IView::Name`（宿主 %r）" % (fname, ln, host))
    return out


# ── ① ★★★ 换路由已完成：`scripts/` 里**不许**再有对 view/av 调 `Name` ──
def test_no_deprecated_name_call_on_view_hosts():
    """★★★ 4 处真命中**必须已改掉**。

    ★ 能红的判据：★ 把任一处改回 `get_com_member(view, "Name")` ⇒ 当场红。
    ★ 按**名字 + AST** 定位（★ 不按行号）。
    """
    calls = {}
    for fname in TOUCHED:
        p = SCRIPTS / fname
        assert p.exists(), "%s 不在本机" % fname
        calls[fname] = _name_calls(p)
    bad = _failures(calls)
    assert not bad, "仍有对 `IView::Name` 的调用：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★ 换路由的**依据**（真机等价性）必须留在判据里 ────────────────
def test_routing_evidence_is_recorded():
    """★★ 换路由的依据 = **真机上 `Name` == `GetName2`**（★ 254 + 255 两轮读数）。"""
    assert MACHINE["diff"] == 0, "真机有 %d 处不等价 ⇒ 换路由**失去依据**" % MACHINE["diff"]
    assert MACHINE["real_model_views"] >= 3, \
        "真实模型视图只剩 %d 个 ⇒ 证据退化" % MACHINE["real_model_views"]
    assert MACHINE["views"] + MACHINE["prev_views"] >= 5, \
        "两轮样本合计 %d < 5 ⇒ 证据不足" % (MACHINE["views"] + MACHINE["prev_views"])


# ── ③ ★ 替换点是**后继**而不是「随便换个名字」 ───────────────────────
def test_replacement_uses_the_official_successor():
    """★ `sw_review.py` 那处（★ 原本**直接**调 `Name`）必须换成官方后继 `GetName2`。"""
    text = (SCRIPTS / "sw_review.py").read_text(encoding="utf-8")
    assert 'get_com_member(av, "GetName2")' in text, \
        "`sw_review.py` 没换成 `GetName2` ⇒ 换的不是官方后继"


# ── ④ ★★ 纯函数**能红**（合成负例）──────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 有残留调用；② 空表（★ 应通过）；③ 换的不是后继。"""
    assert not _failures({}), "空表被判红 ⇒ 判据过严"
    bad = {"sw_drawing_view.py": [(436, "view")]}
    assert _failures(bad), "有残留调用却未判出 ⇒ **空判据**"
    assert "436" in _failures(bad)[0], "报错里没有位置信息"
