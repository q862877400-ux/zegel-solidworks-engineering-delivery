"""把 ruff 报的 N812 / N806 改名成 PEP 8 口径（★ 每个名字全文件唯一才动）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/rename_pep8_names.py
# 定位:   ★ 2026-10-22（仓库统一化 · 业主「同一个东西在不同地方命名不一样」）：
#         处理 ruff 的两条命名规则 ——
#           · `N812`：`import x as X`（★ 小写模块被导入成大写别名）
#           · `N806`：**函数内局部变量**用了大写（★ 模块级常量用大写是对的，局部的不是）
#         判据来源：PEP 8「模块名 lowercase / 函数内局部变量 lowercase / 常量 UPPER_CASE」，
#         与 Google Python Style Guide 的 naming 段一致。
# ★★ 安全前提（**只改**满足全部条件者，否则跳过并列出来）：
#     ① 该名字在**本文件里绑定次数 == 1**（多绑 = 可能是另一个东西，不动）
#     ② 目标小写名在**本文件里从未出现**（避免撞名）
#     ③ 改完 `ast.parse` 必须通过
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import json
import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R = pathlib.Path(__file__).resolve().parents[1]
SCAN = ("scripts", "tools", "mcp-server")
RULES = ("N812", "N806")


def ruff_sites(rule: str) -> list[tuple[str, str]]:
    """⇒ [(文件, 名字)]（按 ruff 的 json 输出）。"""
    p = subprocess.run(
        [sys.executable, "-m", "ruff", "check", *SCAN, "--select", rule,
         "--output-format", "json", "--no-cache"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(R),
    )
    try:
        rows = json.loads(p.stdout or "[]")
    except json.JSONDecodeError:
        return []
    out = []
    for it in rows:
        msg = it.get("message", "")
        names = re.findall(r"`([^`]+)`", msg)
        if names:
            out.append((it["filename"], names[-1]))
    return out


def _target_bound(tgt: ast.AST, name: str) -> int:
    """⇒ 赋值目标（含元组/列表解包）里绑定 `name` 的次数。"""
    if isinstance(tgt, ast.Name):
        return 1 if tgt.id == name else 0
    if isinstance(tgt, (ast.Tuple, ast.List)):
        return sum(_target_bound(e, name) for e in tgt.elts)
    if isinstance(tgt, ast.Starred):
        return _target_bound(tgt.value, name)
    return 0


def bound_count(tree: ast.AST, name: str) -> int:
    """⇒ 该名字在文件里被**绑定**的次数（导入别名 / 赋值 / def / 形参 / except-as）。"""
    n = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for a in node.names:
                if (a.asname or a.name) == name:
                    n += 1
        elif isinstance(node, ast.Import):
            for a in node.names:
                if (a.asname or a.name.split(".")[0]) == name:
                    n += 1
        elif isinstance(node, ast.Assign):
            for tgt in node.targets:
                n += _target_bound(tgt, name)
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == name:
                n += 1
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == name:
                n += 1
            for a in list(node.args.args) + list(node.args.kwonlyargs) if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef)) else []:
                if a.arg == name:
                    n += 1
        elif isinstance(node, ast.ExceptHandler) and node.name == name:
            n += 1
    return n


def main() -> int:
    write = "--write" in sys.argv
    plan: dict[str, set[str]] = {}
    for rule in RULES:
        for fname, name in ruff_sites(rule):
            plan.setdefault(fname, set()).add(name)

    renamed = skipped = files = 0
    reasons: list[str] = []
    for fname, names in sorted(plan.items()):
        path = pathlib.Path(fname)
        try:
            src = path.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src)
        except (OSError, SyntaxError) as exc:
            reasons.append(f"{path.name}: 读/解析失败 {exc}")
            continue
        changed = False
        for name in sorted(names):
            low = name.lower()
            if low == name:
                continue
            if bound_count(tree, name) != 1:
                reasons.append(f"{path.name}: `{name}` 绑定 {bound_count(tree, name)} 次 ⇒ 跳过")
                skipped += 1
                continue
            if re.search(r"\b%s\b" % re.escape(low), src):
                reasons.append(f"{path.name}: 目标名 `{low}` 已存在 ⇒ 跳过")
                skipped += 1
                continue
            new_src = re.sub(r"\b%s\b" % re.escape(name), low, src)
            try:
                ast.parse(new_src)
            except SyntaxError:
                reasons.append(f"{path.name}: 改 `{name}` 后语法崩 ⇒ 跳过")
                skipped += 1
                continue
            src = new_src
            renamed += 1
            changed = True
        if changed:
            files += 1
            if write:
                path.write_text(src, encoding="utf-8")

    print(f"  ★ {'已改名' if write else '（dry-run）'} 名字 {renamed} 个 · 文件 {files} 个 · 跳过 {skipped} 处")
    for r in reasons[:8]:
        print("    跳过: " + r)
    if not write:
        print("  加 `--write` 才落盘")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
