"""★ 真机验证装配族的**五条后继**（★ 一次跑完，★ 逐条记"能不能调"）。

★★ 官方依据（三源里的 `C:\\swapi`，逐条可复核）：
  · `types/IModelDoc2/EditSuppress.md` 逐字「**Obsolete. Superseded [[IModelDoc2::EditSuppress2]].**」
    ★ 后继 `EditSuppress2()` —— ★★ **1 参（无参）⇒ 与旧的逐字同形 ⇒ 疑似纯改名**
  · `types/IModelDoc2/EditUnsuppress.md` 同上 ⇒ `EditUnsuppress2()`
  · `types/IComponent2/SetTransformAndSolve2.md` ⇒ `SetTransformAndSolve3(Xform, **ThisConfiguration**)`（★ 加 1 参）
  · `types/IAssemblyDoc/AddComponent4.md` ⇒ `AddComponent5(8 参)`（★ 多 3 参）
  · `types/IAssemblyDoc/AddMate5.md` 逐字「**Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]**」
    ⇒ ★★★ 后继 `CreateMate(System.object MateData)` —— ★★ **2 参，形态完全不同** ✓

★★★ 判据（★ 跑之前写死）：★ 每条后继**能调不抛**就记"能调"；★ 不能调就如实记（★ 不硬换）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_assembly_family_successors.py
# 定位:   ★ 阶段 2：`scripts/sw_assembly.py` 的装配族 6 条
#   （EditSuppress · EditUnsuppress · SetTransformAndSolve2 · AddComponent4 · AddMate5）。
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

OUT = REPO / "output" / "assembly-family-successor-evidence.json"


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
        #: ★ 装配文档（★ 装配族的前置）
        doc = C.new_document(sw, "assembly")
        R["装配文档"] = repr(_g(doc, "GetTitle"))[:80] if doc is not None else "None"

        #: ★ 先放一个零件进去（★ 否则 suppress / 变换都没对象）
        try:
            part = Path(r"D:\AI\SW\output\probe_assy_part.SLDPRT")
            pdoc = C.new_document(sw, "part")
            P.start_sketch(pdoc, plane_name="Front Plane")
            _g(_g(pdoc, "SketchManager"), "CreateCornerRectangle",
               -0.02, -0.015, 0.0, 0.02, 0.015, 0.0)
            P.end_sketch(pdoc)
            nm = [n for n in (P.feature_names(pdoc) or []) if n.startswith("草图")]
            P.extrude_boss(pdoc, (nm[-1] if nm else "草图1"), 8.0)
            _g(pdoc, "SaveAs3", str(part), 0, 1, None, None)
            _g(sw, "CloseDoc", str(_g(pdoc, "GetTitle") or ""))
            R["造零件"] = str(part.exists())
        except Exception as exc:                                          # noqa: BLE001
            R["造零件出错"] = "%s: %s" % (type(exc).__name__, str(exc)[:130])
            part = None

        #: ★★★ 旧入口（★ 基线）
        R["旧_EditSuppress"] = _try(_g, doc, "EditSuppress")
        R["旧_EditUnsuppress"] = _try(_g, doc, "EditUnsuppress")
        #: ★★★ 新入口
        R["新_EditSuppress2"] = _try(_g, doc, "EditSuppress2")
        R["新_EditUnsuppress2"] = _try(_g, doc, "EditUnsuppress2")

        #: ★ 组件（★ 给 SetTransformAndSolve* 用）
        if part is not None and part.exists():
            R["旧_AddComponent4"] = _try(_g, doc, "AddComponent4",
                                        str(part), "", 0.0, 0.0, 0.0)
            R["新_AddComponent5"] = _try(_g, doc, "AddComponent5",
                                        str(part), 0, "", True, 0.0, 0.0, 0.0, True)
            comp = None
            try:
                comp = _g(doc, "GetActiveComponent")
                if comp is None:
                    m = _g(doc, "GetComponents", False)
                    comp = m[0] if isinstance(m, (list, tuple)) and m else None
            except Exception:                                             # noqa: BLE001
                comp = None
            R["组件"] = repr(comp)[:80]
            if comp is not None:
                xf = _try(_g, comp, "GetTotalTransform") if False else None
                R["旧_SetTransformAndSolve2"] = _try(_g, comp, "SetTransformAndSolve2", None)
                R["新_SetTransformAndSolve3"] = _try(_g, comp, "SetTransformAndSolve3", None, True)

        #: ★★ `AddMate5` 的后继是**换范式**：★ 先 `CreateMateData(MateType)`
        R["CreateMateData"] = _try(_g, doc, "CreateMateData", 0)
        md = None
        try:
            md = _g(doc, "CreateMateData", 0)
        except Exception:                                                 # noqa: BLE001
            md = None
        R["MateData 对象"] = repr(md)[:80]
        R["新_CreateMate"] = _try(_g, doc, "CreateMate", md)
        R["旧_AddMate5_仅试arity"] = _try(_g, doc, "AddMate5")
    except Exception as exc:                                              # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    new_ok = sorted(k for k, v in R.items()
                    if k.startswith("新_") and isinstance(v, dict) and v.get("ok"))
    R["★_新入口能调的"] = "%d 条: %s" % (len(new_ok), ", ".join(x[2:] for x in new_ok))
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
