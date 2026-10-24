"""F 维度观测器：`tests/` 测试层现状（只读）。

记录：测试文件数、`def test_` 数量、**收集期是否通过**（`pytest --collect-only`）、
收集失败的文件与异常类型。不执行任何用例。
"""
from __future__ import annotations

import argparse
import ast
import collections
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
TESTS = ROOT / "tests"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    files = sorted(TESTS.glob("test_*.py"))
    data: dict = {"test_files": len(files)}

    per_file = []
    total_tests = 0
    no_test_files = []
    async_tests = 0
    skip_marks = 0
    for p in files:
        src = p.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(src)
        except SyntaxError as exc:
            per_file.append({"file": p.name, "tests": -1, "syntax_error": f"L{exc.lineno}: {exc.msg}"})
            continue
        n = sum(
            1
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
        )
        total_tests += n
        if n == 0:
            no_test_files.append(p.name)
        if "pytest.mark.asyncio" in src:
            async_tests += 1
        skip_marks += src.count("pytest.mark.skip")

    data["test_functions_total"] = total_tests
    data["files_without_test_functions"] = no_test_files
    data["files_using_asyncio_mark"] = async_tests
    data["pytest_mark_skip_occurrences"] = skip_marks

    # 收集期（不执行用例）
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests", "--collect-only", "-q",
             "-p", "no:cacheprovider"],
            cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=900,
        )
        out = (proc.stdout or "") + (proc.stderr or "")
        data["collect_exit"] = proc.returncode
        m = re.search(r"(\d+)\s+tests?\s+collected", out)
        data["collected"] = int(m.group(1)) if m else None
        errs = re.findall(r"ERROR\s+(tests/\S+)\s*-\s*(.+)", out)
        data["collect_errors"] = len(errs)
        data["collect_error_sample"] = errs[:8]
        kinds = collections.Counter(re.sub(r"[:(].*", "", e[1]).strip() for e in errs)
        data["collect_error_kinds"] = dict(kinds.most_common(8))
        tail = [ln for ln in out.splitlines() if "error" in ln.lower()][-3:]
        data["collect_tail"] = tail
    except Exception as exc:  # noqa: BLE001
        data["collect_exit"] = -1
        data["collect_error_kinds"] = {"<probe failed>": f"{type(exc).__name__}: {exc}"}

    print(f"tests/test_*.py {data['test_files']} 个 · def test_ 共 {data['test_functions_total']} 个")
    print(f"无 test_ 函数的文件 {len(no_test_files)} · 用 asyncio.mark 的文件 {async_tests} · skip 标记 {skip_marks}")
    print(f"收集期 exit={data.get('collect_exit')} · collected={data.get('collected')} · 收集错误 {data.get('collect_errors')}")
    print(f"错误类型分布 {data.get('collect_error_kinds')}")
    for s in data.get("collect_error_sample", []):
        print("  ERR", s[0], "→", s[1][:110])

    if args.json:
        out = pathlib.Path(args.json)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({**data, "per_file": per_file}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("已写出:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())