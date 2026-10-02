"""★ 批量判「缺口操作」：**先从四家取描述，再在我们这边找实现**（objective② 的判据）。

## 与 `union-gap-triage.md` 的区别（★ 那是它被更正的原因）
```
★ 分诊表按**词面**匹配 ⇒ "后缀候选"档抽样 24 条：真 6 · 部分 2 · **假 16（67%）**。
★★ 本脚本**从四家的描述出发**：★ 先知道那个操作**做什么**，再判我们有没有。
```

## ★★ 三条判据（★ 每条都能被反驳）
```
① **描述在手**：★ 该操作名在 `docs/operation-descriptions.json` 里有四家原文（★ 否则跳过 —— 不猜）；
② **实现不在**：★ 用 `sw_com_traps.find_real_implementations`（★ **已排除 `sw_api_*.py` 反射转储**）；
③ **名字不撞**：★ 从**四家的原工具名**去前缀后，看我们有没有**同名或名字含同样关键词**的工具/函数
   （★ 名字来源 = `rc.all_specs()`，★ **不手写**）。
⇒ ★ 三条合起来才给"真缺"：★ **有描述 + 我们无实现 + 名字也不撞**。
```

## ★★ 限度（★ 如实标，★ 写在 `--report` 的头部）
```
⚠ **"名字不撞"不是"能力不在"** —— ★ 我们的实现可能叫**完全不同的名字** ⇒
   ★ 本脚本的输出**只用于挑候选**（★ 真缺要人工核）。
⚠ 因此本脚本**不产出"我们缺 N 个能力"这种数**（★ 那正是 §10.3 更正掉的那个读法）。
```
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/judge_gap_candidates.py
# 定位:   objective②：给"缺口操作"做**有依据**的判定（描述在手 + 实现扫描 + 名字比对）。
# 官方依据: 不适用（★ 读的是四家 MIT 仓库的文本与我们的 ToolSpec）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "mcp-server"))

import sw_com_traps as TRAPS  # noqa: E402

DESC_PATH = REPO_ROOT / "docs" / "operation-descriptions.json"
TRIAGE = REPO_ROOT / "docs" / "union-gap-triage.md"
OUT = REPO_ROOT / "docs" / "union-gap-batch-judgement.md"

#: ★ 词法归一：★ 把 `snake_case` 的名字切词（★ 判"名字撞不撞"用词集，★ 不用整串）
def _words(name: str) -> set[str]:
    return {w for w in re.split(r"[_\W]+", name.lower()) if w and w not in ("sw", "sws", "solidworks")}


def _our_names() -> list[str]:
    """★ 我们这边**所有**工具名 / 函数名 / 模块名（★ 从 `rc.all_specs()`，★ 不手写）。"""
    import register_capabilities as rc

    out: list[str] = []
    for s in rc.all_specs():
        out.extend([s.name or "", s.function or "", s.module or ""])
    return [x for x in out if x]


def _gap_ops() -> list[str]:
    """★ 分诊表里的缺口操作名（★ 只取表行里的第一列）。"""
    if not TRIAGE.is_file():
        return []
    out = []
    for line in TRIAGE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*`([a-z0-9_]+)`\s*\|", line)
        if m:
            out.append(m.group(1))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="只判前 N 条（0 = 全部）")
    ap.add_argument("--show", type=int, default=25)
    args = ap.parse_args()

    if not DESC_PATH.is_file():
        print("  **缺 %s** ⇒ 先跑 tools/extract_operation_descriptions.py" % DESC_PATH.name)
        return 1
    descs = json.loads(DESC_PATH.read_text(encoding="utf-8"))["descriptions"]
    ours = _our_names()

    rows = []
    for op in _gap_ops():
        if op not in descs:                      #: ★ 判据①：没描述 ⇒ 不猜，跳过
            continue
        text = " ".join(descs[op].values())
        #: ★ 判据②：实现扫描（★ 已排除反射转储）—— ★ 用操作名转驼峰去试
        camel = "".join(w.capitalize() for w in op.split("_"))
        hits = TRAPS.find_real_implementations(camel) or TRAPS.find_real_implementations(op)
        #: ★ 判据③：名字词集是否被我们某个名字包含
        need = _words(op)
        named = [n for n in ours if need and need <= _words(n)]
        verdict = "真缺候选" if (not hits and not named) else "有候选"
        rows.append({"op": op, "desc": text[:160], "impl_hits": hits[:2],
                     "name_hits": named[:2], "verdict": verdict})

    real = [r for r in rows if r["verdict"] == "真缺候选"]
    print("  有描述可判: **%d** 条" % len(rows))
    print("  其中「真缺候选」（★ 无实现 + 名字不撞）: **%d**" % len(real))
    print("  「有候选」: **%d**" % (len(rows) - len(real)))
    print()
    for r in rows[:args.show]:
        print("  %-26s %-10s %s" % (r["op"], r["verdict"],
                                    (r["impl_hits"] or r["name_hits"] or [r["desc"][:52]])[0]))

    body = ["# 缺口操作的批量判定（★ 由 `tools/judge_gap_candidates.py` 生成）", "",
            "> ⚠ **限度**：\"名字不撞\"**不是**\"能力不在\" —— 我们的实现可能叫完全不同的名字。",
            "> ★ 本表**只用于挑候选**；★ **不产出\"我们缺 N 个能力\"这种数**（§10.3 更正掉的读法）。", "",
            "## 统计", "",
            "| 口径 | 数 |", "|---|---|",
            "| 有描述可判 | %d |" % len(rows),
            "| **真缺候选**（无实现 + 名字不撞） | **%d** |" % len(real),
            "| 有候选 | %d |" % (len(rows) - len(real)), "",
            "## 真缺候选（★ 逐条带四家描述，★ 供人工核）", "",
            "| 操作 | 四家怎么说 | 我们有无实现 |", "|---|---|---|"]
    for r in real:
        body.append("| `%s` | %s | %s |" % (r["op"], r["desc"][:120].replace("|", "/"),
                                            "无" if not r["impl_hits"] else r["impl_hits"][0]))
    OUT.write_text("\n".join(body) + "\n", encoding="utf-8")
    print()
    print("  产物: %s" % OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
