"""★ `count_sketch_relations` 的 filter 契约：默认必须是 `0`（swAll），不是 `-1`。

## 这个缺陷

官方 `swSketchRelationFilterType_e` 里**没有 -1**：

| 成员 | 值 |
|---|---|
| **swAll** | **0** |
| swDangling | 1 |
| swOverDefining | 2 |
| swExternal | 3 |
| swDefinedInContext | 4 |
| swLocked | 5 |
| swBroken | 6 |
| swSelectedEntities | 7 |

⇒ 传 `-1` 时 SolidWorks **回 0 而不报错**。
⇒ 本仓库原来默认 `filter=-1`，于是函数与它挂的工具
  `solidworks_count_sketch_relations` **每次都报「0 条关系」**。

真机证据（`tools/probe_s3_fully_define_sketch.py`，同一张矩形草图）：
`GetRelationsCount(-1) = 0` 而 `GetRelationsCount(0) = 5`。

详见 `specs/350-first-part-delivery/s3-t008-dimension-driven.md` 第十一节。
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import sw_sketch_dimensions as D  # noqa: E402


def test_默认filter是0不是负一() -> None:
    """★★ 核心：默认值必须是 `0`（`swAll`）。"""
    sig = inspect.signature(D.count_sketch_relations)
    assert sig.parameters["filter"].default == 0, (
        "★ 默认 filter 必须是 0（swAll）；-1 不在官方枚举里，会静默回 0"
    )


def test_函数把filter原样传给COM(monkeypatch) -> None:
    """★ 函数不得在内部「纠正」调用方传的值 —— 如实传下去。"""
    seen = {}

    class _Mgr:
        def GetRelationsCount(self, f):  # noqa: N802
            seen["filter"] = f
            return 21

    monkeypatch.setattr(D, "_relations", lambda model: _Mgr())
    monkeypatch.setattr(
        D, "get_com_member", lambda obj, name, *a: getattr(obj, name)(*a)
    )
    assert D.count_sketch_relations(object(), 0) == 21
    assert seen["filter"] == 0
    D.count_sketch_relations(object(), 5)
    assert seen["filter"] == 5


def test_工具声明的默认值也是0() -> None:
    """★ 挂成工具时 `Param` 的默认值同样必须是 0。"""
    src = (REPO / "mcp-server" / "tool_specs_batch103.py").read_text(encoding="utf-8")
    #: 找到 count_sketch_relations 那个 ToolSpec 段里的 Param("filter", ..., default=X)
    i = src.find('name="solidworks_count_sketch_relations"')
    assert i > 0
    seg = src[i : i + 2000]
    j = seg.find('"filter"')
    assert j > 0, "找不到 filter 参数"
    frag = seg[j : j + 400]
    assert "default=0" in frag, "★ 工具默认 filter 应为 0，实得片段：%r" % frag[:160]
    assert "default=-1" not in frag, "★ 仍有人把默认写回 -1"


def test_源码里不再把负一当全数(monkeypatch) -> None:
    """★ 防回归：函数的 docstring/实现不该再声称「-1 = 全部」。"""
    src = (REPO / "scripts" / "sw_sketch_dimensions.py").read_text(encoding="utf-8")
    i = src.find("def count_sketch_relations")
    seg = src[i : i + 2000]
    #: ★ 只查「旧的结论句」是否还在（新 docstring 会**引用**那句错的作历史记录，
    #:   所以不能简单搜字符串「-1 = 全部」）
    assert "Filter=-1 = 全部" not in seg, (
        "★ 仍把 -1 当全数写在结论位置 —— 那句是错的，会造成静默回 0"
    )
    assert "swAll = 0" in seg or "swAll** | **0" in seg or "swAll" in seg
