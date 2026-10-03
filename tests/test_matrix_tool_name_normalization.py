"""★ 测「操作×对象」矩阵的工具分类**先规范化工具名**、★ 且三个判据达标（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi`）
# 文件:   `tools/build_capability_matrix.py`（★ **只读工具**）·
#         `output/operation-object-matrix.json`
# 定位:   ★ 阶段 3（T2 矩阵 → 密度型缺口地图）✓
#   ★★ **第一版的判据①报**无处可放率 = 100.00%（280/280）**、而逐条显示**全落
#     `（未归类）×（未归类）`** ⇒ ★★★ **那不是"矩阵全空"、是**喂进去的文本形态不对**** ✓
#   ★★★ **真因**（★ 证伪实验 `output/_why_all_unplaced.py`）：
#     ★ 规则是 **CamelCase**（`Add` / `Sketch` / `Get`）、★ 而工具名是 **snake_case + 前缀**
#     （`solidworks_add_dimension`）⇒ ★★ `re.search` **大小写敏感** ⇒ **一个都命中不了** ✓
#     证伪读数：★ 原样 **280/280 = 100.0%** · ★ 驼峰化后 **35/280 = 12.5%** ✓
#   ★★★★ **三个阈值**（★ 文件头写死、★ **跑之前写死、跑完不改**）：
#     ① 无处可放率 ≤ 20% · ② 空格率 ≤ 60% · ③ 双源一致率 ≥ 30% ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "build_capability_matrix.py"
OUT = REPO / "output" / "operation-object-matrix.json"

_spec = importlib.util.spec_from_file_location("_mb", TOOL)
mb = importlib.util.module_from_spec(_spec)
sys.modules["_mb"] = mb
_spec.loader.exec_module(mb)


def test_tool_text_normalizes_to_camel_case() -> None:
    """★★★ **前提断言**：★ `tool_text` **确实**把 snake_case 变成 CamelCase ✓"""
    assert mb.tool_text("solidworks_add_dimension") == "AddDimension", "★ 规范化结果变了"
    assert mb.tool_text("cadstudio_check_dfm") == "CheckDfm", "★ `cadstudio_` 前缀没去掉"


def test_classify_is_case_sensitive_so_normalization_is_required() -> None:
    """★★★ 核心断言：★ **不规范化就全落 `（未归类）`** —— ★ 那正是 100% 的真因 ✓

    ★★ 本测试守的是**因果**：★ 若哪天 `classify` 变成大小写不敏感、
      ★★ 那"必须先规范化"这条就不再必要 ⇒ ★ **本测试会红 ⇒ 那时可以简化** ✓
    """
    assert mb.classify("add_dimension", mb.OPS) == "（未归类）", (
        "★ 小写竟然能命中 ⇒ `classify` 变了 ⇒ 本判据要重看")
    assert mb.classify("AddDimension", mb.OPS) != "（未归类）", "★ CamelCase 命中不了"


def test_the_three_criteria_are_met() -> None:
    """★★★ 核心断言：★ 证据里**三个判据全部达标**（★ 按文件头写死的阈值）✓"""
    if not OUT.is_file():
        return                                                            # ★ 产物不在本机 ⇒ 跳过
    d = json.loads(OUT.read_text(encoding="utf-8", errors="replace"))
    #: ★★ 键名**逐字**（★ 我第一版猜了 `判据`/`criteria`、★ 那两个都不存在）——
    #:   ★ 实际是 `判据①无处可放率` / `判据②空格率` / `判据③双源一致率` ✓
    c1 = d.get("判据①无处可放率") or {}
    c2 = d.get("判据②空格率") or {}
    c3 = d.get("判据③双源一致率") or {}
    assert c1 and c2 and c3, "★ 三个判据的键名变了：%r" % sorted(d)
    assert float(c1["值"]) <= 20.0, "★ 无处可放率 %s%% 超过 20%%" % c1["值"]
    assert float(c2["值"]) <= 60.0, "★ 空格率 %s%% 超过 60%%" % c2["值"]
    assert float(c3["值"]) >= 30.0, "★ 双源一致率 %s%% 低于 30%%" % c3["值"]
    #: ★ 分子分母也要对得上（★ 防"改了分母"）
    assert c1["分子"] == 35 and c1["分母"] == 280, "★ 判据①的分子/分母变了：%r" % c1


def test_negative_case_the_thresholds_are_untouched() -> None:
    """★★★★ **负例 · 阈值不许改**：★ 文件头那三个数字**必须**还是原值 ✓

    ★★ **为什么**：★ 本轮的修法是**规范化输入**、★ **不是**放宽阈值 ⇒
      ★★★ **若哪天有人把 20 改成 30 来"通过"，本测试会红** ✓
    """
    t = TOOL.read_text(encoding="utf-8", errors="replace")
    assert "≤ 20%" in t, "★ 判据①的阈值被改了"
    assert "≤ 60%" in t, "★ 判据②的阈值被改了"
    assert "≥ 30%" in t, "★ 判据③的阈值被改了"
    assert "tool_text" in t, "★ 规范化那一步不见了"
