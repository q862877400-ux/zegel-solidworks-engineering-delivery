"""★ 测「阵列前置的顺序依赖」这条真因（★ 阶段 3 · 追一个遗留负结果 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\examples\Change_Linear_Pattern_Example_VB.md`）
# 文件:   `output/_why_pattern_none.py`（★ 只报不动）· `output/why-pattern-none.json`（★ 证据）·
#         `output/e2e_readback_tools.py`（★ 只报不动）· `output/e2e-readback-tools.json`（★ 证据）
# 定位:   ★ 轮 103 的端到端里 `solidworks_pattern_params` **不过**、★ 而**前置**（建阵列）回了 `None` ✓
#   ★★ **同一个调用在轮 97 建成过** ⇒ ★★ **⇒ 那是**前置不稳**** ⇒ 本轮去追真因 ✓
#   ★★★ **假设（★ 可证伪）**：★ 轮 103 是先建**圆角 + 异型孔**、★ 再选那条边 `(-0.05, 0, 0)` ⇒
#     ★★ **而那两刀可能已经改掉了那条边** ✓
#   ★★★★ **实测读数（★ `output/why-pattern-none.json`）**：
#     · ★ **A · 先建阵列** ⇒ ★ `dir_sel = **True**` · ★★ **`ret = <COMObject>`（★ 建成）** ✓
#     · ★★ **B · 先圆角孔、★ 后建阵列** ⇒ ★★ **`dir_sel = **False**`** ⇒ `ret = None` ✓
#     ⇒ ★★★★★ **⇒ 假设**完全成立****：★★★ **那条边在打完圆角/孔之后**选不到了**** ✓
#   ★★★★★ **修后**（★ e2e 改成**阵列先做**）：★ `pattern_params` ⇒
#     ★ **`feature = 「阵列(线性)1」`** · ★ **`D1TotalInstances = 2`** ⇒ **通了** ✓
#     ★★ **而 ✗ 换成了 `hole_params`**（★ 它自己的诊断：★「HoleWizard5 回 None ⇒
#       常见原因（事实 469）…」）⇒ ★★★ **同一个病：★ 顺序** ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WHY = REPO / "output" / "why-pattern-none.json"
E2E = REPO / "output" / "e2e-readback-tools.json"


def test_hypothesis_is_falsifiable_and_recorded() -> None:
    """★★★ 核心断言：★ 证据里**两条腿的读数都在**（★ A 先阵列 · ★ B 后阵列）✓"""
    if not WHY.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(WHY.read_text(encoding="utf-8", errors="replace"))
    rows = d.get("rows") or {}
    assert len(rows) >= 2, "★ 应该有两组对照：%r" % sorted(rows)
    keys = " ".join(rows)
    assert "先阵列" in keys, "★ 没有「先建阵列」那一组"
    assert "后阵列" in keys, "★ 没有「后建阵列」那一组"


def test_the_order_is_the_real_cause() -> None:
    """★★★★ 核心断言：★ **A 选到方向、★ B 没选到** —— ★ 那就是真因 ✓

    ★★ 判据逐字：★ `dir_sel` 在"先阵列"那组是 `True`、★ 在"后阵列"那组是 `False` ✓
    """
    if not WHY.is_file():
        return
    d = json.loads(WHY.read_text(encoding="utf-8", errors="replace"))
    rows = d.get("rows") or {}
    a = next((v for k, v in rows.items() if "先阵列" in k), None)
    b = next((v for k, v in rows.items() if "后阵列" in k), None)
    assert a and b, "★ 两组读数不全"
    assert (a.get("pattern") or {}).get("dir_sel") is True, (
        "★ 「先阵列」那组没选到方向 ⇒ 假设要重看：%r" % a.get("pattern"))
    assert (b.get("pattern") or {}).get("dir_sel") is False, (
        "★ 「后阵列」那组**选到了**方向 ⇒ 假设被推翻：%r" % b.get("pattern"))


def test_negative_case_the_fix_is_visible_in_the_e2e() -> None:
    """★★★★ **负例 · 修完要看得到**：★ e2e 里 `pattern_params` 现在**通**、★ 且回特征名 ✓

    ★★ **为什么**：★ 只写"找到真因"不算数 ⇒ ★★ **要有**修完之后的读数**** ✓
    """
    if not E2E.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(E2E.read_text(encoding="utf-8", errors="replace"))
    row = next((r for r in (d.get("rows") or [])
                if r.get("tool") == "solidworks_pattern_params"), None)
    assert row is not None, "★ e2e 里没有 `pattern_params` 那一行"
    assert row.get("ok") is True, "★ `pattern_params` 还没通：%r" % row.get("read")
    assert "阵列" in str((row.get("read") or {}).get("feature")), (
        "★ 读到的特征名不含「阵列」：%r" % row.get("read"))


def test_negative_case_the_pre_condition_order_is_written_down() -> None:
    """★★★★ **负例 · 顺序要写进 e2e 脚本**：★ 注释里必须有那条实测依据 ✓

    ★★ **为什么**：★ 顺序是本轮**实测出来**的 ⇒ ★★ **不写下来、下一个人会再踩** ✓
    """
    p = REPO / "output" / "e2e_readback_tools.py"
    if not p.is_file():
        return
    t = p.read_text(encoding="utf-8", errors="replace")
    assert "why_pattern_none" in t or "why-pattern-none" in t, "★ 没引那份真因证据"
    assert "顺序" in t, "★ 没写「顺序」那条"
    assert "dir_sel" in t, "★ 没写 `dir_sel` 那个读数"
