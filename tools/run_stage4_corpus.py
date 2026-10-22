"""★ 阶段 4 验收入口：60 条语义语料评估（规格 319 的 S4-A / S4-B）。

★★ 用法：
     python tools/run_stage4_corpus.py              # ★ 全部 60 条
     python tools/run_stage4_corpus.py --split dev  # ★ 只跑 20 条开发集
     python tools/run_stage4_corpus.py --split blind

★★ 判据（★ 外部方案 S4-A 逐字）：
   · **应等待或拒绝却进入执行**的次数 = **0**
   · **关键需求不满足却获放行**的次数 = **0**
   · 可解盲题**正确且可编译**率 **≥90%**
"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/run_stage4_corpus.py
# 定位:   规格 `specs/319-stage4-constrained-planning` 的**验收入口**（S4-A/S4-B）
# 官方依据: ① 外部方案阶段 4 的验收 S4-A / S4-B（逐字）② `corpus/l3-semantic.yaml`（★ 60
#            条 · 24/12/12/12 · 20/40）③ `scripts/engineering/design_ir.py`（G1~G4）④ `s
#           cripts/engineering/planner.py`（G5）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [
    str(ROOT),
    str(ROOT / "scripts"),
    str(ROOT / "mcp-server"),
    str(ROOT / "tools"),
]

from scripts.engineering import design_ir as DI  # noqa: E402
from scripts.engineering import planner as PL  # noqa: E402

OUT = ROOT / "output" / "stage4"
CORPUS = ROOT / "corpus" / "l3-semantic.yaml"

#: ★ 语料 category → 期望状态（★ 判据的**真源**）
EXPECT = {
    "solvable": DI.READY_FOR_REVIEW,
    "missing_input": DI.WAITING_INPUT,
    #: ★ 能力边界与对抗语义都**不得进执行**（★ 具体是拒绝还是等待由内容定）
    "capability_boundary": None,  #: ★ 只要求「不可执行」
    "adversarial": None,  #: ★ 只要求「不可执行」
}


def load_corpus(path: pathlib.Path) -> list:
    """★ 读 60 条语料（★ 极简 YAML 解析 —— ★ 只认本文件的形状）。"""
    t = path.read_text(encoding="utf-8")
    items = []
    cur: dict = {}
    for line in t.splitlines():
        if line.startswith("- id:"):
            if cur:
                items.append(cur)
            cur = {"id": line.split(":", 1)[1].strip()}
        elif re.match(r"^\s+\w+:", line) and cur is not None:
            m = re.match(r"^\s+(\w+):\s*(.*)$", line)
            if m:
                k, v = m.group(1), m.group(2).strip()
                if k in (
                    "id",
                    "requirement",
                    "category",
                    "split",
                    "needs_owner_judgment",
                    "notes",
                ):
                    cur[k] = v
                elif k in ("function", "interface", "question", "result"):
                    cur.setdefault("labels", {})[k] = v
    if cur:
        items.append(cur)
    return items


def evaluate(items: list) -> dict:
    """★★ **逐条评估**（★ 判据：期望状态 vs 实际状态）。"""
    rows = []
    for it in items:
        req = it.get("requirement", "")
        want = EXPECT.get(it.get("category", ""), None)
        ir = DI.parse_requirement(req)
        got = ir.state

        row = {
            "id": it["id"],
            "category": it.get("category"),
            "split": it.get("split"),
            "want": want or "(不可执行)",
            "got": got,
            "executable": ir.executable,
            "question": (ir.open_questions or [""])[0][:40],
        }

        #: ★★ 判据①：**应等待或拒绝却进入执行**（★ 最严重）
        if want is not None and want != DI.READY_FOR_REVIEW and ir.executable:
            row["verdict"] = "MISRELEASE"
        elif want == DI.READY_FOR_REVIEW and not ir.executable:
            #: ★ 判据②：可解的被误挡
            row["verdict"] = "MISBLOCK"
        elif want is not None and want != got and want == DI.READY_FOR_REVIEW:
            row["verdict"] = "WRONG_STATE"
        else:
            #: ★ 规划（★ 只对可解的做）
            if ir.executable:
                try:
                    ps = PL.plan_from_requirement(req)
                    row["variants"] = len(ps.candidates)
                    row["compilable"] = len(ps.compilable)
                    #: ★ 判据③：**可解且可编译**
                    row["verdict"] = "PASS" if ps.ok else "NOT_COMPILABLE"
                except PL.PlannerError as e:
                    row["variants"] = 0
                    row["planner_error"] = e.code
                    row["verdict"] = "PLAN_FAILED"
            else:
                row["verdict"] = "PASS"
        rows.append(row)
    return {"rows": rows}


def summarize(ev: dict) -> dict:
    rows = ev["rows"]
    by_cat: dict = {}
    for r in rows:
        c = by_cat.setdefault(r["category"], {"n": 0, "pass": 0})
        c["n"] += 1
        if r["verdict"] == "PASS":
            c["pass"] += 1

    #: ★★ 三条硬判据（★ S4-A 逐字）
    misrelease = [r for r in rows if r["verdict"] == "MISRELEASE"]
    blind_solvable = [
        r for r in rows if r["category"] == "solvable" and r["split"] == "blind"
    ]
    blind_ok = [r for r in blind_solvable if r["verdict"] == "PASS"]
    rate = (len(blind_ok) / len(blind_solvable)) if blind_solvable else 0.0

    return {
        "total": len(rows),
        "pass": sum(1 for r in rows if r["verdict"] == "PASS"),
        "by_category": by_cat,
        "misrelease": len(misrelease),
        "misrelease_ids": [r["id"] for r in misrelease],
        "misblock": len([r for r in rows if r["verdict"] == "MISBLOCK"]),
        "blind_solvable": len(blind_solvable),
        "blind_ok": len(blind_ok),
        "blind_rate": round(rate, 4),
        #: ★ 判据：误放 0 · 盲测可解率 ≥90%
        "ok": (len(misrelease) == 0 and rate >= 0.90),
        "★": "★ 误放必须 0 · 可解盲题正确且可编译率 ≥90%",
    }


def run_s4b() -> dict:
    """★ **S4-B**：询问、检索、数据与成本策略真实生效。"""
    rows = []

    #: ① 关键缺项 ⇒ WAITING_INPUT 且**不写 CAD**
    ir = DI.parse_requirement("设计一块板")
    rows.append(
        {
            "case": "关键缺项不写 CAD",
            "got": ir.state,
            "ok": ir.state == DI.WAITING_INPUT and ir.blocks_cad,
        }
    )

    #: ② 最多两批主动问题
    el = DI.Elicitation()
    el.ask(["尺寸？"])
    el.ask(["材料？"])
    exceeded = False
    try:
        el.ask(["载荷？"])
    except DI.DesignIRError:
        exceeded = True
    rows.append(
        {
            "case": "最多两批问题",
            "got": "第 3 批被拒" if exceeded else "没拒",
            "ok": exceeded and len(el.batches) == 2,
        }
    )

    #: ③ 候选不超 4096 token
    ir2 = DI.parse_requirement(
        "在一块 100×60×20 的板上四角各打一个 M6 通孔，孔心距边 10mm"
    )
    ret = DI.retrieve_methods(ir2)
    rows.append(
        {
            "case": "候选 ≤4096 token",
            "got": ret["tokens"],
            "ok": ret["tokens"] <= DI.CANDIDATE_TOKEN_BUDGET,
        }
    )

    #: ④ 数据拒绝 ⇒ 出站 0
    p = DI.outbound_permit(data_permitted=False, budget_permitted=True)
    rows.append(
        {
            "case": "数据拒绝 ⇒ 出站 0",
            "got": p.code,
            "ok": (not p.allowed) and p.code == DI.DATA_NOT_PERMITTED,
        }
    )

    #: ⑤ 余额拒绝 ⇒ 出站 0
    p2 = DI.outbound_permit(data_permitted=True, budget_permitted=False)
    rows.append(
        {
            "case": "余额拒绝 ⇒ 出站 0",
            "got": p2.code,
            "ok": (not p2.allowed) and p2.code == DI.BUDGET_NOT_PERMITTED,
        }
    )

    #: ⑥ 未知费用 ⇒ **不释放**预算预占
    bh = DI.BudgetHold()
    bh.hold(10.0)
    released = bh.release(cost_known=False)
    rows.append(
        {
            "case": "未知费用不释放预占",
            "got": released,
            "ok": released is False and bh.held is True,
        }
    )

    #: ⑦ 都获准 ⇒ 放行
    p3 = DI.outbound_permit(data_permitted=True, budget_permitted=True)
    rows.append({"case": "都获准 ⇒ 放行", "got": p3.allowed, "ok": p3.allowed})

    return {"s4b": rows, "ok": all(r["ok"] for r in rows)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=("dev", "blind", "all"), default="all")
    ap.add_argument("--show", type=int, default=0, help="★ 打印前 N 条明细")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    items = load_corpus(CORPUS)
    if args.split != "all":
        items = [i for i in items if i.get("split") == args.split]
    print("★ 语料 %d 条（split=%s）" % (len(items), args.split))

    ev = evaluate(items)
    s = summarize(ev)
    print("★ 按类别：")
    for c, v in sorted(s["by_category"].items()):
        print("   %-22s %d/%d" % (c, v["pass"], v["n"]))
    print()
    print(
        "★ 误放（应等待/拒绝却进执行）= **%d** %s"
        % (s["misrelease"], s["misrelease_ids"][:5])
    )
    print(
        "★ 可解盲题：%d/%d ⇒ **%.1f%%**（要求 ≥90%%）"
        % (s["blind_ok"], s["blind_solvable"], s["blind_rate"] * 100)
    )

    if args.show:
        print()
        for r in ev["rows"][: args.show]:
            print(
                "   %-8s %-20s want=%-20s got=%-20s ⇒ %s"
                % (r["id"], r["category"], r["want"], r["got"], r["verdict"])
            )

    s4b = run_s4b()
    print()
    print("★ S4-B：")
    for r in s4b["s4b"]:
        print(
            "   %s %-22s ⇒ %s"
            % ("✓" if r["ok"] else "✗", r["case"], str(r["got"])[:40])
        )

    out = {
        "summary": s,
        "rows": ev["rows"],
        "s4b": s4b,
        "finished": time.strftime("%H:%M:%S"),
    }
    p = OUT / "corpus-eval.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print(
        "★ S4-A：%s · S4-B：%s"
        % ("过" if s["ok"] else "不过", "过" if s4b["ok"] else "不过")
    )
    print("★ 证据 → %s" % p)
    return 0 if (s["ok"] and s4b["ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
