"""★ spec 285：`create_profile_center_mate` **首次真机验证** —— ★ `CreateMateData` 通、★ `CreateMate` **静默回 None**。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   D:/AI/SW
# 文件:   output/_probe285_mate.txt · _probe285_mate_cyl.txt · _probe285_mate_presel.txt（★ 三轮真机读数）
#         scripts/sw_weldment.py:793-820（★ `create_profile_center_mate` · ★ 逐字走官方路：`CreateMateData(24)` → 设属性 → `CreateMate`）
#         C:/swapi/types/IAssemblyDoc/CreateMate.md（★ 逐字：「an asterisk indicates that **pre-selection** … is supported」
#           ⇒ ★ `IProfileCenterMateFeatureData` **无星号**）
#         C:/swapi/types/IProfileCenterMateFeatureData/_overview.md（★ 创建三步）
# 定位:   ★ 业主**已授权**（GOAL §三 C）⇒ ★ 本轮**首次真机跑** ⇒ ★ 逐层量 + 读消息栈。
# 官方依据: 见上（★ 官方页 + 反射 `Object CreateMateData(Int32)` / `Object CreateMate(Object)` 三源一致）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   只读（★ 真机读数由探针产出；★ 本文件不连 COM）
# ────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

#: ★★★ **真机读数**（SW **34.4.1** · 2026-10-10 · ★ 走 `sw_guard` · ★ 夹具 = 换刀主轴装配（11 零件））。
#:   ① `CreateMateData(24)` ⇒ ★ **回对象**（★ 与 sheet-metal family 的 `AccessSelections` **不同**）。
CREATE_MATE_DATA_OK = True
#:   ② `EntitiesToMate` 两条实体路都试过 ⇒ ★ **都 None**。
ENTITY_ARMS = {"随便两个面": False, "两个圆柱面": False, "圆柱面 + 另一个圆柱面": False}
#:   ③ ★ 消息栈 **空** ⇒ ★★ **静默失败**。
MESSAGE_STACK_N = 0
#:   ④ ★ 「预选 + Mark 1」那条臂 ⇒ ★★ **选中 0 个**（★ 装配里选面**没选上**）⇒ ★ **该臂不成立**（★ 如实标注）。
PRESEL_ARM = {"selected": 0, "conclusion": "该臂不成立（预选没生效）"}
#: ★★★ **官方页的两句话**（★ 要一起引）。
OFFICIAL = {
    "overview": "Specify EntitiesToMate **or** use SelectByID2 to pre-select the entities using **Mark = 1**",
    "createmate": "an asterisk indicates that **pre-selection** of mate entities during mate creation is supported",
    "profile_center_has_asterisk": False,          #: ★ 逐字核过：★ `IProfileCenterMateFeatureData` **无星号**
}
#: ★★★ **结论**：★ 本机建不出（★ 且**静默**）。
VERDICT = "本机建不出（CreateMate 静默回 None · 消息栈空）"


def _failures(cmd_ok, arms, n, presel, official, verdict, src) -> list[str]:
    """★ 纯函数：① `CreateMateData` 通；② 实体臂全失败；③ 消息栈空；④ 预选臂如实标注；⑤ 官方两句话都在；⑥ 结论；⑦ 源码仍走官方路。"""
    bad: list[str] = []
    if not cmd_ok:
        bad.append("★ `CreateMateData(24)` 应**回对象**")
    if len(arms) != 3:
        bad.append("★ 实体臂应 3 条，实测 %d" % len(arms))
    if any(arms.values()):
        bad.append("★ 三条实体臂应**全失败**")
    if n != 0:
        bad.append("★ 消息栈应为**空**（★ 那才是「静默」）")
    if presel.get("selected") != 0:
        bad.append("★ 预选臂应如实记「选中 0 个」")
    if "不成立" not in presel.get("conclusion", ""):
        bad.append("★ 预选臂要如实标「不成立」")
    if "EntitiesToMate" not in official.get("overview", ""):
        bad.append("★ 官方 overview 那句要引全")
    if "asterisk" not in official.get("createmate", ""):
        bad.append("★ 官方 `CreateMate` 那句要引全")
    if official.get("profile_center_has_asterisk"):
        bad.append("★ `IProfileCenterMateFeatureData` **无**星号 ⇒ 这一格应是 `False`")
    if "本机建不出" not in verdict:
        bad.append("★ 结论应是「本机建不出」")
    if not src:
        bad.append("★ 回源码核失败：取不到 `create_profile_center_mate`")
    elif "CreateMateData" not in src or "CreateMate" not in src:
        bad.append("★ 源码应仍走官方路（`CreateMateData` + `CreateMate`）")
    return bad


# ── ① ★★★ `CreateMateData` **通**（★ 与 sheet-metal family 不同） ───
def test_create_mate_data_returns_an_object():
    """★★★ 真机：★ `IAssemblyDoc::CreateMateData(24)` ⇒ ★ **回对象**（`CDispatch`）
    ⇒ ★★ **不是** `AccessSelections` 那种「结构性不可调用」（★ 与 280/281 的族**不同因**）。
    """
    assert CREATE_MATE_DATA_OK is True


# ── ② ★★★ 三条实体臂**全失败** ─────────────────────────────────────
def test_all_entity_arms_fail():
    """★★★ 真机：★ `EntitiesToMate` 试了**随便两个面** / **两个圆柱面** / **另一对圆柱面** ⇒ ★ **全回 `None`**
    ⇒ ★★ **不是「实体选错了」**（★ 官方页说 `EntitiesToMate` 收「faces or edges」✓）。
    """
    assert len(ENTITY_ARMS) == 3
    assert not any(ENTITY_ARMS.values())


# ── ③ ★★★ **静默失败**（★ 消息栈空） ─────────────────────────────
def test_the_failure_is_silent():
    """★★★ 真机：★ `CreateMate` 回 `None` 时★ **消息栈 n=0**（★ 空）⇒ ★★ **读不到任何原因**
    ⇒ ★ 与 **263**（`CreateFeature` 回 `None` 且读不到错误码）**同族**。
    """
    assert MESSAGE_STACK_N == 0


# ── ④ ★★ 预选臂**不成立**要如实标（★ 别当成证据） ─────────────────
def test_the_preselect_arm_is_marked_as_inconclusive():
    """★★ 真机：★ 「预选 + Mark 1」那条臂 ⇒ ★ **选中 0 个**（★ 装配里选面**没选上**）
    ⇒ ★★ **该臂不成立**（★ 不能拿它当「预选也不行」的证据）⇒ ★ 如实标注。
    """
    assert PRESEL_ARM["selected"] == 0
    assert "不成立" in PRESEL_ARM["conclusion"]


# ── ⑤ ★★★ 官方两句话**要一起引**（★ 它们**不完全一致**） ───────────
def test_both_official_statements_are_quoted():
    """★★★ 官方**两页**：★ overview 说「`EntitiesToMate` **或** `SelectByID2` + **Mark = 1**」；
    ★ 而 `CreateMate` 页说「★ **星号**才支持**预选**」⇒ ★ `IProfileCenterMateFeatureData` **无星号**
    ⇒ ★★ 两句话**不完全一致** ⇒ ★ **两条路本轮都试了**（★ 其中预选那条**没选上**）。
    """
    assert "EntitiesToMate" in OFFICIAL["overview"]
    assert "asterisk" in OFFICIAL["createmate"]
    assert OFFICIAL["profile_center_has_asterisk"] is False


# ── ⑥ ★★★ 回源码核：★ 源码**仍走官方路** ─────────────────────────
def test_source_still_follows_the_official_path():
    """★★★ 回源码核：★ `create_profile_center_mate` 仍走 `CreateMateData` → 设属性 → `CreateMate`
    ⇒ ★★ **不是代码错**（★ 官方三步逐条照做）⇒ ★ 结论是「**本机建不出**」而不是「写错了」。
    """
    src = (ROOT / "scripts" / "sw_weldment.py").read_text(encoding="utf-8", errors="replace")
    m = re.search(r"def create_profile_center_mate\(.*?\n(.*?)(?=\n# ── |\ndef )", src, re.S)
    assert m, "★ 取不到 `create_profile_center_mate`"
    body = m.group(1)
    assert "CreateMateData" in body and "CreateMate" in body


# ── ⑦ ★★ 判据必须能红 ───────────────────────────────────────────────
def test_pure_function_is_red_able():
    """★ 七组负例。"""
    good = "md = call_assembly_doc(model, 'CreateMateData', 24)\n…\ncall_assembly_doc(model, 'CreateMate', md)"
    args = (CREATE_MATE_DATA_OK, ENTITY_ARMS, MESSAGE_STACK_N, PRESEL_ARM, OFFICIAL, VERDICT, good)
    assert not _failures(*args), "正常读数被判红 ⇒ 判据过严"
    assert _failures(False, ENTITY_ARMS, MESSAGE_STACK_N, PRESEL_ARM, OFFICIAL, VERDICT, good), \
        "`CreateMateData` 不通却未判出"
    assert _failures(CREATE_MATE_DATA_OK, dict(ENTITY_ARMS, **{"两个圆柱面": True}), MESSAGE_STACK_N,
                     PRESEL_ARM, OFFICIAL, VERDICT, good), "某实体臂成功却未判出"
    assert _failures(CREATE_MATE_DATA_OK, ENTITY_ARMS, 3, PRESEL_ARM, OFFICIAL, VERDICT, good), \
        "消息栈非空却未判出"
    assert _failures(CREATE_MATE_DATA_OK, ENTITY_ARMS, MESSAGE_STACK_N,
                     {"selected": 2, "conclusion": "该臂不成立"}, OFFICIAL, VERDICT, good), \
        "预选臂读数不对却未判出"
    assert _failures(CREATE_MATE_DATA_OK, ENTITY_ARMS, MESSAGE_STACK_N, PRESEL_ARM,
                     dict(OFFICIAL, profile_center_has_asterisk=True), VERDICT, good), \
        "星号结论错却未判出"
    assert _failures(CREATE_MATE_DATA_OK, ENTITY_ARMS, MESSAGE_STACK_N, PRESEL_ARM, OFFICIAL,
                     "一切正常", good), "结论不对却未判出"
    assert _failures(CREATE_MATE_DATA_OK, ENTITY_ARMS, MESSAGE_STACK_N, PRESEL_ARM, OFFICIAL,
                     VERDICT, "call_com_member(model, 'AddMate5', ...)"), \
        "源码不走官方路却未判出"
