r"""@brief 探针：**哪些 `scripts/sw_*.py` 模块没有任何能力条目提到它**。

## 为什么（2026-10-01 轮 118，Spec Kit `037`）
`036` **碰巧**发现 `sw_sketch.py` 没有能力条目（它是 `sketch_query` 的载体，但当时没人登记）。
⇒ 本轮**系统核对**：`scripts/sw_*.py` ↔ `capabilities.yaml` 的对应关系。
★ 这属 **A1/A4 的直接判据**，**且可以机器化**。

## 判法
1. 列出 `scripts/sw_*.py`（**排除 API 名登记表** —— 它们不是能力模块）；
2. 把 `capabilities.yaml` 全文（含 `label` / `limitations` / `source_evidence`）当文本；
3. 每个模块名去里面找 ⇒ **一次都没出现**的列出来。

⚠ **只出清单，不下"该建条目"的结论** —— 一个模块可能：
* 是**辅助件**（`sw_connect` / `sw_com_traps`）⇒ 本就不该有独立条目；
* 被某个条目的**描述覆盖**但没写模块名 ⇒ **假阳性**；
* 真的是**漏登记** ⇒ 那才是发现。
⇒ **三类要人工分**。

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_capability_coverage.py
# 定位:   给 Spec Kit `037` 取证：能力条目对 `scripts/` 模块的覆盖是否有洞。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

#: ⚠ 这些不是"能力模块"：API 名登记表 / COM 辅助 / 纯知识表
NOT_A_CAPABILITY = re.compile(
    r"sw_api_|^sw_com_traps|^sw_connect|^sw_automation_knowledge|^sw_preflight"
)


def modules() -> list:
    return sorted(
        p.stem
        for p in (ROOT / "scripts").glob("sw_*.py")
        if not NOT_A_CAPABILITY.search(p.stem)
    )


# ⚠⚠ **2026-10-01 轮 118 的结论：本探针不能当判据，而且它问的问题本身是错的。**
#   两版判据都失败（模块名 / 函数名，各报 43 个；并集仍 38 个，假阳性约 59%）——
#   因为**能力条目是域级的**（routing / weldments / surface_modeling …），
#   **本来就不写模块文件名**。
#   ★ 而 **A1 的单位是「域」，不是「文件」** ⇒ 条目**已经在正确的粒度上**，
#     「模块名没出现」**根本不是缺陷**。
#   ⚠ 详见 docs/module-capability-coverage.md。**不要把它接进门禁。**


def main() -> int:
    caps = (ROOT / "capabilities.yaml").read_text(encoding="utf-8", errors="replace")
    mods = modules()
    print("`scripts/sw_*.py` 里**可能承载能力**的模块：**%d** 个" % len(mods))
    print(
        "  （已排除 API 名登记表 / COM 辅助 / 知识表 / 预检：%s）"
        % NOT_A_CAPABILITY.pattern
    )

    print("⚠⚠ **判据换过一次（轮 118 当场发现）**：")
    print("   第一版判「**模块名**是否出现在 capabilities.yaml 文本里」⇒")
    print("   把 `sw_routing`↔`routing`、`sw_weldment`↔`weldments`、")
    print(
        "   `sw_topology`↔`topology_optimization` 这些**明明有条目**的模块全报成「没覆盖」"
    )
    print("   （**假阳性**）—— 因为条目用的是**域标签**，**不写模块文件名**。")
    print("   ⇒ 改用**更具体**的判据：**该模块的公开函数名**有没有被提到。")
    print()

    never, sometimes = [], []
    for m in mods:
        t = (ROOT / "scripts" / (m + ".py")).read_text(
            encoding="utf-8", errors="replace"
        )
        pub = [f for f in re.findall(r"^def (\w+)\(", t, re.M) if not f.startswith("_")]
        hit = [f for f in pub if re.search(r"\b%s\b" % re.escape(f), caps)]
        (sometimes if hit else never).append(m)

    print("=== 被覆盖（≥1 个公开函数名被提到）：**%d** 个模块 ===" % len(sometimes))
    print()
    print("=== ★ **一个函数名都没被提到**：**%d** 个模块 ===" % len(never))
    for m in never:
        t = (ROOT / "scripts" / (m + ".py")).read_text(
            encoding="utf-8", errors="replace"
        )
        pub = [f for f in re.findall(r"^def (\w+)\(", t, re.M) if not f.startswith("_")]
        print("  **%s**（%d 个公开函数，**0 个**被提到）" % (m, len(pub)))
        print("      例: %s" % ", ".join(pub[:5]))
    print()
    print("⚠ **仍不下「该建条目」的结论** —— 三类要人工分：")
    print("  ① 辅助件（本就不该有独立条目）")
    print("  ② 被某条目的描述覆盖、只是没写函数名（**假阳性**）")
    print("  ③ 真的漏登记（**那才是发现**）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
