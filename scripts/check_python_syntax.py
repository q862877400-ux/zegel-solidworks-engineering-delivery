"""★ 门禁：**每个 `.py` 必须能 `ast.parse`**（★ 本会话同一处踩了**四次** ⇒ 机械化）。

## 为什么要有它（★ 四次实录）
```
★ 本会话**四次**新建文件时，把**来源块写进了头部 **三个双引号** 里面**（★ 忘了闭合 docstring）⇒
   Python 把后面几十行**当字符串吞掉** ⇒ 报的是
   `SyntaxError: invalid character '★' (U+2605)` —— ★ **错误信息指向的是那个星号，不是真因**。
   实录：`tools/modal_dialog_forensics.py` · `tests/test_deprecated_entry_interlock.py` ·
        `tools/extract_operation_descriptions.py` · `tools/judge_gap_candidates.py`。
★★ 而这类错**有一个统一且廉价的判据**：★ **`ast.parse` 能不能过** ⇒
   ★ 它一次抓住**所有**语法错（★ 含"docstring 未闭合把后文吞掉"这一类），
   ★ **比"再小心一点"可靠**（★ 事实 62：一个门禁写了不等于有效；★ 而这一条**有四次实录**当下限）。
```

## ★ 用法
```
python scripts/check_python_syntax.py          # 扫全部（exit 0 = 全过）
python scripts/check_python_syntax.py -v       # 列出扫过的目录与文件数
```

## ★ 覆盖面（★ 与 `release_check` 的其它门禁不重叠）
```
★ 扫 `scripts` `tools` `tests` `mcp-server` `subskills` 五个目录下的**全部** `.py`。
★ 不 import、不执行 —— ★ 只 `ast.parse`（★ 因而**不需要 SolidWorks、不需要依赖装好**）。
```

"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁）
# 文件:   scripts/check_python_syntax.py
# 定位:   把"文件头 docstring 未闭合"这一类**反复踩**的错机械化（objective⑤ 的同族：静态比对）。
# 官方依据: 不适用（★ 用 Python 标准库 `ast`）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ⚠ 本组为静态检查，未在本机实测（见 AGENTS.md 铁律 2）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DIRS = ("scripts", "tools", "tests", "mcp-server", "subskills")


def scan() -> tuple[int, list[str]]:
    """★ 回 `(扫过的文件数, 失败清单)`。"""
    total = 0
    bad: list[str] = []
    for sub in DIRS:
        base = REPO_ROOT / sub
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.py")):
            total += 1
            try:
                #: ★★ 2026-10-02（轮 375）**用 `compile` 而不是 `ast.parse`** ——
                #:   ★ 真例：某文件在 `from __future__ import annotations` **之前**
                #:   写了一个裸字符串（空 docstring）⇒ `ast.parse` **说 OK**，
                #:   而真跑报 `SyntaxError: from __future__ imports must occur at the beginning of the file`
                #:   ⇒ ★ **门禁有盲区** ⇒ 改用 `compile(..., "exec")`（★ 它走完整的编译期检查）。
                compile(p.read_text(encoding="utf-8"), str(p), "exec")
            except SyntaxError as exc:
                bad.append("%s:%s: %s" % (p.relative_to(REPO_ROOT), exc.lineno,
                                          (exc.msg or "").split("(")[0].strip()))
            except UnicodeDecodeError:
                bad.append("%s: 不是 UTF-8（★ 本仓库要求 UTF-8）" % p.relative_to(REPO_ROOT))
    return total, bad


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()
    total, bad = scan()
    if args.verbose:
        print("  扫过目录: %s" % ", ".join(DIRS))
    print("  .py 语法门禁 · 扫 **%d** 个文件 · 失败 **%d** 处" % (total, len(bad)))
    for b in bad[:20]:
        print("    ✗ %s" % b)
    if bad:
        print("  ⇒ ★ 修法：★ 多数是**头部 docstring 未闭合**（★ 来源块写进 `\"\"\"` 里了）"
              "—— ★ 在 `# ── 来源 ──` **之前**补 `\"\"\"`。")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
