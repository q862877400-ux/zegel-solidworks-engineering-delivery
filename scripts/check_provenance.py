#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""来源可追溯性静态门禁（AGENTS.md 铁律 1 / 验收 A2）。

为什么需要这个工具
------------------
铁律 1 规定「只做缝合，不做发明 —— 每加一个能力，必须能指认它的出处」，
§四 4.3 进一步规定每个移植函数都要有来源头注释。但「要写注释」靠自觉必然衰减，
所以本工具把这条要求变成**可机械执行的门禁**：

对每一处相对上游 ``origin/main`` 的新增代码行，要求它出现在某个
``# ── 来源 ──`` 块的覆盖范围内（块内须含 仓库 / 文件 / 定位 / 官方签名依据
/ 许可 / 「未在本机实测」标注）。未被覆盖的新增行会被报成违规。

用法
----
::

    python scripts/check_provenance.py                 # 门禁模式，有违规则退出码 1
    python scripts/check_provenance.py --report        # 只打印报告，退出码恒 0
    python scripts/check_provenance.py --index         # 输出机器可读的来源索引 (JSON)

范围
----
只检查 ``.py`` 文件的**新增行**。文档（``.md``）与数据文件不强制来源块。

⚠ 本工具为静态文本比对，不导入任何 CAD 模块、不连接 SolidWorks、
  不执行任何 COM 调用（见 AGENTS.md 铁律 2）。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

#: 2026-10-03（接手轮）强制 stdout 为 UTF-8 —— 本门禁会 print 中文与箭头/勾这类符号，
#:   而 stdout 是管道时（测试正是用管道抓输出）默认按 locale（本机 GBK）编码
#:   ⇒ UnicodeEncodeError: 'gbk' codec can't encode character … ⇒ 门禁自己崩掉。
#:   known-facts 58 那一族（中文 Windows 上两侧默认编码不一致 —— 病灶在输出侧）；
#:   而测试那侧的 subprocess.run 已经带了 encoding='utf-8'。
sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[1]
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务的工具层，非第三方移植）
# 文件:   scripts/check_provenance.py —— 本文件自身
# 定位:   AGENTS.md 铁律 1「每加一个能力必须能指认出处」与 §四 4.3「来源头注释」
#         的可执行化。把注释要求从自觉变成对 origin/main 新增行的门禁。
#         判据设计（来源块四字段、覆盖范围延伸、豁免规则）全部来自
#         AGENTS.md §一 A2 与 §四 4.3 模板，本文件不含任何外部抄录文本。
# 许可:   本仓库 MIT。本文件为原创实现，无第三方代码引入。
# 覆盖:   全文件 —— 本模块是一个内聚的门禁实现，逐个私有函数贴来源块无意义。
# ⚠ 本工具为静态文本比对，未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）；
#   其自身行为已用正反两向用例核对（见 docs/signature-audit.md 复跑方式）。
# ────────────────────────────────────────────────────────────────────
ANCHOR = "origin/main"

#: Windows 控制台默认 GBK，强制 UTF-8 输出，否则中文报告全是乱码
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

#: 来源块起止标记（与 AGENTS.md §四 4.3 的模板一致）。
#: 允许前导空白 —— 来源块写在函数体内是合法且常见的（解释某一行为什么改），
#: 若强制第 0 列，这类块会被整体漏判，改过的代码行反而报成「无出处」。
BLOCK_OPEN = re.compile(r"^\s*#\s*─{2,}\s*来源\s*─")
BLOCK_CLOSE = re.compile(r"^\s*#\s*─{3,}\s*$")

#: 来源块内必须出现的字段，缺一即判该块不合规
REQUIRED_FIELDS = ("仓库", "文件", "定位", "未在本机实测")

#: 允许没有来源块的「非实质新增行」
ALLOWED_NO_SOURCE = re.compile(
    r"^\s*$"  # 空行
    r"|^\s*#"  # 纯注释（但块外的注释不算覆盖）
    r"|^\s*from\s+__future__\s+import"
    r"|^\s*(import|from)\s+"
    r"|^\s*(try|except|else|elif|finally)\b.*:"
    r"|^\s*\)+\s*$"  # 闭合括号
    r"|^\s*if\s+__name__\s*=="  # 标准入口惯用法
    r"|^\s*_[A-Za-z0-9_]+\(\)\s*$"  # 入口里调用本文件私有辅助（如 _enable_utf8_stdout）
    r"|^\s*raise\s+SystemExit\("
)

