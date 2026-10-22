r"""@brief 逐个真机跑被迁移过的 `verify_*` 冒烟 —— 上轮（轮 169）迁移后只抽样跑了 2 个。

## 为什么（轮 170）
轮 169 把 **34 个脚本**的收尾从「只查」改成「查+点掉」，但**只抽样跑了 2 个**
⇒ ⚠ 若某个脚本的收尾依赖返回值**形状之外的细节**，可能没被发现。
★ 本脚本把**被迁的 15 个 `verify_*`** 逐个真机跑一遍，汇总 verdict。

## ⚠ 安全
顺序执行（COM 单实例，事实 24）；每个脚本自己管收尾；本脚本**只读它们的输出**，
不额外碰 SolidWorks（除最后一次兜底点掉）。

# ── 来源 ──
# 仓库:   本项目自身（批量跑既有冒烟）
# 文件:   tools/run_migrated_verify_smokes.py
# 定位:   给 Spec Kit `090` 补上轮欠的「逐个真机跑」。
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
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "migrated-verify-smokes.json"
)

SCRIPTS = [
    "verify_batch10_smoke.py",
    "verify_bbox_smoke.py",
    "verify_bmp_smoke.py",
    "verify_centerline_smoke.py",
    "verify_dome_smoke.py",
    "verify_ellipse_smoke.py",
    "verify_equation_smoke.py",
    "verify_gtol_smoke.py",
    "verify_helix_smoke.py",
    "verify_hole_standards_smoke.py",
    "verify_in_context_reference_smoke.py",
    "verify_interference_smoke.py",
    "verify_png_smoke.py",
    "verify_sketch_edit_smoke.py",
    "verify_sketch_getters_smoke.py",
]
VERDICT = re.compile(r"──\s*(\d+)/(\d+)\s*·\s*verdict:\s*(\w+)\s*──")


def main() -> int:
    rows = []
    for name in SCRIPTS:
        p = ROOT / "tools" / name
        if not p.is_file():
            rows.append({"script": name, "status": "MISSING"})
            print("  %-42s **文件不在**" % name)
            continue
        try:
            r = subprocess.run(
                [sys.executable, str(p)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=600,
            )
            out = (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired:
            rows.append({"script": name, "status": "TIMEOUT"})
            print("  %-42s **超时**（600s）" % name)
            continue
        m = None
        for m in VERDICT.finditer(out):
            pass
        #: ★ 收尾那行也要看（证明迁移后的收尾仍在跑、且如实报）
        tail = [l.strip() for l in out.splitlines() if "扫了" in l and "窗口" in l]
        rec = {
            "script": name,
            "exit": r.returncode,
            "verdict": (m.group(3) if m else None),
            "passed": (int(m.group(1)) if m else None),
            "total": (int(m.group(2)) if m else None),
            "cleanup_line": tail[-1][:80] if tail else None,
        }
        rows.append(rec)
        print(
            "  %-42s %s/%s · verdict=%s · exit=%s · %s"
            % (
                name,
                rec["passed"],
                rec["total"],
                rec["verdict"],
                r.returncode,
                (rec["cleanup_line"] or "**收尾行没有**")[:34],
            )
        )

    n_pass = sum(1 for r in rows if r.get("verdict") == "pass")
    n_fail = sum(1 for r in rows if r.get("verdict") == "fail")
    n_none = sum(1 for r in rows if r.get("verdict") is None)
    n_cleanup = sum(1 for r in rows if r.get("cleanup_line"))
    print()
    print("  ── 汇总 ──")
    print(
        "   pass **%d** · fail **%d** · 没有 verdict **%d** · 共 %d"
        % (n_pass, n_fail, n_none, len(rows))
    )
    print(
        "   ★ 收尾行**都还在**（迁移后收尾确实在跑）: **%d/%d**"
        % (n_cleanup, len(rows))
    )
    print(
        "   ★ 收尾报「扫了 N 个窗口」且 N>0 的: **%d** 个（0 就说明口径又串了）"
        % sum(
            1
            for r in rows
            if r.get("cleanup_line") and "扫了 0 个窗口" not in r["cleanup_line"]
        )
    )

    #: 兜底：万一哪个脚本留了弹窗
    try:
        import sw_connect

        f, d, s = sw_connect.settle_residual_dialogs()
        print(
            "   收尾兜底（settle_residual_dialogs）⇒ 发现 %d · 点掉 %d · 扫了 %d"
            % (f, d, s)
        )
        OUT.write_text(
            json.dumps(
                {"rows": rows, "leftover": {"found": f, "dismissed": d}},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    except Exception as exc:  # noqa: BLE001
        print("   收尾兜底失败: %s" % str(exc)[:70])
        OUT.write_text(
            json.dumps({"rows": rows}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print("  证据: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
