"""修剩下的 4 处 `text=True` 缺 `encoding=`（含**单行参数**形式）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**上游文件的缺陷修复**）+ Python 标准库 `subprocess` 文档
# 文件:   tests/test_cad_studio_cli.py（2 处）· apps/desktop/cad_workbench/queue_worker.py（2 处）
# 定位:   轮 46 新门禁 `scripts/check_env_pitfalls.py` **抓出轮 45 的一次性清扫漏了这 4 处**：
#         · 测试里那 2 处是**单行参数**（`text=True, check=False,` 同行），
#           轮 45 的正则要求 `text=True,` **独立成行** ⇒ 漏掉；
#         · `apps/desktop/` 那 2 处**根本没在那个清扫的扫描目录里**。
#         **⇒ 这次用**括号配对**切分调用段（事实 58），按 `text=True` 的**实际位置**插入。**
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 顺序：**先改代码、后写来源块**（事实 60 —— 否则说明块会落进扫描范围被改坏）。
# ⚠ 长内容走**短的单行字符串**（事实 48 定则）；跑完核对落盘。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\swprojects\sw-skill-fork")

#: 每个文件要加的来源块（**代码改完后再加**，事实 60）
BLOCK = (
    "# ── 来源 ──\n"
    "# 仓库:   本项目自身（**上游文件的缺陷修复**）+ Python 标准库 `subprocess` 文档\n"
    "# 文件:   %s\n"
    "# 定位:   ⚠ `subprocess` 用了 `text=True` 但**没给 `encoding=`** ⇒ 父进程用\n"
    "#         `locale.getpreferredencoding()`（中文 Windows 是 **GBK**）解子进程的\n"
    "#         **UTF-8 中文**输出 ⇒ `UnicodeDecodeError` ⇒ `stdout` 变 **None** ⇒\n"
    "#         `json.loads(None)` 抛 `TypeError`（**错误信息指向不了真因**，事实 58）。\n"
    "#         **⇒ 已补 `encoding=\"utf-8\", errors=\"replace\"`。**\n"
    "#         ★ 这 4 处是轮 46 的**门禁**（`scripts/check_env_pitfalls.py`）从轮 45 的\n"
    "#           一次性清扫里**补抓**出来的：测试里 2 处是**单行参数**形式、\n"
    "#           `apps/desktop/` 那 2 处**当时不在扫描目录里**。\n"
    "# 许可:   本仓库 MIT。无第三方代码引入。\n"
    "# 覆盖:   全文件\n"
    "# ─────────────────────────────────────────────────────────────────────────\n"
)


def balanced(text: str, start: int) -> tuple:
    i = text.find("(", start)
    if i < 0:
        return "", -1, -1
    depth, j = 0, i
    while j < len(text):
        if text[j] == "(":
            depth += 1
        elif text[j] == ")":
            depth -= 1
            if depth == 0:
                return text[i:j + 1], i, j + 1
        j += 1
    return text[i:], i, len(text)


def fix(path: Path) -> int:
    t = path.read_text(encoding="utf-8")
    out, last, n = [], 0, 0
    for m in re.finditer(r"subprocess\.(run|Popen|check_output|check_call)\s*\(", t):
        seg, s, e = balanced(t, m.start())
        if s < last or "text=True" not in seg or "encoding=" in seg:
            continue
        k = seg.index("text=True") + len("text=True")
        # 缩进取 `text=True` 所在行的行首空白
        line_start = seg.rfind("\n", 0, k) + 1
        indent = re.match(r"[ \t]*", seg[line_start:]).group(0)
        # 同行时 `text=True,` 后面还有内容 ⇒ 在它之后**就地**插入，用空格分隔
        inline = seg[k:k + 1] == ","
        if inline:
            ins = ' encoding="utf-8", errors="replace",'
        else:
            ins = '\n' + indent + 'encoding="utf-8",' + '\n' + indent + 'errors="replace",'
        new_seg = seg[:k] + ins + seg[k:]
        out.append(t[last:s]); out.append(new_seg); last = e; n += 1
    if n:
        path.write_text("".join(out), encoding="utf-8")
    return n


def add_block(path: Path, rel: str) -> bool:
    t = path.read_text(encoding="utf-8")
    if "# ── 来源 ──" in t:
        return False
    m = re.match(r'^"""(?:.|\n)*?"""\s*\n', t)
    pos = m.end() if m else 0
    path.write_text(t[:pos] + BLOCK % rel + t[pos:], encoding="utf-8")
    return True


def main() -> int:
    total = 0
    for rel in ("tests/test_cad_studio_cli.py",
                "apps/desktop/cad_workbench/queue_worker.py"):
        p = ROOT / rel
        if not p.is_file():
            print("  ⚠ 不在: %s" % rel); continue
        n = fix(p)                       # ⚠ **先改代码**
        b = add_block(p, rel)            # ⚠ **后写来源块**（事实 60）
        total += n
        print("  %-52s 修 %d 处  来源块 %s" % (rel, n, "已加" if b else "已存在"))
    print()
    print("  ⇒ 共修 **%d** 处" % total)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
