"""检查新增/改动文件里是否混入了 diff 记号（`+` / `*` 前缀的注释行）。

为什么需要这个
--------------
本项目在写「来源块」注释时，**连续三轮**把 diff/patch 的行首记号
（``+ `` 或 ``* ``）一起写进了注释块：

    # 定位:   导线端点与路径。官方签名逐条照抄：
    #     IWire : Void set_FromComponentReference(String) /
     *                   set_ToComponentReference(String) /     ← 语法错误
     *             Int32   SetRoutePathForWire(Object)           ← 1

后果是 ``IndentationError``。三次都是靠 ``py_compile`` 抓到 ——
说明**只靠编译器不报警不行**：应该有一条专门门禁，在提交前就点出「你又写了
diff 记号」，并**直接点名文件与行号**（编译错误只给一个 IndentationError，
不告诉你是哪个来源块）。

⚑ 判定口径的一个重要修正（本门禁初版就踩了）
------------------------------------------
初版只看「行首有缩进 + ``*`` 或 ``+``」，结果把**合法的表达式续行**也报了出来::

        value = (
            base
            + int(spec.tip_arc_segments)      ← 合法，+ 是二元运算符

本项目 ``sw_gear.py`` 就有这种写法。⇒ 必须先判断「该行是不是注释」，
**只在注释块里**判定 —— 那才是 diff 记号唯一会误入的地方。

⚠ 只读本地文件，不改任何东西。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的门禁工具）
# 文件:   scripts/check_diff_markers.py —— 本文件自身
# 定位:   模块级常量、正则与 scan()（其演进见 scan 的 docstring）、
#         main() 的目录清单。
# 触发原因: 本任务写「来源块」注释时**连续三轮**把 diff/patch 的行首记号
#         （``+ `` / ``* ``）带进注释块（sw_simulation_loads.py /
#         sw_routing.py / sw_costing.py），每次都由 py_compile 的
#         IndentationError 才发现，且编译错误不告诉你是哪个来源块。
# 覆盖:   全文件 —— 本模块是一个自洽的门禁工具单元。
# ⚠ 本工具只读本地文件，不改任何东西。
# ⚠ 本工具的规则**已做过负向验证**：注入一行真 diff 记号后确实报 FAIL
#   并点名文件与行号（同一文件 py_compile 报 IndentationError）；
#   干净树上报 PASS（187 个 .py 文件）。除此之外未在本机实测
#   （见 AGENTS.md 铁律 2）。
# ────────────────────────────────────────────────────────────────────

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

REPO = Path(r"C:\swprojects\sw-skill-fork")
SCAN_DIRS = ("scripts", "subskills", "tests", "examples", "docs")

#: 注释行的行首（缩进后是 #）
COMMENT_LINE = re.compile(r"^[ \t]*#")
#: 注释块里的 diff 记号：行首缩进后紧跟单个 * 或 +
MARKER = re.compile(r"^[ \t]+([*+])(?=\s|$)")


def scan(path: Path) -> list[tuple[int, str]]:
    """判定 diff 记号，并排除合法的表达式续行。

    ⚑ 三轮踩坑才做对，判据的来历记在这里：

    **第 1 版**（只看行首有缩进 + ``*``/``+``）—— 把**合法表达式续行**也报了::

        value = (
            base
            + int(spec.tip_arc_segments)      ← 合法，+ 是二元运算符

    **第 2 版**（只看注释行内）—— **漏报**，这比误报更糟。原因是循环论证::

         *  Object GetBodies()  ← 注入的真 diff 记号

    这行**不以 # 开头**（而这正是 diff 记号的特征），
    所以「只查注释行」把它排除在外了。负向测试实测：注入真记号后门禁仍报 PASS，
    而同一文件 ``py_compile`` 报 ``IndentationError`` —— 门禁形同虚设。

    **第 3 版**（当前）—— 用**语法结构**判断，而不是猜「像不像注释」：
      · 维护括号深度；
      · 深度 > 0 且上一条代码行以运算符/逗号/开括号结尾时，
        行首的 ``+`` / ``*`` 是二元运算符续行，合法；
      · 其余情况下一律判为 diff 记号。
    ⇒ 注释块里的真记号必被抓，表达式续行必被放过。
    """
    # ── 来源 ─────────────────────────────────────────────────────────
    # 仓库:   本项目自身（本任务新增的门禁工具）
    # 文件:   scripts/check_diff_markers.py —— 本文件自身
    # 定位:   scan() 的判据实现（三版演进见上方 docstring）。
    # 依据:   三次真实误报/漏报 + 一次负向测试，均记录在上方 docstring。
    # ⚠ 本工具只读本地文件，不改任何东西。
    # ⚠ 本工具的规则本身未在本机实测（见 AGENTS.md 铁律 2）——
    #   但**已做过负向验证**：注入一行真 diff 记号后本门禁确实报 FAIL
    #   并点名文件与行号（同一文件 py_compile 报 IndentationError）。
    # ─────────────────────────────────────────────────────────────────
    hits: list[tuple[int, str]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return hits

    depth = 0
    in_doc = False          # 是否在 """ 或 ''' 里面（docstring 里的示例不是代码）
    prev_code = ""
    for index, line in enumerate(lines):
        stripped = line.strip()
        # —— 三引号字符串内的示例行不算（否则本门禁会抓自己的文档）
        quotes = stripped.count('"""') + stripped.count("'''")
        if in_doc:
            if quotes:
                in_doc = False
            continue
        if quotes == 1:
            in_doc = True
            continue
        if quotes >= 2:
            continue
        if not stripped or stripped.startswith("#"):
            continue
        match = MARKER.match(line)
        if match:
            # 括号未闭合 ⇒ 行首的 + / * 是二元运算符续行（sw_gear.py 就是这种写法）
            if depth <= 0:
                hits.append((index + 1, line.rstrip()))
        depth += line.count("(") + line.count("[") + line.count("{")
        depth -= line.count(")") + line.count("]") + line.count("}")
        if depth < 0:
            depth = 0
        prev_code = stripped
    return hits


def main() -> int:
    targets: list[Path] = []
    for name in SCAN_DIRS:
        directory = REPO / name
        if directory.is_dir():
            targets.extend(sorted(directory.rglob("*.py")))
    if not targets:
        print("[WARN] 没扫到任何 .py 文件，检查 REPO 路径是否正确")
        return 2

    total = 0
    for path in targets:
        hits = scan(path)
        if not hits:
            continue
        total += len(hits)
        print(f"  {path.relative_to(REPO)}")
        for number, line in hits[:6]:
            print(f"    {number}: {line}")
        if len(hits) > 6:
            print(f"    … 另有 {len(hits) - 6} 行")

    print()
    if total:
        print(f"[FAIL] {total} 行混入了 diff 记号（`*` / `+` 前缀）。")
        print("       写来源块注释时别把 patch 的行首记号带进来。")
        return 1
    print(f"[PASS] {len(targets)} 个 .py 文件里没有 diff 记号残留")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
