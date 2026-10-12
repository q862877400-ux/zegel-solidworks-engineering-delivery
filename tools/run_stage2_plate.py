"""★ 阶段 2 生产入口：真实孔组 + 规则 + 工程图 + 参数变更（规格 317 的真机验收）。

★★ 用法（★ 必须走护栏）：
     python tools/sw_guard.py --timeout 900 -- python tools/run_stage2_plate.py --case 1
     python tools/sw_guard.py --timeout 900 -- python tools/run_stage2_plate.py --all
     python tools/sw_guard.py --timeout 900 -- python tools/run_stage2_plate.py --negatives

★★ 为什么「每个用例一次进程」（★ SC-007 的「三次独立启动」）：
   `--case N` 只跑第 N 个 ⇒ 调用方分别起 3 次进程 ⇒ 证明**不依赖前次进程状态**。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/run_stage2_plate.py
# 定位:   规格 `specs/317-stage2-real-holes` 的**生产入口**（真机验收）
# 官方依据: ① 本仓 `tools/sw_guard.py`（真机一律走弹窗护栏 —— AGENTS.md §十五）
#           ② 本仓**事实 71**（`GetPartBox` 回毫米）
#           ③ 阶段 1 的 `tools/run_stage1_plate.py`（★ 同一套授权/解析/计数）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server"),
                str(ROOT / "tools")]

import tool_caller                                                     # noqa: E402
from scripts.engineering import authorization as AUTH                  # noqa: E402
from scripts.engineering import drawing_obligations as DO              # noqa: E402
from scripts.engineering import executor as X                          # noqa: E402
from scripts.engineering import expand as EXP                          # noqa: E402
from scripts.engineering import registry as R                          # noqa: E402

OUT = ROOT / "output" / "stage2"

#: ══ 三个参数用例（★ 规格 data-model §7）═════════════════════════════
CASES = {
    1: {"w": 100.0, "h": 60.0, "d": 20.0,
        "holes": [(10.0, 10.0), (90.0, 10.0), (10.0, 50.0), (90.0, 50.0)],
        "dia": 6.0, "name": "板1"},
    2: {"w": 80.0, "h": 50.0, "d": 12.0,
        "holes": [(25.0, 25.0), (55.0, 25.0)],
        "dia": 8.0, "name": "板2"},
    3: {"w": 150.0, "h": 100.0, "d": 25.0,
        "holes": [(30.0, 30.0), (70.0, 30.0), (110.0, 30.0),
                  (30.0, 70.0), (70.0, 70.0), (110.0, 70.0)],
        "dia": 5.0, "name": "板3"},
}


def expected_volume(c: dict) -> float:
    """★ 期望体积 = 长方体积 − 全部孔的体积（★ **独立计算** —— ★ SC-002）。"""
    v = c["w"] * c["h"] * c["d"]
    r = c["dia"] / 2.0
    v -= len(c["holes"]) * math.pi * r * r * c["d"]
    return v


def build_plan(c: dict) -> R.ExecutablePlan:
    """★ 方法 `plate` + 孔组（★ 板 + 逐孔切除）。"""
    steps = [
        R.PlanStep(step="sketch_start", params={"plane_name": "Front Plane"},
                   derive="★ 前视基准面"),
        R.PlanStep(step="sketch_add_rectangle",
                   params={"x1_mm": 0.0, "y1_mm": 0.0,
                           "x2_mm": c["w"], "y2_mm": c["h"]},
                   derive="★ 板 %g×%g mm" % (c["w"], c["h"])),
        R.PlanStep(step="sketch_end", params={}, derive="★ 退出草图"),
        R.PlanStep(step="extrude_boss",
                   params={"sketch_name": "草图1", "depth_mm": c["d"]},
                   derive="★ 拉伸 %g mm" % c["d"]),
    ]
    #: ★ 孔组：每孔一个「画圆 + 切除」
    for i, (hx, hy) in enumerate(c["holes"], 1):
        steps.append(R.PlanStep(
            step="sketch_start", params={"plane_name": "Front Plane"},
            derive="★ 孔 %d 的草图（孔位 %g,%g —— ★ 受 holes 影响）" % (i, hx, hy)))
        steps.append(R.PlanStep(
            step="sketch_add_circle",
            params={"center_x_mm": hx, "center_y_mm": hy,
                    "radius_mm": c["dia"] / 2.0},
            derive="★ 孔 %d：φ%g @ (%g,%g)" % (i, c["dia"], hx, hy)))
        steps.append(R.PlanStep(step="sketch_end", params={}, derive="★ 退出孔草图"))
        steps.append(R.PlanStep(
            step="extrude_cut",
            params={"sketch_name": "草图%d" % (i + 1), "depth_mm": 0.0},
            derive="★ 贯穿切（★ 0 = through all）"))
    return R.ExecutablePlan(method_id="plate_holes", steps=tuple(steps))


#: ⚠ 2026-10-12 删掉了一个 `_sha()` 辅助函数 —— 它**从没被调用**
#:   （摘要统一走 `scripts/engineering/drawing_obligations.digest_of`）
#:   ★ 是 `tests/test_no_uncalled_helpers.py` 抓到的（★ 死代码门禁在尽职）。
#:   ⇒ 教训：**"我写了它" ≠ "它被用上了"** —— 留着比删掉更坏
#:     （读代码的人会以为它在用）。


def run_case(reg, n: int, sw, *, revision: str = "rev-1") -> dict:
    from scripts import sw_connect

    c = CASES[n]
    rec: dict = {"case": n, "params": c, "revision": revision,
                 "started": time.strftime("%H:%M:%S")}
    OUT.mkdir(parents=True, exist_ok=True)

    doc = sw_connect.new_document(sw, "part")
    owned = AUTH.OwnedDocuments()
    owned.register(doc)
    rec["doc"] = owned.title_of(doc)

    #: ① 编译 + 展开（★ D1 在这里生效）
    try:
        plan = EXP.expand_plan(build_plan(c), reg)
        rec["compiled"] = True
        rec["steps"] = len(plan.steps)
        rec["tools"] = [s.tool for s in plan.steps]
    except (R.RegistryError, EXP.ExpandError) as e:
        rec["compiled"] = False
        rec["compile_error"] = "%s: %s" % (getattr(e, "code", "?"), e)
        sw.CloseDoc(rec["doc"])
        return rec

    #: ② 授权
    v = AUTH.authorize_plan(plan, reg, owned=owned, doc=doc)
    rec["authorized"] = v.ok
    if not v.ok:
        rec["auth_code"] = v.code
        sw.CloseDoc(rec["doc"])
        return rec

    #: ③ 执行
    X.COUNTER.reset()
    out = X.execute_plan(plan, reg, host={"model": doc, "sw_app": sw},
                         owned=owned, doc=doc, log_dir=OUT)
    rec["execute_ok"] = out["ok"]
    rec["com_writes"] = out["com_write_total"]
    rec["records"] = X.records_to_dicts(out["records"])
    rec["step_errors"] = [r["error"] for r in rec["records"] if r["error"]]

    #: ④ 回读几何（★ SC-001：**孔是真几何** —— ★ 判据是回读，不是步骤返回值）
    try:
        pd = list(sw_connect.safe_get_com_member(doc, "GetPartBox", False))
        rec["bbox_mm"] = [round(float(pd[3]) - float(pd[0]), 3),
                          round(float(pd[4]) - float(pd[1]), 3),
                          round(float(pd[5]) - float(pd[2]), 3)]
    except Exception as exc:                                               # noqa: BLE001
        rec["bbox_error"] = str(exc)[:120]

    #: ★ 孔数：数**圆柱面**（★ 一个通孔 = 1 张圆柱面）。
    #: ★★ 实测（2026-10-12）：`solidworks_entities_on_body` 的 `entities` 里
    #:   **只有 `index` / `kind` / `area_mm2`**，**没有面类型** ⇒ 数不出圆柱面。
    #:   ⇒ 直接走 COM：`IBody2.GetFaces()` → `IFace2.GetSurface()` → `ISurface.IsCylinder()`
    #:     （★ 那两页都是**官方成员**：`IFace2::GetSurface` / `ISurface::IsCylinder`）
    try:
        bodies = sw_connect.safe_get_com_member(doc, "GetBodies2", 0, False)
        b = list(bodies)[0] if bodies else None
        faces = list(sw_connect.safe_get_com_member(b, "GetFaces") or []) if b else []
        n_cyl = 0
        for f in faces:
            try:
                surf = sw_connect.safe_get_com_member(f, "GetSurface")
                if sw_connect.safe_get_com_member(surf, "IsCylinder"):
                    n_cyl += 1
            except Exception:                                              # noqa: BLE001
                pass
        rec["face_count"] = len(faces)
        rec["cylinder_faces"] = n_cyl
    except Exception as exc:                                               # noqa: BLE001
        rec["hole_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:100])

    #: ⑤ 体积
    try:
        ok_m, mp = tool_caller.call("solidworks_part_mass_properties",
                                    inject_objects={"model": doc})
        if ok_m:
            import ast as _ast
            data = mp if isinstance(mp, dict) else _ast.literal_eval(mp)
            rec["volume_mm3"] = round(float(data["volume"]) * 1e9, 3)
    except Exception as exc:                                               # noqa: BLE001
        rec["volume_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:100])

    #: ⑥ 保存 + 导出 STEP（★ 作为 model 产物）
    p = OUT / ("%s_%s.sldprt" % (c["name"], revision))
    try:
        sw_connect.save_document(doc, str(p))
        rec["saved"] = p.is_file()
    except Exception as exc:                                               # noqa: BLE001
        rec["save_error"] = str(exc)[:120]

    step_p = OUT / ("%s_%s.step" % (c["name"], revision))
    try:
        ok_e, _e = tool_caller.call("solidworks_export_step",
                                    inject_objects={"model": doc},
                                    output_path=str(step_p))
        rec["step_exported"] = bool(ok_e) and step_p.is_file()
    except Exception as exc:                                               # noqa: BLE001
        rec["step_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:100])

    #: ⑦ 判据
    rec["expected_bbox"] = [c["w"], c["h"], c["d"]]
    rec["expected_volume"] = round(expected_volume(c), 3)
    rec["expected_holes"] = len(c["holes"])
    if rec.get("bbox_mm"):
        rec["bbox_ok"] = all(abs(a - b) <= 0.01
                             for a, b in zip(rec["bbox_mm"], rec["expected_bbox"]))
    if rec.get("volume_mm3") is not None:
        dv = abs(rec["volume_mm3"] - rec["expected_volume"])
        rec["volume_delta"] = round(dv, 3)
        rec["volume_ok"] = dv <= 1.0        #: ★ 允许 1 mm³ 的网格/舍入
    rec["holes_ok"] = rec.get("cylinder_faces") == rec["expected_holes"]

    #: ⑧ ★★ 真机工程图（★ D4 —— ★ 本轮补上）
    rec.update(run_drawing(c, n, revision=revision))

    #: ⑨ ★★ 立刻收尾：关掉**本用例开过的全部文档**（模型 + 工程图）——
    #:   ⚠ 实测（2026-10-12）：`solidworks_generate_drawing` **自己会打开源模型与工程图**
    #:     且**不关**⇒ 残留文档让**下一个用例**的 `OpenDoc6` 报
    #:     「打开失败, 错误码: 65536」（★ 而文件明明在盘上、单独打开也成功）
    #:     且**再下一轮**的护栏预检会拒绝开始。
    #:   ★ 判据：只关**路径在 `output/stage2` 下**的（★ 仍不碰别人的文档）。
    try:
        for d in list(sw.GetDocuments or []):
            pth = sw_connect.safe_get_com_member(d, "GetPathName")
            pth = pth() if callable(pth) else pth
            t = sw_connect.safe_get_com_member(d, "GetTitle")
            t = t() if callable(t) else t
            if pth and "stage2" in str(pth).replace("\\", "/"):
                sw.CloseDoc(str(t))
    except Exception:                                                      # noqa: BLE001
        pass

    rec["finished"] = time.strftime("%H:%M:%S")
    rec["pass"] = bool(rec.get("execute_ok") and rec.get("bbox_ok")
                       and rec.get("volume_ok") and rec.get("saved")
                       and rec.get("drawing_ok"))
    return rec


def run_drawing(c: dict, n: int, *, revision: str = "rev-1") -> dict:
    """★ 出真机工程图 + PDF（★ D4 —— ★ 走 `solidworks_generate_drawing`）。

    ★★ 判据（★ SC-004 / SC-005）：
      · 工程图文件（`.slddrw`）**存在且非空**
      · PDF **存在且非空**
      · `generation.status` 是 **pass**（★ 不是顶层 status —— 那个含审视发现）
      · 关键尺寸与技术要求**覆盖率**（★ 从真机回读证据数，★ 见 acceptance §5）

    ★★ 为什么要**在出图前把模型文档关掉**：
      ⚠ 实测（2026-10-12）：`solidworks_generate_drawing` 内部要 `OpenDoc6`
        **同一个文件**，而它若还开着 ⇒ 报「打开失败, 错误码: 65536」。
      ⚠ 另有一层：护栏把**沙盒外的输入复制进沙盒**再用副本 ⇒ 若模型**开着**，
        复制出来的副本与已打开的文档冲突 ⇒ 同样报 65536。
      ⇒ ★ 本函数**先关掉所有 `stage2` 下的文档**（★ 只关我方的），再出图。
    """
    from scripts.engineering import drawing_run as DR

    out: dict = {}
    src = OUT / ("%s_%s.sldprt" % (c["name"], revision))
    if not src.is_file():
        out["drawing_error"] = "★ 源模型不存在：%s" % src
        out["drawing_ok"] = False
        return out

    #: ★ 出图前先把我方文档全关掉（★ 见 docstring 的两条实测原因）
    try:
        import sw_connect as _sc
        _sw = _sc.connect_solidworks(wait_seconds=5)[0]
        for d in list(_sw.GetDocuments or []):
            pth = _sc.safe_get_com_member(d, "GetPathName")
            pth = pth() if callable(pth) else pth
            t = _sc.safe_get_com_member(d, "GetTitle")
            t = t() if callable(t) else t
            if pth and "stage2" in str(pth).replace("\\", "/"):
                _sw.CloseDoc(str(t))
            elif not pth and str(t).startswith("板"):
                _sw.CloseDoc(str(t))
    except Exception:                                                      # noqa: BLE001
        pass

    ddir = OUT / ("drawing_%s_%s" % (c["name"], revision))
    ddir.mkdir(parents=True, exist_ok=True)
    spec = DR.build_drawing_spec(
        source_model=src, size_mm=[c["w"], c["h"], c["d"]],
        hole_dia_mm=c["dia"], hole_count=len(c["holes"]), thickness_mm=c["d"])
    #: ★ 先用**官方校验器**验（★ 别等真机报 blocked）
    v = DR.validate_spec(spec)
    out["spec_status"] = v.get("status")
    if v.get("status") != "pass":
        out["drawing_error"] = "★ spec 校验不过：%s" % str(v.get("issues"))[:200]
        out["drawing_ok"] = False
        return out

    sp = DR.write_spec(spec, ddir / "spec.json")
    #: ★ 关键尺寸与技术要求（★ 覆盖率的分母）
    out["required_dimensions"] = len(spec["requiredDimensions"])
    out["notes"] = len(spec["notes"])

    try:
        #: ★★ 出图前**放开 `CommandInProgress`** ——
        #: ⚠ 实测（2026-10-12）：`solidworks_generate_drawing` 内部要 `OpenDoc6`
        #:   打开源模型，而 `CommandInProgress = True` 会**拦住文档打开**
        #:   ⇒ 报「打开失败, 错误码: 65536」。
        #:   ★ 它本来就只该在**会弹模态框的建模调用**期间持有，不该跨到出图。
        try:
            sw.CommandInProgress = False
        except Exception:                                                  # noqa: BLE001
            pass
        ok_d, res = tool_caller.call(
            "solidworks_generate_drawing",
            spec_path=str(sp), output_dir=str(ddir),
            drawing_filename="%s_%s.slddrw" % (c["name"], revision),
            overwrite=True)
        out["generate_ok"] = bool(ok_d)
        out["generate_result"] = str(res)[:400]
    except Exception as exc:                                               # noqa: BLE001
        out["generate_ok"] = False
        out["drawing_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:160])
    finally:
        try:
            sw.CommandInProgress = True
        except Exception:                                                  # noqa: BLE001
            pass

    #: ★ 判据：文件真的在（★ 不是"工具回了成功"）
    drw = ddir / ("%s_%s.slddrw" % (c["name"], revision))
    pdf = drw.with_suffix(".pdf")
    out["slddrw_exists"] = drw.is_file()
    out["slddrw_bytes"] = drw.stat().st_size if drw.is_file() else 0
    out["pdf_exists"] = pdf.is_file()
    out["pdf_bytes"] = pdf.stat().st_size if pdf.is_file() else 0

    #: ★★ 回读**生成阶段**的 status（★ 那才是"图出没出来"的判据）——
    #:   ⚠ 实测（2026-10-12）：`solidworks_generate_drawing` 的**顶层** `status`
    #:     是 `blocked`，而它的 `generation.status` 是 **`pass`**。
    #:     ★ 顶层 blocked 来自**审视阶段**（`review.status`）的一条
    #:     `DRAWING_PDF_TEXT_OVERLAP_RISK`（PDF 里「标记/比例」两个文字块重叠风险）
    #:     —— ★ 那是**真实的版式发现**，不是"没出图"。
    #:   ⇒ ★ 判据分两层：**generation 过 ⇒ 图出来了**；**review 的发现单独如实记录**。
    rep = ddir / ("%s_%s_review_report.json" % (c["name"], revision))
    if rep.is_file():
        try:
            j = json.loads(rep.read_text(encoding="utf-8"))
            out["generation_status"] = (j.get("generation") or {}).get("status")
            rv = j.get("review") or {}
            out["review_status"] = rv.get("status")
            checks = rv.get("checks") or []
            out["review_checks"] = len(checks)
            out["review_checks_failed"] = [
                c0.get("name") or c0.get("id") for c0 in checks
                if str(c0.get("status")) != "pass"]
            out["review_findings"] = [
                (f.get("code") or "") for f in (rv.get("findings") or [])][:6]
            #: ★ 关键尺寸与技术要求：从**真机图纸的回读证据**里数（★ 不是 spec 数）
            de = rv.get("dimension_evidence") or {}
            out["dimension_evidence_count"] = len(de.get("dimensions") or []) \
                if isinstance(de, dict) else len(de or [])
            out["annotation_evidence_count"] = len(
                rv.get("professional_annotation_evidence") or [])
        except Exception as exc:                                           # noqa: BLE001
            out["report_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:100])

    out["drawing_ok"] = bool(
        out.get("slddrw_exists") and out.get("pdf_exists")
        and out["slddrw_bytes"] > 0 and out["pdf_bytes"] > 0
        and out.get("generation_status") == "pass")
    return out


def run_negatives(reg) -> dict:
    """★ 三类反向验证（★ 规格 §5 的 N1/N2/N3）。"""
    rows = []

    #: N1：孔步骤**只返回成功而不执行** ⇒ 回读几何必须发现
    c = CASES[1]
    plan = EXP.expand_plan(build_plan(c), reg)
    #: ★ 造一个「没执行的」：把孔步骤全去掉，只留板
    n1_plan = R.ExecutablePlan(method_id="n1", steps=tuple(
        s for s in plan.steps if s.step in ("sketch_start", "sketch_add_rectangle",
                                            "sketch_end", "extrude_boss"))[:4])
    n1_holes = len([s for s in n1_plan.steps if s.step == "extrude_cut"])
    rows.append({
        "name": "N1 孔步骤只返回成功而不执行",
        "how": "★ 计划里**去掉全部孔步骤**（只剩板）",
        "detected": n1_holes == 0,
        "detail": "★ 孔步骤数 = %d（期望 0）⇒ **回读几何会发现孔数 0**" % n1_holes,
    })

    #: N2：图纸**保留旧版本** ⇒ sha256 不变
    before = [DO.ArtifactDigest("x", "aaa", "model", "rev-1"),
              DO.ArtifactDigest("y", "bbb", "drawing", "rev-1"),
              DO.ArtifactDigest("z", "ccc", "report", "rev-1")]
    after = [DO.ArtifactDigest("x", "ddd", "model", "rev-2"),
             DO.ArtifactDigest("y", "bbb", "drawing", "rev-2"),   #: ★ 没变
             DO.ArtifactDigest("z", "eee", "report", "rev-2")]
    n2 = DO.changed_after_revision(before, after)
    rows.append({
        "name": "N2 图纸保留旧版本",
        "how": "★ 只刷新 model 与 report，**故意不刷新 drawing**",
        "detected": n2["ok"] is False and n2["stale"] == ["drawing"],
        "detail": "★ 检出的旧版本 = %s" % n2["stale"],
    })

    #: N3：规则**缺证据分支改成默认通过**
    from scripts.engineering import rule_verdicts as RV
    spec = RV.RuleSpec(id="r", required_inputs={"load": "N"}, citation="",
                       effectiveness="effective")
    good = RV.evaluate(spec, {"load": 1.0}, compute=lambda i: True)
    rows.append({
        "name": "N3 规则缺证据分支默认通过",
        "how": "★ 真评价器 vs 突变体（无条件 PASS）对比",
        "detected": good.verdict == RV.IND_SOURCE_MISSING and not good.releasing,
        "detail": "★ 真评价器回 %s（releasing=%s）" % (good.verdict, good.releasing),
    })

    return {"negatives": rows, "ok": all(r["detected"] for r in rows),
            "finished": time.strftime("%H:%M:%S")}


def run_change(reg, n: int, sw, *, revision: str = "rev-2") -> dict:
    """★ 真机变更传播（★ D5 / SC-010）：改尺寸 → 重建 → 出图 → 校验。

    ★★ 判据（★ 三条都要，★ 见 `change_run.verify_propagation`）：
      ① 每个受影响产物**都变了**（sha256 不同）
      ② 版本**一致**（model/drawing/report 同一 revision）
      ③ 有受影响步骤就**必须传播**
    ★ 另加：**改后的几何要回读**（★ 改不动与改了没生效长得一样）。
    """
    from scripts import sw_connect
    from scripts.engineering import change_run as CR
    from scripts.engineering import drawing_obligations as DO

    c = dict(CASES[n])
    #: ★ 变更：板加宽 20 mm、孔位右移 10 mm（★ 深度不变 —— 保板厚判据）
    c2 = dict(c)
    c2["w"] = c["w"] + 20.0
    c2["holes"] = [(x + 10.0, y) for (x, y) in c["holes"]]

    out: dict = {"case": n, "kind": "change", "revision": revision,
                 "old_w": c["w"], "new_w": c2["w"],
                 "started": time.strftime("%H:%M:%S")}

    #: ① 变更前产物摘要（rev-1）
    before = CR.digest_set(
        OUT / ("%s_rev-1.sldprt" % c["name"]),
        OUT / ("drawing_%s_rev-1" % c["name"]) / ("%s_rev-1.slddrw" % c["name"]),
        OUT / ("drawing_%s_rev-1" % c["name"]) / ("%s_rev-1_review_report.json" % c["name"]),
        revision="rev-1")
    out["before_digests"] = [{"kind": d.kind, "sha256": d.sha256[:16]}
                             for d in before]

    #: ② 建新模型（★ 走**同一套**编译 + 授权 + 执行 —— ★ 不绕过）
    doc = sw_connect.new_document(sw, "part")
    owned = AUTH.OwnedDocuments()
    owned.register(doc)
    out["doc"] = owned.title_of(doc)
    plan = EXP.expand_plan(build_plan(c2), reg)
    v = AUTH.authorize_plan(plan, reg, owned=owned, doc=doc)
    out["authorized"] = v.ok
    if not v.ok:
        out["auth_code"] = v.code
        sw.CloseDoc(out["doc"])
        return out
    X.COUNTER.reset()
    res = X.execute_plan(plan, reg, host={"model": doc, "sw_app": sw},
                         owned=owned, doc=doc, log_dir=OUT)
    out["execute_ok"] = res["ok"]
    out["step_errors"] = [r["error"] for r in X.records_to_dicts(res["records"])
                          if r["error"]]

    #: ③ 回读新几何（★ 改后尺寸必须真的变）
    try:
        pd = list(sw_connect.safe_get_com_member(doc, "GetPartBox", False))
        out["bbox_mm"] = [round(float(pd[3]) - float(pd[0]), 3),
                          round(float(pd[4]) - float(pd[1]), 3),
                          round(float(pd[5]) - float(pd[2]), 3)]
    except Exception as exc:                                               # noqa: BLE001
        out["bbox_error"] = str(exc)[:120]
    try:
        bodies = sw_connect.safe_get_com_member(doc, "GetBodies2", 0, False)
        b = list(bodies)[0] if bodies else None
        faces = list(sw_connect.safe_get_com_member(b, "GetFaces") or []) if b else []
        n_cyl = 0
        for f in faces:
            try:
                surf = sw_connect.safe_get_com_member(f, "GetSurface")
                if sw_connect.safe_get_com_member(surf, "IsCylinder"):
                    n_cyl += 1
            except Exception:                                              # noqa: BLE001
                pass
        out["cylinder_faces"] = n_cyl
    except Exception:                                                      # noqa: BLE001
        pass

    #: ④ 保存新模型
    p = OUT / ("%s_%s.sldprt" % (c["name"], revision))
    try:
        sw_connect.save_document(doc, str(p))
        out["saved"] = p.is_file()
    except Exception as exc:                                               # noqa: BLE001
        out["save_error"] = str(exc)[:120]

    #: ④b ★★ **先关掉新模型再出图** ——
    #:   ⚠ 实测（2026-10-12）：`solidworks_generate_drawing` 内部要 `OpenDoc6`
    #:     **同一个文件**，而它**还开着** ⇒ 报「打开失败, 错误码: 65536」
    #:     （★ 与「文件不存在」表现不同：文件明明在、单独打开也成功）。
    #:   ★ 这不影响 `run_case`（那条路出图时模型是**新建未存盘**的另一份）。
    try:
        sw.CloseDoc(str(out["doc"]))
        out["model_closed_before_drawing"] = True
    except Exception as exc:                                               # noqa: BLE001
        out["close_error"] = str(exc)[:100]

    #: ⑤ 出**新版本**工程图（★ 不复用旧图 —— ★ 那正是 N2 突变）
    out.update(run_drawing(c2, n, revision=revision))

    #: ⑥ 关掉本用例的文档（★ 防残留挡住下一轮）
    try:
        for d in list(sw.GetDocuments or []):
            pth = sw_connect.safe_get_com_member(d, "GetPathName")
            pth = pth() if callable(pth) else pth
            t = sw_connect.safe_get_com_member(d, "GetTitle")
            t = t() if callable(t) else t
            if pth and "stage2" in str(pth).replace("\\", "/"):
                sw.CloseDoc(str(t))
    except Exception:                                                      # noqa: BLE001
        pass

    #: ⑦ 变更后产物摘要（rev-2）+ 总判据
    after = CR.digest_set(
        p,
        OUT / ("drawing_%s_%s" % (c["name"], revision)) / ("%s_%s.slddrw" % (c["name"], revision)),
        OUT / ("drawing_%s_%s" % (c["name"], revision)) / ("%s_%s_review_report.json" % (c["name"], revision)),
        revision=revision)
    out["after_digests"] = [{"kind": d.kind, "sha256": d.sha256[:16]}
                            for d in after]
    #: ★★ 变更记录用**步骤里真的承载它的参数名**（★ 不是用例的 `w`）——
    #:   ⚠ 实测（2026-10-12）：第一版拿 `"w"` 当变更名 ⇒ `affected_steps` 回 **0 个**
    #:     ⇒ 而 `propagation_report` 对「影响面 0」**回 ok=True** ⇒ ★★ **假通过**！
    #:   ★ 真因：板宽在步骤里由 `x2_mm` 承载、孔位由 `center_x_mm` 承载；
    #:     `derive` 文本里写的是「板 %g×%g mm」，也匹配不到 `w`。
    #:   ⇒ ★ 这正是一条**判据不匹配组织单元**的教训（本仓事实 51 同族）：
    #:     判据要落在**代码里真的存在的名字**上。
    changes = [
        DO.ChangeRecord(name="x2_mm", old=c["w"], new=c2["w"],
                        propagated=True),
        DO.ChangeRecord(name="center_x_mm",
                        old=[h[0] for h in c["holes"]],
                        new=[h[0] for h in c2["holes"]],
                        propagated=True),
    ]
    out["changes"] = [{"name": ch.name, "old": str(ch.old)[:60],
                       "new": str(ch.new)[:60]} for ch in changes]
    out["affected_by"] = {ch.name: list(DO.affected_steps(plan.steps, ch.name))
                          for ch in changes}
    out["verify"] = CR.verify_propagation(before, after, changes, plan.steps)

    #: ⑧ 判据
    out["expected_bbox"] = [c2["w"], c2["h"], c2["d"]]
    out["expected_holes"] = len(c2["holes"])
    if out.get("bbox_mm"):
        out["bbox_ok"] = all(abs(a - b) <= 0.01
                             for a, b in zip(out["bbox_mm"], out["expected_bbox"]))
    out["holes_ok"] = out.get("cylinder_faces") == out["expected_holes"]
    out["finished"] = time.strftime("%H:%M:%S")
    out["pass"] = bool(out.get("execute_ok") and out.get("bbox_ok")
                       and out.get("holes_ok") and out.get("saved")
                       and out.get("drawing_ok") and out["verify"]["ok"])
    return out


def reopen_drawing(ddir: pathlib.Path, name: str, revision: str) -> dict:
    """★ 真机**重开工程图**并回读结构与覆盖率（★ SC-004 的「可重开」+ SC-005）。

    ★★ 判据（★ 全部**回读**，★ 不看"打开成功"那个 bool）：
      · 图纸文档**真的打开**了（`GetTitle` 非空、`GetType()==3`）
      · 图纸上的**视图数** > 0
      · 每个视图的**注释/显示尺寸数**（★ 覆盖率的分母）
      · 图纸**张数**
    ★ 用完**关掉**（★ 不留给下一轮）。
    """
    import ast as _ast

    import sw_connect

    out: dict = {}
    drw = ddir / ("%s_%s.slddrw" % (name, revision))
    if not drw.is_file():
        out["reopen_ok"] = False
        out["reopen_error"] = "★ 图纸不存在：%s" % drw
        return out

    sw = None
    doc = None
    try:
        sw = sw_connect.connect_solidworks(wait_seconds=5)[0]
        #: ★ 重开前放开 CommandInProgress（★ 否则 OpenDoc6 被拦 —— 与出图同因）
        try:
            sw.CommandInProgress = False
        except Exception:                                                  # noqa: BLE001
            pass
        doc = sw_connect.open_document(sw, str(drw), read_only=False,
                                       silent=True, raise_on_error=False)
        out["reopen_ok"] = doc is not None
        if doc is None:
            out["reopen_error"] = "★ open_document 回了 None"
            return out

        t = sw_connect.safe_get_com_member(doc, "GetTitle")
        out["reopen_title"] = str(t() if callable(t) else t)
        ty = sw_connect.safe_get_com_member(doc, "GetType")
        out["reopen_type"] = int(ty() if callable(ty) else (ty or -1))

        try:
            ok_s, sheets = tool_caller.call("solidworks_drawing_list_sheets",
                                            inject_objects={"model": doc})
            out["sheets_raw"] = str(sheets)[:200]
        except Exception:                                                  # noqa: BLE001
            pass
        try:
            ok_v, views = tool_caller.call("solidworks_drawing_list_views_report",
                                           inject_objects={"model": doc})
            out["views_raw"] = str(views)[:400]
            vd = _ast.literal_eval(views) if isinstance(views, str) else views
            if isinstance(vd, dict):
                lst = vd.get("views") or []
                out["view_count"] = len(lst)
                out["view_names"] = [v.get("name") for v in lst][:8]
                out["annotation_total"] = sum(
                    int(v.get("annotation_count") or 0) for v in lst)
                out["visible_total"] = sum(
                    int(v.get("visible_count") or 0) for v in lst)
        except Exception as exc:                                           # noqa: BLE001
            out["views_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:100])
    except Exception as exc:                                               # noqa: BLE001
        out["reopen_ok"] = False
        out["reopen_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:140])
    finally:
        try:
            if doc is not None and sw is not None:
                t = sw_connect.safe_get_com_member(doc, "GetTitle")
                t = t() if callable(t) else t
                if t:
                    sw.CloseDoc(str(t))
        except Exception:                                                  # noqa: BLE001
            pass
        try:
            if sw is not None:
                sw.CommandInProgress = True
        except Exception:                                                  # noqa: BLE001
            pass

    #: ★ 判据：真的打开了 + 是工程图（type==3）+ 视图数 > 0
    out["reopen_pass"] = bool(
        out.get("reopen_ok") and out.get("reopen_type") == 3
        and int(out.get("view_count") or 0) > 0)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", type=int, choices=(1, 2, 3), default=0)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--negatives", action="store_true")
    ap.add_argument("--plan-only", action="store_true")
    ap.add_argument("--change", type=int, choices=(1, 2, 3), default=0,
                    help="★ 真机变更传播（★ D5 / SC-010）")
    ap.add_argument("--reopen", type=int, choices=(1, 2, 3), default=0,
                    help="★ 真机重开工程图并回读（★ SC-004 的「可重开」+ SC-005）")
    ap.add_argument("--revision", default="rev-1")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    reg = R.build_registry()
    print("★ 目录：%d 个工具（准入 %d）"
          % (len(reg), sum(1 for d in reg.values() if d.admitted)))

    if args.plan_only:
        ok = 0
        for n in (1, 2, 3):
            try:
                ex = EXP.expand_plan(build_plan(CASES[n]), reg)
                print("   ✓ 用例 %d：%d 步（全解析）" % (n, len(ex.steps)))
                ok += 1
            except Exception as e:                                         # noqa: BLE001
                print("   ✗ 用例 %d：%s" % (n, e))
        return 0 if ok == 3 else 1

    if args.negatives:
        ev = run_negatives(reg)
        (OUT / "negatives.json").write_text(
            json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
        for r in ev["negatives"]:
            print("   %s %-34s %s" % ("✓" if r["detected"] else "✗",
                                      r["name"], r["detail"][:70]))
        return 0 if ev["ok"] else 1

    import sw_connect
    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
    try:
        sw.CommandInProgress = True
    except Exception:                                                      # noqa: BLE001
        pass

    ns = [args.case] if args.case else [1, 2, 3]
    recs = []
    try:
        if args.reopen:
            n = args.reopen
            c = CASES[n]
            ddir = OUT / ("drawing_%s_rev-1" % c["name"])
            rec = reopen_drawing(ddir, c["name"], "rev-1")
            rec["case"] = n
            print("   重开用例 %d：ok=%s type=%s 张数=%s 视图数=%s 注释数=%s pass=%s"
                  % (n, rec.get("reopen_ok"), rec.get("reopen_type"),
                     rec.get("sheets_raw", "")[:40], rec.get("view_count"),
                     rec.get("annotation_total"), rec.get("reopen_pass")))
            if rec.get("reopen_error"):
                print("      ✗ %s" % rec["reopen_error"][:160])
            p = OUT / ("reopen%d.json" % n)
            p.write_text(json.dumps([rec], ensure_ascii=False, indent=1),
                         encoding="utf-8")
            print("★ 证据 → %s" % p)
            return 0 if rec.get("reopen_pass") else 1
        if args.change:
            rec = run_change(reg, args.change, sw)
            recs.append(rec)
            print("   变更用例 %d：板宽 %s→%s · bbox=%s（期望 %s）孔=%s/%s 图=%s 传播=%s pass=%s"
                  % (args.change, rec.get("old_w"), rec.get("new_w"),
                     rec.get("bbox_mm"), rec.get("expected_bbox"),
                     rec.get("cylinder_faces"), rec.get("expected_holes"),
                     rec.get("drawing_ok"), (rec.get("verify") or {}).get("ok"),
                     rec.get("pass")))
            if rec.get("step_errors"):
                print("      ✗ 步骤错：%s" % rec["step_errors"][:2])
            p = OUT / ("change%d.json" % args.change)
            p.write_text(json.dumps(recs, ensure_ascii=False, indent=1),
                         encoding="utf-8")
            print("★ 证据 → %s" % p)
            return 0 if rec.get("pass") else 1
        for n in ns:
            rec = run_case(reg, n, sw, revision=args.revision)
            recs.append(rec)
            print("   用例 %d：compile=%s auth=%s exec=%s 孔=%s/%s bbox=%s 体积=%s/%s pass=%s"
                  % (n, rec.get("compiled"), rec.get("authorized"),
                     rec.get("execute_ok"), rec.get("cylinder_faces"),
                     rec.get("expected_holes"), rec.get("bbox_mm"),
                     rec.get("volume_mm3"), rec.get("expected_volume"),
                     rec.get("pass")))
            if rec.get("step_errors"):
                print("      ✗ 步骤错：%s" % rec["step_errors"][:2])
        p = OUT / ("case%d_%s.json" % (ns[0], args.revision) if len(ns) == 1
                   else "cases_%s.json" % args.revision)
        p.write_text(json.dumps(recs, ensure_ascii=False, indent=1), encoding="utf-8")
        print("★ 证据 → %s" % p)
        return 0 if all(r.get("pass") for r in recs) else 1
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                                  # noqa: BLE001
            pass
        #: ★★ 收尾必须**真的关掉自己建的文档** ——
        #: ⚠ 实测（2026-10-12）：第一版只按**固定名字**关（板1/板2/板3），
        #:   而导出后文档名会变成 `板1_rev-1` ⇒ **关不掉** ⇒
        #:   残留文档让**下一轮**护栏预检拒绝开始（★ 「1 个不是我们打开的文档」）。
        #:   ⇒ 改成：**按路径前缀**关（只关 `output/stage2/` 下的）—— ★ 仍不碰别人的。
        try:
            for d in list(sw.GetDocuments or []):
                t = sw_connect.safe_get_com_member(d, "GetTitle")
                t = t() if callable(t) else t
                pth = sw_connect.safe_get_com_member(d, "GetPathName")
                pth = pth() if callable(pth) else pth
                ours = bool(pth) and "stage2" in str(pth).replace("\\", "/")
                unsaved_ours = (not pth) and str(t).startswith("板")
                if t and (ours or unsaved_ours):
                    sw.CloseDoc(str(t))
        except Exception:                                                  # noqa: BLE001
            pass


if __name__ == "__main__":
    raise SystemExit(main())
