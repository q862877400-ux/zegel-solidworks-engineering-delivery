"""★ 门禁：`local` 桶调用点的**候选值集**必须可枚举，且候选值要在官方两源里查得到。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁）
# 文件:   scripts/check_dispatch_arg_guard.py
# 定位:   收 spec 229–233 一路登记下来的那个桶：**成员名由局部变量传入**的 COM 包装器调用点
#         （`audit_byref_args` 只认「第二实参是字符串字面量」⇒ 这些点**静态审计看不见**）。
#         spec 229 量出它有 52 个（spec 233 订正为 46），spec 230–233 一路只**计数**、不判罪。
# 官方依据: ① `_raw/reflect/iface_*.txt`（出厂程序集纯元数据反射；★ 属性编码成 `get_X()`/`set_X()`，
#             接口名另有 `## <接口>` 头行）
#           ② `C:\\swapi\\types\\<接口>\\<成员>.md`（官方 API 文档镜像，**含属性页**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
#
# ## 为什么需要它
# `local` 桶的调用点把成员名写在**局部变量**里，于是：
#   · `audit_byref_args` 看不见（它要求第二实参是字面量）；
#   · `check_dispatch_entry_guard` 只把它**计入 `buckets["local"]`**，不做任何定性。
# ⇒ 46 个点长期处于「被计数、无判据」状态。本门禁给它们两条**可红**的路：
#   **① 候选集能静态枚举** ⇒ 每个候选值必须能在官方两源里查到（查不到 = 要么拼错、
#      要么是**试名探测**，后者须显式表态）；
#   **② 枚举不出** ⇒ 必须显式表态 `#: dispatch-arg: dynamic <理由>`（**未表态即红**）。
#
# ## 契约（由人写死；门禁只负责「按你写的查」）
# 声明写在**调用点所在行的正上方**（跳过空行取第一行非空行 —— 确定性关联，不用行窗口启发式）：
# ```
# #: dispatch-arg: dynamic <理由>     # 该点的候选集**枚举不出**（值由调用方/运行期决定）
# #: dispatch-arg: probe <理由>       # 该点是**试名探测**（fallback 列表，允许含查不到的候选名）
# ```
# ★ 两个 code 都**自带自证条件**，防止拿它一键躺平：
#   · `dynamic` ⇒ 若静态**能**枚举出候选集 ⇒ 红（能枚举却声明枚举不出 = 逃避表态）；
#   · `probe`   ⇒ 若候选值**全部**能在两源里查到 ⇒ 红（没有探测语义却用逃生门）；
#                 若**枚举不出** ⇒ 红（那该用 `dynamic`）。
#
# ## 候选集读取器（**封闭形态清单**，读不出即 `dynamic`，不许静默降级成空集）
# ```
# for <v> in <字面量 Tuple/List/Set>                   ⇒ 全部字符串常量
# for <a>, <b> in ((s, x), (t, y))                     ⇒ 按 <v> 在解包目标里的**下标投影**
# for <v> in <字面量 dict>                             ⇒ 键
# for <k>, <v> in <dict 字面量/常量>.items()           ⇒ **按位置**取键/值（★ 下标 1 才是值）
# for <v> in <X>.keys() / <X>.values()                 ⇒ 键 / 值
# for <v> in <X>，X 是**本函数局部**或**模块级**的可解容器/dict 字面量
# <v> = <字面量> / <dict 字面量>[k] / <常量>.get(...)  ⇒ 值
# ```
# ★ 两条**踩过的坑**（都写成形态规则，不写散文）：
#   · `for kind, getter in DICT.items()` 里 `getter` 取的是**值**（首版取键 ⇒ 读出一堆
#     语义键 `mass`/`stress` 冒充成员名）；
#   · `DICT.get(k)` 返回的是**值**（首版取键 ⇒ 同上）。
#
# ## 只增不减（下界冻结）
# 调用点数 / 可枚举数 / 候选值 distinct 数都只允许**增**：减少 = 读取器漏了
# （不是「问题解决了」）⇒ 判 FAIL，先查清再改常量。
#
# ## 假绿守卫
# ★ 「检查过的 `local` 调用点 == 0」判失败（事实 46）。
# ★ 与 `check_dispatch_entry_guard.scan()` 的 `buckets["local"]` **必须相等** ——
#   两个独立实现 + 一致性断言 ⇒ 防止本门禁自己另起一套口径（spec 233 的教训）。
#
# ## 便携性
# 两源**都**读不到 ⇒ `[SKIP]` + `exit 0`（缺数据源 ≠ 检查失败）。可用
# `DSH_DISPATCH_ARG_DUMPS` / `DSH_DISPATCH_ARG_SWAPI` 覆盖路径。
# 合成树开关：`DSH_DISPATCH_ARG_ROOT` · `DSH_DISPATCH_ARG_BASELINE_MIN`。
from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

#: ★ 扫描根可被覆盖 ⇒ 负例能在**合成树**上端到端跑（与 `DSH_DISPATCH_ROOT` 同风格）。
ROOT = Path(os.environ.get("DSH_DISPATCH_ARG_ROOT") or Path(__file__).resolve().parents[1])
#: 反射转储根（默认 `ROOT/_raw/**/iface_*.txt`；`;` 分隔可多点）。
DUMPS_ENV = os.environ.get("DSH_DISPATCH_ARG_DUMPS", "")
#: 官方 API 文档镜像的 `types` 目录。
SWAPI_TYPES = Path(os.environ.get("DSH_DISPATCH_ARG_SWAPI") or r"C:\swapi\types")
#: 声明（**调用点上方**第一行非空行）。
DECL = re.compile(r"^#:\s*dispatch-arg:\s*(?P<code>dynamic|probe)\b\s*(?P<rest>.*)$")
#: 封闭词表。
CODES = {"dynamic", "probe"}
#: 明细打印上限。
DETAIL_LIMIT = 25
#: ★ 下界（真树实测 · 2026-10-09 · spec 234）—— 只增不减。
#: ★ **候选值 distinct 是 131 而不是 140**：首版读取器把 `DICT.items()` / `DICT.get(k)`
#:   读成了**键**（`_TOPOLOGY_GETTERS` 的语义键 `mass`/`stress`/… 共 **9** 个）⇒ 131 + 9 = 140。
#:   改按**位置/语义**取值后降为 131 —— ★ 这是**修读取器**（先查清了 9 个的来源），不是漏探测。
BASELINE_SITES = 46
BASELINE_ENUM = 42
BASELINE_VALUES = 131


def _baseline() -> tuple[int, int, int]:
    """⇒ `(sites, enum, values)`；`DSH_DISPATCH_ARG_BASELINE_MIN` 可整体覆盖（仅测试用）。"""
    spec = os.environ.get("DSH_DISPATCH_ARG_BASELINE_MIN", "")
    if spec.strip():
        parts = [int(x) for x in spec.split(",")]
        if len(parts) == 3:
            return tuple(parts)
    return (BASELINE_SITES, BASELINE_ENUM, BASELINE_VALUES)


def official_members() -> tuple[set[str], list[str]]:
    """⇒ `(官方成员名集合, 数据源说明)`。

    三个来源合并（**各自的覆盖边界都写在这里**）：
    · 反射转储的成员行 `Int32 GetBreakLineCount(Int32&)` ⇒ 成员名；
      ★ 属性在转储里是 `get_X()` / `set_X()` ⇒ **剥前缀**才算 `X`（不剥会误判 100 个属性名不存在）；
    · 反射转储的 `## <接口>` 头行 ⇒ 接口名（★ cosworks 里 `ICWStaticStudyOptions` 这类
      **以接口名命名的属性**只出现在头行，不出现为成员行）；
    · `C:\\swapi\\types\\<接口>\\<成员>.md` 的 basename ⇒ 官方文档成员名（含属性页）。
    """
    names: set[str] = set()
    notes: list[str] = []
    dumps = [Path(p) for p in DUMPS_ENV.split(";") if p.strip()] or sorted(
        ROOT.glob("_raw/**/iface_*.txt"))
    rows = 0
    for p in dumps:
        p = Path(p)
        if not p.is_file():
            continue
        for raw in p.read_text(encoding="utf-8", errors="replace").splitlines():
            h = re.match(r"^##\s+(?P<name>\w+)\s*$", raw)
            if h:
                names.add(h.group("name"))
                continue
            m = re.match(r"^\s+[\w\.\[\]<>, ]+?\s+(?P<name>\w+)\((?P<args>.*)\)\s*$", raw)
            if not m:
                continue
            rows += 1
            nm = m.group("name")
            names.add(nm)
            if nm.startswith("get_") or nm.startswith("set_"):
                names.add(nm[4:])
    if rows:
        notes.append("转储 %d 行 / %d 名" % (rows, len(names)))
    if SWAPI_TYPES.is_dir():
        before = len(names)
        for p in SWAPI_TYPES.glob("*/*.md"):
            if not p.name.startswith("_"):
                names.add(p.stem)
        notes.append("swapi +%d" % (len(names) - before))
    return names, notes


def names_in_target(t) -> list[str]:
    """⇒ 解包目标里的变量名（`a, b` / `[a, b]` / 单个 `a`）。"""
    if isinstance(t, ast.Name):
        return [t.id]
    if isinstance(t, (ast.Tuple, ast.List)):
        out = []
        for el in t.elts:
            out.extend(names_in_target(el))
        return out
    return []


def index_in_target(t, var: str) -> int | None:
    """⇒ `var` 在解包目标里的下标；不是解包 ⇒ `None`。"""
    if isinstance(t, (ast.Tuple, ast.List)):
        for i, el in enumerate(t.elts):
            if isinstance(el, ast.Name) and el.id == var:
                return i
    return None


def str_consts(node) -> list[str] | None:
    """⇒ 节点里**所有**字符串常量；含不可解元素 ⇒ `None`（**不静默降级**）。"""
    if isinstance(node, ast.Constant):
        return [node.value] if isinstance(node.value, str) else None
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        out = []
        for el in node.elts:
            got = str_consts(el)
            if got is None:
                return None
            out.extend(got)
        return out
    if isinstance(node, ast.Dict):
        out = []
        for v in node.values:
            got = str_consts(v)
            if got is None:
                return None
            out.extend(got)
        return out
    if isinstance(node, ast.IfExp):
        a, b = str_consts(node.body), str_consts(node.orelse)
        if a is None or b is None:
            return None
        return a + b
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        a, b = str_consts(node.left), str_consts(node.right)
        if a is None or b is None:
            return None
        return a + b
    return None


def dict_keys(node) -> list[str] | None:
    """⇒ dict 字面量的**键**（全字符串）或 `None`。"""
    if isinstance(node, ast.Dict):
        out = []
        for k in node.keys:
            if not (isinstance(k, ast.Constant) and isinstance(k.value, str)):
                return None
            out.append(k.value)
        return out
    return None


def scope_env(scope) -> dict[str, object]:
    """⇒ `{变量名: 值节点}`（`X = …` / `X: T = …`，**先到先得**）。"""
    env: dict[str, object] = {}
    for st in ast.walk(scope):
        if isinstance(st, ast.Assign):
            for tg in st.targets:
                if isinstance(tg, ast.Name):
                    env.setdefault(tg.id, st.value)
        elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name) \
                and st.value is not None:
            env.setdefault(st.target.id, st.value)
    return env


def _bind_node(name: str, env: dict, modenv: dict):
    if name in env:
        return env[name]
    return modenv.get(name)


def _iter_candidates(it, target, var: str, env: dict, modenv: dict):
    """⇒ `(候选值, 读取路径)` 或 `(None, 原因)`。"""
    if isinstance(it, ast.Call) and isinstance(it.func, ast.Attribute) \
            and isinstance(it.func.value, ast.Name) \
            and it.func.attr in ("items", "keys", "values"):
        node = _bind_node(it.func.value.id, env, modenv)
        if node is not None:
            idx = index_in_target(target, var)
            if it.func.attr == "keys" or (it.func.attr == "items" and idx == 0):
                keys = dict_keys(node)
                if keys is not None:
                    return keys, "dict .%s() 键" % it.func.attr
            if it.func.attr == "values" or (it.func.attr == "items" and idx == 1):
                got = str_consts(node)
                if got is not None:
                    return got, "dict .%s() 值" % it.func.attr
        return None, "for:非字面量(.%s)" % it.func.attr
    if isinstance(it, ast.Name):
        node = _bind_node(it.id, env, modenv)
        if node is not None:
            idx = index_in_target(target, var)
            if idx is not None and isinstance(node, (ast.Tuple, ast.List)) \
                    and all(isinstance(e, (ast.Tuple, ast.List)) for e in node.elts):
                out = []
                for e in node.elts:
                    if idx >= len(e.elts):
                        return None, "for:解包投影越界"
                    got = str_consts(e.elts[idx])
                    if got is None:
                        return None, "for:解包投影非字面量"
                    out.extend(got)
                return out, "for 元组解包投影"
            got = str_consts(node)
            if got is not None:
                return got, "for 常量容器（经变量）"
            keys = dict_keys(node)
            if keys is not None:
                return keys, "for dict 字面量（经变量）"
        return None, "for:非字面量"
    idx = index_in_target(target, var)
    if idx is not None and isinstance(it, (ast.Tuple, ast.List)) \
            and all(isinstance(e, (ast.Tuple, ast.List)) for e in it.elts):
        out = []
        for e in it.elts:
            if idx >= len(e.elts):
                return None, "for:解包投影越界"
            got = str_consts(e.elts[idx])
            if got is None:
                return None, "for:解包投影非字面量"
            out.extend(got)
        return out, "for 元组解包投影"
    got = str_consts(it)
    if got is not None:
        return got, "for 字面量容器"
    keys = dict_keys(it)
    if keys is not None:
        return keys, "for dict 字面量"
    return None, "for:非字面量"


def resolve(fn, var: str, env: dict, modenv: dict):
    """⇒ `(候选值列表, 读取路径)` 或 `(None, 原因)`。"""
    for st in ast.walk(fn):
        if isinstance(st, (ast.For, ast.AsyncFor)) and var in names_in_target(st.target):
            got, why = _iter_candidates(st.iter, st.target, var, env, modenv)
            if got:
                return got, why
        if isinstance(st, ast.comprehension) and var in names_in_target(st.target):
            got, why = _iter_candidates(st.iter, st.target, var, env, modenv)
            if got:
                return got, why
    if var in env:
        node = env[var]
        got = str_consts(node)
        if got is not None:
            return got, "assign 字面量"
        if isinstance(node, ast.Subscript):
            got = str_consts(node.value)
            if got is not None:
                return got, "dict 字面量下标"
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and isinstance(node.func.value, ast.Name):
            base = _bind_node(node.func.value.id, env, modenv)
            if base is not None:
                #: ★ `DICT.get(k)` 返回**值**（首版取键 ⇒ 语义键冒充成员名）。
                if node.func.attr == "get":
                    got = str_consts(base)
                    if got is not None:
                        return got, "dict 常量 .get() 值"
                keys = dict_keys(base)
                if keys is not None:
                    return keys, "dict 常量 .%s() 键" % node.func.attr
        return None, "assign:非字面量"
    if var in modenv:
        got = str_consts(modenv[var])
        if got is not None:
            return got, "模块级常量"
        keys = dict_keys(modenv[var])
        if keys is not None:
            return keys, "模块级 dict 常量"
    return None, "（本函数内无绑定）"


def local_sites(files):
    """⇒ `[(rel, path, fn, 变量名, 调用节点, 行)]` —— `local` 桶调用点（去重口径）。

    ★ 口径**镜像** `check_dispatch_entry_guard.scan()`：第 2 实参是 `Name`、不是所在 `def`
      的形参、且**最内层包围 `def`** 是该 `def`（spec 233 的嵌套去重）。
    ★ 本函数与 `scan()` 的一致性由 `main()` 里的硬断言守（两个独立实现 + 一致性检查）。
    """
    from check_dispatch_entry_guard import _params, wrapper_names  # noqa: PLC0415

    wrappers = wrapper_names()
    out = []
    for path, (_src, tree, _lines) in files.items():
        rel = path.as_posix()
        innermost: dict[int, object] = {}
        for fn in ast.walk(tree):
            if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for sub in ast.walk(fn):
                    if isinstance(sub, ast.Call):
                        innermost[id(sub)] = fn
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            params = set(_params(fn))
            for sub in ast.walk(fn):
                if not (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)
                        and sub.func.id in wrappers and len(sub.args) >= 2):
                    continue
                if innermost.get(id(sub)) is not fn:
                    continue
                arg = sub.args[1]
                if isinstance(arg, ast.Name) and arg.id not in params:
                    out.append((rel, path, fn, arg.id, sub, sub.lineno))
    return out


def declaration_above(lines: list[str], lineno: int):
    """⇒ `(code, 理由)` 或 `None`（未表态）。★ 确定性关联：向上跳过空行取第一行非空行。"""
    i = lineno - 2
    while i >= 0 and not lines[i].strip():
        i -= 1
    if i < 0:
        return None
    m = DECL.match(lines[i].strip())
    if not m:
        return None
    return m.group("code"), (m.group("rest") or "").strip()


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_dispatch_entry_guard as cdeg  # noqa: PLC0415

    _e, _v, _nl, buckets, _df, _cf, files = cdeg.scan()
    sites = local_sites(files)
    official, notes = official_members()
    min_sites, min_enum, min_values = _baseline()

    print("== `local` 桶调用点（成员名由局部变量传入）的候选集 ==")
    print("扫描 `%s/scripts/**/*.py` · 官方成员名 %d 个（%s）"
          % (ROOT.as_posix(), len(official), " · ".join(notes) or "无数据源"))

    violations: list[dict] = []
    enum_n = 0
    all_values: set[str] = set()
    for rel, _path, fn, var, _call, lineno in sites:
        lines = files[_path][2]
        env = scope_env(fn)
        modenv = scope_env(files[_path][1])
        got, why = resolve(fn, var, env, modenv)
        decl = declaration_above(lines, lineno)
        shown = rel.replace(ROOT.as_posix() + "/", "")
        if got:
            enum_n += 1
            all_values.update(got)
            uncovered = sorted({c for c in got if c not in official}) if official else []
            if decl is None:
                if uncovered:
                    violations.append({"kind": "undeclared", "file": shown, "line": lineno,
                                       "detail": "候选值查不到且未表态：%s（变量 `%s`）"
                                                 % (", ".join(uncovered[:8]), var)})
            else:
                code, rest = decl
                if code == "dynamic":
                    violations.append({"kind": "invalid-claim", "file": shown, "line": lineno,
                                       "detail": "`dynamic` 但**静态可枚举**（%d 个候选）："
                                                 "能枚举却声明枚举不出" % len(got)})
                elif code == "probe":
                    if not uncovered:
                        violations.append({"kind": "invalid-claim", "file": shown, "line": lineno,
                                           "detail": "`probe` 但候选值**全部**查得到（无探测语义）"})
                    elif not rest:
                        violations.append({"kind": "invalid-claim", "file": shown, "line": lineno,
                                           "detail": "`probe` 缺理由"})
        else:
            if decl is None:
                violations.append({"kind": "undeclared", "file": shown, "line": lineno,
                                   "detail": "候选集枚举不出（%s）且未表态（变量 `%s`）" % (why, var)})
            else:
                code, rest = decl
                if code == "dynamic":
                    if not rest:
                        violations.append({"kind": "invalid-claim", "file": shown, "line": lineno,
                                           "detail": "`dynamic` 缺理由"})
                elif code == "probe":
                    violations.append({"kind": "invalid-claim", "file": shown, "line": lineno,
                                       "detail": "`probe` 但候选集**枚举不出**（该用 `dynamic`）"})

    #: ★ 口径一致性（两个独立实现）：本门禁的取点数**必须**等于 `scan()` 的 `local` 桶。
    if len(sites) != buckets["local"]:
        violations.append({"kind": "bucket-mismatch", "file": "-", "line": 0,
                           "detail": "本门禁取点 %d != scan() 的 local 桶 %d（口径漂移）"
                                     % (len(sites), buckets["local"])})
    #: ★ 只增不减（下界冻结）。
    if len(sites) < min_sites:
        violations.append({"kind": "baseline-shrunk", "file": "-", "line": 0,
                           "detail": "local 调用点 %d < 下界 %d（只增不减：先查取点口径）"
                                     % (len(sites), min_sites)})
    if enum_n < min_enum:
        violations.append({"kind": "baseline-shrunk", "file": "-", "line": 0,
                           "detail": "可枚举调用点 %d < 下界 %d（只增不减：先查读取器）"
                                     % (enum_n, min_enum)})
    if len(all_values) < min_values:
        violations.append({"kind": "baseline-shrunk", "file": "-", "line": 0,
                           "detail": "候选值 distinct %d < 下界 %d（只增不减）"
                                     % (len(all_values), min_values)})
    #: ★ 假绿守卫（事实 46）。
    if not sites:
        violations.append({"kind": "zero-checked", "file": "-", "line": 0,
                           "detail": "检查过的 `local` 调用点 == 0"})

    print("local 调用点 %d · 可枚举 %d · 候选值 distinct %d"
          % (len(sites), enum_n, len(all_values)))
    if violations:
        print("[FAIL] 违规 %d 处：" % len(violations))
        for v in violations[:DETAIL_LIMIT]:
            print("  [%s] %s:%s —— %s" % (v["kind"], v["file"], v["line"], v["detail"]))
        if len(violations) > DETAIL_LIMIT:
            print("  …另有 %d 处" % (len(violations) - DETAIL_LIMIT))
    ok = not violations
    print("[PASS]" if ok else "[FAIL]")
    print("local %d · 可枚举 %d · 候选值 %d · 违规 %d · [%s] · exit %d"
          % (len(sites), enum_n, len(all_values), len(violations),
             "PASS" if ok else "FAIL", 0 if ok else 1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
