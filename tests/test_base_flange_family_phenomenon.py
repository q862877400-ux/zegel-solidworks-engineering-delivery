"""★ spec 265：`create_base_flange` 的失败**属于一族已知现象**（★ 事实 34/43 早记「`CreateFeature` 回 None」）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   docs/known-facts.md 事实 34（★ 记 `create_base_flange` **2026-10-01 成功**；★ 另 4 个特征
#           「现在**卡在同一层** `CreateFeature(N)`」）· 事实 43（★ `CreateDefinition` 只接受 35 个常量）
#         output/_probe265_env.py（★ 本轮真机：平面 / 模板 / 插件）
# 定位:   ★ spec 264 判「失败在环境/前置」⇒ ★ 本文件把**族现象**合并，★ 免得一轮一个特征地试参数。
# 官方依据: SW rev **34.4.1** 真机
# 许可:   本仓自产（无外部来源）
# 覆盖:   只读 `scripts/` 与 `docs/`；★ 真机部分由探针跑（★ 临时零件、不存盘、用完关闭）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
for _p in (str(ROOT), str(SCRIPTS)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★★★ **族现象**（★ 事实 34 逐字）：★ 4 个特征「现在**卡在同一层** `CreateFeature(N)`」
#:   ⇒ ★ `create_base_flange` **加入这一族**（★ 2026-10-01 它还成功）。
FAMILY = {
    "create_base_flange": "★ 2026-10-01 **成功**（特征树出现「钣金6 / 基体-法兰1 / 平展型式6」）⇒ 现在失败 = **回归**",
    "create_one_bend": "★ 事实 34：从 `CreateDefinition(33) 返回 None` **前推到** `CreateFeature(35) 创建失败`",
    "create_draft": "★ 事实 34：`swFmDraft(3)` 不在 35 个常量里",
    "create_edge_flange": "★ 事实 34：设 `ReverseDirection` 报 `Property ... can not be set`",
    "create_gusset": "★ 事实 34：属性层 8/8 过，`CreateFeature(118)` **仍 None**",
}
#: ★ 已知「卡在 `CreateFeature`」的条数（★ 事实 34 记 4 个；★ 加上 base flange = **5**）。
BASELINE_FAMILY = 5

#: ★★ **本轮真机环境读数**（`output/_probe265_env.py` · SW rev **34.4.1**）。
ENV = {
    "part_template": "C:/ProgramData/SolidWorks/SOLIDWORKS 2026/templates/gb_part.prtdot",
    "template_count_part": 1,                 #: ★ 本机**只有 1 个**零件模板 ⇒ ★ **换模板不可行**
    "addin_object_sheetmetal": None,           #: ★ `GetAddInObject('SldWorks.SheetMetal')` ⇒ **None**
    "front_plane": None,                       #: ★ 换 `Front Plane` ⇒ `CreateFeature` 仍 `None`
    "top_plane": "★ 选不上（`无法选择基准面: Top`）",
}

#: ★★ 迟到绑定下**不可用**的成员（★ 本轮实测）。
UNAVAILABLE = ("IsAddInRegistered", "GetCommandManager(0).GetTabs")


def _env_failures(env: dict, family: dict) -> list[str]:
    """★ 纯函数：① 平面不是因素；② 族现象条数够；③ 每条都要有出处。"""
    out: list[str] = []
    if env["front_plane"] is not None:
        out.append("`Front Plane` 竟然成功了 ⇒ ★ 结论要改")
    if env["template_count_part"] > 1:
        out.append("零件模板多于 1 个 ⇒ ★ 「换模板不可行」的结论要改")
    if len(family) != BASELINE_FAMILY:
        out.append("族现象条数 %d ≠ %d ⇒ 请同步" % (len(family), BASELINE_FAMILY))
    for k, v in family.items():
        if "事实 34" not in v and "回归" not in v:
            out.append("%s 没写出处" % k)
    return out


# ── ① ★★★ 族现象：`CreateFeature` 回 None **不是钣金独有** ─────────
def test_it_is_a_family_phenomenon():
    """★★★ 事实 34 早记「**4 个特征卡在同一层 `CreateFeature(N)`**」⇒ ★ `create_base_flange` 加入这一族。

    ★★ **为什么这条值钱**：★ 不合并 ⇒ ★ 下一轮会**一个特征一个特征地试参数**；
    ★ 合并后 ⇒ ★ **方向转到「这一族的共同环境因素」**。
    """
    bad = _env_failures(ENV, FAMILY)
    assert not bad, "族现象结论不成立：\n" + "\n".join("  " + b for b in bad)
    assert len(FAMILY) >= 5, "族里至少 5 个（★ 4 个既有 + base flange）"


# ── ② ★★ 平面不是因素 ───────────────────────────────────────────────
def test_plane_is_not_a_factor():
    """★★ 换官方示例用的 `Top` 平面**试不了**（★ `无法选择基准面: Top`）；
    ★ 而 `Front Plane` ⇒ **仍 `None`** ⇒ ★ **平面不是因素**。"""
    assert ENV["front_plane"] is None, "`Front Plane` 成功了 ⇒ 结论要改"
    assert "选不上" in ENV["top_plane"], "`Top` 的读数变了 ⇒ 请复核"


# ── ③ ★★ 换模板**不可行**（★ 本机只有 1 个零件模板）──────────────────
def test_template_switch_is_not_available():
    """★★ 本机零件模板**只有 1 个**（`gb_part.prtdot`）⇒ ★ **「换模板」这条路走不通**。"""
    assert ENV["template_count_part"] == 1, "模板数变了 ⇒ 请复核"
    assert ENV["part_template"].endswith("gb_part.prtdot"), "默认零件模板变了 ⇒ 请复核"


# ── ④ ★★ 迟到绑定下不可用的成员要留档 ───────────────────────────────
def test_unavailable_members_are_recorded():
    """★ `IsAddInRegistered` / `GetCommandManager(0).GetTabs` 在**迟到绑定**下抛 `AttributeError`
    ⇒ ★ 留档（★ 免得下一轮再试）。"""
    assert len(UNAVAILABLE) == 2, "不可用成员表被削"
    assert "IsAddInRegistered" in UNAVAILABLE


# ── ⑤ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 三组负例：① `Front Plane` 成功；② 模板多于 1 个；③ 族条数不对。"""
    assert not _env_failures(ENV, FAMILY), "正常读数被判红 ⇒ 判据过严"
    assert _env_failures(dict(ENV, front_plane="特征"), FAMILY), "平面成功未判出 ⇒ **空判据**"
    assert _env_failures(dict(ENV, template_count_part=2), FAMILY), "模板数变了未判出 ⇒ **空判据**"
    assert _env_failures(ENV, dict(list(FAMILY.items())[:3])), "族条数不对未判出 ⇒ **空判据**"
