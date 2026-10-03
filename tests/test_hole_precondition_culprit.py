"""★ 测「打孔前置被**阵列**弄坏」这条真因（★ 阶段 3 · 第二个同病前置 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IFeatureManager\HoleWizard5.md`）
# 文件:   `output/_why_hole_none.py`（★ 只报不动）· `output/why-hole-none.json`（★ 证据）·
#         `output/e2e_readback_tools.py` · `output/e2e-readback-tools.json`
# 定位:   ★ 轮 104 的 e2e 里 `hole_params` **不过**、★ 而**前置**（打孔）回了 `None` ——
#   ★★ 报的是**它自己的诊断**（★ 逐字）：「`HoleWizard5` 回 None ⇒ 孔没建出来。
#      ★ 常见原因（事实 469）：★ ① `size` 不是规格串；★ ② `fastener_index` 与 `standard_index`
#      不匹配；★ ③ **射线没命中了面**。」✓
#   ★★★ **而同样的调用在轮 98 成功过** ⇒ ★★ **⇒ 又是顺序/状态依赖** ✓
#   ★★★★ **二分法实测（★ `output/why-hole-none.json`）**：
#     · ★ **A · 只板 + 孔** ⇒ ★ **`True`**（★ 建出 `异型孔向导`）✓
#     · ★★ **B · 板 + 阵列 + 圆角 + 孔** ⇒ ★ **`None`** ✓
#     · ★ **C · 板 + 圆角 + 孔**（★ **去阵列**）⇒ ★ **`True`** ⇒ ★★ **圆角不是元凶** ✓
#     · ★★ **D · 板 + 阵列 + 孔**（★ **去圆角**）⇒ ★ **`None`** ⇒ ★★★★ **⇒ **阵列**是元凶** ✓
#     ⇒ ★★★★★ **⇒ 真因：★ 阵列之后、★ `+z` **射线打不中面了**** ——
#       ★ 正是工具自己诊断的**第 ③ 条** ✓
#   ★★★★★ **⇒ 唯一可行序：★ 板 → 孔 → 阵列 → 圆角** ⇒ 端到端 **6 / 6** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WHY = REPO / "output" / "why-hole-none.json"
E2E = REPO / "output" / "e2e-readback-tools.json"


def test_bisection_has_all_four_legs() -> None:
    """★★★ 核心断言：★ 二分法的**四条腿**都在（★ A 只孔 · ★ B 全序 · ★ C 去阵列 · ★ D 去圆角）✓"""
    if not WHY.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(WHY.read_text(encoding="utf-8", errors="replace"))
    rows = d.get("rows") or {}
    keys = " ".join(rows)
    for tag in ("只板", "板_阵列_圆角", "板_圆角", "板_阵列_孔"):
        assert tag in keys, "★ 缺了「%s」那条腿：%r" % (tag, sorted(rows))


def test_the_pattern_is_the_culprit_not_the_fillet() -> None:
    """★★★★ 核心断言：★ **去阵列就成、★ 去圆角不成** ⇒ **阵列是元凶** ✓

    ★★ 判据逐字：★ C（去阵列）`ok = True`、★ D（去圆角）`ok = None/False` ⇒
      ★★★ **⇒ 一个"去哪个"的对照就够了**（★ 那正是二分法的价值）✓
    """
    if not WHY.is_file():
        return
    d = json.loads(WHY.read_text(encoding="utf-8", errors="replace"))
    rows = d.get("rows") or {}
    c = next((v for k, v in rows.items() if "板_圆角_孔" in k), None)
    dd = next((v for k, v in rows.items() if "板_阵列_孔" in k), None)
    assert c and dd, "★ 对照那两条腿不全"
    assert (c.get("hole") or {}).get("ok") is True, (
        "★ 「去阵列」那条**没成** ⇒ 元凶不是阵列：%r" % c.get("hole"))
    assert not (dd.get("hole") or {}).get("ok"), (
        "★ 「去圆角」那条**成了** ⇒ 元凶不是阵列：%r" % dd.get("hole"))


def test_negative_case_the_unique_order_is_recorded() -> None:
    """★★★★ **负例 · 唯一可行序要写进脚本**：★ 「板 → 孔 → 阵列 → 圆角」 ✓

    ★★ **为什么**：★ 那序是**两轮实测**定出来的 ⇒ ★★ **不写下来、下一个人会再踩** ✓
    """
    p = REPO / "output" / "e2e_readback_tools.py"
    if not p.is_file():
        return
    t = p.read_text(encoding="utf-8", errors="replace")
    assert "why-hole-none" in t or "why_hole_none" in t, "★ 没引那份二分法证据"
    assert "唯一可行序" in t, "★ 没写「唯一可行序」"
    assert "孔 → 阵列 → 圆角" in t, "★ 没写那个序"


def test_negative_case_the_e2e_is_now_six_of_six() -> None:
    """★★★★ **负例 · 端到端现在是 6/6**：★ 且每个工具都读到真特征 ✓"""
    if not E2E.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(E2E.read_text(encoding="utf-8", errors="replace"))
    assert d.get("通过") == 6 and d.get("总数") == 6, (
        "★ 端到端不是 6/6：%r / %r" % (d.get("通过"), d.get("总数")))
    #: ★★ 那三个"要前置"的必须读到**真特征名**（★ 而不是空）✓
    want = {"solidworks_pattern_params": "阵列",
            "solidworks_hole_params": "异型孔",
            "solidworks_fillet_params": "圆角"}
    for row in (d.get("rows") or []):
        feat = want.get(row.get("tool"))
        if feat:
            got = str((row.get("read") or {}).get("feature") or "")
            assert feat in got, "★ `%s` 读到的特征名不含「%s」：%r" % (row.get("tool"), feat, got)
