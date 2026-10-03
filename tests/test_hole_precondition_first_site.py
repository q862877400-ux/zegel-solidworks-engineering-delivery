"""★ 测「阵列后打孔会失败」这条真因**写进了第一现场**（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身。
# 文件:   `scripts/sw_hole_features.py`（★ **第一现场** —— ★ 那句诊断长在那里）·
#         `output/why-hole-none.json`（★ 二分法证据）
# 定位:   ★ 轮 105 用**二分法**定位出：★ **做了线性阵列之后、★ 沿 `+z` 的射线打不中面**、
#   ★★ **打孔回 `None`** ⇒ ★★★ **本轮的活是**把那条真因写进第一现场**** ✓
#   ★★★★ **为什么要写进**那里**（★ 而不是只留在 `output/`）**：
#     ★ `output/` 是**证据**、★ 而**下一轮读代码的人看的是那句 `RuntimeError`** ⇒
#     ★★ **依据要落在**报错那行旁边****（★ 那正是**第一现场**的定义）✓
#     （★ 与 AGENTS.md「① 官方页 → … → ③ **该能力的 `limitations`**（第一现场）」**同源**）✓
#   ★★★★★ **判据（★ 可核）**：
#     ★ 那句 `RuntimeError` 里要能看到 ① **元凶是阵列** ② **建议的顺序** ③ **指向证据文件** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_hole_features.py"


def test_the_first_site_carries_the_new_finding() -> None:
    """★★★ 核心断言：★ 第一现场要能看到**三条**（★ 元凶 · ★ 顺序 · ★ 证据）✓"""
    t = SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find("HoleWizard5 回 None")
    assert i != -1, "★ 找不到那句诊断（★ 它被改了？）"
    seg = t[i:i + 4200]
    #: ★ ① 元凶
    assert "阵列" in seg, "★ 没写元凶是**阵列**"
    #: ★ ② 建议顺序
    assert "板 → 孔 → 阵列 → 圆角" in seg, "★ 没写建议的**唯一可行序**"
    #: ★ ③ 指向证据
    assert "why-hole-none" in seg or "why_hole_none" in seg, "★ 没指向那份二分法证据"


def test_the_original_three_reasons_are_kept() -> None:
    """★★★ 核心断言：★ **原来那三条**常见原因**不许被删** ✓

    ★★ **为什么**：★ 本轮是**追加**一条实测发现 ⇒
      ★★★ **不可以用新内容把原来那三条顶掉**（★ 那三条**各自**都可能成立）✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find("HoleWizard5 回 None")
    seg = t[i:i + 4200]
    for old in ("① `size` 不是规格串", "② `fastener_index`", "③ 射线没命中了面"):
        assert old in seg, "★ 原来那条 `%s` 不见了" % old


def test_negative_case_the_two_layers_are_distinguished() -> None:
    """★★★★ **负例 · 两层要分开**：★ 「射线没命中」与「`HoleWizard5` 回 None」是**两件事** ✓

    ★★ **为什么**：★ 我上一轮**看到的是 `None`**、★ 而**射线那一层先过了** ⇒
      ★★★ **⇒ 若混为一谈，会以为"射线命中就万事大吉"** ✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find("HoleWizard5 回 None")
    seg = t[i:i + 4200]
    assert "射线命中与建孔成功是" in seg or "两件事" in seg, (
        "★ 没写清「射线命中」与「建孔成功」是两件事")


def test_negative_case_the_bisection_evidence_is_referenced() -> None:
    """★★ **负例 · 依据要指向证据文件**：★ 那句注释里要写明四条腿是哪些 ✓"""
    t = SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find("HoleWizard5 回 None")
    seg = t[i:i + 4200]
    assert "去阵列" in seg and "去圆角" in seg, "★ 没写那两条**对照腿**（★ 二分法的关键）"
