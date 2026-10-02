"""★ 审计：有没有**同一个文件被不同解析器读**的地方（★ 承事实 370 那条定则）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/check_same_parser.py
# 定位:   ★ 2026-10-03（轮 456）承**事实 370**。
#   ★★★ **那条定则**：★ 「**验证要用**同一个**解析器** —— ★ 不要用"另一个能读的"当验证**」。
#     ★ 而它的来由：★ `gen_dead_ends.py` 用 `json.loads` 读 `capabilities.yaml`，
#     ★★ 而我用 `yaml.safe_load` 验证 —— ★ 两者**对尾随逗号的容忍度不同** ⇒
#       ★★★ **我"验证通过"而生成器读不到** ⚠
#   ★★ **故本检查把它机器化**：★ 扫 `scripts/` 与 `tools/` 里对**同一个文件名**的读取，
#     ★ **看有没有两种解析器**（`json.loads` / `yaml.safe_load` / `ast.literal_eval` / `tomllib`）。
#   ⚠ **判据要保守**（★ 本仓一贯：宁可漏，不要噪音）：
#     ★ 只报**同一文件被≥2 种解析器读**的 ⇒ ★★ 而那**不是**"一定错"，★ 而是"**值得看一眼**" ✓
# 官方依据: 不适用（本仓自有的分析）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 按**文件名**分组，★ 报**解析器种类 ≥2** 的那些（★ 而**先报总数** —— 事实 357）。

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

#: ★ 解析器 → 它的正则（★ 只收"读文件"的形态）
PARSERS = (
    ("json.loads", re.compile(r"json\.loads\(")),
    ("yaml.safe_load", re.compile(r"yaml\.safe_load\(")),
    ("yaml.load", re.compile(r"yaml\.load\(")),
    ("tomllib", re.compile(r"tomllib\.load")),
    ("literal_eval", re.compile(r"ast\.literal_eval\(")),
)
#: ★ 关心的文件（★ 本仓的数据文件）
TARGETS = ("capabilities.yaml", "gate-classification.json", "judge-registry.json",
           "union-sources.json")


def main(argv: list) -> int:
    files = [p for d in ("scripts", "tools", "mcp-server") for p in (REPO_ROOT / d).glob("*.py")]
    print("  扫了 **%d** 个 .py（★ 先报数量 —— 事实 357）" % len(files))
    #: ★ 每个文件：★ 谁读了它、用什么解析器
    readers: dict = defaultdict(set)
    for f in files:
        try:
            t = f.read_text(encoding="utf-8")
        except Exception:                                      # noqa: BLE001
            continue
        for target in TARGETS:
            if target not in t:
                continue
            for name, rx in PARSERS:
                if rx.search(t):
                    readers[target].add(name)
    print("  关心的数据文件：%d 个（%s）" % (len(TARGETS), ", ".join(TARGETS)))
    bad = 0
    for target in TARGETS:
        used = readers.get(target, set())
        if not used:
            print("    %-28s ★ 没人读它（★ 或被别的机制读）" % target)
            continue
        mark = "⚠ **两种以上**" if len(used) > 1 else "✓ 一种"
        print("    %-28s %-14s %s" % (target, mark, ", ".join(sorted(used))))
        if len(used) > 1:
            bad += 1
    print()
    if bad:
        print("  ⚠★ **%d 个文件被两种以上解析器读** —— ★★ 而那**不是「一定错」**，" % bad)
        print("       ★ 而是「**值得看一眼**」：★ 若那两种解析器**容忍度不同**（★ 如尾随逗号 / 注释），")
        print("       ★★ 就会重演**事实 370** 那个坑（★ 一边读得了、另一边读不到）✓")
        return 0
    print("  ✓ 没有「同一文件被两种解析器读」的情形（★ 按本判据）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