#: 显然由本文件内部产生的样板（fixture / recorder / 加载器），不要求外部来源
INTERNAL_FIXTURE = re.compile(
    r"^(class\s+_Recorder|class\s+_Doc|def\s+_load_|def\s+_main|"
    r"DETAIL_VIEW_AT4_PARAMS|INSERT_BOM_TABLE4_PARAMS|"
    r"REPO_ROOT|WORKFLOW_PATH|MODULE_PATH)"
)


def _def_ranges(text: str, predicate) -> set[int]:
    """命中 predicate 的顶层定义所占行号，**含其整个函数体**。

    内部循环从 i+1 起步：def 行本身单独计入，否则在
    ``def f():`` 这种单行签名上会立刻 break，函数体整段漏掉。
    """
    lines = text.splitlines()
    exempt: set[int] = set()
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped.startswith(("def ", "class ")) or not predicate(stripped):
            i += 1
            continue
        base = len(lines[i]) - len(lines[i].lstrip())
        exempt.add(i + 1)
        j = i + 1
        while j < len(lines):
            if not lines[j].strip():
                j += 1
                continue
            if (len(lines[j]) - len(lines[j].lstrip())) <= base:
                break
            exempt.add(j + 1)
            j += 1
        i = max(j, i + 1)
    return exempt


def _git(*args: str) -> str:
    """跑 git 并取 stdout。

    ``stdin=DEVNULL`` 是必须的：否则子进程继承父进程的 stdin，在 pwsh
    管道环境下 git 会一直等输入，表现为整个门禁挂死。
    ``timeout`` 兜底，避免个别仓库状态异常时无限等待。
    """
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdin=subprocess.DEVNULL,
        timeout=60,
    ).stdout


def _added_lines(path: str) -> dict[int, str]:
    """返回 {行号: 该行文本}，只含相对上游新增的行。"""
    diff = _git("diff", "--unified=0", ANCHOR, "--", path)
    added: dict[int, str] = {}
    new_no = 0
    for line in diff.splitlines():
        if line.startswith("@@"):
            match = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if match:
                new_no = int(match.group(1))
            continue
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            added[new_no] = line[1:]
            new_no += 1
        elif not line.startswith("-"):
            new_no += 1
    return added


def _module_docstring_lines(text: str) -> set[int]:
    """模块级 docstring 占的行号（散文，允许不含来源块）。

    必须先跳过 shebang / coding 声明等行首注释——它们合法地位于 docstring 之前，
    不跳过的话 lstrip().startswith('\"\"\"') 直接落空，散文行会被误报成违规。
    """
    lines = text.splitlines()
    first = 0
    while first < len(lines) and (
        not lines[first].strip() or lines[first].lstrip().startswith("#")
    ):
        first += 1
    if first >= len(lines):
        return set()
    head = lines[first].lstrip()
    # 允许字符串前缀 r / u / b / f 及其组合（r""" 最常见）
    if not re.match(
        r'''^[rubfRUBF]{0,2}("""|''' + r"'''" + r'''|"""|''' + r"'''" + r""")""", head
    ):
        return set()
    quote = (
        head[:3]
        if head[:3] in ('"""', "'''")
        else head[head.index('"') if '"' in head else head.index("'") :][:3]
    )
    end = first
    closed = lines[first].lstrip().count(quote) >= 2
    while not closed and end + 1 < len(lines):
        end += 1
        if quote in lines[end]:
            closed = True
    return set(range(first + 1, end + 2))


#: 来源块内出现该标记时，其覆盖范围延伸到文件末尾。
#: 用途：内聚型工具模块（本身即一个整体，如本门禁）只需在文件头声明一次，
#:       不必为每个私有函数贴重复的块。**必须显式写出**，不是默认放行。
WHOLE_FILE_MARK = re.compile(r"覆盖\s*[:：]\s*全文件|scope\s*[:：]\s*whole-file")

#: 来源块内出现该标记时，其覆盖范围延伸到**下一个来源块为止**的全部同级定义。
#: 用途：形如「下列 N 个薄封装逐一对应签名表」的成组声明——逐个贴块是噪声，
#:       但也不能因此默认放行，所以要求作者显式写出作用域。
GROUP_MARK = re.compile(
    r"覆盖\s*[:：]\s*后续同级定义|scope\s*[:：]\s*following-siblings"
)


