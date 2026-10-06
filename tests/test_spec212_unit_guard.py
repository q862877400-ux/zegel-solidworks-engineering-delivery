"""★ 规格 212 · D-5：返回出口**单位守卫**的契约与负例（★ 不连真机、不连 MCP）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`mcp-server/server.py` 的 `_unit_guard` / `_unit_suffix_of`）
# 文件:   tests/test_spec212_unit_guard.py
# 定位:   ★ 规格 `specs/212-unit-discipline` 的 **D-5**。★ `_result()` 是**工具结果出 JSON 的
#   唯一出口** ⇒ ★★ 守卫加在那里**一次覆盖全部工具** ✓
# 判据:   ★★ **确定性**（★ 判据就是"后缀在不在已知集合"，★ 不猜语义、★ 不靠 LLM）：
#     ★ ① 键名带**已知**单位后缀 ⇒ **放行**
#     ★ ② 键名**不像**单位（`stage` / `depth_foo`）⇒ **放行**（★ 门禁不管没声明的东西 ✓）
#     ★ ③ 键名**像**单位但**不在已知集合**（`_inch` / `_ft` / `_yd`）⇒ **报**
#     ★ ④ ★★ **嵌套 dict 里**的键 ⇒ **报**（★ 静态 AST 看不到这里 ✗）
#     ★ ⑤ ★★ **列表元素里**的键 ⇒ **报**（★ 同上）
#     ★ ⑥ ★ 守卫**自己出错也不许影响工具**（★ 与规格 210 的预检同一纪律）✓
#   ★★ **只报不拦的铁证**：★ ⑥ 与"返回值不改"两条 —— ★ 守卫**绝不抛、绝不改 payload** ✓
#   ★ 开关：★ `SW_UNIT_GUARD=off` 可关 ✓
# 官方依据: 无（本仓约定 `docs/union-conventions.md` **规则 2b**）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "mcp-server"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import server as S                                             # noqa: E402


# ── ① 放行：已知单位后缀 ────────────────────────────────────────────────────
@pytest.mark.parametrize("key", ["volume_mm3", "area_mm2", "depth_mm", "padding_m",
                                 "angle_deg", "top_px", "elapsed_s", "mass_kg"])
def test_known_unit_suffixes_pass(key):
    assert S._unit_guard({key: 1.0}, "t") == []


# ── ② 放行：不像单位的键（★ 门禁不管"没声明"的东西）──────────────────────────
@pytest.mark.parametrize("key", ["stage", "op", "count", "depth_foo", "output",
                                 "document", "retryable", "schemaVersion"])
def test_non_unit_keys_pass(key):
    assert S._unit_guard({key: 1}, "t") == []


# ── ③ 负例：像单位但不在已知集合 ⇒ 必须报 ───────────────────────────────────
@pytest.mark.parametrize("key", ["depth_inch", "padding_ft", "gap_yd", "width_mil"])
def test_unitlike_but_unknown_suffix_is_reported(key):
    hits = S._unit_guard({key: 1.0}, "t")
    assert len(hits) == 1 and key in hits[0]


# ── ④ 负例：**嵌套** dict 里的 ⇒ 必须报（★ 静态 AST 看不到）────────────────
def test_nested_dict_key_is_reported():
    hits = S._unit_guard({"status": "ok", "detail": {"inner_ft": 2.0}}, "t")
    assert len(hits) == 1 and "inner_ft" in hits[0]


# ── ⑤ 负例：**列表元素**里的 ⇒ 必须报（★ 静态 AST 看不到）──────────────────
def test_list_element_key_is_reported():
    hits = S._unit_guard([{"a_mm": 1.0}, {"a_yd": 2.0}], "t")
    assert len(hits) == 1 and "a_yd" in hits[0]


# ── ⑥ 只报不拦：★ 守卫**绝不改 payload、绝不抛** ────────────────────────────
def test_guard_never_mutates_payload():
    payload = {"depth_inch": 1.0, "nested": {"x_ft": 2.0}}
    import copy
    before = copy.deepcopy(payload)
    S._unit_guard(payload, "t")
    assert payload == before, "★ 守卫不许改 payload（只报不拦）"


def test_guard_swallows_its_own_errors():
    """★ **负例**：★ 传一个**必然让它出错**的对象（★ 键的 `__str__` 抛）⇒ ★ 必须**回空表、不抛** ✓

    ★ 依据：★ 与规格 210 的预检同一纪律 —— ★ **守卫自己出错不许影响工具** ✓
    """
    class _Boom:
        def __str__(self):  # pragma: no cover - 故意抛
            raise RuntimeError("boom")

        def __repr__(self):  # pragma: no cover
            raise RuntimeError("boom")

    #: ★ `_scan_unit_keys` 只在 `isinstance(k, str)` 时用键 ⇒ ★ 这里用一个**会让递归抛**的映射
    class _BadDict(dict):
        def items(self):
            raise RuntimeError("boom")

    assert S._unit_guard(_BadDict(), "t") == []


# ── ⑦ 开关：`SW_UNIT_GUARD=off` ⇒ 完全不报 ─────────────────────────────────
def test_switch_off(monkeypatch):
    monkeypatch.setenv("SW_UNIT_GUARD", "off")
    assert S._unit_guard({"depth_inch": 1.0}, "t") == []
