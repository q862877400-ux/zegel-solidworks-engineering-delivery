"""★ 测「线性阵列」换代后**两处调用点**都用 `FeatureLinearPattern5`（★ 含负例）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\`）
# 文件:   `scripts/sw_part.py::linear_pattern` / `::linear_pattern_report`（★ 生产两处）·
#         `tools/probe_linear_pattern_baseline.py`（★ 探针、★ 只报不动）·
#         `output/linear-pattern-baseline-evidence.json`
# 定位:   ★ 阶段 2 · T1 · ★ 逐条流程 ①②③ ✓
#   ★★ **官方链**（★ 按接口限定地追）：★ `3` 废弃 ⇒ `4` ⇒ `5`（★ 5 也废弃、★ 后继空）·
#     ★★ **反射裁决**（★ 铁律 4）：★ `FeatureLinearPattern` 最高代 **22 参**、★ **没有 `6`** ⇒
#     ★ **`5` 是现行可用那代** ✓
#   ★★★ **调用序来自**官方示例****（★ `Change_Linear_Pattern_Example_VB.md` 逐字）：
#     ★ `ClearSelection2(True)` ⇒ ★ 方向 **`mark=1`** ⇒ ★ 实体 **`mark=256`** ✓
#     ★★ **⚠ 而选实体是 `IBody2::Select(Append, Mark)`、★ 不是 `Select4`** ✓
#   ★★★★ **真机结果**（★ `output/linear-pattern-baseline-evidence.json`）：
#     ★ `3`(10 参) / `4`(20 参) / **`5`(22 参)** ⇒ ★★ **三种全部建成**（★ 20→21 · `阵列(线性)1`）✓
#   ★★★★★ **∴ 本轮同时办成两件**：★ ①**本仓"阵列"基线第一次真机建成** ·
#     ★★ ②**`5` 代可替**（★ 上一轮记的"没验出来"**本轮被推翻** —— ★ 而那**正是记档的价值**）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "scripts" / "sw_part.py"
EVID = REPO / "output" / "linear-pattern-baseline-evidence.json"


def test_both_call_sites_use_generation_five() -> None:
    """★★★ 核心断言：★ **两处**调用点都换成 `FeatureLinearPattern5` ✓

    ★★ 为什么是**两处**：★ 本仓有 `linear_pattern`（★ 返回 raw 对象）与
      `linear_pattern_report`（★ 带**特征树回读**）⇒ ★★ **只改一处会留下半成品** ✓
    """
    src = SRC.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    calls = []
    for n in ast.walk(tree):
        #: ★★ **两种调用形态**（★ 判据要**按形态分开** —— ★ 与上一轮那条同族）：
        #:   · ★ `get_com_member(fm, "FeatureLinearPattern5", …22)` ⇒ **24 个实参** ✓
        #:   · ★★ `model.FeatureManager.FeatureLinearPattern5(…22)` ⇒ **22 个实参** ✓
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id == "get_com_member" and len(n.args) >= 2
                and isinstance(n.args[1], ast.Constant)
                and isinstance(n.args[1].value, str)
                and "FeatureLinearPattern" in n.args[1].value):
            calls.append((n.args[1].value, len(n.args) - 2, "get_com_member"))
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and "FeatureLinearPattern" in n.func.attr):
            calls.append((n.func.attr, len(n.args), "attribute"))
    assert calls, "★ 找不到任何 `FeatureLinearPattern*` 调用"
    names = {nm for nm, _n, _k in calls}
    assert names == {"FeatureLinearPattern5"}, "★ 还有别的代：%r" % sorted(names)
    for nm, nargs, kind in calls:
        assert nargs == 22, "★ `%s`（%s 形态）有 %d 个签名实参、★ 期望 **22**" % (nm, kind, nargs)


def test_evidence_three_generations_all_built() -> None:
    """★★★ 核心断言：★ 证据里**三种形态全部建成**、★ 新特征名含「阵列」 ✓"""
    if not EVID.is_file():
        return                                                            # ★ 证据不在本机 ⇒ 跳过
    d = json.loads(EVID.read_text(encoding="utf-8", errors="replace"))
    rows = {r["form"]: r for r in d["rows"]}
    assert rows, "★ 证据里没有记录"
    for form, r in rows.items():
        assert r.get("built") is True, "★ `%s` 没建成：%r" % (form, r.get("error"))
        assert any("阵列" in str(x) for x in (r.get("new_features") or [])), (
            "★ `%s` 的新特征名里没有「阵列」：%r" % (form, r.get("new_features")))


def test_negative_case_the_calling_sequence_is_recorded() -> None:
    """★★★ **负例 · 调用序必须记**：★ docstring 里要有**两个 mark** 与**选实体的成员名** ✓

    ★★ **为什么**：★ 这两样**签名与 Remarks 都给不了**（★ Remarks 只说了 `4`）、
      ★★★ **而官方**示例**给了** ⇒ ★ **不记就会再踩一次** ✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find("def linear_pattern(")
    seg = t[i:i + 8000]
    #: ★★ 那两个 mark 的说明写在 `linear_pattern` 的**长注释块**里 ⇒
    #:   ★ 若窗口不够就退到**全模块**里找（★ 而不放宽内容要求）✓
    hay = seg if ("mark=1" in seg and "256" in seg) else t
    assert "mark=1" in hay or "`mark=1`" in hay or "mark = 1" in hay, "★ 没记方向那个 mark"
    assert "256" in hay, "★ 没记实体那个 mark（★ 官方示例逐字是 256）"
    assert "IBody2::Select" in hay or "IBody2.Select" in hay, "★ 没记「选实体用 `IBody2::Select`」"


def test_negative_case_previous_round_record_is_corrected() -> None:
    """★★★★ **负例 · 推翻要有据**：★ 本轮**推翻了**上一轮的「没验出来」⇒ ★ 必须写明依据 ✓

    ★★ **为什么**：★ 上一轮的记档是**诚实且正确的**（★ 基线确实没成）⇒
      ★★★ **而本轮查到真因是"我调错了成员"** ⇒ ★ **必须把这条更正落进第一现场**，
      ★★ 否则后人读到的仍是"没验出来" ✓
    """
    t = SRC.read_text(encoding="utf-8", errors="replace")
    i = t.find("def linear_pattern(")
    seg = t[i:i + 8000]
    assert "Select4" in seg, "★ 没写明「我第一版用的是 `Select4`」这个错"
    assert "IBody2" in seg, "★ 没写明正确的接口"
