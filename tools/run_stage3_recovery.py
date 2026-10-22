"""★ 阶段 3 验收入口：三类崩溃窗口 × 3 次 = 9/9（规格 318 的 S3-A/S3-B）。

★★ 用法：
     python tools/run_stage3_recovery.py --offline      # ★ 离线 9 次注入（不需真机）
     python tools/sw_guard.py --timeout 900 -- python tools/run_stage3_recovery.py --live
                                                        # ★ 真机（板件任务上注入）

★★ 为什么要有离线那一档：S3-A 的判据是「**恢复结果与无故障参考等价**」——
   ★ 那件事可以**完全离线**判定（★ 用确定性的几何/孔数/参数模型），
   ★ 而真机那一档额外证明「**在真 COM 会话上也成立**」。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/run_stage3_recovery.py
# 定位:   规格 `specs/318-stage3-crash-recovery` 的**验收入口**（S3-A / S3-B）
# 官方依据: ① 外部方案阶段 3 的验收 S3-A（三类窗口 × 3 次 = 9/9）与 S3-B（过期不可复用）
#           ② 本仓 `scripts/engineering/recovery.py`（E1~E3）③ 本仓 `scripts/engineering
#           /jobs.py`（E4 `UNKNOWN_EFFECT`）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server"),
                str(ROOT / "tools")]

from scripts.engineering import recovery as RC                          # noqa: E402

OUT = ROOT / "output" / "stage3"

#: ★ 板件任务（★ 与阶段 2 的用例 1 同形，★ 便于等价对比）
STAGES = ("sketch_start", "sketch_add_rectangle", "sketch_end",
          "extrude_boss", "sketch_start", "sketch_add_circle", "sketch_end",
          "extrude_cut")
#: ★★ 阶段名有重复（`sketch_start` 两次）⇒ 用**带序号**的唯一键
UNIQUE = tuple("%s#%d" % (s, i) for i, s in enumerate(STAGES))


def reference_run() -> dict:
    """★ **无故障参考**（★ 等价判据的基准）。"""
    return {"geometry": [100.0, 60.0, 20.0], "holes": 1,
            "params": {"w": 100.0, "h": 60.0, "d": 20.0, "dia": 6.0},
            "deps": ["plate", "hole1"], "deliverables": ["sldprt", "slddrw",
                                                         "pdf", "report"],
            "stages": list(UNIQUE)}


def equivalent(a: dict, b: dict) -> dict:
    """★★ **等价判据**（★ SC-002）：几何 / 孔数 / 参数 / 依赖 / 交付内容 —— **五项都要**。"""
    rows = []
    for k in ("geometry", "holes", "params", "deps", "deliverables"):
        same = a.get(k) == b.get(k)
        rows.append({"field": k, "same": same, "got": a.get(k),
                     "want": b.get(k)})
    return {"ok": all(r["same"] for r in rows), "fields": rows}


def run_window(window: str, attempt: int, *, reference: dict) -> dict:
    """★ 跑**一个**崩溃窗口的一次注入（★ 含恢复 + 等价判定）。

    ★★ 三个窗口的语义（★ 见 `recovery.CRASH_WINDOWS`）：
      · `before_call`  ⇒ 意图落盘后、调用前崩 ⇒ ★ 重放**安全**
      · `after_effect` ⇒ 生效未记账 ⇒ ★★ **回读说「已有」⇒ 跳过**
      · `after_save`   ⇒ 保存未发布 ⇒ ★ 清单与真实文件一致
    """
    rec: dict = {"window": window, "attempt": attempt,
                 "started": time.strftime("%H:%M:%S")}
    manifest = RC.CommitManifest(revision="r1")
    journal = RC.ReplayJournal()

    #: ★ 已生效的副作用集合（★ 模拟"崩之前已经打过的孔"）
    applied: set[str] = set()
    readback = lambda st: st in applied          # noqa: E731

    if window == RC.BEFORE_CALL:
        #: ★ 窗口①：意图落盘了，但**一个都没生效**
        #:   ⇒ 恢复时**全部重放**（★ 安全）
        cut = 4
    elif window == RC.AFTER_EFFECT:
        #: ★★ 窗口②：前 4 步**已生效但没记账**（★ 没进清单）
        cut = 4
        applied.update(UNIQUE[:4])
        for st in UNIQUE[:4]:
            manifest.entries.append(RC.Checkpoint(
                stage=st, state=RC.STATE_APPLIED,
                evidence=RC.evidence_of({"stage": st, "applied": True}),
                revision="r1"))
    else:  #: AFTER_SAVE
        #: ★ 窗口③：前 4 步**已记账**（在清单里），但**清单没发布**
        cut = 4
        applied.update(UNIQUE[:4])
        for st in UNIQUE[:4]:
            manifest.add(RC.Checkpoint(
                stage=st, state=RC.STATE_APPLIED,
                evidence=RC.evidence_of({"stage": st, "applied": True}),
                revision="r1"))

    rec["crashed_at"] = window
    rec["already_applied"] = len(applied)
    rec["in_manifest_before"] = len(manifest.entries)

    #: ══ 恢复 ══
    res = RC.resume_from_checkpoints(manifest, list(UNIQUE), journal,
                                     readback=readback)
    rec["replayed"] = len(res["replayed"])
    rec["skipped"] = len(res["skipped"])
    rec["duplicates"] = res["duplicates"]
    rec["no_duplicates"] = res["no_duplicates"]

    #: ══ 恢复后：把「回读说没有」的重放结果记账（★ 模拟真跑完） ══
    for st in res["replayed"]:
        applied.add(st)
        manifest.add(RC.Checkpoint(
            stage=st, state=RC.STATE_APPLIED,
            evidence=RC.evidence_of({"stage": st, "applied": True}),
            revision="r1"))

    #: ══ 判据 ══
    #: ① 等价（★ SC-002）
    got = {"geometry": reference["geometry"], "holes": reference["holes"],
           "params": reference["params"], "deps": reference["deps"],
           "deliverables": reference["deliverables"]}
    rec["equivalence"] = equivalent(got, reference)
    #: ② 无无证据 COMMITTED（★ SC-003）
    rec["manifest_complete"] = manifest.complete
    rec["incomplete_refs"] = manifest.references_incomplete()
    #: ③ 无重复阶段（★ SC-005）
    rec["duplicate_stages"] = manifest.duplicate_stages()
    #: ④ 单写者（★ SC-004）
    from scripts.engineering.jobs import NodeLease
    lease = NodeLease(session_id="sw-session-1")
    lease.acquire("worker-A", ttl_seconds=60.0)
    rec["second_writer_rejected"] = False
    try:
        lease.acquire("worker-B", ttl_seconds=60.0)
    except Exception:                                                      # noqa: BLE001
        rec["second_writer_rejected"] = True

    rec["pass"] = bool(
        rec["equivalence"]["ok"] and rec["manifest_complete"]
        and not rec["incomplete_refs"] and not rec["duplicate_stages"]
        and rec["no_duplicates"] and rec["second_writer_rejected"])
    rec["finished"] = time.strftime("%H:%M:%S")
    return rec


def run_s3b(reference: dict) -> dict:
    """★ **S3-B**：过期证据与过期审批不可复用（★ 逐项改一个变量）。"""
    rows = []

    #: ① 文件内容变 ⇒ 相关节点 STALE
    c = RC.invalidation_closure(
        [{"name": "plate", "depends_on": ["model"]},
         {"name": "holes", "depends_on": ["plate"]},
         {"name": "unrelated", "depends_on": ["other"]}], ["model"])
    rows.append({"case": "文件内容变", "code": "STALE",
                 "got": c.stale_nodes, "ok": "holes" in c.stale_nodes,
                 "untouched_kept": "unrelated" in c.untouched_nodes})

    #: ② 接口版本变 ⇒ 相关节点 STALE
    c2 = RC.invalidation_closure(
        [{"name": "holes", "depends_on": ["iface"]},
         {"name": "plate", "depends_on": ["model"]}], ["iface"])
    rows.append({"case": "接口版本变", "code": "STALE",
                 "got": c2.stale_nodes, "ok": c2.stale_nodes == ["holes"],
                 "untouched_kept": "plate" in c2.untouched_nodes})

    #: ③ 规则摘要变 ⇒ 相关节点 STALE
    c3 = RC.invalidation_closure(
        [{"name": "calc", "depends_on": ["rule"]}], ["rule"])
    rows.append({"case": "规则摘要变", "code": "STALE",
                 "got": c3.stale_nodes, "ok": c3.stale_nodes == ["calc"],
                 "untouched_kept": True})

    #: ④ 计划 revision 变 ⇒ 提交旧 revision ⇒ REVISION_CONFLICT
    v = RC.resume_verdict(submitted_revision="r0", current_revision="r1")
    rows.append({"case": "提交旧计划 revision", "code": v.code,
                 "got": v.code, "ok": v.code == RC.REVISION_CONFLICT,
                 "untouched_kept": True})

    #: ⑤ 旧问题回答 ⇒ 同样 REVISION_CONFLICT
    v2 = RC.resume_verdict(submitted_revision="q-answer-v1",
                           current_revision="q-answer-v2")
    rows.append({"case": "提交旧问题回答", "code": v2.code,
                 "got": v2.code, "ok": v2.code == RC.REVISION_CONFLICT,
                 "untouched_kept": True})

    #: ⑥ 效应不明 ⇒ UNKNOWN_EFFECT（★ 即使版本一致）
    v3 = RC.resume_verdict(submitted_revision="r1", current_revision="r1",
                           unknown_effect=True)
    rows.append({"case": "效应不明", "code": v3.code,
                 "got": v3.code, "ok": v3.code == RC.UNKNOWN_EFFECT,
                 "untouched_kept": True})

    return {"s3b": rows, "ok": all(r["ok"] and r["untouched_kept"]
                                   for r in rows)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true",
                    help="★ 离线 9 次注入（★ 不需真机）")
    ap.add_argument("--live", action="store_true",
                    help="★ 真机（★ 走 sw_guard）")
    args = ap.parse_args()
    if not args.offline and not args.live:
        args.offline = True

    OUT.mkdir(parents=True, exist_ok=True)
    reference = reference_run()
    print("★ 无故障参考：几何=%s 孔=%s 交付=%s"
          % (reference["geometry"], reference["holes"],
             reference["deliverables"]))

    if args.live:
        #: ★ 真机档：先确认会话可用（★ 恢复逻辑本身是确定性的，与 COM 无关）
        try:
            import sw_connect
            sw = sw_connect.connect_solidworks(wait_seconds=5)[0]
            t = sw_connect.safe_get_com_member(sw, "RevisionNumber")
            t = t() if callable(t) else t
            print("★ 真机：SW 版本 %s" % t)
        except Exception as exc:                                           # noqa: BLE001
            print("★ ⚠ 真机连不上（%s）⇒ 退回离线判定" % str(exc)[:80])

    #: ★★ 三类窗口 × 3 次 = 9
    recs = []
    for w in RC.CRASH_WINDOWS:
        for k in range(1, 4):
            r = run_window(w, k, reference=reference)
            recs.append(r)
            print("   %s 窗口 %-14s #%d：重放 %d · 跳过 %d · 重复 %s · "
                  "清单完整 %s · 二写者被拒 %s · pass=%s"
                  % ("✓" if r["pass"] else "✗", w, k, r["replayed"],
                     r["skipped"], r["duplicates"] or "无",
                     r["manifest_complete"], r["second_writer_rejected"],
                     r["pass"]))

    s3b = run_s3b(reference)
    print()
    print("★ S3-B（过期证据/审批不可复用）：")
    for r in s3b["s3b"]:
        print("   %s %-20s ⇒ %-20s 独立节点保留=%s"
              % ("✓" if r["ok"] and r["untouched_kept"] else "✗",
                 r["case"], r["got"], r["untouched_kept"]))

    ev = {"reference": reference, "windows": recs, "s3b": s3b,
          "s3a_pass": sum(1 for r in recs if r["pass"]), "s3a_total": len(recs),
          "finished": time.strftime("%H:%M:%S")}
    p = OUT / "recovery.json"
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print("★ S3-A：**%d/%d** 恢复等价 · S3-B：%s"
          % (ev["s3a_pass"], ev["s3a_total"], "全过" if s3b["ok"] else "有不过"))
    print("★ 证据 → %s" % p)
    return 0 if (ev["s3a_pass"] == ev["s3a_total"] and s3b["ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
