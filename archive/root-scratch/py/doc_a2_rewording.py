"""记录一处**取退出码的测量坑**；并把 A2 的措辞澄清（消解两种读法）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（纪律 + 验收判据澄清）
# 文件:   scripts/check_union_conventions.py（6 项检查，全 PASS，退出码 0）
#         tools/union-sources.json（**来源级** provenance：4 家，字段齐全）
#         tools/build_union_map.py（地图生成器）
# 定位:   两件事。
#
#   **① 记录一处测量坑。** 本轮做来源级门禁的**负例测试**时：
#      · `python check_union_conventions.py | Select-Object -First 14` ⇒ 报 `[FAIL] 规则 5`
#        并**点名 3 条坏来源**（真源 repo 非 owner/repo / `x/y` 许可 GPL-3.0 / `p/q` 缺 note）
#        —— **检查本身完全正常。**
#      · 但那次读到的 `$LASTEXITCODE` 是 **0**；而还原后另一次读到 **1**。
#      **⇒ 结论：`python ... | Select-Object ...` 之后读 `$LASTEXITCODE` **不可靠**。**
#      **正确做法**：`python x.py > out.txt 2>&1` 再读 `$LASTEXITCODE`，
#      或 `$o = python x.py 2>&1; $code = $LASTEXITCODE`（**赋值，不接管道**）。
#      ⚠ 本会话多轮用的是后者（可靠）；**只在本轮那一处用了前者**。
#
#   **② 澄清 A2 的措辞。** A2 原文「每个**并入条目**带 `provenance`」里的「条目」
#      有**两种读法，答案相反**（已知事实 41 的更正）：
#      · **来源条目** ⇒ `tools/union-sources.json` **4/4 完整** ⇒ 满足（**门禁查这里**）
#      · **能力条目** ⇒ `capabilities[].provenance` 1/29 ⇒ 不满足
#      **而门禁实现的是窄读法**（只有 `source_verified` 才强制，**本仓库 0 条**）。
#      **⇒ 把 A2 改成**两层都写明**（更清楚，不比原来弱）。**
#
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

#: A2 的新措辞 —— **两层都写明**
A2_OLD = ("| A2 | 每个并入条目带 `provenance`（`owner/repo` 全名 + 许可 + 文件 + 来源验证状态） "
          "| grep 抽查 10 条，100% 命中 |")
A2_NEW = ("| A2 | **两层 provenance 都要**：① **来源级** —— `tools/union-sources.json` 的每个来源带 "
          "`owner/repo` 全名 + 许可（白名单内）+ `declared_verified` + `note`；"
          "② **能力级** —— `capabilities[].provenance` 对**来源派生**的条目（`level: source_verified`）"
          "必须齐 `repo`/`license`/`files`/`upstream_verified` 四字段。"
          "⚠ ①与②**不是同一件事**：① 说的是「哪几家、什么许可、他们自己声明跑过什么」；"
          "② 说的是「这一条能力是从哪条来源派生的」。**`level: verified` 只表示"
          "「有我们自己的运行证据」，不表示「代码是我们写的」—— 两条线不该混。** "
          "| ① `python scripts/check_union_conventions.py` 的「规则 5 · 出处与许可」段；"
          "② 同门禁的「清单形状」段（现 `source_verified` 条目数为 **0**，"
          "故②**空满足**；一旦新增 `source_verified` 条目，②即强制生效）|")

FACT50 = (
    "| 50 | **`python x.py \\| Select-Object ...` 之后读 `$LASTEXITCODE` **不可靠**** —— "
    "2026-10-01 实测：同一条命令，接管道时读到 **0**、不接管道（重定向到文件）时读到 **1**。"
    "**⇒ 正确做法二选一：① `python x.py > out.txt 2>&1` 再读 `$LASTEXITCODE`；"
    "② `$o = python x.py 2>&1; $code = $LASTEXITCODE`（**赋值，不接管道**）。**"
    "⚠ 本会话多轮用的是 ②（可靠）；只在本轮那一处用了 ① 的错误形式，"
    "**一度误以为门禁是红的**（实际 6 项全 PASS、退出码 0）。"
    "**⇒ 教训：判「门禁绿不绿」时，先确认**退出码的读法本身**是可靠的。** | "
    "`D:\\AI\\SW\\AGENTS.md` 已知事实 7 那类「返回值不可信」在本机 shell 层的同类；"
    "证据：同一条 `check_union_conventions.py` 两种读法给出不同退出码 |"
)


def main() -> int:
    f = WS / "AGENTS.md"
    t = f.read_text(encoding="utf-8")

    # ① A2 措辞澄清（§一 验收标准表）
    n_a2 = 0
    if A2_OLD in t:
        t = t.replace(A2_OLD, A2_NEW, 1)
        n_a2 = 1
    print("  ✓ A2 措辞已澄清（两层都写明）" if n_a2 else "  ⚠ A2 未匹配（可能已改）")

    # ② 事实 50
    n50 = 0
    i = t.find("| 49 |")
    if i >= 0 and "| 50 |" not in t:
        e = t.find("\n", i) + 1
        t = t[:e] + FACT50 + "\n" + t[e:]
        n50 = 1
    print("  ✓ 已加已知事实 50" if n50 else "  ⚠ 事实 50 未加（已存在或找不到 49）")

    f.write_text(t, encoding="utf-8")

    # ③ 落盘核对（事实 48 第 ② 条）
    t2 = f.read_text(encoding="utf-8")
    print()
    print("  ── 落盘核对 ──")
    print("    A2 行含「两层 provenance 都要」: %s"
          % ("是 ✓" if "两层 provenance 都要" in t2 else "**否**"))
    print("    A2 行仍以 | 开头（表格合法）: %s"
          % ("是 ✓" if any(l.lstrip().startswith("| A2 |") for l in t2.splitlines()) else "**否**"))
    print("    AGENTS.md | 50 |: %d 行" % t2.count("\n| 50 |"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
