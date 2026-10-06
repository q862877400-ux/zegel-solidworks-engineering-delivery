"""★ `needs` 机械初推的契约与负例（规格 210 · B3 第三次拆解）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/effect_rules.py` 的 `derive_needs` + `tools/survive_sweep.py` 的 `apply_needs`
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B3**。★ 起因（真机）：
#   ★★ 几条 `sketch_*` 报 `没有活动草图` / `不在草图编辑态`，★ `part_bounding_box` 报
#     `零件里可能没有实体` ⇒ ★★ 它们要的**不是「宿主对象」**，★ 而是**宿主处于某种状态** ✗
# 判据:   ★★ 只认**工具源码（含被调函数）里出现的说法** ⇒ ★ 认不出就是**空元组**（★ 不许瞎猜）✓
#   ★★ 并且：★ **推出来的顺序不等于施加的顺序** —— ★ 施加时 `edit:sketch` 必须**最后** ✓
#     ★（★ 真机：★ 我先推 `edit:sketch` 再推 `body`，★ 而 `body` 要 `extrude_boss`、
#       ★★ **那会退出草图** ⇒ ★ 把刚进的编辑态 undo 掉了 ✗ —— ★ 三条 `sketch_*` 全都不转）
# 官方依据: 报错话与成员名出自本仓工具自身的检查
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "mcp-server"), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from effect_rules import derive_needs                        # noqa: E402


def test_sketch_edit_state_is_derived():
    assert derive_needs("没有活动草图 ⇒ 先调 sketch_start") == ("edit:sketch",)
    assert "edit:sketch" in derive_needs("ISketchManager.ActiveSketch 为 None")


def test_body_need_is_derived():
    assert derive_needs("零件里可能没有实体") == ("body",)


def test_nothing_recognised_yields_an_empty_tuple_not_a_guess():
    """★★ **负例（★ 不许瞎猜）**：★ 源码里**没有**那几种说法 ⇒ ★ **空元组** ✓"""
    assert derive_needs("def f():\n    return 1\n") == ()


def test_real_tools_get_their_needs():
    """★ 实证：★ 那几条**真机失败过**的工具，★ `needs` 现在推出来了 ✓"""
    import json
    t = json.loads((ROOT / "docs" / "effect-declarations.json").read_text(encoding="utf-8"))["tools"]
    assert t["solidworks_sketch_fully_defined_status"]["needs"] == ["edit:sketch"]
    assert t["solidworks_sketch_mirror"]["needs"] == ["edit:sketch"]
    assert t["solidworks_part_bounding_box"]["needs"] == ["body"]


def test_apply_order_puts_edit_sketch_last():
    """★★★ **顺序判据**（★ 真机踩过）：★ `edit:sketch` **必须最后施加** ——
    ★ 因为 `body` 要调 `extrude_boss`、★ **那会退出草图** ⇒ ★ 先施加就白施加了 ✗

    ★ 判据是从**源码文本**里看施加顺序（★ 这是一个**形态判据**，★ 不依赖真机）✓
    """
    src = (ROOT / "tools" / "survive_sweep.py").read_text(encoding="utf-8")
    i = src.index('for n in ("')
    order = src[i:src.index("):", i)]
    assert order.index("edit:sketch") > order.index("body"), order
    assert order.index("edit:sketch") > order.index("selection"), order
