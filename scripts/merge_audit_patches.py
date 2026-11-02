"""★ 合并逐文件审阅补丁进台账：校验路径/裁决/证据形态，拒收不合规条目。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/merge_audit_patches.py
# 定位:   业主 2026-11-02 指令里的「多轮」机制：审阅者（人/agent）**各自**写补丁 jsonl，
#         由本脚本统一合并进 `docs/state/file-audit.jsonl`。★ 这样多个审阅者并行时
#         **不会互相覆盖**台账；且合并前统一校验，坏补丁进不了台账。
# 官方依据: docs/state/INDEX.md 记录纪律（口径要说出来 / 不凭记忆报数）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   docs/state/file-audit.jsonl 的 verdict/evidence/round/checked_by 四列
# ⚠ 只接受 `reviewed` / `derived-verified` 两种裁决；其它一律拒收（出册由生成器决定）。
# -----------------------------------------------------------------------------
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")  # 事实 58：管道下 GBK 会崩
ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "state" / "file-audit.jsonl"
ALLOWED = {"reviewed", "derived-verified"}
MIN_EVIDENCE = 12


def main() -> int:
    """入口。"""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--patch-dir", required=True, help="含 patch-*.jsonl 的目录")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    patch_dir = pathlib.Path(args.patch_dir)
    if not patch_dir.is_dir():
        print(f"[FAIL] 补丁目录不存在：{patch_dir}")
        return 2

    rows = [json.loads(l) for l in LEDGER.read_text(encoding="utf-8").splitlines() if l.strip()]
    by_path = {r["path"]: r for r in rows}

    applied = 0
    refused: list[str] = []
    seen: dict[str, str] = {}
    for patch in sorted(patch_dir.glob("patch-*.jsonl")):
        for line in patch.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                refused.append(f"{patch.name}: 非法 JSON（{exc}）")
                continue
            path = item.get("path", "")
            verdict = item.get("verdict", "")
            evidence = (item.get("evidence") or "").strip()
            if path not in by_path:
                refused.append(f"{path}: 不在台账里（路径不存在或已移出）")
                continue
            if verdict not in ALLOWED:
                refused.append(f"{path}: verdict={verdict!r} 不在 {sorted(ALLOWED)}")
                continue
            if len(evidence) < MIN_EVIDENCE:
                refused.append(f"{path}: evidence 过短")
                continue
            if verdict == "reviewed" and not evidence.startswith(("deep:", "skim:")):
                refused.append(f"{path}: reviewed 证据须以 deep:/skim: 开头")
                continue
            if path in seen:
                refused.append(f"{path}: 同一路径在多个补丁里重复出现（先到先得：{seen[path]}）")
                continue
            seen[path] = patch.name
            row = by_path[path]
            row["verdict"] = verdict
            row["evidence"] = evidence
            row["round"] = int(item.get("round") or 0)
            row["checked_by"] = item.get("checked_by") or patch.stem
            applied += 1

    print(f"补丁目录：{patch_dir}")
    print(f"  合并 {applied} 条 · 拒收 {len(refused)} 条")
    for item in refused[:15]:
        print("   [拒收]", item)
    if len(refused) > 15:
        print(f"   ... 其余 {len(refused) - 15} 条略")

    if args.dry_run:
        print("[dry-run] 未写台账")
        return 0

    with LEDGER.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"台账已更新：{LEDGER.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
