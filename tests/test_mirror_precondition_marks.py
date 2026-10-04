"""★ T2-4 模式的示范：把「官方 Remarks 揭示的前置」写成**静态断言**（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tests/test_mirror_precondition_marks.py
# 定位:   规格 206 / **T2-4 的第一个样板** —— 治「官方示例揭示了前置、而我们的运行证据没覆盖」
#         （`docs/precondition-coverage-gaps.md` 里 `part_and_features` 的那条：
#          「镜像前先 ClearSelection2；被镜像特征 mark=1、镜像平面 mark=2」）✓
# ★★ 为什么挑这一条：
#   ① ★ 官方 `InsertMirrorFeature2.md` 的 `## Remarks` **给了完整 mark 表**（Features⇒1 · Planes⇒2）；
#   ② ★★ 我们**真的错过**（轮 317：mark 反了 ⇒ 静默回 `None`）⇒
#      ★★★ **这是"真发生过、且没有断言守着"的那一类**（事实 62）✓
#   ③ ★ 判据**纯静态**（读我们自己的源码）⇒ ★ **不需要真机**（D-3 的按批限制不适用）✓
# 依据:   `scripts/sw_part.py` 的 `mirror_feature`（L1489-1498）· 官方 `InsertMirrorFeature2.md` 的
#         Remarks mark 表 · 事实 8（mark 计数为准）· 事实 62（负例是唯一证明）·
#         `docs/precondition-coverage-gaps.md` §三 ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "scripts" / "sw_part.py"

#: ★★★ 官方 Remarks 的 mark 表（逐字来自 `InsertMirrorFeature2.md`）
#:   ★ **Features ⇒ 1** · Planes or planar faces ⇒ **2** ⇒ ★ 这是本测试的**期望** ✓
FEATURE_MARK = 1
PLANE_MARK = 2


def mirror_body(text: str) -> str:
    """★ 取 `mirror_feature` 的函数体（★ 到下一个 `def ` 为止）—— ★ 不做全文件匹配。"""
    m = re.search(r"def mirror_feature\(.*?\n(?=def |\Z)", text, re.S)
    return m.group(0) if m else ""


def marks_in(body: str) -> dict:
    """★ 从函数体里抽出两次选择的 mark（★ 按 `_select_by_id` 的实参顺序）。"""
    out = {}
    calls = re.findall(r"_select_by_id\((.*?)\)\s*$", body, re.M)
    for i, c in enumerate(calls, 1):
        mm = re.search(r"mark\s*=\s*(\d+)", c)
        out["call%d" % i] = int(mm.group(1)) if mm else None
    return out


def test_source_is_reachable():
    """★ 守卫：源文件或函数抽不出来时，下面的断言会「静默全通过」⇒ 先证明抽得到。"""
    assert SRC.is_file(), "找不到 %s" % SRC
    body = mirror_body(SRC.read_text(encoding="utf-8", errors="replace"))
    assert body, "抽不到 mirror_feature 的函数体"
    assert marks_in(body), "函数体里抽不到 _select_by_id 的 mark"


def test_mirror_marks_match_official_remarks():
    """★★ 主断言：被镜像特征 **mark=1**、镜像平面 **mark=2**（★ 官方 Remarks 的 mark 表）。"""
    body = mirror_body(SRC.read_text(encoding="utf-8", errors="replace"))
    got = marks_in(body)
    vals = list(got.values())
    assert vals[:2] == [FEATURE_MARK, PLANE_MARK], (
        "mirror_feature 的 mark 与官方 Remarks 不符: %s（★ 应为 特征=1 · 平面=2；"
        "★ 轮 317 就是这么错的 ⇒ 特征 mark=4、平面 mark=1 ⇒ 静默回 None）" % got)


def test_negative_reversed_marks_are_detected():
    """★★ 负例（★ 事实 62）：**故意把 mark 调反** ⇒ 判据**必须**报出来 ✓"""
    fake = ("def mirror_feature(model, feature_name, mirror_plane_name):\n"
            '    _select_by_id(model.Extension, feature_name, "BODYFEATURE", mark=4)\n'
            '    _select_by_id(model.Extension, mirror_plane_name, "PLANE", append=True, mark=1)\n'
            "    return model.FeatureManager.InsertMirrorFeature2(...)\n\n"
            "def hole_wizard(model):\n    pass\n")
    body = mirror_body(fake)
    assert body, "负例样本抽不出函数体"
    vals = list(marks_in(body).values())
    assert vals[:2] != [FEATURE_MARK, PLANE_MARK], "负例（mark 反了）没被抓到 ⇒ 判据是空转的"


def test_negative_unmarked_call_is_detected():
    """★★ 反向负例：**不写 mark** ⇒ 也应当被抓（★ `None` ≠ 期望值）✓"""
    fake = ("def mirror_feature(model, feature_name, p):\n"
            '    _select_by_id(model.Extension, feature_name, "BODYFEATURE")\n'
            '    _select_by_id(model.Extension, p, "PLANE", append=True)\n'
            "    return model.FeatureManager.InsertMirrorFeature2()\n\n"
            "def next_one():\n    pass\n")
    vals = list(marks_in(mirror_body(fake)).values())
    assert vals[:2] != [FEATURE_MARK, PLANE_MARK], "无 mark 的写法没被抓到"
