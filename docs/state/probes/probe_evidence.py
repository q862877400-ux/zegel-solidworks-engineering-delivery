"""L 维度观测器：`capabilities.yaml` 里 100 条 verified 的 evidence 逐条核验（只读）。

对每条 evidence 元素做三件事：
  ① 分类（文件路径 / 命令 / 自由文本）
  ② 路径类：解析后 `Path.exists()`，记录存在与否
  ③ 命令类：抽出命令里出现的脚本/文件记号，逐个查存在性（**不执行命令**）

跑法：python docs\\state\\probes\\probe_evidence.py --json docs/state/inventory-l.json
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
import yaml  # noqa: E402

PATH_RE = re.compile(r"[A-Za-z0-9_./\\-]+\.(?:py|json|md|txt|log|ps1|yaml|yml|csv)")
CMD_RE = re.compile(r"\b(python|pytest|pwsh|git|npm|uv)\b", re.I)


def norm_path(tok: str) -> str:
    t = tok.strip().strip("`'\"()[]，。；：、").replace("\\\\", "\\")
    return t


#: ★ 仓库外的官方源（AGENTS 记的两套离线源之一）。evidence 里出现 `\swapi\...` 属于**外部引用**，
#:   不能按仓库相对路径判存在性 —— 本节实测踩到过：11 条 `\swapi\` 路径被误判为「全仓找不到」。
EXTERNAL_ROOTS = {"swapi": pathlib.Path(r"C:\swapi")}


def resolve(token: str) -> tuple[str, str]:
    """返回 (判定, 位置)。判定 ∈ {repo, external, elsewhere, missing}。"""
    p = norm_path(token)
    if (ROOT / p).exists():
        return "repo", p
    first = pathlib.Path(p.lstrip("\\/")).parts[:1]
    if first and first[0].lower() in EXTERNAL_ROOTS:
        ext = EXTERNAL_ROOTS[first[0].lower()]
        if not ext.exists():
            return "missing", f"<外部源 {ext} 不存在>"
        rel = pathlib.Path(*pathlib.Path(p.lstrip("\\/")).parts[1:])
        if (ext / rel).exists():
            return "external", str(ext / rel)
    alt = [q for q in ROOT.rglob(pathlib.Path(p).name)][:1]
    if alt:
        return "elsewhere", str(alt[0].relative_to(ROOT))
    return "missing", ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    doc = yaml.safe_load((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))
    caps = [c for c in doc.get("capabilities", []) if c.get("level") == "verified"]

    kinds = collections.Counter()
    missing = []
    checked = 0
    per_cap = []
    cat = collections.Counter()
    caps_no_path = []
    caps_all_text = []
    for c in caps:
        ev = c.get("evidence") or []
        items = ev if isinstance(ev, list) else [ev]
        n_ok = 0
        has_path = False
        for raw in items:
            s = str(raw)
            m = PATH_RE.search(s)
            if m:
                has_path = True
                kinds["path"] += 1
                checked += 1
                verdict, where = resolve(m.group(0))
                if verdict in ("repo", "external"):
                    n_ok += 1
                else:
                    missing.append({
                        "capability": c.get("id"),
                        "token": norm_path(m.group(0)),
                        "verdict": verdict,
                        "found_elsewhere": where,
                    })
                    cat[
                        "移到仓库内他处" if verdict == "elsewhere" else "全仓与外部源都找不到"
                    ] += 1
            elif CMD_RE.search(s):
                kinds["command"] += 1
                for tok in PATH_RE.findall(s):
                    checked += 1
                    verdict, where = resolve(tok)
                    if verdict not in ("repo", "external"):
                        missing.append({
                            "capability": c.get("id"),
                            "token": norm_path(tok),
                            "from": "command",
                            "verdict": verdict,
                            "found_elsewhere": where,
                        })
                        cat[
                            "移到仓库内他处" if verdict == "elsewhere" else "全仓与外部源都找不到"
                        ] += 1
            else:
                kinds["text"] += 1
        if not has_path:
            caps_no_path.append(c.get("id"))
            if not any(CMD_RE.search(str(x)) for x in items):
                caps_all_text.append(c.get("id"))
        per_cap.append({"id": c.get("id"), "items": len(items), "path_hits_ok": n_ok})

    data = {
        "verified_capabilities": len(caps),
        "evidence_items": sum(kinds.values()),
        "item_kinds": dict(kinds),
        "path_tokens_checked": checked,
        "path_tokens_unreachable": len(missing),
        "classification": dict(cat),
        "missing_all": missing,
        "caps_without_path_evidence": caps_no_path,
        "caps_evidence_all_free_text": caps_all_text,
        "caps_with_zero_evidence": [p["id"] for p in per_cap if p["items"] == 0],
        "per_cap": per_cap,
    }

    print(f"verified 能力 {data['verified_capabilities']} 条 · evidence 元素 {data['evidence_items']} 个")
    print(f"元素分类：{data['item_kinds']}")
    print(f"路径记号检查 {checked} 个 · 不可达 {len(missing)}")
    print(f"不可达分类：{data['classification']}")
    print(f"没有任何路径类证据的能力 {len(caps_no_path)} 个 · 证据全为自由文本的 {len(caps_all_text)} 个")
    for m in missing[:10]:
        print("   不可达:", m["capability"], "→", m["token"], f"[{m['verdict']}]", m["found_elsewhere"] or "")

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