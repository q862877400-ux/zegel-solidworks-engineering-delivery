"""★ T2-4 的第三个样板：**索引属性是"读"** —— 把这条判据写成静态断言（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tests/test_index_property_is_a_read.py
# 定位:   规格 206 / **T2-4 的第三个样板** —— 前两型是「调用顺序/选择」与「值域」，
#         ★ 本型是「**参数形态**」（★ 索引属性的下标是**读**的参数，不是**写**）✓
# ★★ 为什么挑这一条：`scripts/sw_equation.py` L99-107 **自己写出了判据与同族清单** ——
#   ① ★ 前置：`Equation` 是**索引属性**（★ 官方 `IEquationMgr::Equation(Index)`）⇒ 用**读**取；
#   ② ★★ **真错过**：轮 470 把 98 处「写 COM 属性」批量改名时，**按形态匹配 ⇒ 把这一处也改了**
#      ⇒ 变成"写下标"、回 `0/1/2` ⇒ 测试 `assert [0,1,2] == ['"A" = 1', …]` **当场失败**；
#   ③ ★ 判据**可静态判**（★ 笔记原文）：「**返回值被使用 ⇒ 那是读**；返回值被丢掉才是写」；
#   ④ ★★ **同族共 3 处**（此处 + `sw_assembly.py` 的 `MateEntityType` / `MateComponentName`）✓
# 依据:   `scripts/sw_equation.py` L99-108 · `scripts/sw_assembly.py` 的同族两处 ·
#         事实 62（负例是唯一证明）· 事实 51（范围要贴合组织单元）✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: ★★★ 那 3 处索引属性（★ 逐字来自 `sw_equation.py` L100-106 的同族清单）
SITES = (
    ("scripts/sw_equation.py", "Equation"),
    ("scripts/sw_assembly.py", "MateEntityType"),
    ("scripts/sw_assembly.py", "MateComponentName"),
)


def _text(rel: str) -> str:
    p = ROOT / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


def reads(name: str, text: str) -> int:
    """★ 「读」的形态：`get_com_member(<任意>, "<name>", <下标>…)` ✓"""
    return len(re.findall(r"get_com_member\([^)]*[\"']%s[\"']\s*," % re.escape(name), text))


def writes(name: str, text: str) -> int:
    """★ 「写」的形态：`set_com_member(<任意>, "<name>", <值>)` ⇒ ★ 对本型**不该出现** ✓"""
    return len(re.findall(r"set_com_member\([^)]*[\"']%s[\"']" % re.escape(name), text))


def test_sources_are_reachable():
    """★ 守卫：源抽不出来时下面的断言会「静默全通过」⇒ 先证明抽得到 ✓"""
    for rel, name in SITES:
        t = _text(rel)
        assert t, "读不到 %s" % rel
        assert re.search(r"[\"']%s[\"']" % re.escape(name), t), "在 %s 里找不到 %s" % (rel, name)


def test_index_properties_are_read_not_written():
    """★★ 主断言：这 3 处**用读**（`get_com_member`）、**没有用写**（`set_com_member`）✓

    ★ 判据出处（逐字）：`sw_equation.py` L105 ——
      「**返回值被使用 ⇒ 那是读**；返回值被丢掉才是写」✓
    """
    bad = []
    for rel, name in SITES:
        t = _text(rel)
        r, w = reads(name, t), writes(name, t)
        if r < 1 or w > 0:
            bad.append((rel, name, r, w))
    assert not bad, (
        "索引属性被当成「写」了（★ 轮 470 就是这么错的）: %s\n"
        "★ 期望：每处 读≥1 且 写=0" % bad)


def test_negative_write_form_is_detected():
    """★★ 负例（★ 事实 62）：**把某处改成写** ⇒ 判据**必须**报 ✓"""
    fake = 'out.append(set_com_member(mgr, "Equation", i))\n'
    assert writes("Equation", fake) > 0, "写下标没被抓到 ⇒ 判据是空转的"


def test_negative_missing_read_is_detected():
    """★★ 反向负例：**该处完全没有读** ⇒ 也应当被抓 ✓"""
    fake = "# 什么都没做\n"
    assert reads("Equation", fake) < 1, "无读的写法没被抓到"
