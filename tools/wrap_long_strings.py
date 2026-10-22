"""把超宽**单行字符串字面量**按隐式拼接折行（★ 字符串内容一个字节都不变）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/wrap_long_strings.py
# 定位:   ★ 2026-10-22（仓库统一化）：两档 `E501` 判据下，最后一批超宽行里有 **396 条是
#         `doc="……"` 这类单行字符串字面量**（`tool_specs_batch*.py` 最宽 379 显示列）。
#         `tools/wrap_long_prose.py` 只能折三引号串；单引号串一折就「未终止字符串」✗
#         ⇒ 本工具用 **Python 的隐式字符串拼接**折：
#             ``doc="前半""后半"``  ⇒  ``doc="前半"\n    "后半"``
#         ★★ **拼接不加换行** ⇒ `doc` 的值**逐字不变** ✓
# 官方依据: Python 语言参考 — 「Adjacent string literals are concatenated」（隐式拼接）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import ast
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from display_width import display_width  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R = pathlib.Path(__file__).resolve().parents[1]
LIMIT = 120
BREAK_AFTER = "，。；：、！？,.;:!?）)》】」』 "
#: ★ 只接「`名字="……"` 或 `名字='……'`，行尾可能带逗号/右括号」这种形态
ONE = re.compile(r'^(\s*)([A-Za-z_]\w*)=(["\'])(.*)\3(\s*[,)])?\s*$')


def chunks(text: str, budget: int) -> list[str]:
    """按显示宽度切块；优先在标点/空格后断（★ 断点处不增删任何字符）。"""
    out: list[str] = []
    rest = text
    while display_width(rest) > budget:
        cut = -1
        acc = 0
        for i, ch in enumerate(rest):
            acc += display_width(ch)
            if acc > budget:
                break
            if ch in BREAK_AFTER:
                cut = i + 1
        if cut <= 0:
            acc = 0
            cut = len(rest)
            for i, ch in enumerate(rest):
                acc += display_width(ch)
                if acc > budget:
                    cut = i
                    break
        out.append(rest[:cut])
        rest = rest[cut:]
    if rest:
        out.append(rest)
    return out


def wrap_file(path: pathlib.Path, write: bool) -> tuple[int, str]:
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
        ast.parse(src)
    except (OSError, SyntaxError) as exc:
        return 0, f"读/解析失败: {exc}"
    out: list[str] = []
    n = 0
    for line in src.split("\n"):
        if display_width(line) <= LIMIT:
            out.append(line)
            continue
        m = ONE.match(line)
        if not m:
            out.append(line)
            continue
        lead, name, quote, body, tail = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5) or ""
        if quote * 3 in body:
            out.append(line)
            continue
        budget = LIMIT - len(lead) - len(name) - 3
        parts = chunks(body, budget)
        if len(parts) <= 1:
            out.append(line)
            continue
        cont = lead + " " * (len(name) + 2)
        out.append(f"{lead}{name}={quote}{parts[0]}{quote}")
        for j, p in enumerate(parts[1:]):
            last = j == len(parts) - 2
            out.append(f"{cont}{quote}{p}{quote}{tail if last else ''}")
        n += 1
    if n and write:
        new = "\n".join(out)
        try:
            ast.parse(new)
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
