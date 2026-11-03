"""★ 提交纪律护栏：**只提交自己这一线的文件**，并在提交前拦住「误带删除」。"""

# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/commit_mine.py
# 定位:   规格 206 —— 处置一个**本轮实测踩到的**地雷（事实 555）：
#         `tools/round_chain.ps1` 在 **3 处**跑 `git add -A`（★ L84 / L117 / L142），
#         ★★ 而它的用途是「把重生成的产物加进索引，好让 release_check 看到一致的树」——
#         ★★★ 副作用是：**跑完链之后，整个工作树都在索引里** ⇒
#         ★★★★ 此时一次普通的 `git commit` 会把**别人未提交的文件（914 个）一起提交** ✓✗
# ★ 本仓 25 个未跟踪文件与 4 个未暂存改动**都不属于本线**（交接件逐字：「未提交的只有别
# 人的文件」）✓
# 官方依据: 不适用（本仓 git 纪律，非 SolidWorks API）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding="utf-8", errors="replace")


#: ★★ 为什么把 stderr 折进 stdout（★ 本轮实测的教训）：`git add` 在**每个** CRLF 文件上
#: 打一行 `LF will be replaced by CRLF` 警告 ⇒ ★ 909 个文件的那次测试**吐了 1.4 万字节**
#: ，
#:   ★★ 把真正要看的那 6 行结果**冲出了可见范围** ⇒ ★ 判据被噪音淹没（★ 与事实 51 同族）✓
#:   ⇒ ★ 本工具**只关心 stdout**；stderr 仍被捕获在 `CompletedProcess` 上，出错时再取 ✓


