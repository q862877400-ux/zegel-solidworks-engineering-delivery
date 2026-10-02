"""@brief 给本次迁移改过的文件插入 `# ── 来源 ──` 块（check_provenance.py 要求）。

插在模块 docstring 之后（插在之前会被并进 docstring，块就不算数）。

# ── 来源 ──
# 仓库:   本项目自身（执行方对上游能力清单的迁移改造，非第三方移植）
# 文件:   tools/add_provenance_blocks.py
# 定位:   AGENTS.md §四 4.3「来源头注释」；scripts/check_provenance.py 的
#         REQUIRED_FIELDS = 仓库 / 文件 / 定位 / 未在本机实测。
# 许可:   本仓库 MIT。本文件为原创实现，无第三方代码引入。
# ⚠ 本工具只改注释，未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

BLOCK = """# ── 来源 ──
# 仓库:   本项目自身（执行方对上游能力清单的迁移改造，非第三方移植）
# 文件:   {path}
# 定位:   docs/capabilities-schema-proposal.md §1.2（`pilot`→五级迁移，裁断走选项 A）
#         与 §五 R11；AGENTS.md 铁律 1「每加一个能力必须能指认出处」。
# 许可:   本仓库 MIT。本文件为原创实现，无第三方代码引入。
# ⚠ 未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。本次是清单形状与授权判据的迁移，
#   不改变任何 COM 调用；授权等价性由 tests/test_unattended_equivalence.py 对冻结基线守住。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

TARGETS = (
    "apps/desktop/cad_workbench/engineering_orchestrator.py",
    "apps/desktop/cad_workbench/queue_worker.py",
    "scripts/capabilities.py",
    "scripts/check_union_conventions.py",
    "scripts/sw_capability_probe.py",
    "tests/test_cad_reliability.py",
    "tests/test_sw_capability_probe.py",
    "tests/test_unattended_equivalence.py",
    "tools/freeze_unattended_baseline.py",
    "tools/migrate_pilot_to_five_levels.py",
)


def docstring_end(lines: list[str]) -> int:
    """返回模块 docstring 最后一行的下标（0-based）；没有 docstring 则返回 -1。"""
    i = 0
    while i < len(lines) and (not lines[i].strip() or lines[i].lstrip().startswith("#")):
        i += 1
    if i >= len(lines):
        return -1
    head = lines[i].lstrip()
    m = re.match(r'^[rubfRUBF]{0,2}("""|\'\'\')', head)
    if not m:
        return -1
    quote = m.group(1)
    if head.count(quote) >= 2:
        return i
    j = i + 1
    while j < len(lines):
        if quote in lines[j]:
            return j
        j += 1
    return -1


def main() -> int:
    apply = "--apply" in sys.argv
    for rel in TARGETS:
        p = REPO / rel
        if not p.is_file():
            print("  ✗ 缺 %s" % rel)
            continue
        text = p.read_text(encoding="utf-8")
        if "── 来源 ──" in text:
            print("  · 已有来源块，跳过 %s" % rel)
            continue
        lines = text.splitlines()
        end = docstring_end(lines)
        block = BLOCK.format(path=rel)
        insert_at = end + 1 if end >= 0 else 0
        new = lines[:insert_at] + block.rstrip("\n").splitlines() + [""] + lines[insert_at:]
        out = "\n".join(new) + "\n"
        if apply:
            p.write_text(out, encoding="utf-8")
            print("  ✓ 已插入 %s（docstring 结束于 L%d）" % (rel, end + 1))
        else:
            print("  [dry-run] 将插入 %s（docstring 结束于 L%d）" % (rel, end + 1))
    if not apply:
        print("\n加 --apply 落地。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
