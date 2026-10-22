"""★ 门禁：`docs/*.md` 里的量化断言必须能追溯到出处。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   scripts/check_fact_provenance.py
# 定位:   `docs/text-to-cad-lessons-verdict.md` §2.3 的落地 ——★ 经验①「事实/尺寸来源分
#           级」的**改造后采纳**形态。★ 判据：`docs/*.md` 里形如「N 条 / N 个 / N% / N
#           秒 / N MB」的  量化断言，若来自实测，**同一行或同一段落**内必须能找到可追溯
#           的  出处（命令 / 脚本路径 / 日志路径 / `git show` 引用 / 上游路径:行号）。
# 官方依据: `docs/text-to-cad-lessons-verdict.md` §1.3（增量豁免范式）+ `docs/known-fact
#           s.md` 事实 62（负例测试是门禁有效的唯一证明）
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   `docs/*.md` 的**增量行**（相对 `origin/main` 的 diff）
# ⚠ 存量不查：★ 依据 §1.3 的既有范式（同 `scripts/check_provenance.py`）——
#   只对**新增行**收税，老文档天然在基线内，不做一次性清洗。
# ⚠ 等级 `stitched`（未真机跑过整条链）：★ 但本门禁**自带负例自证**
#   （★ 见 `selftest()`）—— 它造一条无出处的量化断言，★ 必须报出来。
# -----------------------------------------------------------------------------
from __future__ import annotations

import re
import subprocess
import sys
import pathlib

sys.stdout.reconfigure(encoding="utf-8")  # 事实 58：管道下 GBK 会崩
ROOT = pathlib.Path(__file__).resolve().parents[1]

#: ★ 相对上游的基线。★ 与 `scripts/check_provenance.py:59` 同一锚点。
ANCHOR = "origin/main"

#: ★ 量化断言的形态：数字 + 量词/单位。
#: ★ 只认**可能来自实测**的量词 —— 「个 / 条 / 处 / 次 / 行 / 秒 / MB / GB / %」。
#: ⚠ 故意**不认**「第 N 条 / 第 N 行」这类**序号**（那是引用不是断言），
#:   也不认纯数字（如 `0.7.22`、`2.0`）—— 那会淹没真断言（事实 53 的教训）。
QUANT = re.compile(
    r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)\s*"
    r"(条|个|处|次|行|秒|毫秒|MB|GB|KB|%|倍|档|级)"
)

#: ★ 可追溯出处的形态（任一命中即认为该断言有出处）。
#: ⚠ 每条都对应一种**可复核**的指向，不是「看起来像引用」：
TRACE = [
    re.compile(
        r"`[^`]*\.(?:py|json|md|txt|log|yaml|yml|ps1|sh)(?::\d+(?:-\d+)?)?`"
    ),  # 路径[:行]
    re.compile(r"`[^`]*(?:--|pytest |python |git |pwsh |Get-|Select-)[^`]*`"),  # 命令
    re.compile(r"\[[^\]]+\]\([^)]+\)"),  # md 链接
    re.compile(r"git show [0-9a-f]{4,}"),  # git show 引用
    re.compile(r"(?:实测|核验|测得|跑过|依据|出处|来源)\s*[:：]"),  # 显式声明
    #: ★ 事实台账引用。★ 两个方向都要认 —— 「事实 62」与「第 62 条事实」都是引用，
    #:   而后者在 `docs/` 里更常见。⚠ 只认一个方向会漏报（★ 负例测试抓到的真实缺陷）。
    re.compile(r"事实\s*\d+"),
    re.compile(r"第\s*\d+\s*条事实"),
    re.compile(r"[A-Za-z0-9_./-]+\.(?:py|md|json|txt|log):\d+"),  # 裸路径:行号
    #: ★ 引文标记：数字是**引用别人的原文**，不是本文件的断言 ⇒ 不需要本文件的出处。
    #:   ★ 出现场景：`docs/tools-removed-*.md` 的归档表（描述列是已删文件的原始首句）。
    #:   ⚠ 必须与「实测/依据」并列，因为引文的责任方是**被引的那份原文**，不是这里。
    re.compile(r"(?:原文引述|逐字引用|原文照抄|转述自)"),
]


def _git(*args: str) -> str:
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return out.stdout if out.returncode == 0 else ""
    except OSError:
        return ""


def _added_lines(path: pathlib.Path) -> dict[int, str]:
    """★ 相对 `ANCHOR` 的新增行 {行号: 文本}。★ 未跟踪文件 ⇒ 整文件算新增。"""
    rel = path.relative_to(ROOT).as_posix()
    if not _git("ls-files", "--error-unmatch", rel):
        #: ★ 未跟踪：整文件都是新增（★ 同 check_provenance.py:294-302 的处理）
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return {}
        return {i: ln for i, ln in enumerate(text.splitlines(), start=1)}
    diff = _git("diff", "--unified=0", ANCHOR, "--", rel)
    added: dict[int, str] = {}
    new_no = 0
    for line in diff.splitlines():
        if line.startswith("@@"):
            m = re.search(r"\+(\d+)", line)
            new_no = int(m.group(1)) if m else 0
        elif line.startswith("+") and not line.startswith("+++"):
            added[new_no] = line[1:]
            new_no += 1
    return added


def _line_has_trace(line: str) -> bool:
    return any(p.search(line) for p in TRACE)


def _para_has_trace(lines: list[str], idx: int, span: int = 3) -> bool:
    """★ 同段落（±span 行，遇空行止）内是否任一行带出处。"""
    lo = max(0, idx - span)
    hi = min(len(lines), idx + span + 1)
    for j in range(lo, hi):
        if not lines[j].strip():
            continue
        if _line_has_trace(lines[j]):
            return True
    return False


def scan_text(text: str, *, allow_para: bool = True) -> list[tuple[int, str, str]]:
    """★ 扫一段文本，返回 [(行号, 违规片段, 原因)]。★ 供 check() 与 selftest() 共用。"""
    lines = text.splitlines()
    problems: list[tuple[int, str, str]] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        #: ★ 跳过结构性行：标题 / 表格分隔 / 代码围栏 / 纯引用块
        if not stripped or stripped.startswith(("#", "```", "|---", "| :", "> ")):
            continue
        for m in QUANT.finditer(line):
            snippet = m.group(0)
            if _line_has_trace(line):
                continue
            if allow_para and _para_has_trace(lines, i):
                continue
            problems.append((i + 1, snippet, "量化断言没有可追溯出处"))
            break  # 一行报一次，避免噪声
    return problems


def check() -> list[str]:
    """★ 返回问题列表（空 = 过）。★ 只查 `docs/*.md` 的增量行。"""
    problems: list[str] = []
    docs = ROOT / "docs"
    if not docs.is_dir():
        return ["★ 没有 docs/ 目录"]
    for path in sorted(docs.glob("*.md")):
        added = _added_lines(path)
        if not added:
            continue
        #: ★ 增量行按行号还原成一段连续文本再扫 —— 保证「同段落」判据可用
        max_no = max(added)
        text = "\n".join(added.get(n, "") for n in range(1, max_no + 1))
        for lineno, snippet, why in scan_text(text):
            problems.append("%s:%d  %r —— %s" % (path.name, lineno, snippet, why))
    return problems


def selftest() -> bool:
    """★★ **负例自证**（★ 事实 62：门禁「写了」不等于「有效」）。

    ★ 判据两条，缺一不可：
      ① **无出处**的量化断言 ⇒ 必须被报出来（否则门禁是恒绿的摆设）；
      ② **有出处**的量化断言 ⇒ 必须**不**被报（否则门禁是恒红的噪声源）。
    ⚠ 第②条同样是自证的一部分：★ 一个「什么都报」的门禁与「什么都不报」
      同样无用（事实 53 同族）。
    """
    #: ① 负例：无任何出处的量化断言
    bad = "本次共发现 37 条能力没有实现，耗时 12 秒。"
    got = scan_text(bad)
    if not got:
        print("★★ 负例自证失败：无出处的量化断言**没有**被报出来")
        return False
    #: ② 正例：同一句话 + 出处 ⇒ 必须不报
    good = "本次共发现 37 条能力没有实现（实测：`python scripts/check_x.py`）。"
    if scan_text(good):
        print("★★ 正例自证失败：带出处的量化断言被误报 %r" % (scan_text(good),))
        return False
    #: ③ 正例：段落级出处也算（出处在上/下一行）
    good_para = (
        "核验命令如下：\n`python scripts/release_check.py`\n结果：37 条能力没有实现。"
    )
    if scan_text(good_para):
        print("★★ 正例自证失败：段落级出处未被接受")
        return False
    return True


def main() -> int:
    if not selftest():
        return 1
    print("★ 负例自证：过（无出处的断言抓得到，带出处的不误报）")
    problems = check()
    if problems:
        print("★★ 发现 %d 处量化断言没有出处：" % len(problems))
        for p in problems[:20]:
            print("   %s" % p)
        print(
            "\n★ 修法：给该断言补出处（命令 / 脚本路径:行号 / 日志路径 / `git show` 引用），"
            "或改写为非量化表述。"
        )
        return 1
    print("★ [PASS] docs/ 增量里的量化断言都能追溯到出处")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
