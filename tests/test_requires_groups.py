"""★ `requires` 推导的契约与负例（规格 210 · B3 的分组基数）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/effect_rules.py` 的 `INJECT_REQUIRES` / `derive_requires`
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B3**。★ 起因（真机读数）：
#   ★★ `nonempty` 组抽样的失败**全部**是「声明注入 X 但没给对应对象」⇒
#     ★ **B3 的分组要按「需要什么宿主对象」来分**，★ 而那个信息**声明里已经有**（`inject`）✓
# 判据:   ★★ `derive_requires` 只做一件事：★ 把**声明里的 `inject` 种类**映射成**分组键** ✓
#   ★★ 负例（★ 本仓一贯纪律「不许蒙混」）：★ **认不出的注入名** ⇒ ★ **不许静默归到某个已知组**，
#      ★ 必须带前缀 `host:` **原样带回**（★ 于是它自成一组、★ 且看得见）✓
# 官方依据: 无 —— ★ 这是**我方分组口径**，如实标注 ✓
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "mcp-server"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from effect_rules import INJECT_REQUIRES, derive_requires   # noqa: E402


def test_known_injects_map_to_their_group():
    assert derive_requires("model") == "part"
    assert derive_requires("asm_model") == "assembly"
    assert derive_requires("drawing_model") == "drawing"
    assert derive_requires("view") == "view"
    assert derive_requires("sldworks") == "app"
    assert derive_requires("") == "none"


def test_unknown_inject_is_not_silently_folded_into_a_known_group():
    """★★ **负例**：★ 认不出的注入名 ⇒ ★ **不许**静默归到某个已知组 ⇒
    ★ 必须带 `host:` 前缀**原样带回**（★ 于是它自成一组、★ 也看得见）✓"""
    got = derive_requires("some_new_thing")
    assert got == "host:some_new_thing", got
    assert got not in set(INJECT_REQUIRES.values()), "★ 被静默归进了某个已知组"


def test_every_mapping_value_is_a_small_token():
    """★ 分组键必须是**短标记**（★ 组数才可能少 —— ★ 那是「不随工具数增长」的前提）✓"""
    assert all(isinstance(v, str) and v and " " not in v for v in INJECT_REQUIRES.values())
    assert len(set(INJECT_REQUIRES.values())) <= 12, sorted(set(INJECT_REQUIRES.values()))


def test_the_real_table_has_a_small_number_of_groups():
    """★★ 实证：★ 真实声明表里 `requires` 的种类数**必须很小**（★ 分组基数）✓

    ★★ 这条把评审的架构主张变成**可跑的判据**：★「耗时随**不同前置的数量**增长，
      ★ 不随工具数增长」—— ★ 若种类数逼近工具数，★ 那条主张就**不成立** ✓
    """
    import json
    table = json.loads((ROOT / "docs" / "effect-declarations.json").read_text(encoding="utf-8"))
    groups = {r.get("requires") for r in (table.get("tools") or {}).values()}
    assert len(groups) <= 15, sorted(groups)
    assert None not in groups, "★ 有工具没推出 requires"
