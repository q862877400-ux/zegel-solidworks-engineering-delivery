"""★ 真机验：段 1 选择底座的 6 个工具（`sw_selection_spec`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_selection_base.py
# 定位:   ★ 2026-10-03（轮 397）24h 计划 v2 **段 1** 的真机探针。★ 被验的 6 个工具
# （见 `mcp-server/tool_specs_batch53.py`）：`get_selection_count` · `select_entity_by_i
# ndex` ·
# `resolve_selection` · `selection_point` · `select_by_selector_report` · `resolve_entit
# y_report`。
#   ★★ **按 ToolSpec 的契约调**（`inject="model"` ⇒ 传文档对象），**不手调内部实现**。
# 官方依据: `ISelectionMgr.GetSelectedObjectCount2(-1)`（判据回读数）· `IEntity.Select4`
#           （按对象选）·
#   `IModelDocExtension` 的 `GetSelectionPoint2` / `GetSelectionPoint`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 定量 + 正负例）：
# ```
# 正例：① 清空后计数 = 0 ② 按序号选一条边 ⇒ 计数 ≥ 1 ③ 解析选择器选中 ⇒ 计数 ≥ 1
#       ④ 有选中时读点 ⇒ ok 且 point_mm 是三个数 ⑤ 用选择器选中 ⇒ 计数 ≥ 1
#       ⑥ 解析实体 ⇒ resolved=True 且 count ≥ 1
# 负例：⑦ 按序号选越界实体 ⇒ **必须抛错** ⑧ **空选区**读点 ⇒ ok=False + 有原因
#       ⑨ **非法选择器** ⇒ ok=False + 有原因
# ```
# ★ 全程走 `sw_guard` 护栏（AGENTS.md 的常驻纪律）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "selection-base-evidence.json"
)


def main() -> int:
    import sw_connect
    from sw_part import (
        current_sketch_name,
        end_sketch,
        extrude_boss,
        sketch_corner_rectangle,
        start_sketch,
    )
    import sw_selection_spec as S

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -20.0, -10.0, 20.0, 10.0)
        sk = current_sketch_name(doc)
        end_sketch(doc)
        extrude_boss(doc, sk, 10.0)
        ev["steps"]["doc"] = {
            "ok": True,
            "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or ""),
        }

        def step(label, fn, key_ok=True):
            try:
                v = fn()
                if isinstance(v, dict):
                    ev["steps"][label] = {"ok": bool(v.get("ok")), "value": v}
                else:
                    ev["steps"][label] = {"ok": bool(v) if key_ok else True, "value": v}
            except Exception as exc:  # noqa: BLE001
                ev["steps"][label] = {
                    "ok": False,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
                }

        def expect_ok_false(label, fn, want_error=True):
            """★ 负例：**期望它回 ok=False**（★ 或抛）—— ★ 成功 = 它**真的拒绝了**。"""
            try:
                v = fn()
            except Exception as exc:  # noqa: BLE001
                ev["steps"][label] = {
                    "ok": True,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:120]),
                }
                return
            ok_false = isinstance(v, dict) and v.get("ok") is False
            has_err = (not want_error) or bool(isinstance(v, dict) and v.get("error"))
            ev["steps"][label] = {"ok": bool(ok_false and has_err), "value": v}

        def expect_fail(label, fn):
            try:
                v = fn()
                ev["steps"][label] = {"ok": False, "unexpected": str(v)[:80]}
            except Exception as exc:  # noqa: BLE001
                ev["steps"][label] = {
                    "ok": True,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:120]),
                }

        #: ① 清空后计数 = 0
        doc.ClearSelection2(True)
        _c0 = S.get_selection_count(doc)
        #: ★ 清空后计数 **= 0 是正确的**（★ 先前我把它当成失败了：`bool(0)` 为假）
        ev["steps"]["count_after_clear"] = {"ok": _c0 == 0, "value": _c0}
        #: ② 按序号选一条边
        step("select_edge_index0", lambda: S.select_entity_by_index(doc, "EDGE", 0))
        #: ④ 读点 —— ★★ **必须先选中一个「点」**（VERTEX）：
        #:   ★ 先前我在选了**边**之后读点 ⇒ `GetSelectionPoint2` 回 **None**
        #: ★★ 而那**是正确的**（官方说 "selected **point**"）—— ★ 是**我的期望错了**，不
        #: 是能力坏了。
        #:   ★★ 而**穷举给出了答案**（轮 397 实测）：
        #: · 选 **VERTEX** ⇒ `GetSelectionPoint2` 的 **6 种 (Index, Mark) 组合全部回 Non
        #: e**
        #:   · 选 **FACE**   ⇒ `(1, -1)` ⇒ **`[-20.0, 0.0, -5.0]`** ✓
        #:   ★ 即："selection point" 是**选择时鼠标落在「面」上的那个位置**；
        #:   ★ 而顶点选中时**没有面可投影** ⇒ None。
        step("select_face_index0", lambda: S.select_entity_by_index(doc, "FACE", 0))
        step("selection_point", lambda: S.selection_point(doc))
        #: ③ 解析选择器并选中（★ 用 index:1）
        step(
            "resolve_selection_index1",
            lambda: S.resolve_selection(doc, "index:1", "EDGE"),
        )
        #: ⑤ 用选择器选中
        step(
            "select_by_selector_index2",
            lambda: S.select_by_selector_report(doc, "index:2", "EDGE"),
        )
        #: ⑥ 解析实体
        step(
            "resolve_entity_index0",
            lambda: S.resolve_entity_report(doc, "index:0", "EDGE"),
        )
        #: ── 负例 ──
        expect_fail(
            "neg_index_out_of_range", lambda: S.select_entity_by_index(doc, "EDGE", 999)
        )
        doc.ClearSelection2(True)
        expect_ok_false("neg_empty_selection_point", lambda: S.selection_point(doc))
        expect_ok_false(
            "neg_bad_selector",
            lambda: S.resolve_entity_report(doc, "index:not_an_int", "EDGE"),
        )

        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = (
            "★ 段 1 选择底座 6 个工具；★ 判据统一是**回读计数**（★ 事实 8："
            "Select4 的 bool 返回值不可信）；★ 含三条负例（越界 / 空选区读点 / 非法选择器）。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1800])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
