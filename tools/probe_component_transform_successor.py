"""★ 真机验证 `SetTransformAndSolve2` → `SetTransformAndSolve3` 与 `AddComponent4` → `AddComponent5`。

★★ 官方依据（三源里的 `C:\\swapi`）：
  · `types/IComponent2/SetTransformAndSolve2.md` ⇒ `SetTransformAndSolve3(Xform, **ThisConfiguration**)`（★ 1 → 2 参）
  · `types/IAssemblyDoc/AddComponent4.md`（5 参）⇒ `AddComponent5`（**8 参**）
  · `types/IModelDoc2/SaveAs3.md` ⇒ `System.int SaveAs3(NewName, SaveAsVersion, Options)` —— ★★ **3 参**
    （★ 上一版我传了 6 个 ⇒ 报"无效的参数数目" ⇒ **那是我探针的错**）✓

★★ 本仓已有：
  · `scripts/sw_assembly._add_component5` —— ★★ **已经写好了 8 参的正确顺序**（★ 直接复用）
  · `scripts/sw_connect.save_document(model, path)` —— ★ 保存帮手

★★★ 判据（★ 跑之前写死）：★ 新旧各能调且**返回值语义一致** ⇒ 可换。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_component_transform_successor.py
# 定位:   ★ 阶段 2：`scripts/sw_assembly.py` 的 `SetTransformAndSolve2`（1 条）与
#   `AddComponent4`（1 条，★ 而它是**刻意兜底**，★ 只作对照）。
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(r"D:\AI\SW")
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402
from scripts.sw_assembly import _add_component4, _add_component5          # noqa: E402

OUT = REPO / "output" / "component-transform-successor-evidence.json"
PART = REPO / "output" / "probe_assy_part2.SLDPRT"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _try(fn, *a):
    try:
        return {"ok": True, "ret": repr(fn(*a))[:90]}
    except Exception as exc:                                              # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:180])}


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        #: ★ ① 造一个零件并**用本仓的 save_document 保存**（★ 不再手拼 SaveAs3 的 6 个参数）
        pdoc = C.new_document(sw, "part")
        P.start_sketch(pdoc, plane_name="Front Plane")
        _g(_g(pdoc, "SketchManager"), "CreateCornerRectangle",
           -0.02, -0.015, 0.0, 0.02, 0.015, 0.0)
        P.end_sketch(pdoc)
        nm = [n for n in (P.feature_names(pdoc) or []) if n.startswith("草图")]
        P.extrude_boss(pdoc, (nm[-1] if nm else "草图1"), 8.0)
        R["保存"] = _try(C.save_document, pdoc, str(PART))
        _g(sw, "CloseDoc", str(_g(pdoc, "GetTitle") or ""))
        R["零件存在"] = PART.exists()

        #: ★ ② 装配
        doc = C.new_document(sw, "assembly")
        R["装配"] = repr(_g(doc, "GetTitle"))[:60]
        comp = None
        if PART.exists():
            #: ★ 新入口优先（★ 与 `add_component` 同序：★ 本仓已写好的 8 参顺序）
            R["新_add_component5"] = _try(_add_component5, doc, str(PART), "", 0.0, 0.0, 0.0)
            comp = None
            try:
                comp = _add_component5(doc, str(PART), "", 0.0, 0.0, 0.0)
            except Exception:                                             # noqa: BLE001
                comp = None
            if comp is None:
                R["旧_add_component4(对照)"] = _try(_add_component4, doc, str(PART), "", 0.0, 0.0, 0.0)
                try:
                    comp = _add_component4(doc, str(PART), "", 0.0, 0.0, 0.0)
                except Exception:                                         # noqa: BLE001
                    comp = None
        R["组件"] = repr(comp)[:80]

        #: ★ ③ 变换（★ 新入口多一个 `ThisConfiguration`）
        if comp is not None:
            xf = None
            try:
                xf = _g(comp, "GetTotalTransform")
            except Exception:                                             # noqa: BLE001
                xf = None
            R["变换对象"] = repr(xf)[:70]
            R["旧_SetTransformAndSolve2(xf)"] = _try(_g, comp, "SetTransformAndSolve2", xf)
            R["新_SetTransformAndSolve3(xf, True)"] = _try(
                _g, comp, "SetTransformAndSolve3", xf, True)
            R["新_SetTransformAndSolve3(xf, False)"] = _try(
                _g, comp, "SetTransformAndSolve3", xf, False)
    except Exception as exc:                                              # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    ok = sorted(k for k, v in R.items() if isinstance(v, dict) and v.get("ok") and
                k.startswith(("新_", "旧_")))
    R["★_能调的"] = ", ".join(x for x in ok)
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
