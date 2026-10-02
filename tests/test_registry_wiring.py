"""钉住「注册表 / 注入 / 批次清单」的**接线一致性**（死守卫的**第三种形态**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_registry_wiring.py
# 定位:   轮 137：`053`/`054` 扫**常量**形态、`055` 扫**函数**形态；
#         本文件管**第三种** —— 注册表/清单层面的「登记了却没接上」。
#         ★ 与那两次不同：**这四条判据全是"集合比对"（结构），不含任何语义判断**
#         ⇒ 按事实 74 的对照（"判结构可靠、判语义不可靠"）⇒ **它们可以安全地当回归**。
# 官方依据: 不适用（本项目内部纪律）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
for p in (REPO_ROOT / "mcp-server", REPO_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import register_capabilities as rc          # noqa: E402
from tool_registry import effective_inject       # noqa: E402

MCP = REPO_ROOT / "mcp-server"
REG = MCP / "register_capabilities.py"


def _declared_batches() -> set:
    """★ 用 **AST 读结构**，**不用正则**（2026-10-01 轮 211 修）。

    ⚠ 原实现是 `re.search(r"BATCH_MODULES\\s*=\\s*\\((.*?)\\)", src, re.S)` ——
    **非贪婪 ⇒ 撞到第一个 `)` 就停**，即它**假设「元组里不会出现 `)`」**。
    ★ 而注释是**自由文本**，那个假设本来就不成立：轮 211 我在 `BATCH_MODULES` 里
    加了一行注释写着 ``_consumed(angle_deg)`` 与 ``sw_connect.deg()``（**半角括号**）
    ⇒ 正则在那里就截断了 ⇒ `"tool_specs_batch17"` 落在范围外 ⇒
    **门禁报「文件在磁盘上却没登记」，而它其实登记了**（门禁**自己**抓到了这个解析错误）。
    ⇒ 修法不是"注释里别写括号"（那是绕过），而是**换成结构解析** ——
    「**能靠结构保证的，不要靠约定**」。
    """
    tree = ast.parse(REG.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if "BATCH_MODULES" in targets and isinstance(node.value, (ast.Tuple, ast.List)):
                return {
                    e.value for e in node.value.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)
                }
    raise AssertionError("register_capabilities.py 里找不到 BATCH_MODULES（AST 里没有这个赋值）")


def test_every_batch_file_on_disk_is_registered():
    """@brief ★★ **文件在、却没登记** ⇒ 那批工具**永远不会被注册**（而文件看着好好的）。

    ★ 这是"死守卫"的第三种形态里最隐蔽的一种：
    文件存在、内容正确、测试也可能过 —— 只是**没接上**。
    """
    on_disk = {p.stem for p in MCP.glob("tool_specs_batch*.py")}
    missing = sorted(on_disk - _declared_batches())
    assert not missing, "这些批次文件在磁盘上却没登记进 BATCH_MODULES: %s" % missing


def test_no_ghost_batches_declared():
    """@brief **登记了、文件却不在** ⇒ 注册时会炸（这种会自己暴露，但仍要守）。"""
    on_disk = {p.stem for p in MCP.glob("tool_specs_batch*.py")}
    ghost = sorted(_declared_batches() - on_disk)
    assert not ghost, "BATCH_MODULES 登记了不存在的模块: %s" % ghost


def test_every_declared_spec_actually_reaches_all_specs():
    """@brief ★★ 每个批次文件里 `SPECS_*` 声明的工具，**都要出现在 `all_specs()` 里**。

    ⚠ 「文件在清单里」还不够 —— 一个批次里的**某一条**也可能因为改名/漏加而没进去。
    """
    allnames = {s.name for s in rc.all_specs()}
    problems = []
    for mod in sorted(_declared_batches()):
        mm = __import__(mod)
        lists = [getattr(mm, n) for n in dir(mm)
                 if n.startswith("SPECS_") and isinstance(getattr(mm, n), list)]
        for var in lists:
            absent = sorted({s.name for s in var} - allnames)
            if absent:
                problems.append("%s: %s" % (mod, absent))
    assert not problems, "这些声明的工具没进 all_specs():\n  %s" % "\n  ".join(problems)


def test_every_inject_name_has_a_resolver():
    """@brief ★★ 用了某个 `inject` 名 ⇒ **必须有对应解析器**（否则调用时才炸）。"""
    missing = sorted({effective_inject(s) for s in rc.all_specs()}
                     - set(rc.RESOLVERS) - {""})
    assert not missing, "这些 inject 名没有解析器: %s" % missing


def test_no_unused_resolver():
    """@brief ★ 登记在 `RESOLVERS` 里、却**没有任何 spec 用**的 ⇒ 那就是一段死接线。

    ⚠ 与上一条**方向相反**：那条防"缺"，这条防"多"。
    """
    used = {effective_inject(s) for s in rc.all_specs()}
    unused = sorted(set(rc.RESOLVERS) - used)
    assert not unused, (
        "RESOLVERS 里这些没人用（要么接上、要么删掉并说明）: %s" % unused)
