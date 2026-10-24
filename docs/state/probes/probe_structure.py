"""A 维度观测器：顶层结构、目录规模、gitignore 落位（只读）。

跑法：python docs\\state\\probes\\probe_structure.py --json docs/state/inventory-a.json
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SKIP = {".git"}


def git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    return proc.stdout


def dir_stats(p: pathlib.Path, cap: int = 200000) -> tuple[int, int]:
    """返回 (文件数, 总字节)。cap 防止在超大目录上跑太久。"""
    n = 0
    size = 0
    for f in p.rglob("*"):
        try:
            if f.is_file():
                n += 1
                size += f.stat().st_size
        except OSError:
            continue
        if n >= cap:
            break
    return n, size


def is_ignored(rel: str) -> bool:
    proc = subprocess.run(
        ["git", "check-ignore", "-q", rel], cwd=str(ROOT), capture_output=True
    )
    return proc.returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    dirs = sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name not in SKIP)
    files = sorted(p for p in ROOT.iterdir() if p.is_file())

    data: dict = {
        "top_dirs_total": len(dirs),
        "top_files_total": len(files),
        "top_files": [p.name for p in files],
        "top_dirs": [],
        "ignored_entries": len([x for x in git("status", "--ignored", "--porcelain").splitlines() if x.startswith("!!")]),
        "tracked_files": int(git("ls-files").count("\n")),
    }
    for d in dirs:
        n, size = dir_stats(d)
        data["top_dirs"].append(
            {
                "name": d.name,
                "files": n,
                "mb": round(size / 1048576, 1),
                "git_ignored": is_ignored(d.name),
            }
        )

    print(f"顶层目录 {data['top_dirs_total']} 个 · 顶层文件 {data['top_files_total']} 个")
    print(f"git 跟踪文件 {data['tracked_files']} · ignored 条目 {data['ignored_entries']}")
    print("\n按文件数 top12：")
    for r in sorted(data["top_dirs"], key=lambda x: -x["files"])[:12]:
        print(f"  {r['name']:<28} {r['files']:>7} 文件  {r['mb']:>9.1f} MB  ignored={r['git_ignored']}")

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