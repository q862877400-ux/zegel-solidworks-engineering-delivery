"""★ 按**显示宽度**折长行（中文一个字符占 2 列，`len()` 会低估）。

## 为什么要有这个工具

本仓 ruff 的上限是 88 列，而 **E501 按显示宽度算**。
我用手写的 `len(l) > 88` 判断，中文行永远判不出来 ——
一天之内因此反复：折了还是超、改了还是红。

⇒ 把它做成工具：**输入文件名，反复折到 ruff 不再报 E501 为止**。
   （只折**注释**与**文档串**行；代码行只做安全的括号内断行，不敢乱动。）

## 用法

```
python -B tools/wrap_long_lines.py scripts/x.py [更多文件…]
python -B tools/wrap_long_lines.py --dry scripts/x.py     # 只看不改
```
"""
from __future__ import annotations

import subprocess
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parents[1]

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（工具 · 按显示宽度折长行）
# 文件:   tools/wrap_long_lines.py
# 定位:   把超过 88 **显示列**的行折开。起因：我用 len() 判断长度，
#          中文行被低估 ⇒ 折了仍超、反复返工。
# 官方依据: 不适用（ruff E501 的 88 列口径见 AGENTS.md 统一化门禁）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

LIMIT = 88


def width(s: str) -> int:
    """**显示宽度**：东亚宽字符算 2 列。"""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in s)


def e501_lines(path: Path) -> list:
    """问 ruff 要这份文件的 E501 行号（权威口径）。"""
    try:
        r = subprocess.run(
            [
                sys.executable, "-B", "-m", "ruff", "check",
                "--select", "E501", "--output-format", "concise", "--no-cache",
                str(path),
            ],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(R), timeout=120,
        )
    except Exception:  # noqa: BLE001
        return []
    out = []
    #: ★ 不能按 ":" 切 —— Windows 路径里 D: 也是冒号（第一版因此永远解析出 0 行）
    import re

    for ln in (r.stdout or "").splitlines():
        m = re.search(r":(\d+):(\d+): E501", ln)
        if m:
            out.append(int(m.group(1)))
    return sorted(set(out))


def _split_at(s: str, limit: int) -> tuple:
    """在空白处切一刀，使前半 ≤ limit（按显示宽度）。回 `(前, 后)` 或 `(s, "")`。"""
    best = -1
    for i, ch in enumerate(s):
        if ch in " ，、。｜·—":
            if width(s[:i]) <= limit:
                best = i
            else:
                break
    if best <= 0:
        return s, ""
    return s[:best].rstrip(), s[best:].lstrip()


def wrap_file(path: Path, *, dry: bool = False) -> int:
    """反复折到没有 E501。回折了几次。"""
    turns = 0
    for _ in range(12):  #: 防死循环
        bad = e501_lines(path)
        if not bad:
            break
        lines = path.read_text(encoding="utf-8").splitlines()
        changed = False
        for n in sorted(bad, reverse=True):
            if n > len(lines):
                continue
            ln = lines[n - 1]
            indent = ln[: len(ln) - len(ln.lstrip())]
            body = ln.strip()
            #: 只处理注释 / 文档串里的普通文本行；纯代码行**不硬折**
            if not (body.startswith("#") or body.startswith("*") or "，" in body
                    or "「" in body or "的" in body or "⇒" in body):
                continue
            head, tail = _split_at(body, LIMIT - width(indent))
            if not tail:
                continue
            if body.startswith("#"):
                prefix = "#:" if body.startswith("#:") else "#"
                #: 保留原注释前缀风格
                if body.startswith("#:"):
                    head, tail = head, tail
                    cont = indent + "#:" + " " + tail
                else:
                    cont = indent + prefix + " " + tail
            else:
                cont = indent + tail
            lines[n - 1:n] = [indent + head, cont]
            changed = True
            turns += 1
        if not changed:
            break
        if not dry:
            path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        else:
            break
    return turns


def main() -> int:
    dry = "--dry" in sys.argv
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not files:
        print("用法：python -B tools/wrap_long_lines.py [--dry] <文件…>")
        return 2
    total = 0
    for f in files:
        p = R / f if not Path(f).is_absolute() else Path(f)
        before = len(e501_lines(p))
        n = wrap_file(p, dry=dry)
        after = len(e501_lines(p))
        total += before - after
        print("%-52s E501 %d → %d（折 %d 次）" % (p.name, before, after, n))
    print("合计减少 E501：%d" % total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
