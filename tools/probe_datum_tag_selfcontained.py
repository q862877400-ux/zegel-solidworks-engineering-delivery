"""★ 真机：自足建图（新工程图 + 从**已在盘上**的零件加视图）⇒ 再验 `InsertDatumTag2()`。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_datum_tag_selfcontained.py
# 定位:   ★ 2026-10-03（轮 412）24h 计划 v2 收敛报告 §五 第 ④ 条（objective ② 的画图域
#           ）。
#   ★★ 承**事实 326** 的结论：★ **外部夹具会把"不可控的加载弹窗"带进验证路径** ⇒
#     ★ 验证路径必须**自足**。
#   ★★ 而"自足"在这里有一条**硬约束⑦ 带来的边界**（★ 本轮读签名时才发现）：
#     · `add_view(drawing_model, **part_path**, view_name, x, y, …)` 要的是**零件文件路径**
#       ⇒ ★ **自建的零件必须先保存到盘上** ⇒ ★ **那撞硬约束⑦（不碰保存/另存/删除）** ⚠
#     ⇒ ★★ 正解：★ **用已经在盘上的零件**（★ SolidWorks 自带示例零件，★ 我只读不写）
#       —— ★ 那样**我不保存任何东西**，★ 而视图也建得出来。
#   ★ 建图链条（★ 全部来自仓内的子技能实现，★ 不是新发明）：
#     `new_document(sw, "drawing")` → `add_view(drawing, 零件路径, "*Front", x, y)`
#     → ★ 回读 `IView.GetDatumTagCount()` 作**基线** → `InsertDatumTag2()` → **再回读**。
#   ⚠ 只**新建并加注**、**不保存**（★ 硬约束⑦）⇒ 不动任何已有文件。
# 官方依据: `IModelDoc2.InsertDatumTag2()`（**零参**）· `IView.GetDatumTagCount()`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ `GetDatumTagCount()` **真的 +1**（★ 定量回读）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(
    0, str(REPO_ROOT / "subskills" / "solidworks-engineering-drawing" / "scripts")
)

OUT = Path(
    Path(__file__).resolve().parents[1]
    / "output"
    / "datum-tag-selfcontained-evidence.json"
)
PART = Path(
    r"C:\Users\Public\Documents\SOLIDWORKS\SOLIDWORKS 2026\samples"
    r"\tutorial\api\squarepad_blue.sldprt"
)


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    import drawing_workflow as DW

    ev: dict = {
        "steps": {},
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "part_fixture": str(PART),
        "part_exists": PART.exists(),
    }
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "drawing")
        ev["steps"]["new_drawing"] = {
            "ok": doc is not None,
            "title": str(safe_get_com_member(doc, "GetTitle") or ""),
        }
        #: ① 加视图（★ 零件是**已在盘上**的 —— 我没有保存任何东西）
        view = None
        try:
            view = DW.add_view(doc, str(PART), "*Front", 0.15, 0.15)
            ev["steps"]["add_view"] = {
                "ok": view is not None,
                "returned": str(view)[:52],
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["add_view"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:130]),
            }
        if view is not None:
            #: ② 基线回读
            before = None
            try:
                before = safe_get_com_member(view, "GetDatumTagCount")
                ev["steps"]["count_before"] = {"ok": True, "value": before}
            except Exception as exc:  # noqa: BLE001
                ev["steps"]["count_before"] = {
                    "ok": False,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:110]),
                }
            #: ③ 插基准标签（零参）
            try:
                tag = get_com_member(doc, "InsertDatumTag2")
                ev["steps"]["insert_datum_tag2"] = {
                    "ok": tag is not None,
                    "returned": str(tag)[:60],
                }
            except Exception as exc:  # noqa: BLE001
                ev["steps"]["insert_datum_tag2"] = {
                    "ok": False,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:130]),
                }
            #: ④ 判据：回读 +1
            try:
                after = safe_get_com_member(view, "GetDatumTagCount")
                ev["steps"]["count_after"] = {"ok": True, "value": after}
                ev["steps"]["judged_by_readback"] = {
                    "ok": before is not None
                    and after is not None
                    and after == before + 1,
                    "count": [before, after],
                }
            except Exception as exc:  # noqa: BLE001
                ev["steps"]["count_after"] = {
                    "ok": False,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:110]),
                }
        ev["verdict"] = (
            "pass" if ev["steps"].get("judged_by_readback", {}).get("ok") else "partial"
        )
        ev["note"] = (
            "★ 自足路径（★ 事实 326 的处方）：★ **新建内存工程图** + 从**已在盘上**的零件加视图 "
            "—— ★ 我**不保存任何东西**（★ 那条正是 `add_view` 要 `part_path` 带来的边界，"
            "★ 硬约束⑦）。★ 判据是 `GetDatumTagCount()` 真的 +1。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1500])
        print("  产物: %s ⇒ %s" % (OUT, str(ev["verdict"]).upper()))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None:
                t = str(safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
