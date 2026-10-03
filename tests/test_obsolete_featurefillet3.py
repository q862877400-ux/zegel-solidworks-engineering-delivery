"""★ 测 `fillet` 用的是**现行的 `FeatureFillet3`**（★ 阶段 2 · T1 · 含负例 · 含环形链真因）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + 本机三套源
# 文件:   `scripts/sw_part.py::fillet`（★ 生产）·
#         `tools/probe_featurefillet3.py`（★ 探针、★ 只报不动）·
#         `output/featurefillet3-probe-evidence.json`
# 定位:   ★ 阶段 2 · T1 的逐条流程 ①（查官方）+ ②（真机验证）+ ③（改）✓
#   ★★ **官方三页连读**：★ `FeatureFillet` 废弃 ⇒ `2` · ★ `FeatureFillet2` 废弃 ⇒ `3` ·
#     ★★★ **`FeatureFillet3` **不废弃** ⇒ 现行** ✓
#   ★★★ **⚠ 而追链时出现过"环形"**（★ `F → 2 → 3 → F`）—— **真因是**跨族同名****：
#     ★ `IModelDoc2` 上**也有一族** `FeatureFillet`（★ 5/7/9/13/7 参）、
#     ★★ 而它的"后继"写的是 **`IFeatureManager::FeatureFillet`** ⇒ ★ **跨族跳转成环** ✓
#     ⇒ ★★★ **按铁律 4 查反射定案**：★ `IFeatureManager` ⇒ 7 / 11 / **14**（★ `3` 是 14 参）✓
#   ★★★★ **真机对照**（★ `output/featurefillet3-probe-evidence.json`）：
#     ★ 旧 7 参 ⇒ **特征数 20 → 21** · ★★ 新 14 参 ⇒ **23 → 24** ⇒ ★ **两者都建成** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_part.py"
EVID = REPO / "output" / "featurefillet3-probe-evidence.json"
OFF3 = Path(r"C:\swapi\types\IFeatureManager\FeatureFillet3.md")
OFF2 = Path(r"C:\swapi\types\IFeatureManager\FeatureFillet2.md")


def test_official_chain_ends_at_three() -> None:
    """★★★ **前提断言**：★ 官方链在 `3` 收口（★ `2` 废弃、★ `3` 不废弃）✓"""
    if not (OFF3.is_file() and OFF2.is_file()):
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t3 = OFF3.read_text(encoding="utf-8", errors="replace")
    t2 = OFF2.read_text(encoding="utf-8", errors="replace")
    assert "Obsolete" not in t3, "★ `FeatureFillet3` 也被标废弃了 ⇒ 判据要重看"
    assert "Obsolete" in t2 and "FeatureFillet3" in t2, "★ `2` 的废弃链变了"


def test_code_calls_the_fourteen_arg_successor() -> None:
    """★★★ 核心断言：★ 生产代码调 `FeatureFillet3`、★ **且恰好 14 个实参** ✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    found = []
    for n in ast.walk(tree):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr in ("FeatureFillet", "FeatureFillet2", "FeatureFillet3")):
            found.append(n)
    assert found, "★ 找不到那个调用"
    for n in found:
        assert n.func.attr == "FeatureFillet3", (
            "★ 调的是 `%s`（★ 官方已废弃）" % n.func.attr)
        assert len(n.args) == 14, "★ 实参 %d 个、★ 官方要 **14** 个" % len(n.args)


def test_evidence_both_forms_built() -> None:
    """★★★ 核心断言：★ 证据里**两种形态都建成**（★ 特征数各 +1）✓"""
    if not EVID.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(EVID.read_text(encoding="utf-8", errors="replace"))
    rows = {r["form"]: r for r in d["rows"]}
    for form in ("old_7", "new3_14"):
        r = rows.get(form) or {}
        assert r.get("built") is True, "★ `%s` 没建成：%r" % (form, r.get("error"))
        assert r.get("bodies") == 1, "★ `%s` 的实体数不是 1：%r" % (form, r.get("bodies"))
        assert r.get("picked") is True, "★ `%s` 没选中边" % form


def test_negative_case_the_cyclic_chain_reason_is_recorded() -> None:
    """★★★ **负例 · 环形链的真因**：★ docstring 必须写明**跨族同名** ✓

    ★★ **为什么**：★ 下一轮若有人再追一遍链、★ 会**又撞上那个环** ⇒
      ★★★ **必须留下「按接口限定地追」这条判据** + ★ **两族的参数个数** ✓
      ★ 与**事实 36**同族（★ **同名接口分属不同族**）✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find("def fillet(")
    seg = t[i:i + 4600]
    assert "跨族" in seg, "★ 没写「跨族同名」这个真因"
    assert "IModelDoc2" in seg and "IFeatureManager" in seg, "★ 没点名那两族"
    assert "环形" in seg, "★ 没写「环形」这个现象"
    assert "按接口限定" in seg or "按接口" in seg, "★ 没留下「按接口限定地追」这条判据"
