"""记录踩了 **6 次**的坑：**往 Python 源码里内联长文本**；并更新 ROADMAP 游标。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（文档更新）
# 文件:   capabilities.yaml 的 `backend_catalog` 限制段（事实 47 的呼应）
#         D:\\AI\\SW\\_t011_section28.md（本轮改用的**独立文件**做法）
# 定位:   2026-10-01 的教训。本会话在「把长文本写进 Python 源码」上**踩了 6 次**：
#           ① 文档串里嵌同类引号          ② 补丁脚本插真换行（第 3 次那回）
#           ③ `%`-格式串里的 `100%`        ④ `\\A` 之类坏转义
#           ⑤ `sw_sheet_metal` 状态表断行  ⑥ 本轮：`write` 工具写的 Python 里
#              字符串被真实换行截断 ⇒ `SyntaxError: unterminated string literal`（连踩两次）
#         **⇒ 定则：长内容一律先写成**独立文件**（`.md` / `.txt`），
#            再用**最短**的读写脚本搬运。不要在 Python 源码里拼长字符串。**
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
WS = Path(r"D:\AI\SW")

# 事实 48 —— 用**单行独立字符串**，绝不跨行拼接
FACT48 = (
    "| 48 | **长文本不要内联进 Python 源码** —— 本会话在这一件事上**踩了 6 次**："
    "文档串里嵌同类引号 / 补丁脚本插真换行 / `%`-格式串里的 `100%` / `\\A` 之类坏转义 / "
    "状态表字符串断行 / 以及 `write` 工具写的 Python 里字符串被**真实换行**截断"
    "（`SyntaxError: unterminated string literal`，**连踩两次**）。"
    "⚠ 最坑的一次：**脚本语法错 ⇒ 内容没写进去，而外面的 `git add -A && commit` 照跑**"
    "⇒ 产生「提交信息说改了文档、实际只提交了那个坏脚本」的**假提交**"
    "（2026-10-01 连出两次）。"
    "**⇒ 定则两条：① 长内容先写成**独立文件**（`.md`），再用最短脚本搬运；"
    "② 批量脚本跑完**必须核对落盘**（`grep` 一下目标文件），**不能只看脚本的 stdout**。** | "
    "`D:\\AI\\SW\\_t011_section28.md`（正确做法）；`doc_fact47.py`（错误做法的两次失败） |"
)

ROADMAP_ADD = (
    "                · ★★ **`create_one_bend`/`create_edge_flange`/`create_gusset` 三条："
    "**pywin32 后端到不了**\n"
    "                  （事实 47）——**两轮 20+ 种形态穷尽**：`SetFixedFace` 七种数组包装×两个重载"
    "全报\n"
    "                  `类型不匹配`；`AccessSelections` 传空 Dispatch 报 **`0x80010105`**"
    "（与事实 28 同码）\n"
    "                  ⇒ 与 `capabilities.yaml` 早已记录的「不能调用仅进程内非托管 C++ 的指针接口」吻合\n"
    "                  ⚠ **不要再用「换个参数试试」继续试** —— 已穷尽\n"
)


def main() -> int:
    # ① AGENTS.md 事实 48
    f = WS / "AGENTS.md"
    t = f.read_text(encoding="utf-8")
    i = t.find("| 47 |")
    if i < 0:
        print("  ✗ 找不到 | 47 |")
        return 1
    if "| 48 |" in t:
        print("  ⚠ 事实 48 已存在")
    else:
        e = t.find("\n", i) + 1
        f.write_text(t[:e] + FACT48 + "\n" + t[e:], encoding="utf-8")
        print("  ✓ AGENTS.md 已加已知事实 48")

    # ② ROADMAP 游标
    r = WS / "docs" / "ROADMAP.md"
    rt = r.read_text(encoding="utf-8")
    anchor = "                · ★ **`create_one_bend` 真因已查明并修复**"
    if "pywin32 后端到不了" in rt:
        print("  ⚠ ROADMAP 已记录")
    elif anchor in rt:
        # 插在那一段之后（找该段最后一行）
        j = rt.find(anchor)
        k = rt.find("\n", rt.find("\n", j) + 1)          # 粗略取两行后
        rt = rt[:k + 1] + ROADMAP_ADD + rt[k + 1:]
        r.write_text(rt, encoding="utf-8")
        print("  ✓ ROADMAP 游标已更新")
    else:
        print("  ⚠ ROADMAP 找不到锚点")

    # ③ **落盘核对**（事实 48 的第 2 条定则：不能只看 stdout）
    t2 = f.read_text(encoding="utf-8")
    print()
    print("  ── 落盘核对 ──")
    print("    AGENTS.md  | 47 | : %d 行" % t2.count("\n| 47 |"))
    print("    AGENTS.md  | 48 | : %d 行" % t2.count("\n| 48 |"))
    rt2 = r.read_text(encoding="utf-8")
    print("    ROADMAP 含「pywin32 后端到不了」: %s" % ("是" if "pywin32 后端到不了" in rt2 else "**否**"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
