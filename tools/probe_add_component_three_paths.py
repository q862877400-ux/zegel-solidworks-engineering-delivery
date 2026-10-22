"""★ 真机验证：用**本仓自己那条三步路**（`sw_assembly.add_component`）能不能建成组件。

★★ 为什么单独探：★ 上一版发现 `_add_component5` 与 `_add_component4` **都能调但都返回 `None`**
  ⇒ ★ 组件没建成 ⇒ **`SetTransformAndSolve3` 没有对象可验** ✓
★★ 而本仓 `scripts/sw_assembly.add_component` **自己就有第三条路**（★ 源码逐字）：
  ```
  component = _add_component5(...)                  # ① 优先新的
  if component is None: component = _add_component4(...)   # ② 退回旧的
  if component is None:                             # ③ 打开零件 → 激活装配 → 再试 5
      opened = open_document(sw, component_path, read_only=False, silent=True)
      elif _activate_model_document(sw, asm_model):
          component = _add_component5(...)
  ```
★★★ 判据（★ 跑之前写死）：★ `add_component` 返回**非 None** ⇒ 组件建成 ⇒ 才能验 `SetTransformAndSolve3`。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_add_component_three_paths.py
# 定位:   ★ 阶段 2 的前置打通：★ 本仓 `sw_assembly.add_component` 的三条路哪条真能建成
#           组件。
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
for _p in (str(REPO), str(REPO / "scripts"), str(REPO / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from scripts import sw_connect as C  # noqa: E402
from scripts import sw_part as P  # noqa: E402
from scripts.sw_assembly import add_component, get_components  # noqa: E402

OUT = REPO / "output" / "add-component-three-paths-evidence.json"
PART = REPO / "output" / "probe_assy_part3.SLDPRT"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _try(fn, *a, **kw):
    try:
        return {"ok": True, "ret": repr(fn(*a, **kw))[:100]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:200])}


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        #: ★ 造零件
        pdoc = C.new_document(sw, "part")
        P.start_sketch(pdoc, plane_name="Front Plane")
        _g(
            _g(pdoc, "SketchManager"),
            "CreateCornerRectangle",
            -0.02,
            -0.015,
            0.0,
            0.02,
            0.015,
            0.0,
        )
        P.end_sketch(pdoc)
        nm = [n for n in (P.feature_names(pdoc) or []) if n.startswith("草图")]
        P.extrude_boss(pdoc, (nm[-1] if nm else "草图1"), 8.0)
        R["保存"] = _try(C.save_document, pdoc, str(PART))
        _g(sw, "CloseDoc", str(_g(pdoc, "GetTitle") or ""))
        R["零件存在"] = PART.exists()

        doc = C.new_document(sw, "assembly")
        R["装配"] = repr(_g(doc, "GetTitle"))[:60]
        #: ★★ 走本仓自己的三步路（★ `sw` 也传进去，★ 让第 ③ 条路可用）
        R["add_component(走本仓三步路)"] = _try(
            add_component, doc, str(PART), 0.0, 0.0, 0.0, "", sw
        )
        comp = None
        try:
            comp = add_component(doc, str(PART), 0.0, 0.0, 0.0, "", sw)
        except Exception:  # noqa: BLE001
            comp = None
        R["组件"] = repr(comp)[:90]
        R["get_components"] = _try(get_components, doc)

        #: ★★ 组件建成 ⇒ **才**验 `SetTransformAndSolve3`
        if comp is not None:
            #: ★★★ 2026-10-03 修：★ 官方 `IComponent2.GetTotalTransform` 是 **1 参**
            #:   （`GetTotalTransform(System.bool IncludePresentationXform)`）——
            #: ★★ 我上一版**无参调它** ⇒ `get_com_member` 的"取或调"试了 0 参调用、**失
            #: 败**
            #:   ⇒ ★★★ **回了 `bound method`** ⇒ 报 `Objects of type 'method' can not be
            #:   converted to a COM VARIANT` ✓
            #: ★ 本仓注册表里也写着 `'GetTotalTransform': 1`（★ 与官方一致）⇒ **是我探针
            #: 的错** ✓
            xf, xf2 = None, None
            try:
                xf = _g(comp, "GetTotalTransform", True)
            except Exception:  # noqa: BLE001
                xf = None
            #: ★ 备选：`IComponent2.Transform2` 是**真属性**（0 参，`{get; set;}`）
            try:
                xf2 = _g(comp, "Transform2")
            except Exception:  # noqa: BLE001
                xf2 = None
            R["变换对象(GetTotalTransform(True))"] = repr(xf)[:70]
            R["变换对象(Transform2 属性)"] = repr(xf2)[:70]
            if xf is None or "method" in repr(xf):
                xf = xf2
            R["旧_SetTransformAndSolve2(xf)"] = _try(
                _g, comp, "SetTransformAndSolve2", xf
            )
            R["新_SetTransformAndSolve3(xf, True)"] = _try(
                _g, comp, "SetTransformAndSolve3", xf, True
            )
            R["新_SetTransformAndSolve3(xf, False)"] = _try(
                _g, comp, "SetTransformAndSolve3", xf, False
            )
    except Exception as exc:  # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:  # noqa: BLE001
            pass
    R["★_组件建成了吗"] = (
        "★ 是（可验变换）"
        if R.get("组件", "None") not in ("None", "")
        else "★★ 否（变换仍验不了 —— 如实记）"
    )
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
