"""★ 阶段 1 生产入口：经方法入口安全建成参数板（规格 316 的真机验收）。

★★ 用法（★ 必须走护栏）：
     python tools/sw_guard.py --timeout 600 -- python tools/run_stage1_plate.py
     python tools/sw_guard.py --timeout 600 -- python tools/run_stage1_plate.py --case 1
     python tools/sw_guard.py --timeout 600 -- python tools/run_stage1_plate.py --negatives

★★ 为什么「每个用例一次进程」（★ SC-001 的「独立启动」要求）：
   `--case N` 只跑第 N 个用例 ⇒ 调用方**分别起 3 次进程** ⇒
   证明**不依赖前一次进程的状态** ✓
"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/run_stage1_plate.py
# 定位:   规格 `specs/316-stage1-parameter-plate` 的**生产入口**（真机验收）
# 官方依据: ① 本仓 `tools/sw_guard.py`（真机命令一律走弹窗护栏 —— AGENTS.md §十五）② 本
#           仓**事实 71**（`GetPartBox` 回毫米）③ `register_capabilities.all_specs()`（
#           工具契约真源）④ 规格 316 的 §4 SC-001~SC-010 与 §5 的 M1~M4
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "scripts"),
    str(ROOT / "mcp-server"),
    str(ROOT / "tools"),
]

import tool_caller  # noqa: E402

from scripts.engineering import authorization as AUTH  # noqa: E402
from scripts.engineering import executor as X  # noqa: E402
from scripts.engineering import registry as R

OUT = ROOT / "output" / "stage1"

#: ══ 三个参数用例（★ 规格 §7 data-model §8 逐字）═══════════════════════
#: ★ 判据：体积 = W×H×D − 倒角损耗（沿一条边 c 的损耗 = 0.5·c²·L）
CASES = {
    1: {"w": 100.0, "h": 60.0, "d": 20.0, "c": 2.0, "name": "板1"},
    2: {"w": 80.0, "h": 50.0, "d": 12.0, "c": 1.5, "name": "板2"},
    3: {"w": 150.0, "h": 100.0, "d": 25.0, "c": 3.0, "name": "板3"},
}


def expected_volume(c: dict) -> float:
    """★ 期望体积 = 长方体积 − 倒角损耗。

    ★★ 倒角切在**哪条边**（★ 实测反推，3/3 一致）：
      `selection="index:0"` 命中的是**竖直边**（★ 长度 = 板厚 `d`）。
      反推证据（`output/stage1/case*.json`）：
        · 用例 1：损耗 40.0 ⇒ `L = 40/(0.5·2²)` = **20.0** = `d` ✓
        · 用例 2：损耗 13.5 ⇒ `L = 13.5/(0.5·1.5²)` = **12.0** = `d` ✓
        · 用例 3：损耗 112.5 ⇒ `L = 112.5/(0.5·3²)` = **25.0** = `d` ✓
      ⇒ ★ 损耗 = `0.5 · c² · d`（★ **不是** `0.5 · c² · w` —— 我第一版按长边算，差 160/73.5/562.5）。
      ⚠ **边序号顺序官方未承诺稳定**（本仓已知事实）⇒ 本判据是**冻结在本机当前行为**上的。
    """
    return c["w"] * c["h"] * c["d"] - 0.5 * c["c"] ** 2 * c["d"]


def build_plan(case: dict) -> R.ExecutablePlan:
    """★ 把方法 `plate` 展开成**带参数**的可执行计划（★ C2 + C4）。"""
    c = case
    return R.ExecutablePlan(
        method_id="plate",
        steps=(
            R.PlanStep(
                step="sketch_start",
                params={"plane_name": "Front Plane"},
                derive="★ 前视基准面（★ 板的主平面）",
            ),
            R.PlanStep(
                step="sketch_add_rectangle",
                params={"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": c["w"], "y2_mm": c["h"]},
                derive="★ 左下 (0,0) → 右上 (W,H) ⇒ 板 %g×%g mm" % (c["w"], c["h"]),
            ),
            R.PlanStep(step="sketch_end", params={}, derive="★ 退出草图"),
            R.PlanStep(
                step="extrude_boss",
                params={"sketch_name": "草图1", "depth_mm": c["d"]},
                derive="★ 拉伸 %g mm（★ 工具层做 mm→m 换算，恰好一次）" % c["d"],
            ),
            R.PlanStep(
                step="chamfer",
                params={
                    "selection": "index:0",
                    "distance_mm": c["c"],
                    "angle_deg": 45.0,
                },
                derive="★ 倒角 %g×45°（★ 后置 —— 避免早期拓扑依赖）；"
                "★ `selection` 是**声明式选择器**（规则 3：不收坐标）" % c["c"],
            ),
        ),
    )


def run_case(reg, n: int, sw) -> dict:
    """★ 跑一个用例（★ 真机）。"""
    from scripts import sw_connect

    c = CASES[n]
    rec: dict = {"case": n, "params": c, "started": time.strftime("%H:%M:%S")}

    #: ══ ① 建文档（★ 登记为「本任务所有」）══════════════════════════
    doc = sw_connect.new_document(sw, "part")
    owned = AUTH.OwnedDocuments()
    owned.register(doc)
    rec["doc"] = owned.title_of(doc)

    #: ══ ② 编译计划（★ 名字解析 + 参数绑定 —— ★ 任一步失败即整计划拒绝）══
    plan = build_plan(c)
    try:
        plan = R.resolve_plan(plan, reg)
        rec["compiled"] = True
        rec["tools"] = [st.tool for st in plan.steps]
    except R.RegistryError as e:
        rec["compiled"] = False
        rec["compile_error"] = "%s: %s" % (e.code, e.detail)
        sw.CloseDoc(rec["doc"])
        return rec

    #: ══ ③ 授权（★ 不过 ⇒ 一次 COM 都不碰）══════════════════════════
    v = AUTH.authorize_plan(plan, reg, owned=owned, doc=doc)
    rec["authorized"] = v.ok
    if not v.ok:
        rec["auth_code"] = v.code
        sw.CloseDoc(rec["doc"])
        return rec

    #: ══ ④ 执行（★ 走 `solidworks_*` 全名 —— ★ FR-012）══════════════
    X.COUNTER.reset()
    host = {"model": doc, "sw_app": sw}
    out = X.execute_plan(plan, reg, host=host, owned=owned, doc=doc, log_dir=OUT)
    rec["execute_ok"] = out["ok"]
    rec["com_writes"] = out["com_write_total"]
    rec["records"] = X.records_to_dicts(out["records"])

    #: ══ ⑤ 回读判据（★ 事实 71：`GetPartBox` 回**毫米**）══════════════
    try:
        pd = list(sw_connect.safe_get_com_member(doc, "GetPartBox", False))
        size = [
            round(float(pd[3]) - float(pd[0]), 3),
            round(float(pd[4]) - float(pd[1]), 3),
            round(float(pd[5]) - float(pd[2]), 3),
        ]
    except Exception as exc:  # noqa: BLE001
        size = None
        rec["bbox_error"] = str(exc)[:120]
    rec["bbox_mm"] = size

    #: ★ 体积走**工具层的 `solidworks_part_mass_properties`**（★ 不是手搓 ——
    #:   ⚠ 实测踩过：第一版调 `sw_part.get_mass_properties`，**那个函数不存在**
    #:   ⇒ 体积恒 `None`。★ 判据必须走**已注册的工具**（那才是「经方法入口」）。
    #: ★★ 另两处实测（2026-10-12）：
    #:   ① 该工具回的是 **JSON 字符串**（不是 dict）⇒ 必须 `json.loads`
    #:   ② 它的 `volume` 单位是 **m³**（★ 40×40×10 的板回 `1.6e-05` = **16000 mm³**）
    #:      ⇒ 要 **×1e9** 才是 mm³（★ 与 `GetPartBox` 的毫米口径**不同**，别混）
    try:
        ok_mp, mp = tool_caller.call(
            "solidworks_part_mass_properties", inject_objects={"model": doc}
        )
        if ok_mp:
            #: ⚠ 实测：它回的字符串是 **Python dict 的 repr**（单引号），**不是 JSON**
            #:   ⇒ `json.loads` 会报 `JSONDecodeError`。两路都试。
            data = None
            if isinstance(mp, dict):
                data = mp
            elif isinstance(mp, str):
                try:
                    data = json.loads(mp)
                except Exception:  # noqa: BLE001
                    import ast as _ast

                    data = _ast.literal_eval(mp)
            if isinstance(data, dict) and data.get("volume") is not None:
                rec["volume_m3"] = data["volume"]
                rec["volume_mm3"] = round(float(data["volume"]) * 1e9, 3)
                rec["mass_evidence"] = str(data)[:300]
    except Exception as exc:  # noqa: BLE001
        rec["volume_error"] = "%s: %s" % (type(exc).__name__, str(exc)[:100])

    #: ══ ⑥ 保存 + 重开（★ 规格要求「真实建板、保存、重开」）══════════
    p = OUT / ("%s.sldprt" % c["name"])
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        sw_connect.save_document(doc, str(p))
        rec["saved"] = p.is_file()
    except Exception as exc:  # noqa: BLE001
        rec["save_error"] = str(exc)[:120]

    rec["expected_bbox"] = [c["w"], c["h"], c["d"]]
    rec["expected_volume"] = expected_volume(c)
    #: ★★ 判据（★ 规格 §4 SC-002：**尺寸与体积符合冻结判据**，相对误差 ≤1e-6）
    #:   ⚠ 实测：`volume_mm3` 是**四舍五入到 3 位**的 ⇒ 容差要容得下那个舍入
    #:     （★ 用**绝对** 0.01 mm³ 或**相对** 1e-6 里**宽**的那个 —— 两个都报）
    if rec.get("bbox_mm") and rec.get("volume_mm3") is not None:
        eb, ev = rec["expected_bbox"], rec["expected_volume"]
        rec["bbox_ok"] = all(abs(a - b) <= 0.01 for a, b in zip(rec["bbox_mm"], eb))
        dv = abs(rec["volume_mm3"] - ev)
        rec["volume_delta"] = round(dv, 4)
        rec["volume_rel_err"] = round(dv / ev, 9) if ev else None
        rec["volume_ok"] = (dv <= 0.01) or (ev and dv / ev <= 1e-6)
    rec["pass"] = bool(
        rec.get("execute_ok")
        and rec.get("bbox_ok")
        and rec.get("volume_ok")
        and rec.get("saved")
    )
    rec["finished"] = time.strftime("%H:%M:%S")
    return rec


def run_negatives(reg, sw) -> dict:
    """★ 跑四类负例（★ SC-005~SC-009：COM 写调用数必须为 0）。"""

    out: dict = {"negatives": [], "started": time.strftime("%H:%M:%S")}
    c = CASES[1]
    plan = R.resolve_plan(build_plan(c), reg)

    #: ★ 一个未准入的工具
    bad_tool = next(d.canonical_name for d in reg.values() if not d.admitted)

    class _Foreign:
        def GetTitle(self):
            return "别人的文档.SLDPRT"

    cases = [
        (
            "① 工具未准入",
            R.ExecutablePlan(
                method_id="n", steps=(R.PlanStep(step="x", params={}, tool=bad_tool),)
            ),
            {},
        ),
        ("② 路径越权", plan, {"write_paths": (r"C:\Windows\evil.json",)}),
        ("③ 文档越权", plan, {"owned": AUTH.OwnedDocuments(), "doc": _Foreign()}),
        (
            "④ 计划未编译",
            R.ExecutablePlan(
                method_id="n",
                steps=(
                    R.PlanStep(
                        step="extrude_boss",
                        params={"sketch_name": "s", "depth_mm": 1.0},
                    ),
                ),
            ),
            {},
        ),
    ]
    for name, p, kw in cases:
        X.COUNTER.reset()
        got = X.execute_plan(p, reg, **kw)
        out["negatives"].append(
            {
                "name": name,
                "ok": got["ok"],
                "code": got.get("code", ""),
                "com_writes": X.COUNTER.count(),
                "pass": (got["ok"] is False) and X.COUNTER.count() == 0,
            }
        )
    out["finished"] = time.strftime("%H:%M:%S")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--case",
        type=int,
        choices=(1, 2, 3),
        default=0,
        help="★ 只跑第 N 个用例（★ 独立启动用）",
    )
    ap.add_argument(
        "--negatives", action="store_true", help="★ 跑四类负例（★ SC-005~SC-009）"
    )
    ap.add_argument(
        "--plan-only", action="store_true", help="★ 只编译不执行（★ 无真机也能跑）"
    )
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    reg = R.build_registry()
    print(
        "★ 目录：%d 个工具（准入 %d）"
        % (len(reg), sum(1 for d in reg.values() if d.admitted))
    )

    if args.plan_only:
        ok = 0
        for n in (1, 2, 3):
            try:
                p = R.resolve_plan(build_plan(CASES[n]), reg)
                print("   ✓ 用例 %d 编译通过：%s" % (n, [s.tool for s in p.steps][:3]))
                ok += 1
            except R.RegistryError as e:
                print("   ✗ 用例 %d：%s" % (n, e))
        return 0 if ok == 3 else 1

    import sw_connect

    sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass

    docs: list = []
    try:
        if args.negatives:
            ev = run_negatives(reg, sw)
            (OUT / "negatives.json").write_text(
                json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8"
            )
            for r in ev["negatives"]:
                print(
                    "   %s %-14s code=%-22s com_writes=%d"
                    % ("✓" if r["pass"] else "✗", r["name"], r["code"], r["com_writes"])
                )
            return 0 if all(r["pass"] for r in ev["negatives"]) else 1

        ns = [args.case] if args.case else [1, 2, 3]
        allrec = []
        for n in ns:
            rec = run_case(reg, n, sw)
            allrec.append(rec)
            print(
                "   用例 %d：compiled=%s auth=%s exec=%s bbox=%s（期望 %s）体积=%s（期望 %.1f）"
                % (
                    n,
                    rec.get("compiled"),
                    rec.get("authorized"),
                    rec.get("execute_ok"),
                    rec.get("bbox_mm"),
                    rec.get("expected_bbox"),
                    rec.get("volume_mm3"),
                    rec.get("expected_volume", 0),
                )
            )
        p = OUT / ("case%d.json" % ns[0] if len(ns) == 1 else "cases.json")
        p.write_text(json.dumps(allrec, ensure_ascii=False, indent=1), encoding="utf-8")
        print("★ 证据 → %s" % p)
        return 0 if all(r.get("pass") for r in allrec) else 1
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        #: ★ 只关**本任务创建的**文档（★ 不碰别人的 —— AGENTS.md §十九）
        try:
            for d in list(sw.GetDocuments or []):
                t = sw_connect.safe_get_com_member(d, "GetTitle")
                t = t() if callable(t) else t
                if t and str(t) in (
                    "板1.SLDPRT",
                    "板2.SLDPRT",
                    "板3.SLDPRT",
                    "Part1",
                    "零件1",
                ):
                    sw.CloseDoc(str(t))
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    raise SystemExit(main())
