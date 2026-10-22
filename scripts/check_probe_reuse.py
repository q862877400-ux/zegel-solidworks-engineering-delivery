"""★ 门禁：不许再手搓「已有工具的替代品」—— ★ 为某能力写的探针，若该能力已有工具，就报出来。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁；2026-10-07 交接文档 §五-2 点名要建的那条）
# 文件:   scripts/check_probe_reuse.py
# 定位:   ★ 用户 2026-10-07 的原话：「★ 你用 `pwsh` 调 `tools/sw_guard.py` 起探针的方
#           式，我怕你会**忘记你有哪些工具**，然后就一直用常用工具硬干」✓
#         ★★ 实测基础：本仓 `tools/probe_*.py` 246 个 + `tools/prove_*.py` 110 个 = **356 个**；
#           而 `AGENTS.md`「写探针验能力时」那条纪律管的是「**怎么调**（按 ToolSpec 契约）」，
#           ★ **不管「该不该自己调」** ✗ ⇒ ★★ 没有任何门禁能拦住「手搓一个已有工具的替代品」✓
#         ★★★ 判据（**两条同时成立才算命中** —— ★ 见下方「为什么两条都要」）：
#           ① **名字对应**：工具名的词序列是探针文件名词序列的**连续子段**；
#           ② **调用证据**：该探针**确实调到了**那个工具的**实现函数**（`module.function`）。
# 官方依据: 不适用（本项目内部口径；`ToolSpec` 见 `mcp-server/tool_registry.py`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件（分析范围 = `tools/probe_*.py` + `tools/prove_*.py` + `mcp-server/serve
# r.py`）
# ─────────────────────────────────────────────────────────────────────────────
#
# ★★★ **为什么「两条都要」（★ 这是本文件最要紧的一段，★ 我第一版栽在这上面）**：
#  ★ 第一版判据只有「② 调用证据」⇒ 实测报出 **2112 处 / 1469 条**，★ 而几乎全是噪声 ✗：
#    · `json.dumps` / `pathlib.Path` —— ★ 我给 `server.py` 收集调用时**没过模块白名单**，
#      ⇒ ★ **标准库的调用被塞进了「工具实现」表**（★ 已知事实 51 的原样复现：
#        分析范围没有贴合「哪些模块才是本仓的 scripts 模块」这个组织单元 ✗）✓
#    · `sw_part.extrude_boss` —— ★ 探针**为了搭测试几何**先建一个方块 ⇒ ★ 它调的是
#      `solidworks_extrude_boss`，★ **但那不是该探针要验的能力** ✗
#  ⇒ ★★ 根因：**「调到了某工具的实现」不等于「这个探针在重复那个工具」** ——
#    ★ 前者是**图上的边**，后者是**探针的意图**；★ 只有名字对应才能表达意图 ✓
#  ⇒ ★ 所以判据是「**为这个能力写了探针** ∧ **而且它调的是该能力的实现**」✓

from __future__ import annotations

import argparse
import ast
import json
import sys
import warnings
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

#: ★ 中文 Windows 上打印 `✓` / `★` 会 `UnicodeEncodeError: 'gbk' codec`（已知事实 58 那
#: 一族）
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    pass

PROBE_GLOBS = ("probe_*.py", "prove_*.py")
SERVER_PY = ROOT / "mcp-server" / "server.py"
#: ★★ **基线**：已存在的命中按「探针 × 工具」逐条登记，★ 每条**必须带理由**
#:   （与 `docs/gate-wiring-exemptions.json` / `docs/union-not-doing.json` 同型 ——
#    ★ **一个没有理由的豁免等于没写** ✓）。
BASELINE = ROOT / "docs" / "probe-reuse-baseline.json"
#: ★ 本仓的 scripts 模块（★ 模块白名单 —— ★ 第一版漏了它，把 `json` / `pathlib` 也算了进
#: 来 ✗）
SCRIPT_MODULES = {p.stem for p in (ROOT / "scripts").glob("*.py")}
#: ★ 工具名前缀（★ 与 `tools/probe_mcp_stdio_handshake.py` 的 `KNOWN_PREFIXES` 同源）
TOOL_PREFIXES = ("solidworks_", "cadstudio_", "mcp_")


def _norm_module(mod: str | None) -> str:
    """★ 把 `scripts.sw_part` / `sw_part` 归一成 `sw_part`（★ 两种导入写法本仓都有）。"""
    if not mod:
        return ""
    return mod.split(".")[-1] if mod.startswith("scripts.") else mod


def _imported_symbols(tree: ast.AST) -> dict:
    """⇒ `{本地名: (模块, 原名)}` —— 覆盖 `from m import a as b` / `import m as x` 两种。

    ★ 判据范围贴合「**一次导入**」这个组织单元（已知事实 51）：只认 `ast.Import` /
      `ast.ImportFrom`，★ 不靠名字文本猜 ✓
    """
    out: dict = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "scripts":  # `from scripts import sw_part as sp`
                for a in node.names:
                    if a.name in SCRIPT_MODULES:
                        out[a.asname or a.name] = (a.name, None)
                continue
            mod = _norm_module(node.module)
            if mod not in SCRIPT_MODULES:
                continue
            for a in node.names:
                out[a.asname or a.name] = (mod, a.name)
        elif isinstance(node, ast.Import):
            for a in node.names:
                mod = _norm_module(a.name)
                if mod not in SCRIPT_MODULES:
                    continue
                out[a.asname or a.name.split(".")[-1]] = (mod, None)
    return out


def _calls_in(node: ast.AST, symbols: dict) -> list:
    """⇒ `[(模块, 函数, 行号)]` —— 只报**能解析到具体函数**的调用。

    ★ 三种形态都收：`f(...)` · `mod.f(...)` · `alias.f(...)`（`alias` 来自 `import sw_x as alias`）。
    """
    found = []
    for sub in ast.walk(node):
        if not isinstance(sub, ast.Call):
            continue
        fn = sub.func
        if isinstance(fn, ast.Name):
            hit = symbols.get(fn.id)
            if hit and hit[1]:
                found.append((hit[0], hit[1], sub.lineno))
        elif isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name):
            hit = symbols.get(fn.value.id)
            if hit and hit[1] is None:  # `import sw_x` 形态：取 attr 当函数名
                found.append((hit[0], fn.attr, sub.lineno))
    return found


def tool_map_from_specs() -> dict:
    """⇒ `{(模块, 函数): [工具名, …]}` —— ★ 来自声明式 `all_specs()`（459 条）。"""
    import register_capabilities as rc

    out: dict = defaultdict(list)
    for s in rc.all_specs():
        out[(_norm_module(s.module), s.function)].append(s.name)
    return {k: sorted(set(v)) for k, v in out.items()}


def tool_map_from_server() -> dict:
    """⇒ `{(模块, 函数): [工具名, …]}` —— ★ 来自 `server.py` 那 45 个**装饰器**工具。

    ★★ 为什么必须有这一半：★ 504 = 459 声明式 + 45 装饰器（★ 两条注册路径 ✓）——
      ★ 只看 `all_specs()` 会漏掉 `solidworks_connect` 那一族 ✓
    ⚠ 组织单元：★ 逐个**被 `@mcp.tool` 装饰的函数**走它**自己的函数体**，
      ★ 不跨函数收集 —— 否则会把别的工具的实现算进来（★ 事实 51）✓
    """
    out: dict = defaultdict(list)
    if not SERVER_PY.is_file():
        return {}
    tree = ast.parse(SERVER_PY.read_text(encoding="utf-8", errors="replace"))
    symbols = _imported_symbols(tree)
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        tool_name = None
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            for kw in dec.keywords:
                if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                    tool_name = kw.value.value
        if not tool_name:
            continue
        for mod, func, _ln in _calls_in(node, symbols):
            if tool_name not in out[(mod, func)]:
                out[(mod, func)].append(tool_name)
    return {k: sorted(set(v)) for k, v in out.items()}


def all_tools() -> dict:
    """⇒ `{(模块, 函数): [工具名, …]}` —— ★ 两条注册路径**合并**（客观事实，无政策）。"""
    merged = dict(tool_map_from_specs())
    for k, v in tool_map_from_server().items():
        merged[k] = sorted(set(merged.get(k, [])) | set(v))
    return merged


def _tool_tokens(tool: str) -> list:
    """★ 工具名 → 词序列（★ 剥掉已知前缀；★ 前缀是本仓命名规则 1 强制要求的 ✓）。"""
    for pre in TOOL_PREFIXES:
        if tool.startswith(pre):
            return [t for t in tool[len(pre) :].split("_") if t]
    return [t for t in tool.split("_") if t]


def _probe_tokens(stem: str) -> list:
    """★ 探针文件名 → 词序列（★ 剥掉 `probe_` / `prove_` 前缀）。"""
    for pre in ("probe_", "prove_"):
        if stem.startswith(pre):
            stem = stem[len(pre) :]
    return [t for t in stem.split("_") if t]


def _contains_run(hay: list, needle: list) -> bool:
    """★ `needle` 是否是 `hay` 的**连续子段**（★ 连续 —— 比"子集"严得多，★ 假阳性也少得多 ✓）。"""
    if not needle or len(needle) > len(hay):
        return False
    n = len(needle)
    return any(hay[i : i + n] == needle for i in range(len(hay) - n + 1))


def _parse(source: str) -> ast.AST:
    """★ 解析探针源码 —— ★ **只读它的调用图，不替它报语法警告** ✓。

    ⚠ 实测：某探针正文里有 `"\\d"`（非 raw 字符串里的坏转义）⇒ `ast.parse` 会往 **stderr**
      打一条 `SyntaxWarning: "\\d" is an invalid escape sequence`（★ 归属显示 `<unknown>`，
      ★ 与我无关、★ 也定位不到是哪个文件）⇒ ★ 把**我这个门禁的输出**搅浑 ✗
    ⇒ ★ 只在**本次解析**范围内静音 `SyntaxWarning`（★ 不吞别的警告、★ 不改探针 ✓）
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        return ast.parse(source)


