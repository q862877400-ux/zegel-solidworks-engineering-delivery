"""★ 批次 14 的契约测试（本轮扩写）：`solidworks_entities_on_body` 改成**可 JSON 化的报告形态**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `mcp-server/tool_specs_batch14.py` · `scripts/sw_selection_spec.py`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B3-1（idx 115 edges + idx 145 faces）**；
#         ★ 裁决书强制「**扩**已有的 `solidworks_entities_on_body`，**不许开平行工具**」✓
#         ★★ 本文件钉住四件事：
#           ① 工具**名字没变**、指向已改成 `entities_report`（★ 不是新开一条）
#           ② `entities_report` / `entity_geometry` **只回 JSON 可序列化的东西**
#              （★ 旧的 `entities_on_body` 回 **COM 对象** ⇒ 过不了 MCP 边界）
#           ③ ★★ **`IEdge` 上不许出现「长度」成员调用** —— 官方成员表里没有它，
#              ★ 边长只能由两个顶点**自己算**（★ 这是我真机踩出来的）
#           ④ 判据是**计数 + 欧拉公式 `V−E+F=2`**（★ 不依赖任何新 API）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib
import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import tool_specs_batch14 as b14                              # noqa: E402


def _spec():
    return next(s for s in b14.SPECS_BATCH14 if s.name == "solidworks_entities_on_body")


def test_tool_name_unchanged_but_now_points_at_the_report_function():
    """★★ 裁决书：**扩**已有工具（名字不变），★ **不许开平行工具** ——
    而改指向的理由是**可核的**：旧的 `entities_on_body` 回 COM 对象、过不了 JSON 边界 ✓"""
    s = _spec()
    assert s.function == "entities_report", s.function
    names = [x.name for x in b14.SPECS_BATCH14]
    assert names.count("solidworks_entities_on_body") == 1, names
    assert not any("entity" in n and n != "solidworks_entities_on_body" for n in names), names
    m = importlib.import_module("scripts.sw_selection_spec")
    assert callable(getattr(m, "entities_report"))
    assert callable(getattr(m, "entity_geometry"))


def test_declared_params_bind_to_the_report_function():
    s = _spec()
    sig = inspect.signature(importlib.import_module("scripts.sw_selection_spec").entities_report)
    for p in s.params:
        assert p.name in sig.parameters, (p.name, list(sig.parameters))
    assert sig.parameters["kind"].default is inspect.Parameter.empty      # ★ kind 必填


def test_report_shape_is_json_serializable_and_self_describing():
    """★ 报告形态：`{ok, kind, body_index, count, entities, euler, error}` —— ★ 都能 JSON 化 ✓"""
    import sw_selection_spec as SS
    r = SS.entities_report(None, "EDGE")                   # ★ 不碰 COM：model=None 走早退分支
    assert r["ok"] is False and r["error"], r
    for key in ("ok", "kind", "body_index", "count", "entities", "euler", "error"):
        assert key in r, (key, sorted(r))
    json.dumps(r, ensure_ascii=False)                      # ★ 必须可序列化（旧的会在这里炸）


def test_edge_has_no_length_member_in_the_source():
    """★★★ `IEdge` **没有**「长度」成员（官方成员表逐条列过）⇒ ★ 本仓**不许**调 `IEdge.GetLength`。

    ★ 判据：正文里**不许出现** `"GetLength"`（★ 边长必须由两个顶点算）——
      ★ 用 `strip_comments_and_strings` 把注释里的"反面教材引用"与真调用**分开** ✓
    """
    sys.path.insert(0, str(ROOT / "scripts"))
    from check_env_pitfalls import strip_comments_and_strings
    src = (ROOT / "scripts" / "sw_selection_spec.py").read_text(encoding="utf-8")
    code = strip_comments_and_strings(src)
    assert "GetLength" not in code, "★ IEdge 上没有长度成员；长度要用 GetStartVertex/GetEndVertex 算"
    assert '"GetStartVertex"' in src and '"GetEndVertex"' in src, "★ 端点才是官方入口"
    assert '"GetPoint"' in src and '"GetArea"' in src, "★ 顶点读数与面积读数都要有"


def test_euler_formula_is_the_declared_criterion():
    """★ 判据声明在返回值里（★ 一个人看代码就知道该看哪个字段）"""
    import sw_selection_spec as SS
    src = inspect.getsource(SS.entities_report)
    assert "V−E+F=2" in src or "V-E+F=2" in src or "v_minus_e_plus_f" in src, src[:200]


def test_batch14_specs_all_resolve():
    for s in b14.SPECS_BATCH14:
        m = importlib.import_module("scripts.%s" % s.module)
        assert callable(getattr(m, s.function, None)), (s.name, s.module, s.function)
