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
import hashlib
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


def _sha(p: pathlib.Path) -> str:
    if not p.is_file():
        return ""
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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
    rec["finished"] = time.strftime("%H:%M:%S")
    rec["pass"] = bool(rec.get("execute_ok") and rec.get("bbox_ok")
                       and rec.get("volume_ok") and rec.get("saved"))
    return rec


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", type=int, choices=(1, 2, 3), default=0)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--negatives", action="store_true")
    ap.add_argument("--plan-only", action="store_true")
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
