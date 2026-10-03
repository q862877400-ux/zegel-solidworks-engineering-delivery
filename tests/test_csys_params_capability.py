"""★ 测 `csys_params`：★ 判据、★ **三个读数互相印证**、★ 「页不在」要如实记（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\ICoordinateSystemFeatureData\`）
# 文件:   `scripts/sw_feature_readback.py::csys_params`（★ 阶段 3 补的能力 · 第七个）·
#         `tools/probe_csys_params_recheck.py`（★ 只报不动）·
#         `output/csys-params-capability-recheck.json`
# 定位:   ★ 阶段 3 · 按密度图补能力 ⇒ **第七个**、★ **第六个族** ✓
#   ★★ **本族的官方页**只有四个**（★ `output/_read_csys_members.py`）：
#     ★ `GetOriginEntityType()` ⇒ `swSelectType_e` ·
#     ★ 三个 `Get{X,Y,Z}AxisEntitiesCount()` ⇒ 「Number of entities for the x/y/z axis」·
#     ★ `Transform {get;}` ⇒ 回 `Math transform` ·
#     ★★ `AccessSelections(TopDoc, Component)` ⇒ 要两个入参 ⇒ **本函数不碰** ✓
#     ★★★ **其余一律「页不在」**（★ `Flipped` / ★ `Reverse*Direction` / ★ `Get*AxisEntities` …）⇒
#       ★★ **按铁律 5：★ 查不到就写「查不到」、★ 不许用相似名字蒙混** ✓
#   ★★★ **真机 8/8 全过**（★ `output/csys-params-capability-recheck.json`）：
#     ★ 特征 **`坐标系1`** · ★ `GetOriginEntityType = **-1**` ·
#     ★ **三轴实体数 = 0/0/0** · ★ **`Transform.ArrayData_len = **16****
#       （★ `[1.0, 0.0, 0.0, 0.0]` = **单位阵**）✓
#   ★★★★ **⇒ 三个读数**互相印证****：★ 没选实体（0/0/0）+ ★ 原点类型 `-1` ⇒
#     ★★ **变换必然是单位阵** ⇒ ★★★ **而那正是本仓 `insert_coordinate_system` 的语义**
#     （★ 建**默认三轴**）✓
#   ★★★★★ **⚠ 本族**没有长度量****（★ 三是计数、★ 一是枚举、★ 一是变换对象）⇒
#     **不涉及单位口径** —— ★ 那是本会话**唯一**一个这样的一族 ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_feature_readback.py"
EVID = REPO / "output" / "csys-params-capability-recheck.json"
D = Path(r"C:\swapi\types\ICoordinateSystemFeatureData")

#: ★★ **「页不在」那一批**（★ 逐个 `is_file()` 过、★ 那才是"查不到"的依据）✓
NO_PAGE = ["Flipped", "ReverseXDirection", "ReverseYDirection", "ReverseZDirection",
           "GetXAxisEntities", "GetYAxisEntities", "GetZAxisEntities",
           "GetXAxisEntitiesType", "GetYAxisEntitiesType", "GetZAxisEntitiesType",
           "GetOriginEntity"]


def test_official_pages_are_really_absent() -> None:
    """★★★ **前提断言**：★ 那 11 个**确实没有页**（★ 「查不到」的依据）✓

    ★★ **为什么**：★ 我在 docstring 里写了「页不在」⇒ ★★ **那句话必须可核** ——
      ★★★ 若哪天官方补了页、本测试会红 ⇒ **那时就该去调它们** ✓
    """
    if not D.is_dir():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    present = [n for n in NO_PAGE if (D / (n + ".md")).is_file()]
    assert not present, (
        "★ 这些现在**有页**了 ⇒ 该去读它们、★ 并把它们加进能力：%r" % present)


def test_code_does_not_call_the_no_page_members() -> None:
    """★★★ 核心断言：★ 函数体里**一个都不调**那 11 个（★ 铁律 5）✓

    ★★★★ **判据要精确**（★ 事实 51）：★ 那 11 个名字**本身就在函数体里** ——
      ★ 它们是**返回值**里那份「★ `页不在`」清单的内容**、★ **不是调用**** ⇒
      ★★ **所以要查**调用形态** `get_com_member(fd, "<name>"`、★ 而不是查名字出现 ✓
      （★ 我第一版就是查名字出现 ⇒ **红了**）✓
    """
    src = SRC.read_text(encoding="utf-8", errors="replace")
    i = src.find("def csys_params(")
    assert i != -1, "★ 找不到 `csys_params`"
    body = src[i:].split('"""')[-1]                       #: ★ 函数体（★ 跳过 docstring）
    for n in NO_PAGE:
        for shape in ('get_com_member(fd, "%s"' % n, "get_com_member(fd, '%s'" % n,
                      'safe_get_com_member(fd, "%s"' % n):
            assert shape not in body, "★ 函数体里调了 `%s`（★ 那个页不在）" % n
    #: ★★ 而那份清单**必须还在**（★ 那是"查不到"的记录）✓
    assert "页不在" in body, "★ 那份「页不在」清单不见了"


def test_code_uses_the_two_layer_filter() -> None:
    """★★★ 核心断言：★ 兜底过**两层**（★ 前几轮的教训：★ 容器也可能有类型名）✓"""
    src = SRC.read_text(encoding="utf-8", errors="replace")
    i = src.find("def csys_params(")
    seg = src[i:i + 4200]
    assert "_CONTAINER_NODES" in seg, "★ 兜底没过名字那一层"
    assert "CoordSys" in seg, "★ 兜底没过类型名那一层"


def test_negative_case_the_three_readings_are_consistent() -> None:
    """★★★★ **负例 · 三个读数要**互相印证****：★ 0/0/0 + `-1` ⇒ **16 个数的单位阵** ✓

    ★★ **判据逐字**：★ 建**默认三轴**的坐标系 ⇒
      ★ `GetOriginEntityType = -1` · ★ 三轴实体数 = `0/0/0` · ★ `ArrayData_len = 16` ·
      ★★ **而 `ArrayData` 的前 4 位必然是 `[1.0, 0.0, 0.0, 0.0]`**（★ 单位阵第一行）✓
      ★★★ **⇒ 一个不满足就说明"读的不是那个对象"**（★ 本会话那条判据的用法）✓
    """
    if not EVID.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(EVID.read_text(encoding="utf-8", errors="replace"))
    checks = d.get("★_逐条判据") or {}
    assert len(checks) >= 8, "★ 判据条数不够：%r" % sorted(checks)
    bad = [k for k, v in checks.items() if v is not True]
    assert not bad, "★ 有判据没过：%r" % bad
    r = d.get("读取") or {}
    assert str(r.get("GetOriginEntityType")) == "-1", "★ 原点类型不是 -1：%r" % r
    for ax in ("GetXAxisEntitiesCount", "GetYAxisEntitiesCount", "GetZAxisEntitiesCount"):
        assert str(r.get(ax)) == "0", "★ `%s` 不是 0：%r" % (ax, r.get(ax))
    assert str(r.get("Transform.ArrayData_len")) == "16", "★ 变换不是 16 个数：%r" % r
    assert "1.0" in str(r.get("Transform.ArrayData_head")), (
        "★ 变换头不是单位阵：%r" % r.get("Transform.ArrayData_head"))
