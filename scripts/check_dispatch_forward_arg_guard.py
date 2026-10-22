"""★ 门禁：分发口**调用点**的非字面量成员名实参必须可枚举，或显式表态。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁）
# 文件:   scripts/check_dispatch_forward_arg_guard.py
# 定位:   收 spec 230–234 一路登记下来的**最后一块无判据区**：37 个分发口的 362 个
#         **调用点**里，有 8 个把成员名以**非字面量**传入 ⇒ `audit_byref_args` 看不见，
#         而 spec 230 的 `resolution()` 只把入口**分类计数**（`partial 3 · unresolved 4 ·
#         no-callers 12`），**没有任何判据落在调用点上**。
#         上游门禁分工：`check_dispatch_entry_guard` 判**入口表态** + 解析面分类；
#         `check_dispatch_byref_guard` 判**一级转发入口**的 327 个可解析调用点；
#         `check_dispatch_arg_guard`（234）判**包装器调用点**的 `local` 桶（46 个，与本门禁
#         的 8 个**零重叠**，已实测）。
# 官方依据: ① `_raw/**/iface_*.txt`（出厂程序集纯元数据反射；★ 属性编码成 `get_X()`/`set
#           _X()`，  接口名另有 `## <接口>` 头行）② `C:\\swapi\\types\\<接口>\\<成员>.md
#           `（官方 API 文档镜像）★ 两源读取器**从 `check_dispatch_arg_guard.official_me
#           mbers` import，不重写**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
#
# ## 为什么需要它
# `audit_byref_args` 只审「成员名**写在调用点**」的调用。分发口的调用点里若成员名是
# 变量 / 条件式 / 下标，静态审计**一律看不见** ⇒ 这批点长期「被计数、无判据」。
# 本门禁给每个这样的调用点两条**可红**的路：
#   **① 候选集能静态枚举** ⇒ 每个候选值必须能在官方两源里查到（查不到 = 要么拼错、
#      要么是**试名探测**，后者须显式表态 `probe`）；
#   **② 枚举不出** ⇒ 调用点**正上方**必须表态（`dynamic` / `upstream`）。
#
# ## 契约（由人写死；门禁只负责「按你写的查」）
# 声明写在**调用点所在行的正上方**（向上跳过空行取第一行非空行 —— 确定性关联，
# 与 227/228/234 同一方式，**不用行窗口启发式**）：
# ```
# #: dispatch-fwd: dynamic <理由>              # 候选集由运行期决定（值不在静态可解范围
# 内）
# #: dispatch-fwd: upstream <caller-def 名> <理由>   # **二级转发**：实参是包围 `def` 的
# 形参
# #: dispatch-fwd: probe <理由>                # 试名探测（fallback 列表，允许含查不到的
# 候选名）
# ```
# ★ 三个 code 都**自带自证条件**，防止拿它一键躺平：
#   · `dynamic`  ⇒ 若静态**能**枚举出候选集 ⇒ 红（能枚举却声明枚举不出 = 逃避表态）；
#   · `upstream` ⇒ 实参**必须**是**包围 `def` 的形参**，且包围 `def` 名**必须**等于声明的
#                  `<caller-def 名>`（否则红）；能枚举却声明 `upstream` ⇒ 红；
#   · `probe`    ⇒ 若候选值**全部**能在两源里查到 ⇒ 红（没有探测语义却用逃生门）；
#                  若**枚举不出** ⇒ 红（那该用 `dynamic`）。
# ★★ **二级转发只「要求声明」，不「递归解析」**（交接单 §③ 的处置）：追下去会变成
#   一个会移动的靶子，而「登记在案 + 自证」已能保证它**不会被悄悄扩大**。
#
# ## 候选集读取器（**封闭形态清单**；读不出即要求表态，**不许静默降级成空集**）
# ```
# <str 字面量>                                  ⇒ 自身
# <字面量 Tuple/List/Set> / <dict 字面量的 values> ⇒ 全部字符串常量
# <IfExp>                                       ⇒ **两支并集**（`str_consts` 已含）
# <BinOp +>                                     ⇒ 左右并集（`str_consts` 已含）
# <Name> 绑定的字面量容器 / 元组解包投影 / 模块级常量 / `DICT.get(k)`
#                                               ⇒ 复用 234 的 `resolve`（不重写）
# <DICT[k]>，`DICT` 是字面量 dict                ⇒ **值**（★ 与 234 的 `.get(k)` 同族：
#                                                   `DICT[k]` 返回的是**值**，不是键）
# ```
#
# ## 只增不减（下界冻结）
# 非字面量调用点数 / 可枚举数 / 候选值 distinct 数都只允许**增**：
# 减少 = 读取器或取点漏了（**不是**「问题解决了」）⇒ 判 FAIL，先查清再改常量。
#
# ## 假绿守卫
# ★ 「检查过的非字面量调用点 == 0」判失败（事实 46）。
#
# ## 口径不变量（**独立于本门禁的取点**）
# ★★ 凡带非字面量调用点的入口，`check_dispatch_entry_guard.resolution()` 给它的分类
#   **必须**是 `partial` 或 `unresolved` —— 因为 `resolved` 的定义就是「**全部**调用点的
#   成员名都是字面量」。两者不符 ⇒ 口径漂移 ⇒ 红（spec 233 的教训：口径要有人守）。
#
# ## 便携性
# 两源**都**读不到 ⇒ `[SKIP]` + `exit 0`（缺数据源 ≠ 检查失败）。源开关：
# `DSH_DISPATCH_FWD_DUMPS` / `DSH_DISPATCH_FWD_SWAPI`（未设 ⇒ 回落到
# `check_dispatch_arg_guard` 自己的 `DSH_DISPATCH_ARG_*` 与默认路径）。
# 合成树开关：`DSH_DISPATCH_FWD_ROOT` · `DSH_DISPATCH_FWD_BASELINE_MIN`。
from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

#: ★ 扫描根可被覆盖 ⇒ 负例能在**合成树**上端到端跑。
ROOT = Path(
    os.environ.get("DSH_DISPATCH_FWD_ROOT") or Path(__file__).resolve().parents[1]
)
#: 本门禁自己的官方源开关（未设 ⇒ 回落到 234 的 `DSH_DISPATCH_ARG_*`）。
FWD_DUMPS = os.environ.get("DSH_DISPATCH_FWD_DUMPS", "")
FWD_SWAPI = os.environ.get("DSH_DISPATCH_FWD_SWAPI", "")
#: 声明（**调用点上方**第一行非空行）。
DECL = re.compile(r"^#:\s*dispatch-fwd:\s*(?P<head>[a-z-]+)(?:\s+(?P<rest>\S.*?))?\s*$")
#: 封闭词表。
CODES = {"dynamic", "upstream", "probe"}
#: 明细打印上限。
DETAIL_LIMIT = 25
#: ★ 下界（真树实测 · 2026-10-09 · spec 235）—— 只增不减。
BASELINE_SITES = 8  # 非字面量调用点
BASELINE_ENUM = 4  # 其中可静态枚举
BASELINE_VALUES = 12  # 可枚举候选值 distinct


def _baseline() -> tuple[int, int, int]:
    """⇒ `(sites, enum, values)`；`DSH_DISPATCH_FWD_BASELINE_MIN` 可整体覆盖（仅测试用）。"""
    spec = os.environ.get("DSH_DISPATCH_FWD_BASELINE_MIN", "")
    if spec.strip():
        parts = [int(x) for x in spec.split(",")]
        if len(parts) == 3:
            return tuple(parts)
    return (BASELINE_SITES, BASELINE_ENUM, BASELINE_VALUES)


def official_members():
    """⇒ `(官方成员名集合, 数据源说明)`。★ 读取器在 `check_dispatch_arg_guard`，路径由本门禁的开关覆盖。"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_dispatch_arg_guard as cdag  # noqa: PLC0415

    return cdag.official_members_with(FWD_DUMPS, FWD_SWAPI)


