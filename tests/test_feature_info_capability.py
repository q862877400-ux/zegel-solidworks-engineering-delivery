"""★ 测 `feature_info`：★ **容器节点**与**基准面**这两处判据修正（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IFeature\`）
# 文件:   `scripts/sw_feature_readback.py::feature_info`（★ 阶段 3 补的能力 · 第五个）·
#         `tools/check_obsolete_heuristic.py`（★ 上一轮修的新判据）·
#         `tools/probe_feature_info_recheck.py` · `output/feature-info-capability-recheck.json`
# 定位:   ★ 阶段 3 · 按密度图补能力 ⇒ **第五个**、★ **第四个族**（★ `IFeature` ×51）✓
#   ★★ **本族先用**新判据**重扫**：★ **126 个成员** ⇒ ★ **真废弃 24** · ★ **没废弃 102** ⇒
#     ★★★ **而旧判据会多报 2 个假阳性**：★ `GetTypeName` · ★ **`GetTypeName2`** ⇒
#     ★★★★ **⇒ 而 `GetTypeName2` 正是本仓在用的那个** ⇒ **用它是对的** ✓
#   ★★★ **官方逐字**：★ `GetID()` ⇒ 「Feature ID of this feature」·
#     ★ `GetFaceCount()` ⇒ 「Number of faces in this feature」· ★ `Visible` ⇒ `swVisibilityState_e` ·
#     ★ `GetChildren()` ⇒ 「Array of child features」· ★ `GetParents()` ⇒ 父特征 ✓
#   ★★★★ **⚠ `GetBox` **不用**** —— ★ 官方 `## Remarks` 逐字「The values returned are **approximate**
#     and **should not be used for comparison or calculation purposes**」✓
#   ★★★★★ **真机 8/8 全过**（★ `output/feature-info-capability-recheck.json`）：
#     ★ `Name` 非空 · ★ **`GetFaceCount = 6`** · ★ `GetID = 79`（★ 正整数）·
#     ★ `GetChildren = 0` · ★ `GetParents = 2` · ★ `Visible` / `GetEditStatus` 是 int ·
#     ★ `CreatedBy = "Zegel"` ✓
#   ★★★★★★ **⚠ 而这条判据我改了**三次**（★ 值记）**：
#     ★ ① 兜底取 `FirstFeature` ⇒ 中文 UI 下回 **`收藏`**（★ 容器）⇒ `GetFaceCount = 0` ✓
#     ★★ ② 加 `_is_real_feature` ⇒ 而它**只判"有没有类型名"**、★ `收藏` 的 `FavoriteFolder`
#       **是一个类型名** ⇒ ★ **仍回 `收藏`** ⇒ 又改成**两层过滤**（★ 名字 + 类型名）✓
#     ★★★ ③ 过了两层 ⇒ 回 **`前视基准面`**（★ `RefPlane` · ★ **官方文档说基准面也是合法特征**）⇒
#       ★★ **而 `GetFaceCount = 0` 是**应然的****（★ 基准面没有面）⇒
#       ★★★ **⇒ 是我的判据"面数=6"只对**拉伸**成立** ⇒ **这次**按名字**取那个拉伸** ✓
#     ★★★★ **⇒ 三次都不是能力错、★ 是判据/兜底错**（★ 事实 51 的第三次实例）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_feature_readback.py"
EVID = REPO / "output" / "feature-info-capability-recheck.json"


def test_code_excludes_getbox_with_the_official_reason() -> None:
    """★★★ 核心断言：★ 代码里**不调 `GetBox`**、★ 且**写明官方理由** ✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    i = src.find("def feature_info(")
    assert i != -1, "★ 找不到 `feature_info`"
    seg = src[i:i + 5200]
    assert "GetBox" not in seg.split('"""')[-1], "★ 函数体里调了 `GetBox`（★ 官方说不可核）"
    assert "approximate" in seg, "★ 没引官方那句 `approximate`"
    assert "should not be used for comparison" in seg, "★ 没引官方的「不可用于比较或计算」"


def test_code_uses_the_two_layer_filter_in_the_fallback() -> None:
    """★★★ 核心断言：★ 兜底必须过**两层**（★ 名字 + `_is_real_feature`） ✓

    ★★ **为什么**：★ 只过第二层会回 `收藏`（★ 它的 `FavoriteFolder` **是一个类型名**）✓
    """
    src = SRC.read_text(encoding="utf-8", errors="replace")
    i = src.find("def feature_info(")
    seg = src[i:i + 5200]
    assert "_CONTAINER_NODES" in seg, "★ 兜底没过名字那一层"
    assert "_is_real_feature" in seg, "★ 兜底没过类型名那一层"


def test_evidence_all_eight_pass() -> None:
    """★★★ 核心断言：★ 证据里 **8 条全过** ✓"""
    if not EVID.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(EVID.read_text(encoding="utf-8", errors="replace"))
    checks = d.get("★_逐条判据") or {}
    assert len(checks) >= 8, "★ 判据条数不够：%r" % sorted(checks)
    bad = [k for k, v in checks.items() if v is not True]
    assert not bad, "★ 有判据没过：%r" % bad
    assert d.get("★_全过") is True, "★ 汇总不是全过"


def test_negative_case_the_three_revisions_are_recorded() -> None:
    """★★★★ **负例 · 三次判据修正要记**：★ 必须写明**容器**与**基准面**这两处 ✓

    ★★ **为什么**：★ 后人若见 `feature_info(model)` 无参调用 ⇒ ★ 会拿到**第一个真节点**、
      ★★ **而那可能是基准面**（★ `GetFaceCount = 0`）⇒ ★★★ **不记就会再判错一次** ✓
    """
    src = SRC.read_text(encoding="utf-8", errors="replace")
    i = src.find("def feature_info(")
    seg = src[i:i + 5200]
    assert "收藏" in seg, "★ 没记 `收藏`（★ 容器）那次"
    assert "基准面" in seg or "RefPlane" in seg, "★ 没记基准面那次"
    assert "两层" in seg, "★ 没写「两层过滤」"
