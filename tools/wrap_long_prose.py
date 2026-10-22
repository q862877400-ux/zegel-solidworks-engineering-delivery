"""把超过显示宽度上限的 **docstring / 长字符串行**按标点折行（中文不插空格）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/wrap_long_prose.py
# 定位:   ★ 2026-10-22（仓库统一化）：`check_repo_uniformity.py` 的 ②/① 判据改成**两档**
#         之后（代码行 88 / 散文行 120），剩下的超宽行全在 **docstring 与长字符串**里，
#         而 `tools/wrap_long_comments.py` 只处理**注释**（COMMENT token）。
#         本工具补上这一块：**只在中文/英文标点处断行**，★ 中文行**不插空格**（无空格可插）。
# 官方依据: 不适用（纯文本重排）。宽度口径与 ruff 的 `E501` 一致 —— 用
#         `scripts/display_width.py`（CJK 计 2 列）。
# ★★ 边界（刻意写死）：
#     · 只动 **docstring 与隐式拼接的相邻字符串字面量所在行**，不动代码逻辑；
#     · 断点优先取 `，。；：、！？,.;:!?）)》】` 之后；没有标点就退回在预算处硬断；
#     · 每行断完必须仍 ≤ 上限；
#     · 改完 `ast.parse` 必须过（由调用方复核）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import io
import pathlib
import sys
import tokenize

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from display_width import display_width  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R = pathlib.Path(__file__).resolve().parents[1]
LIMIT = 120
#: ★ 优先在这些字符**之后**断行（中文标点后断，读者看不出被切）
BREAK_AFTER = "，。；：、！？,.;:!?）)》】」』"


def split_prose(text: str, budget: int) -> list[str] | None:
    """把一段散文按显示宽度折成多行；⇒ 行列表（折不动就回 `None`）。"""
    if display_width(text) <= budget:
        return None
    out: list[str] = []
    rest = text
    while display_width(rest) > budget:
        # 在预算内找**最后一个**标点
        cut = -1
        acc = 0
        for i, ch in enumerate(rest):
            acc += display_width(ch)
            if acc > budget:
                break
            if ch in BREAK_AFTER:
                cut = i + 1
        if cut <= 0:
            # 没有标点 ⇒ 在预算处硬断（按显示宽度）
            acc = 0
            cut = len(rest)
            for i, ch in enumerate(rest):
                acc += display_width(ch)
                if acc > budget:
                    cut = i
                    break
        out.append(rest[:cut])
        rest = rest[cut:].lstrip()
    if rest:
        out.append(rest)
    return out


def wrap_file(path: pathlib.Path, write: bool) -> tuple[int, str]:
    """⇒（折行数, 错误说明）。只动 docstring / 字符串**所在的行**。"""
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)
    except (OSError, SyntaxError) as exc:
        return 0, f"读/解析失败: {exc}"
    lines = src.split("\n")

    #: 收集「字符串 token 覆盖的行」⇒ 这些行才允许折
    str_rows: set[int] = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.STRING:
                str_rows.update(range(tok.start[0], tok.end[0] + 1))
    except (tokenize.TokenError, IndentationError) as exc:
        return 0, f"tokenize 失败: {exc}"

    #: docstring 节点 ⇒ 其首行所在行号（用于取缩进与引号）
    doc_rows: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(
                    body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                doc_rows[body[0].lineno] = body[0]

    out: list[str] = []
    n = 0
    for idx, line in enumerate(lines, 1):
        if idx not in str_rows or display_width(line) <= LIMIT:
            out.append(line)
            continue
        stripped = line.strip()
        lead = line[: len(line) - len(line.lstrip())]
        #: ★ 只折「纯散文行」—— 排除含赋值 / 定义 / 导入的行
        #:   （★ 符号只排除 `=`：散文里本来就会有括号与反引号）
        ok = "=" not in stripped and not stripped.startswith(
            ("def ", "class ", "import ", "from ", "return ", "assert "))
        if not ok:
            out.append(line)
            continue
        parts = split_prose(stripped, LIMIT - len(lead))
        if not parts or len(parts) <= 1:
            out.append(line)
            continue
        out.extend([lead + parts[0]] + [lead + p for p in parts[1:]])
        n += 1

    if n and write:
        new = "\n".join(out)
        try:
            ast.parse(new)                 # ★ 语法不过就不写
        except SyntaxError as exc:
            return 0, f"折后语法崩（已跳过）: {exc.msg}"
        path.write_text(new, encoding="utf-8")
    return n, ""


def main() -> int:
    write = "--write" in sys.argv
    total = files = 0
    for d in ("scripts", "tools", "mcp-server"):
        for f in (R / d).rglob("*.py"):
            s = str(f).replace("\\", "/")
            if "__pycache__" in s:
                continue
            c, err = wrap_file(f, write)
            if err:
                print(f"    ✗ {f.name}: {err}")
            if c:
                total += c
                files += 1
    print(f"  ★ {'已折行' if write else '（dry-run）'} 文件 {files} 个 · 折行 {total} 处（上限 {LIMIT} 显示列）")
    if not write:
        print("  加 `--write` 才落盘")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