def enclosing_def(tree, lineno: int):
    """⇒ 包住该行的**最内层** `def`（按行号范围取 `lineno` 最大者）。"""
    best = None
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        lo = fn.lineno
        hi = getattr(fn, "end_lineno", lo) or lo
        if lo <= lineno <= hi and (best is None or lo > best.lineno):
            best = fn
    return best


def candidates(arg, fnode, env: dict, modenv: dict):
    """⇒ `(候选值列表, 读取路径)` 或 `(None, 原因)`（封闭形态清单见文件头）。"""
    import check_dispatch_arg_guard as cdag  # noqa: PLC0415

    got = cdag.str_consts(arg)  # 字面量 / 容器 / dict 的 values / IfExp / BinOp+
    if got:
        return got, "字面量/IfExp"
    if isinstance(arg, ast.Subscript) and isinstance(arg.value, ast.Name):
        node = cdag._bind_node(arg.value.id, env, modenv)
        if node is not None:
            got = cdag.str_consts(node)  # ★ `DICT[k]` 取**值**
            if got:
                return got, "dict 字面量下标（**值**）"
    if isinstance(arg, ast.Name):
        return cdag.resolve(fnode, arg.id, env, modenv)
    return None, "非封闭形态"


def forward_sites(entries, files):
    """⇒ `[(rel, path, 入口 fn, 包围 def, 实参节点, 行)]` —— 分发口调用点里成员名**非字面量**的。

    ★ 取点口径**全部复用** `check_dispatch_entry_guard`：`_import_map` / `_entry_sites` / `_bind`。
    """
    import check_dispatch_entry_guard as cdeg  # noqa: PLC0415

    imap = cdeg._import_map(files)
    out = []
    for entry in entries:
        path, fn = entry[0], entry[1]
        rel = (
            path.relative_to(ROOT).as_posix()
            if path.is_relative_to(ROOT)
            else path.as_posix()
        )
        for p, call in cdeg._entry_sites(entry, files, imap):
            env = cdeg._bind(fn, call)
            m = env.get(entry[3])
            if isinstance(m, ast.Constant) and isinstance(m.value, str):
                continue  # 字面量 ⇒ `audit_byref_args` 看得见
            out.append(
                (rel, p, fn, enclosing_def(files[p][1], call.lineno), m, call.lineno)
            )
    out.sort(key=lambda r: (r[0], r[5]))
    return out


