"""★ 把 Python 源码里「中文散文中的 ASCII 双引号」批量换成「」（★ 事实 48 的自动修法）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/fix_cjk_quotes.py
# 定位:   ★ 本仓写中文文档串时**反复**踩同一个坑（★ 交接文档已记：**同一处栽过多次**）：
#   在 `"…"` 字符串**内部**再写 ASCII 双引号 ⇒ Python 提前闭合字符串 ⇒
#   `SyntaxError: invalid syntax. Perhaps you forgot a comma?`，★ **而报错行常常指向下一行**。
#   ★★ 定则（本仓既有）：**中文散文里的引号一律用「」** —— 本工具就是把它们自动换掉 ✓
#   ★ 为什么做成工具：★ 我在规格 209 的 7 个轮次里**手改了 6 次以上**，
#     每次的形态都在变（`"X"` / `**"X"**` / `**"X"**` 前面还有 `**`）⇒
#     ★ 与事实 61 定则④同源：**写了个好用的东西，就要在所有同类场合用它** ✓
# 判据:   ★ **只改「至少有一边紧邻中文」的引号对**；★ 纯英文/代码里的引号**一律不动** ✓
#   ★ 且改完**必须 `ast.parse` 通过**才算成功（本工具自己验）✓
# 官方依据: 不适用（纯文本工具）· Python 标准库 `ast` / `re`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

CJK = r"\u4e00-\u9fff\u3000-\u303f\uff00-\uffef"
#: ★★ **第一版太窄，改了两处**（★ 实测踩出来的）：
#:   ① 把"中文"限定在三个 Unicode 区段 ⇒ ★ **`★`（U+2605）不在里面**，
#:      而本仓的散文**几乎每行都以 `★` 开头** ⇒ 那一整类形态全被漏掉；
#:   ② 装饰类里没有**空白** ⇒ `★★ **"…"**` 这种"星号 + 空格 + 引号"的形态也漏 ✓
#:   ⇒ ★ 现在：**"非 ASCII 字符"就算邻接**（★ 判据简单且够用），★ 装饰类含**空白** ✓
NON_ASCII = r"\x00-\x7f"          #: ★ 这是**字符类的内容**（不是完整的类）—— 用时写成 `[^…]`
DECO = r"\*`_\s"                  #: ★ 同上：**内容**，不是完整的类（⚠ 一版写成 `[…]` ⇒ 又造出嵌套类）
#: ★ 一条"非 ASCII 散文里的引号对"：左边有非 ASCII（可隔着装饰符），右边有非 ASCII（可隔着装饰符）——
#:   ★★ 用**捕获组**而不是定宽 lookbehind（Python 的 lookbehind 必须定宽，`*` 这种量词放不进去）✓
#:   ⚠ ⚠ **本文件在这上面错了两次**（★ 都只给 `FutureWarning`、**不报错**，所以极难发现）：
#:     ① 把 `^\x00-\x7f` 整个塞进字符类 ⇒ `[^ ^…]`；
#:     ② 把 `[\*`_\s]`（**已经带方括号**）再套一层 ⇒ `[[…]]`。
#:   ⇒ ★ 定则：**凡是要拼进字符类的东西，都只存"类的内容"** —— 由**用它的那一行**加 `[` `]` ✓
#:   ⇒ ★ 这也解释了为什么前两次"改完仍是 0 处"：**正则静默变形、一处也匹配不上** ✓
PAIR = re.compile(
    r"([^" + NON_ASCII + r"])([" + DECO + r"]*)\"([^\"\n]{1,80}?)\"([" + DECO + r"]*)(?=[^"
    + NON_ASCII + r"])"
)


def _string_constants(text: str):
    """★ 取源码里**全部字符串常量的值**（★ 递归进容器）；★ 解析不了 ⇒ `None` ✓

    ★★ 用途：★ 做"**只改分隔符、不改内容**"的**语义护栏** ✓
    """
    import ast
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            out.append(node.value)
    return sorted(out)


def fix_text(src: str) -> tuple[str, int]:
    """★ 返回 `(改过的文本, 改动处数)` —— ★ **不做任何其它改写** ✓

    ★★★ 2026-10-06 **加了一道语义护栏**（★ 真机被抓到，★ 这次是它**改坏了断言**）：
      ★ 实录：★ `assert … == str(("另一个", "默认<按加工>"))` 被改成
        `str(("另一个「, 」默认<按加工>"))` ✗✗ —— ★ 它把**代码里的两个字符串**
        当成了"散文里的引号对" ✓
      ★ 现象有多坑：★ 那个文件**仍能解析**（★ 只是**语义变了**）⇒ ★ 于是
        **一条一直绿的测试突然红，而报错指向断言的值、不指引号** ✗
      ⇒ ★★ 护栏判据（★ **语义级，不是形态级**）：
        ★ 若**原文能解析**，★ 则**改完也必须能解析**，★★ **且两边"字符串常量集合"必须一字不差** ✓
        ★ 任一条不满足 ⇒ ★ **整份原样返回、改动数记 0**（★ 宁可不改，不许改坏）✓
      ★★ 这与本仓**两次"过度纠正"**的教训**同族**：★ **宁可不改 ≠ 一律不改** ——
        ★ 护栏只在"**会改变语义**"时拒绝 ✓
    """

    def _sub(m: re.Match) -> str:
        return "%s%s「%s」%s" % (m.group(1), m.group(2), m.group(3), m.group(4))

    new, n = PAIR.subn(_sub, src)
    if not n:
        return src, 0
    #: ★★ **语义护栏**：★ 原文本来就解析不了（★ 如 `.md`）⇒ 不适用护栏 ✓
    before = _string_constants(src)
    if before is None:
        return new, n
    if _string_constants(new) == before:
        return new, n
    #: ★★★ **逐行回退**（★ 全有全无**太粗** —— ★ 真机：一个文件里既有正当的散文、
    #:   又有会改坏的代码 ⇒ ★ 整份拒绝会把**该改的也不改** ✗）：
    #:   ★ 只改"**改完仍满足不变式**"的那些行 ⇒ ★ 精确到**行** ✓
    #:   ★（★ 判据仍是**语义级**：★ 每行改完，★ 全文件字符串常量必须一字不变）✓
    out_lines, changed = [], 0
    for idx, ln in enumerate(src.splitlines(keepends=True)):
        cand, cnt = PAIR.subn(_sub, ln)
        if not cnt:
            out_lines.append(ln)
            continue
        trial = "".join(out_lines) + cand + "".join(src.splitlines(keepends=True)[idx + 1:])
        if _string_constants(trial) == before:
            out_lines.append(cand)
            changed += cnt
        else:
            out_lines.append(ln)          # ★ 这一行会改坏语义 ⇒ **原样保留** ✓
    return "".join(out_lines), changed


def main(argv=None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("用法: python tools/fix_cjk_quotes.py <文件…>   # ★ 就地改；先跑 --dry 只看")
        return 2
    dry = "--dry" in args
    files = [a for a in args if not a.startswith("--")]
    bad = 0
    for f in files:
        p = Path(f)
        src = p.read_text(encoding="utf-8")
        new, n = fix_text(src)
        ok_before = _parses(src)
        ok_after = _parses(new)
        print("%-58s 改 %2d 处 · 语法 %s → %s"
              % (f, n, "OK" if ok_before else "FAIL", "OK" if ok_after else "FAIL"))
        if n and not dry:
            if not ok_after:
                print("   ★★ 改完语法仍不过 ⇒ **不写盘**（★ 免得把好文件改坏）")
                bad += 1
                continue
            p.write_text(new, encoding="utf-8")
    return 1 if bad else 0


def _parses(text: str) -> bool:
    try:
        ast.parse(text)
        return True
    except SyntaxError:
        return False


if __name__ == "__main__":
    raise SystemExit(main())
