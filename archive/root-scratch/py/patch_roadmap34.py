"""更新 ROADMAP 游标：把「后端限制已写进清单」记上。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（文档更新）
# 文件:   C:\\swprojects\\sw-skill-fork\\capabilities.yaml（`backend_catalog` 的限制已具体化）
#         D:\\AI\\SW\\AGENTS.md 已知事实 47 / 48
# 定位:   清单承载了结论之后，把「下一步」游标同步。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 长内容走**短的单行字符串**（事实 48 定则）；跑完核对落盘。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROADMAP = Path(r"D:\AI\SW\docs\ROADMAP.md")

ANCHOR = "                  ⚠ **不要再用「换个参数试试」继续试** —— 已穷尽\n"
ADD = (
    "                · ★ **该结论已**写进清单****：`capabilities.yaml` 的 "
    "`backend_catalog[solidworks-com-pywin32]`\n"
    "                  限制**具体化**（点名接口/成员 + `0x80010105` + 证据脚本）；\n"
    "                  `capabilities[sheet_metal]` 补**真机实测状态**（6 个入口里 **2 个可跑**）\n"
    "                  ⇒ **状态由清单承载**（AGENTS.md §一 的要求）\n"
)


def main() -> int:
    t = ROADMAP.read_text(encoding="utf-8")
    if "该结论已**写进清单**" in t:
        print("  ⚠ 已记录")
    elif ANCHOR in t:
        t = t.replace(ANCHOR, ANCHOR + ADD, 1)
        ROADMAP.write_text(t, encoding="utf-8")
        print("  ✓ ROADMAP 游标已更新")
    else:
        print("  ⚠ 找不到锚点")
        return 1

    # 落盘核对（事实 48 第 ② 条）
    t2 = ROADMAP.read_text(encoding="utf-8")
    print()
    print("  ── 落盘核对 ──")
    print("    ROADMAP 含「写进清单」: %s" % ("是" if "写进清单" in t2 else "**否**"))
    print("    ROADMAP 含「2 个可跑」: %s" % ("是" if "2 个可跑" in t2 else "**否**"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
