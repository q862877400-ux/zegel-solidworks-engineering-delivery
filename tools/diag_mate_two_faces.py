"""补一步：**同时选中两个面**后再读归属 —— 隔离「两项选择」这个情形。

## 为什么

聚焦测试（每次只选一个）证明几何是对的：
```
x=-40mm → 板1_rev-1-1 ✓      x=+70mm → 板1_rev-1-2 ✓
```
但探针**同时选两个**后读到的却是「两个都属于组件2」。

⇒ 必须在「两个已同时选中」的状态下读归属，才能分清是
  ① 选择本身错了，还是 ② `GetSelectedObjectsComponent4` 在多项下不可靠。
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))
sys.path.insert(0, str(R / "tools"))


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 多项选择的归属诊断）
# 文件:   tools/diag_mate_two_faces.py
# 定位:   同时选中两块板的一个面，再逐项读归属与名字 —— 分清「选错」与「读法错」。
# 官方依据: IModelDocExtension::SelectByRay · ISelectionMgr::GetSelectedObjectsComponent4 ·
#          ISelectionMgr::GetSelectedObject6 · ISelectionMgr::GetSelectedObjectCount2
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

PART = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "mate-two-faces.json"

import sw_assembly as asm_  # noqa: E402
import sw_connect as c_  # noqa: E402
from sw_connect import get_com_member  # noqa: E402


def main() -> int:
    ev: dict = {"probe": "diag-mate-two-faces"}
    conn = c_.connect_solidworks(wait_seconds=30)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass
    try:
        for d in list(get_com_member(sw, "GetDocuments") or ()):
            sw.CloseDoc(str(get_com_member(d, "GetTitle") or ""))
        c_.open_document(sw, str(PART))
        ok, asm = c_.try_call(c_.new_document, sw, "assembly")
        try:
            sw.ActivateDoc3(str(get_com_member(asm, "GetTitle") or ""), 0, False)
        except Exception:  # noqa: BLE001
            pass
        asm_.add_component(asm, str(PART), x_m=0.0, y_m=0.0, z_m=0.0, sw=sw)
        asm_.add_component(asm, str(PART), x_m=0.030, y_m=0.0, z_m=0.050, sw=sw)

        ext = get_com_member(asm, "Extension")
        sm = get_com_member(asm, "SelectionManager")
        asm.ClearSelection2(True)

        #: 一束打组件1 顶面（x=−40mm，自上而下）；一束打组件2 底面（x=+70mm，自下而上）
        for k, (x, y, z, dz, append) in enumerate(
            (
                (-0.040, 0.0, 0.070, -1.0, False),
                (0.070, 0.0, 0.040, 1.0, True),
            ),
            1,
        ):
            ok_r, _ = c_.try_call(
                c_.get_com_member, ext, "SelectByRay",
                x, y, z, 0.0, 0.0, dz, 1e-4, 2, append, 1, 0,
            )
            try:
                n = int(get_com_member(sm, "GetSelectedObjectCount2", 1) or 0)
            except Exception:  # noqa: BLE001
                n = -1
            print("   射线%d：ok=%s · 累计选中=%s" % (k, ok_r, n))

        recs = []
        for k in (1, 2):
            rec: dict = {"index": k}
            try:
                ok_o, comp = c_.try_call(
                    c_.get_com_member, sm, "GetSelectedObjectsComponent4", k, 1
                )
                rec["owner"] = (
                    str(get_com_member(comp, "Name2") or "") if ok_o and comp else None
                )
            except Exception as exc:  # noqa: BLE001
                rec["owner_err"] = type(exc).__name__
            for mark in (-1, 1):
                try:
                    ok_s, obj = c_.try_call(
                        c_.get_com_member, sm, "GetSelectedObject6", k, mark
                    )
                    rec["obj_type_mark%d" % mark] = (
                        str(get_com_member(obj, "GetTypeName2") or "") if ok_s and obj else None
                    )
                except Exception as exc:  # noqa: BLE001
                    rec["obj_err_mark%d" % mark] = type(exc).__name__
            recs.append(rec)
            print("   项%d：归属=%s · 类型(-1)=%s · 类型(1)=%s"
                  % (k, rec.get("owner"), rec.get("obj_type_mark-1"),
                     rec.get("obj_type_mark1")))
        ev["items"] = recs
        owners = [r.get("owner") for r in recs]
        ev["distinct"] = len({o for o in owners if o}) if all(owners) else None
        print("★ distinct = %s" % ev["distinct"])
        return 0
    finally:
        try:
            for d in list(get_com_member(sw, "GetDocuments") or ()):
                sw.CloseDoc(str(get_com_member(d, "GetTitle") or ""))
        except Exception:  # noqa: BLE001
            pass
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        DEST.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("   证据已写：%s" % DEST)


if __name__ == "__main__":
    raise SystemExit(main())
