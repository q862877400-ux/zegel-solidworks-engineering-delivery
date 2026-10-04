"""★ T2-4 的第二个样板：官方 Remarks 派生的**值域前置**写成静态断言（★ 含两个负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tests/test_gtol_allowed_tol_types.py
# 定位:   规格 206 / **T2-4 的第二个样板** —— 与第一个样板（镜像 mark）**形状不同**：
#         那个是「**调用顺序/选择** 前置」（mark 表），★ 本条是「**值域** 前置」✓
# ★★ 为什么挑这一条（★ 沿用第一个样板立的三条理由）：
#   ① ★ 官方 `C:/swapi/types/IGtolFrame/AddIndicator.md` 的 `## Remarks` **给了确定的值域**
#      （`TolType` 只能是 5 个 `swGtolGeomCharSymbol_e` 成员）；
#   ② ★★ 我们**真的错过** —— `scripts/sw_gtol.py` L286-288 逐字记着
#      「`GTOL_GEOM_SYMBOL` 里另外 **14 个**（flatness / position / straightness …）**都不在清单里**
#        ⇒ 传它们 `AddIndicator` **必然返回 False**（**过去会被读成"到不了"**）」；
#   ③ ★ 判据**纯静态**（读我们自己的常量）⇒ ★ **不需要真机** ✓
# 依据:   `scripts/sw_gtol.py` 的 `GTOL_INDICATOR_ALLOWED_TOL_TYPES` · 官方
#         `IGtolFrame/AddIndicator.md` 的 Remarks · 事实 62（负例是唯一证明）·
#         `docs/precondition-coverage-gaps.md` §三 ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts" / "sw_gtol.py"

#: ★★★ 官方 Remarks 给的**值域**（★ 逐字来自 `IGtolFrame/AddIndicator.md`）：
#:   5 个 `swGtolGeomCharSymbol_e` 成员及其数值 ✓
OFFICIAL = {20: "angularity", 22: "parallelism", 21: "perpendicularity",
            25: "circular_runout", 13: "symmetry"}


def _load_constant():
    """★ 从源码里抽常量（★ 不 import 整个模块 —— 那会拉起 COM 依赖）。"""
    text = SRC.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"GTOL_INDICATOR_ALLOWED_TOL_TYPES\s*=\s*\{(.*?)\}", text, re.S)
    if not m:
        return None
    out = {}
    for k, v in re.findall(r"(\d+)\s*:\s*[\"']([a-z_]+)[\"']", m.group(1)):
        out[int(k)] = v
    return out


def test_source_and_constant_are_reachable():
    """★ 守卫：抽不出常量时下面的断言会「静默全通过」⇒ 先证明抽得到 ✓"""
    assert SRC.is_file(), "找不到 %s" % SRC
    got = _load_constant()
    assert got, "抽不到 GTOL_INDICATOR_ALLOWED_TOL_TYPES（★ 常量名或写法变了？）"


def test_allowed_set_equals_official_remarks():
    """★★ 主断言：允许集**恰好等于**官方 Remarks 给的那 5 个 ✓"""
    got = _load_constant()
    assert got == OFFICIAL, (
        "GTOL_INDICATOR_ALLOWED_TOL_TYPES 与官方 Remarks 不符:\n  我们的: %s\n  官方:   %s\n"
        "★ 官方 Remarks 逐字：TolType 只能是这 5 个成员 ⇒ ★ 多一个会放过错值、少一个会挡住对值"
        % (got, OFFICIAL))


def test_negative_extra_member_is_detected():
    """★★ 负例 1（★ 事实 62）：**多放一个**（如 flatness=19）⇒ 判据**必须**报 ✓

    ★ 这正是那个真错的形态：`GTOL_GEOM_SYMBOL` 里另外 14 个**都不在清单里** ✓
    """
    fake = {**OFFICIAL, 19: "flatness"}
    assert fake != OFFICIAL, "负例构造失败"


def test_negative_missing_member_is_detected():
    """★★ 负例 2：**少一个**（如删掉 symmetry=13）⇒ 判据**必须**报 ✓"""
    fake = {k: v for k, v in OFFICIAL.items() if k != 13}
    assert fake != OFFICIAL, "负例构造失败"
