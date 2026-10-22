"""★ 规格 325 验收入口：四类协议 + check_ref + 三态决策（Q1/Q5 的 R1~R10）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/run_s325_protocols.py
# 定位:   规格 `specs/325-declarative-protocols-and-decisions` 的**验收入口**
# 官方依据: ① `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q1（L10-34）逐字② 同文件 Q5
#           （L59-94）逐字③ `metadata/protocols/*.yaml`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

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

from scripts.engineering import decisions as D  # noqa: E402
from scripts.engineering import protocols as P  # noqa: E402

OUT = ROOT / "output" / "s325"


def _dec(**kw) -> D.Decision:
    base = dict(
        proposer=D.PROPOSER_LLM,
        input_version="r1",
        alternatives=["A", "B"],
        visible_rationale="按 8mm",
        basis=["GB/T 5796"],
        affected_nodes=["上箱体"],
    )
    base.update(kw)
    return D.make_decision(**base)


def run_r() -> dict:
    """★ **R1~R10 逐条**。"""
    rows = []

    #: R1 四类协议
    allp = P.load_all()
    rows.append(
        {
            "r": "R1",
            "what": "四类协议齐",
            "ok": set(allp) == set(P.REQUIRED_PROTOCOLS),
            "got": ", ".join(sorted(allp)),
        }
    )

    #: R2 五要素
    miss = {n: p.missing_fields() for n, p in allp.items() if p.missing_fields()}
    rows.append(
        {
            "r": "R2",
            "what": "每份五要素齐",
            "ok": not miss,
            "got": "五要素齐" if not miss else str(miss),
        }
    )

    #: R3 check_ref 解析
    v = P.validate_all()
    unres = sum(len(x["unresolved"]) for x in v["protocols"])
    total = sum(len(x["check_refs"]) for x in v["protocols"])
    rows.append(
        {
            "r": "R3",
            "what": "check_ref 全解析",
            "ok": unres == 0 and total > 0,
            "got": "%d 个 · 未解析 %d" % (total, unres),
        }
    )

    #: R4 8 项必设检查
    rc_ok = all(P.run_required_checks(p)["ok"] for p in allp.values())
    rows.append(
        {
            "r": "R4",
            "what": "8 项必设检查",
            "ok": rc_ok and len(P.REQUIRED_CHECKS) == 8,
            "got": "%d 项 · 全过=%s · 第 9 项在测试层"
            % (len(P.REQUIRED_CHECKS), rc_ok),
        }
    )

    #: R5 重生成三视图
    rg = P.regenerate_all()
    three = all(x["document"] and x["prompt"] and x["catalog"] for x in rg.values())
    rows.append(
        {
            "r": "R5",
            "what": "改一处 ⇒ 三视图重生成",
            "ok": three and len(rg) == 4,
            "got": "%d 份 · 三样齐=%s" % (len(rg), three),
        }
    )

    #: R6 decision_id 五要素
    d = _dec()
    rows.append(
        {
            "r": "R6",
            "what": "decision_id + 五要素",
            "ok": bool(d.decision_id) and not d.missing(),
            "got": "%s · 五要素齐" % d.decision_id,
        }
    )

    #: R7 三态
    d2 = _dec()
    jump = D.promote(d2, D.APPROVED, by=D.PROPOSER_HUMAN)
    llm = D.promote(
        d2, D.VALIDATED, by=D.PROPOSER_LLM, code_verdict={"verdict": "PASS"}
    )
    code = D.promote(
        d2, D.VALIDATED, by=D.PROPOSER_CODE, code_verdict={"verdict": "PASS"}
    )
    human = D.promote(d2, D.APPROVED, by=D.PROPOSER_HUMAN)
    rows.append(
        {
            "r": "R7",
            "what": "三态且 LLM 不能自升",
            "ok": (not jump.ok) and (not llm.ok) and code.ok and human.ok,
            "got": "跳级=%s LLM自升=%s 代码=%s 人=%s"
            % (jump.code, llm.code, code.ok, human.ok),
        }
    )

    #: R8 字段门禁
    g = P.field_gate(allp["requirement"], {"requirement_text": "x"})
    g2 = P.field_gate(
        allp["requirement"], {"requirement_text": "x", "worst_case_load": "999kN"}
    )
    rows.append(
        {
            "r": "R8",
            "what": "缺需求先问 · 最坏工况不顶替",
            "ok": g["state"] == "WAITING_INPUT" and g2["state"] == "WAITING_INPUT",
            "got": "缺⇒%s · 给最坏工况⇒%s" % (g["state"], g2["state"]),
        }
    )

    #: R9 同错两次 ⇒ 诊断
    t = D.SameErrorTrigger()
    t.observe("E1")
    trig = t.observe("E1")
    rows.append(
        {
            "r": "R9",
            "what": "同错两次 ⇒ 诊断（不判根因）",
            "ok": trig["triggered"]
            and trig["action"] == "DIAGNOSIS_REQUIRED"
            and "root_cause" not in t.to_dict(),
            "got": "触发=%s · 根因字段在=%s"
            % (trig["triggered"], "root_cause" in t.to_dict()),
        }
    )

    #: R10 改 YAML 不能获得新能力
    bad = P.resolve_check_ref("never_implemented@1")
    rows.append(
        {
            "r": "R10",
            "what": "只改 YAML 不得获得新能力",
            "ok": bad.resolved is False,
            "got": bad.reason[:40],
        }
    )

    return {"rows": rows, "ok": all(r["ok"] for r in rows)}


def run_x() -> dict:
    """★ **X1~X8 反向验证**。"""
    rows = []

    #: X1 跳级
    p1 = D.promote(_dec(), D.APPROVED, by=D.PROPOSER_HUMAN)
    rows.append(
        {
            "x": "X1",
            "what": "Proposal 直接 Approved",
            "ok": (not p1.ok) and p1.code == "illegal-transition",
            "got": p1.code,
        }
    )

    #: X2 LLM 自升
    p2 = D.promote(
        _dec(), D.VALIDATED, by=D.PROPOSER_LLM, code_verdict={"verdict": "PASS"}
    )
    rows.append(
        {
            "x": "X2",
            "what": "LLM 自评就能 Validated",
            "ok": (not p2.ok) and p2.code == "not-authorized",
            "got": p2.code,
        }
    )

    #: X3 check_ref 指向不存在
    P.CHECK_REGISTRY["bogus@1"] = ("engineering.protocols", "nope")
    try:
        r3 = P.resolve_check_ref("bogus@1")
    finally:
        del P.CHECK_REGISTRY["bogus@1"]
    rows.append(
        {
            "x": "X3",
            "what": "check_ref 指向不存在",
            "ok": r3.resolved is False,
            "got": r3.reason[:40],
        }
    )

    #: X4 协议里塞 eval
    pr = P.load_protocol("layout")
    pr.extra["sneaky"] = "eval('1+1')"
    v4 = P.validate_protocol(pr)
    rows.append(
        {
            "x": "X4",
            "what": "协议里塞 eval",
            "ok": bool(v4["forbidden"]),
            "got": "检出 %d 处" % len(v4["forbidden"]),
        }
    )

    #: X5 只改 YAML 加检查
    pr5 = P.load_protocol("requirement")
    pr5.checks = list(pr5.checks) + ["brand_new@1"]
    v5 = P.validate_protocol(pr5)
    rows.append(
        {
            "x": "X5",
            "what": "只改 YAML 加新检查",
            "ok": "brand_new@1" in v5["unresolved"],
            "got": "未解析 %s" % v5["unresolved"],
        }
    )

    #: X6 缺必填却继续
    g6 = P.field_gate(P.load_protocol("scheme_gate"), {})
    rows.append(
        {
            "x": "X6",
            "what": "缺必填却继续",
            "ok": g6["state"] == "WAITING_INPUT",
            "got": g6["state"],
        }
    )

    #: X7 两次同错却重试
    o7 = D.check_same_error(["E1", "E1"])
    rows.append(
        {
            "x": "X7",
            "what": "两次同错却重试",
            "ok": o7["triggered"] == ["E1"],
            "got": o7["last"]["action"],
        }
    )

    #: X8 最坏工况当默认值
    g8 = P.field_gate(P.load_protocol("requirement"), {"worst_case_load": "999kN"})
    rows.append(
        {
            "x": "X8",
            "what": "最坏工况当默认值",
            "ok": g8["state"] == "WAITING_INPUT"
            and "worst_case_load" in g8["used_forbidden_defaults"],
            "got": "%s · 禁用项 %s" % (g8["state"], g8["used_forbidden_defaults"]),
        }
    )

    return {"rows": rows, "ok": all(r["ok"] for r in rows)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    r = run_r()
    x = run_x()

    print("★ R1~R10：")
    for row in r["rows"]:
        print(
            "   %s %-4s %-30s ⇒ %s"
            % ("✓" if row["ok"] else "✗", row["r"], row["what"], str(row["got"])[:48])
        )
    print()
    print("★ X1~X8 反向验证：")
    for row in x["rows"]:
        print(
            "   %s %-4s %-28s ⇒ %s"
            % ("✓" if row["ok"] else "✗", row["x"], row["what"], str(row["got"])[:46])
        )

    ev = {"r": r, "x": x, "finished": time.strftime("%H:%M:%S")}
    p = OUT / "protocols.json"
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print(
        "★ R：%s · X：%s" % ("过" if r["ok"] else "不过", "过" if x["ok"] else "不过")
    )
    print("★ 证据 → %s" % p)
    return 0 if (r["ok"] and x["ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
