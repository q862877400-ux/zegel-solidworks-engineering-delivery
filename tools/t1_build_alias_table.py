"""★ T1-3：生成别名表 `docs/tool-aliases.md` + 裁判输入（★ 带诚实口径）。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

cand = json.loads((ROOT / "output" / "t1-alias-candidates.json").read_text(encoding="utf-8"))
gain = json.loads((ROOT / "output" / "t1-alias-gain.json").read_text(encoding="utf-8"))
by_tool = {r["tool"]: r for r in gain["summary"]}
#: ★ 每对的来源（op/keys/sources）
pair_of: dict = {}
for k in cand["kept"]:
    pair_of.setdefault(k["tool"], {"ops": set(), "keys": set(), "sources": set()})
    pair_of[k["tool"]]["ops"].add(k["op"])
    pair_of[k["tool"]]["keys"] |= set(k["keys"])
    pair_of[k["tool"]]["sources"] |= set(k.get("sources") or [])

improved = {t: r for t, r in by_tool.items() if r["gain"] and r["gain"] > 0}
flat = {t: r for t, r in by_tool.items() if not r["gain"]}

lines = [
    "# 工具别名表（★ 由 C5 手核数据机械筛 + 增益实测得出）",
    "",
    "> **生成物** —— 由 `tools/t1_build_alias_table.py` 产出，**不要手改**。",
    "> 输入：`specs/204-bunny-moat-batches/recon/c5-gap-handcheck.json`（另一个对话的 C5 手核，"
    "**只读复用**）+ 本仓 `all_specs()`。",
    "",
    "## 一 · 口径（★ 先说清这些数是怎么来的，否则数字没有意义）",
    "",
    "| 项 | 值 |",
    "|---|---|",
    "| 候选来源 | C5 手核里 `verdict=换名已有` 的 **24** 行（共 27 行，另有 3 行判「真缺」）|",
    "| 机械筛 | ★ `op` 或其 `key` 必须**作为词**出现在目标工具的 `name`/`title` 里 |",
    "| 筛后 | **79 对**，涉及 **52** 个工具（★ 丢掉 18 对子串疑云 + 7 对本仓没该工具）|",
    "| 增益判据 | 查询 = 该工具的 `op` + `keys`（★ **来自四家外部项目的词表，不是本仓编的**）；"
    "把别名追加进该工具 `doc` 后看排名变化 |",
    "| 结果 | ★ **45 个提升 · 0 个变差 · 7 个无变化** |",
    "",
    "★★ **本表「不算什么」（★ 必须与数字一起读）**：",
    "",
    "- ★ 它证明的是**机制有效**（用户说 `bbox`/`edges`/`jog` 时这些工具变得可命中），",
    "  ★★ **不证明用户真的会这么说** —— 查询词就是这个别名本身，**结构上近似同义反复**；",
    "- ★ 缓解证据：那些 `op`/`keys` 来自 **四家外部项目各自的工具名** ⇒ 四个独立团队都这么命名，",
    "  是该领域自然用词的**弱到中等**证据；",
    "- ★★ **不构成**任何「中文用户会怎么说」的证据（本表全是英文词）。",
    "",
    "## 二 · ★ 提升的别名（**45** 个工具 · 已过增益判据）",
    "",
    "| 工具 | 别名（op / keys）| 排名 现状 → 加别名 | 增益 | 来源项目 |",
    "|---|---|---|---:|---|",
]
for t, r in sorted(improved.items(), key=lambda x: -(x[1]["gain"] or 0)):
    p = pair_of[t]
    alias = ", ".join(sorted(p["ops"] | p["keys"]))
    srcs = ", ".join(sorted(s.split("/")[0] for s in p["sources"]))
    lines.append("| `%s` | %s | %s → **%s** | **+%d** | %s |"
                 % (t, alias, r["rank0"], r["rank1"], r["gain"], srcs or "—"))

lines += ["", "## 三 · ★ 无变化的（**7** 个 · **不采纳** —— 别名挣不到字节）", "",
          "| 工具 | 别名 | 排名 | 说明 |", "|---|---|---:|---|"]
for t, r in sorted(flat.items()):
    p = pair_of[t]
    lines.append("| `%s` | %s | %s | ★ 加了也不动 ⇒ 不接进 doc |"
                 % (t, ", ".join(sorted(p["ops"] | p["keys"])), r["rank0"]))

lines += [
    "",
    "## 四 · ★ 被机械筛丢掉的（**供复核，不进表**）",
    "",
    "★ 判据：`op`/`key` 不在目标工具的 `name`/`title` 里 ⇒ **疑子串命中**（★ 例：`bbox` → `toolbox_*`，",
    "只因 `toolbox` 含 `box`）。**这批是对方 `hits` 不能直接用的直接证据**。",
    "",
    "共 **18** 对，全表见 `output/t1-alias-candidates.json` 的 `dropped_substring_suspect`。",
    "",
    "## 五 · ★ 下一步（本表尚未接进工具 doc）",
    "",
    "1. ★ **先过语义闸**：由裁判逐条判「这个别名与这个工具**真的是同一件事**吗」——",
    "   ★ 重点查**泛词命中**（`drawing` / `appearance` / `sketch` 这类词在多工具里都出现，",
    "   ★ 例如 `balloon → drawing_create_auxiliary_view` 只是匹到了 `drawing`，**不是别名关系**）；",
    "2. ★ 过闸的才按 D-2 **只追加**一行 `别名:` 进 `doc`（不动 schema 契约、逐批提交可回退）；",
    "3. ★ 接进后用**现成的 48 题**复测（★ 带口径）⇒ SC-1。",
]
out = ROOT / "docs" / "tool-aliases.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("★ 写出 %s（%d 行）" % (out, len(lines)))
print("★ 提升 %d · 无变化 %d" % (len(improved), len(flat)))

#: ★ 裁判输入：每条候选对给「工具真实说明 + 别名 + 增益」，问"是不是同一件事"
J = ROOT / "output" / "t1-judge"
J.mkdir(parents=True, exist_ok=True)
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import register_capabilities as rc                                    # noqa: E402
by_name = {s.name: s for s in rc.all_specs()}
items = []
for t, r in sorted(by_tool.items()):
    p = pair_of[t]
    s = by_name.get(t)
    items.append({"tool": t, "aliases": sorted(p["ops"] | p["keys"]),
                  "title": getattr(s, "title", "") or "",
                  "doc": (getattr(s, "doc", "") or "")[:400],
                  "rank0": r["rank0"], "rank1": r["rank1"], "gain": r["gain"]})
N = 3
per = (len(items) + N - 1) // N
for i in range(N):
    (J / ("alias-in-%d.json" % i)).write_text(
        json.dumps({"judge_index": i, "items": items[i * per:(i + 1) * per]},
                   ensure_ascii=False, indent=1), encoding="utf-8")
print("★ 裁判输入 %d 份（每份 ≤%d 条）: %s" % (N, per, J))
