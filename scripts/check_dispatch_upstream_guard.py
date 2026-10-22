"""★ 门禁：分发口 `upstream` 声明的**上游覆盖**必须与事实相符（封闭桶 + 自证）。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁）
# 文件:   scripts/check_dispatch_upstream_guard.py
# 定位:   收 spec 235 交接单的**待办 1**（「二级转发的上游」）。235 给分发口**调用点**的
#         非字面量实参开了三条逃生门，其中 `upstream <caller-def 名>` **只自证两件**：
#         ① 实参是包围 `def` 的形参；② 包围 `def` 名 == 声明的 `<caller-def 名>`。
#         ★★ **它从不检查那个 `<caller-def 名>` 的调用方到底传了什么** ⇒ `upstream`
#         是一个**半开的逃生门**：写 `upstream X` 只要 X 恰好是包围 `def`、恰好收一个
#         成员名形参，就**永远绿** —— 哪怕 X 的每个调用方都在用运行期变量传成员名。
#         本门禁把这个洞封上：**声明必须带一个上游桶，且桶必须与事实相符**。
# 官方依据: ① `_raw/**/iface_*.txt`（出厂程序集纯元数据反射；★ 属性编码成  `get_X()`/`se
#           t_X()`，须剥前缀；接口名另有 `## <接口>` 头行）② `C:\\swapi\\types\\<接口>\\
#           <成员>.md`（官方 API 文档镜像）★ 两源读取器**从 `check_dispatch_arg_guard.of
#           ficial_members` import，不重写**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
#
# ## 为什么需要它
# 「一句话不是守卫」（spec 229）：`upstream` 声明**写了**，但**没人查声明的内容**。
# 本门禁让「写了」变成「写了且对得上」：桶与事实不符、上游调用点用变量传名、
# 候选值官方查不到 —— 任一 ⇒ 红。
#
# ## 契约（由人写死；门禁只负责「按你写的查」）
# 声明格式（**向后兼容 spec 235**：`<caller-def 名>` 仍是第一个 token）：
# ```
# #: dispatch-fwd: upstream <caller-def 名> <sites|tool-only|orphan> <理由>
# ```
# | 桶 | 含义 | 自证条件（写错即红） |
# |---|---|---|
# | `sites`     | 上游 `def` 在本仓**有** AST 调用点，且每个调用点都传**字面量**成员名 | 无调用点 ⇒ 红；任一调用点非字面量 ⇒ 红；候选值官方查不到 ⇒ 红 |
# | `tool-only` | 上游**无** AST 调用点，但名字出现在某 `mcp-server/tool_specs_*.py` 的 `function="…"` | 有 AST 调用点 ⇒ 红；无 ToolSpec 引用 ⇒ 红 |
# | `orphan`    | 上游**既无** AST 调用点、**也无** ToolSpec 引用（未被调用） | 任一非空 ⇒ 红 |
# ★★ **为什么必须有 `tool-only` 这一档**：`set_study_option_report` 的 **AST 调用点是 0**，
#   但它**不是** orphan —— 它由**工具层按名**注册（`tool_specs_batch37.py:96` 的
#   `function="set_study_option_report"`）⇒ ★ 「AST 调用点为 0」**不等于**「没人用」
#   （与 spec 234「窄读取器读出 0 也会骗人」同族）。
#
# ## 只增不减（下界冻结）
# `upstream 声明数` / `上游调用点总数` / `字面量候选值 distinct` 只允许**增**：
# 减少 = 取点或读取器漏了（**不是**「问题解决了」）⇒ 判 FAIL，先查清再改常量。
#
# ## 假绿守卫
# ★ 「检查过的 `upstream` 声明 == 0」判失败（事实 46）。
#
# ## 不做（边界，见 spec §五）
# · **不递归解析**：只核一层（上游 `def` 的调用点）；再往上追会变成「会移动的靶子」。
# · **不判接口归属**：字面量只判「名字在两源里存在」。
# · **不动 229 的下界常量**（`_sum_over_views` **不是**分发口 ⇒ 无需扩 `entries`）。
#
# ## 便携性
# 两源**都**读不到 ⇒ `[SKIP]` + `exit 0`（缺数据源 ≠ 检查失败）。源开关：
# `DSH_DISPATCH_UPSTREAM_DUMPS` / `DSH_DISPATCH_UPSTREAM_SWAPI`（未设 ⇒ 回落到
# `check_dispatch_arg_guard` 自己的 `DSH_DISPATCH_ARG_*` 与默认路径）。
# 合成树开关：`DSH_DISPATCH_UPSTREAM_ROOT` · `DSH_DISPATCH_UPSTREAM_BASELINE_MIN`。
from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

#: ★ 扫描根可被覆盖 ⇒ 负例能在**合成树**上端到端跑。
ROOT = Path(os.environ.get("DSH_DISPATCH_UPSTREAM_ROOT") or Path(__file__).resolve().parents[1])
#: 本门禁自己的官方源开关（未设 ⇒ 回落到 234 的 `DSH_DISPATCH_ARG_*`）。
UP_DUMPS = os.environ.get("DSH_DISPATCH_UPSTREAM_DUMPS", "")
UP_SWAPI = os.environ.get("DSH_DISPATCH_UPSTREAM_SWAPI", "")
#: ★ 封闭词表：上游桶。
MODES = ("sites", "tool-only", "orphan")
#: 上游调用点的扫描面（★ 真树两处；打包副本 `apps/**` **有意不扫**）。
SITE_DIRS = ("scripts", "mcp-server")
#: 明细打印上限。
DETAIL_LIMIT = 25
#: ★ 下界（真树实测 · 2026-10-09 · spec 236）—— 只增不减。
BASELINE_DECLS = 3          # `upstream` 声明数
BASELINE_SITES = 10         # 上游调用点总数（`sites` 桶）
BASELINE_VALUES = 5         # 字面量候选值 distinct


def _baseline() -> tuple[int, int, int]:
    """⇒ `(decls, sites, values)`；`DSH_DISPATCH_UPSTREAM_BASELINE_MIN` 可整体覆盖（仅测试用）。"""
    spec = os.environ.get("DSH_DISPATCH_UPSTREAM_BASELINE_MIN", "")
    if spec.strip():
        parts = [int(x) for x in spec.split(",")]
        if len(parts) == 3:
            return tuple(parts)
    return (BASELINE_DECLS, BASELINE_SITES, BASELINE_VALUES)


def official_members():
    """⇒ `(官方成员名集合, 数据源说明)`。★ 读取器**复用 234**，只用本门禁的源开关覆盖它的路径。"""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_dispatch_arg_guard as cdag  # noqa: PLC0415

    if UP_DUMPS:
        cdag.DUMPS_ENV = UP_DUMPS
    if UP_SWAPI:
        cdag.SWAPI_TYPES = Path(UP_SWAPI)
    return cdag.official_members()


def _iter_py(base: Path):
    """⇒ `(path, tree)` —— 解析不了的**静默跳过**（与其它门禁一致）。"""
    if not base.is_dir():
        return
    for p in sorted(base.rglob("*.py")):
        try:
            yield p, ast.parse(p.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue


def upstream_call_sites(name: str):
    """⇒ `[(path, call, tree)]` —— 本仓对 `name` 的 AST 调用点（裸名 + 限定名）。"""
    out = []
    for d in SITE_DIRS:
        for p, tree in _iter_py(ROOT / d):
            for call in ast.walk(tree):
                if not isinstance(call, ast.Call):
                    continue
                f = call.func
                nm = (f.id if isinstance(f, ast.Name)
                      else (f.attr if isinstance(f, ast.Attribute) else None))
                if nm == name:
                    out.append((p, call, tree))
    return out


def toolspec_refs(name: str):
    """⇒ `[(path, line)]` —— `mcp-server/tool_specs_*.py` 里 `function="<name>"` 的引用。"""
    out = []
    base = ROOT / "mcp-server"
    if not base.is_dir() or not name:
        return out
    pat = re.compile(r'function\s*=\s*["\']%s["\']' % re.escape(name))
    for p in sorted(base.glob("tool_specs_*.py")):
        try:
            txt = p.read_text(encoding="utf-8")
        except OSError:
            continue
        for m in pat.finditer(txt):
            out.append((p, txt[:m.start()].count("\n") + 1))
    return out


def arg_for_param(call, params, pname):
    """⇒ `(实参节点 或 None, 说明)` —— 按**关键字名**优先、再按**位置下标**取该形参的实参。"""
    if not pname:
        return None, "无名形参"
    for kw in call.keywords:
        if kw.arg == pname:
            return kw.value, "kw:%s" % pname
    if pname in params:
        i = params.index(pname)
        if i < len(call.args):
            return call.args[i], "pos:%d" % i
    return None, "missing"


def collect_facts(udef, params, pname):
    """⇒ 上游事实（取数，**不判罪**）：`n_sites` / `nonliteral` / `values`。"""
    sites = upstream_call_sites(udef.name)
    nonliteral = []
    values: set[str] = set()
    for p, call, _tree in sites:
        arg, how = arg_for_param(call, params, pname)
        if arg is None:
            nonliteral.append((p, call.lineno, "缺该形参（%s）" % how))
        elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            values.add(arg.value)
        else:
            nonliteral.append((p, call.lineno, "实参是 <%s>" % type(arg).__name__))
    return {"n_sites": len(sites), "nonliteral": nonliteral, "values": values}


def judge(tokens, encl, facts, uncovered):
    """⇒ 违规说明列表（空 = 绿）。★★ **所有判罪都在这一个函数里**（spec 235 的教训：判罪不许分居两处）。"""
    if len(tokens) < 2:
        return ["`upstream` **未表态**上游桶（封闭词表：%s）" % " / ".join(MODES)]
    caller, mode = tokens[0], tokens[1]
    if mode not in MODES:
        return ["上游桶 `%s` 不在封闭词表（%s）" % (mode, " / ".join(MODES))]
    bad = []
    if len(tokens) < 3:
        bad.append("`upstream %s %s` 缺理由" % (caller, mode))
    #: ★ 上游 `def` 就是**包围 `def` 本身**（声明的 caller 名必须等于它）——
    #:   所以这里同时是「名字对不对」与「def 存不存在」两个判定，不需要另做按名查找。
    if encl is None or encl.name != caller:
        bad.append("`upstream %s` 与实际的包围 `def`（`%s`）不符"
                   % (caller, encl.name if encl is not None else "?"))
        return bad
    n_sites, n_trefs = facts["n_sites"], facts["n_trefs"]
    expected = "sites" if n_sites else ("tool-only" if n_trefs else "orphan")
    if mode != expected:
        bad.append("桶声明 `%s` 与**事实** `%s` 不符（上游 AST 调用点 %d · ToolSpec 引用 %d）"
                   % (mode, expected, n_sites, n_trefs))
        return bad
    if mode == "sites":
        for rel, lineno, why in facts["nonliteral"]:
            bad.append("上游调用点 %s:%d 的成员名实参**非字面量**（%s）⇒ 该点须另行表态"
                       % (rel, lineno, why))
        if uncovered:
            bad.append("上游调用点的候选值在官方两源**查不到**：%s" % ", ".join(uncovered[:8]))
    return bad


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import check_dispatch_entry_guard as cdeg  # noqa: PLC0415
    import check_dispatch_forward_arg_guard as cdfag  # noqa: PLC0415

    entries, _visible, _nonliteral, _buckets, _df, _cf, files = cdeg.scan(root=ROOT)
    fwd = cdfag.forward_sites(entries, files)

    decls = []
    for rel, path, _entry_fn, encl, arg, lineno in fwd:
        #: ★ 2026-10-22 统一化：原借用 cdfag.declaration_above（跨门禁依赖），
        #:   现直接用共享实现 scripts/gate_decl.decl_parts_above，
        #:   正则用前向门禁已定义的那一份（cdfag.DECL）
        from gate_decl import decl_parts_above as _decl_parts
        decl = _decl_parts(files[path][2], lineno, cdfag.DECL)
        if decl is None or decl[0] != "upstream":
            continue
        decls.append((rel, path, encl, arg, lineno, (decl[1] or "").split()))

    official, notes = official_members()
    min_decls, min_sites, min_values = _baseline()

    print("== 分发口 `upstream` 声明的**上游覆盖** ==")
    print("扫描 `%s/{%s}/**/*.py` · `upstream` 声明 %d 个 · 官方成员名 %d 个（%s）"
          % (ROOT.as_posix(), ",".join(SITE_DIRS), len(decls), len(official),
             " · ".join(notes) or "无数据源"))

    #: ★ 数据源全缺 ⇒ SKIP（缺数据源 ≠ 检查失败）。
    if not official and decls:
        print("[SKIP] 官方两源都读不到 ⇒ 不做存在性判罪（exit 0）")
        print("upstream 声明 %d · [SKIP] · exit 0" % len(decls))
        return 0

    violations: list[dict] = []
    n_up_sites = 0
    all_values: set[str] = set()
    buckets = {m: 0 for m in MODES}
    for rel, path, encl, arg, lineno, tokens in decls:
        caller = tokens[0] if tokens else ""
        pname = arg.id if isinstance(arg, ast.Name) else None
        facts = {"n_sites": 0, "n_trefs": len(toolspec_refs(caller)), "nonliteral": [], "values": set()}
        if encl is not None and pname:
            facts.update(collect_facts(encl, cdeg._params(encl), pname))
        uncovered = sorted(v for v in facts["values"] if v not in official)
        n_up_sites += facts["n_sites"]
        all_values.update(facts["values"])
        for detail in judge(tokens, encl, facts, uncovered):
            violations.append({"file": rel, "line": lineno, "detail": detail})
        if len(tokens) >= 2 and tokens[1] in MODES:
            buckets[tokens[1]] += 1

    #: ★ 只增不减（下界冻结）。
    if len(decls) < min_decls:
        violations.append({"file": "-", "line": 0,
                           "detail": "`upstream` 声明 %d < 下界 %d（只增不减：先查取点）"
                                     % (len(decls), min_decls)})
    if n_up_sites < min_sites:
        violations.append({"file": "-", "line": 0,
                           "detail": "上游调用点 %d < 下界 %d（只增不减：先查取点）"
                                     % (n_up_sites, min_sites)})
    if len(all_values) < min_values:
        violations.append({"file": "-", "line": 0,
                           "detail": "字面量候选值 distinct %d < 下界 %d（只增不减）"
                                     % (len(all_values), min_values)})
    #: ★ 假绿守卫（事实 46）。
    if not decls:
        violations.append({"file": "-", "line": 0,
                           "detail": "检查过的 `upstream` 声明 == 0"})

    print("upstream 声明 %d · 上游调用点 %d · 字面量候选值 distinct %d · 桶 %s"
          % (len(decls), n_up_sites, len(all_values),
             " / ".join("%s %d" % (m, buckets[m]) for m in MODES)))
    if violations:
        print("[FAIL] 违规 %d 处：" % len(violations))
        for v in violations[:DETAIL_LIMIT]:
            print("  [invalid-claim] %s:%s —— %s" % (v["file"], v["line"], v["detail"]))
        if len(violations) > DETAIL_LIMIT:
            print("  …另有 %d 处" % (len(violations) - DETAIL_LIMIT))
    ok = not violations
    print("[PASS]" if ok else "[FAIL]")
    print("upstream 声明 %d · 上游调用点 %d · 候选值 %d · 违规 %d · [%s] · exit %d"
          % (len(decls), n_up_sites, len(all_values), len(violations),
             "PASS" if ok else "FAIL", 0 if ok else 1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
