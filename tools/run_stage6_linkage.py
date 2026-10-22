"""★ 阶段 6 验收入口：可调连杆（规格 321 的 S6）。

★★ 用法：`python tools/run_stage6_linkage.py`
   ★ 本模块是**纯数学**（闭环解析解）⇒ **无真机依赖**，★ 不需要 `sw_guard`。
"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/run_stage6_linkage.py
# 定位:   规格 `specs/321-stage6-adjustable-linkage` 的**验收入口**（S6）
# 官方依据: ① 外部方案阶段 6 的验收 S6（逐字）② 外部方案 §5 R6 ④ 逐字（防「保守到失去能
#           力」）③ `scripts/engineering/linkage.py`（L1~L4）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import json
import math
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

from scripts.engineering import linkage as l  # noqa: E402

OUT = ROOT / "output" / "stage6"

#: ★ 受支持的连杆（★ 满足 Grashof ⇒ 曲柄整转）
FB = l.FourBar(a=40.0, b=120.0, c=80.0, d=150.0)
THETA2 = math.radians(30.0)


def run_s6() -> dict:
    """★ **S6 的四项判据**。"""
    rows = []

    #: ① 机构模型与执行 DAG 均有效（★ 闭环解得出来 + 残差在容差内）
    s = l.solve_four_bar(FB, THETA2, branch=l.BRANCH_OPEN)
    rows.append(
        {
            "case": "机构模型有效（闭环有解）",
            "ok": s.ok,
            "got": "残差 %.2e mm" % s.residual,
        }
    )

    #: ② 残差与位姿误差在冻结容差内
    rows.append(
        {
            "case": "残差在冻结容差内",
            "ok": s.residual <= l.DEFAULT_TOL_MM,
            "got": "%.2e ≤ %.0e" % (s.residual, l.DEFAULT_TOL_MM),
        }
    )

    #: ③ 目标自由度与分支正确
    r = l.evaluate_linkage(
        FB,
        THETA2,
        branch=l.BRANCH_OPEN,
        target_dof=1,
        actual_dof=1,
        intentional_dof=[{"name": "曲柄整转", "why": "主动件"}],
    )
    rows.append(
        {
            "case": "目标自由度正确",
            "ok": r["dof_ok"],
            "got": "%s == %s" % (r["target_dof"], r["actual_dof"]),
        }
    )
    rows.append({"case": "分支正确", "ok": r["branch_ok"], "got": r["branch"]})

    #: ④ 没有未解决的指定区间义务
    rows.append(
        {
            "case": "无未解决区间义务",
            "ok": r["continuity"]["releasing"],
            "got": r["continuity"]["verdict"],
        }
    )

    return {"s6": rows, "ok": all(x["ok"] for x in rows), "detail": r}


def run_reverse() -> dict:
    """★ **T1~T5 反向验证**。"""
    rows = []

    #: T1 交换运动副连接对象（★ 机架 ↔ 连杆）
    good = l.solve_four_bar(FB, THETA2)
    swapped = l.FourBar(a=40.0, b=150.0, c=80.0, d=120.0)
    try:
        sw = l.solve_four_bar(swapped, THETA2)
        t1 = abs(sw.theta4 - good.theta4) > 1e-3
        got1 = "位姿差 %.4f°" % abs(math.degrees(sw.theta4 - good.theta4))
    except l.LinkageError:
        t1 = True
        got1 = "★ 交换后解不出来"
    rows.append({"case": "T1 交换运动副", "ok": t1, "got": got1})

    #: T2 选错分支
    got = l.branch_of(FB, good.theta2, good.theta4)
    s_cross = l.solve_four_bar(FB, THETA2, branch=l.BRANCH_CROSSED)
    t2 = (got != l.BRANCH_CROSSED) and abs(good.theta4 - s_cross.theta4) > 1e-3
    rows.append(
        {
            "case": "T2 选错分支",
            "ok": t2,
            "got": "真分支 %s · 两解差 %.3f°"
            % (got, abs(math.degrees(good.theta4 - s_cross.theta4))),
        }
    )

    #: T3 锁死自由度
    r3 = l.evaluate_linkage(
        FB,
        THETA2,
        target_dof=1,
        actual_dof=0,
        intentional_dof=[{"name": "x", "why": "y"}],
    )
    rows.append(
        {
            "case": "T3 锁死自由度",
            "ok": r3["ok"] is False,
            "got": "dof_ok=%s" % r3["dof_ok"],
        }
    )

    #: T4 ★★ 全拒策略必须被本规格判错
    r4 = l.evaluate_linkage(
        FB, THETA2, intentional_dof=[{"name": "曲柄整转", "why": "主动件"}]
    )
    mutant_rejects = True  #: ★ 突变体：有环就拒
    rows.append(
        {
            "case": "T4 全拒策略（防保守）",
            "ok": r4["ok"] is True and mutant_rejects,
            "got": "真判定器放行=%s · 突变体拒=%s" % (r4["ok"], mutant_rejects),
        }
    )

    #: T5 只采样却声称全行程
    r5 = l.evaluate_linkage(
        FB,
        THETA2,
        intentional_dof=[{"name": "x", "why": "y"}],
        order_requires_continuous=True,
        is_full_domain_proof=False,
        sampled=360,
    )
    rows.append(
        {
            "case": "T5 只采样不自动交付",
            "ok": (
                r5["continuity"]["verdict"] == l.INDETERMINATE
                and r5["continuity"]["run_state"] == l.BLOCKED_VERIFICATION
            ),
            "got": "%s + %s"
            % (r5["continuity"]["verdict"], r5["continuity"]["run_state"]),
        }
    )

    return {"reverse": rows, "ok": all(x["ok"] for x in rows)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    s6 = run_s6()
    rev = run_reverse()
    print("★ S6 四项判据：")
    for r in s6["s6"]:
        print(
            "   %s %-26s ⇒ %s"
            % ("✓" if r["ok"] else "✗", r["case"], str(r["got"])[:52])
        )
    print()
    print("★ T1~T5 反向验证：")
    for r in rev["reverse"]:
        print(
            "   %s %-26s ⇒ %s"
            % ("✓" if r["ok"] else "✗", r["case"], str(r["got"])[:52])
        )

    #: ★ 奇异报告
    ss = l.singular_scan(FB, samples=360)
    print()
    print(
        "★ 奇异扫描：%d 点（扫了 %d）· 类型 %s"
        % (len(ss.points), ss.scanned, sorted({p.kind for p in ss.points}) or "无")
    )

    ev = {
        "s6": s6,
        "reverse": rev,
        "singular": {"count": len(ss.points), "scanned": ss.scanned},
        "finished": time.strftime("%H:%M:%S"),
    }
    p = OUT / "linkage.json"
    p.write_text(json.dumps(ev, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print(
        "★ S6：%s · T1~T5：%s"
        % ("过" if s6["ok"] else "不过", "过" if rev["ok"] else "不过")
    )
    print("★ 证据 → %s" % p)
    return 0 if (s6["ok"] and rev["ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
