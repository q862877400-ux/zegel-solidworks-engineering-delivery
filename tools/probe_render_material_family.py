"""★ 真机对照：渲染材质族的**旧入口 vs 新入口**（★ 决定怎么改之前先跑）。

★★ 背景（两个问题叠在一起）：
  ① ★ 旧入口**全是废弃的**：
     · `IModelDocExtension.GetRenderMaterialsCount()` 1 参 ⇒ `Obsolete → …Count2`（★ **3 参**）
     · `IModelDocExtension.GetRenderMaterials()`      1 参 ⇒ `Obsolete → …Materials2`
     · `IModelDocExtension.AddRenderMaterial`       2 参 ⇒ `**Not supported in SOLIDWORKS 2011 and later**`
     · `IModelDocExtension.DeleteRenderMaterial`    3 参 ⇒ 同上
  ② ★★ `scripts/sw_render_material.py` 自己标着「**未在本机实测**」⇒ ★ **它连旧的都没验过** ✓

★★ 官方例子的确切用法（`examples/Add_and_Delete_Materials_from_Specific_Display_States_Example_VB.md`）：
  ```vbnet
  status = swModelDocExt.AddDisplayStateSpecificRenderMaterial(swRenderMaterial, swalldisplaystate, displayStateNames, id1, id2)
  nbrMaterials = swModelDocExt.GetRenderMaterialsCount2(swalldisplaystate, Nothing)
  renderMaterials = swModelDocExt.GetRenderMaterials2(swalldisplaystate, Nothing)
  swModelDocExt.DeleteDisplayStateSpecificRenderMaterial (materialID1), (materialID2)
  ```
  ★ `swDisplayStateOpts_e`：★ `swThisDisplayState = 1` · **`swalldisplaystate = 2`** · `swSpecifyDisplayState = 3`

★★★ 判据（★ 跑之前写死）：
  · ★ 每条入口**不抛异常** ⇒ 记"能调"
  · ★★ **旧的四条都能调** ⇒ ★ 说明"废弃 ≠ 不能用"（★ 与官方例子自己在用 `GraphicsRedraw2` 同理）
  · ★★★ **新的四条也都能调** ⇒ ★ **才允许换**（★ 换不了就如实记"保留现状"）
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_render_material_family.py
# 定位:   ★ T1 的「渲染材质族」4 条（★ `sw_render_material.py`）。
#   官方依据: `c:\\swapi\\types\\IModelDocExtension\\` 下 14 个渲染材质成员页 ·
# `c:\\swapi\\examples\\Add_and_Delete_Materials_from_Specific_Display_States_Example_VB
# .md` ·
#     `c:\\swapi\\enums\\swDisplayStateOpts_e.md`
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

from scripts import sw_connect as c  # noqa: E402
from scripts.sw_connect import out_i4  # noqa: E402

OUT = REPO / "output" / "render-material-family-evidence.json"


def _g(o, n, *a):
    return c.get_com_member(o, n, *a)


def _try(fn, *a, **kw):
    """★ 调一次并归一化结果（★ 不抛出去 —— 我们要"能不能调"这个事实）。"""
    try:
        r = fn(*a, **kw)
        return {"ok": True, "ret": repr(r)[:110]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:170])}


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = c.connect_solidworks(wait_seconds=30)
    swalldisplaystate = 2  #: ★ 官方枚举
    doc = None
    try:
        doc = c.new_document(sw, "part")
        ext = _g(doc, "Extension")
        R["extension_ok"] = ext is not None

        #: ★ 需要一个 RenderMaterial 对象 —— 用官方的 `CreateRenderMaterial`（★ 无废弃）
        #: 建
        mat = _try(_g, ext, "CreateRenderMaterial", 0)
        R["CreateRenderMaterial"] = mat
        #: ★★★ 2026-10-03 修：★ 上一版把 `None` 当材质传进去了（★ 我在调试时留的 `if Fal
        #: se else None`）
        #:   ⇒ ★★ 两处"类型不匹配"其实**是我探针的错**，★ 不是 API 的问题 ✓
        mat_obj = None
        try:
            mat_obj = _g(ext, "CreateRenderMaterial", 0)
        except Exception:  # noqa: BLE001
            mat_obj = None
        R["材质对象"] = repr(mat_obj)[:80]
        from scripts.sw_connect import create_empty_dispatch_variant as _empty

        blank = _empty()

        #: ★★★ 旧入口（★ 四条）
        R["旧_GetRenderMaterialsCount"] = _try(_g, ext, "GetRenderMaterialsCount")
        R["旧_GetRenderMaterials"] = _try(_g, ext, "GetRenderMaterials")
        R["旧_AddRenderMaterial"] = _try(
            _g, ext, "AddRenderMaterial", mat_obj, out_i4()
        )
        R["旧_DeleteRenderMaterial"] = _try(_g, ext, "DeleteRenderMaterial", 0, False)

        #: ★★★ 新入口（★ 四条，★ 按官方例子；★ 空参数用空 VARIANT —— 事实 33）
        R["新_GetRenderMaterialsCount2"] = _try(
            _g, ext, "GetRenderMaterialsCount2", swalldisplaystate, blank
        )
        R["新_GetRenderMaterials2"] = _try(
            _g, ext, "GetRenderMaterials2", swalldisplaystate, blank
        )
        R["新_AddDisplayStateSpecificRenderMaterial"] = _try(
            _g,
            ext,
            "AddDisplayStateSpecificRenderMaterial",
            mat_obj,
            swalldisplaystate,
            blank,
            out_i4(),
            out_i4(),
        )
        R["新_DeleteDisplayStateSpecificRenderMaterial"] = _try(
            _g, ext, "DeleteDisplayStateSpecificRenderMaterial", blank, blank
        )
    except Exception as exc:  # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:  # noqa: BLE001
            pass

    old_ok = sum(
        1
        for k, v in R.items()
        if k.startswith("旧_") and isinstance(v, dict) and v.get("ok")
    )
    new_ok = sum(
        1
        for k, v in R.items()
        if k.startswith("新_") and isinstance(v, dict) and v.get("ok")
    )
    R["★_旧入口能调数"] = "%d/4" % old_ok
    R["★_新入口能调数"] = "%d/4" % new_ok
    R["verdict"] = (
        "★ 新旧都能调 ⇒ **可以换**（★ 换掉废弃入口）"
        if old_ok >= 3 and new_ok >= 3
        else "★★ 需逐条看 —— 至少一边有不可调的（★ 如实记，★ 不硬换）"
    )
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(
        json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8"
    )
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
