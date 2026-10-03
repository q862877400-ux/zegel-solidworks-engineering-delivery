"""★ 测「6 个回读能力**挂进了 ToolSpec**」+ 端到端读数（★ 阶段 5 的完整判据 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `mcp-server/tool_specs_batch77.py`（★ 新）· `output/e2e_readback_tools.py`（★ 只报不动）·
#         `output/e2e-readback-tools.json`（★ 证据）
# 定位:   ★ 任务书阶段 5 逐字：「每格：查官方签名 → 建能力 → **挂 ToolSpec** → 真机验证 → 提交」⇒
#   ★★ **本测试守的是我自己漏掉的那一环** ✓
#   ★★★ **起因（★ 可核）**：★ 我在轮 95–102 补了 6 个回读能力、★ 做了建能力与真机验证、
#     ★★ **却没挂 ToolSpec** ⇒ 真机查（★ `output/_check_readback_toolspecs.py`）：
#       ★ **6 个全部「没有」** · ★★ **与 `feature_readback` 相关的 ToolSpec 一个都没有** ✓
#   ★★★★ **端到端读数**（★ `output/e2e-readback-tools.json`）：
#     ★ **5 / 6 通过** —— ★ `extrude_depth` · ★ `extrude_params` · ★ **`hole_params`**（★ 回 `异型孔向导`）·
#       ★ `feature_info` · ★ **`fillet_params`**（★ 回 `圆角1` · ★ `DefaultRadius = 5.0`）✓
#     ★★ **唯一不过的是 `pattern_params`** —— ★ 而它的**前置**（建阵列）回了 `None` ⇒
#       ★★★ **⇒ 那是"前置没成"、★ 不是"读能力不成"** ✓
#   ★★★★★ **可复用判据**：★★★ **「建成了能力」与「能力能被调」是两件事** ——
#     ★ 前者看**函数存在 + 真机读数**、★ 后者看**ToolSpec 清单里有没有它** ✓
#     ★★ 与**事实 40**（★ 一个存在但没人用的守卫与没有守卫等价）**同族** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "mcp-server"))
sys.path.insert(0, str(REPO / "scripts"))

BATCH = REPO / "mcp-server" / "tool_specs_batch77.py"
EVID = REPO / "output" / "e2e-readback-tools.json"

WANT = ["solidworks_extrude_depth", "solidworks_extrude_params",
        "solidworks_pattern_params", "solidworks_hole_params",
        "solidworks_feature_info", "solidworks_fillet_params"]


def test_all_six_are_registered_as_toolspecs() -> None:
    """★★★ 核心断言：★ 6 个工具名**都在 `all_specs()` 里** ✓"""
    import register_capabilities as rc
    names = {getattr(s, "name", "") for s in rc.all_specs()}
    missing = [w for w in WANT if w not in names]
    assert not missing, "★ 这 %d 个没挂进 ToolSpec：%r" % (len(missing), missing)


def test_the_batch_is_listed_in_register_capabilities() -> None:
    """★★★ 核心断言：★ `batch77` **被列进发现表**（★ 否则挂了也没人读）✓"""
    t = (REPO / "mcp-server" / "register_capabilities.py").read_text(
        encoding="utf-8", errors="replace")
    assert "tool_specs_batch77" in t, "★ batch77 没进 `BATCH_MODULES`"


def test_negative_case_every_spec_injects_model() -> None:
    """★★★ **负例 · 契约要对**：★ 6 条的 `inject` 都必须是 `model` ✓

    ★★ **为什么**：★ 那 6 个能力的首个形参都是 `model` ⇒
      ★★★ **`inject` 写错会让工具层给错对象、★ 而报的错看起来像"能力坏了"** ✓
      （★ 与**事实 36/51**同族）✓
    """
    import register_capabilities as rc
    specs = {getattr(s, "name", ""): s for s in rc.all_specs()}
    for w in WANT:
        s = specs.get(w)
        assert s is not None, "★ %s 没挂" % w
        assert getattr(s, "inject", None) == "model", (
            "★ `%s` 的 inject 是 %r、★ 期望 `model`" % (w, getattr(s, "inject", None)))


def test_negative_case_the_e2e_reading_is_recorded() -> None:
    """★★★★ **负例 · 端到端读数要落盘**：★ 含**5/6** 与那条**前置没成**的原因 ✓

    ★★ **为什么**：★ 若只写"6 条都挂了"就收工 ⇒
      ★★★ **那是"清单里有它"、★ 不是"它能被调"**（★ 正是本轮要修的那个错）✓
    """
    if not EVID.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(EVID.read_text(encoding="utf-8", errors="replace"))
    assert d.get("总数") == 6, "★ 总数不是 6：%r" % d.get("总数")
    assert d.get("通过") == 5, (
        "★ 通过数变成 %r ⇒ ★ 要么修好了、要么退化了 ⇒ 判据要重看" % d.get("通过"))
    #: ★★ 那条没过的必须**写明是前置没成**（★ 而不是含糊"失败"）✓
    bad = [r for r in (d.get("rows") or []) if not r.get("ok")]
    assert len(bad) == 1, "★ 不过的条数不是 1：%r" % [r.get("tool") for r in bad]
    assert "找不到" in str(bad[0].get("read")), (
        "★ 那条不过的**不是**「找不到 X 特征」⇒ 真因变了、要重看：%r" % bad[0].get("read"))
    #: ★★★ 前置那一栏也要在（★ 它才是"为什么找不到"的答案）✓
    assert any("前置" in k for k in d), "★ 没记前置栏：%r" % sorted(d)
