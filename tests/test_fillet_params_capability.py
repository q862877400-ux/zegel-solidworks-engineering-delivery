"""★ 测 `fillet_params`：★ 判据、★ **第六层单位口径**、★ 不碰"要 item"的成员（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\ISimpleFilletFeatureData2\`）
# 文件:   `scripts/sw_feature_readback.py::fillet_params`（★ 阶段 3 补的能力 · 第六个）·
#         `tools/probe_fillet_params_recheck.py`（★ 只报不动）·
#         `output/fillet-params-capability-recheck.json`
# 定位:   ★ 阶段 3 · 按密度图补能力 ⇒ **第六个**、★ **第五个族** ✓
#   ★★ **官方逐字**：★ `DefaultRadius` ⇒ 「Default radius of the **symmetric** fillet」·
#     ★ `GetEdgeCount()` ⇒ 「Number of edges」· ★ `GetSetbackVerticesCount()` ⇒
#     「Number of setback vertices」· ★ `Type` ⇒ `swSimpleFilletType_e` ·
#     ★ `OverflowType` ⇒ `swFilletOverFlowType_e` ✓
#   ★★★ **真机 7/7 全过**：★ `DefaultRadius = **5.0**` · ★ `GetEdgeCount = 1` ·
#     ★ `GetSetbackVerticesCount = 0` · ★ `Type/OverflowType = 0` ·
#     ★ `RoundCorners = False` · ★ **`KeepFeatures = True`** ·
#     ★ `PropagateToTangentFaces = True` ✓
#   ★★★★ **单位口径的第六层**：★ `DefaultRadius` 的官方 `## Returns` **没写单位** ⇒
#     ★ **真机测出**：★ `5.0`（★ 与建的 `R5` 同口径）⇒ ★★ **随文档单位** ✓
#     （★ 六层汇总：① 随文档 · ② radians · ③ meters · ④ 官方没写 · ⑤ 接口内部就分裂 ·
#       ★⑥ **本族随文档**）✓
#   ★★★★★ **⚠ 前置签名**（★ **先在仓里搜出来的**、★ 不是猜的）：
#     ★ `sw_part.fillet(model, radius, edges=None)` ⇒ **`radius` 在第 2 位** ✓
#     ★★ 我第一版注释里猜成 `fillet(model, selection, radius_mm)` ⇒ **错的** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _funcbody import func_source  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_feature_readback.py"
EVID = REPO / "output" / "fillet-params-capability-recheck.json"
SP = Path(r"C:\swapi\types\ISimpleFilletFeatureData2\DefaultRadius.md")


def test_official_page_gives_no_unit() -> None:
    """★★★ **前提断言**：★ 官方那页**没写单位**（★ 判据的锚点）✓"""
    if not SP.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t = SP.read_text(encoding="utf-8", errors="replace")
    assert "Default radius" in t, "★ 官方页变了"
    low = t.lower()
    for w in ("meters", "meter", "millimeters", "millimeter", "inches"):
        assert not __import__("re").search(r"\b%s\b" % w, low), (
            "★ 官方页现在写了单位 `%s` ⇒ 判据要重看" % w)


def test_code_does_not_touch_the_item_taking_members() -> None:
    """★★★ 核心断言：★ 函数里**不碰**那三个"要 item 对象"的成员 ✓

    ★★ **为什么**：★ `GetRadius(PFilletItem)` / ★ `GetDistance` / ★ `GetConicRhoOrRadius`
      ★ 都要先 `IGetFilletEdgeAtIndex` ⇒ ★★ **硬写会得到一个每次都不一样的结果** ✓
    """
    src = SRC.read_text(encoding="utf-8", errors="replace")
    i = src.find("def fillet_params(")
    assert i != -1, "★ 找不到 `fillet_params`"
    #: ★★★★ 2026-10-04（轮 113）**改用 `ast` 取那一个函数**（★ 事实 51）——
    #:   ★ **真因**：★ `src[i:].split('"""')[-1]` **看着像"函数体"**、
    #:     ★★ **而它实际是"从那个 `def` 到**文件末尾**"** ⇒
    #:     ★★★ **文件末尾后来多了一个函数 ⇒ 范围**悄悄变宽**、判据**误报**** ✓
    #:   ★★★★ **⇒ 用 `tests/_funcbody.py::func_source`**（★ 按 `ast` 的 `end_lineno`）✓
    body = func_source(src, "fillet_params")
    #: ★★★★ **判据要精确**（★ 事实 51 · 本会话第 N 次）：★ 那三个名字**本身就在**函数体里** ——
    #:   ★ 它们是**注释**里「★ 本函数**不碰**它们」那句话的内容、★ **不是调用**** ⇒
    #:   ★★ **所以要查**调用形态** `get_com_member(fd, "<name>"`、★ 而不是查名字出现** ✓
    #:   （★ 与 `test_csys_params_capability.py` 那条**同一个修法**）✓
    for bad in ("GetRadius", "GetDistance", "GetConicRhoOrRadius"):
        for shape in ('get_com_member(fd, "%s"' % bad, "get_com_member(fd, '%s'" % bad,
                      'safe_get_com_member(fd, "%s"' % bad):
            assert shape not in body, "★ 函数体里**调了** `%s`（★ 那要 item 对象）" % bad
    #: ★★ 而那句"不碰"的**记录**必须还在 ✓
    assert "不碰" in body, "★ 那句「本函数不碰它们」的记录不见了"


def test_code_uses_the_two_layer_filter() -> None:
    """★★★ 核心断言：★ 兜底过**两层**（★ 上一轮的教训 —— ★ 容器也可能有类型名）✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    i = src.find("def fillet_params(")
    seg = src[i:i + 4200]
    assert "_CONTAINER_NODES" in seg, "★ 兜底没过名字那一层"
    assert "GetTypeName2" in seg, "★ 兜底没过类型名那一层"


def test_negative_case_evidence_all_seven_pass() -> None:
    """★★★★ **负例 · 7 条判据全过 + 单位判定要写**：★ 含 `DefaultRadius = 5.0` ✓"""
    if not EVID.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(EVID.read_text(encoding="utf-8", errors="replace"))
    checks = d.get("★_逐条判据") or {}
    assert len(checks) >= 7, "★ 判据条数不够：%r" % sorted(checks)
    bad = [k for k, v in checks.items() if v is not True]
    assert not bad, "★ 有判据没过：%r" % bad
    assert d.get("★_全过") is True, "★ 汇总不是全过"
    #: ★★ 单位判定必须落盘（★ 那是本轮的第二件事）✓
    assert "随" in str(d.get("★_单位判定")), "★ 没写单位判定：%r" % d.get("★_单位判定")
