"""★ 扫描：哪些工具声明了 `*_mm` 参数**却没有换算**（本缺陷的普查）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/scan_mm_without_conversion.py
# 定位:   规格 206 / 本轮**同一类缺陷的普查**。已确证两处真缺陷：· `solidworks_extrude
#           _{boss,cut,midplane}`（已修，提交 0055b7c）· `solidworks_sketch_add_circle`
#           （本轮踩到：给 (30,43,r7) 画出 30 米外的圆）
#         ★ 判据（静态可判）：**声明了 `Param("*_mm")`，而该文件里没有 `derived_args`**
#           ⇒ 那个 `_mm` 值只能经 `param_alias` **改名直传**（或同名直传）⇒ **不换算** ✓
#         ⚠ 本扫描**只筛候选**：`derived_args` 也可能只服务别的参数 ⇒ **命中≠确证**，
#           要读那一条再判（★ 判据要写「不算什么」）✓
# 官方依据: 不适用（本仓声明层的静态普查）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
MCP = ROOT / "mcp-server"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: ★ 复用 `sw_connect.mm` 的那句 import —— 有它才说明这文件真的会换算
MM_IMPORT = re.compile(
    r"from\s+scripts\.sw_connect\s+import[^\n]*\bmm\b|sw_connect\.mm\("
)


def main() -> int:
    rows = []
    for p in sorted(MCP.glob("tool_specs_batch*.py")):
        text = p.read_text(encoding="utf-8", errors="replace")
        mm_params = sorted(set(re.findall(r'Param\(\s*"([A-Za-z_]*_mm)"', text)))
        if not mm_params:
            continue
        has_derived = "derived_args" in text
        has_mm_call = bool(MM_IMPORT.search(text))
        rows.append(
            {
                "file": p.name,
                "mm_params": mm_params,
                "derived_args": has_derived,
                "uses_mm": has_mm_call,
                "suspect": (not has_derived) and (not has_mm_call),
            }
        )

    suspects = [r for r in rows if r["suspect"]]
    print("★ 声明了 `*_mm` 的 tool_specs 文件: **%d** 个" % len(rows))
    print(
        "★★ 其中**既无 derived_args 也无 mm() 调用**（= 疑似不换算）: **%d** 个"
        % len(suspects)
    )
    print()
    for r in suspects:
        print("  %-28s %s" % (r["file"], ", ".join(r["mm_params"])[:120]))
    print()
    print(
        "★ 本扫描「不算什么」：① `derived_args`/`mm()` 出现**不等于**那些 `_mm` 都被换算；"
    )
    print(
        "   ② 反过来，命中只是**候选** —— 有些 `_mm` 参数的能力层本身就吃毫米（★ 例如"
    )
    print("      `sw_part.sketch_spline` 内部换算）⇒ ★ **要读那一条声明再判** ✓")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
