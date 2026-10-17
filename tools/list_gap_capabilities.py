"""★ 列出能力清单里**没真正可用**的条目（`not_implemented` / `stitched`）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/list_gap_capabilities.py
# 定位:   ★ 回答「还有没有没实现的功能」时，**必须以 `capabilities.yaml` 的 `level` 为准**：
#           `verified` = 有我们自己的运行证据 · `stitched` = 代码写好但**没真机跑过** ·
#           `not_implemented` = 没做 ✓（五级枚举见 `docs/union-conventions.md`）
#         ★★ 教训：本文件第一版我用 `Select-String` 按 `level:\s*X` 找 —— **一条也没找到**，
#           因为该文件是 **JSON**（`"level": "verified"`，**带引号**）⇒ 按 YAML 形态写判据 = 空转 ✓✗
# 官方依据: 不适用（本仓声明层）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

GAP_LEVELS = ("not_implemented", "stitched")


def main() -> int:
    data = json.loads((ROOT / "capabilities.yaml").read_text(encoding="utf-8"))
    caps = data.get("capabilities")
    if not isinstance(caps, list):
        #: ★ 找不到就**如实说**，不猜结构（铁律 5）
        print("★ `capabilities` 不是 list ⇒ 结构变了，本脚本要看一眼再改（键：%s）"
              % list(data.keys()))
        return 1

    by_level: dict[str, int] = {}
    for c in caps:
        by_level[str(c.get("level"))] = by_level.get(str(c.get("level")), 0) + 1

    print("★ 能力清单条目 **%d** 条，按 level 分组：" % len(caps))
    for lv, n in sorted(by_level.items(), key=lambda kv: -kv[1]):
        mark = "  ← 没真正可用" if lv in GAP_LEVELS else ""
        print("    %-18s %3d%s" % (lv, n, mark))

    print()
    for lv in GAP_LEVELS:
        rows = [c for c in caps if str(c.get("level")) == lv]
        print("★★ `%s`（%d 条）：" % (lv, len(rows)))
        for c in rows:
            print("    · id=%-42s %s" % (str(c.get("id"))[:42], str(c.get("name"))[:58]))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
