"""★ 契约测试：草图完全定义门禁（★ 含**负例自证**）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tests/test_sketch_definition_gate.py
# 定位:   `scripts/check_sketch_definition.py` 的契约测试。
#           ★★ 触发它的是 2026-10-12 业主审 L3-001~008 的 **4 处批注**。
# 官方依据: ① SolidWorks 官方
#             [草图状态](https://help.solidworks.com/2026/Chinese-simplified/SolidWorks/acadhelp/c_moving2d3d_sketch_states.htm)
#           ② `specs/315-eval-corpus/sketch-definition-protocol.md`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"),
                str(ROOT / "mcp-server"), str(ROOT / "tools")]

import check_sketch_definition as C                                     # noqa: E402


def _l3() -> list:
    return yaml.safe_load(
        (ROOT / "corpus" / "l3-semantic.yaml").read_text(encoding="utf-8"))


def test_gate_passes() -> None:
    """★★★ 主判据：有草图的语料条目**都写清了**三要素。"""
    problems = C.check()
    assert problems == [], "★★ 有 %d 处问题：\n%s" % (
        len(problems), "\n".join(problems[:5]))


def test_selftest_passes() -> None:
    """★★ 负例自证：★ 业主批注的 3 种形态**必须**被抓到。"""
    assert C.selftest() is True


def test_all_24_solvable_have_sketch_definition() -> None:
    """★ 24 条「能做」**全都有** `sketch_definition`。"""
    items = [x for x in _l3() if x["category"] == "solvable"]
    miss = [x["id"] for x in items if not x.get("sketch_definition")]
    assert miss == [], "★ 缺 sketch_definition：%s" % miss


def test_every_sketch_has_origin() -> None:
    """★★★ 业主批注 2：「你如果**不定好原点**的话，你就算是加了尺寸，
    也不是一个完全定义的草图」。

    ★ 判据：凡有 `sketch_definition` 且**建草图**的，`origin` **非空**。
    """
    bad = [x["id"] for x in _l3()
           if x.get("sketch_definition")
           and C._has_sketch(x)
           and not x["sketch_definition"].get("origin")]
    assert bad == [], "★★ 没写位置（原点）：%s" % bad


def test_every_sketch_has_relations() -> None:
    """★★★ 业主批注 1/3/4：「平行垂直关系呢？」「这些几何关系你都要约定」。

    ★ 判据：**凡有 `sketch_definition` 的**，`relations` **非空**。
    ⚠ 实测（2026-10-12）：第一版没先判 `sketch_definition` 在不在 ⇒
      ★ 把 36 条「该问/该拒」的条目（★ 它们**本来就不该有做法**）
      也算成「没写关系」✗ —— ★ 而"36 条都缺"看起来像"语料大面积不合格"。
    """
    bad = [x["id"] for x in _l3()
           if x.get("sketch_definition")
           and C._has_sketch(x)
           and not x["sketch_definition"].get("relations")]
    assert bad == [], "★★ 没写形状关系：%s" % bad


def test_line_tool_entries_mention_orientation() -> None:
    """★★★ 业主批注 1：「如果你在 L 型这个环境下，**直接用直线工具画**，
    那么直线和直线之间**是没有关系的**」。

    ★ 判据：凡提到「直线工具」的，**必须**提到垂直/平行/水平/竖直之一。
    """
    bad = []
    for x in _l3():
        sd = x.get("sketch_definition") or {}
        rels = " ".join(sd.get("relations") or [])
        if "直线工具" in rels and not any(
                k in rels for k in ("垂直", "平行", "水平", "竖直")):
            bad.append(x["id"])
    assert bad == [], "★★ 用了直线工具却没写方向关系：%s" % bad


def test_every_sketch_states_tool_builtin() -> None:
    """★★ 业主批注 1 的核心：**矩形/圆工具自带关系，直线工具不自带**
    ⇒ ★ 每条都要写清「工具自带了什么」。

    ⚠ 同 `test_every_sketch_has_relations`：★ 先判 `sketch_definition` 在不在。
    """
    bad = [x["id"] for x in _l3()
           if x.get("sketch_definition")
           and C._has_sketch(x)
           and not x["sketch_definition"].get("tool_builtin")]
    assert bad == [], "★★ 没写工具自带什么：%s" % bad


def test_l_shape_spells_out_all_relations() -> None:
    """★★★ 业主批注 1 的原例（L3-003 的 L 形）：**逐条**写出 6 个关系族。

    ★ 判据：`relations` 里同时出现**重合/垂直/水平/竖直**四类
      （★ 那是 L 形完全定义所必需的）。
    """
    x = next(y for y in _l3() if y["id"] == "L3-003")
    rels = " ".join(x["sketch_definition"]["relations"])
    for k in ("重合", "垂直", "水平", "竖直"):
        assert k in rels, "★★ L 形缺 `%s` 关系" % k


def test_slot_spells_out_position_and_direction() -> None:
    """★★★ 业主批注 4 的原例（L3-008 的槽口）：要写清
    **位置**（怎么定）、**尺寸口径**（中心距 vs 切线长）、**方向关系**。
    """
    x = next(y for y in _l3() if y["id"] == "L3-008")
    sd = x["sketch_definition"]
    blob = " ".join(sd["dims"] + sd["relations"])
    assert "圆弧中心至圆弧中心" in blob, (
        "★★ 没写槽长口径 —— ★ 官方 2026 SP1：圆弧中心之间 / 圆弧切线长度**是两回事**")
    assert "对称" in blob, "★★ 没写槽的位置怎么定（★ 该用对称，不用 1/2 尺寸）"
    assert "平行" in blob or "竖直" in blob or "水平" in blob, (
        "★★ 没写槽的**方向关系**")


def test_no_sketch_entries_are_exempt() -> None:
    """★ 不建草图的条目（装配/工程图/属性）**豁免** —— ★ 但要是**真的**不建。"""
    items = [x for x in _l3() if x.get("sketch_definition")]
    exempt = [x["id"] for x in items if not C._has_sketch(x)]
    assert exempt, "★ 一条豁免的都没有 ⇒ 标记可能写错了"
    for x in items:
        if not C._has_sketch(x):
            assert x["sketch_definition"]["expected_status"] is None, (
                "★ %s 标了豁免却又有期望状态码" % x["id"])


def test_gate_is_registered_in_the_classification() -> None:
    """★★ 元门禁要求：★ 每个调用点都要**登记分类**。"""
    import json                                                         # noqa: PLC0415
    d = json.loads((ROOT / "docs" / "gate-classification.json")
                   .read_text(encoding="utf-8"))
    runners = {e.get("runner") for e in d["classification"]}
    assert "_run_sketch_definition_gate" in runners
    entry = next(e for e in d["classification"]
                 if e.get("runner") == "_run_sketch_definition_gate")
    for f in ("gate", "kind", "reason", "environment", "owner", "runs_in"):
        assert entry.get(f), "★ 缺字段 %s" % f


def test_gate_result_is_in_the_return_body() -> None:
    """★★ 元门禁要求：★ 结果必须进 `_gate_results`。"""
    t = (ROOT / "scripts" / "release_check.py").read_text(encoding="utf-8")
    assert '"sketch_definition": sk_def' in t


def test_protocol_document_exists() -> None:
    """★ 协议文档在（★ 官方依据的落点）。"""
    p = ROOT / "specs" / "315-eval-corpus" / "sketch-definition-protocol.md"
    assert p.is_file()
    t = p.read_text(encoding="utf-8")
    for k in ("位置", "大小", "形状关系", "直线工具", "对称"):
        assert k in t, "★ 协议缺 `%s`" % k
