"""★ 测 `FeatureCutThicken` 用的是**现行 6 参版**（★ 阶段 2 · T1 · 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `scripts/sw_feature_entry_ops.py::thicken_report`（★ 生产）·
#         `tools/probe_thicken2.py`（★ 探针、★ 只报不动）
# 定位:   ★ 阶段 2 · T1 的逐条流程第一条：★ **先查官方签名与 Remarks** ✓
#   ★★ **官方逐字**（★ `IModelDoc2/FeatureCutThicken2.md`）：
#     「**Obsolete. Superseded by `IFeatureManager::FeatureCutThicken`**.」✓
#     ★ 旧签名 ⇒ `(double Thickness, int Direction, int FaceIndex, bool FillVolume)` ⇒ **4 参** ✓
#   ★★★ **后继逐字**（★ `IFeatureManager/FeatureCutThicken.md`）：★ **无 Obsolete** ·
#     ★ 签名 ⇒ `(…, bool UseFeatScope, bool UseAutoSelect)` ⇒ **6 参**（★ 前 4 参同名同型）✓
#     ★★ 而 `## Parameters` 逐字：★ `Direction` = **0 / 1 / 2** · ★ `FaceIndex` = **Not currently used** ✓
#   ★★★★ **本仓现状：★ 生产代码**已经**用现行的 6 参版**** ——
#     ★ 而扫描器报的 3 处**全在 `tools/probe_thicken2.py`**（★ 探针、★ 按纪律不动）✓
#   ★★★★★ **∴ 本条**已完成**** —— ★ 本测试守它别退化 ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROD = REPO / "scripts" / "sw_feature_entry_ops.py"
PROBE = REPO / "tools" / "probe_thicken2.py"
OFF_OLD = Path(r"C:\swapi\types\IModelDoc2\FeatureCutThicken2.md")
OFF_NEW = Path(r"C:\swapi\types\IFeatureManager\FeatureCutThicken.md")


def test_official_chain_is_as_documented() -> None:
    """★★★ **前提断言**：★ 官方那两页**确实**这么写（★ 判据的锚点）✓"""
    if not (OFF_OLD.is_file() and OFF_NEW.is_file()):
        return                                                            # ★ 官方源不在本机 ⇒ 跳过
    old = OFF_OLD.read_text(encoding="utf-8", errors="replace")
    new = OFF_NEW.read_text(encoding="utf-8", errors="replace")
    assert "Obsolete" in old and "IFeatureManager::FeatureCutThicken" in old, "★ 旧页口径变了"
    assert "Obsolete" not in new, "★ 后继被标废弃了 ⇒ 判据要重看"
    assert "UseFeatScope" in new and "UseAutoSelect" in new, "★ 后继的后两参变了"


def test_production_uses_the_six_arg_successor() -> None:
    """★★★ 核心断言：★ 生产代码调的是**现行的 6 参版**、★ 且**调用了 6 个实参** ✓"""
    src = PROD.read_text(encoding="utf-8", errors="replace")
    assert '"FeatureCutThicken"' in src, "★ 没调现行的 `FeatureCutThicken`"
    assert '"FeatureCutThicken2"' not in src, "★ 生产代码里出现了废弃的 `FeatureCutThicken2`"
    tree = ast.parse(src)
    found = []
    for n in ast.walk(tree):
        #: ★★ 判据要**精确到那一处调用**（★ 事实 51：范围贴合组织单元）——
        #:   形态是 `get_com_member(<fm>, **kind**, …)` ⇒ ★ 认**第二个实参是 `kind`** ✓
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id == "get_com_member" and len(n.args) >= 2
                and isinstance(n.args[1], ast.Name) and n.args[1].id == "kind"):
            found.append(n)
    assert found, "★ 找不到那处 `get_com_member(fm, kind, …)` 调用（★ 判据要重看）"
    #: ★★★ **两个分支的实参个数**本来就不同**（★ 我第一版写死 8 ⇒ 红了）——
    #:   · ★ `cut=True` ⇒ `FeatureCutThicken`（**6 参**）⇒ 加 2 个定位参数 = **8** ✓
    #:   · ★ `cut=False` ⇒ `FeatureBossThicken`（**7 参**，★ 它多一个 `Merge`）⇒ **9** ✓
    #:   ★★ **⇒ 判据要按"调的是哪个成员"分开**，★ 而不是一个数管两边 ✓
    counts = sorted(len(n.args) for n in found)
    assert counts == [8, 9], (
        "★ 两个分支的实参个数是 %r ⇒ 期望 [8, 9]（★ 6 参 + 2 / 7 参 + 2）" % counts)


def test_negative_case_probe_is_left_alone() -> None:
    """★★ **负例 · 探针不动**：★ 探针里**允许**留着旧名（★ 「`tools/` 只报不动」）✓

    ★★ 为什么：★ 探针的**历史输出是证据** ⇒ ★★ **改了它就破坏了"证据不可变"** ✓
      ★★★ 而**本条的 3 处命中正是在探针里** ⇒ ★ **那正是"已完成"的原因** ✓
    """
    if not PROBE.is_file():
        return
    t = PROBE.read_text(encoding="utf-8", errors="replace")
    assert "FeatureCutThicken2" in t, (
        "★ 探针里的旧名被删了 ⇒ 破坏了「证据不可变」（★ 那 3 处命中本来就该在探针里）")


def test_negative_case_scan_rows_are_probe_scoped() -> None:
    """★★★ **负例 · 判据边界**：★ 那 3 处命中**必须**带 `探针` 的 scope 标记 ✓

    ★★ 判据：★★★ **"真命中"要分清**生产**与**探针**** —— ★ 后者按纪律**不动** ✓
      ★ 与**事实 518/519** 同族：★★★ **"我这张表里有"≠"该改"** ✓
    """
    f = REPO / "output" / "obsolete-dotcall-scan.json"
    if not f.is_file():
        return
    d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
    rows = [r for r in d["全部行"] if "Thicken" in str(r.get("member", ""))]
    assert rows, "★ 那几条记录不见了 ⇒ 判据要重看"
    for r in rows:
        assert "探测" in str(r.get("scope")) or "探针" in str(r.get("scope")), (
            "★ `%s` 竟然不在探针范围内 ⇒ 要按生产项处理" % r.get("file"))
