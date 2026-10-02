"""★ 把运行时文件里写死的旧代码仓绝对路径，改成 __file__ 自定位。

★ 做法只有一个模式：在 r-string 里把前缀 `C:\\swprojects\\sw-skill-fork` 换成
  `" + _ROOT_S + r"` —— 因为 `r"<前缀>\\docs\\x"` 变成 `r"" + _ROOT_S + r"\\docs\\x"`
  仍然是**合法 Python**，值为 `_ROOT_S + "\\docs\\x"`。
★ 注释行则把前缀直接去掉（变成仓库内相对路径的读法）。
★ 每个改过的 .py 会插入一行 `_ROOT_S = str(Path(__file__).resolve().parents[D])`
  （D = 该文件相对仓库根的层级数；根目录下的文件 D=0）。
"""

import ast
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"D:\AI\SW")
LIT = "C:\\swprojects\\sw-skill-fork"
DIRS = ("scripts", "tools", "tests", "mcp-server", "apps", "agents", "subskills")
CONST = "_ROOT_S"


def depth_of(p: Path) -> int:
    return len(p.relative_to(ROOT).parts) - 1


def insert_const(text: str, d: int) -> str:
    """★ 在最后一个顶层 import 之后插入常量定义。"""
    if CONST in text:
        return text
    lines = text.splitlines()
    last = -1
    for i, l in enumerate(lines[:120]):
        s = l.rstrip()
        if re.match(r"^(import |from )", s) and not s.endswith("(") and not s.endswith("\\"):
            last = i
    if last < 0:
        return text
    #: \u2605 \u8df3\u8fc7\u7d27\u8ddf\u7740\u7684\u7eed\u884c\uff08\u62ec\u53f7\u5305\u8d77\u6765\u7684 import\uff09
    j = last + 1
    while j < len(lines) and (lines[j].startswith((" ", "\t", ")")) or not lines[j].strip()):
        j += 1
        if j - last > 40:
            break
    ins = ["", "#: \u2605 \u672c\u4ed3\u5e93\u6839\uff08\u2605 2026-10-03 \u5408\u5e76\u540e\u81ea\u5b9a\u4f4d\uff0c\u4ee3\u66ff\u5199\u6b7b\u7684\u65e7\u4ee3\u7801\u4ed3\u8def\u5f84\uff09",
           "%s = str(Path(__file__).resolve().parents[%d])" % (CONST, d)]
    return "\n".join(lines[:j] + ins + lines[j:]) + ("\n" if text.endswith("\n") else "")


def main() -> int:
    targets = []
    for d in DIRS:
        base = ROOT / d
        if base.is_dir():
            targets += [p for p in base.rglob("*") if p.suffix in (".py", ".ps1") and p.is_file()]
    #: ★★ 2026-10-03：**只**改运行时目录下的文件。
    #:   ⚠ 上一次我多写了一行 `ROOT.glob("*.py")`，把仓库根那 **1055 个一次性草稿**
    #:     也扫进来 ⇒ 改了 1091 个文件（远超要改的 56 个）⇒ 已回退。
    #:   ★ 教训：**目标清单要显式**，不要用"目录遍历"当成"要改的东西"。
    changed, skipped, bad = [], [], []
    for p in targets:
        try:
            raw = p.read_text(encoding="utf-8")
        except Exception:                                      # noqa: BLE001
            continue
        if LIT not in raw and LIT.replace("\\", "/") not in raw:
            continue
        d = depth_of(p)
        out = []
        n_code = n_cmt = n_other = 0
        for line in raw.splitlines():
            st = line.lstrip()
            if LIT in line:
                if st.startswith("#") or st.startswith("//"):
                    line = line.replace(LIT + "\\", "").replace(LIT, "")
                    n_cmt += 1
                elif 'r"' + LIT in line or "r'" + LIT in line:
                    line = line.replace(LIT, '" + %s + r"' % CONST)
                    n_code += 1
                else:
                    n_other += 1
            out.append(line)
        if n_code:
            new = insert_const("\n".join(out) + ("\n" if raw.endswith("\n") else ""), d)
            try:
                ast.parse(new)
            except SyntaxError as exc:
                bad.append("%s: %s" % (p.relative_to(ROOT), exc))
                continue
            p.write_text(new, encoding="utf-8")
            changed.append((str(p.relative_to(ROOT)), n_code, n_cmt, d))
        elif n_cmt or n_other:
            new = "\n".join(out) + ("\n" if raw.endswith("\n") else "")
            p.write_text(new, encoding="utf-8")
            skipped.append((str(p.relative_to(ROOT)), n_code, n_cmt, n_other))
    print("  \u2605 \u5df2\u6539\uff08\u542b\u4ee3\u7801\uff09\uff1a**%d** \u4e2a\u6587\u4ef6" % len(changed))
    for r, c, m, d in changed:
        print("      %-52s \u4ee3\u7801%-3d \u6ce8\u91ca%-3d parents[%d]" % (r, c, m, d))
    if skipped:
        print("  \u2605 \u53ea\u6709\u6ce8\u91ca/\u5176\u4ed6\uff1a**%d** \u4e2a" % len(skipped))
        for r, c, m, o in skipped:
            print("      %-52s \u6ce8\u91ca%-3d \u5176\u4ed6%d" % (r, m, o))
    if bad:
        print("  **\u8bed\u6cd5\u574f\u4e86\u800c\u56de\u9000\uff1a%d**" % len(bad))
        for b in bad:
            print("      " + b)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
