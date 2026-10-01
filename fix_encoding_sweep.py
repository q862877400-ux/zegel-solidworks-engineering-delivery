"""给 11 处 `subprocess.run(..., text=True)` 补 `encoding="utf-8"`，并加来源块。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**上游文件的缺陷修复**）+ Python 标准库文档（`subprocess`）
# 文件:   tests/test_cad_studio_cli.py · tests/test_dfm_review.py
#         tests/test_cnc_fillet_chamfer_subskill.py
#         scripts/fea_analysis.py · scripts/capture_simulation_evidence.py
#         scripts/capture_topology_evidence.py
# 定位:   轮 45 查明 4 个**真实基线失败**同源：
#         `subprocess.run(..., capture_output=True, text=True)` **没给 `encoding=`**
#         ⇒ 用 `locale.getpreferredencoding()`，本机是 **GBK**
#         ⇒ 子进程输出的 **UTF-8 中文** 解不了（`UnicodeDecodeError: 'gbk' codec …`）
#         ⇒ `completed.stdout` 变 **None** ⇒ `json.loads(None)` 抛 TypeError。
#         **⇒ 修法：补 `encoding="utf-8", errors="replace"`**（与子进程实际输出一致；
#            `errors="replace"` 保证**再遇到别的编码也不会让整条测试崩掉**）。
#         ⚠ **第一次扫描报了 23 处，是**假阳性**** —— 我按「第一个 `)`」截断调用段，
#           把本来就有 `encoding=` 的多行调用误判了。**⇒ 改用**括号配对**切分 ⇒ 真值 11 处。**
# 许可:   本仓库 MIT。无第三方代码引入。
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

#: 每个文件的来源块（插在**模块 docstring 之后**）
BLOCKS = {
    "tests/test_cad_studio_cli.py":
        "# ── 来源 ──\n"
        "# 仓库:   本项目自身（**上游文件的缺陷修复**，非第三方移植）+ Python 标准库 `subprocess` 文档\n"
        "# 文件:   tests/test_cad_studio_cli.py\n"
        "# 定位:   ⚠ 本文件的 `subprocess.run(..., text=True)` **没给 `encoding=`** ⇒ 用\n"
        "#         `locale.getpreferredencoding()`（本机 **GBK**）⇒ 子进程的 **UTF-8 中文**输出\n"
        "#         解不了（`UnicodeDecodeError`）⇒ `stdout` 变 **None** ⇒ `json.loads(None)` 崩。\n"
        "#         **这是 4 个真实基线失败的共同根因**（轮 45 查明）。\n"
        "#         **⇒ 已补 `encoding=\"utf-8\", errors=\"replace\"`**（与子进程实际输出一致）。\n"
        "# 许可:   本仓库 MIT。无第三方代码引入。\n"
        "# 覆盖:   全文件\n"
        "# ─────────────────────────────────────────────────────────────────────────\n",
    "tests/test_dfm_review.py":
        "# ── 来源 ──\n"
        "# 仓库:   本项目自身（**上游文件的缺陷修复**）+ Python 标准库 `subprocess` 文档\n"
        "# 文件:   tests/test_dfm_review.py\n"
        "# 定位:   同 `test_cad_studio_cli.py`：`subprocess.run(..., text=True)` 缺 `encoding=`\n"
        "#         ⇒ Windows 中文环境下用 GBK 解子进程的 UTF-8 输出 ⇒ `stdout=None` ⇒ 崩。\n"
        "#         **⇒ 已补 `encoding=\"utf-8\", errors=\"replace\"`**（轮 45）。\n"
        "# 许可:   本仓库 MIT。无第三方代码引入。\n"
        "# 覆盖:   全文件\n"
        "# ─────────────────────────────────────────────────────────────────────────\n",
    "tests/test_cnc_fillet_chamfer_subskill.py":
        "# ── 来源 ──\n"
        "# 仓库:   本项目自身（**上游文件的缺陷修复**）+ Python 标准库 `subprocess` 文档\n"
        "# 文件:   tests/test_cnc_fillet_chamfer_subskill.py\n"
        "# 定位:   同一族缺陷：`subprocess.run(..., text=True)` 缺 `encoding=` ⇒ 中文环境用 GBK\n"
        "#         解 UTF-8 输出。**⇒ 已补 `encoding=\"utf-8\", errors=\"replace\"`**（轮 45）。\n"
        "# 许可:   本仓库 MIT。无第三方代码引入。\n"
        "# 覆盖:   全文件\n"
        "# ─────────────────────────────────────────────────────────────────────────\n",
    "scripts/fea_analysis.py":
        "# ── 来源 ──\n"
        "# 仓库:   本项目自身（**上游文件的缺陷修复**）+ Python 标准库 `subprocess` 文档\n"
        "# 文件:   scripts/fea_analysis.py\n"
        "# 定位:   同一族缺陷：`subprocess.run(..., text=True)` 缺 `encoding=` ⇒ 中文环境用 GBK\n"
        "#         解求解器（CalculiX/Elmer）的 UTF-8 输出。**⇒ 已补\n"
        "#         `encoding=\"utf-8\", errors=\"replace\"`**（轮 45）。\n"
        "# 许可:   本仓库 MIT。无第三方代码引入。\n"
        "# 覆盖:   全文件\n"
        "# ─────────────────────────────────────────────────────────────────────────\n",
    "scripts/capture_simulation_evidence.py":
        "# ── 来源 ──\n"
        "# 仓库:   本项目自身（**上游文件的缺陷修复**）+ Python 标准库 `subprocess` 文档\n"
        "# 文件:   scripts/capture_simulation_evidence.py\n"
        "# 定位:   同一族缺陷（轮 45）：`subprocess.run(..., text=True)` 缺 `encoding=`。\n"
        "#         **⇒ 已补 `encoding=\"utf-8\", errors=\"replace\"`**。\n"
        "# 许可:   本仓库 MIT。无第三方代码引入。\n"
        "# 覆盖:   全文件\n"
        "# ─────────────────────────────────────────────────────────────────────────\n",
    "scripts/capture_topology_evidence.py":
        "# ── 来源 ──\n"
        "# 仓库:   本项目自身（**上游文件的缺陷修复**）+ Python 标准库 `subprocess` 文档\n"
        "# 文件:   scripts/capture_topology_evidence.py\n"
        "# 定位:   同一族缺陷（轮 45）：`subprocess.run(..., text=True)` 缺 `encoding=`。\n"
        "#         **⇒ 已补 `encoding=\"utf-8\", errors=\"replace\"`**。\n"
        "# 许可:   本仓库 MIT。无第三方代码引入。\n"
        "# 覆盖:   全文件\n"
        "# ─────────────────────────────────────────────────────────────────────────\n",
}


def call_seg(t: str, start: int) -> tuple:
    """按**括号配对**取 `subprocess.*(` 的整段 ⇒ ``(段文本, 起, 止)``。"""
    i = t.find("(", start)
    if i < 0:
        return "", -1, -1
    depth, j = 0, i
    while j < len(t):
        if t[j] == "(":
            depth += 1
        elif t[j] == ")":
            depth -= 1
            if depth == 0:
                return t[i:j + 1], i, j + 1
        j += 1
    return t[i:], i, len(t)


def fix_encoding(path: Path) -> int:
    """给该文件里**缺 `encoding=`** 的 `text=True` 调用补上 ⇒ 改了几处。"""
    t = path.read_text(encoding="utf-8")
    out, last, n = [], 0, 0
    for m in re.finditer(r"subprocess\.(run|Popen|check_output|check_call)\s*\(", t):
        seg, s, e = call_seg(t, m.start())
        if s < last or "text=True" not in seg or "encoding=" in seg:
            continue
        # 找到 `text=True` 那一行，按**它的缩进**插入两行
        tm = re.search(r"^([ \t]*)text=True,\s*$", seg, re.M)
        if not tm:
            continue
        indent = tm.group(1)
        new_seg = (seg[:tm.end()]
                   + "\n" + indent + 'encoding="utf-8",'
                   + "\n" + indent + 'errors="replace",'
                   + seg[tm.end():])
        out.append(t[last:s])
        out.append(new_seg)
        last = e
        n += 1
    out.append(t[last:])
    if n:
        path.write_text("".join(out), encoding="utf-8")
    return n


def add_block(path: Path, block: str) -> bool:
    """把来源块插在**模块 docstring 之后**（已有 `# ── 来源 ──` 就跳过）。"""
    t = path.read_text(encoding="utf-8")
    if "# ── 来源 ──" in t:
        return False
    m = re.match(r'^"""(?:.|\n)*?"""\s*\n', t)
    pos = m.end() if m else 0
    path.write_text(t[:pos] + block + t[pos:], encoding="utf-8")
    return True


def main() -> int:
    total_fix = total_block = 0
    for rel, block in BLOCKS.items():
        p = ROOT / rel
        if not p.is_file():
            print("  ⚠ 不在: %s" % rel)
            continue
        n = fix_encoding(p)
        b = add_block(p, block)
        total_fix += n
        total_block += 1 if b else 0
        print("  %-48s 修 %d 处  来源块 %s" % (rel, n, "已加" if b else "已存在"))
    print()
    print("  ⇒ 共修 **%d** 处；加来源块 **%d** 个" % (total_fix, total_block))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
