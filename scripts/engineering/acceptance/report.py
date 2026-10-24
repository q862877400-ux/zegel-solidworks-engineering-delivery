"""★ E1–E7 验收报告的汇总与渲染。

## 为什么需要这个模块

`specs/349-e1-e7-acceptance/` 交付了 10 条采集器/判定器，但它们是**彼此孤立**的：
每条只回答「我这一项如何」。而 `AGENTS.md` 的验收判据 A8 要求的是：

> 进度按 S0–S6 报：走到哪步、该步完成标准是否满足、
> **首件 E1–E7 逐条状态与证据变化**

⇒ 需要一层把 10 条 `CheckResult` 汇成「每条 E 的状态 + 失败/未测明细」。

## ★★ 三条汇总判据（不是简单数数）

① **一个 E 下有多条检查时，全部要绿** —— 拆分不放宽
   （例如 E4 = `E4.dof` + `E4.interference`）
② **`unknown` 与 `fail` 分开列** ——
   前者是「我们没测到」，后者是「测到了且不合格」。混成一个数字，
   就会把「测不了」说成「东西坏了」
③ **空集合不得判绿** —— 没检查过 ≠ 合格
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/engineering/acceptance/report.py
# 定位:   docs/ENGINEERING-PATH.md 与 AGENTS.md 判据 A8 的落地 ——
#         把 10 条孤立的 CheckResult 汇成「E1–E7 逐条状态 + 证据变化」。
#          ★ A8 逐字：「进度按 S0–S6 报：走到哪步、该步完成标准是否满足、
#            首件 E1–E7 逐条状态与证据变化」
#          ★★ 三条汇总判据：同一 E 下全部要绿（拆分不放宽）·
#            unknown 与 fail 分开列（不把「测不了」说成「东西坏了」）·
#            空集合不得判绿（没检查过 ≠ 合格）
# 官方依据: 不适用（纯 Python 层，不调 SolidWorks API）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


from __future__ import annotations

from .result import CheckResult, Status

#: ★ 七个判据的正式标识（charter 第四节）
CRITERIA = ("E1", "E2", "E3", "E4", "E5", "E6", "E7")

#: ★ 每个判据的中文名（报告里用人看得懂的话）
CRITERIA_NAMES = {
    "E1": "草图全约束",
    "E2": "参数化可重建",
    "E3": "特征树可编辑",
    "E4": "装配自由度闭合",
    "E5": "图样合规",
    "E6": "工艺可行",
    "E7": "结论可溯源",
}


def _criterion_of(check_id: str) -> str:
    """★ 从 `check_id` 取判据标识：`E4.dof` → `E4`。"""
    return str(check_id).split(".", 1)[0]


def build_report(checks: list) -> dict:
    """★ 把一组 `CheckResult` 汇成 E1–E7 报告。

    返回结构：
      ```
      {
        "criteria": {
          "E1": {"checks": [...], "status": "pass|fail|unknown|not_checked",
                 "failed": [...], "unknown": [...], "not_applicable": [...]},
          ...
        },
        "overall": "pass|fail|unknown|not_checked",
        "counts": {...},
        "unassigned": [...],   # ← check_id 不以 E1..E7 开头的（防拼写错）
      }
      ```
    """
    buckets: dict = {c: [] for c in CRITERIA}
    unassigned: list = []

    for r in checks:
        if not isinstance(r, CheckResult):
            raise TypeError("★ 报告只收 CheckResult，收到 %r" % type(r))
        crit = _criterion_of(r.check_id)
        if crit in buckets:
            buckets[crit].append(r)
        else:
            #: ★ 拼错的 check_id 不该悄悄消失 —— 它会让报告漏掉一条检查
            unassigned.append(
                {"check_id": r.check_id, "status": r.status.value, "reason": r.reason}
            )

    criteria: dict = {}
    for crit in CRITERIA:
        items = buckets[crit]
        failed = [r.check_id for r in items if r.status is Status.FAIL]
        unknown = [r.check_id for r in items if r.status is Status.UNKNOWN]
        na = [r.check_id for r in items if r.status is Status.NOT_APPLICABLE]
        passed = [r.check_id for r in items if r.status is Status.PASS]

        if not items:
            status = "not_checked"
        elif failed:
            status = "fail"
        elif unknown:
            #: ★ 有 fail 时优先报 fail（更严重）；否则 unknown 使整体不绿
            status = "unknown"
        else:
            #: 全是 pass / not_applicable ⇒ 绿
            status = "pass"

        criteria[crit] = {
            "name": CRITERIA_NAMES[crit],
            "checks": [
                {
                    "check_id": r.check_id,
                    "status": r.status.value,
                    "reason": r.reason,
                    "observed": r.observed,
                    "expected": r.expected,
                }
                for r in items
            ],
            "status": status,
            "passed": passed,
            "failed": failed,
            "unknown": unknown,
            "not_applicable": na,
        }

    counts = {
        "checks": len(checks),
        "pass": sum(1 for r in checks if r.status is Status.PASS),
        "fail": sum(1 for r in checks if r.status is Status.FAIL),
        "unknown": sum(1 for r in checks if r.status is Status.UNKNOWN),
        "not_applicable": sum(
            1 for r in checks if r.status is Status.NOT_APPLICABLE
        ),
    }

    #: ★ 总体判据：七条都要 pass（`not_checked` / `unknown` / `fail` 都不算）
    not_checked = [c for c in CRITERIA if criteria[c]["status"] == "not_checked"]
    any_fail = [c for c in CRITERIA if criteria[c]["status"] == "fail"]
    any_unknown = [c for c in CRITERIA if criteria[c]["status"] == "unknown"]

    if not checks:
        overall = "not_checked"
    elif any_fail:
        overall = "fail"
    elif not_checked or any_unknown:
        overall = "unknown"
    else:
        overall = "pass"

    return {
        "criteria": criteria,
        "overall": overall,
        "counts": counts,
        "not_checked": not_checked,
        "unassigned": unassigned,
    }


def _badge(status: str) -> str:
    return {
        "pass": "✅ pass",
        "fail": "❌ fail",
        "unknown": "⚠️ unknown",
        "not_checked": "⬜ 未检查",
    }.get(status, "? %s" % status)


def render_markdown(report: dict, *, title: str = "E1–E7 验收报告") -> str:
    """★ 把 `build_report()` 的结果渲染成 markdown。

    ★ 三条都要写出来：**不合格**、**未测到**、**未检查** ——
      只写「通过了几条」的报告没有信息量。
    """
    lines: list = []
    lines.append("# %s" % title)
    lines.append("")
    lines.append("**总体**：%s" % _badge(report["overall"]))
    lines.append("")

    c = report["counts"]
    lines.append(
        "检查共 %d 条：pass %d · fail %d · unknown %d · not_applicable %d"
        % (c["checks"], c["pass"], c["fail"], c["unknown"], c["not_applicable"])
    )
    lines.append("")
    lines.append("## 逐条状态")
    lines.append("")
    lines.append("| 判据 | 名称 | 状态 | 检查 | 不合格 | 未测到 |")
    lines.append("|---|---|---|---|---|---|")
    for crit in CRITERIA:
        row = report["criteria"][crit]
        lines.append(
            "| **%s** | %s | %s | %d | %s | %s |"
            % (
                crit,
                row["name"],
                _badge(row["status"]),
                len(row["checks"]),
                ("、".join(row["failed"]) or "—"),
                ("、".join(row["unknown"]) or "—"),
            )
        )

    #: ★ 未测到的单列一段 —— 这是最容易被含糊掉的一类
    unknown_any = [
        (cri, cid)
        for cri in CRITERIA
        for cid in report["criteria"][cri]["unknown"]
    ]
    if unknown_any:
        lines.append("")
        lines.append("## 未测到的项（不等于合格）")
        lines.append("")
        for cri, cid in unknown_any:
            item = next(
                x for x in report["criteria"][cri]["checks"] if x["check_id"] == cid
            )
            lines.append("- `%s`：%s" % (cid, item["reason"]))

    #: ★ 不合格的单列一段，带读数
    fail_any = [
        (cri, cid) for cri in CRITERIA for cid in report["criteria"][cri]["failed"]
    ]
    if fail_any:
        lines.append("")
        lines.append("## 不合格的项")
        lines.append("")
        for cri, cid in fail_any:
            item = next(
                x for x in report["criteria"][cri]["checks"] if x["check_id"] == cid
            )
            lines.append("- `%s`：%s" % (cid, item["reason"]))

    if report["not_checked"]:
        lines.append("")
        lines.append("## 未检查的判据")
        lines.append("")
        lines.append(
            "- %s —— 一条检查都没跑过，不能当成通过"
            % "、".join(report["not_checked"])
        )

    if report["unassigned"]:
        lines.append("")
        lines.append("## ⚠ 无法归类的检查（check_id 拼写可疑）")
        lines.append("")
        for u in report["unassigned"]:
            lines.append(
                "- `%s`（%s）：%s" % (u["check_id"], u["status"], u["reason"][:80])
            )

    return "\n".join(lines) + "\n"


def deltas(previous: dict, current: dict) -> dict:
    """★ 两次报告之间的**状态变化**（A8 要求「证据变化」）。

    ★ 只报变化，不重复全量 —— 全量在 current 里已经有了。
    """
    out: dict = {"changed": [], "improved": [], "regressed": []}
    order = {"not_checked": 0, "unknown": 1, "fail": 2, "pass": 3}

    for crit in CRITERIA:
        old = (previous.get("criteria", {}).get(crit) or {}).get("status")
        new = (current.get("criteria", {}).get(crit) or {}).get("status")
        if old == new:
            continue
        out["changed"].append({"criterion": crit, "from": old, "to": new})
        if old is not None and new is not None:
            if order.get(new, -1) > order.get(old, -1):
                out["improved"].append(crit)
            elif order.get(new, -1) < order.get(old, -1):
                out["regressed"].append(crit)

    out["overall_from"] = previous.get("overall")
    out["overall_to"] = current.get("overall")
    return out
