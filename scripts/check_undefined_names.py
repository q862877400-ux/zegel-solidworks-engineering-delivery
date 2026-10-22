"""★ 门禁：扫出**未定义名**（`NameError` 隐患）—— `compile()` 抓不到的那一类。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁）
# 文件:   scripts/check_undefined_names.py
# 定位:   ★ 2026-10-03（轮 404）24h 计划 v2 收敛报告 §五 第 ⑤ 条的落地：
#   ★★ 「全仓扫一遍"有契约测试但从不真调"的函数 —— 它们正是这一类
#      （导入缺失 / 空存根）的藏身处」。
# ★ 触发它的真 bug：`export_to_image` 用了 `out_i4()` 而模块漏了导入 ⇒ 一调就 `NameError
# `；
#     ★ 而 `check_python_syntax.py` 只做 `compile()` ⇒ **语法合法、名字没解析** ⇒ 抓不到。
# ★★ **判据（保守版）**：★ 一个名字若**在整个文件里从未被绑定**（既非导入 / 赋值 / 形参 
# /
# def / class / except-as / match 绑定 / 全局声明），★ 而它**在代码位置被读取** ⇒ **报**
# 。
#     · ★ 这样**嵌套作用域与闭包都不会假阳性**（★ 因为判据是"**整文件**绑没绑过"）；
#     · ★ 代价：★ 会漏掉"绑在 A 函数而读在 B 函数"这种跨作用域误用 —— ★ **宁可漏，不要噪音**
#       （★ 事实 53：需要反复修补的判据不该进工具）。
#   ★★ **跳过注解**：★ Python 3.14 起注解是**惰性**的（PEP 649）⇒ 注解里的名字**不会**引发
#     `NameError`（★ 只有 `get_type_hints()` 才会）⇒ ★ 把它算进来就是假阳性。
#   ★★★ 2026-10-08（spec 223 / FR-010）**边界透明化**：★ 被整文件跳过的（`import *` /
#     `globals()` 注入）原先**一个字都不打印** ⇒ ★ 实测静默跳过 **7** 个文件，
# 含 `scripts/sw_part.py`（★ 222 那个 `from typing import Any` 致命缺陷**正藏在它里面**
# ）。
#     ⇒ ★ 现在**每次运行都打印**「跳过 N 个文件 + 逐个文件的原因」——
#     ★ **退出码不变**（跳过不是失败，是**看得见的豁免**，与 `KNOWN_BROKEN` 同族）✓
# 官方依据: 不适用（Python 语言作用域规则 + `ast` 标准库 + PEP 649）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import builtins
import sys
from pathlib import Path

#: 2026-10-03（接手轮）强制 stdout 为 UTF-8 —— 本门禁会 print 中文与箭头/勾这类符号，
#:   而 stdout 是管道时（测试正是用管道抓输出）默认按 locale（本机 GBK）编码
#:   ⇒ UnicodeEncodeError: 'gbk' codec can't encode character … ⇒ 门禁自己崩掉。
#:   known-facts 58 那一族（中文 Windows 上两侧默认编码不一致 —— 病灶在输出侧）；
#:   而测试那侧的 subprocess.run 已经带了 encoding='utf-8'。
sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = ("scripts", "mcp-server", "tools")
BUILTINS = set(dir(builtins)) | {"__file__", "__name__", "__doc__", "__package__",
                                 "__spec__", "__loader__", "__builtins__", "__debug__"}

#: ★★ **已登记的损坏模块** —— ★ 这些**每次都打印**（★ 不静默），但**不拦门禁**
#:   （★ 因为修好它们要**补功能**、不是补导入）。★ 留在名单上就是待办。
#: ⚠ 这是**白名单而不是修复**：★ 一旦有人补全或删掉该模块，★ 必须同时把它从名单里去掉
#:   —— ★ 否则它就成了"一个存在但没人管的豁免"。
#: ★★ 白名单（★ **而不是修复**）**现在是空的**。
#:   ★★★ 2026-10-03（轮 431）**唯一那条已按决断删除**：
#:     `scripts/sw_selection_tx.py`（残骸：引用的 4 个名字全仓不存在 · 无人导入）。
#:   ★ **删它的三条依据**：
#:     ① 它要管理的 `AccessSelections` 在本机后端上**调不通**
#:        （**事实 47**：架构性限制，20+ 种形态实测）⇒ ★ **补全了也没用**；
#:     ② **无任何模块导入它**（已核）⇒ **删它不影响调用方**；
#:     ③ 它的**意图**（★“异常路径也释放选区接管”）**值得保留**
#:        ⇒ ★ 已写进 `docs/known-facts.md`（★ **而不是留在死代码里**）。
#:   ⚠ ★ 而本白名单的契约**不变**：★ **每条都必须有**那个文件
#:     （★ 删了文件就该删名单 —— ★ 那正是本轮发生的事）。
KNOWN_BROKEN: dict[str, str] = {}


def _bound_names(node: ast.AST) -> set:
    """★ 收集整棵树里**被绑定**的名字（导入 / 赋值 / 形参 / def / class / except-as / match / global）。"""
    out: set = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            out.add(n.id)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(n.name)
            for a in getattr(n.args, "args", []) if hasattr(n, "args") else []:
                out.add(a.arg)
        elif isinstance(n, ast.arg):
            out.add(n.arg)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for a in n.names:
                out.add(a.asname or a.name.split(".")[0])
        elif isinstance(n, ast.ExceptHandler) and n.name:
            out.add(n.name)
        elif isinstance(n, ast.Global) or isinstance(n, ast.Nonlocal):
            out.update(n.names)
        elif isinstance(n, ast.MatchAs) and n.name:
            out.add(n.name)
        elif isinstance(n, ast.MatchStar) and n.name:
            out.add(n.name)
        elif isinstance(n, ast.MatchMapping) and n.rest:
            out.add(n.rest)
    return out


def _annotation_nodes(tree: ast.AST) -> set:
    """★ 收集**注解子树**里所有节点的 id（★ 那些位置的名字在 3.14 下是惰性的 ⇒ 不算读）。"""
    skip: set = set()
    for n in ast.walk(tree):
        for attr in ("returns", "annotation"):
            ann = getattr(n, attr, None)
            if isinstance(ann, ast.AST):
                for sub in ast.walk(ann):
                    skip.add(id(sub))
        if isinstance(n, ast.arg) and n.annotation is not None:
            for sub in ast.walk(n.annotation):
                skip.add(id(sub))
    return skip


def _skip_reason(tree: ast.Module) -> str | None:
    """★ 名字来源**看不见**的三种情形 ⇒ 返回**原因串**（不跳过则 `None`）。

    ① `star-import` —— `from x import *`（★ 经典）；
    ② `globals-update` —— `globals().update(...)`（★ 真例：`mcp-server/server.py`
       的 `globals().update(exports)`，`exports` 是一张 **100+ 项的绑定表**，
       而那些名字在静态源码里**根本不存在**）；
    ③ `globals-subscript` —— `globals()[...] = ...`。

    ★★ **2026-10-08（spec 223 / FR-010）**：本函数**从布尔改成原因串** ——
      原先是 `_has_star_import()` 回 `True/False`，而**主流程从不报告**跳过了谁
      ⇒ ★ 实测**静默跳过 7 个文件**（含 `scripts/sw_part.py` —— 222 那个
      `from typing import Any` 致命缺陷**正藏在它的跳过里**）。
      ⇒ ★ 判据是「**看不见的豁免**」不可接受：跳过**不是失败**（那些文件本来就
      无法静态判定），但**必须看得见** ✓
    """
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom) and any(a.name == "*" for a in n.names):
            return "star-import"
        #: ★ `globals().update(...)`
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "update":
            base = n.func.value
            if (isinstance(base, ast.Call) and isinstance(base.func, ast.Name)
                    and base.func.id == "globals"):
                return "globals-update"
        #: ★ `globals()[...] = ...`
        if isinstance(n, ast.Assign):
            for tgt in n.targets:
                if (isinstance(tgt, ast.Subscript) and isinstance(tgt.value, ast.Call)
                        and isinstance(tgt.value.func, ast.Name) and tgt.value.func.id == "globals"):
                    return "globals-subscript"
    return None


def _has_star_import(tree: ast.Module) -> bool:
    """★ 兼容薄壳（旧名保留）：等价于 `_skip_reason(tree) is not None`。"""
    return _skip_reason(tree) is not None


def skip_reason_for(path: Path) -> str | None:
    """★ 读一个文件 ⇒ 它的跳过原因（`None` = 会正常扫）。★ 供主流程**报告**用。"""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:                                          # noqa: BLE001
        return None
    return _skip_reason(tree)


def scan_file(path: Path) -> list:
    """★ 扫一个文件 ⇒ `[(行号, 所在函数, 名字), …]`（★ 空 = 没发现问题）。"""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:                                          # noqa: BLE001
        return []
    if _skip_reason(tree):                                     #: ★ 有 `import *` / `globals()` 注入 ⇒ 无法判定
        return []
    file_bound = _bound_names(tree)                            #: ★ **整个文件**绑过的名字
    skip = _annotation_nodes(tree)                             #: ★ 注解里的不算读
    #: ★ 记录每个 `Name` 所属的最近函数（★ 只为报错时能说出位置）
    owner: dict = {}
    for fn in ast.walk(tree):
        if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for sub in ast.walk(fn):
                owner.setdefault(id(sub), fn.name)
    problems: list = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Name) or not isinstance(node.ctx, ast.Load):
            continue
        if node.id in file_bound or node.id in BUILTINS:
            continue
        if id(node) in skip:
            continue
        problems.append((node.lineno, owner.get(id(node), "<module>"), node.id))
    return sorted(set(problems))


def main(argv: list) -> int:
    total = 0
    bad: list = []
    skipped: list = []
    for d in SCAN_DIRS:
        for p in sorted((REPO_ROOT / d).rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            total += 1
            #: ★★ spec 223 / FR-010：跳过的文件**必须被报告**（★ 原先静默 ⇒ 看不见的豁免
            #: ）。
            reason = skip_reason_for(p)
            if reason:
                skipped.append((p.relative_to(REPO_ROOT).as_posix(), reason))
                continue
            for ln, fn, name in scan_file(p):
                bad.append((str(p.relative_to(REPO_ROOT)), ln, fn, name))
    print("  未定义名门禁 · 扫 **%d** 个文件 · 命中 **%d** 处" % (total, len(bad)))
    if skipped:
        print("  ★ 跳过 **%d** 个文件（判据无法判定 ⇒ 不静默；★ 跳过不是失败，"
              "但**必须看得见**）：" % len(skipped))
        for rel, reason in skipped:
            print("      %-18s %s" % (reason, rel))
    else:
        print("  ★ 跳过 **0** 个文件（没有 `import *` / `globals()` 注入）")
    known = [b for b in bad if b[0].replace("\\", "/") in KNOWN_BROKEN]
    fresh = [b for b in bad if b[0].replace("\\", "/") not in KNOWN_BROKEN]
    for f, ln, fn, name in fresh[:40]:
        print("    %s:%d  在 %s() 里读取了**全文件都没绑定过**的名字 %r" % (f, ln, fn, name))
    for f in sorted({b[0] for b in known}):
        n = len([b for b in known if b[0] == f])
        print("\n  [WARN] %s（%d 处）\n         已登记损坏：%s" % (f, n, KNOWN_BROKEN[f.replace("\\", "/")]))
    if fresh:
        print("\n  判据：★ 该名字在**整个文件里从未被绑定**（导入 / 赋值 / 形参 / def / class /")
        print("        except-as / match / global）★ 而它**在这里被读取** ⇒ **NameError 隐患**。")
        print("  ★★ `compile()` 抓不到（语法合法）—— ★ 而**一调用就炸**")
        print("  （真例：轮 403 `export_to_image` 用了 `out_i4()` 而模块漏了导入）。")
        print("  修法：补导入 / 补定义。★ 而**不要**为了变绿去 `# noqa` 掉它。")
        return 1
    if known:
        print("\n  [OK] 除**已登记损坏**的 %d 处外，没有未定义名" % len(known))
    else:
        print("  [OK] 没有未定义名（★ 保守判据：宁可漏，不要噪音）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
