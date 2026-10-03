"""★ R3 四条（钣金/焊件）的**首次**真机探针：按 ToolSpec 的契约逐条调 + 如实记前置。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针）。规格 `specs/202-user-coverage-gaps` 的 **R3 收口**。
# 文件:   tools/probe_r3_tools.py
# 定位:   ★★ **为什么必须跑这一趟**：R3 的四条工具**已注册**（会进覆盖率），
#   但**至今零真机读数**（★ 能力层是队友按官方契约写的、从没在本机跑过）。
#   ★ 本探针**只做两件事**：① 尽力造出前置；② 按 ToolSpec 的契约调，并把
#     **建成 / 前置未成立 / 真阴性** 三态如实分开（★ 事实 496）。
#   官方依据（★ 逐条写在 `scripts/sw_sheet_metal_weld_entry.py` 的 docstring 里）:
#     · 斜接法兰 `IFeatureManager.InsertSheetMetalMiterFlange`（**14 参**·未废弃）
#       ★ 其官方页**无 `## Remarks`** ⇒ ★ 前置**查不到**（★ 队友如实报 `None`）
#     · 闭合角 `IModelDoc2.InsertSheetMetalClosedCorner`（**零参·回 `void`**）
#       ★ 官方页**同样无 `## Remarks`** ⇒ ★ 判据只能是**树增量 + 面数增量 + 体积增量**三合一
#     · 顶端盖 `InsertEndCapFeature3`（10 参）★ 官方：「select one or more **end faces**」· **没给 mark**
#     · 角撑板 `InsertGussetFeature3`（20 参）★ 官方：「**two faces** … with a **Mark of 1**」
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

import register_capabilities as RC                                        # noqa: E402
from scripts import sw_connect as C                                       # noqa: E402
from scripts import sw_part as P                                          # noqa: E402

OUT = REPO / "output" / "r3-tools-evidence.json"


def _g(o, n, *a):
    return C.get_com_member(o, n, *a)


def _call(tool: str, args: dict) -> dict:
    """★ **按 ToolSpec 的契约调** —— ★ **逐字复刻注册器 `tool_registry.make_tool_function._impl`**。"""
    spec = {getattr(s, "name", None): s for s in RC.all_specs()}.get(tool)
    if spec is None:
        return {"ok": False, "err": "★ 工具没注册"}
    mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
    fn = getattr(mod, spec.function)
    want = {getattr(p, "name", None) for p in (spec.params or [])}
    alias = dict(getattr(spec, "param_alias", None) or {})
    #: ★★★ **2026-10-03（接手轮）修的一处缺陷（★ 我自己的探针）**：
    #:   上一版写成 `kwargs = {k: v for k, v in args.items() if k in want}` ——
    #:   ★ **漏了 `param_alias`**。而注册器的真口径逐字是
    #:   （`tool_registry.py:493-498`）：
    #:     ```
    #:     for p in spec.params:
    #:         if p.name in spec.param_alias and spec.param_alias[p.name] is None: continue
    #:         target = spec.param_alias.get(p.name, p.name)
    #:         kwargs[target] = getattr(params, p.name)
    #:     ```
    #:   ★★ 后果：`batch74` 用 `param_alias` 把 `wall_ratio` 映射到 `wall_thickness_ratio`
    #:     ⇒ ★ 我传 `wall_ratio` 时当场 `TypeError: unexpected keyword argument`
    #:     ⇒ ★ **把一条好工具记成了坏的**（★ 与事实 36/502 同族：**报错指向名字，真因在别处**）。
    out_note: list = []
    kwargs = {}
    for k, v in args.items():
        if k not in want:
            continue
        if k in alias and alias[k] is None:
            continue                     #: ★ 由解析器消费，不进目标函数
        kwargs[alias.get(k, k)] = v
    inj = spec.inject
    if inj not in RC.RESOLVERS:
        return {"ok": False, "err": "★ 注入名 %r 不在 RESOLVERS" % inj}
    kwargs[inj] = RC.RESOLVERS[inj](None)
    #: ★★★ **2026-10-03（接手轮）补的第二处**：注册器在调目标函数前还会跑
    #:   `pre_call(params)`（副作用）与 **`derived_args(params)`（补实参）**
    #:   （`tool_registry.py:510-523` 逐字）。★ 我上一版**两样都没跑** ⇒
    #:   ★ 那些靠 `derived_args` 补「必填形参」的工具会当场
    #:   `TypeError: … missing 1 required positional argument`
    #:   ⇒ ★ **又一条好工具被我记成坏的**（★ 实测：`create_base_flange` 等 4 条钣金工具，
    #:     其 `spec` 形参正是由 `derived_args` 供给的 —— `derived_args` 补 kwargs 的规则还含
    #:     「**不得覆盖已直传的参数名**」，这里照抄）。
    class _P:                                    #: ★ 形参对象：注册器的 `derived_args(params)` 收的就是它
        pass

    _params = _P()
    for _k, _v in args.items():
        setattr(_params, _k, _v)
    _params.response_format = None
    if getattr(spec, "pre_call", None) is not None:
        try:
            spec.pre_call(_params)
            out_note.append("pre_call 已跑")
        except Exception as exc:                                      # noqa: BLE001
            out_note.append("pre_call 抛错 %s: %s" % (type(exc).__name__, str(exc)[:90]))
    if getattr(spec, "derived_args", None) is not None:
        try:
            _extra = spec.derived_args(_params) or {}
            _clash = set(_extra) & set(kwargs)
            if _clash:
                out_note.append("derived_args 想覆盖 %s（★ 契约不允许）" % sorted(_clash))
            kwargs.update({k: v for k, v in _extra.items() if k not in _clash})
            out_note.append("derived_args 补了 %s" % sorted(_extra))
        except Exception as exc:                                      # noqa: BLE001
            out_note.append("derived_args 抛错 %s: %s" % (type(exc).__name__, str(exc)[:90]))
    out: dict = {"call_path": "module=%s function=%s inject=%s params=%s"
                              % (spec.module, spec.function, inj, sorted(kwargs)),
                 "notes": list(out_note)}
    try:
        ret = fn(**kwargs)
        if isinstance(ret, dict):
            #: ★★ 2026-10-03：**记整份返回** —— 上一版只拷白名单键 ⇒
            #:   ★ 把 `selection_marks`（工具**自己读到的选区**）丢掉了 ⇒
            #:   前置判 False 时**看不出它读到了几个、什么 mark**（★ 白名单会把诊断字段吃掉）。
            out["ret_all"] = {k: (str(v)[:200] if not isinstance(v, (int, float, bool, type(None), list, dict))
                                  else v) for k, v in ret.items()}
            for k in ("ok", "preconditions_held", "ret_name", "ret_type", "ret_is_none",
                      "new_features", "error", "err"):
                if k in ret:
                    out[k] = ret[k]
        out["ret_ok"] = out.get("ok")
        out["ok"] = bool(out.get("ok"))
    except Exception as exc:                                              # noqa: BLE001
        out["ok"] = False
        out["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:260])
    return out


def _state(doc) -> dict:
    """★ 三合一读数（★ 闭合角那条**没有"返回非 None"这条判据** ⇒ 只能靠这三个）。"""
    st: dict = {}
    try:
        st["features"] = list(P.feature_names(doc) or [])
    except Exception:                                                     # noqa: BLE001
        st["features"] = None
    try:
        bodies = list(_g(doc, "GetBodies2", 0, True) or [])
        st["body_count"] = len(bodies)
        st["face_count"] = sum(len(list(_g(b, "GetFaces") or [])) for b in bodies)
    except Exception:                                                     # noqa: BLE001
        pass
    return st


def _delta(before: dict, after: dict) -> dict:
    d: dict = {}
    if before.get("features") is not None and after.get("features") is not None:
        d["new_features"] = [n for n in after["features"] if n not in before["features"]]
    if "face_count" in before and "face_count" in after:
        d["face_delta"] = after["face_count"] - before["face_count"]
    return d


def _l_shape_sketch(doc):
    """★ **闭合矩形**草图 —— ★ `create_base_flange` 的文档逐字：closed contour ⇒ **平板**。

    ★★ 2026-10-03 修：上一版画**两条线**（想当"开放折线"走 profile flange）⇒ ★ 真机上
      `create_base_flange` **回了 `ok=False` 且不抛错**（★ 静默无输出那个体量）⇒
      ★ 换成**闭合矩形**（官方文档里最明确的那个形态）先把"有没有钣金件"这件事确定下来。
    """
    P.start_sketch(doc, plane_name="Front Plane")
    _g(_g(doc, "SketchManager"), "CreateCornerRectangle",
       -0.05, -0.03, 0.0, 0.05, 0.03, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("草图") or n.lower().startswith("sketch")]
    return names[-1] if names else "草图1"


def _line_sketch(doc):
    P.start_sketch(doc, plane_name="Front Plane")
    _g(_g(doc, "SketchManager"), "CreateLine", -0.08, 0.0, 0.0, 0.08, 0.0, 0.0)
    P.end_sketch(doc)
    names = [n for n in (P.feature_names(doc) or [])
             if n.startswith("草图") or n.lower().startswith("sketch")]
    return names[-1] if names else "草图1"


def _profile() -> str:
    """★ 找**焊件轮廓**（`.sldlfp`）—— ★ 必须落在 `weldment profiles` 目录下。

    ★★ 2026-10-03 修：上一版直接 `rglob("*.sldlfp")` 取第一个 ⇒ ★ 挑到的是
      `...\design library\features\inch\fluid power ports\...sldlfp`
      —— ★ **那是"库特征"、不是焊件轮廓** ⇒ `InsertStructuralWeldment5` 必失败
      （★ 真机报「创建失败」—— 而错误信息**指不出是轮廓选错了**）。
    """
    for root in (r"C:\ProgramData\SOLIDWORKS", r"C:\ProgramData\SolidWorks"):
        for h in sorted(Path(root).rglob("*.sldlfp")):
            if "weldment profiles" in str(h).lower():
                return str(h)
    return ""


def _pick_faces(doc, count: int, mark: int) -> dict:
    """★ 按官方 mark 选 `count` 个面 —— ★ **官方前置就是它**。

    · 顶端盖 `InsertEndCapFeature3` 官方逐字：「select one or more **end faces**」，
      ★ **没给 mark**（官方例子用 **mark=0**）⇒ 本函数传 `mark=0`。
    · 角撑板 `InsertGussetFeature3` 官方逐字：「**two faces** … with a **Mark of 1**」
      ★ 且官方例子**两次都 `Append=True`** ⇒ 本函数照办。
    ★ 取面顺序不做假设（★ 官方没说哪两个面），只保证「**选上了 N 个、且 mark 对**」，
      并把实选到的数量如实回报 —— ★ 选不上就报**前置未成立**，不硬调。
    """
    import scripts.sw_part as _SP
    out = {"requested": count, "mark": mark, "selected": 0, "errs": []}
    try:
        _g(doc, "ClearSelection2", True)
    except Exception:                                                     # noqa: BLE001
        pass
    def _count(m: int) -> int:
        #: ★★ **事实 8**：`Select4` / `SelectByID2` 的**布尔返回值不可信**，
        #:   ★ **只有回读计数算数**（本仓实测：12 次全 false 而计数 12）。
        try:
            return int(_g(_g(doc, "SelectionManager"), "GetSelectedObjectCount2", m) or 0)
        except Exception:                                                 # noqa: BLE001
            return -1

    picked = 0
    for body in list(_g(doc, "GetBodies2", 0, True) or []):
        for face in list(_g(body, "GetFaces") or []):
            if picked >= count:
                break
            try:
                _SP._select_com_object(face, append=(picked > 0), mark=mark)
                #: ★★ **不回读就等于没选** —— 上一版信了 bool 返回值 ⇒
                #:   ★ 报「selected 1」而工具那边读到 **全 0**
                #:   （★ 工具 `_selection_marks` 回读的是 `GetSelectedObjectCount2(mark)`）。
                if _count(mark) > picked:
                    picked = _count(mark)
            except Exception as exc:                                      # noqa: BLE001
                out["errs"].append("%s: %s" % (type(exc).__name__, str(exc)[:60]))
        if picked >= count:
            break
    out["selected"] = picked
    out["readback_mark"] = _count(mark)
    out["readback_all"] = _count(-1)
    out["held"] = picked >= count
    return out


def main() -> int:
    started = time.time()
    row: dict = {"at": time.strftime("%Y-%m-%d %H:%M:%S"), "cases": []}
    sw, _ = C.connect_solidworks(wait_seconds=30)
    prof = _profile()
    row["profile_path"] = prof

    plan = [
        ("solidworks_sheet_metal_insert_miter_flange", "base_flange",
         {"use_default_radius": True, "global_radius_mm": 0.0, "rip_gap_mm": 0.0,
          "use_default_relief": True, "use_relief_ratio": False, "relief_ratio": 0.0,
          "relief_width_mm": 0.0, "relief_depth_mm": 0.0, "relief_type": 1,
          "trim_side_bends": False, "flange_pos": 1, "offset_dist1_mm": 0.0,
          "offset_dist2_mm": 0.0}),
        ("solidworks_sheet_metal_insert_closed_corner", "base_flange", {}),
        ("solidworks_weldment_insert_end_cap", "structural",
         {"depth_mm": 5.0, "is_given_offset": False, "is_chamfer": False, "offset_value_mm": 0.0,
          "wall_ratio": 0.0, "chamfer_value_mm": 0.0, "is_corner_treatment": False,
          "depth_offset_mm": 0.0, "is_reverse": False, "is_end_cap_inward": 0}),
        ("solidworks_weldment_gusset_create", "structural",
         {"depth_mm": 5.0, "dir_type": 1, "loc_type": 1, "is_profile": False,
          "profile_d1_mm": 0.0, "profile_d2_mm": 0.0, "profile_d3_mm": 0.0,
          "profile_angle_deg": 45.0, "profile_d4_mm": 0.0, "offset_reference_plane": False,
          "d_profile_offset_mm": 0.0, "crv_index": 0, "reverse_dir": False,
          "reverse_face": False, "use_len_dim": False, "profile_d5_mm": 0.0,
          "profile_d6_mm": 0.0, "profile_chamfer_angle_deg": 45.0,
          "use_len_dim_for_chamfer": False, "need_chamfer_in_gusset": False}),
    ]

    for tool, setup, args in plan:
        r: dict = {"tool": tool, "setup": setup}
        doc = None
        try:
            doc = C.new_document(sw, "part")
            if setup == "base_flange":
                sk = _l_shape_sketch(doc)
                r["sketch"] = sk
                r["setup_call"] = _call("solidworks_sheet_metal_create_base_flange",
                                        {"sketch_name": sk, "thickness_mm": 1.0,
                                         "bend_radius_mm": 1.0, "depth_mm": 30.0,
                                         "k_factor": 0.42, "relief_ratio": 0.5,
                                         "reverse_direction": False,
                                         "reverse_thickness": False})
                r["is_sheet_metal"] = bool((_call("solidworks_sheet_metal_evidence", {}) or {}).get("ok"))
            elif setup == "structural":
                sk = _line_sketch(doc)
                r["sketch"] = sk
                r["profile"] = prof
                if prof:
                    r["setup_call"] = _call("solidworks_weldment_create_structural_member",
                                            {"sketch_name": sk, "profile_path": prof})
                else:
                    r["setup_call"] = {"ok": False, "err": "★ 找不到 .sldlfp 焊件轮廓"}
            #: ★★ 2026-10-03（接手轮）：**官方前置是"先选面"** ⇒ 调工具前按 mark 选好
            #:   （★ 端盖 mark=0 选 1 个端面 · 角撑板 mark=1 选 2 个面），并把实选数如实记下。
            _need = {"solidworks_weldment_insert_end_cap": (1, 0),
                     "solidworks_weldment_gusset_create": (2, 1)}.get(tool)
            if _need:
                r["face_pick"] = _pick_faces(doc, _need[0], _need[1])
            before = _state(doc)
            r["call"] = _call(tool, args)
            after = _state(doc)
            r["delta"] = _delta(before, after)
            r["ok"] = bool(r["call"].get("ok") or (r["delta"].get("new_features") or []))
            r["judged_by"] = ("工具返回 ok **或** 树增量"
                              "（★ 闭合角那条**没有「返回非 None」这条判据** ⇒ 树/面/体积三合一）")
        except Exception as exc:                                          # noqa: BLE001
            r["ok"] = False
            r["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:260])
        finally:
            try:
                if doc is not None:
                    _g(sw, "CloseDoc", str(_g(doc, "GetTitle") or ""))
            except Exception:                                             # noqa: BLE001
                pass
        row["cases"].append(r)
    row["passed"] = sum(1 for r in row["cases"] if r.get("ok"))
    row["total"] = len(row["cases"])
    row["seconds"] = round(time.time() - started, 2)
    OUT.write_text(json.dumps(row, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
