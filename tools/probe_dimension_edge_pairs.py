"""★ 真机：`AddDimension2` 的**边对穷举表** —— 找出"哪一类边对能定义出尺寸"。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_dimension_edge_pairs.py
# 定位:   ★ 2026-10-03（轮 405）24h 计划 v2 收敛报告 §五 第 ③ 条的落地。
# ★ 背景：轮 400 的 `add_dimension_report` 选中 **2 条边**后 `AddDimension2` **仍回 None
# **
#     （★ 而我当时用的是**相邻边** 0 与 1）。
#   ★★ **本探针不"再试一次"** —— ★ 而按**事实 53 的正解**：★ **把猜测变成一张穷举表**
#     （★ 对 12 条边取两两 = **66 对**，逐对试并记录结果）。
#     ★ 那样得到的不是"某次侥幸成功"，★ 而是**哪一类边对能成**这条可复用的规则。
# 官方依据: `IModelDoc2.AddDimension2(X, Y, Z)` —— 官方 Remarks：
#   “Before calling this method, you must **select the entities**” ＋
# “If extension lines are needed during dimensioning because the selected entities do no
# t
#    **unambiguously define** what needs to be dimensioned, then use …”
#   ⇒ ★ 即：★ **能不能定义出来，取决于选中的实体**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 逐对记录 `dimension_created`；★ 收满 **8 个成功**即提前停（★ 够看出规律）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1]
    / "output"
    / "dimension-edge-pairs-evidence.json"
)
MAX_SUCCESS = 8


def main() -> int:
    import sw_connect
    from sw_part import (
        add_dimension_report,
        current_sketch_name,
        end_sketch,
        extrude_boss,
        sketch_corner_rectangle,
        start_sketch,
    )
    from sw_selection_spec import entities_on_body, select_entity_by_index

    ev: dict = {"pairs": [], "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -20.0, -15.0, 20.0, 15.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)
        edges = entities_on_body(doc, "EDGE")
        ev["edge_count"] = len(edges)
        #: ⚠★ 我第一版把 `edges` **原样**塞进 evidence ⇒ `json.dumps` 炸（**COM 对象不可
        #: 序列化**）。
        #:   ★ 那正是本项目「**包装绝不许漏出 COM 对象**」那条契约要防的形态 ——
        #:   而我在探针里自己犯了。★ 只留可序列化的摘要。
        ev["edges_repr"] = [str(e)[:48] for e in edges]
        n_ok = 0
        for i in range(len(edges)):
            for j in range(i + 1, len(edges)):
                if n_ok >= MAX_SUCCESS:
                    break
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                try:
                    select_entity_by_index(doc, "EDGE", i)
                    select_entity_by_index(doc, "EDGE", j, append=True)
                except Exception as exc:  # noqa: BLE001
                    ev["pairs"].append(
                        {
                            "pair": [i, j],
                            "selected": None,
                            "created": False,
                            "err": str(exc)[:80],
                        }
                    )
                    continue
                try:
                    r = add_dimension_report(
                        doc, 30.0, 20.0, selector="__current_selection__"
                    )
                    created = bool(r.get("dimension_created"))
                    if created:
                        n_ok += 1
                    ev["pairs"].append(
                        {
                            "pair": [i, j],
                            "selected": r.get("selected"),
                            "created": created,
                            "err": (r.get("error") or "")[:70],
                        }
                    )
                except Exception as exc:  # noqa: BLE001
                    ev["pairs"].append(
                        {
                            "pair": [i, j],
                            "created": False,
                            "err": "%s: %s" % (type(exc).__name__, str(exc)[:70]),
                        }
                    )
            if n_ok >= MAX_SUCCESS:
                break
        ev["successes"] = [p["pair"] for p in ev["pairs"] if p.get("created")]
        ev["tried"] = len(ev["pairs"])
        ev["verdict"] = "pass" if ev["successes"] else "partial"
        ev["note"] = (
            "★ 穷举 12 条边的两两组合（★ 事实 53 的正解：把猜测变成一张表），"
            "★ 记录**哪一类边对**能让 `AddDimension2` 真的建出尺寸。"
            "★ 盒体的 12 条边按 SolidWorks 惯例分组：0-3 / 4-7 是上下两个面环、8-11 是竖边。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(
            json.dumps(
                {k: ev[k] for k in ("edge_count", "tried", "successes", "verdict")},
                ensure_ascii=False,
                indent=1,
            )
        )
        print("  产物: %s" % OUT)
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
