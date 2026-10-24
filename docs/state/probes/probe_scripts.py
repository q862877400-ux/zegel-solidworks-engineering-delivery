"""D 维度观测器：`scripts/` 脚本层现状（只读）。

记录：模块数、语法可解析性、函数数、被工具层引用的模块数、未被引用的模块、
以及 ruff/克隆读数（复用 `check_repo_uniformity.py` 的输出）。
不 import 任何 scripts 模块（避免触发 COM）。
"""
from __future__ import annotations

import argparse
import ast
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    files = sorted(SCRIPTS.glob("*.py"))
    data: dict = {"script_files": len(files)}

    parse_fail = []
    funcs = 0
    classes = 0
    no_docstring = 0
    has_source_block = 0
    for p in files:
        src = p.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(src)
        except SyntaxError as exc:
            parse_fail.append({"file": p.name, "line": exc.lineno, "msg": exc.msg})
            continue
        if not ast.get_docstring(tree):
            no_docstring += 1
        if "# ── 来源" in src:
            has_source_block += 1
        funcs += sum(1 for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
        classes += sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))

    data["syntax_errors"] = parse_fail
    data["functions_total"] = funcs
    data["classes_total"] = classes
    data["modules_without_docstring"] = no_docstring
    data["modules_with_source_block"] = has_source_block

    # 被工具层引用的模块
    sys.path.insert(0, str(ROOT / "mcp-server"))
    sys.path.insert(0, str(SCRIPTS))
    import register_capabilities as rc  # noqa: PLC0415

    used_mods = {s.module for s in rc.all_specs() if s.module}
    top_level_used = {m.split(".")[0] for m in used_mods}
    existing = {p.stem for p in files}
    data["modules_referenced_by_toolspec"] = len(top_level_used & existing)
    data["referenced_but_missing"] = sorted(top_level_used - existing)
    data["scripts_never_referenced_by_toolspec"] = sorted(existing - top_level_used)

    # 被 tests / tools 引用的情况（粗粒度：全仓文本搜索）
    never = []
    corpus = []
    for p in list((ROOT / "tools").glob("*.py")) + list((ROOT / "tests").glob("*.py")):
        try:
            corpus.append(p.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            continue
    blob = "\n".join(corpus)
    for name in data["scripts_never_referenced_by_toolspec"]:
        if name not in blob:
            never.append(name)
    data["scripts_never_referenced_anywhere_in_tools_tests"] = never

    # ruff / 克隆读数（复用既有门禁输出）
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_repo_uniformity.py")],
            cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=600,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        data["uniformity_readings"] = {
            m.group(1): m.group(2)
            for m in re.finditer(r"\[(?:PASS|FAIL|INFO)\]\s*([①②③④⑤][^\n=]*?)=\s*(\d+)", out)
        }
        data["uniformity_exit"] = proc.returncode
    except Exception as exc:  # noqa: BLE001
        data["uniformity_readings"] = {"error": f"{type(exc).__name__}: {exc}"}

    print(f"scripts/*.py {data['script_files']} 个 · 语法错误 {len(data['syntax_errors'])}")
    print(f"函数 {data['functions_total']} · 类 {data['classes_total']}")
    print(f"无 docstring {data['modules_without_docstring']} · 有来源块 {data['modules_with_source_block']}")
    print(f"被 ToolSpec 引用 {data['modules_referenced_by_toolspec']} · 引用但不存在 {len(data['referenced_but_missing'])}")
    print(f"未被 ToolSpec 引用 {len(data['scripts_never_referenced_by_toolspec'])} · 其中在 tools/tests 里也搜不到 {len(data['scripts_never_referenced_anywhere_in_tools_tests'])}")
    print(f"统一化门禁读数 {data.get('uniformity_readings')}")

    if args.json:
        out = pathlib.Path(args.json)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("已写出:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())