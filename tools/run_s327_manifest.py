"""★ 规格 327 验收入口：发布清单 + 规则取证 + 落点持久化（Q12/Q13/Q14）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/run_s327_manifest.py
# 定位:   规格 `specs/327-release-manifest-rules-and-runs` 的**验收入口**
# 官方依据: ① `output/PROJECT_STATUS_REVIEW_CONTINUATION.md` Q12（L214-231）逐字② 同文件
#            Q13（L233-259）· Q14（L261-297）逐字
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

from scripts.engineering import release_manifest as RM  # noqa: E402
from scripts.engineering import rule_service as RS  # noqa: E402
from scripts.engineering import runs as RN  # noqa: E402

OUT = ROOT / "output" / "s327"
RUN = "_accept-s327"


def _req(**kw) -> RS.RuleRequest:
    base = dict(
        rule_id="bolt-strength",
        rule_version=1,
        inputs=[{"name": "F", "value": 15000, "unit": "N", "source": "需求"}],
        application_context={"use": "夹具", "date": "2026-10-12"},
        required_standard_editions=["GB/T 5796-2005"],
        evidence_bundle_ref="ev-1",
    )
    base.update(kw)
    return RS.RuleRequest(**base)


def run_t() -> dict:
    """★ **T1~T15 逐条**。"""
    rows = []
    m = RM.build_manifest()

    #: T1 同一发布清单
    rows.append(
        {
            "t": "T1",
            "what": "四部分 + 合成摘要",
            "ok": not m.missing_parts() and bool(m.release_digest),
            "got": "digest=%s · 四部分 %s" % (m.release_digest[:12], sorted(m.parts)),
        }
    )

    #: T2 原子切换
    m.version = 9002
    p = RM.publish_manifest(m)
    back = RM.load_manifest(9002)
    rows.append(
        {
            "t": "T2",
            "what": "原子切换",
            "ok": back.release_digest == m.release_digest
            and not (p.parent / (".tmp-" + p.name)).exists(),
            "got": "发布 + 读回一致",
        }
    )
    p.unlink(missing_ok=True)

    #: T3 计划固定摘要
    bp = RM.bind_plan("accept", ["a"], m)
    m2 = RM.ReleaseManifest(version=2, parts=dict(m.parts))
    m2.parts["tools"] = "changed"
    m2.release_digest = RM._digest(m2.parts)
    stale = bp.check(m2)
    rows.append(
        {
            "t": "T3",
            "what": "清单变 ⇒ 旧计划拒跑",
            "ok": bp.check(m)["ok"] and stale["code"] == "stale-plan",
            "got": "一致=%s · 变了=%s" % (bp.check(m)["ok"], stale["code"]),
        }
    )

    #: T4 唯一裁决者
    try:
        RM.register_arbiter("dof_verdict", "x.y", "z")
        t4 = (False, "★ 没拒")
    except RM.ManifestError as e:
        t4 = (e.code == "multiple-arbiters", e.code)
    rows.append(
        {
            "t": "T4",
            "what": "一个性质一个裁决者",
            "ok": t4[0] and RM.check_single_arbiter()["ok"],
            "got": "%s · %d 个性质" % (t4[1], RM.check_single_arbiter()["n"]),
        }
    )

    #: T5 RuleRequest
    rows.append(
        {
            "t": "T5",
            "what": "RuleRequest 六字段",
            "ok": len(RS.REQUEST_FIELDS) == 6 and not _req().missing(),
            "got": "%d 字段" % len(RS.REQUEST_FIELDS),
        }
    )

    #: T6 RuleResult
    r6 = RS.evaluate_rule(
        _req(),
        formula_ok=True,
        applicability_ok=True,
        authority_status={"source": RS.SRC_OFFICIAL},
    )
    rows.append(
        {
            "t": "T6",
            "what": "RuleResult 八字段",
            "ok": len(RS.RESULT_FIELDS) == 8 and bool(r6.rule_code_digest),
            "got": "%d 字段 · digest=%s" % (len(RS.RESULT_FIELDS), r6.rule_code_digest),
        }
    )

    #: T7 公式与依据分开
    r7 = RS.evaluate_rule(
        _req(),
        formula_ok=True,
        applicability_ok=False,
        authority_status={"source": RS.SRC_OFFICIAL},
    )
    rows.append(
        {
            "t": "T7",
            "what": "公式能跑 ≠ 适用",
            "ok": r7.verdict == RS.NOT_APPLICABLE,
            "got": "formula_ok=True ⇒ %s" % r7.verdict,
        }
    )

    #: T8 效力来源
    r8 = RS.check_authority({"source": RS.SRC_SUMMARY})
    rows.append(
        {
            "t": "T8",
            "what": "只引摘要 ⇒ INDETERMINATE",
            "ok": r8["ok"] is False and r8["verdict"] == RS.INDETERMINATE,
            "got": r8["verdict"],
        }
    )

    #: T9 30 天新鲜度
    f9a = RS.check_freshness("2026-10-01", today="2026-10-12")
    f9b = RS.check_freshness("2026-09-01", today="2026-10-12")
    rows.append(
        {
            "t": "T9",
            "what": "30 天新鲜度",
            "ok": not f9a["stale"] and f9b["stale"],
            "got": "11 天=%s · 41 天=%s" % (f9a["stale"], f9b["stale"]),
        }
    )

    #: T10 runs 结构
    RN.init_run(RUN)
    st = RN.check_structure(RUN)
    rows.append(
        {
            "t": "T10",
            "what": "七个目录",
            "ok": st["ok"] and len(RN.RUN_SUBDIRS) == 7,
            "got": "%d 个 · 缺 %s" % (len(RN.RUN_SUBDIRS), st["missing"] or "无"),
        }
    )

    #: T11 原子写
    aw = RN.atomic_write(RN.run_dir(RUN) / "plans" / "t11.json", {"a": 1})
    rows.append(
        {
            "t": "T11",
            "what": "同卷原子重命名",
            "ok": aw["atomic"]
            and not (RN.run_dir(RUN) / "plans" / ".tmp-t11.json").exists(),
            "got": "atomic=True",
        }
    )

    #: T12 旧版本不覆盖
    RN.write_revision(RUN, "plans", "t12-rev", {"v": 1})
    try:
        RN.write_revision(RUN, "plans", "t12-rev", {"v": 2})
        t12 = (False, "★ 没拒")
    except RN.RunError as e:
        t12 = (e.code == "overwrite", e.code)
    rows.append({"t": "T12", "what": "旧版本不覆盖", "ok": t12[0], "got": t12[1]})

    #: T13 孤立暂存
    RN.write_revision(RUN, "interfaces", "t13-orphan", {"x": 1})
    ic = RN.is_complete(RUN, "interfaces/t13-orphan.json")
    rows.append(
        {
            "t": "T13",
            "what": "孤立暂存不算完成",
            "ok": ic["on_disk"] and not ic["complete"],
            "got": "在盘=%s · 被引用=%s · 完成=%s"
            % (ic["on_disk"], ic["referenced"], ic["complete"]),
        }
    )

    #: T14 四类持久化
    for k in RN.PERSISTED_KINDS:
        RN.persist(RUN, k, "t14-rev", {"kind": k})
    per = RN.check_persistence(RUN)
    rows.append(
        {
            "t": "T14",
            "what": "四类持久化",
            "ok": per["ok"] and len(RN.PERSISTED_KINDS) == 4,
            "got": "四类齐=%s" % per["ok"],
        }
    )

    #: T15 B 侧薄编排
    good = RN.thin_orchestrator(reuses_core=list(RN.SHARED_CORE[:4]), builds=[])
    bad = RN.thin_orchestrator(
        reuses_core=list(RN.SHARED_CORE[:4]), builds=["second_planning_loop"]
    )
    rows.append(
        {
            "t": "T15",
            "what": "B 侧薄编排",
            "ok": good["ok"] and not bad["ok"],
            "got": "复用 %d · 拒第二套规划循环=%s" % (good["reused_n"], not bad["ok"]),
        }
    )

    return {"rows": rows, "ok": all(r["ok"] for r in rows)}


def run_z() -> dict:
    """★ **Z1~Z6 反向验证**。"""
    rows = []
    m = RM.build_manifest()

    bp = RM.bind_plan("z1", ["a"], m)
    m2 = RM.ReleaseManifest(version=9, parts=dict(m.parts))
    m2.parts["rules"] = "changed"
    m2.release_digest = RM._digest(m2.parts)
    rows.append(
        {
            "z": "Z1",
            "what": "清单变了却让旧计划跑",
            "ok": bp.check(m2)["ok"] is False,
            "got": bp.check(m2)["code"],
        }
    )

    r2 = RS.evaluate_rule(
        _req(),
        formula_ok=True,
        applicability_ok=True,
        authority_status={"source": RS.SRC_SUMMARY},
    )
    rows.append(
        {
            "z": "Z2",
            "what": "只引摘要当效力来源",
            "ok": r2.verdict == RS.INDETERMINATE,
            "got": r2.verdict,
        }
    )

    r3 = RS.evaluate_rule(
        _req(),
        formula_ok=True,
        applicability_ok=False,
        authority_status={"source": RS.SRC_OFFICIAL},
    )
    rows.append(
        {
            "z": "Z3",
            "what": "公式跑通就判 PASS",
            "ok": r3.verdict != RS.PASS,
            "got": r3.verdict,
        }
    )

    RN.write_revision(RUN, "plans", "z4-rev", {"v": 1})
    try:
        RN.write_revision(RUN, "plans", "z4-rev", {"v": 2})
        z4 = (False, "★ 没拒")
    except RN.RunError as e:
        z4 = (e.code == "overwrite", e.code)
    rows.append({"z": "Z4", "what": "直接覆盖旧 revision", "ok": z4[0], "got": z4[1]})

    RN.write_revision(RUN, "interfaces", "z5-rev", {"x": 1})
    rows.append(
        {
            "z": "Z5",
            "what": "孤立暂存当完成",
            "ok": RN.is_complete(RUN, "interfaces/z5-rev.json")["complete"] is False,
            "got": "complete=False",
        }
    )

    z6 = RN.thin_orchestrator(
        reuses_core=list(RN.SHARED_CORE[:4]), builds=["second_state_system"]
    )
    rows.append(
        {
            "z": "Z6",
            "what": "B 侧另建一套状态",
            "ok": z6["ok"] is False,
            "got": "拒 %s" % z6["forbidden_built"],
        }
    )

    return {"rows": rows, "ok": all(r["ok"] for r in rows)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    t = run_t()
    z = run_z()

    print("★ T1~T15：")
    for r in t["rows"]:
        print(
            "   %s %-4s %-26s ⇒ %s"
            % ("✓" if r["ok"] else "✗", r["t"], r["what"], str(r["got"])[:50])
        )
    print()
    print("★ Z1~Z6 反向验证：")
    for r in z["rows"]:
        print(
            "   %s %-4s %-26s ⇒ %s"
            % ("✓" if r["ok"] else "✗", r["z"], r["what"], str(r["got"])[:46])
        )

    ev = {"t": t, "z": z, "finished": time.strftime("%H:%M:%S")}
    p = OUT / "manifest.json"
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print(
        "★ T：%s · Z：%s" % ("过" if t["ok"] else "不过", "过" if z["ok"] else "不过")
    )
    print("★ 证据 → %s" % p)
    return 0 if (t["ok"] and z["ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