def impl_index(tools: dict) -> dict:
    """⇒ `{工具名: [(模块, 函数), …]}` —— ★ 一个工具可能由多个实现函数认领 ✓。"""
    out: dict = defaultdict(list)
    for (mod, func), names in tools.items():
        for n in names:
            if (mod, func) not in out[n]:
                out[n].append((mod, func))
    return dict(out)


def analyse_probe(probe: str, source: str, impl_by_tool: dict) -> list:
    """★ **纯函数**：给定「探针名 + 源码」判它是不是已有工具的替代品。

    ★★ 做成纯函数是**为了能被负例测试直接喂样本**（事实 62：门禁只靠负例证明）——
      ★ 否则测试只能改真仓里的文件（★ 与 `test_refuted_patterns_gate.py` 的写-改-复原
      相比，纯函数不会污染工作树 ✓）。
    """
    tokens = _probe_tokens(Path(probe).stem)
    tree = _parse(source)
    called: dict = {}
    for mod, func, line in _calls_in(tree, _imported_symbols(tree)):
        called.setdefault((mod, func), line)
    hits = []
    for tool in sorted(impl_by_tool):
        if not _contains_run(tokens, _tool_tokens(tool)):
            continue
        for impl in impl_by_tool[tool]:
            if impl in called:
                hits.append(
                    {
                        "probe": probe if "/" in probe else "tools/" + probe,
                        "tool": tool,
                        "module": impl[0],
                        "function": impl[1],
                        "line": called[impl],
                    }
                )
    return hits


