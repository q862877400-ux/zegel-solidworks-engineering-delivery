"""★ 门禁：代码里写 `get_X` / `set_X` 当**成员名**用 —— 而官方那个名字**只有属性形**（`X`）。

（★ 处置事实 520：两处「成员名拼错被当成后端限制」的假阴性）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 出厂类型库反射（`_raw/reflect_sldworks/iface_sldworks.
# txt`）
# 文件:   `scripts/check_member_names.py`（★ **同族的前一道闸** ——
#         它只扫 `scripts/*.py` 的 `get_com_member("名字")` / 直接属性访问；
#         ★★ 而本道管的是**另外两个盲区**：① 走 `getattr(obj, "名字", …)` 的；
#         ② ★ **`subskills/` / `mcp-server/` / `tools/` 根本不在它的扫描根里**）
# 定位:   ★★★ **为什么需要它**（★ 2026-10-04 接手轮，处置事实 520）：
#     `subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py` 里
#     `get_model_view_manager()` 逐字调 `get_com_member(model, "GetModelViewManager")`
#     —— ★ 而官方 `IModelDoc2` 上**没有** `GetModelViewManager`：
#       官方页 `C:\swapi\types\IModelDoc2\ModelViewManager.md` 逐字
#         `**Signature**: ModelViewManager ModelViewManager {get;}` · `kind: property`
#       反射 `_raw/reflect_sldworks/iface_sldworks.txt:10284` 逐字
#         `  ModelViewManager get_ModelViewManager()`
#       ⇒ ★★ 即：**官方只有属性形 `ModelViewManager`**，`GetModelViewManager` 出现 **0 次** ✓
#     ⇒ ★ 后果：`get_com_member` 开头是**裸** `getattr` ⇒ **抛 `AttributeError`**
#       ⇒ ★ 那 4 个 FeatureManager 剖视函数**全都取不到 manager**（★ 而它被记成过"后端限制"）✓
#   ★★★★ **判据（★ 硬门禁，★ 依据是官方反射、不是猜）**：
#     一个字符串字面量若形如 `get_<Name>` 或 `set_<Name>`，★ 而 `<Name>`
#     **在全部反射清单里只以 `get_` / `set_` 前缀形出现**（即**没有**同名裸成员）
#     ⇒ ★★ **那个字面量就是"把属性当方法叫"** ⇒ **报**。
# ★ 这条判据是**构造性**的：★ 它不需要知道哪个接口 —— ★ 那个名字**在任何接口上**都只有属
# 性形 ✓
#   ★★★★★ **两个盲区都封住**：
# ① 扫描根 = `scripts` / `mcp-server` / `subskills` / `tools` / `tests`（★ 前一道只管 `s
# cripts`）；
#     ② 形态   = `getattr` / `hasattr` / `get_com_member` / `call_com_member` /
#                `safe_get_com_member` / `get_com_member_raw` **的字符串实参**（★ 前一道只管后四个）✓
#   ★★★★★★ **不误伤**（★ 三条）：① 只认**可执行代码**里的字符串（`ast` 取 `ast.Constant`、
#     不取 docstring；★ 而**注释与文档里的举例**天然不在 `ast` 里）；
#     ② 只认**成员名位置**的字面量（不是全文 grep 字符串）；
#     ③ ★ 要**真的误伤**，得同时满足「是 `get_X`/`set_X`」且「`X` 没有裸同名成员」——
#        这是一个**很强**的条件（实测全仓命中见输出）✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REFLECTIONS = sorted((ROOT / "_raw").rglob("iface_sldworks.txt"))
#: ★ 官方结构化镜像（`C:\swapi\types\**\*.md`）—— ★ 判据的**第二源**，也是本门禁的**收敛
#: 器**：
#:   它每页顶上带 `member:` / `kind:` 元数据 ⇒ ★★ 于是能分清两件**长得很像**的事：
#: · ★ `get_X` **是官方方法**（★ 它**有自己的页**，如 `GetCurrentSheet` / `GetBodies2`）
#: ⇒ **合法**；
#: · ★★ `get_X` **官方没有这个名字**（★ 它**没有页**，而 `X` **有** `kind: property` 的
#: 页）
#:       ⇒ ★★★ **那才是"把属性当方法叫"** ✓
#: ⚠ 第一版只按「反射里有没有裸名」判 ⇒ ★ 实测**命中几百处**（`GetBodies2` / `GetTypeNam
#: e2` …）
#: 全是**合法方法** ⇒ ★★ 那不是门禁、是噪音 ⇒ ★ 加这一源收敛到 **1 条**（★ 而正是那条真
#: bug）✓
SWAPI_TYPES = Path(r"C:\swapi\types")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

#: 名字位置的字面量会传给这些函数（★ 后四个与前一道闸同名，但本道**在所有扫描根**上都查
#: ）
NAME_ARG_FUNCS = {
    "getattr",
    "hasattr",
    "setattr",
    "delattr",
    "get_com_member",
    "get_com_member_raw",
    "call_com_member",
    "safe_get_com_member",
}
SCAN_ROOTS = (
    "scripts",
    "mcp-server",
    "subskills",
    "tools",
    "tests",
    "apps",
    "dotnet",
    "examples",
)
#: ★ 签名行里第一列的那个标识符（与 `check_member_names.py` 同口径）
SIG = re.compile(r"^\s*(?:[\w\.\[\]<>,\s]+?\s+)?([A-Za-z_]\w*)\s*\(")


#: ★★ 前缀这一层有两个坑（★ 两个都是**负例测试当场抓出来的**，★ 第一版两处都错）：
#:   ① ★ **大小写**：SolidWorks 的 COM 属性访问器形如 `get_ModelViewManager`
#:      —— `get_` 小写、成员名首字母大写 ⇒ ★ 剥前缀要**不分大小写**、★ 保留成员名原样；
#:   ② ★★ **下划线可有可无**：★ 我在代码里写错的那个形态是 **`GetModelViewManager`**
#:      —— ★ **`Get` 后面没有下划线**（★ 它不是访问器名，是**把属性名前面加了个 Get**）
#:      ⇒ ★★ 只认 `get_` 形式会让门禁**对它唯一要抓的那个 bug 反而沉默** ✓
#:   ⇒ ★ 故前缀用**正则**（`^(get|set)_?`，★ `IGNORECASE`）——
#:     ★★ 前提是成员名本身是**驼峰**（★ 下一个字符是大写），这样 `getter` 这类词不会被误剥。
_PREFIX_RE = re.compile(r"^(get|set)_?", re.IGNORECASE)
#: ★ 成员名必须**驼峰开头**（★ 这是官方成员名的形态；★ 也是"别把 `getter` 当 `get_ter`"
#: 的护栏）
_MEMBER_RE = re.compile(r"^[A-Z]\w*$")


def _strip_prefix(name: str) -> tuple[str, str] | None:
    """剥 `get` / `set` 前缀（★ 不分大小写、★ 下划线可有可无）。

    :returns: `(前缀种类, 成员名)`；★ 不是那两个前缀、或成员名不是驼峰 ⇒ `None`。
    """
    m = _PREFIX_RE.match(name)
    if not m or m.end() >= len(name):
        return None
    rest = name[m.end() :]
    if not _MEMBER_RE.match(rest):
        return None
    return m.group(1).lower(), rest


def official_pages() -> dict[str, set[str]]:
    """读官方结构化镜像的每页元数据：`member` → `{kind…}`（★ 判据的**第二源**）。

    :returns: `{"member 名": {"property", "method", …}}`；★ 读不到就回 `{}` ⇒ 调用方判 SKIP。
    """
    out: dict[str, set[str]] = {}
    if not SWAPI_TYPES.is_dir():
        return out
    for p in SWAPI_TYPES.rglob("*.md"):
        head = p.read_text(encoding="utf-8", errors="replace")[:400]
        body = re.search(r"^---(.*?)^---", head, re.M | re.S)
        seg = body.group(1) if body else head
        mem = re.search(r"^member:\s*(\S+)", seg, re.M)
        kind = re.search(r"^kind:\s*(\w+)", seg, re.M)
        if not mem:
            continue
        out.setdefault(mem.group(1), set()).add(kind.group(1) if kind else "?")
    return out


def classify(no_reflection_ok: bool = False) -> dict[str, set[str]]:
    """把反射里的成员名按**前缀形**分类。

    :returns: `{"get_only": {Name…}, "set_only": {Name…}}`
        —— ★ `Name` 只在 `get_Name()` / `set_Name()` 里出现，而**没有**裸的 `Name`。
        ★★ 而 `no_reflection_ok=True` 时（★ 反射不在本机）回**空集** ⇒ 调用方判 `SKIP`。
    """
    get_seen: set[str] = set()
    set_seen: set[str] = set()
    plain: set[str] = set()
    for r in REFLECTIONS:
        if not r.is_file():
            continue
        for line in r.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("## "):
                continue
            m = SIG.match(line)
            if not m:
                continue
            name = m.group(1)
            stripped = _strip_prefix(name)
            if stripped is None:
                plain.add(name)
            elif stripped[0] == "get":
                get_seen.add(stripped[1])
            else:
                set_seen.add(stripped[1])
    return {
        "get_only": get_seen - plain - set_seen,
        "set_only": set_seen - plain - get_seen,
        "plain": plain,
    }


def is_property_form(
    literal: str, cls: dict[str, set[str]], pages: dict[str, set[str]]
) -> str | None:
    """★ **本门禁的判据**：这个字面量是不是「把官方属性当方法叫」？

    :returns: 命中的**官方属性名**；不是 ⇒ `None`。

    ★★★ **三条同时成立才算**（★ 三条缺一就会变成噪音，★ 这是我实测出来的）：
      ① 字面量形如 `get_X` / `set_X`（★ 前缀正则见 `_strip_prefix`）；
      ② ★ **`X` 在官方源里是一个 `kind: property` 的成员**（★ 这是"它本该是属性"的**证据**）；
      ③ ★★ **官方**没有 `get_X` 这个名字** —— ★ 两源各查一次：
         · 反射里 `get_X` 不是某个派发成员名（★ 用 `plain` 集，★ 已剥前缀归一）；
         · ★ **官方 md 里没有 `get_X` 这一页**（★ 判据的**收敛器**：`GetBodies2` /
           `GetCurrentSheet` / `GetAnnotationCount` 这些**都有自己的页** ⇒ **合法方法**，
           ★ 而 `GetModelViewManager` 没有页 ⇒ **命中**）✓
    """
    stripped = _strip_prefix(literal)
    if stripped is None:
        return None
    kind, base = stripped
    if kind == "get" and base not in cls["get_only"]:
        return None
    if kind == "set" and base not in cls["set_only"]:
        return None
    if "property" not in pages.get(base, set()):
        return None
    if literal in pages:  # ★ 官方**有这一页** ⇒ 它是官方方法 ⇒ 合法
        return None
    return base


def _string_args(tree: ast.AST) -> list[tuple[int, str, str]]:
    """取**成员名位置**的字符串字面量：`(行号, 函数名, 字面量)`。

    ★ 只取 `getattr(obj, "X")` 这类**带名字实参**的调用；★ 不碰 docstring / 注释。
    """
    out: list[tuple[int, str, str]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = (
            fn.id
            if isinstance(fn, ast.Name)
            else (fn.attr if isinstance(fn, ast.Attribute) else None)
        )
        if name not in NAME_ARG_FUNCS:
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                out.append((getattr(arg, "lineno", node.lineno), name, arg.value))
    return out


def scan() -> tuple[list[dict], int]:
    """扫全部扫描根，回 `(命中, 看过的文件数)`。"""
    cls = classify()
    pages = official_pages()
    hits: list[dict] = []
    seen = 0
    for root in SCAN_ROOTS:
        base = ROOT / root
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.py")):
            #: ★ 跳过自己的测试（★ 它的正例**故意**造这种形态）
            if (
                p.name.startswith("test_")
                or ".venv" in p.parts
                or "node_modules" in p.parts
            ):
                continue
            #: ★★ 跳过**内嵌快照**（`apps/workbench-ui/src-tauri/resources/skill/**`）——
            #: ★ 它是 `scripts/sync_bundled_skill.py` 的**生成物**（在 `.gitignore` 里）
            #: ，
            #:   逐字是源码的副本 ⇒ ★ 扫它只会把同一处命中**报两遍**（★ 且它不在源码树里，
            #:   修不了也没意义）✓
            if "resources" in p.parts and "skill" in p.parts:
                continue
            try:
                tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            seen += 1
            for lineno, fn, lit in _string_args(tree):
                base_name = is_property_form(lit, cls, pages)
                if base_name:
                    hits.append(
                        {
                            "file": str(p.relative_to(ROOT)).replace("\\", "/"),
                            "line": lineno,
                            "func": fn,
                            "literal": lit,
                            "official": base_name,
                        }
                    )
    return hits, seen


def main() -> int:
    if not any(r.is_file() for r in REFLECTIONS):
        print(
            "★ SKIP：本机读不到出厂反射清单（%s）—— 判据**没有真源** ⇒ 不报假绿"
            % (REFLECTIONS[0].parent if REFLECTIONS else "?")
        )
        return 0
    if not SWAPI_TYPES.is_dir():
        print(
            "★ SKIP：本机读不到官方结构化镜像（%s）—— 判据的**收敛器**不在 ⇒ 不报假绿"
            % SWAPI_TYPES
        )
        return 0
    cls = classify()
    pages = official_pages()
    print("★ 属性形门禁（★ 事实 520）—— 两个官方源的读数：")
    print(
        "   反射：`get_X()` 独有 %d 个 · `set_X()` 独有 %d 个 · 裸名 %d 个"
        % (len(cls["get_only"]), len(cls["set_only"]), len(cls["plain"]))
    )
    print(
        "   官方 md：%d 个成员页（★ 其中 `kind: property` 的 %d 个）"
        % (len(pages), sum(1 for v in pages.values() if "property" in v))
    )
    hits, seen = scan()
    print(
        "   扫了 %d 个 .py（★ 扫描根：%s；★ 已跳过内嵌快照）· ★ 命中：%d 处"
        % (seen, " ".join(SCAN_ROOTS), len(hits))
    )
    for h in hits:
        print(
            "   [HIT] %s:%d  %s(…, %r)  ⇒ ★ 官方那个成员是**属性** `%s`"
            "（★ 且官方**没有** %r 这一页）"
            % (
                h["file"],
                h["line"],
                h["func"],
                h["literal"],
                h["official"],
                h["literal"],
            )
        )
    if hits:
        print(
            "\n[FAIL] ★ 把官方属性当方法叫 ⇒ 反射里没有这个名字 ⇒ `getattr` **抛 AttributeError**；"
            "★ 改成官方那个属性名（去掉 `get_`/`set_` 前缀）"
        )
        return 1
    print("\n[PASS] 没有把官方属性写成 `get_X`/`set_X` 去调")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
