"""★ 真机：**先上 A3 图框**再 `add_view` —— ★ 承事实 327 的具体下一步。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_datum_tag_selfcontained2.py
# 定位:   ★ 2026-10-03（轮 413）承**事实 327**：★ 上一版 `add_view` 回 `None`，
#   ★ 而**官方签名核对过是对的**（`CreateDrawViewFromModelView3` 5 参）⇒ ★ 卡点在别处。
#   ★ 事实 327 给的**具体下一步**：★ **先给图纸上 A3 图框**（用行内现成的
# `setup_current_sheet_as_a3` —— ★ 它走官方 `IDrawingDoc.SetupSheet6`），★ 再 `add_view`
# 。
#   ★ 图框文件在本机：`C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\lang\Chinese-Simplified\
#     sheetformat\**a3 - gb.slddrt**`（★ GB/T，★ 中文 UI 下的国标框）。
#   ★ 零件仍用**已在盘上**的自带示例件（★ 硬约束⑦：★ 我**不保存任何东西**）。
#   ⚠ 只新建与加注、**不保存**。
# 官方依据: `IDrawingDoc.SetupSheet6` · `IDrawingDoc.CreateDrawViewFromModelView3` ·
#   `IModelDoc2.InsertDatumTag2()`（零参）· `IView.GetDatumTagCount()`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ `GetDatumTagCount()` **真的 +1**。

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
    / "datum-tag-selfcontained2-evidence.json"
)
PART = Path(
    r"C:\Users\Public\Documents\SOLIDWORKS\SOLIDWORKS 2026\samples"
    r"\tutorial\api\squarepad_blue.sldprt"
)
A3_GB = Path(
    r"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\lang\Chinese-Simplified"
    r"\sheetformat\a3 - gb.slddrt"
)


def main() -> int:
    import sw_connect
    from sw_connect import get_com_member, safe_get_com_member
    import drawing_workflow as DW

    ev: dict = {
        "steps": {},
        "at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "part": str(PART),
        "a3_format": str(A3_GB),
        "a3_exists": A3_GB.exists(),
    }
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "drawing")
        ev["steps"]["new_drawing"] = {
            "ok": doc is not None,
            "title": str(safe_get_com_member(doc, "GetTitle") or ""),
        }
        #: ① **先上 A3 图框**（★ 事实 327 的具体下一步）
        try:
            rep = DW.setup_current_sheet_as_a3(doc, [str(A3_GB)])
            ev["steps"]["setup_a3_sheet"] = {
                "ok": rep is not None,
                "returned": json.dumps(rep, ensure_ascii=False, default=str)[:130]
                if isinstance(rep, (dict, list))
                else str(rep)[:130],
            }
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["setup_a3_sheet"] = {
                "ok": False,
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
            }
        #: ② 加视图
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
                "err": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
            }
        if view is not None:
            before = None
            try:
                before = safe_get_com_member(view, "GetDatumTagCount")
                ev["steps"]["count_before"] = {"ok": True, "value": before}
            except Exception as exc:  # noqa: BLE001
                ev["steps"]["count_before"] = {
                    "ok": False,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:110]),
                }
            try:
                tag = get_com_member(doc, "InsertDatumTag2")
                ev["steps"]["insert_datum_tag2"] = {
                    "ok": tag is not None,
                    "returned": str(tag)[:60],
                }
            except Exception as exc:  # noqa: BLE001
                ev["steps"]["insert_datum_tag2"] = {
                    "ok": False,
                    "err": "%s: %s" % (type(exc).__name__, str(exc)[:140]),
                }
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
            "★ 事实 327 的具体下一步：★ **先上 A3 图框**（`setup_current_sheet_as_a3` 走官方 "
            "`SetupSheet6`）★ **再** `add_view`。★ 判据是 `GetDatumTagCount()` 真的 +1。"
            "★ 零件用**已在盘上**的自带件 ⇒ ★ 不保存任何东西（硬约束⑦）。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        print(json.dumps(ev, ensure_ascii=False, indent=1)[:1600])
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
