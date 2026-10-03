"""★ 测 `linear_pattern` 的记档理由写的是**"没验出来"**、★ 而不是"后继到不了"（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\IFeatureManager\`）
# 文件:   `scripts/sw_part.py::linear_pattern` · `tools/probe_pattern5.py`（★ 只报不动）·
#         `output/pattern5-probe-evidence.json`
# 定位:   ★ 阶段 2 · T1 的逐条流程 ①②③ ✓
#   ★★ **官方链**（★ 按接口限定地追）：★ `3` 废弃 ⇒ `4` · ★ `4` 废弃 ⇒ `5` · ★ **`5` 废弃、后继空** ✓
#   ★★★ **反射裁决**（★ 铁律 4）：★ `FeatureLinearPattern` 最高 **22 参**（★ `5` 代）·
#     ★ `FeatureCircularPattern` 最高 **14 参**（★ `5` 代）⇒ ★ **没有 `6`** ✓
#   ★★★★ **真机三轮**：★ **四种形态**（★ 两条基线 + 两条新代）**特征数都是 22 → 22** ⇒
#     ★★ **连基线都没建成** ⇒ ★★★ **这个探针**证明不了** `5` 代能不能替** ✓
#   ★★★★★ **∴ 本测试守的是**记档的理由要对****：
#     ★ 必须写「**没验出来**」/「**基线立不起来**」，★ **不许**写成「后继到不了」 ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_part.py"
EVID = REPO / "output" / "pattern5-probe-evidence.json"
OFF3 = Path(r"C:\swapi\types\IFeatureManager\FeatureLinearPattern3.md")


def test_official_remarks_gives_the_mark_table() -> None:
    """★★★ **前提断言**：★ 官方 Remarks **确实**给了 mark 表（★ 判据的锚点）✓"""
    if not OFF3.is_file():
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    t = OFF3.read_text(encoding="utf-8", errors="replace")
    assert "4 to mark the features to pattern" in t, "★ mark 表变了"
    assert "ordered selection" in t, "★ 「有序选择」那句变了"


def test_evidence_shows_baseline_also_failed() -> None:
    """★★★ 核心断言：★ 证据里**四种都是 `built=False`** —— ★ 含**基线** ✓

    ★★ **那正是"没验出来"的根据**：★ 若基线成了而新代没成 ⇒ 那是"新代不行"；
      ★★ **而基线也没成** ⇒ ★★★ **只能说"这个探针测不出东西"** ✓
    """
    if not EVID.is_file():
        return
    d = json.loads(EVID.read_text(encoding="utf-8", errors="replace"))
    rows = {r["form"]: r for r in d["rows"]}
    assert set(rows) >= {"linear3_10", "linear5_22", "circular4_7", "circular5_14"}, (
        "★ 四种形态不全：%r" % sorted(rows))
    for form, r in rows.items():
        assert r.get("built") is False, (
            "★ `%s` 竟然成了（%r）⇒ 那就可以换代了 ⇒ 请复核" % (form, r.get("built")))
        assert r.get("features_before") == r.get("features_after"), (
            "★ `%s` 的特征数变了 ⇒ 判据要重看" % form)


def test_negative_case_reason_is_not_verified_not_unreachable() -> None:
    """★★★ **负例 · 理由必须对**：★ 要写「**没验出来**」/「**基线立不起来**」✓

    ★★ **为什么关键**：★ 若写成「后继到不了」，★ 后人会以为**已经验过了**、
      ★★★ **而事实是"什么都没验出来"** ⇒ ★ **两种说法会导向完全不同的下一步** ✓
      ★ 与**事实 519/518**同族：★★★ **"表里有"≠"它做到了"** · ★ **"没换"≠"不能换"** ✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find("def linear_pattern(")
    j = t.find("\ndef ", i + 10)
    seg = t[i:j if j != -1 else len(t)]
    assert "没验出来" in seg, "★ 没写「没验出来」"
    assert "基线" in seg, "★ 没写「基线立不起来」"
    assert "事实 53" in seg, "★ 没写「连续修补 ≥3 次就该停」这条（★ 我改了 5 版）"


def test_negative_case_does_not_claim_successor_unreachable() -> None:
    """★★★ **负例 · 不许误写成"后继到不了"**：★ 它**可调**（★ 只是基线没成）✓"""
    t = SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find("def linear_pattern(")
    j = t.find("\ndef ", i + 10)
    seg = t[i:j if j != -1 else len(t)]
    #: ★ 判据：★ 若出现"到不了"，★ 必须同时出现"**没验出来**"或"未验"之类的限定 ✓
    if "到不了" in seg:
        assert "没验出来" in seg or "未验" in seg, (
            "★ 写了「到不了」、★ 而没说那只是「没验出来」⇒ 会误导")
