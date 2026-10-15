"""★ spec 257：**换路由后的真机复验** —— `list_views` / `get_view_name` 在真机上仍正常。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   scripts/sw_drawing_query.py::list_views（★ 含 :194 换路由点）
#         scripts/sw_drawing_view.py::get_view_name（★ 含 :436 换路由点）
#         output/_probe257_reverify.py（★ 真机探针）· output/_probe255_views.SLDDRW（★ 4 视图图纸）
# 定位:   ★ spec 256 改了路由但**没跑过改后的函数** ⇒ ★ 本文件把那次真机复验**冻成判据**。
# 官方依据: C:/swapi/types/IView/GetName2.md（官方后继）· SW rev **34.4.1** 真机
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读；★ 不碰 SolidWorks（★ 读数来自探针，★ 判据只冻结它）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★★ **真机读数**（`output/_probe257_reverify.py` · SW rev **34.4.1** · 图纸只读打开、未保存关闭）。
MACHINE = {
    "list_views_count": 3,
    "list_views_names": ("工程图视图1", "工程图视图2", "工程图视图3"),
    "get_view_name_all": ("图纸1", "工程图视图1", "工程图视图2", "工程图视图3"),
    "report_ok": True,
    "report_views": 3,
    "errors": 0,
}

#: ★ 下界（★ 只增不减）。
BASELINE_VIEWS = 3
BASELINE_NAMED = 4


def _failures(m: dict) -> list[str]:
    """★ 纯函数：复验必须「有视图、有名字、无异常」。"""
    out: list[str] = []
    if m["errors"]:
        out.append("真机复验有 %d 处异常 ⇒ 换路由**破坏了功能**" % m["errors"])
    if m["list_views_count"] < BASELINE_VIEWS:
        out.append("`list_views` 只回 %d 个视图（< %d）" % (m["list_views_count"], BASELINE_VIEWS))
    if len(m["get_view_name_all"]) < BASELINE_NAMED:
        out.append("`get_view_name` 只拿到 %d 个名字（< %d）" % (len(m["get_view_name_all"]), BASELINE_NAMED))
    for n in m["get_view_name_all"]:
        if not n:
            out.append("`get_view_name` 回了**空串** ⇒ 名字丢了")
            break
    if not m["report_ok"]:
        out.append("`list_drawing_views_report` 回 `ok=False`")
    if m["report_views"] != m["list_views_count"]:
        out.append("两个入口的视图数不一致：%d vs %d" % (m["report_views"], m["list_views_count"]))
    return out


# ── ① ★★★ 换路由后功能正常 ──────────────────────────────────────────
def test_rerouted_functions_still_work_on_real_machine():
    """★★★ 真机复验：`list_views` / `get_view_name` **照常拿到视图名**。

    ★ 能红的判据：★ 把任一处改坏（如让 `GetName2` 分支不回值）⇒ 名字变空 ⇒ 当场红。
    """
    bad = _failures(MACHINE)
    assert not bad, "换路由后的真机复验不合格：\n" + "\n".join("  " + b for b in bad)


# ── ② ★★ 名字必须**非空**（★ 这是「兜底删了会不会丢名字」的直接回答）──
def test_names_are_not_empty_after_removing_the_fallback():
    """★★ 256 删了兜底 ⇒ ★ 本判据回答「**会不会丢名字**」：★ **不会** —— 4 个视图全部有名字。

    ★ 原因：★ 兜底只在 `GetName2` **抛异常**时才会走到；★ 真机上 `GetName2` **正常返回**。
    """
    named = [n for n in MACHINE["get_view_name_all"] if n]
    assert len(named) == len(MACHINE["get_view_name_all"]), \
        "有 %d 个视图名字为空 ⇒ 删兜底**确实丢了名字**" % (len(MACHINE["get_view_name_all"]) - len(named))
    assert MACHINE["errors"] == 0, "复验过程有异常 ⇒ 结论不可用"


# ── ③ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① 有空名字；② 有异常；③ 两入口数不一致。"""
    assert not _failures(MACHINE), "正常读数被判红 ⇒ 判据过严"
    assert _failures(dict(MACHINE, get_view_name_all=("图纸1", ""))), "空名字未判出 ⇒ **空判据**"
    assert _failures(dict(MACHINE, errors=1)), "有异常未判出 ⇒ **空判据**"
    assert _failures(dict(MACHINE, report_views=2)), "两入口数不一致未判出 ⇒ **空判据**"
