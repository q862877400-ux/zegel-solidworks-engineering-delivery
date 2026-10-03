"""★ 台账的 `capability_id` 提升：正例 + **负例**（★ 事实 62：负例是门禁有效的唯一证明）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（契约测试）
# 文件:   tests/test_toolbar_ledger_capability_promotion.py
# 定位:   ★ 2026-10-03（轮 549）★ 给「台账先查 capabilities」这条新判据**立负例**。
#
#   ★★ **它防的是什么**：`tools/build_toolbar_ledger.py` 的 `tier()` 原先只用**手填的 `level`**
#     —— ★ 而它自己的 docstring 写着「之后从不自动更新」⇒ ★ **做成了的能力台账永远不知道** ⚠
#     ★ 实测（轮 549）：★ 修前「已能 47」、**修后 54**。
#
#   ★★★ **而按事实 62**（一个门禁"写了"不等于它"有效" —— **负例测试是唯一的证明**）：
#     光测「指到 verified 就提升」**不够** —— ★ 还得测
#     **「指到 _非_ verified 就不该提升」**，★ 否则**变成"见 capability_id 就提升"**也照样绿 ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
GEN = R / "tools" / "build_toolbar_ledger.py"
CAPS = R / "capabilities.yaml"
LEDGER = R / "docs" / "toolbar-ledger.json"


def _load_funcs():
    """★ 从生成器里把 `promoted_by_capability` 与 `tier` **一起**抠出来跑。

    ★★★ 2026-10-03（轮 549）**为什么要两个**：★ 第一版我只抠 `tier` ⇒ 它读外层变量
      `_VERIFIED` ⇒ **`NameError`** ⚠ —— ★ **那是测试抓到的真缺陷**，
      ★ 故把那段逻辑改成**模块级 `promoted_by_capability`**、★ 而本函数**两个都抠**、
      并把 `VERIFIED_IDS` **注入命名空间** ✓
    ★ 这样测的是**真代码**（★ 不复制它的逻辑 —— 复制就等于测副本）。
    """
    src = GEN.read_text(encoding="utf-8")
    tree = ast.parse(src)
    want = {"promoted_by_capability", "tier"}
    fns = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in want]
    assert {f.name for f in fns} == want, "生成器里没找齐 %s" % sorted(want)
    mod = ast.Module(body=fns, type_ignores=[])
    ast.fix_missing_locations(mod)
    ns: dict = {"VERIFIED_IDS": set()}
    exec(compile(mod, str(GEN), "exec"), ns)          # noqa: S102
    return ns


def _verified_ids() -> set:
    caps = json.loads(CAPS.read_text(encoding="utf-8"))["capabilities"]
    return {c["id"] for c in caps if c.get("level") == "verified" and c.get("id")}


def _non_verified_id() -> str:
    caps = json.loads(CAPS.read_text(encoding="utf-8"))["capabilities"]
    for c in caps:
        if c.get("level") != "verified" and c.get("id"):
            return c["id"]
    raise AssertionError("capabilities.yaml 里没有非 verified 的条目 —— 负例无法构造")


def test_positive_promotes_when_capability_is_verified():
    """★ 正例：★ `capability_id` 指向**已 verified** 的能力 ⇒ 判「已能」。"""
    ns = _load_funcs()
    tier, _prom, ver = ns["tier"], ns["promoted_by_capability"], _verified_ids()
    ns["VERIFIED_IDS"] = ver
    vid = sorted(ver)[0]
    assert _prom({"capability_id": vid}, ver) is True, "promoted_by_capability 正例失效"
    assert tier({"capability_id": vid, "level": "不能"}) == "已能", (
        "指向 verified 的能力却没被提升为「已能」—— 本判据失效了")


def test_negative_does_not_promote_when_capability_is_not_verified():
    """★★ 负例（★ 事实 62）：★ 指向**非 verified** 的能力 ⇒ **不该**判「已能」。"""
    ns = _load_funcs()
    tier, _prom, ver = ns["tier"], ns["promoted_by_capability"], _verified_ids()
    ns["VERIFIED_IDS"] = ver
    nid = _non_verified_id()
    assert _prom({"capability_id": nid}, ver) is False, (
        "promoted_by_capability 对非 verified 也回 True ⇒ 判据退化了")
    got = tier({"capability_id": nid, "level": "不能", "api_verified": True, "entry": ""})
    assert got != "已能", (
        "指向**非 verified** 的能力也被提升为「已能」⇒ 判据退化成「见 capability_id 就提升」")
    assert got in ("可攻关", "待验证", "待查"), "落到了未知档：%r" % got


def test_negative_missing_capability_id_falls_back_to_hand_level():
    """★ 负例二：★ **没有** `capability_id` 时 ⇒ ★ 仍走手填 `level`（★ 不误提升）。"""
    ns = _load_funcs()
    ns["VERIFIED_IDS"] = _verified_ids()
    assert ns["tier"]({"level": "不能", "api_verified": True, "entry": ""}) != "已能"


def test_real_ledger_items_built_this_session_are_promoted():
    """★ 正例（★ 真实数据）：★ 本轮做成的 7 条，★ 现在必须是「已能」。"""
    raw = json.loads(LEDGER.read_text(encoding="utf-8"))
    items = raw if isinstance(raw, list) else (raw.get("items") or [])
    want = {
        "旋转曲面": "surface_revolve",
        "等距曲面": "surface_offset",
        "平面区域": "surface_planar_region",
        "替换面": "replace_face",
        "放样曲面": "surface_ref_ops",
        "水平尺寸": "sketch_dimension_horizontal",
        "竖直尺寸": "sketch_dimension_vertical",
    }
    ver = _verified_ids()
    by_zh = {str(i.get("zh")): i for i in items}
    for zh, cid in want.items():
        assert zh in by_zh, "台账里没有 %r" % zh
        assert cid in ver, "%s 在 capabilities 里不是 verified" % cid
        assert by_zh[zh].get("capability_id") == cid, (
            "台账条目 %r 的 capability_id 不是 %r ⇒ 生成器对不上号" % (zh, cid))
    ns = _load_funcs()
    ns["VERIFIED_IDS"] = ver
    for zh, cid in want.items():
        assert ns["tier"](by_zh[zh]) == "已能", "%s（%s）没有被提升为「已能」" % (zh, cid)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print("  ✓ %s" % name)
    print("  全部通过")
    sys.exit(0)
