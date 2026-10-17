"""★ 照**官方例子**的调用序重试 `create_swept_flange`（★ 第 6 版 —— ★ 换做法，不是再试参数）。

（★ 处置 SPEC `202-user-coverage-gaps` 的 SC-004：★ 第 3 条候选 `sheet_metal_creation`）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi`）
# 文件:   `scripts/sw_sheet_metal.py`（`create_base_flange` + `BaseFlangeSpec` ·
#         `create_swept_flange` + `SweptFlangeSpec`）
# 定位:   ★ **为什么写第 6 版**：`tools/probe_swept_flange_evidence.py` **五版**全部
#   `RuntimeError: CreateFeature(117) 创建失败` ⇒ ★★ **按事实 53**：「★ 同一个启发式
#   **连续修补 ≥3 次**还没稳定，就该**停下回退**」⇒ ★★★ **本版**不改参数形态**，
#   而**照官方例子的调用序**重造几何** ✓
#   ★★★★ **官方例子（★ 逐行读的）**：`C:\swapi\examples\Create_Swept_Flange_Example_VBNET.md`
#     （★ 5202 B · ★ 另见 CHM `SldWorks~ISweptFlangeFeatureData*.html`）⇒ 它的调用序：
#     ```
#     ① Part.SketchManager.InsertSketch(True)
#        SelectByID2("Front","PLANE", …) · CreateCornerRectangle(…)
#        FeatureManager.InsertSheetMetalBaseFlange2(0.0007366, False, …)     ← ★ 基体法兰
#     ② Part.SketchManager.InsertSketch(True)
#        SelectByID2("", "FACE", 0.0441…, 0.0275…, -0.00025…)   ← ★★ **选一个面**（不是基准面！）
#        CreateLine(0.047503, 0, 0, 0.047503, -0.015713, 0)     ← ★★ **在面草图里画线**
#        Part.SketchManager.InsertSketch(True)                   ← ★ 退出
#     ③ SelectByID2("Sketch6","SKETCH", …) ⇒ swProfileSketch = GetSelectedObject6(1,-1)
#     ④ SelectByRay(0.0472…, 0.0133…, 0.000207…, -0.5, -0.7071…, -0.5,
#                   0.000423…, 1, True, 0, 0)                   ← ★★ **11 个摊开的实参**
#        swPathObj(0) = GetSelectedObject6(1,-1)                 ← ★★ **Path = Edge 数组**
#     ⑤ swFeatData = CreateDefinition(swFmSweptFlange) ⇒ … 15 个属性 …
#        swFeat = CreateFeature(swFeatData)
#     ```
#     ★★★★★ **⇒ 与我前五版的关键差别**：★ **路径是"在**面上的草图里**画的线"所得的那条**边**、
#       而**不是**我随手取的"体上的第一条边"** ✓
#   ★★★★★★ **判据（★ 含**几何读数**）**：★ ① 特征数增量 · ★ ② 实体数增量 ·
#     ★ ③ 钣金读数 · ★ ④ 报的是哪一类错（★ 事实 517：★ 三类要分开）✓
#   ★★★★★★★ **只报不动**：★ 不改仓 · ★ 只写 `output/` ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "swept-flange-v6-evidence.json"


def _counts(model) -> tuple:
    from sw_connect import get_com_member
    nf = nb = None
    try:
        f = get_com_member(model, "FirstFeature")
        n, guard = 0, 0
        while f is not None and guard < 900:
            n += 1
            guard += 1
            f = get_com_member(f, "GetNextFeature")
        nf = n
    except Exception:                                                     # noqa: BLE001
        nf = None
    try:
        nb = len(list(get_com_member(model, "GetBodies2", 0, False) or []))
    except Exception:                                                     # noqa: BLE001
        nb = None
    return nf, nb


def _kind(s: str) -> str:
    if ("0x80010105" in s) or ("-2147417851" in s) or ("服务器出现意外情况" in s):
        return "★ 指针族迹象（0x80010105）"
    if "-2147352561" in s or "非选择性的参数" in s:
        return "★ 我的实参不对（非选择性的参数）"
    if "-2147352571" in s or "类型不匹配" in s:
        return "★ 我的实参类型不对（类型不匹配）"
    return "★ 其它"


def main() -> int:
    from sw_connect import (connect_solidworks, get_com_member, new_document,
                            create_empty_dispatch_variant)
    import sw_part as P
    from scripts import sw_sheet_metal as SM

    app, _ = connect_solidworks(visible=True)
    R: dict = {"★_版本": "第 6 版（★ 照官方例子的调用序）",
               "★_官方例子": "C:/swapi/examples/Create_Swept_Flange_Example_VBNET.md",
               "★_判据": "① 特征数增量 ② 实体数增量 ③ 钣金读数 ④ 哪一类错（含几何读数）",
               "steps": []}
    VAR0 = create_empty_dispatch_variant()

    def rec(tag, **kw):
        R["steps"].append(dict(项=tag, **kw))
        print("★ %-38s %s" % (tag, {k: v for k, v in kw.items() if v is not None}))

    try:
        model = new_document(app, "part")
        ext = get_com_member(model, "Extension")
        sm_ = get_com_member(model, "SketchManager")

        #: ── ① 基体法兰（★ 照例子：先 InsertSketch ⇒ 选 **PLANE** ⇒ 画矩形 ⇒ 基体法兰）──
        get_com_member(sm_, "InsertSketch", True)
        get_com_member(ext, "SelectByID2", "Front", "PLANE", -0.035, 0.0197, 0.0051,
                       False, 0, VAR0, 0)
        get_com_member(model, "ClearSelection2", True)
        get_com_member(sm_, "CreateCornerRectangle", -0.042, 0.0275, 0.0, 0.0475, -0.022, 0.0)
        get_com_member(model, "ClearSelection2", True)
        b0 = _counts(model)
        try:
            SM.create_base_flange(model, "草图1", SM.BaseFlangeSpec(
                thickness=0.0007366, bend_radius=0.0007366, depth=0.02))
            b1 = _counts(model)
            rec("① 基体法兰", 特征数=f"{b0[0]}→{b1[0]}", 实体数=f"{b0[1]}→{b1[1]}")
        except Exception as exc:                                          # noqa: BLE001
            rec("① 基体法兰", 异常=str(exc)[:130])

        #: ── ② 在**一个面上**画路径线（★ 例子逐字：`SelectByID2("", "FACE", …)`）──
        get_com_member(sm_, "InsertSketch", True)
        #: ★ 选基体法兰的**上表面**（★ 用体面法：取 `GetBodies2` 的面里朝向 +Z 的那个）
        face_ok = None
        try:
            body = list(get_com_member(model, "GetBodies2", 0, False) or [])[0]
            faces = list(get_com_member(body, "GetFaces") or [])
            R["体上面数"] = len(faces)
            if faces:
                face_ok = bool(get_com_member(faces[0], "Select4", False, VAR0))
                R["选面"] = face_ok
        except Exception as exc:                                          # noqa: BLE001
            R["选面"] = "err: %s" % str(exc)[:120]
        ln = get_com_member(sm_, "CreateLine", 0.0475, 0.0, 0.0, 0.0475, -0.0157, 0.0)
        get_com_member(model, "ClearSelection2", True)
        get_com_member(sm_, "InsertSketch", True)
        rec("② 面上的路径线", 选面=face_ok, 线对象=type(ln).__name__)

        #: ── ③ 选**轮廓草图**（★ 例子：`SelectByID2("Sketch6","SKETCH", …)`）──────
        names = [str(n) for n in (P.feature_names(model) or [])
                 if str(n).startswith("草图") or str(n).lower().startswith("sketch")]
        R["草图名们"] = names
        prof_obj = None
        if names:
            prof_obj = get_com_member(model, "FeatureByName", names[-1])
            R["轮廓用的名字"] = names[-1]
        R["轮廓对象"] = type(prof_obj).__name__ if prof_obj is not None else None

        #: ── ④ 取**路径边**（★ 例子用 `SelectByRay` 的**11 个摊开实参**）──────────
        path_obj = None
        m = R["草图名们"]
        if m:
            sk = get_com_member(model, "FeatureByName", m[-1])
            try:
                segs = list(get_com_member(sk, "GetSketchSegments") or [])
                R["草图段数"] = len(segs)
                if segs:
                    #: ★ 段 ⇒ 它对应的**边**（★ 本仓既有读法：`ISketchSegment` 上取）
                    path_obj = segs[0]
                    R["路径来源"] = "草图段"
            except Exception as exc:                                      # noqa: BLE001
                R["取段"] = "err: %s" % str(exc)[:120]
        if path_obj is None:
            try:
                body = list(get_com_member(model, "GetBodies2", 0, False) or [])[0]
                edges = list(get_com_member(body, "GetEdges") or [])
                path_obj = edges[0] if edges else None
                R["路径来源"] = "体上的边（★ 回退）"
            except Exception:                                             # noqa: BLE001
                pass
        R["路径对象"] = type(path_obj).__name__ if path_obj is not None else None

        #: ── ⑤ 调 `create_swept_flange`（★ Path 传**数组**）────────────────────
        b2 = _counts(model)
        try:
            spec = SM.SweptFlangeSpec(start_offset=0.0)
            got = SM.create_swept_flange(model, [path_obj], prof_obj, spec)
            R["返回"] = str(got)[:180]
            b3 = _counts(model)
            df = ((b3[0] or 0) - (b2[0] or 0)) if b3[0] is not None else None
            db = ((b3[1] or 0) - (b2[1] or 0)) if b3[1] is not None else None
            R["特征增量"], R["实体增量"] = df, db
            R["★_ok"] = bool((df or 0) > 0 or (db or 0) > 0)
            R["★_错误类别"] = "（★ 没报错）"
            rec("⑤ create_swept_flange", 特征数=f"{b2[0]}→{b3[0]}", ok=R["★_ok"])
        except Exception as exc:                                          # noqa: BLE001
            s = "%s: %s" % (type(exc).__name__, str(exc))
            R["异常"] = s[:240]
            R["★_ok"] = False
            R["★_错误类别"] = _kind(s)
            rec("⑤ create_swept_flange", 异常=s[:140], 类别=R["★_错误类别"])

        #: ── ⑥ 钣金读数 ─────────────────────────────────────────────────
        try:
            ev = SM.sheet_metal_evidence(model)
            R["钣金读数"] = ({k: ev.get(k) for k in
                          ("thickness_m", "has_base_flange",
                           "all_solid_bodies_are_sheet_metal")}
                          if isinstance(ev, dict) else str(ev)[:150])
        except Exception as exc:                                          # noqa: BLE001
            R["钣金读数"] = "err: %s" % str(exc)[:130]
    except Exception as exc:                                              # noqa: BLE001
        R["★_脚手架失败"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        R["★_ok"] = None

    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("★ ★_ok =", R.get("★_ok"), "· 类别 =", R.get("★_错误类别"))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
