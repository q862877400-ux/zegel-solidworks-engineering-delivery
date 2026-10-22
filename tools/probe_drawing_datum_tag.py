"""★ 真机：工程图**标注的写操作**第一枪 —— `InsertDatumTag2()` + `GetDatumTagCount()` 回读。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_drawing_datum_tag.py
# 定位:   ★ 2026-10-03（轮 411）24h 计划 v2 收敛报告 §五 第 ④ 条（objective ② 的画图域
#           ）。
#   ★★ **差距是实的**：`capabilities.yaml` 的 `drawing_*` 条目自己写着
#     「**工程图的写操作（加视图 / 标注 / 表格 / BOM）不在本能力内**」，
#     而工具面 13 个全是**读/查询 + 比例**。
#   ★ 而 `Hem`/`Jog` 那两条：★ **反射 dump 里一个都没有** ⇒ 按**铁律 5**
#     「名字缺席 = 官方 API 里没有这个成员」⇒ 不猜、不做（★ 见事实 326）。
#   ★★ **`balloon` / `datum` 在**：`IModelDoc2.InsertDatumTag2` 是**零参**（★ 与已能用的
#     `gtol_insert` 同形），★ 而 **`IView.GetDatumTagCount()`** 是**现成的回读** ⇒
#     ★ 判据可以**定量**（★ 那正是"规则 6"要的）。
# ★★ **夹具用法照 capabilities 里记的成法**：「用 SolidWorks 自带示例图当**有内容的测试
# 夹具**」
#     （★ 那样不必先造工程图 + 视图）—— ★ 本探针用 `samples\introsw\box.slddrw`。
#   ⚠ 只**打开并加注**、**不保存**（★ 硬约束⑦：不碰保存/另存/删除）⇒ 原文件不受影响。
# 官方依据: `IModelDoc2.InsertDatumTag2()`（**零参** · `System.object`）·
#   `IView.GetDatumTagCount()`（`System.int`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **`GetDatumTagCount()` 真的 +1**（★ 定量回读，★ 不看返回值）。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "drawing-datum-tag-evidence.json"
)
FIXTURE = Path(
    r"C:\Users\Public\Documents\SOLIDWORKS\SOLIDWORKS 2026\samples\introsw\box.slddrw"
)


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    from scripts.sw_drawing_view import get_first_view

    ev: dict = {
        "steps": {},
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "fixture": str(FIXTURE),
        "fixture_exists": FIXTURE.exists(),
    }
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        if not FIXTURE.exists():
            ev["steps"]["open"] = {"ok": False, "err": "夹具不存在"}
        else:
            doc = sw_connect.open_document(sw, str(FIXTURE), read_only=True)
            ev["steps"]["open"] = {
                "ok": doc is not None,
                "title": str(safe_get_com_member(doc, "GetTitle") or ""),
            }
        if doc is not None:
            #: ① 取第一个视图（★ 回读的宿主）
            view = None
            try:
                view = get_first_view(doc)
                ev["steps"]["first_view"] = {
                    "ok": view is not None,
                    "name": str(safe_get_com_member(view, "GetName") or ""),
                }
            except Exception as exc:  # noqa: BLE001
                ev["steps"]["first_view"] = {
                    "ok": False,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:110]),
                }
            #: ② 回读基线
            before = None
            if view is not None:
                try:
                    before = safe_get_com_member(view, "GetDatumTagCount")
                    ev["steps"]["datum_count_before"] = {"ok": True, "value": before}
                except Exception as exc:  # noqa: BLE001
                    ev["steps"]["datum_count_before"] = {
                        "ok": False,
                        "err": "%s: %s" % (type(exc).__name__, str(exc)[:110]),
                    }
            #: ③ 插基准标签（★ 零参）
            if view is not None:
                try:
                    tag = get_com_member(doc, "InsertDatumTag2")
                    ev["steps"]["insert_datum_tag2"] = {
                        "ok": tag is not None,
                        "returned": str(tag)[:60],
                    }
                except Exception as exc:  # noqa: BLE001
                    ev["steps"]["insert_datum_tag2"] = {
                        "ok": False,
                        "err": "%s: %s" % (type(exc).__name__, str(exc)[:120]),
                    }
                #: ④ 回读 —— ★ **判据在这里**
                try:
                    after = safe_get_com_member(view, "GetDatumTagCount")
                    ev["steps"]["datum_count_after"] = {"ok": True, "value": after}
                    ev["steps"]["judged_by_readback"] = {
                        "ok": before is not None
                        and after is not None
                        and after == before + 1,
                        "count": [before, after],
                    }
                except Exception as exc:  # noqa: BLE001
                    ev["steps"]["datum_count_after"] = {
                        "ok": False,
                        "err": "%s: %s" % (type(exc).__name__, str(exc)[:110]),
                    }
        exec_ok = all(
            v.get("ok")
            for v in ev["steps"].values()
            if isinstance(v, dict) and "judged_by_readback" not in ev["steps"] or True
        )
        judged = ev["steps"].get("judged_by_readback", {}).get("ok")
        ev["verdict"] = "pass" if judged else "partial"
        ev["note"] = (
            "★ 判据是 **`IView.GetDatumTagCount()` 真的 +1**（★ 定量回读，不看返回值）。"
            "★ 夹具用 SolidWorks 自带示例图（★ 照 capabilities 里记的成法），"
            "★ 只打开并加注、**不保存**（★ 硬约束⑦）。"
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
