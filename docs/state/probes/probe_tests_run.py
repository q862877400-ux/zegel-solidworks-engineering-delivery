"""M 维度观测器：测试**执行期**结果（只跑离线门禁类测试，分层抽样）。

纪律：
  · 只跑 `tests/test_*_gate.py`（门禁测试，离线静态）——不跑需要 SolidWorks 的用例；
  · 每个文件独立子进程 + 单文件超时；累计墙钟超预算就停，并如实记录「未跑到哪些」；
  · 不修改任何测试、不改仓库。

跑法：python docs\\state\\probes\\probe_tests_run.py --json docs/state/inventory-m.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
TESTS = ROOT / "tests"
PER_FILE_TIMEOUT = 240
TOTAL_BUDGET = 1200  # 秒


def parse_counts(out: str) -> dict:
    last = ""
    for ln in reversed(out.splitlines()):
        if re.search(r"\d+ (passed|failed|error|skipped)", ln):
            last = ln
            break
    c = {}
    for key in ("passed", "failed", "error", "errors", "skipped", "xfailed", "warnings"):
        m = re.search(r"(\d+) " + key + r"\b", last)
        if m:
            c[key.rstrip("s")] = int(m.group(1))
    return c


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    files = sorted(TESTS.glob("test_*_gate.py"))
    rows = []
    started = time.time()
    skipped_for_budget = []
    for i, f in enumerate(files):
        if time.time() - started > TOTAL_BUDGET:
            skipped_for_budget = [p.name for p in files[i:]]
            break
        t0 = time.time()
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", str(f), "-q", "--no-header",
                 "-p", "no:cacheprovider"],
                cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=PER_FILE_TIMEOUT,
            )
            out = (proc.stdout or "") + (proc.stderr or "")
            rc = proc.returncode
            counts = parse_counts(out)
        except subprocess.TimeoutExpired:
            rc = -9
            counts = {"timeout": 1}
            out = ""
        rows.append({
            "file": f.name,
            "exit": rc,
            "seconds": round(time.time() - t0, 1),
            "counts": counts,
        })
        print(f"  {f.name:<48} exit={rc:<3} {round(time.time()-t0,1):>6}s  {counts}")

    agg = {"files_run": len(rows)}
    for r in rows:
        for k, v in r["counts"].items():
            agg[k] = agg.get(k, 0) + v
    bad = [r for r in rows if r["exit"] not in (0, 5)]  # 5 = no tests collected
    data = {
        "scope": "tests/test_*_gate.py",
        "budget_seconds": TOTAL_BUDGET,
        "per_file_timeout": PER_FILE_TIMEOUT,
        "aggregate": agg,
        "files_with_nonzero_exit": [{"file": r["file"], "exit": r["exit"], "counts": r["counts"]} for r in bad],
        "skipped_for_budget": skipped_for_budget,
        "rows": rows,
    }

    print(f"\n跑了 {len(rows)} 个门禁测试文件 · 汇总 {agg}")
    print(f"非零退出 {len(bad)} 个 · 预算内未跑 {len(skipped_for_budget)} 个")

    if args.json:
        out = pathlib.Path(args.json)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("已写出:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())