def scan() -> list:
    """⇒ `[{probe, tool, module, function, line}]` —— ★ 名字对应 ∧ 调用证据，两条都要 ✓。"""
    impl_by_tool = impl_index(all_tools())
    hits = []
    for pattern in PROBE_GLOBS:
        for path in sorted((ROOT / "tools").glob(pattern)):
            hits += analyse_probe(
                "tools/" + path.name,
                path.read_text(encoding="utf-8", errors="replace"),
                impl_by_tool,
            )
    return sorted(hits, key=lambda h: (h["probe"], h["tool"]))


def load_baseline() -> dict:
    if not BASELINE.is_file():
        return {"entries": []}
    try:
        return json.loads(BASELINE.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise SystemExit("★ 基线 %s 解析失败：%s" % (BASELINE, exc))


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description="探针复用门禁")
    ap.add_argument(
        "--report", action="store_true", help="★ 只打印命中的全表（不判基线）"
    )
    args = ap.parse_args(argv[1:])

    hits = scan()
    key = lambda h: (h["probe"], h["tool"])
    uniq = sorted({key(h): h for h in hits}.values(), key=key)

    if args.report:
        print("★ 探针复用 · 命中 **%d 条**「探针 × 工具」" % len(uniq))
        by_probe: dict = defaultdict(list)
        for h in uniq:
            by_probe[h["probe"]].append(h)
        for f in sorted(by_probe):
            for h in by_probe[f]:
                print(
                    "  %-58s L%-5d %s.%s  ⇒ 已有工具 %s"
                    % (h["probe"], h["line"], h["module"], h["function"], h["tool"])
                )
        return 0

    base = load_baseline()
    entries = base.get("entries") or []
    for e in entries:
        for f in ("probe", "tool", "module", "function", "reason"):
            if not str(e.get(f) or "").strip():
                print(
                    "★ 基线条目缺字段 `%s`（★ 一个没有理由的豁免等于没写）：%r" % (f, e)
                )
                return 1
    known = {(e["probe"], e["tool"]) for e in entries}
    got = {key(h) for h in uniq}

    new = sorted(got - known)
    stale = sorted(known - got)

    print("★ 探针复用门禁 —— 命中 %d 条 · 基线认可 %d 条" % (len(got), len(known)))
    if new:
        print()
        print(
            "  ★★ **新增命中 %d 条** ⇒ ★ 这些是「已有工具的替代品」，请改走工具层："
            % len(new)
        )
        for probe, tool in new:
            h = next(x for x in uniq if key(x) == (probe, tool))
            print(
                "      %s  L%d  %s.%s  ⇒ 已有工具 %s"
                % (probe, h["line"], h["module"], h["function"], tool)
            )
        print()
        print("  ★ 若该探针**确实不能**改（如探针要验的正是**工具层之下**的那一层），")
        print("    请把它登记进 docs/probe-reuse-baseline.json 并**写明理由**。")
    if stale:
        print()
        print(
            "  ★ **基线腐坏 %d 条** ⇒ ★ 名单里认了、实际已不存在（★ 名单要跟着改）："
            % len(stale)
        )
        for probe, tool in stale:
            print("      %s  %s" % (probe, tool))
    if not new and not stale:
        print("  ✓ 无新增命中、基线无腐坏")
    return 1 if (new or stale) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
