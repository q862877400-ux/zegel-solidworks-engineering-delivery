"""★ 测「探针复用」门禁（`scripts/check_probe_reuse.py`）—— ★ 含**负例**（事实 62）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   tests/test_probe_reuse_gate.py
# 定位:   ★ 事实 62：「**一个门禁「写了」不等于它「有效」—— 负例测试是唯一的证明**」⇒
#           ★★ 本测试的**负例是主角**：★ 喂一个「**就是某工具的替代品**」的探针样本
#             ⇒ ★ **门禁必须命中并点名那个工具** ✓
#         ★★ 三条对照（都是**必须不命中**的形态）：
#           ① 名字**不是**冲着那个能力去的（★ 探针为搭测试几何调了某工具 ⇒ 不算重复）；
#           ② 名字对得上、但**没有调用证据**（★ 只有名字一致，不能定罪）；
#           ③ `from pathlib import Path` / `import json` 这类**标准库导入**（★ 事实 51：
#              分析范围必须贴合「**哪些模块才是本仓的 scripts 模块**」这个组织单元）✓
#         ★★ 另有**正例**：★ 真仓当前的命中**必须逐条对上基线**（新增即失败、基线腐坏也失败）。
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_probe_reuse as gate                                          # noqa: E402

BASELINE = ROOT / "docs" / "probe-reuse-baseline.json"

#: ★ **人造的工具表**（★ 负例不依赖真仓的工具清单 ⇒ ★ 真仓加/删工具时这些断言不会漂 ✓）
FIXTURE_IMPL = {"solidworks_widget_params": [("sw_feature_readback", "widget_params")]}
#: ★ 「就是替代品」的样本：★ 名字**冲着 `widget_params` 去**、★ 而且**真的调了它的实现** ✓
PROBE_DUPLICATE = (
    "import sys\n"
    "sys.path.insert(0, r'D:\\AI\\SW\\scripts')\n"
    "from sw_feature_readback import widget_params\n"
    "print(widget_params(model))\n"
)


def test_negative_duplicate_probe_is_caught() -> None:
    """★★ **负例**（事实 62）：★ 名字对应 ∧ 有调用证据 ⇒ **必须命中并点名工具** ✓"""
    hits = gate.analyse_probe("tools/probe_widget_params_recheck.py", PROBE_DUPLICATE, FIXTURE_IMPL)
    assert hits, "★ 负例**没有**被拦住 ⇒ 门禁抓不到它真正要抓的东西（事实 62）"
    assert hits[0]["tool"] == "solidworks_widget_params", hits
    assert (hits[0]["module"], hits[0]["function"]) == ("sw_feature_readback", "widget_params"), hits
    assert hits[0]["line"] > 0, "★ 报错要给出**行号** ⇒ 否则定位不了：%r" % hits


def test_name_mismatch_is_not_flagged() -> None:
    """★ 对照①：★ 同样的调用，**换个不是冲那个能力去的**探针名 ⇒ **不许命中**。

    ★ 这正是第一版判据的假阳性来源：★ 探针**为了搭测试几何**先 `extrude_boss` 建个方块，
      ★ 它调到了 `solidworks_extrude_boss` 的实现，★ 但**那不是这个探针要验的能力** ✗
    """
    hits = gate.analyse_probe("tools/probe_a4_runtime_evidence.py", PROBE_DUPLICATE, FIXTURE_IMPL)
    assert hits == [], "★ 名字不对应却命中了 ⇒ 会把「搭测试几何」也报成重复（噪声淹没信号）：%r" % hits


def test_name_match_without_call_is_not_flagged() -> None:
    """★ 对照②：★ 名字对得上、但**没调那个实现** ⇒ **不许命中**（★ 只有名字一致不能定罪）。"""
    src = "from sw_feature_readback import other_thing\nother_thing()\n"
    hits = gate.analyse_probe("tools/probe_widget_params_recheck.py", src, FIXTURE_IMPL)
    assert hits == [], "★ 没有调用证据却命中了：%r" % hits


def test_stdlib_imports_are_not_script_modules() -> None:
    """★ 对照③（**事实 51 的回归位**）：★ 标准库导入**不许**被当成「本仓 scripts 模块」。

    ⚠ 第一版漏了这个白名单 ⇒ `json.dumps` / `pathlib.Path` 被塞进「工具实现」表 ⇒
      ★ 报出 **2112 处**假阳性 ✗
    """
    assert gate._imported_symbols(ast.parse("from pathlib import Path\nPath('x')\n")) == {}
    assert gate._imported_symbols(ast.parse("import json\njson.dumps({})\n")) == {}
    assert gate._imported_symbols(
        ast.parse("from scripts.sw_part import extrude_boss\n")
    ) == {"extrude_boss": ("sw_part", "extrude_boss")}
    assert gate._imported_symbols(
        ast.parse("from scripts import sw_part as sp\n")
    ) == {"sp": ("sw_part", None)}


def test_current_tree_matches_baseline() -> None:
    """★ 正例：★ 真仓当前的命中**必须逐条对上基线** —— ★ 新增即失败、基线腐坏也失败 ✓"""
    entries = json.loads(BASELINE.read_text(encoding="utf-8"))["entries"]
    known = {(e["probe"], e["tool"]) for e in entries}
    got = {(h["probe"], h["tool"]) for h in gate.scan()}
    assert not (got - known), "★ 有**没登记**的命中（新犯的）⇒ 请改走工具层或登记理由：%r" % sorted(got - known)
    assert not (known - got), "★ 基线里认了、实际已不存在 ⇒ **名单腐坏**，要跟着改：%r" % sorted(known - got)
    for e in entries:
        for f in ("probe", "tool", "module", "function", "reason"):
            assert str(e.get(f) or "").strip(), "★ 基线条目缺 `%s`（没有理由的豁免等于没写）：%r" % (f, e)