def _extend_to_code(lines: list[str], block_end: int, whole_file: bool = False) -> int:
    """把来源块的有效覆盖范围延伸到它所描述的代码单元末尾。

    来源块是注释，真正被它「说明」的是紧随其后的定义单元：常量字典的闭合括号，
    或函数的整个函数体。判据用**括号深度 + 顶层定界符**，不用缩进
    （缩进对 `FOO = {` 这类顶层定义无效，会一路吃到文件尾）。

    截断条件：括号深度回到 0，且遇到顶层 ``def`` / ``class`` / ``@`` / 新来源块，
    并且它前面是空行（两个定义单元之间的自然间隔）。
    """
    if whole_file:
        return len(lines)
    i = block_end
    n = len(lines)
    while i < n and (not lines[i].strip() or lines[i].lstrip().startswith("#")):
        i += 1
    if i >= n:
        return block_end

    depth = 0
    base_indent = len(lines[i]) - len(lines[i].lstrip())
    last = i
    j = i
    while j < n:
        raw = lines[j]
        if raw.strip():
            stripped = raw.strip()
            opens = sum(stripped.count(c) for c in "([{")
            closes = sum(stripped.count(c) for c in ")]}")
            indent = len(raw) - len(raw.lstrip())
            # 截断只在**顶层**定义处发生：嵌套的 def（如 class 内的 validate、
            # 函数内的 _apply）属于本单元的一部分，不能当边界。
            if (
                depth <= 0
                and j > i
                and indent <= base_indent
                and (
                    stripped.startswith(("def ", "class ", "@"))
                    or BLOCK_OPEN.match(raw)
                )
                and not lines[j - 1].strip()
            ):
                break
            depth += opens - closes
            last = j
        j += 1
    return last + 1


def _source_blocks(text: str) -> list[tuple[int, int, dict[str, str]]]:
    """扫描来源块，返回 [(起始行, 有效结束行, 字段字典)]，行号为 1-based。"""
    blocks: list[tuple[int, int, dict[str, str]]] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if BLOCK_OPEN.match(lines[i]):
            start = i
            fields: dict[str, str] = {}
            whole_file = False
            group = False
            i += 1
            while i < len(lines) and not BLOCK_CLOSE.match(lines[i]):
                # 去掉行首装饰符号（⚠ ⛔ ★ ※ 等）再匹配字段名，
                # 否则 "⚠ 本函数…未在本机实测" 会被 startswith 漏判。
                body = re.sub(r"^[⚠⛔★※✓\s]+", "", lines[i].lstrip("# ")).strip()
                for key in REQUIRED_FIELDS:
                    if key in body:
                        fields.setdefault(key, body)
                if WHOLE_FILE_MARK.search(body):
                    whole_file = True
                if GROUP_MARK.search(body):
                    group = True
                i += 1
            if whole_file:
                end = len(lines) + 1
            elif group:
                # 延伸到下一个来源块的起始行（组内成员共用这一个块）
                nxt = len(lines) + 1
                for k in range(i, len(lines)):
                    if BLOCK_OPEN.match(lines[k]):
                        nxt = k
                        break
                end = nxt
            else:
                end = _extend_to_code(lines, i) + 1
            blocks.append((start + 1, end, fields))
        i += 1
    return blocks


def check_file(path: str, whole_file: bool = False) -> tuple[list[dict], list[dict]]:
    """返回 (违规列表, 合法来源块列表)。

    ``whole_file=True`` 用于**未跟踪的新增文件**：它相对上游是整文件新增，
    没有任何 diff 可比，故把每一行都当作待检查的新增行。
    """
    full = REPO_ROOT / path
    if not full.exists():
        return [], []
    text = full.read_text(encoding="utf-8", errors="replace")
    if whole_file:
        added = {i: line for i, line in enumerate(text.splitlines(), start=1)}
    else:
        added = _added_lines(path)
    blocks = _source_blocks(text)
    docstring_lines = _module_docstring_lines(text)
    has_valid_block = any(all(k in f for k in REQUIRED_FIELDS) for _, _, f in blocks)
    # 测试自产样板（fixture / 加载器 / _main）与测试函数：
    #   前者没有外部出处；后者只要文件里有合规来源块，其断言取值即由该块声明。
    internal = _def_ranges(text, lambda s: bool(INTERNAL_FIXTURE.match(s)))
    if has_valid_block:
        internal |= _def_ranges(text, lambda s: s.startswith("def test_"))
        # 测试文件里的私有辅助（桩、录制器、假对象工厂、main 入口）是本文件
        # 自产的测试装置，没有外部出处。仅在 tests/ 下豁免 —— 生产代码里的
        # 私有函数仍必须有来源块。
        if "/tests/" in f"/{path}":
            internal |= _def_ranges(text, lambda s: s.startswith(("def _", "class _")))

    incomplete = [
        {
            "path": path,
            "start": s,
            "end": e,
            "missing": [k for k in REQUIRED_FIELDS if k not in f],
        }
        for s, e, f in blocks
        if any(k not in f for k in REQUIRED_FIELDS)
    ]
    valid = [
        {"path": path, "start": s, "end": e, "fields": f}
        for s, e, f in blocks
        if all(k in f for k in REQUIRED_FIELDS)
    ]

    violations: list[dict] = []
    for lineno, content in added.items():
        if any(s <= lineno <= e for s, e, _ in blocks):
            continue  # 已被来源块覆盖
        if lineno in docstring_lines:
            continue  # 模块 docstring 是散文
        if lineno in internal:
            continue  # 测试自产样板 / test_ 函数
        if ALLOWED_NO_SOURCE.match(content):
            continue  # 非实质行
        if INTERNAL_FIXTURE.match(content.strip()):
            continue  # 样板定义行本身
        violations.append({"path": path, "line": lineno, "text": content.rstrip()})
    return violations, valid


