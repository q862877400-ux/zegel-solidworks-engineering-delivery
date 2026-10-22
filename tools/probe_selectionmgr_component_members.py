"""★ 在**活的 `SelectionMgr`** 上逐个试官方候选成员，看**哪一个真的可达**（★ 不猜名字）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）
# 文件:   `C:\\swapi\\types\\ISelectionMgr\\GetSelectedObjectsComponent*.md`（官方 4 代）
# 定位:   ★ 2026-10-04：`get_selected_component` 改用后继 `…Component4` 后**仍**报
#         `<unknown>.GetSelectedObjectsComponent3/4` ⇒ ★ **不再猜**，直接在活对象上枚举可达性 ✓
# 官方依据: `GetSelectedObjectsComponent4.md:31` 逐字「the now obsolete `GetSelectedObje
#           ctsComponent3`」；
#         `…4.md:14` 签名 `System.object GetSelectedObjectsComponent4( System.int Index, System.int Mark )`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8")
from scripts import sw_connect                                    # noqa: E402

ASM = ROOT / "output" / "fr008-assembly-copy.SLDASM"
OUT = ROOT / "output" / "selectionmgr-member-probe.json"


def main() -> int:
    ev: dict = {"_": "SelectionMgr 上组件取用成员的**可达性**枚举", "tries": {}}
    sw = model = None
    try:
        sw, _m, _meta = sw_connect.connect_solidworks(wait_seconds=30, return_metadata=True)
        model = sw_connect.open_document(sw, ASM, silent=True)
        sel = sw_connect.get_com_member(model, "SelectionManager")
        ev["selection_manager_type"] = type(sel).__name__
        #: ① 先把第一个顶层组件**选上**（★ 走官方选择管理器，不裸坐标）
        comps = list(sw_connect.get_com_member(model, "GetComponents", True) or [])
        ev["component_count"] = len(comps)
        if comps:
            try:
                sw_connect.get_com_member(sel, "AddSelectionListObject", comps[0],
                                          sw_connect.create_empty_dispatch_variant())
                ev["select_ok"] = True
            except Exception as exc:                                  # noqa: BLE001
                ev["select_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:180])
        ev["selected_count"] = int(sw_connect.get_com_member(sel, "GetSelectedObjectCount2", -1) or 0)
        #: ② 逐个试候选成员（★ 四代 + 两个常用的兄弟成员）
        for member, args in (("GetSelectedObjectsComponent4", (0, 0)),
                             ("GetSelectedObjectsComponent3", (0, 0)),
                             ("GetSelectedObjectsComponent2", (0, 0)),
                             ("GetSelectedObjectsComponent", (0,)),
                             ("GetSelectedObject6", (1, -1)),
                             ("GetSelectedObjectType3", (1, -1))):
            try:
                v = sw_connect.get_com_member(sel, member, *args)
                ev["tries"][member] = {"reachable": True, "type": type(v).__name__,
                                       "none": v is None}
            except Exception as exc:                                  # noqa: BLE001
                ev["tries"][member] = {"reachable": False,
                                       "error": "%s: %s" % (type(exc).__name__, str(exc)[:120])}
            print("  %-32s %s" % (member, json.dumps(ev["tries"][member], ensure_ascii=False)[:150]))
    except Exception as exc:                                          # noqa: BLE001
        ev["★_异常"] = "%s: %s" % (type(exc).__name__, str(exc)[:300])
        print("★ 异常:", ev["★_异常"])
    finally:
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
        print("★ wrote", OUT)
        if sw is not None and model is not None:
            try:
                sw_connect.get_com_member(sw, "CloseDoc", str(
                    sw_connect.get_com_member(model, "GetTitle") or ""))
            except Exception:                                         # noqa: BLE001
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
