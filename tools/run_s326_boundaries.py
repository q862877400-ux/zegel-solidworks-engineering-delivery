"""★ 规格 326 验收入口：问题持久化 + DoD 边界 + 止损关口 + 运行边界（S1~S19）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/run_s326_boundaries.py
# 定位:   规格 `specs/326-question-persistence-and-boundaries` 的**验收入口**
# 官方依据: ① `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q8（L163-174）逐字② 同文件 
#           Q9（L176-199）· Q11（L201-212）· Q15（L299-327）逐字③ `metadata/scope-v1.jso
#           n`
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server"),
                str(ROOT / "tools")]

from scripts.engineering import boundaries as B                          # noqa: E402
from scripts.engineering import questions as Q                           # noqa: E402
from scripts.engineering import scope as S                               # noqa: E402

OUT = ROOT / "output" / "s326"


def _q(**kw) -> Q.Question:
    base = dict(run_id="accept-run", requirement_revision="rev-1",
                field_name="load_upper", value_schema="number", unit="N",
                reason="缺载荷上界")
    base.update(kw)
    return Q.make_question(**base)


def run_s() -> dict:
    """★ **S1~S19 逐条**。"""
    rows = []

    #: ── Q8
    q = _q()
    rows.append({"s": "S1", "what": "问题对象 11 字段",
                 "ok": len(Q.QUESTION_FIELDS) == 11 and not q.missing(),
                 "got": "%d 字段 · 缺 %s" % (len(Q.QUESTION_FIELDS),
                                             q.missing() or "无")})
    p = Q.save_questions("accept-run", "rev-1", [_q()])
    back = Q.load_questions("accept-run", "rev-1")
    rows.append({"s": "S2", "what": "落盘读回一致",
                 "ok": p.is_file() and len(back) == 1,
                 "got": "%s · 读回 %d 条" % (p.name, len(back))})

    q3 = _q(field_name="travel_upper")
    try:
        Q.answer(q3, 1, source=Q.SRC_HUMAN)
        ok3, got3 = False, "★ 自报 human 被接受"
    except Q.QuestionError as e:
        ok3, got3 = e.code == "untrusted-human", e.code
    rows.append({"s": "S3", "what": "LLM 自报 human 不算",
                 "ok": ok3, "got": got3})

    q4 = _q(field_name="jaw_force")
    try:
        Q.apply_answer(q4, 1, source=Q.SRC_HUMAN, carried_revision="rev-0",
                       current_revision="rev-1",
                       channel_proof="local_confirm_ui")
        ok4, got4 = False, "★ 旧版本被接受"
    except Q.QuestionError as e:
        ok4, got4 = e.code == "stale-revision", e.code
    rows.append({"s": "S4", "what": "旧 revision 补答被拒",
                 "ok": ok4, "got": got4})

    w = Q.WaitingState()
    w.enter_waiting()
    rows.append({"s": "S5", "what": "等待时释放执行锁",
                 "ok": w.released, "got": "released=%s" % w.released})

    #: ── Q9
    sc = S.load_scope()
    ok6 = (sc["limits"]["max_self_made_parts"] == 10
           and sc["limits"]["max_driven_dof"] == 1
           and sc["limits"]["max_method_level_nodes"] == 100)
    rows.append({"s": "S6", "what": "v1 上界五条",
                 "ok": ok6 and S.check_scope(self_made_parts=11)["ok"] is False,
                 "got": "上界 %s" % sc["limits"]})

    rows.append({"s": "S7", "what": "不承诺清单",
                 "ok": len(sc["not_promised"]) >= 5
                       and S.check_not_promised("freeform_surface")["ok"] is False,
                 "got": "%d 类" % len(sc["not_promised"])})

    d_no = S.delivery_state(auto_done=True)
    d_yes = S.delivery_state(auto_done=True, approved_by="owner_typed")
    rows.append({"s": "S8", "what": "DELIVERED 需人工批准",
                 "ok": d_no["state"] == S.READY_FOR_REVIEW
                       and d_yes["state"] == S.DELIVERED,
                 "got": "无批准=%s · 有批准=%s" % (d_no["state"], d_yes["state"])})

    tl = S.TakeoverLedger(autonomous=5)
    tl.record("t1", hand_built=True)
    rows.append({"s": "S9", "what": "人工接管单独计数",
                 "ok": tl.autonomous_only == 5 and len(tl.taken_over) == 1,
                 "got": "自主 %d · 接管 %d" % (tl.autonomous_only,
                                               len(tl.taken_over))})

    #: ── Q11
    g2 = S.stage2_gate(passes=2)
    g4 = S.stage4_gate(attributed_rounds=2, meets_threshold=False)
    rows.append({"s": "S10", "what": "两个止损关口",
                 "ok": g2["stop"] and g4["stop"] and len(S.STOP_GATES) == 2,
                 "got": "阶段2=%s · 阶段4=%s" % (g2["action"], g4["action"])})

    ht = S.HypothesisTracker()
    for _ in range(3):
        r11 = ht.record("h1", succeeded=False)
    rows.append({"s": "S11", "what": "三次失败停补丁",
                 "ok": r11["stop_patching"],
                 "got": r11["action"]})

    pb = S.PlanB()
    rows.append({"s": "S12", "what": "Plan B",
                 "ok": pb.route(human_did=["DesignIR"])["ready"] is False
                       and pb.route(human_did=["DesignIR",
                                               "method_selection"])["ready"],
                 "got": "人工 %s · 系统 %s" % (list(pb.human_confirms),
                                               list(pb.system_does))})

    bs = S.BlindSet(blind=["b1"])
    bs.see_failure("b1")
    rows.append({"s": "S13", "what": "盲题转回开发集",
                 "ok": "b1" not in bs.blind and "b1" in bs.dev,
                 "got": "dev=%s blind=%s" % (bs.dev, bs.blind)})

    rows.append({"s": "S14", "what": "叶子方法可增长",
                 "ok": S.method_growth_policy()["allowed"]
                       and S.admit_leaf_method(has_contract=True,
                                               composable=True,
                                               verifiable=True)["admitted"],
                 "got": "allowed=True · 三门槛"})

    #: ── Q15
    tb = B.transaction_boundary()
    rows.append({"s": "S15", "what": "事务边界声明",
                 "ok": "com_undo_stack" in tb["is_not"]
                       and tb["rollback_claim"] is False,
                 "got": "★ 不是 COM 撤销栈 · 不冒称回滚"})

    m = B.current_environment_mode()
    rows.append({"s": "S16", "what": "无人值守门槛",
                 "ok": m["mode"] == "attended" and m["unattended_claim"] is False,
                 "got": "mode=%s · claim=%s" % (m["mode"], m["unattended_claim"])})

    r17 = B.can_reclaim(owned_by_this_task=False, has_owner_documents=False)
    rows.append({"s": "S17", "what": "回收只针对自有实例",
                 "ok": r17["action"] == "STOP" and r17["kill_process"] is False,
                 "got": "%s · 杀进程=%s" % (r17["action"], r17["kill_process"])})

    r18 = B.disk_gate(free_bytes=100, needed_bytes=10**9)
    rows.append({"s": "S18", "what": "磁盘不足拒开始",
                 "ok": r18["action"] == "REFUSE_START"
                       and r18["auto_delete_evidence"] is False,
                 "got": "%s · 自动清删=%s" % (r18["action"],
                                              r18["auto_delete_evidence"])})

    r19 = B.network_gate("execution_process")
    rows.append({"s": "S19", "what": "执行进程不访问公网",
                 "ok": r19["allowed"] is False,
                 "got": r19["code"]})

    return {"rows": rows, "ok": all(r["ok"] for r in rows)}


def run_y() -> dict:
    """★ **Y1~Y10 反向验证**。"""
    rows = []

    try:
        Q.answer(_q(field_name="y1"), 1, source=Q.SRC_HUMAN)
        y1 = (False, "★ 没拒")
    except Q.QuestionError as e:
        y1 = (e.code == "untrusted-human", e.code)
    rows.append({"y": "Y1", "what": "LLM 自报 human", "ok": y1[0], "got": y1[1]})

    try:
        Q.apply_answer(_q(field_name="y2"), 1, source=Q.SRC_HUMAN,
                       carried_revision="old", current_revision="new",
                       channel_proof="local_confirm_ui")
        y2 = (False, "★ 没拒")
    except Q.QuestionError as e:
        y2 = (e.code == "stale-revision", e.code)
    rows.append({"y": "Y2", "what": "旧 revision 补答", "ok": y2[0], "got": y2[1]})

    over = {k: S.check_scope(**{k: v})["ok"] for k, v in
            (("self_made_parts", 11), ("assembly_instances", 31),
             ("driven_dof", 2), ("method_level_nodes", 101))}
    rows.append({"y": "Y3", "what": "超上界四种",
                 "ok": not any(over.values()),
                 "got": "全拒=%s" % (not any(over.values()))})

    rows.append({"y": "Y4", "what": "无批准就标 DELIVERED",
                 "ok": S.delivery_state(auto_done=True)["delivered"] is False,
                 "got": S.delivery_state(auto_done=True)["state"]})

    tl = S.TakeoverLedger(autonomous=3)
    tl.record("t1", hand_built=True)
    rows.append({"y": "Y5", "what": "接管算作自主",
                 "ok": tl.autonomous_only == 3,
                 "got": "自主 %d ≠ 总 %d" % (tl.autonomous_only, tl.total)})

    ht = S.HypothesisTracker()
    for _ in range(3):
        ht.record("h1", succeeded=False)
    r6 = ht.record("h1", succeeded=False)
    rows.append({"y": "Y6", "what": "第 4 次还在打补丁",
                 "ok": r6["stop_patching"], "got": r6["action"]})

    bs = S.BlindSet(blind=["b1"])
    bs.see_failure("b1")
    rows.append({"y": "Y7", "what": "看过的盲题仍叫盲测",
                 "ok": "b1" not in bs.blind, "got": "blind=%s" % bs.blind})

    m8 = B.AttendedMode(separate_execution_identity=False,
                        business_files_readonly=True,
                        os_level_isolation=True,
                        prompt_based_isolation_only=False).evaluate()
    rows.append({"y": "Y8", "what": "无身份却宣称无人值守",
                 "ok": m8["unattended_claim"] is False,
                 "got": m8["mode"]})

    r9 = B.can_reclaim(owned_by_this_task=False, has_owner_documents=True)
    rows.append({"y": "Y9", "what": "回收非自有实例",
                 "ok": r9["action"] == "STOP" and not r9["kill_process"],
                 "got": r9["action"]})

    r10 = B.disk_gate(free_bytes=1, needed_bytes=10**9)
    rows.append({"y": "Y10", "what": "磁盘不足仍开始",
                 "ok": r10["action"] == "REFUSE_START",
                 "got": r10["action"]})

    return {"rows": rows, "ok": all(r["ok"] for r in rows)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    s = run_s()
    y = run_y()

    print("★ S1~S19：")
    for r in s["rows"]:
        print("   %s %-4s %-24s ⇒ %s" % ("✓" if r["ok"] else "✗", r["s"],
                                         r["what"], str(r["got"])[:50]))
    print()
    print("★ Y1~Y10 反向验证：")
    for r in y["rows"]:
        print("   %s %-4s %-24s ⇒ %s" % ("✓" if r["ok"] else "✗", r["y"],
                                         r["what"], str(r["got"])[:46]))

    m = B.current_environment_mode()
    print()
    print("★★ 本机运行模式（★ 如实报）：mode=%s · unattended_claim=%s"
          % (m["mode"], m["unattended_claim"]))
    print("   ★ 缺：%s" % m["missing"])

    ev = {"s": s, "y": y, "mode": m, "finished": time.strftime("%H:%M:%S")}
    p = OUT / "boundaries.json"
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print("★ S：%s · Y：%s" % ("过" if s["ok"] else "不过",
                                "过" if y["ok"] else "不过"))
    print("★ 证据 → %s" % p)
    return 0 if (s["ok"] and y["ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
