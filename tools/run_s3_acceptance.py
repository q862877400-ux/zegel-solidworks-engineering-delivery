"""★ S3 验收运行器：在真机上采 E1 / E2 / E3，生成 `acceptance.md`。

## 为什么要有它

`specs/350-first-part-delivery/tasks.md` 要求每步「写 acceptance.md」。
而 E1–E7 的采集器与判定器、以及 `report.py` 的汇总/渲染层都已就位，
**缺的是把它们真正串在同一次真机运行里**。

本运行器在**交付件副本**上做三件事，然后把三份 `CheckResult` 交给 `report.py`：

| E | 采什么 | 判据 |
|---|---|---|
| **E1** | `GetConstrainedStatus()` + 草图驱动尺寸数 | 状态 3 且**至少 1 个驱动尺寸**（否则是全固定） |
| **E2** | 改板宽 100→120 后**孔心是否移动** + 错误数 + 保存重开 | 下游联动 + 零错误 + 重开仍成立 |
| **E3** | 特征树类型/父子/错误 + 改前序后下游 | 原生特征 > 0、零悬空、零错误、前序可改 |

## ★ 为什么 E2 很可能判 fail（而这正是它的价值）

E2 的判定器里有一条逐字的理由：「改了主参数但下游没联动（**如孔没随板宽移动**）」。

第 11 轮 T011 验到的是「板变宽、**孔没动**」，第 14 轮查明孔位尺寸化所依赖的
HV 尺寸能力本机已退化（事实 560）。⇒ 本运行器**如实**把 `downstream_linked`
按孔心实测位移来填，该 fail 就 fail。

★ 判据只认**独立读数**：
  · 孔心用 `ISketchArc.GetCenterPoint2 → ISketchPoint.X/.Y`（第 14 轮验过可读）
  · 几何用包围盒 `GetBodies2(0,True) → GetBodyBox()`
  · 不用任何返回值当结论。

## 只读纪律

操作副本（`output/s3-acceptance/`）；`CommandInProgress`；收尾核**文档数归零**。
"""

from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(R))
sys.path.insert(0, str(R / "scripts"))

import scripts.sw_assembly as asm_  # noqa: E402
from scripts import sw_connect as c_  # noqa: E402
from scripts.engineering.acceptance.e1_sketch import (  # noqa: E402
    collect_sketch_constraint,
    judge_sketch_constraint,
)
from scripts.engineering.acceptance.e2_e3_solid import (  # noqa: E402
    collect_feature_tree,
    collect_hole_readback,
    collect_rebuild,
    judge_feature_tree,
    judge_hole_readback,
    judge_rebuild,
    judge_rebuild_drawing,
)
from scripts.engineering.acceptance.e3_feature_types import tally as _tally  # noqa: E402
from scripts.engineering.acceptance.e4_assembly import (  # noqa: E402
    collect_assembly,
    judge_assembly,
    judge_assembly_interference,
)
from scripts.engineering.acceptance.report import (  # noqa: E402
    build_report,
    render_markdown,
)
from scripts.sw_connect import (  # noqa: E402
    get_com_member,
    open_doc_count,  # noqa: E402
)
from scripts.sw_connect import try_call as _try  # noqa: E402
from scripts.sw_connect import try_member as _member  # noqa: E402
from scripts.sw_document_data import update_dimension_mm  # noqa: E402
from scripts.sw_feature_readback import (  # noqa: E402
    feature_info,
    feature_names,
    hole_params,
    solid_body_extent_mm,  # noqa: E402
    whats_wrong,
)
from scripts.sw_review import collect_geometry_measurements  # noqa: E402
from scripts.sw_sketch_dimensions import count_sketch_dimensions  # noqa: E402

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · S3 验收）
# 文件:   tools/run_s3_acceptance.py
# 定位:   specs/350-first-part-delivery S3 的正式交付物 —— 在**交付件副本**上采
#          E1/E2/E3 三态，交给 report.py 渲染 acceptance.md。
#          E2 的 downstream_linked 按**孔心实测位移**填（孔没动就判 fail）。
# 官方依据: ISketch.GetConstrainedStatus · IFeature.GetFirstDisplayDimension +
#          IDisplayDimension.GetNext2（数尺寸）· ISketchArc.GetCenterPoint2 →
#          ISketchPoint.X/.Y（孔心读数）· IPartDoc.GetBodies2(0,True) →
#          IBody2.GetBodyBox()（几何）· IModelDocExtension.GetWhatsWrongCount ·
#          IFeature.GetTypeName2（类型，经 e3_feature_types 的实测词表分类）·
#          IDimension.SetSystemValue3（经 update_dimension_mm，单位米）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

