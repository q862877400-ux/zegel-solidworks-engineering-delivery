"""记录轮 45 的三条发现：编码 / 盘根 / 替换扫描碰注释。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（纪律记录）+ Python 标准库 `subprocess` / `pathlib` 文档
# 文件:   scripts/cad_installation.py（**真实功能 bug** 已修）
#         tests/test_cad_studio_cli.py 等 6 个文件（编码已修）
#         scripts/fea_analysis.py（我的替换扫描曾碰坏它的注释）
# 定位:   轮 45 **修掉全部 5 个基线失败** ⇒ 全量回归 **0 failed / 861 passed**（首次全绿）。
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

F58 = (
    "| 58 | **`subprocess.run(..., text=True)` 不给 `encoding=` 在**中文 Windows 上会炸**** —— "
    "父进程用 `locale.getpreferredencoding()`（本机 **GBK**）去解子进程的 **UTF-8 中文**输出 ⇒ "
    "`UnicodeDecodeError: 'gbk' codec can't decode …` ⇒ **`completed.stdout` 变成 `None`** ⇒ "
    "下游 `json.loads(None)` 抛 `TypeError`（**错误信息指向不了真因**）。"
    "**⇒ 修法：一律补 `encoding=\"utf-8\", errors=\"replace\"`**（与子进程实际输出一致；"
    "`errors=\"replace\"` 保证再遇到别的编码也不至于整条测试崩掉）。"
    "★ 2026-10-01（轮 45）：本仓 **11 处**这样写，**4 个基线失败全因此**；修完全量回归 **0 failed**。"
    "⚠ **同一轮还踩了扫描的假阳性**：我按「第一个 `)`」截断调用来判断「有没有 encoding=」，"
    "**把本来就有 `encoding=` 的多行调用误判了，报了 23 处**，真值只有 11 处"
    "⇒ **判「某个调用带没带某参数」必须按**括号配对**切分整段调用，不能按第一个 `)` 截。** | "
    "`tests/test_cad_studio_cli.py` / `tests/test_dfm_review.py` / `scripts/fea_analysis.py` 等 6 个文件；"
    "Python 标准库 `subprocess` 文档（`text`/`encoding`）|"
)

F59 = (
    "| 59 | **`Path(\"D:\")` 是「带盘符的**相对**路径」，不是盘根** —— "
    "`Path(\"D:\") / \"AutoCAD 2024\" / \"acad.exe\"` 得到 **`'D:AutoCAD 2024\\\\acad.exe'`（缺反斜杠）**，"
    "而 `Path(\"D:/\") / …` 才得到 `'D:\\\\AutoCAD 2024\\\\acad.exe'`。"
    "**⇒ 2026-10-01（轮 45）在 `scripts/cad_installation.py` 的 `_common_candidates` 里发现这个真实功能 bug**："
    "`root = Path(drive)`（`drive` 是 `\"D:\"` / `\"E:\"`）⇒ **D:/E: 盘上的 AutoCAD / SolidWorks 一直发现不了**"
    "（不影响 C:，因为 C: 走的是 `ProgramFiles` 环境变量拼的路径）。"
    "**⇒ 修法 `Path(drive + \"/\")`；修完全量回归 0 failed。**"
    "★ **这个 bug 是测试**尽职抓到的** —— `test_discover_installation_supports_injected_filesystem` "
    "注入的 `exists` **只认精确字符串** `d:\\\\autocad 2024\\\\acad.exe`，于是把「路径拼错」"
    "暴露成了断言失败。**⇒ 教训：注入式的精确匹配测试能抓到「路径拼错」这类功能 bug；"
    "「在不在」类测试（模糊匹配）抓不到。** | "
    "`scripts/cad_installation.py` 的 `_common_candidates`；`tests/test_cad_reliability.py`；"
    "Python 标准库 `pathlib` 文档（`Path(\"c:\")` 与 `Path(\"c:/\")` 的区别）|"
)

F60 = (
    "| 60 | **文本替换扫描必须排除注释与字符串 —— 否则会改坏自己的说明文字** —— "
    "2026-10-01（轮 45）实例：我用一个脚本把 `text=True` 就地替换成 "
    "`text=True, encoding=\"utf-8\", errors=\"replace\"`，结果**把我在同一文件里刚写的来源块散文也改了**："
    "注释里那句 `` `subprocess.run(..., text=True)` 缺 `encoding=` `` 变成了 "
    "`` `subprocess.run(..., text=True, encoding=\"utf-8\", errors=\"replace\")` 缺 `encoding=` `` "
    "—— **自相矛盾**。**⇒ 三条：① 替换前先**剥掉注释/字符串**，或只在**语法结构**上定位"
    "（如本轮的「括号配对切分调用段」）；② 顺序上**先改代码、后写说明块**，"
    "否则说明块会落进扫描范围；③ 替换完**回读被改文件**核对（事实 48 定则②）。** | "
    "`scripts/fea_analysis.py` 的来源块（曾被改坏）；轮 45 的替换脚本 |"
)


def main() -> int:
    f = WS / "AGENTS.md"
    src = f.read_text(encoding="utf-8").splitlines(keepends=True)
    for num, fact in ((58, F58), (59, F59), (60, F60)):
        if any(l.lstrip().startswith("| %d |" % num) for l in src):
            print("  ⚠ 事实 %d 已存在" % num)
            continue
        i = next((k for k, l in enumerate(src) if l.lstrip().startswith("| %d |" % (num - 1))), None)
        if i is None:
            print("  ✗ 找不到 | %d | 行" % (num - 1))
            return 1
        src = src[:i + 1] + [fact + "\n"] + src[i + 1:]
        print("  ✓ 已加已知事实 %d" % num)
    f.write_text("".join(src), encoding="utf-8")

    r = WS / "docs" / "ROADMAP.md"
    rt = r.read_text(encoding="utf-8")
    anchor = ("            ⑮ 🔴 **修一处「靠巧合通过」的测试**：`test_tool_specs_batch4` 有 2 个测试\n"
              "               的 `derived_args` 碰活 COM（要求界面已选中边）⇒ 干净机器必然失败\n"
              "               ⇒ 改成**带原因 skip**（只吞「碰 COM」那类，别的照旧抛）\n"
              "               ⚠ **推论**：回归基线**依赖 SolidWorks 的文档/选择状态** ⇒ 记基线要同时记环境\n")
    add = ("            ⑯ ★★★★ **修掉全部 5 个基线失败 ⇒ 全量回归首次全绿**（轮 45）：\n"
           "               **5 failed / 856 passed / 17 skipped → 0 failed / 861 passed / 17 skipped**\n"
           "               ★ 根因一（4 个同源）：`subprocess.run(text=True)` 缺 `encoding=` ⇒ GBK 解 UTF-8 中文崩\n"
           "                 ⇒ 11 处补上（**判「带没带参数」必须按括号配对切分调用段** —— 按首个 `)` 截会假阳性）\n"
           "               ★ 根因二（1 个）：**`Path(\"D:\")` 不是盘根** ⇒ `D:AutoCAD 2024\\acad.exe`（缺反斜杠）\n"
           "                 ⇒ **D:/E: 盘的 CAD 一直发现不了**（**真实功能 bug**，被注入式精确匹配测试抓到）\n"
           "                 ⇒ 修法 `Path(drive + \"/\")`\n"
           "               ★ release_check 也 pass；四项门禁全绿\n")
    if "首次全绿" in rt:
        print("  ⚠ ROADMAP 已记录")
    elif anchor in rt:
        r.write_text(rt.replace(anchor, anchor + add, 1), encoding="utf-8")
        print("  ✓ ROADMAP 游标已更新")
    else:
        print("  ⚠ ROADMAP 找不到锚点")

    t2 = f.read_text(encoding="utf-8")
    rt2 = r.read_text(encoding="utf-8")
    print()
    print("  ── 落盘核对 ──")
    for n in (58, 59, 60):
        print("    AGENTS.md | %d |: %d 行" % (n, t2.count("\n| %d |" % n)))
    print("    ROADMAP 含「首次全绿」: %s" % ("是 ✓" if "首次全绿" in rt2 else "**否**"))
    ks = [k for k, l in enumerate(t2.splitlines()) if l.lstrip().startswith("| 41 |")]
    if ks:
        bad = [l[:36] for l in t2.splitlines()[ks[0]:ks[0] + 20]
               if l.strip() and not l.lstrip().startswith("|")]
        print("    事实 41 起 20 行的非表格行: %s" % ("无 ✓" if not bad else "**有 %r**" % bad))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
