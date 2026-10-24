"""K 维度观测器：501 条 ToolSpec 声明 ↔ 实际代码的对应关系（只读，不 import）。

核什么（全部静态 AST，不 import 任何 scripts 模块，避免触发 COM）：
  ① `module` 指向的 .py 文件是否存在
  ② `function` 指向的函数是否在该文件里（顶层 def）
  ③ 函数形参名 vs 声明参数名（经 `param_alias` 映射后）是否一一对得上
  ④ `inject` 的关键字名是否是函数的真实形参
  ⑤ 有多余/缺失的形参

跑法：python docs\\state\\probes\\probe_specs_vs_code.py --json docs/state/inventory-k.json
"""
from __future__ import annotations

import argparse
import ast
import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "mcp-server"))
sys.path.insert(0, str(ROOT / "scripts"))

import register_capabilities as rc  # noqa: E402


def module_path(module: str) -> pathlib.Path | None:
    if not module:
        return None
    base = ROOT / "scripts"
    cand = base.joinpath(*module.split("."))
    for p in (cand.with_suffix(".py"), cand / "__init__.py"):
        if p.exists():
            return p
    return None


def top_level_funcs(path: pathlib.Path) -> dict[str, ast.FunctionDef]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return {}
    return {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    specs = rc.all_specs()
    stats = collections.Counter()
    no_module, no_file, no_func = [], [], []
    param_mismatch, inject_missing = [], []
    rows = []

    func_cache: dict[pathlib.Path, dict[str, ast.FunctionDef]] = {}

    for s in specs:
        stats["total"] += 1
        if not s.module or not s.function:
            stats["no_module_or_function"] += 1
            no_module.append(s.name)
            continue
        mp = module_path(s.module)
        if mp is None:
            stats["module_file_missing"] += 1
            no_file.append({"tool": s.name, "module": s.module})
            continue
        if mp not in func_cache:
            func_cache[mp] = top_level_funcs(mp)
        fn = func_cache[mp].get(s.function)
        if fn is None:
            stats["function_missing"] += 1
            no_func.append({"tool": s.name, "module": s.module, "function": s.function})
            continue
        stats["resolved"] += 1

        fn_params = [a.arg for a in fn.args.args] + [a.arg for a in fn.args.kwonlyargs]
        # inject 关键字必须在形参里
        if s.inject:
            if s.inject not in fn_params:
                stats["inject_not_in_signature"] += 1
                inject_missing.append(
                    {"tool": s.name, "inject": s.inject, "func": f"{s.module}.{s.function}",
                     "fn_params": fn_params[:8]}
                )
        # 声明参数（经 param_alias 映射）→ 目标形参名
        alias = dict(getattr(s, "param_alias", {}) or {})
        declared = []
        for p in getattr(s, "params", []) or []:
            target = alias.get(p.name, p.name)
            if target is None:  # 由解析器消费，不传给函数
                continue
            declared.append(target)
        missing_in_fn = [d for d in declared if d not in fn_params]
        if missing_in_fn:
            stats["declared_param_not_in_signature"] += 1
            param_mismatch.append(
                {"tool": s.name, "func": f"{s.module}.{s.function}",
                 "declared_missing": missing_in_fn[:5], "fn_params": fn_params[:8]}
            )
        # 反向：函数有、但声明面没暴露的形参（实现面 ⊃ 声明面）
        exposed = set(declared) | ({s.inject} if s.inject else set())
        omitted = set(getattr(s, "omitted_params", []) or [])
        skip_internal = {"self", "cls"}
        undeclared = [
            p for p in fn_params
            if p not in exposed and p not in omitted and p not in skip_internal
        ]
        if undeclared:
            stats["has_undeclared_params"] += 1
            rows.append(
                {
                    "tool": s.name, "module": s.module, "function": s.function,
                    "inject": s.inject, "declared": len(declared), "fn_params": len(fn_params),
                    "undeclared": undeclared[:6], "undeclared_n": len(undeclared),
                }
            )
            continue
        rows.append(
            {
                "tool": s.name,
                "module": s.module,
                "function": s.function,
                "inject": s.inject,
                "declared": len(declared),
                "fn_params": len(fn_params),
            }
        )

    data = {
        "stats": dict(stats),
        "module_file_missing": no_file[:15],
        "function_missing": no_func[:15],
        "inject_not_in_signature": inject_missing[:15],
        "declared_param_not_in_signature": param_mismatch[:15],
        "counts": {
            "module_file_missing": len(no_file),
            "function_missing": len(no_func),
            "inject_not_in_signature": len(inject_missing),
            "declared_param_not_in_signature": len(param_mismatch),
        },
    }

    print(f"声明 {stats['total']} 条 · 解析到函数 {stats['resolved']}")
    print(f"  模块文件不存在 {len(no_file)} · 函数不存在 {len(no_func)}")
    print(f"  inject 不在形参里 {len(inject_missing)} · 声明参数不在形参里 {len(param_mismatch)}")
    for k, v in list(data["counts"].items()):
        if v:
            print(f"  {k} 前几例：")
            for r in data[k][:4]:
                print("    ", r)

    if args.json:
        out = pathlib.Path(args.json)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({**data, "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("已写出:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())