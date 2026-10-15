"""★ 分辨性实验：`IBody2.GetBodyBox` / 能力层包装 / MCP 工具，三层各返回什么单位。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   probe_bbox_unit_levels.py
# 定位:   ★★★ 本轮复盘的核心事实，必须**实验判决**而不是推理：
#           · `scripts/sw_part.get_bounding_box` 的 docstring 逐字断言
#             「`GetBodyBox` 原始返回 `[0,0,-50,80,60,0]` ⇒ **原始值就是 80/60/50（毫米）**」✓
#           · `mcp-server` 的 `solidworks_part_bounding_box.doc` 逐字断言
#             「Units are **MILLIMETRES**（measured: 80×60×50 的盒子返回 80/60/50）」✓
#           · ★★ 而我本轮用**工具**量 40×40×10 的盒子，拿到的是 **0.04**（= 米）✓✗
#         ⇒ ★ 两者互斥 ⇒ 本探针把**三层分别量一遍**，用**同一个已知尺寸的盒子**：
#             ① 原始 `IBody2.GetBodyBox()`
#             ② 能力层 `sw_part.get_bounding_box(doc)`
#             ③ 参考：`GetPartBox(True)`（我探针里用的那个）与质量属性体积
#         ★★ 判据：40×40×10 的盒子，若某层回 **40/40/10** ⇒ 该层是**毫米**；
#           回 **0.04/0.04/0.01** ⇒ 该层是**米**。★ 体积 1.6e-5 与之互证（1.6e-5 m³ = 16000 mm³）✓
# 单位口径: 本探针**不假定任何单位**，只报原始数 —— 这正是本轮该做而没先做的事 ✓
# 官方依据: `IBody2/GetBodyBox.md` · `IModelDoc2/GetPartBox.md`（★ 两者是**不同成员**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# -------------------------------------------------------------------------
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import sw_part  # noqa: E402
from sw_connect import connect_solidworks, get_com_member, mm, new_document  # noqa: E402

OUT = ROOT / "output"
#: ★ 已知尺寸的参照物：40 × 40 × 10 mm（`create_basic_part` 的 box 语义：宽/高/深）
REF_W, REF_H, REF_D = 40.0, 40.0, 10.0


def build_reference_box(sw, doc):
    """★ 建参照物：40×40×10 的盒子（尺寸是**我们指定的**，不是量出来的）。"""
    ext = get_com_member(doc, "Extension")
    sm = get_com_member(doc, "SketchManager")
    import pythoncom                                                   # noqa: E402
    from win32com.client import VARIANT                                # noqa: E402
    co = VARIANT(pythoncom.VT_DISPATCH, None)
    get_com_member(ext, "SelectByID2", "前视基准面", "PLANE", 0, 0, 0, False, 0, co, 0)
    get_com_member(sm, "InsertSketch", True)
    #: ★ 能力层 `sketch_circle` 吃米，而矩形同理 ⇒ 用 **米** 给（0.02 等）
    sw_part.sketch_corner_rectangle(doc, mm(-REF_W / 2), mm(-REF_H / 2),
                                   mm(REF_W / 2), mm(REF_H / 2))
    get_com_member(sm, "InsertSketch", True)
    sk = ""
    for nm in (str(x) for x in sw_part.feature_names(doc)) if hasattr(sw_part, "feature_names") else []:
        sk = nm
    from sw_feature_readback import feature_names                        # noqa: E402
    for nm in feature_names(doc):
        if "草图" in str(nm) or "Sketch" in str(nm):
            sk = str(nm)
    sw_part.extrude_boss(doc, sk, mm(REF_D))
    return sk


def main() -> int:
    sw = connect_solidworks(visible=True)
    if isinstance(sw, tuple):
        sw = sw[0]
    doc = new_document(sw, "part")
    if doc is None:
        print("★ 新建零件失败")
        return 1
    build_reference_box(sw, doc)
    rep = {"参照物": "%.0f × %.0f × %.0f mm（我们指定的）" % (REF_W, REF_H, REF_D)}

    #: ① 原始 IBody2.GetBodyBox()
    try:
        bodies = get_com_member(doc, "GetBodies2", 0, False)
        body = bodies[0] if bodies else None
        raw = list(get_com_member(body, "GetBodyBox") or [])
        rep["① GetBodyBox 原始"] = raw
        rep["① 判读"] = ("**毫米**" if raw and abs(max(raw) - 40.0) < 1.0
                        else ("**米**" if raw and abs(max(raw) - 0.04) < 0.005 else "两者都不是"))
    except Exception as exc:                                            # noqa: BLE001
        rep["① err"] = "%s: %s" % (type(exc).__name__, str(exc)[:110])

    #: ② 能力层包装
    try:
        cap = sw_part.get_bounding_box(doc)
        rep["② 能力层 get_bounding_box"] = cap
        mx = max(cap["max"]) if cap else None
        rep["② 判读"] = ("**毫米**" if mx and abs(mx - 40.0) < 1.0
                        else ("**米**" if mx and abs(mx - 0.04) < 0.005 else "两者都不是"))
    except Exception as exc:                                            # noqa: BLE001
        rep["② err"] = "%s: %s" % (type(exc).__name__, str(exc)[:110])

    #: ③ 参考：GetPartBox(True)（我探针里用的那个）+ 质量属性体积
    try:
        pb = list(get_com_member(doc, "GetPartBox", True) or [])
        rep["③ GetPartBox(True)"] = [round(v, 6) for v in pb]
        rep["③ 判读"] = ("**毫米**" if pb and abs(max(pb) - 40.0) < 1.0
                        else ("**米**" if pb and abs(max(pb) - 0.04) < 0.005 else "两者都不是"))
    except Exception as exc:                                            # noqa: BLE001
        rep["③ err"] = str(exc)[:110]
    try:
        props = get_com_member(get_com_member(doc, "Extension"), "CreateMassProperty")
        vol = get_com_member(props, "Volume")
        rep["④ 质量属性体积"] = vol
        rep["④ 判读"] = ("**米³**（×1e9 = %.0f mm³ ⇒ 40×40×10 = 16000）" % (vol * 1e9)
                        if vol and abs(vol * 1e9 - 16000) < 200 else "对不上 16000 mm³")
    except Exception as exc:                                            # noqa: BLE001
        rep["④ err"] = str(exc)[:110]

    print(json.dumps(rep, ensure_ascii=False, indent=1))
    (OUT / "bbox-unit-levels-evidence.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
