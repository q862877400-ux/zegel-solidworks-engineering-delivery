"""★ 决定性对照：`AddMate5` 与后继 `CreateMate(MateData)` **谁真能建成 mate**。

★★ 为什么必须先判"该不该换"（★ 而不是直接换）：
  ★ `IAssemblyDoc.AddMate5.md` 逐字「**Obsolete. Superseded by [[IAssemblyDoc::CreateMate.]]**」
    ⇒ ★ 但它**只是"废弃"**，★ 而**本会话已多次见到"废弃的真能用"**
      （★ 例：官方例子自己在 40+ 处用 `GraphicsRedraw2`；★ `AddRenderMaterial` 真机回 True）✓
  ★★ 而后继 `CreateMate(System.object MateData)` 的形态**完全不同** ——
    ★ 旧的 15 个散参数 ⇒ 新的**一个 `MateData` 对象**（★ 由 `CreateMateData(MateType)` 建）
    ⇒ ★★ **映射不是平凡替换**（★ 15 个标量怎么进那个对象，★ 官方没给一对一表）✓
  ★★★ 且我已验的只是「`CreateMateData(0)` 与 `CreateMate(md)` **能调**」
    ⇒ ★★★ **"能调" ≠ "建成了 mate"**（★ 事实 40 的教训：`IModeler.Create*Surface` 也"能调"却回 None）✓

★★★ 判据（★ 跑之前写死）：
  ① ★ 先建一个**含两个组件**的装配（★ 两平面可对齐 ⇒ 真的能成 mate）
  ② ★ **选两个面**（★ 用本仓的声明式选择器）
  ③ ★★ 调旧 `AddMate5(0=重合, …)` ⇒ 记「回什么 + 装配的 mate 数变化」
  ④ ★★ 调新 `CreateMateData(0)` + `CreateMate(md)` ⇒ 同样记
  ⑤ ★★★ **判据**：★ **mate 数 +1 的那一条才算"真建成"** ✓
    ★ 只回对象而 mate 数不变 ⇒ ★ **不算建成**（★ 事实 40/本会话多次）
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验证）。
# 文件:   tools/probe_mate5_vs_createmate.py
# 定位:   ★ 阶段 2：`scripts/sw_assembly.py` 的 `AddMate5`（★ 2 条）——
#   ★ 先判**该不该换**，★ 再决定改不改。
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

import pythoncom                                                        # noqa: E402
from win32com.client import VARIANT                                     # noqa: E402

from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402
from scripts.sw_assembly import add_component, get_components             # noqa: E402

OUT = REPO / "output" / "mate5-vs-createmate-evidence.json"
PART = REPO / "output" / "probe_mate_part.SLDPRT"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _try(fn, *a):
    try:
        return {"ok": True, "ret": repr(fn(*a))[:90]}
    except Exception as exc:                                              # noqa: BLE001
        return {"ok": False, "err": "%s: %s" % (type(exc).__name__, str(exc)[:200])}


def _mate_count(doc) -> int:
    """★ 装配里 Mate 特征的个数（★ 这才是"真建成"的判据）。"""
    n, feat = 0, None
    try:
        feat = _g(doc, "FirstFeature")
        while feat is not None:
            try:
                tn = str(_g(feat, "GetTypeName2") or "")
                if tn in ("MateGroup", "Mate") or "Mate" in tn or "配合" in tn:
                    n += 1
            except Exception:                                             # noqa: BLE001
                pass
            feat = _g(feat, "GetNextFeature")
    except Exception:                                                     # noqa: BLE001
        pass
    return n


def main() -> int:
    started = time.time()
    R: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S")}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    doc = None
    try:
        #: ① 造零件
        pdoc = C.new_document(sw, "part")
        P.start_sketch(pdoc, plane_name="Front Plane")
        _g(_g(pdoc, "SketchManager"), "CreateCornerRectangle",
           -0.03, -0.02, 0.0, 0.03, 0.02, 0.0)
        P.end_sketch(pdoc)
        nm = [n for n in (P.feature_names(pdoc) or []) if n.startswith("草图")]
        P.extrude_boss(pdoc, (nm[-1] if nm else "草图1"), 10.0)
        R["保存"] = _try(C.save_document, pdoc, str(PART))
        _g(sw, "CloseDoc", str(_g(pdoc, "GetTitle") or ""))

        #: ② 装配 + **两个**组件
        doc = C.new_document(sw, "assembly")
        c1 = _try(add_component, doc, str(PART), 0.0, 0.0, 0.0, "", sw)
        c2 = _try(add_component, doc, str(PART), 0.1, 0.0, 0.0, "", sw)
        R["加组件1"] = c1
        R["加组件2"] = c2
        comps = get_components(doc)
        R["组件数"] = len(comps) if isinstance(comps, (list, tuple)) else repr(comps)[:60]
        R["★_mate数_基线"] = _mate_count(doc)

        #: ③ 选两个面（★ 用声明式选择器 —— 规则 3）
        R["选面"] = _try(_g, doc, "ClearSelection2", True)
        n_sel = 0
        try:
            from sw_selection_spec import resolve_selection
            for spec in ("index:0", "index:0"):
                try:
                    resolve_selection(doc, spec, "FACE", append=True)
                    n_sel += 1
                except Exception:                                         # noqa: BLE001
                    pass
        except Exception as exc:                                          # noqa: BLE001
            R["选择器出错"] = str(exc)[:130]
        try:
            R["回读选中数"] = int(_g(_g(doc, "SelectionManager"),
                                     "GetSelectedObjectCount2", -1) or 0)
        except Exception:                                                 # noqa: BLE001
            R["回读选中数"] = -1

        #: ④ 旧入口 `AddMate5`（★ 15 参；★ 0 = swMateCOINCIDENT；★ 0 = swAlignNONE）
        err = VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)
        before = _mate_count(doc)
        R["旧_AddMate5"] = _try(_g, doc, "AddMate5",
                                0, 0, False, 0.0, 0.0, 0.0, 0.0, 0.0,
                                0.0, 0.0, 0.0, False, False, 0, err)
        R["旧_AddMate5_error_status"] = int(err.value) if hasattr(err, "value") else "?"
        after_old = _mate_count(doc)
        R["★_mate数_旧入口后"] = after_old
        R["★_旧入口建成"] = "★ 是（mate 数 +%d）" % (after_old - before) if after_old > before \
            else "★★ 否（mate 数没变）"

        #: ⑤ 新入口 `CreateMateData` + `CreateMate`
        try:
            _g(doc, "ClearSelection2", True)
        except Exception:                                                 # noqa: BLE001
            pass
        before2 = _mate_count(doc)
        R["新_CreateMateData(0)"] = _try(_g, doc, "CreateMateData", 0)
        md = None
        try:
            md = _g(doc, "CreateMateData", 0)
            R["MateData 对象"] = repr(md)[:80]
        except Exception:                                                 # noqa: BLE001
            md = None
        if md is not None:
            #: ★ `IMateFeatureData` / `IMate2` 的常见字段（★ 名字照官方页，★ 不猜语义）
            for field, val in (("MateAlignment", 0), ("Flip", False),
                               ("Distance", 0.0), ("ErrorStatus", 0)):
                R["新_设_%s" % field] = _try(C.set_com_member, md, field, val)
        R["新_CreateMate(md)"] = _try(_g, doc, "CreateMate", md)
        after_new = _mate_count(doc)
        R["★_mate数_新入口后"] = after_new
        R["★_新入口建成"] = "★ 是（mate 数 +%d）" % (after_new - before2) if after_new > before2 \
            else "★★ 否（mate 数没变）"
    except Exception as exc:                                              # noqa: BLE001
        R["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
    finally:
        try:
            if doc is not None:
                _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
        except Exception:                                                 # noqa: BLE001
            pass
    R["★★_结论"] = ("★ 旧入口能建成 ⇒ **没有换的必要**（废弃 ≠ 不能用）"
                    if str(R.get("★_旧入口建成", "")).startswith("★ 是")
                    else "★★ 旧入口建不成 ⇒ 值得试新入口")
    R["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
