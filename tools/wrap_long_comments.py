"""把超宽**注释行**按显示宽度折行（用 tokenize 精确定位，不碰代码与字符串）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/wrap_long_comments.py
# 定位:   ★ 2026-10-22（仓库统一化）：E501 共 16,801 条，其中**注释行 5,562 条（33%）**
# 。
#         注释折行是**语义安全**的（不动代码、不动字符串），故单独做成可批量执行的一步。
#         ★★ **只处理 tokenize 判定为 COMMENT 的行** —— 不按「以 # 开头」猜（那会把
#           字符串里的 `#` 也算进来）。
#         ★★ **机器可读指令一律跳过**：本仓有 `#: dispatch-arg:` / `#: dispatch-guard:` /
#           `# noqa` / `# isort:` / `# fmt:` / `# type:` / `# pragma:` 这些被门禁或工具解析的注释，
#           折行会**拆断它们**（第 9 轮踩过：折行把 `dispatch-arg` 拆断 ⇒ 门禁少算 12 个调用点）✗
# 官方依据: ruff 的 E501 按**显示宽度**算，CJK 字符计 2 列（第 7 轮实测：按字符数折行仍
# 违规）
#         ⇒ 本工具用 `unicodedata.east_asian_width` 判宽。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import io
import pathlib
import re
import sys
import tokenize
import unicodedata

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R = pathlib.Path(__file__).resolve().parents[1]
LIMIT = 88

#: ★★ 出现这些标记的注释**一律不折**（会被门禁/工具按行解析）
SKIP_MARKERS = (
    "# noqa",
    "# type:",
    "# pragma:",
    "# isort:",
    "# fmt:",
    "# pyright:",
)

#: ★★★ **通用规则：形如 `#: <name>:` 的注释一律不折。**
#:   本仓机器可读的指令都是这个形状（2026-10-22 全仓清点）：
#:     `enum-gate:` 56 · `dispatch-guard:` 37 · `arity-reflect:` 14 ·
#:     `dispatch-arg:` 7 · `dispatch-fwd:` 4 · `cd-site:` 2
#:   ★ 门禁靠「紧邻上方那一行」找它们（只跳空行）⇒ ★ 一折行，**续行就顶替了声明的位置**
#: ⇒ 门禁当场判「未表态」（2026-10-22 实测：折行后 `sw_sweep.py` 2 处 cd-site 被判未表态
#: ）✗
DIRECTIVE = re.compile(r"^#:\s*[a-z][a-z0-9-]*:")


def width(s: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)


def split_width(body: str, budget: int) -> list[str]:
    parts: list[str] = []
    cur = ""
    for ch in body:
        cw = 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1
        if width(cur) + cw > budget:
            parts.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        parts.append(cur)
    return parts


def wrap_file(path: pathlib.Path, write: bool) -> tuple[int, str]:
    """返回（折行数, 错误说明）。`write=False` 时只统计、不落盘。"""
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.split("\n")
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, IndentationError) as exc:
        return 0, f"tokenize 失败: {exc}"
    #: 收集需要折的注释行（1-based 行号 → 整行原文）
    #: ★★★ **只收「整行都是注释」的行** —— `tokenize` 的 COMMENT token 也可能是
    #:   **行尾注释**（如 `return None   # ★ 说明`）。★ 若不分这两种，就会把整行当纯注释
    #:   重建 ⇒ **代码部分被删掉** ⇒ 块变空 ⇒ `IndentationError` ✗
    #:   （2026-10-22 实测：不分这两种时，649 文件里 **45 个语法崩、108 个内容不守恒**。）
    targets: dict[int, str] = {}
    for tok in toks:
        if tok.type != tokenize.COMMENT:
            continue
        row = tok.start[0]
        raw = lines[row - 1]
        indent_len = len(raw) - len(raw.lstrip())
        if tok.start[1] != indent_len:
            continue  # ★ 行尾注释 ⇒ 整行不是注释 ⇒ 跳过（不改）
        if width(raw) <= LIMIT:
            continue
        if any(m in raw for m in SKIP_MARKERS):
            continue
        if DIRECTIVE.match(raw.lstrip()):
            continue  # ★ 机器可读指令 ⇒ 不折
        targets[row] = raw

    if not targets:
        return 0, ""

    out: list[str] = []
    n = 0
    for i, line in enumerate(lines, 1):
        raw = targets.get(i)
        if raw is None:
            out.append(line)
            continue
        indent = raw[: len(raw) - len(raw.lstrip())]
        stripped = raw.lstrip()
        lead = "#:" if stripped.startswith("#:") else "#"
        body = stripped[len(lead) :].lstrip()
        cont = indent + lead + " "
        budget = LIMIT - len(cont)
        parts = split_width(body, budget)
        if len(parts) <= 1:
            out.append(line)
            continue
        out.append(indent + lead + " " + parts[0])
        for p in parts[1:]:
            out.append(cont + p)
        n += 1
    if n and write:
        path.write_text("\n".join(out), encoding="utf-8")
    return n, ""


def main() -> int:
    write = "--write" in sys.argv
    roots = [a for a in sys.argv[1:] if not a.startswith("--")] or [
        "scripts",
        "tools",
        "mcp-server",
    ]
    total = 0
    files = 0
    errs: list[str] = []
    for r in roots:
        for f in (R / r).rglob("*.py"):
            s = str(f).replace("\\", "/")
            if "__pycache__" in s or "resources/skill" in s or "/archive/" in s:
                continue
            n, err = wrap_file(f, write)
            if err:
                errs.append(f"{f}: {err}")
            if n:
                total += n
                files += 1
    print(
        f"  ★ {'已折行' if write else '（dry-run）'} 文件 {files} 个 · 折行 {total} 处"
    )
    for e in errs[:5]:
        print("    ✗ " + e)
    if not write:
        print("  加 `--write` 才落盘")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
