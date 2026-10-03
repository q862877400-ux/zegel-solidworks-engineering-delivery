"""★ 测 `sw_sketch_edit._active_sketch_segment_count` 的**取数对象**（★ 含负例）。

（★ 处置 SPEC `202-user-coverage-gaps` 的 SC-004：★ 第 2 条候选 `sketch_edit_ops`）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `scripts/sw_sketch_edit.py`（`_active_sketch_segment_count` / `convert_entities` /
#         `sketch_mirror`）· `scripts/sw_sketch.py`（`get_lines` / `get_arcs`）·
#         `tools/probe_sketch_edit_pending_evidence.py`（★ 真机探针、★ 只报不动）·
#         `output/sketch-edit-pending-evidence.json`
# 定位:   ★ **本轮修掉一个真 bug** —— ★ 真机读数先暴露它：★ 走这条取数路径时
#   `segments_before` / `segments_after` **都回 `null`** ⇒ ★ 让三态判据保守判 `ok=false`；
#   ★★ **而几何其实变了**（★ 同一次真机里另一条路径读到 **0 → 1**）✓
#   ★★★ **真因**：★ `sw_sketch.get_lines(sketch)` / `get_arcs(sketch)` 的**第一个形参是
#     `ISketch` 对象**（★ 内部第一句 `_require(sketch)`）—— ★ **而原来把 `model` 传了进去** ✓
#   ★★★★ **修后真机读数**（★ `output/sketch-edit-pending-evidence.json`）：
#     · `convert_entities` ⇒ ★ `{"ok": true, "segments_before": 0, "segments_after": 1,
#       "new_segments": 1, "official_return": true}` ✓
#     · `sketch_mirror`     ⇒ ★ `{"ok": True, "segments_before": 2, "segments_after": 3}` ✓
#   ★★★★★ **可复用判据**：★★★ **「取数为 `None`」与「真的没变」是两件事** ——
#     ★ 三态判据（★ 变了 True · ★ 没变 False · ★ **量不到 None**）的价值就在这里：
#     ★★ **它没把"量不到"骗成 False**，★ 才让真因（传错对象）被查出来 ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_sketch_edit.py"
SK = REPO / "scripts" / "sw_sketch.py"
EVID = REPO / "output" / "sketch-edit-pending-evidence.json"


def _fn_src(name: str) -> str:
    tree = ast.parse(SRC.read_text(encoding="utf-8", errors="replace"))
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == name:
            return ast.unparse(n)
    return ""


def test_helper_fetches_active_sketch_before_calling_getters() -> None:
    """★★★ 核心断言：★ 取数前**必须先取 `ActiveSketch`**、★ 且**不许把 `model` 传下去** ✓"""
    code = _fn_src("_active_sketch_segment_count")
    assert code, "★ 找不到那个助手"
    assert "ActiveSketch" in code, "★ 没有先取 ActiveSketch（★ 那正是本轮的 bug）"
    #: ★★ 判据：★ `get_lines` / `get_arcs` 的实参**不能是裸 `model`** ✓
    assert "get_lines(sketch)" in code or "get_lines(sketch," in code, (
        "★ `get_lines` 的实参不是 sketch ⇒ 又会取不到（★ 本轮的 bug 会复发）")
    assert "get_arcs(sketch)" in code or "get_arcs(sketch," in code, (
        "★ `get_arcs` 的实参不是 sketch")
    for bad in ("get_lines(model)", "get_arcs(model)"):
        assert bad not in code, "★ 又出现了 `%s`" % bad


def test_the_getters_really_require_a_sketch_object() -> None:
    """★★★ 前提断言：★ `sw_sketch.get_lines/get_arcs` 的**第一个形参**确实叫 `sketch` ✓

    ★★ 若哪天它们改成收 `model`，★ 本轮那条判据就不再必要 ⇒ ★ **本测试会红、★ 那时可以简化** ✓
    """
    t = SK.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(t)
    want = {"get_lines", "get_arcs"}
    seen = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name in want:
            seen[n.name] = [a.arg for a in n.args.args]
    assert set(seen) == want, "★ 找不到那两个取数函数：%r" % sorted(seen)
    for name, args in seen.items():
        assert args and args[0] == "sketch", (
            "★ `%s` 的第一个形参变成 %r 了 ⇒ 本判据要重看" % (name, args[:1]))


def test_negative_case_the_three_state_rule_is_kept() -> None:
    """★★★★ **负例 · 三态判据不许退化**：★ 取不到时**不能**当成 0/False ✓

    ★★ 判据出处：★ 本仓的定则「变了 True · 没变 False · **量不到 `None`（不许报成功）**」⇒
      ★★★ 若这条退化成"取不到就当 False"，★ 那本轮的 bug **永远不会被发现** ✓
    """
    code = _fn_src("_active_sketch_segment_count")
    assert "return None" in code, "★ 没有 None 分支 ⇒ 三态判据退化了"
    assert "if sketch is None" in code, "★ 取不到草图对象时没有直接回 None"
    #: ★ 不许把 None 兜成 0
    for bad in ("or 0) + (n_arcs or 0)", ):
        assert bad in code, "★ 计数合成的写法变了，请重看三态语义"


def test_negative_case_evidence_shows_both_layers_true() -> None:
    """★★★ **负例 · 证据要两层都真**：★ 官方布尔 **and** 计数变化 **都**为真 ✓

    ★★ 为什么两层：★ 本仓那条规则逐字是「★ **跨种类 ⇒ `and`**」——
      ★ 官方 `bool` 是**对象类**判据、★ 计数变化是**结构类**判据 ⇒ **两层都要** ✓
      （★ 单靠官方布尔 ⇒ 就回到"官方回 true 而几何没变"那个坑，★ 见事实 486）
    """
    if not EVID.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(EVID.read_text(encoding="utf-8", errors="replace"))
    rows = {r["项"]: r for r in (d.get("rows") or [])}
    assert rows, "★ 证据里没有 rows"
    for item, r in rows.items():
        raw = r.get("返回")
        if not raw:
            continue
        try:
            got = json.loads(raw) if isinstance(raw, str) else raw
        except Exception:                                                 # noqa: BLE001
            continue
        assert got.get("ok") is True, "★ `%s` 的能力层判据不是 True：%r" % (item, got)
        b, a = got.get("segments_before"), got.get("segments_after")
        assert b is not None and a is not None, (
            "★ `%s` 的段数取数为 None ⇒ 就是本轮那个 bug 复发了" % item)
        assert a > b, "★ `%s` 的几何没变（%s → %s）⇒ 不算建成" % (item, b, a)
