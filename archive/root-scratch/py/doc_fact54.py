"""记录：**来源块必须在 `def` 之前的注释块里，写在 docstring 里不算**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（纪律记录）
# 文件:   scripts/release_check.py（轮 42 新增 `_run_interface_ownership_probe` 时踩到）
#         scripts/check_provenance.py（**判据在这里**，不接受 docstring 形式的来源块）
# 定位:   轮 42 我给 release_check.py 加了一个探针函数，把 `# ── 来源 ──` 块
#         **写在函数的 docstring 里**（看起来更内聚）⇒ `check_provenance.py`
#         报「**25 行新增代码没有可追溯的出处**」，而报的行号是**后面**
#         `run_release_check` 里的行 —— **错误信息指向不了真因**。
#         **⇒ 本文件补上它：**
#         ① 来源块必须是**顶层注释块**（`#` 开头），放在目标的 `def` **之前**；
#         ② docstring（`\"\"\"…\"\"\"`）里的块**不被认**；
#         ③ 覆盖多个同级定义要靠 `# 覆盖: 后续同级定义`。
#         ⚠ 这与已知事实 35（「来源块覆盖范围不足有两种面孔」）是**同一族但不同面**。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 长内容走**短的单行字符串**（事实 48 定则）；跑完核对落盘。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
WS = Path(r"D:\AI\SW")

FACT54 = (
    "| 54 | **来源块必须是 `def` **之前**的顶层 `#` 注释块 —— 写在 docstring 里**不算**** —— "
    "2026-10-01 实测（轮 42）：我给 `release_check.py` 加了一个探针函数，把 `# ── 来源 ──` 块"
    "**写进函数的 docstring**（看起来更内聚）⇒ `scripts/check_provenance.py` 报"
    "「**25 行新增代码没有可追溯的出处**」，**而它报的行号是**后面** `run_release_check` 里的行**"
    "（因为插入把原来的覆盖链断开了）⇒ **错误信息指向不了真因**。"
    "**⇒ 三条：① 来源块放目标的 `def` **之前**；② docstring 里的块**不被认**；"
    "③ 覆盖多个同级定义靠 `# 覆盖: 后续同级定义`。**"
    "⚠ 与已知事实 35（覆盖范围不足的两种面孔）是**同一族但不同面** —— "
    "35 说的是**范围**不够，本条说的是**位置**不对。"
    "★ 附：同一轮还踩了一处**判据误报** —— 用 `\"[HIT]\" in output` 判检查结果，"
    "而该脚本的**说明文字里**就写着「报 `[HIT]` 时值得看」⇒ **明明 `[OK]` 却报 `hits`**。"
    "**⇒ 判「输出里有没有某个标记」一律**按行首**匹配，不用 `in`。** | "
    "`scripts/release_check.py` 的 `_run_interface_ownership_probe`；"
    "`scripts/check_provenance.py`（`_extend_to_code` 的调用链）；已知事实 35 |"
)


def main() -> int:
    # ① AGENTS.md
    f = WS / "AGENTS.md"
    src = f.read_text(encoding="utf-8").splitlines(keepends=True)
    if any(l.lstrip().startswith("| 54 |") for l in src):
        print("  ⚠ 事实 54 已存在")
    else:
        i = next((k for k, l in enumerate(src) if l.lstrip().startswith("| 53 |")), None)
        if i is None:
            print("  ✗ 找不到 | 53 | 行"); return 1
        src = src[:i + 1] + [FACT54 + "\n"] + src[i + 1:]
        f.write_text("".join(src), encoding="utf-8")
        print("  ✓ 已加已知事实 54")

    # ② ROADMAP 游标
    r = WS / "docs" / "ROADMAP.md"
    rt = r.read_text(encoding="utf-8")
    anchor = ("               ⇒ **下一步**：剩下 4 条未映射（`swFmDimPattern`/`swFmSolidToSheetMetal`/\n"
              "                 `swFmRefSurface`/`swFmFillet`）**需要人**逐条核（已列进 T-040 证据文档）\n")
    add = ("            ⑫ ★ **接口归属诊断已接进 `release_check.py`**（**非硬失败**，且**假绿可见**）：\n"
           "               `_run_interface_ownership_probe()` ⇒ 排在所有硬门禁之后、bundled 检查之前\n"
           "               ⇒ 三条差别：不 raise / `checked_nothing` 写进返回体 / 数据源缺失不算违规\n"
           "               ★ **它自己就在本轮抓到两处错**：① 用 `in` 判 `[HIT]` ⇒ 误报；\n"
           "                 ② 来源块写进 docstring ⇒ 来源门禁报 25 行缺出处（**已记进事实 54**）\n")
    if "接口归属诊断已接进" in rt:
        print("  ⚠ ROADMAP 已记录")
    elif anchor in rt:
        r.write_text(rt.replace(anchor, anchor + add, 1), encoding="utf-8")
        print("  ✓ ROADMAP 游标已更新")
    else:
        print("  ⚠ ROADMAP 找不到锚点")

    # ③ 落盘核对
    t2 = f.read_text(encoding="utf-8")
    rt2 = r.read_text(encoding="utf-8")
    print()
    print("  ── 落盘核对 ──")
    print("    AGENTS.md | 54 |: %d 行" % t2.count("\n| 54 |"))
    print("    含「docstring 里**不算**」: %s"
          % ("是 ✓" if "docstring 里**不算**" in t2 else "**否**"))
    print("    ROADMAP 含「接口归属诊断已接进」: %s"
          % ("是 ✓" if "接口归属诊断已接进" in rt2 else "**否**"))
    ks = [k for k, l in enumerate(t2.splitlines()) if l.lstrip().startswith("| 41 |")]
    if ks:
        bad = [l[:36] for l in t2.splitlines()[ks[0]:ks[0] + 14]
               if l.strip() and not l.lstrip().startswith("|")]
        print("    事实 41 起 14 行的非表格行: %s" % ("无 ✓" if not bad else "**有 %r**" % bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
