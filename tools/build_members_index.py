"""★ 建**全量成员索引**（接口 × 成员），并统计"同名成员分布在几个接口上"。

★ ★★★ 为什么必须有它（★ 这是**业主那个问题的答案本身**）：
  ★ 我先做的 `scan_obsolete_usage.py` **只按成员名对废弃名单** ⇒ 报 **870 处**，
  ★★ 而头几名 **全是假阳性**：`FeatureCut4`（★ 本仓**事实 1** 说它才是正确入口）·
    `GetBodies2` / `Name` / `GetEdges` / `CreateLine`（★ **同名不同接口**：
    `IModelDoc2.GetBodies2` 没废弃，废弃的是 `IComponent2.GetBodies2`）。
  ⇒ ★★ **按名字对人，等于没对** —— ★ 与**事实 36**（同名接口分属不同族）同族。
★ 本脚本产出两份东西：
  ① `official-members-index.json`：★ 每个接口的每个成员（含是否废弃 + 后继）；
  ② ★ **同名歧义表**：★ 一个成员名出现在 N 个接口上、其中 M 个是废弃的
     ⇒ ★ 只有 `M == N` 时"按名字判废弃"才**不含歧义**。
★ 只读官方文档。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/build_members_index.py
# 定位:   建**全量成员索引**（接口 × 成员），并统计"同名成员分布在几个接口上"。
# 官方依据: 官方源 `C:\swapi\types\**`（★ 逐条见文件内引用）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
SWAPI = Path(r"C:\swapi\types")
RECON = Path(
    Path(__file__).resolve().parents[1] / "specs" / "202-user-coverage-gaps" / "recon"
)

OBS_LINE = re.compile(r"Obsolete|Superseded by", re.I)
HEAD_SKIP = (
    "#",
    "---",
    "type:",
    "member:",
    "kind:",
    "assembly:",
    "namespace:",
    "category:",
)


def main() -> int:
    started = time.time()
    per_iface: dict = defaultdict(list)
    pages = 0
    for iface_dir in sorted(p for p in SWAPI.iterdir() if p.is_dir()):
        for page in sorted(iface_dir.glob("*.md")):
            pages += 1
            try:
                txt = page.read_text(encoding="utf-8", errors="replace")
            except Exception:  # noqa: BLE001
                continue
            head = txt.split("\n## ", 1)[0]
            obs_line = ""
            for l in head.splitlines():
                s = l.strip()
                if s and not s.startswith(HEAD_SKIP) and OBS_LINE.search(s):
                    obs_line = s
                    break
            succ = ""
            m = re.search(r"\[\[([^\]]+)\]\]", obs_line)
            if m:
                succ = m.group(1).strip()
            per_iface[iface_dir.name].append(
                {
                    "member": page.stem,
                    "obsolete": bool(obs_line),
                    "successor": succ,
                    "obsolete_line": obs_line[:200],
                }
            )
    #: ★ 同名歧义：★ 一个成员名 → 出现在哪些接口、其中几个废弃
    by_name: dict = defaultdict(list)
    for iface, members in per_iface.items():
        for m in members:
            by_name[m["member"]].append(
                {
                    "interface": iface,
                    "obsolete": m["obsolete"],
                    "successor": m["successor"],
                }
            )
    ambiguous = {
        n: v
        for n, v in by_name.items()
        if len(v) > 1
        and any(x["obsolete"] for x in v)
        and not all(x["obsolete"] for x in v)
    }
    pure_obs = {n: v for n, v in by_name.items() if all(x["obsolete"] for x in v)}

    (RECON / "official-members-index.json").write_text(
        json.dumps(
            {
                "at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "scanned_pages": pages,
                "interfaces": len(per_iface),
                "unique_member_names": len(by_name),
                "per_interface": {k: v for k, v in per_iface.items()},
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )

    print(
        "★ 扫了官方页 **%d** 篇 · 接口 **%d** 个 · **唯一成员名 %d** 个"
        % (pages, len(per_iface), len(by_name))
    )
    print(
        "★ 其中：★ **在所有接口上都废弃**的名字 **%d** 个（★ 只有这批「按名字判」才不含歧义）"
        % len(pure_obs)
    )
    print("★★ **有歧义的**（★ 部分接口废弃、部分不废弃）**%d** 个" % len(ambiguous))
    print()
    print("★ 歧义样例（★ 这些名字**不能**按名字判废弃）：")
    print("%-30s %-9s %s" % ("成员名", "接口数", "废弃的在哪个接口"))
    print("-" * 112)
    for n in sorted(ambiguous, key=lambda x: -len(ambiguous[x]))[:16]:
        v = ambiguous[n]
        obs = [x["interface"] for x in v if x["obsolete"]]
        ok = [x["interface"] for x in v if not x["obsolete"]]
        print(
            "%-30s %-9d ★废弃:%-34s ☆没废弃:%s"
            % (n[:29], len(v), ",".join(obs)[:33], ",".join(ok)[:26])
        )
    print()
    #: ★★ 我上一版误报的那几个，逐个摊开
    print("★ 上一版扫描的头几名，逐个摊开（★ 看它们是不是假阳性）：")
    for n in (
        "GetBodies2",
        "Name",
        "GetEdges",
        "CreateLine",
        "FeatureCut4",
        "CreateCircleByRadius",
    ):
        v = by_name.get(n) or []
        if not v:
            print("   %-24s ★ 官方索引里没有这个名字" % n)
            continue
        obs = [x["interface"] for x in v if x["obsolete"]]
        print(
            "   %-24s 接口数=%-3d ★废弃的=%d 个 %s ⇒ %s"
            % (
                n,
                len(v),
                len(obs),
                ("(在 " + ",".join(obs[:2]) + ")") if obs else "",
                "★ **假阳性**" if len(obs) < len(v) else "★ 真废弃",
            )
        )
    print()
    print(
        "★ 产出:",
        RECON / "official-members-index.json",
        "（%.1f s）" % (time.time() - started),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
