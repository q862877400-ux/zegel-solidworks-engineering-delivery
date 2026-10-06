"""★ 实证覆盖层的契约与负例（规格 210 · B3/B4）：★ 实证**优先于**静态。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `docs/effect-observed.json` + `mcp-server/tool_registry.py` 的 `observed_writes` /
#      `effective_writes`（★ 判序：显式声明 → **实证** → 静态 → 未知）
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B3 收尾 + B4**。★ 评审的设计原话：
#   ★「**静态当提案与否决票，运行时实证当实证，两者都通过才开**」✓
# 判据:   ★★ **实证优先**：★ 静态说「无写」而实证观察到改动 ⇒ ★ **以实证为准** ✓
#   ★★ 负例（★ 不许颠倒）：★ **静态说「有写」不许被实证的「没变」翻成无写** ——
#      ★ 因为「没变」可能只是**没跑到**；★ 而「变了」是**确凿的** ✓（保守方向不对称）
# 官方依据: 读数出处见 `scripts/sw_fingerprint.py` 的 `OFFICIAL`
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "mcp-server"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import tool_registry as TR                                     # noqa: E402

OBS = ROOT / "docs" / "effect-observed.json"


def _spec(name):
    import register_capabilities as rc
    for s in rc.all_specs():
        if s.name == name:
            return s
    return None


def test_overlay_file_exists_and_marks_its_reason():
    assert OBS.is_file(), "★ 缺实证覆盖层：跑 python tools/gen_observed_effects.py"
    d = json.loads(OBS.read_text(encoding="utf-8"))
    assert "静态漏报" in d["_why"], d["_why"]


def test_observed_beats_static_for_the_two_real_findings():
    """★★ **真机抓到的两条**（★ 硬红门禁的产出）⇒ ★ 它们现在必须是**非只读** ✓

    ★★ 这两条是 B3 目前**最有价值的产出**：★ 静态说「无写」、★ 真机观察到**改了状态** ⇒
      ★ 若不覆盖，★ 它们会继续被当只读（★ 那会让 B4 对它们**开自动重试** ✗）
    """
    idx = json.loads(OBS.read_text(encoding="utf-8"))["tools"]
    for name in ("solidworks_assembly_check_interference", "solidworks_motion_create_study"):
        assert name in idx, "★ 这两条真机发现不在覆盖层里：%s" % name
        s = _spec(name)
        assert s is not None
        assert TR.observed_writes(s), name
        assert TR.effective_read_only(s) is False, "★ 实证抓到的工具仍被当只读：%s" % name


def test_overlay_only_contains_observed_changes():
    """★ 覆盖层里**只许有**「观察到变化」的条目（★ 没变的不进 —— ★ 那会把「没跑到」当结论）✓"""
    idx = json.loads(OBS.read_text(encoding="utf-8"))["tools"]
    for name, rec in idx.items():
        assert rec.get("writes"), "★ 覆盖层里有 writes 为空的条目：%s" % name
        assert rec.get("source") == "observed", name


def test_static_readonly_is_not_flipped_back_by_a_no_change_observation():
    """★★ **负例（不对称）**：★ 「**没变**」**不许**把静态的「有写」翻成无写 ——
    ★ 因为「没变」可能只是**没跑到**；★ 而「变了」是**确凿的** ⇒ ★ 保守方向**不对称** ✓
    """
    class _S:
        name = "__synthetic__"
        writes = ("document",)
    assert TR.effective_writes(_S()) == ("document",)