try:
    from .gate_decl import decl_parts_above as _decl
except ImportError:
    from gate_decl import decl_parts_above as _decl


def judge(got, decl, arg, encl, params, uncovered):
    """⇒ 违规说明，或 `None`。**每个 code 的自证条件都在这里**（唯一一处）。"""
    enumerable = bool(got)
    if decl is None:
        if enumerable:
            if uncovered:
                return "候选值查不到且未表态：%s" % ", ".join(uncovered[:8])
            return None  # 可枚举且全查得到 ⇒ 无需声明
        return "候选集枚举不出且**未表态**"
    head, rest = decl
    if head not in CODES:
        return "未知 code `%s`（封闭词表：%s）" % (head, " / ".join(sorted(CODES)))
    if enumerable:
        if head == "dynamic":
            return (
                "`dynamic` 但**静态可枚举**（%d 个候选）：能枚举却声明枚举不出"
                % len(got)
            )
        if head == "upstream":
            return (
                "`upstream` 但**静态可枚举**（%d 个候选）：能枚举却声明二级转发"
                % len(got)
            )
        if head == "probe":
            if not uncovered:
                return "`probe` 但候选值**全部**查得到（无探测语义）"
            return None if rest else "`probe` 缺理由"
        return None
    if head == "dynamic":
        return None if rest else "`dynamic` 缺理由"
    if head == "probe":
        return "`probe` 但候选集**枚举不出**（该用 `dynamic`）"
    #: `upstream`：二级转发的自证 —— 实参必须是包围 `def` 的形参，且名字要对得上。
    if not rest:
        return "`upstream` 缺 `<caller-def 名>` 与理由"
    caller = rest.split()[0]
    if not (isinstance(arg, ast.Name) and arg.id in params):
        return "`upstream` 但实参**不是**包围 `def` 的形参（`%s`）" % (
            arg.id if isinstance(arg, ast.Name) else type(arg).__name__
        )
    if encl is None or encl.name != caller:
        return "`upstream %s` 与实际的包围 `def`（`%s`）不符" % (
            caller,
            encl.name if encl is not None else "?",
        )
    return None


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_dispatch_arg_guard as cdag  # noqa: PLC0415
    import check_dispatch_entry_guard as cdeg  # noqa: PLC0415

    entries, _visible, _nonliteral, _buckets, _df, _cf, files = cdeg.scan(root=ROOT)
    classes, _resolved_sites = cdeg.resolution(entries, files)
    sites = forward_sites(entries, files)
    official, notes = official_members()
    min_sites, min_enum, min_values = _baseline()

    dist: dict[str, int] = {}
    for _cls, _n in classes.values():
        dist[_cls] = dist.get(_cls, 0) + 1

    print("== 分发口**调用点**的非字面量成员名实参 ==")
    print(
        "扫描 `%s/scripts/**/*.py` · 分发口 %d 个（%s）· 官方成员名 %d 个（%s）"
        % (
            ROOT.as_posix(),
            len(entries),
            " · ".join(
                "%s %d" % (k, dist.get(k, 0))
                for k in ("resolved", "partial", "unresolved", "no-callers")
            ),
            len(official),
            " · ".join(notes) or "无数据源",
        )
    )

    #: ★ 数据源全缺 ⇒ SKIP（缺数据源 ≠ 检查失败）。
    if not official and sites:
        print("[SKIP] 官方两源都读不到 ⇒ 不做存在性判罪（exit 0）")
        print("非字面量调用点 %d · [SKIP] · exit 0" % len(sites))
        return 0

    violations: list[dict] = []
    enum_n = 0
    all_values: set[str] = set()
    claimed: dict[str, int] = {}
    nonliteral_entries: set[tuple] = set()
    for rel, path, entry_fn, encl, arg, lineno in sites:
        nonliteral_entries.add((entry_fn.lineno, path))
        lines = files[path][2]
        fnode = encl if encl is not None else entry_fn
        env = cdag.scope_env(fnode) if fnode is not None else {}
        modenv = cdag.scope_env(files[path][1])
        got, why = candidates(arg, fnode, env, modenv)
        decl = _decl(lines, lineno, DECL)
        params = cdeg._params(encl) if encl is not None else []
        shown = rel.replace(ROOT.as_posix() + "/", "")
        uncovered = sorted({c for c in got if c not in official}) if got else []
        bad = judge(got, decl, arg, encl, params, uncovered)
        if got:
            enum_n += 1
            all_values.update(got)
        if bad is None and decl is not None and decl[0] in CODES:
            claimed[decl[0]] = claimed.get(decl[0], 0) + 1
        if bad:
            violations.append(
                {
                    "kind": "undeclared" if decl is None else "invalid-claim",
                    "file": shown,
                    "line": lineno,
                    "detail": bad + ("" if got else "（读取路径：%s）" % why),
                }
            )

    #: ★★ 口径不变量（**独立于本门禁的取点**）：带非字面量调用点的入口，
    #: `resolution()` 的分类**必须**是 `partial` / `unresolved`（`resolved` = 全字面量）
    #: 。
    for lineno, path in sorted(nonliteral_entries):
        cls = classes.get((path, lineno), ("?", 0))[0]
        if cls not in ("partial", "unresolved"):
            violations.append(
                {
                    "kind": "class-mismatch",
                    "file": path.name,
                    "line": lineno,
                    "detail": "该入口有非字面量调用点，但 `resolution()` 判它是 `%s`（口径漂移）"
                    % cls,
                }
            )

    #: ★ 只增不减（下界冻结）。
    if len(sites) < min_sites:
        violations.append(
            {
                "kind": "baseline-shrunk",
                "file": "-",
                "line": 0,
                "detail": "非字面量调用点 %d < 下界 %d（只增不减：先查取点）"
                % (len(sites), min_sites),
            }
        )
    if enum_n < min_enum:
        violations.append(
            {
                "kind": "baseline-shrunk",
                "file": "-",
                "line": 0,
                "detail": "可枚举调用点 %d < 下界 %d（只增不减：先查读取器）"
                % (enum_n, min_enum),
            }
        )
    if len(all_values) < min_values:
        violations.append(
            {
                "kind": "baseline-shrunk",
                "file": "-",
                "line": 0,
                "detail": "候选值 distinct %d < 下界 %d（只增不减）"
                % (len(all_values), min_values),
            }
        )
    #: ★ 假绿守卫（事实 46）。
    if not sites:
        violations.append(
            {
                "kind": "zero-checked",
                "file": "-",
                "line": 0,
                "detail": "检查过的非字面量调用点 == 0",
            }
        )

    print(
        "非字面量调用点 %d · 可枚举 %d · 候选值 distinct %d · 表态 %s"
        % (
            len(sites),
            enum_n,
            len(all_values),
            " / ".join(
                "%s %d" % (k, claimed.get(k, 0))
                for k in ("upstream", "dynamic", "probe")
            )
            or "无",
        )
    )
    if violations:
        print("[FAIL] 违规 %d 处：" % len(violations))
        for v in violations[:DETAIL_LIMIT]:
            print("  [%s] %s:%s —— %s" % (v["kind"], v["file"], v["line"], v["detail"]))
        if len(violations) > DETAIL_LIMIT:
            print("  …另有 %d 处" % (len(violations) - DETAIL_LIMIT))
    ok = not violations
    print("[PASS]" if ok else "[FAIL]")
    print(
        "非字面量 %d · 可枚举 %d · 候选值 %d · 违规 %d · [%s] · exit %d"
        % (
            len(sites),
            enum_n,
            len(all_values),
            len(violations),
            "PASS" if ok else "FAIL",
            0 if ok else 1,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