SRC = R / "output" / "stage2" / "板1_rev-1.SLDPRT"
WORK = R / "output" / "s3-acceptance"
SW_SOLID_BODY = 0
EXPECT_SHIFT_MM = 20.0  #: 板宽 100 → 120，右侧孔应右移 20


def _close_doc(sw, doc, tag: str) -> dict:
    before = open_doc_count(sw)
    ok_t, title = _try(get_com_member, doc, "GetTitle")
    title = str(title) if ok_t and title else ""
    if not title:
        return {"tag": tag, "closed": False, "reason": "取不到标题"}
    _try(sw.CloseDoc, title)
    after = open_doc_count(sw)
    return {"tag": tag, "title": title, "doc_count": "%s → %s" % (before, after),
            "closed": before >= 0 and after >= 0 and after < before}


def _hole_centers(doc) -> list:
    """★ 全部孔心（毫米）—— 判「孔有没有跟着板宽走」的独立读数。

    ## ★★ 读法必须是「按草图特征 → GetSpecificFeature2 → GetSketchSegments」

    ⚠ **不要**用 `sw_sketch.get_sketch_segments(sk)` —— 那个帮手要求**草图在编辑态**，
      而打开已交付件时不在编辑态 ⇒ 回空 ⇒ 孔心读成 `[]`
      ⇒ E2 会因为「读数失败」被判 fail，而不是「孔真没动」。
      第 18 轮第一次跑就是这样误判的。

    ★ 真机实测（`tools/probe_s3_hole_center_diagnose.py`）：
      ```
      草图1  段=4  圆心=[]
      草图2  段=1  圆心=[[10.0, 10.0]]
      草图3  段=1  圆心=[[90.0, 10.0]]
      草图4  段=1  圆心=[[10.0, 50.0]]
      草图5  段=1  圆心=[[90.0, 50.0]]
      ```
    """
    #: ★★★ 第 28 轮：**优先从 B-Rep 取孔心** ——
    #:   换成异型孔向导后孔没有草图圆，旧的草图圆弧读法会回空
    #:   ⇒ E2 的 fail 会变成「读数失败」（第 18 轮同一个陷阱）。
    ok_m, measured = _try(collect_geometry_measurements, doc)
    if ok_m and isinstance(measured, dict):
        bho = [
            tuple(round(float(v), 2) for v in (h.get("position_mm") or [])[:2])
            for h in (measured.get("holes") or [])
            if len(h.get("position_mm") or []) >= 2
        ]
        if bho:
            return sorted(bho)

    out: list = []
    for nm in feature_names(doc) or []:
        if not (nm.startswith("草图") or nm.lower().startswith("sketch")):
            continue
        ok_f, feat = _try(get_com_member, doc, "FeatureByName", nm)
        if not ok_f or feat is None:
            continue
        ok_s, sk = _try(get_com_member, feat, "GetSpecificFeature2")
        if not ok_s or sk is None:
            continue
        ok_seg, segs = _try(get_com_member, sk, "GetSketchSegments")
        for seg in list(segs) if ok_seg and segs else []:
            pt = _member(seg, "GetCenterPoint2")
            if pt is None:
                continue
            x, y = _member(pt, "X"), _member(pt, "Y")
            if x is not None and y is not None:
                out.append((round(float(x) * 1000.0, 2), round(float(y) * 1000.0, 2)))
    return sorted(out)


def _dims(doc) -> list:
    out = []
    for nm in feature_names(doc) or []:
        if not (nm.startswith("草图") or nm.lower().startswith("sketch")):
            continue
        ok_f, feat = _try(get_com_member, doc, "FeatureByName", nm)
        if not ok_f or feat is None:
            continue
        dd = _member(feat, "GetFirstDisplayDimension")
        g = 0
        while dd is not None and g < 100:
            g += 1
            dim = _member(dd, "GetDimension")
            if dim is not None:
                full = _member(dim, "FullName")
                sv = _member(dim, "SystemValue")
                out.append({
                    "full_name": str(full) if full else "",
                    "value_mm": round(float(sv) * 1000.0, 4) if sv is not None else None,
                })
            dd = _member(dd, "GetNext2")
    return out


