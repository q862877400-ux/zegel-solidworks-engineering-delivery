r"""@brief 逐条跑 `verified` 条目声明的**真机验收命令** —— 「曾经绿」要重新确认为「现在绿」。

## 为什么（轮 180）
objective ③ 要求「**跑该阶段验收命令确认真绿**」。★ 轮 179 跑拓扑那条时发现它**已经变红**
（原因是环境：Simulation 加载项/许可）⇒ ★★ **那么其余条目呢？**
⇒ 本跑器把 `capabilities.yaml` 里 `level == verified` 的条目**声明的** `python tools/*.py`
**逐条跑一遍**，汇总 `verdict` —— **不靠记忆，靠跑**。

## 判据
```
① 每条命令的 **exit code** 与输出里的 `verdict: pass|fail`（两样都记，不只看一样）
② ★ 汇总：pass / fail / 无 verdict / 超时，**逐个列出**
③ 对 fail 的，**不尝试修**（本轮只做"**确认现状**"）—— 修留给下轮，且要先分辨原因
```
⚠ **顺序执行**（COM 单实例，事实 24）；每条**独立子进程**（一条崩不带走全部）。

## ⚠ 安全
每条脚本自己管收尾（本仓库的冒烟都会 `settle_residual_dialogs`）；
本跑器只在**全部跑完后**做一次兜底点掉。

# ── 来源 ──
# 仓库:   本项目自身（批量跑既有验收命令）
# 文件:   tools/run_verified_acceptance_commands.py
# 定位:   给 Spec Kit `100` 把「曾经绿」系统性地重新确认为「现在绿」。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "verified-acceptance-run.json"
)
#: ⚠⚠⚠ **2026-10-01（轮 180）：本仓库的验收脚本有**三种**输出格式**（实测）：
#: ```
#:   ① `── 8/8 · verdict: pass ──`              （多数冒烟）
#: ② `── 15/15 项通过 · verdict: pass ──`      （`verify_dfm_e2e` / `verify_routing_e2e`
#: ）
#: ③ `verdict: pass`                          （`verify_costing_e2e`，**没有 N/M 计数**
#: ）
#: ```
#: ★ 我第一版**只认 ①** ⇒ 把 ②③ 报成了"**无 verdict**"（**3 个 pass 被误报**）。
#: ⇒ ★ 教训（本会话第 N 次，事实 51 那一族）：**判据要与实现的**实际形态**对齐**，
#:   而不是与我**记得的**形态对齐。★ 且**两个证据都要看**（verdict 文本 + exit code）。
VERDICT = re.compile(
    #: ⚠ `(?m)` **必须放在最前**（放中间会报 `global flags not at the start`）
    r"(?m)(?:──\s*(\d+)\s*/\s*(\d+)\s*(?:项通过)?\s*·\s*verdict:\s*(\w+)\s*──"  #: ①②
    r"|^\s*verdict:\s*(\w+)\s*$)"  #: ③
)
#: ★ 由 capabilities.yaml 抽出来的那 31 条（本轮固定快照 ⇒ 可复跑、可比对）
CMDS = [
    "tools/audit_get_com_member_semantics.py",
    "tools/capture_simulation_evidence.py",
    "tools/capture_topology_evidence.py",
    "tools/probe_add_relation_forms.py",
    "tools/probe_chamfer_forms.py",
    "tools/probe_dwg_magic.py",
    "tools/probe_export_magic_matrix.py",
    "tools/probe_getlines_count.py",
    "tools/probe_gtol_frame_order.py",
    "tools/probe_pdf_on_drawing.py",
    "tools/probe_sketch_getter_shapes.py",
    "tools/probe_slot_and_point_shapes.py",
    "tools/probe_window_vs_graphics.py",
    "tools/verify_bbox_smoke.py",
    "tools/verify_bmp_smoke.py",
    "tools/verify_centerline_smoke.py",
    "tools/verify_composite_curve_smoke.py",
    "tools/verify_costing_e2e.py",
    "tools/verify_dfm_e2e.py",
    "tools/verify_dome_smoke.py",
    "tools/verify_dxf_preview_e2e.py",
    "tools/verify_ellipse_smoke.py",
    "tools/verify_equation_smoke.py",
    "tools/verify_gtol_smoke.py",
    "tools/verify_helix_smoke.py",
    "tools/verify_hole_standards_smoke.py",
    "tools/verify_in_context_reference_smoke.py",
    "tools/verify_png_smoke.py",
    "tools/verify_routing_e2e.py",
    "tools/verify_sketch_edit_smoke.py",
    "tools/verify_sketch_getters_smoke.py",
]


def main() -> int:
    rows = []
    for rel in CMDS:
        p = ROOT / rel
        if not p.is_file():
            rows.append({"cmd": rel, "status": "MISSING"})
            print("  %-48s **文件不在**" % rel)
            continue
        try:
            r = subprocess.run(
                [sys.executable, str(p)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=900,
            )
            out = (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired:
            rows.append({"cmd": rel, "status": "TIMEOUT"})
            print("  %-48s **超时**（900s）" % rel)
            continue
        m = None
        for m in VERDICT.finditer(out):
            pass
        if m is None:
            verdict, npass, ntot = None, None, None
        elif m.group(3):  #: ①② 形态：带 N/M
            npass, ntot, verdict = int(m.group(1)), int(m.group(2)), m.group(3)
        else:  #: ③ 形态：只有 verdict
            npass, ntot, verdict = None, None, m.group(4)
        rec = {
            "cmd": rel,
            "exit": r.returncode,
            "verdict": verdict,
            "passed": npass,
            "total": ntot,
        }
        rows.append(rec)
        print(
            "  %-48s %s/%s · verdict=%-4s · exit=%s"
            % (rel, rec["passed"], rec["total"], rec["verdict"], r.returncode)
        )

    n_pass = sum(1 for r in rows if r.get("verdict") == "pass")
    n_fail = sum(1 for r in rows if r.get("verdict") == "fail")
    n_none = sum(
        1 for r in rows if r.get("verdict") is None and r.get("status") != "MISSING"
    )
    n_missing = sum(1 for r in rows if r.get("status") in ("MISSING", "TIMEOUT"))
    print()
    print("  ── 汇总 ──")
    print(
        "   pass **%d** · fail **%d** · 无 verdict **%d** · 文件不在/超时 **%d** · 共 %d"
        % (n_pass, n_fail, n_none, n_missing, len(rows))
    )
    print()
    print("   ★ 需要分辨原因的 fail：")
    for r in rows:
        if r.get("verdict") == "fail":
            print("      %s（%s/%s）" % (r["cmd"], r.get("passed"), r.get("total")))
    if n_none:
        print("   ⚠ 没有 verdict 的（多半是**探针**，不设 verdict —— 属正常）：")
        for r in rows:
            if r.get("verdict") is None and r.get("status") != "MISSING":
                print("      %s（exit=%s）" % (r["cmd"], r.get("exit")))

    try:
        import sw_connect

        f, d_, s = sw_connect.settle_residual_dialogs(settle_seconds=1.0)
        print()
        print("   收尾兜底：发现 %d · 点掉 %d · 扫了 %d" % (f, d_, s))
    except Exception as exc:  # noqa: BLE001
        print("   收尾兜底失败: %s" % str(exc)[:60])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(
            {
                "rows": rows,
                "pass": n_pass,
                "fail": n_fail,
                "no_verdict": n_none,
                "missing": n_missing,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
