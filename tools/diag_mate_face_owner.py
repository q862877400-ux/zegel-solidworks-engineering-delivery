"""聚焦诊断：**一束一束**射线地看归属，并打印每束命中点的坐标。

## 为什么

上一跑两束射线都报告属于「组件2」（`distinct: 1`），但按我的几何推算，
x=−40mm 处只有组件1 覆盖 ⇒ 应该命中组件1。
⇒ 要么我的几何假设错，要么 `GetSelectedObjectsComponent4` 的用法错。
**分开测**能一次分清。

## 输出

对每一束射线：
- `selected`：选中数
- `owner`：`GetSelectedObjectsComponent4(k, mark)` 回的组件名
- `hit`：命中面的**最近点坐标**（mm）—— 用它反推打到了哪块板
- 组件1/组件2 各自的**平移**（mm）
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
# 仓库:   本项目自身（工具 · 配合选面聚焦诊断）
# 文件:   tools/diag_mate_face_owner.py
# 定位:   一束一束地验证 `SelectByRay` 命中了哪个组件，并打印命中点坐标。
#          起因：两束射线都报告属于组件2（`distinct: 1`）⇒ 配合变成「面和它自己」。
# 官方依据: IModelDocExtension::SelectByRay（11 参，Mark=1）·
#          ISelectionMgr::GetSelectedObjectsComponent4(Index, Mark) ·
#          IFace2::GetClosestPointOn → IMathPoint::ArrayData（米）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

PART = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
DEST = R / "output" / "mate-face-owner.json"

#: 四束候选射线（米）：x 从「只属于组件1」到「只属于组件2」
CANDIDATES = (
    ("只组件1(x=-90mm)", -0.090, 0.0, 0.070, -1.0),
    ("只组件1(x=-40mm)", -0.040, 0.0, 0.070, -1.0),
    ("只组件2(x=+70mm)", 0.070, 0.0, 0.100, -1.0),
    ("重叠区(x=0mm)", 0.0, 0.0, 0.100, -1.0),
)

import sw_assembly as asm_  # noqa: E402
import sw_connect as c_  # noqa: E402
from sw_connect import get_com_member  # noqa: E402


def main() -> int:
    ev: dict = {"probe": "diag-mate-face-owner", "rays": []}
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

        #: 两个组件的平移（毫米）—— 用它反推各自的 x 覆盖范围
        comps = list(get_com_member(asm, "GetComponents", False) or ())
        trans = []
        for cp in comps:
            tr = get_com_member(cp, "Transform2")
            data = list(get_com_member(tr, "ArrayData") or ())
            trans.append(
                {
                    "name": str(get_com_member(cp, "Name2") or ""),
                    "t_mm": [round(data[9] * 1000.0, 2), round(data[10] * 1000.0, 2),
                             round(data[11] * 1000.0, 2)] if len(data) >= 12 else None,
                }
            )
        ev["components"] = trans
        print("① 组件平移(mm)：%s" % json.dumps(trans, ensure_ascii=False))

        ext = get_com_member(asm, "Extension")
        sm = get_com_member(asm, "SelectionManager")
        for label, x, y, z, dz in CANDIDATES:
            rec: dict = {"label": label, "ray": [x, y, z, dz]}
            asm.ClearSelection2(True)
            ok_r, _ = c_.try_call(
                c_.get_com_member, ext, "SelectByRay",
                x, y, z, 0.0, 0.0, dz, 1e-4, 2, False, 1, 0,
            )
            try:
                n = int(get_com_member(sm, "GetSelectedObjectCount2", 1) or 0)
            except Exception:  # noqa: BLE001
                n = -1
            rec["selected"] = n
            if n >= 1:
                try:
                    ok_o, comp = c_.try_call(
                        c_.get_com_member, sm, "GetSelectedObjectsComponent4", 1, 1
                    )
                    rec["owner"] = str(get_com_member(comp, "Name2") or "") if ok_o else None
                except Exception as exc:  # noqa: BLE001
                    rec["owner_err"] = type(exc).__name__
                try:
                    ok_f, face = c_.try_call(
                        c_.get_com_member, sm, "GetSelectedObject6", 1, 1
                    )
                    if ok_f and face is not None:
                        pt = c_.get_com_member(face, "GetClosestPointOn", 0.0, 0.0, 0.0)
                        arr = list(get_com_member(pt, "ArrayData") or ())
                        rec["hit_mm"] = [round(v * 1000.0, 2) for v in arr[:3]]
                except Exception as exc:  # noqa: BLE001
                    rec["hit_err"] = type(exc).__name__
            ev["rays"].append(rec)
            print("   %-20s 选中=%s · 归属=%s · 命中=%s"
                  % (label, rec.get("selected"), rec.get("owner"), rec.get("hit_mm")))
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