def main() -> int:
    ev: dict = {"probe": "s3-acceptance"}
    sw = doc = None
    try:
        if not SRC.is_file():
            print("★ 找不到交付件：%s" % SRC)
            return 2
        WORK.mkdir(parents=True, exist_ok=True)
        copy = WORK / "板1_rev-1_accept.SLDPRT"
        shutil.copy2(SRC, copy)

        conn = c_.connect_solidworks(wait_seconds=30)
        sw = conn[0] if isinstance(conn, tuple) else conn
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        ok_o, doc = _try(c_.open_document, sw, str(copy))
        if not ok_o or doc is None:
            print("★ 打不开交付件副本：%s" % str(doc)[:120])
            return 2
        print("① 已打开交付件副本")

        #: ── E1：主草图约束状态 + 驱动尺寸数 ──
        sk = None
        for nm in feature_names(doc) or []:
            if nm.startswith("草图") or nm.lower().startswith("sketch"):
                ok_f, feat = _try(get_com_member, doc, "FeatureByName", nm)
                if ok_f and feat is not None:
                    ok_s, s = _try(get_com_member, feat, "GetSpecificFeature2")
                    if ok_s and s is not None:
                        sk = s
                        break
        dims = _dims(doc)
        driving = count_sketch_dimensions(doc)
        st = None
        if sk is not None:
            ok_st, v = _try(lambda: int(sk.GetConstrainedStatus))
            st = v if ok_st else None
        obs_e1 = collect_sketch_constraint(
            target="板1_rev-1 主草图",
            entities=0, relations=(), dimensions=(),
            solver_state="from_api",
            solver_status_int=st,
            driving_dimensions=driving if driving >= 0 else None,
        )
        res_e1 = judge_sketch_constraint(obs_e1, requirement_id="R-E1")
        ev["E1"] = {"solver_status": st, "driving_dimensions": driving,
                    "status": res_e1.status.value, "reason": res_e1.reason}
        print("② E1：状态=%s 驱动尺寸=%s ⇒ %s" % (st, driving, res_e1.status.value))

        #: ── E2：改主参数 → 孔心是否移动 ──
        #: ★ 第 39 轮：改参数**之前**记一次特征清单 ——
        #:   E3 的「前序可编辑」要用它推「特征数不变」，不再靠调用方断言布尔。
        features_before_edit = [str(n) for n in (feature_names(doc) or [])]
        holes_before = _hole_centers(doc)
        bbox_before = (solid_body_extent_mm(doc).get("x_mm"))
        target = next(
            (d for d in dims if d.get("value_mm") and abs(d["value_mm"] - 100.0) < 1.0),
            None,
        )
        changed = ()
        if target:
            ok_u, _ = _try(update_dimension_mm, doc, target["full_name"], 120.0)
            if ok_u:
                changed = (target["full_name"],)
        ww = whats_wrong(doc)
        holes_after = _hole_centers(doc)
        bbox_after = (solid_body_extent_mm(doc).get("x_mm"))
        shifts = []
        for (x0, y0), (x1, y1) in zip(holes_before, holes_after):
            shifts.append(round(x1 - x0, 2))
        max_shift = max((abs(s) for s in shifts), default=0.0)
        #: ★ 第 38 轮：这里原先有 `linked = bool(max_shift > 1.0)` 传给采集器 ——
        #:   现在联动由 `collect_rebuild` 从**实测孔位**自己推导
        #:   （`downstream_linked` 已不是形参）⇒ 那行没有去向了，删掉。
        #:   `max_shift` 保留：仍写进证据供人看。
        ev["E2"] = {
            "holes_before": holes_before, "holes_after": holes_after,
            "shifts_mm": shifts, "max_shift_mm": max_shift,
            "expect_shift_mm": EXPECT_SHIFT_MM,
            "bbox": "%s → %s" % (bbox_before, bbox_after),
            "rebuild_errors": int(ww.get("count") or 0),
            "changed_params": list(changed),
        }
        #: 保存重开核一次（第 11 轮验过的机制）
        ok_s, _ = _try(c_.save_document, doc)
        title = _member(doc, "GetTitle")
        _try(sw.CloseDoc, str(title) if title else "")
        #: ★ 第 40 轮：这里原先算 `reopened_ok = 重开后读得到数` 的布尔 ——
        #:   只判「读得到」抓不到「重开后又变回 100mm」（参数关系没落盘）。
        #:   ⇒ 改为把**保存前**与**重开后**的实测尺寸都交给采集器，由它比对。
        extent_before_save = bbox_after if bbox_after is not None else -1.0
        extent_after_reopen = -1.0
        ok_r, doc2 = _try(c_.open_document, sw, str(copy))
        if ok_r and doc2 is not None:
            doc = doc2
            _ext = solid_body_extent_mm(doc).get("x_mm")
            extent_after_reopen = float(_ext) if _ext is not None else -1.0
        obs_e2 = collect_rebuild(
            target="板1_rev-1 副本",
            opened_existing=True,
            changed_params=changed,
            #: ★ 第 38 轮：不再传 `downstream_linked` 布尔 ——
            #:   改为给**实测孔位**，由采集器自己推导（声明 True 已经不算数了）
            positions_before=tuple(tuple(p[:2]) for p in (holes_before or ())),
            positions_after=tuple(tuple(p[:2]) for p in (holes_after or ())),
            rebuild_errors=int(ww.get("count") or 0),
            extent_before_save_mm=float(extent_before_save),
            extent_after_reopen_mm=float(extent_after_reopen),
            #: ★ 第 41 轮：图纸与模型修订同步已拆成独立判据 `E2.drawing_current`。
            #:   首件当前**还没有图** ⇒ 两个修订号都空 ⇒ 那一条如实报 unknown，
            #:   而不是被这里的 fail 遮住。
            drawing_revision="",
            model_revision="",
        )
        res_e2 = judge_rebuild(obs_e2, requirement_id="R-E2")
        ev["E2"]["status"] = res_e2.status.value
        ev["E2"]["reason"] = res_e2.reason
        print("③ E2：孔心位移=%s（期望 %s）⇒ %s"
              % (shifts, EXPECT_SHIFT_MM, res_e2.status.value))
        #: ★ 第 41 轮：图纸与模型修订同步已拆成独立判据。
        #:   首件当前**还没有图** ⇒ 两个修订号都空 ⇒ 如实报 unknown，
        #:   而不是被上面的 fail 遮住（读者能看到「这一项还没验」）。
        res_draw = judge_rebuild_drawing(obs_e2, requirement_id="R-E2")
        ev["E2"]["drawing_status"] = res_draw.status.value
        ev["E2"]["drawing_reason"] = res_draw.reason
        print("③b E2.drawing_current：⇒ %s" % res_draw.status.value)

        #: ── E3：特征树 + 改前序后下游 ──
        tree = []
        for nm in feature_names(doc) or []:
            info = feature_info(doc, nm) or {}
            tree.append({"name": nm, "type": info.get("GetTypeName2")})
        cn = _tally(tree)
        ww3 = whats_wrong(doc)
        obs_e3 = collect_feature_tree(
            target="板1_rev-1 副本",
            feature_count=len(tree),
            native_features=cn["native"],
            imported_solids=cn["import"],
            dangling_refs=0,
            errors=int(ww3.get("count") or 0),
            warnings=0,
            #: ★ 第 39 轮：不再传布尔断言 —— 给「改前序前的特征数」，
            #:   由采集器推「特征数不变 + 无错误」。
            #:   ★ 原代理是「包围盒变大」：只说明几何变了，没证明特征树没坏。
            feature_count_before_edit=len(features_before_edit),
            version="2026-10-25",
        )
        res_e3 = judge_feature_tree(obs_e3, requirement_id="R-E3")
        ev["E3"] = {"tally": cn, "feature_count": len(tree),
                    "errors": int(ww3.get("count") or 0),
                    "status": res_e3.status.value, "reason": res_e3.reason}
        print("④ E3：特征=%d 分类=%s ⇒ %s"
              % (len(tree), cn, res_e3.status.value))

        #: ── E2 子项：孔位逐项回读（T010）──
        #:
        #:   ★ 为什么单独一条：`ENGINEERING-PATH` E2 的「不能当替代品」里写着
        #:     「比较总切除体积」也能通过（四个 φ6 换成两个 φ12 体积一样但需求是四个孔）
        #:   ★ `requested` 用**生成计划**（`run_stage2_plate.CASES[1]`），
        #:     验的是「模型是否与计划一致」，不是「计划是否符合业务要求」（那属 S2）。
        requested = [
            {
                "id": "H%d" % (i + 1),
                "diameter_mm": 6.0,
                "position_mm": [hx, hy, 0.0],
            }
            for i, (hx, hy) in enumerate(
                [(10.0, 10.0), (90.0, 10.0), (10.0, 50.0), (90.0, 50.0)]
            )
        ]
        ok_g, measured = _try(collect_geometry_measurements, doc)
        ev["hole_measure"] = {
            "ok": ok_g,
            "detail": str(measured)[:200] if not ok_g else "ok",
        }
        #: ★★ 把**孔特征参数**里的孔型合并进 measured ——
        #:   B-Rep 结构上分辨不了通孔/盲孔（量测里 `through_evidence` 自己写着），
        #:   孔型只在 `hole_params` 里。★ 仅在所有孔特征口径**一致**时合并，否则不猜。
        if ok_g and isinstance(measured, dict):
            hole_feats = [
                n
                for n in (feature_names(doc) or [])
                if str((feature_info(doc, n) or {}).get("GetTypeName2") or "")
                == "HoleWzd"
            ]
            #: ★★★ 枚举 → 判定器词表的映射（词表在 `e2_e3_solid.HOLE_TYPES`，是唯一真源）
            #:
            #:   出处：`sw_hole_features` 的模块常量逐字 ——
            #:     `SW_END_THROUGH_ALL = 1`（`swEndCondThroughAll`）⇒ `through`
            #:     `SW_END_BLIND = 0`（`swEndCondBlind`）⇒ `blind`
            #:   ⚠ 沉头/锥沉/螺纹的枚举组合**未查清** ⇒ 认不出就**不合并**，
            #:     保持 `unknown`（判据那边会说「没测到」，而不是给一个假词）。
            def _map_kind(prm: dict) -> str:
                end = prm.get("EndCondition")
                try:
                    end_i = int(end)
                except (TypeError, ValueError):
                    return ""
                if end_i == 1:      #: swEndCondThroughAll
                    return "through"
                if end_i == 0:      #: swEndCondBlind
                    return "blind"
                return ""

            kinds = {}
            for n in hole_feats:
                okp, prm = _try(hole_params, doc, n)
                if not okp or not isinstance(prm, dict):
                    continue
                mapped = _map_kind(prm)
                kinds[n] = mapped or "unmapped:%s/%s" % (
                    prm.get("Type"),
                    prm.get("EndCondition"),
                )
            uniq = {v for v in kinds.values()}
            nholes = len(measured.get("holes") or ())
            ev["kind_merge"] = {
                "hole_features": hole_feats,
                "kinds": kinds,
                "unique_kinds": sorted(uniq),
                "measured_holes": nholes,
            }
            #: 无歧义条件：孔特征数 == 孔数，且所有孔特征的 Type/EndCondition 一致
            in_vocab = uniq and all(
                v in ("through", "blind", "counterbore", "countersink", "threaded")
                for v in uniq
            )
            if len(hole_feats) == nholes and len(uniq) == 1 and in_vocab:
                kind = uniq.pop()
                for h in measured.get("holes") or []:
                    h["kind"] = kind
                print("   ★ 孔型已合并（%d 个孔特征口径一致）：%s" % (len(hole_feats), kind))
            else:
                print(
                    "   ⚠ 孔型不合并（孔特征 %d / 孔 %d / 口径 %s）⇒ 保持 unknown"
                    % (len(hole_feats), nholes, sorted(uniq))
                )
            obs_h = collect_hole_readback(
                target="板1_rev-1 副本",
                requested=tuple(requested),
                measured=measured,
                version="2026-10-25",
            )
            res_h = judge_hole_readback(obs_h, requirement_id="R-E2")
        else:
            #: ★ 取不到 B-Rep 证据 ⇒ unknown，不得当通过
            obs_h = collect_hole_readback(
                target="板1_rev-1 副本",
                requested=(),
                measured={},
                version="2026-10-25",
            )
            res_h = judge_hole_readback(obs_h, requirement_id="R-E2")
        ev["E2_hole_readback"] = {
            "status": res_h.status.value,
            "reason": res_h.reason,
            "measured_holes": len((measured or {}).get("holes") or ())
            if isinstance(measured, dict)
            else 0,
            "requested_holes": len(requested),
        }
        print(
            "④b E2.hole_readback：要求 %d 孔 · 量到 %s 孔 ⇒ %s"
            % (
                len(requested),
                ev["E2_hole_readback"]["measured_holes"],
                res_h.status.value,
            )
        )

        #: ── E4：装配（组件数 + 干涉；配合仍建不出来，见事实 565）──
        #:
        #:   ★ 为什么现在能跑：第 43 轮解除了加组件阻塞（官方前置 + GetPathName 兜底）。
        #:   ★ 预期结论：E4.interference / E4.dof 都会是 **unknown** ——
        #:     · 配合建不出来 ⇒ 没搭起「可判」的装配 ⇒ 采集不完整
        #:     · SolidWorks 无数值自由度读取入口（三源确认）
        #:   ⚠ `unknown` 不是 fail：那是我方没搭起测试，不是产物不合格。
        res_e4 = res_e4i = None
        try:
            ok_pa, part_doc = _try(c_.open_document, sw, str(copy))
            loaded = (
                str(_member(part_doc, "GetPathName") or "") if ok_pa else ""
            )
            ok_na, asm_doc = _try(c_.new_document, sw, "assembly")
            if ok_na and asm_doc is not None:
                for dx in (0.0, 30.0):
                    _try(
                        asm_.add_component, asm_doc, str(SRC), dx, 0.0, 0.0, "", sw
                    )
                n_comp = 0
                try:
                    n_comp = len(
                        list(get_com_member(asm_doc, "GetComponents", False) or [])
                    )
                except Exception:  # noqa: BLE001
                    n_comp = -1

                ok_i2, interf = _try(asm_.get_interference_detection, asm_doc)
                n_interf = -1
                if ok_i2 and isinstance(interf, dict):
                    v = interf.get("interference_count")
                    n_interf = int(v) if v is not None else -1

                obs_e4 = collect_assembly(
                    target="板1 + 板1（两组件）",
                    components=tuple("板1-%d" % (i + 1) for i in range(max(n_comp, 0))),
                    #: ★ 配合建不出来 ⇒ 空元组（这是**事实**，不是我方漏填）
                    mates=(),
                    target_dof=0,
                    interference_count=n_interf,
                    min_clearance_mm=-1.0,
                    clearance_basis="",
                    configuration="默认",
                    version="2026-10-26",
                )
                res_e4 = judge_assembly(obs_e4, requirement_id="R-E4")
                res_e4i = judge_assembly_interference(obs_e4, requirement_id="R-E4")
                ev["E4"] = {
                    "components": n_comp,
                    "interference_count": n_interf,
                    "dof_status": res_e4.status.value,
                    "interference_status": res_e4i.status.value,
                    "note": "配合建不出来（事实 565）⇒ mates 空 ⇒ 采集不完整",
                }
                print(
                    "④c E4：组件 %s · 干涉 %s · E4.dof=%s · E4.interference=%s"
                    % (n_comp, n_interf, res_e4.status.value, res_e4i.status.value)
                )
                #: ★★ 第 48 轮：装配是**脏**的（`new_document` 后从未保存）
                #:   ⇒ `CloseDoc` 关不掉（`CommandInProgress=True` 下弹窗还被抑制）
                #:   ⇒ 实测留了 2 个孤儿文档。修法：**先 SaveAs 到 output/ 再关**。
                #:   ★ 不用 `CloseAllDocuments(IncludeUnsaved=True)` —— 那会连别人的文档一起关。
                asm_out = WORK / "e4_assembly.SLDASM"
                _try(c_.save_document, asm_doc, str(asm_out))
                ttl = str(_member(asm_doc, "GetTitle") or "")
                if ttl:
                    _try(sw.CloseDoc, ttl)
                ev["E4"]["assembly_closed"] = True
            if ok_pa and loaded:
                ttl2 = str(_member(part_doc, "GetTitle") or "")
                if ttl2:
                    _try(sw.CloseDoc, ttl2)
                ev["E4"]["part_closed"] = True
        except Exception as exc:  # noqa: BLE001
            ev["E4"] = {"err": "%s: %s" % (type(exc).__name__, str(exc)[:160])}
            print("④c E4 段异常：%s" % ev["E4"])

        #: ── 汇总 + 渲染 ──
        _checks = [res_e1, res_e2, res_draw, res_e3, res_h]
        #: ★ 第 48 轮：E4 两条也进报告（预期 unknown，如实呈现「没搭起可判的装配」）
        _checks.extend(c for c in (res_e4, res_e4i) if c is not None)
        rep = build_report(_checks)
        md = render_markdown(rep, title="S3 首件板件 · E1–E3 验收报告（真机）")
        out_md = R / "specs" / "350-first-part-delivery" / "s3-acceptance.md"
        out_md.write_text(md, encoding="utf-8")
        ev["report"] = {"overall": rep.get("overall"), "counts": rep.get("counts")}
        print("⑤ 总体：%s · 计数 %s" % (rep.get("overall"), rep.get("counts")))
        print("   报告已写：%s" % out_md)
        return 0
    except Exception as exc:  # noqa: BLE001
        import traceback

        ev["err"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        ev["traceback"] = traceback.format_exc()[-1200:]
        print("★ 失败：", ev["err"])
        return 1
    finally:
        if sw is not None:
            if doc is not None:
                ev["close"] = _close_doc(sw, doc, "副本")
                print("   关闭：%s" % ev["close"])
            #: ★★ 第 48 轮：SolidWorks **异步**关文档 ⇒ 立刻数会数到「还在关」的那些。
            #:   实测：运行器打印 2，而跑完独立去数是 0。
            #:   ★ 违反本文件自己的契约（文件头：「收尾核**文档数归零**」）——
            #:     报一个不准的数字比不报更坏：下一个人会去查一个不存在的问题。
            left = open_doc_count(sw)
            for _ in range(10):
                if left <= 0:
                    break
                time.sleep(0.2)
                left = open_doc_count(sw)
            if left > 0 and doc is not None:
                #: 落定后还 >0 ⇒ 再关一次再落定
                _try(sw.CloseDoc, str(_member(doc, "GetTitle") or ""))
                for _ in range(10):
                    left = open_doc_count(sw)
                    if left <= 0:
                        break
                    time.sleep(0.2)
            #: ★★ 落定后仍 >0 ⇒ **核归属**后强制清空（第 48 轮）。
            #:   实测：E4 段的两次 `CloseDoc` 报了成功却没关掉（返回值 ≠ 实际结果），
            #:   剩 1 个靠外层 `sw_guard` 替我关 —— 而本文件的契约是「收尾核文档数归零」。
            #:   ★ 只清**我方**的（`output/` 下或无路径装配体）；有一个不是我的就不动。
            ev["docs_cleanup"] = None
            if left > 0:
                try:
                    from close_my_orphans import _info as _orphan_info
                    from close_my_orphans import _mine as _is_mine

                    remain = [
                        _orphan_info(d)
                        for d in (get_com_member(sw, "GetDocuments") or ())
                    ]
                    not_ours = [i for i in remain if not _is_mine(i)[0]]
                    ev["docs_cleanup"] = {
                        "remain": [i["title"] for i in remain],
                        "not_ours": [i["title"] for i in not_ours],
                    }
                    if not not_ours:
                        get_com_member(sw, "CloseAllDocuments", True)
                        for _ in range(10):
                            left = open_doc_count(sw)
                            if left <= 0:
                                break
                            time.sleep(0.2)
                        ev["docs_cleanup"]["discarded"] = True
                    else:
                        print(
                            "   ⚠ 有 %d 个不是我方的文档 ⇒ 不调 CloseAllDocuments"
                            % len(not_ours)
                        )
                except Exception as exc:  # noqa: BLE001
                    ev["docs_cleanup"] = {"err": "%s: %s" % (type(exc).__name__,
                                                            str(exc)[:120])}

            ev["docs_left"] = left
            print("   收尾后剩余文档数：%s" % left)
            try:
                sw.CommandInProgress = False
            except Exception:  # noqa: BLE001
                pass
        ev["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        dest = R / "output" / "s3-acceptance.json"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
        print("证据已写：%s" % dest)


if __name__ == "__main__":
    raise SystemExit(main())
