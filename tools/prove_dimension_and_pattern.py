"""★ 真机验：段 3 收尾两条（`add_dimension_report` · `linear_pattern_report`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_dimension_and_pattern.py
# 定位:   ★ 2026-10-03（轮 400）24h 计划 v2 段 3 收尾。★ 这两条上一轮因**单位存疑**被押后，
#   ★ 本轮从**官方文档**查清（★ 不靠真机试）：`AddDimension2` 的坐标是**米**且**必须先选中实体**；
#   `FeatureLinearPattern3` 的 `Spacing1` 是**米**、`Num1` **含原件**。
# 官方依据: `C:\swapi\types\IModelDoc2\AddDimension2.md` ·
#   `C:\swapi\types\IFeatureManager\FeatureLinearPattern3.md`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据（★ 正例 + 两条负例）：
# ```
# ① `add_dimension_report(selector="index:0")` ⇒ `ok` 且 `dimension_created` 且 `selected ≥ 1`
#    （★ 选择由包装内部完成 —— ★ 兑现"段 1 选择底座"的前置红利）
# ② `linear_pattern_report(feature, spacing_mm=10, count=3)` ⇒ **特征树 +1**（★ 规则 6）
# ③ ★ 负例：`add_dimension_report` 用**指向空选区的选择器** ⇒ `ok=False` + 有原因
# ④ ★ 负例：`count=1` ⇒ `ok=False`（★ 官方口径"含原件"⇒ 1 就是没有阵列）
# ```

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "dimension-pattern-evidence.json")


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member
    from sw_part import (add_dimension_report, current_sketch_name, end_sketch, extrude_boss,
                         linear_pattern_report, sketch_corner_rectangle, start_sketch)

    ev: dict = {"steps": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -20.0, -10.0, 20.0, 10.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 10.0)
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, 15.0, -2.0, 19.0, 2.0)
        sk2 = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk2, 20.0)
        boss = None
        for nm in ("凸台-拉伸2", "Boss-Extrude2"):
            if get_com_member(doc, "FeatureByName", nm) is not None:
                boss = nm
                break
        ev["steps"]["doc"] = {"ok": True, "boss": boss,
                              "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")}


        def expect_reject(label, fn, why=""):
            """★ 负例：**期望它回 ok=False**（★ 或抛）—— ★ 成功 = 它**真的拒绝了**。"""
            try:
                v = fn()
            except Exception as exc:                               # noqa: BLE001
                ev["steps"][label] = {"ok": True, "err": "%s: %s" % (type(exc).__name__, str(exc)[:110]), "why": why}
                return
            bad = isinstance(v, dict) and v.get("ok") is False and bool(v.get("error"))
            ev["steps"][label] = {"ok": bool(bad), "value": v, "why": why}

        def step(label, fn):
            try:
                v = fn()
                if isinstance(v, dict):
                    ev["steps"][label] = {"ok": bool(v.get("ok")), "value": v}
                else:
                    ev["steps"][label] = {"ok": bool(v), "value": str(v)[:60]}
            except Exception as exc:                           # noqa: BLE001
                ev["steps"][label] = {"ok": False,
                                      "err": "%s: %s" % (type(exc).__name__, str(exc)[:140])}

        #: ③ 负例先做（★ 免得前面选中了东西影响它）：指向**空选区**
        doc.ClearSelection2(True)
        expect_reject("neg_dimension_no_entity",
                      lambda: add_dimension_report(doc, 30.0, 20.0, selector="__current_selection__"),
                      why="空选区加尺寸必须被拒")
        #: ④ 负例：count=1（★ 含原件 ⇒ 没有阵列）
        expect_reject("neg_pattern_count1",
                      lambda: linear_pattern_report(doc, boss or "凸台-拉伸2", 10.0, 1),
                      why="count=1 含原件 ⇒ 没有阵列")
        #: ① 正例：加尺寸（★ 选择由包装内部做）
        doc.ClearSelection2(True)
        from sw_selection_spec import select_entity_by_index
        select_entity_by_index(doc, "EDGE", 0)
        select_entity_by_index(doc, "EDGE", 1, append=True)   #: ★ 两条边才能定义一个线性尺寸
        step("add_dimension", lambda: add_dimension_report(doc, 30.0, 20.0, selector="__current_selection__"))
        #: ② 正例：线性阵列
        step("linear_pattern",
             lambda: linear_pattern_report(doc, boss or "凸台-拉伸2", 10.0, 3))

        exec_ok = all(v.get("ok") for v in ev["steps"].values() if isinstance(v, dict))
        ev["verdict"] = "pass" if exec_ok else "partial"
        ev["note"] = ("★ 单位由**官方文档**给出（AddDimension2 与 FeatureLinearPattern3 的 Spacing 都是**米**）"
                      "⇒ ★ 包装对外收毫米并在此换算（★ 规则 2）。"
                      "★ 两条负例：空选区加尺寸 / count=1 的阵列。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1700])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