def main() -> int:
    parser = argparse.ArgumentParser(description="来源可追溯性静态门禁")
    parser.add_argument("--report", action="store_true", help="只打印报告，退出码恒 0")
    parser.add_argument("--index", action="store_true", help="输出机器可读 JSON 索引")
    args = parser.parse_args()

    try:
        changed = _git("diff", "--name-only", ANCHOR).split()
        # ⛔ git diff 不列出**未跟踪**文件——而新增文件恰恰是最需要被门禁
        #   覆盖的那批。漏掉它们等于门禁对新代码失效。故显式并入未跟踪文件。
        untracked = _git("ls-files", "--others", "--exclude-standard").split()
    except subprocess.CalledProcessError:
        print(f"[FAIL] 无法读取 {ANCHOR}，请确认上游锚点已配置", file=sys.stderr)
        return 2

    # 去重并保持稳定顺序
    seen: set[str] = set()
    all_changed = [p for p in changed + untracked if not (p in seen or seen.add(p))]

    py_files = [p for p in all_changed if p.endswith(".py")]
    # 未跟踪文件相对上游是「整文件新增」，须把所有行都当作新增行来查
    untracked_set = set(untracked)
    all_violations: list[dict] = []
    all_blocks: list[dict] = []
    for path in py_files:
        v, b = check_file(path, whole_file=path in untracked_set)
        all_violations.extend(v)
        all_blocks.extend(b)

    if args.index:
        print(
            json.dumps(
                {
                    "anchor": ANCHOR,
                    "py_files": py_files,
                    "source_blocks": all_blocks,
                    "violations": all_violations,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print(
        f"来源门禁 · 锚点 {ANCHOR} · 受检 .py 文件 {len(py_files)} 个"
        f"（其中未跟踪 {len([p for p in py_files if p in untracked_set])} 个）"
    )
    print(f"合规来源块 {len(all_blocks)} 个")
    if all_violations:
        print(f"\n[FAIL] {len(all_violations)} 行新增代码没有可追溯的出处：\n")
        for item in all_violations:
            print(f"  {item['path']}:{item['line']}")
            print(f"      {item['text']}")
        # ⚑ 常见原因诊断（2026-10-01 加；本会话**五次**同族坑，两种面孔）
        print("\n        ↑ 两个最常见原因（机器可查，不必再猜）：")
        print("          ① 常量/导入夹在来源块与目标 def 之间 ⇒ 延伸止于常量")
        print("             ⇒ 把常量挪到**来源块之前**；")
        print("          ② 一个来源块后面有多个 def/常量 ⇒ 默认只覆盖第一个")
        print(
            "             ⇒ 在该块里加**裸的** `# 覆盖: 后续同级定义`（或 `# 覆盖: 全文件`）。"
        )
        print("             ⚠ 那行**不要**加 markdown 粗体 —— 正则匹配不到 `**`。")
        print("        逐行核对就用本命令的输出（它已列出未覆盖的具体行）。")
        print("\n修法：在该段代码上方加 AGENTS.md §四 4.3 规定的来源块，")
        print("      必须含 仓库 / 文件 / 定位 / 未在本机实测 四个字段。")
        return 0 if args.report else 1

    print("[PASS] 全部新增代码行均可追溯到来源")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