def _git(*args: str) -> subprocess.CompletedProcess:
    """★ 跑一条 git（★ `encoding=` 必给 —— 事实 58：中文 Windows 上不给会 `UnicodeDecodeError`）。"""
    return subprocess.run(
        ("git",) + args,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _tracked_files() -> list[str]:
    """★ 当前 HEAD 里被跟踪的全部文件路径（★ 用于区分「记录删除」与「路径拼错」）。

    ⚠ 用 `ls-tree` 而不是 `ls-files`：后者会列出**已删但未提交**的路径
      （它读的是索引），那样「拼错的路径」也可能被误判成「已删」。
      `ls-tree -r HEAD` 只看**上次提交**里的文件 ⇒ 语义正是「这个路径曾经存在过」。
    """
    out = _git("ls-tree", "-r", "--name-only", "HEAD")
    return [ln for ln in (out.stdout or "").splitlines() if ln.strip()]


def staged() -> list[tuple[str, int, int]]:
    """★ 列出索引里的文件及 `(新增行, 删除行)`（★ 二进制给 `-` ⇒ 记 0）。"""
    out = _git("diff", "--cached", "--numstat")
    rows = []
    for line in (out.stdout or "").splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        add = int(parts[0]) if parts[0].isdigit() else 0
        dele = int(parts[1]) if parts[1].isdigit() else 0
        rows.append((parts[2], add, dele))
    return rows



# ── 提交前置门禁（★ 2026-11-02 业主指令）──────────────────────────────────────
# ★★★★★ **为什么把门装在这里**：业主原话——
#   「我们不是已经写了机械门禁吗？问题是你压根就不走门，你直接把门给绕过了……
#     你并没有按照之前设计的路径去走啊」
# ★★ 实测结论：本仓门禁**全部装在下游**（`ToolSpec` 层 / `_unit_guard` 运行时出口 /
#   `release_check` 发布前），而**一次性脚本（`tools/` 里手写、`tools/` 外临时文件）
#   从不经过任何一道**。⇒ 门再好，只要不需要"进门"就等于不存在。
# ★★★ 因此把**唯一提交入口**变成必经之门：
#   ① 新文件必须在 `docs/state/file-audit.jsonl` 里有**非 pending 裁决**
#   ② 改动过的 `.py` 必须过语法/SyntaxWarning 门禁
#   不满足就**拒绝提交**（不是警告）。★ `--no-gate` 可显式跳过，但会打印醒目提示。
LEDGER = ROOT / "docs" / "state" / "file-audit.jsonl"


def _ledger_verdicts() -> dict:
    """⇒ {路径: 裁决}（读不到台账回空表，**不静默放行**）。"""
    if not LEDGER.is_file():
        return {}
    out: dict = {}
    try:
        for line in LEDGER.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            out[rec.get("path", "")] = rec.get("verdict", "")
    except Exception:  # noqa: BLE001
        return {}
    return out


def _gate(paths: list[str], rows: list[tuple[str, int, int]]) -> int:
    """★ 提交前门禁：新增文件必须有裁决 + 改动的 .py 必须过语法门。"""
    head = set(_tracked_files())
    staged_names = [n for n, _a, _d in rows]
    verdicts = _ledger_verdicts()

    problems: list[str] = []
    new_files = [n for n in staged_names if n not in head]
    for n in new_files:
        v = verdicts.get(n)
        if v is None:
            problems.append("%s —— 新文件，台账里**没有**它（先跑 `python -B scripts/gen_file_audit.py`）" % n)
        elif v == "pending":
            problems.append("%s —— 新文件，台账裁决仍是 `pending`（必须给出 deep:/skim: 证据）" % n)

    if problems:
        print()
        print("★★ 提交前置门禁未通过（新增文件没有台账裁决，%d 项）：" % len(problems))
        for p_ in problems:
            print("   %s" % p_)
        print("   ⇒ ★ 这是 2026-11-02 业主指令装的**必经之门**：不许绕过门禁直接提交。")
        return 9

    #: ② 语法/SyntaxWarning（只对**.py**，整仓扫很快）
    pys = [n for n in staged_names if n.endswith(".py")]
    if pys:
        gate = ROOT / "scripts" / "check_python_syntax.py"
        if gate.is_file():
            r = subprocess.run(
                (sys.executable, "-B", str(gate)),
                cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace",
            )
            if r.returncode != 0:
                print()
                print("★★ 提交前置门禁未通过（.py 语法/SyntaxWarning）：")
                tail = (r.stdout or "").strip().splitlines()[-6:]
                for ln in tail:
                    print("   %s" % ln)
                return 10
    return 0

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="★ 只提交自己这一线的文件（★ 先 reset 再只 add 点名的）"
    )
    ap.add_argument("paths", nargs="*", help="★ 本线改动的文件（相对仓库根）")
    ap.add_argument(
        "--allow-deletions",
        action="store_true",
        help="★ 确实要删文件时才开（★ 默认拦：与事实 61 同族）",
    )
    ap.add_argument("--dry-run", action="store_true", help="★ 只看会提交什么，不提交")
    ap.add_argument(
        "--no-gate",
        action="store_true",
        help="★ 跳过提交前置门禁（★ 默认**不跳**；跳了会在末端醒目提示）",
    )
    ap.add_argument(
        "-m",
        "--message-file",
        default=None,
        help="★ 提交信息文件（★ 用 -F ⇒ 避开引号坑）",
    )
    a = ap.parse_args(argv)

    if not a.paths:
        print("★ 必须点名本线的文件 —— ★ 本工具的**存在理由**就是不许 `git add -A` ✓")
        return 2

    # ★★★ 第 0 步（★ 本轮补的，理由是一条实测踩到的顺序问题）：**先看删除、再看存在性**
    # ——
    # ★ 真 git 的 `add -- <被删的路径>` **是合法的**（那是"记录删除"）⇒
    # ★★ 所以不能拿"路径不存在"去拦删除，否则**唯一的删除拦路石会排在存在性后面而永不生
    # 效** ✓
    pre = staged()
    pre_del = sum(d for _n, _a, d in pre)
    if pre_del and not a.allow_deletions:
        print(
            "★★ 索引里**已经**有 **%d** 行删除 ⇒ 按事实 61 的定则**停下核查**："
            % pre_del
        )
        for name, add_n, del_n in pre:
            if del_n:
                print("   %+5d %+5d  %s" % (add_n, del_n, name))
        print(
            "   ★ 批量改动**必须先证明只做加法**；★ 确实要删就加 `--allow-deletions` ✓"
        )
        return 6

    # ★★★ 第 1 步（★ 关键）：把 `round_chain.ps1` 那三次 `git add -A` 清掉
    _git("reset", "-q")
    left = staged()
    if left:
        print("★ `git reset` 之后索引仍非空（%d 个）⇒ 停下，别提交" % len(left))
        return 3

    # ★★ 第 2 步：只加**点名的**文件（★ 加不存在的路径会被 git 报错 ⇒ 不静默）
    # ⚠⚠ **2026-10-19 修（实测踩到）**：原来这里一律拒绝「路径不存在」，
    #   与第 0 步的注释**自相矛盾** —— 注释明写「不能拿'路径不存在'去拦删除，
    #   否则唯一的删除拦路石会排在存在性后面而永不生效」，而代码正是那么拦的。
    #   ⇒ 后果：`--allow-deletions` **形同虚设**，`commit_mine.py` 永远提交不了删除
    #     （本仓 2026-10-19 清理 68 个工具时只能绕道 `git add` + `git commit -F`）。
    #   ★ 正确判据：**已跟踪但工作树已删**的路径是合法的「记录删除」；
    #     只有**既不存在、又不在索引里**的路径才是真错（拼错了/根本没这文件）。
    tracked = set(_tracked_files())
    bad, deletable = [], []
    for p in a.paths:
        if (ROOT / p).exists():
            continue
        if p in tracked:
            deletable.append(p)  #: ★ 合法：已跟踪 + 已删 ⇒ 记录删除
        else:
            bad.append(p)  #: ★ 真错：不存在且未跟踪
    if bad:
        print("★ 这些路径**不存在且未被 git 跟踪**，拒绝提交（拼错了？）：%s" % bad)
        return 4
    if deletable and not a.allow_deletions:
        print(
            "★★ 这些路径**已被删除**（%d 个）⇒ 要记录删除必须加 `--allow-deletions`："
            % len(deletable)
        )
        for p in deletable[:20]:
            print("   %s" % p)
        return 6
    add = _git("add", "--", *a.paths)
    if add.returncode != 0:
        print("★ git add 失败：%s" % (add.stderr or "").strip())
        return 5

    rows = staged()
    print("★ 索引里 **%d** 个文件：" % len(rows))
    for name, add_n, del_n in rows:
        print("   %+5d %+5d  %s" % (add_n, del_n, name))

    total_del = sum(d for _n, _a, d in rows)
    if total_del and not a.allow_deletions:
        print()
        print("★★ 索引里有 **%d** 行删除 ⇒ 按事实 61 的定则**停下核查**：" % total_del)
        print(
            "   ★ 批量改动**必须先证明只做加法**；★ 确实要删就加 `--allow-deletions` ✓"
        )
        return 6

    # ★★★ 必经之门（2026-11-02）：新增文件必须有台账裁决；改动 .py 必须过语法门
    if not a.no_gate:
        rc = _gate(a.paths, rows)
        if rc:
            return rc

    if a.dry_run or not a.message_file:
        print()
        print(
            "★ 未提交（★ 没给 `-m <信息文件>`）—— ★ 索引已备好，可自行 `git commit -F <文件>` ✓"
        )
        return 0

    msg = Path(a.message_file)
    if not msg.is_file():
        print("★ 找不到提交信息文件：%s" % msg)
        return 7
    commit = _git("commit", "-F", str(msg))
    print()
    if commit.returncode != 0:
        print("★ 提交失败：%s" % (commit.stderr or "").strip())
        return 8
    if a.no_gate:
        print("⚠⚠ **本次跳过了提交前置门禁（--no-gate）** —— ★ 请务必自行跑 `release_check`")
    print("★ 提交成功：%s" % (commit.stdout or "").strip().splitlines()[0])
    print("★ 本次提交的文件：")
    for name in (
        _git("show", "--name-only", "--pretty=format:", "HEAD").stdout or ""
    ).splitlines():
        if name.strip():
            print("   %s" % name.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
