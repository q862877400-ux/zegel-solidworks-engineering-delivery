"""N 维度观测器：仓库外来源（`C:\\swprojects`）与尚未触碰的目录（只读）。

第一部分 `C:\\swprojects\\*`：每个克隆是否有 .git / LICENSE / 许可首行 / 文件数 / 最近提交
第二部分 仓库内 `apps/ dotnet/ ai_team/ subskills/ references/`：文件构成与体积

跑法：python docs\\state\\probes\\probe_external.py --json docs/state/inventory-n.json
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SWP = pathlib.Path(r"C:\swprojects")
UNTOUCHED = ("apps", "dotnet", "ai_team", "subskills", "references")
CAP = 60000  # 单目录最多数这么多文件，防超大克隆拖死


def count_files(p: pathlib.Path) -> tuple[int, dict[str, int]]:
    n = 0
    ext: collections.Counter[str] = collections.Counter()
    for f in p.rglob("*"):
        try:
            if f.is_file():
                n += 1
                ext[f.suffix.lower() or "<无扩展名>"] += 1
        except OSError:
            continue
        if n >= CAP:
            break
    return n, dict(ext.most_common(8))


def last_commit(p: pathlib.Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "-C", str(p), "log", "-1", "--format=%ad", "--date=short"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
        )
        return (proc.stdout or "").strip() or "<无>"
    except Exception:  # noqa: BLE001
        return "<超时/失败>"


def license_of(p: pathlib.Path) -> dict:
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "LICENSE-CODE"):
        f = p / name
        if f.exists():
            first = f.read_text(encoding="utf-8", errors="replace").splitlines()
            head = " ".join(x.strip() for x in first[:2] if x.strip())[:90]
            return {"file": name, "first": head}
    return {"file": "", "first": "<无 LICENSE>"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    data: dict = {}
    if SWP.exists():
        rows = []
        for d in sorted(x for x in SWP.iterdir() if x.is_dir()):
            rows.append({
                "name": d.name,
                "is_git": (d / ".git").exists(),
                "files": count_files(d)[0],
                "ext_top": count_files(d)[1],
                "license": license_of(d),
                "last_commit": last_commit(d) if (d / ".git").exists() else "<非 git 检出>",
            })
        data["swprojects"] = {
            "path": str(SWP),
            "dirs": len(rows),
            "with_git": sum(1 for r in rows if r["is_git"]),
            "with_license": sum(1 for r in rows if r["license"]["file"]),
            "without_license": [r["name"] for r in rows if not r["license"]["file"]],
            "license_heads": dict(
                collections.Counter(r["license"]["first"][:40] for r in rows).most_common(8)
            ),
            "rows": rows,
        }
    else:
        data["swprojects"] = {"path": str(SWP), "exists": False}

    unt = {}
    for name in UNTOUCHED:
        p = ROOT / name
        if not p.exists():
            unt[name] = {"exists": False}
            continue
        n, ext = count_files(p)
        subdirs = sorted(x.name for x in p.iterdir() if x.is_dir())[:10]
        unt[name] = {"exists": True, "files": n, "ext_top": ext, "subdirs": subdirs}
    data["untouched_dirs"] = unt

    sp = data["swprojects"]
    print(f"C:\\swprojects: {sp.get('dirs')} 个目录 · 含 .git {sp.get('with_git')} · 有 LICENSE {sp.get('with_license')}")
    if sp.get("without_license"):
        print(f"  无 LICENSE 的: {sp['without_license']}")
    print("  许可首行分布:", sp.get("license_heads"))
    print("\n仓库内未触碰目录：")
    for k, v in unt.items():
        if v.get("exists"):
            print(f"  {k:<12} {v['files']:>6} 文件  扩展 {list(v['ext_top'].items())[:3]}")
        else:
            print(f"  {k:<12} <不存在>")

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