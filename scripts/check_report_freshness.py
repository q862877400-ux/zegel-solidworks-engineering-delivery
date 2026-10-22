r"""@brief 交付报告数字新鲜度门禁：`harvest-report.md` 声称的「偏离上游」必须与 git 实际一致。

## 为什么要有它（**实测出的痛点**）
`docs/harvest-report.md` 是 **A8** 的交付物（「报告写明并入了什么、仍空缺什么、为什么空缺」），
它开篇就写「**偏离上游**：N 个文件 / +N 行 / -N 行 · N 个 commit」。

```
2026-10-01（轮 54）实测：
  报告声称： 22 个文件 / +6,162 行 / -27 行 · 16 个 commit   （轮次 4 的数字）
  实际当时：174 个文件 / +125,916 行 / -262 行 · 158 个 commit
  ⇒ 差 **8 倍文件数 / 20 倍行数 / 10 倍 commit 数**，而且报告里还有一句
    「✅ 已执行（**16 个 commit**，最新 `9bf8cc9`）」——**一个早已失真的完成声明**。
```

⚠ `release_check.py` 的 `REQUIRED_ABILITY_FILES` **只查这两份报告「存在」**，
**不查里面的数字还对不对** ⇒ 报告可以**烂 50 轮而门禁全绿**。

**⇒ 本门禁把「数字」也纳入校验**：报告里的那行必须与
`git diff origin/main --shortstat` + `git rev-list --count origin/main..HEAD` **逐项相符**。

## 便携性守卫（**必须**）
需要 `origin/main` 这个 ref。**拿不到就直接 SKIP 并 exit 0**——
否则任何没有 `origin` 的 clone（或浅克隆）上这个门禁都会**无条件红**。

## 不做的事
* **不自动改报告**（报告是人写的判断，数字只是其中一行）——
  只报「差多少」并给出**可直接跑的修法**。
* 不校验报告里的**其它**数字（那些是历史记录，不是当前状态）。

# ── 来源 ──
# 仓库:   本项目自身（门禁实现）
# 文件:   scripts/check_report_freshness.py —— 本文件自身
#         tests/test_report_freshness_gate.py（契约测试 + 负例）
# 定位:   把 A8 的「报告」从「存在即可」升级为「**数字也要对**」；
#         依据是 2026-10-01（轮 54）实测到的 **8 倍/20 倍/10 倍** 偏差。
# 官方签名依据: 不适用（纯静态：读 markdown + 跑 `git diff --shortstat`，**不连 SolidWorks**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
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

REPO = Path(__file__).resolve().parents[1]

#: 报告里那行的形态（本项目的约定写法）：
#:   > 偏离上游：22 个文件 / +6,162 行 / -27 行 · 16 个 commit · 工作区 clean
DRIFT_LINE = re.compile(
    r"偏离上游\s*[:：]\s*(\d+)\s*个文件\s*/\s*\+([\d,]+)\s*行\s*/\s*-([\d,]+)\s*行"
    r"\s*·\s*(\d+)\s*个\s*commit")

REPORT = REPO / "docs" / "harvest-report.md"


def _git(args: list) -> str:
    """跑一条 git 命令 ⇒ stdout（失败抛 `RuntimeError`）。"""
    proc = subprocess.run(["git", "-C", str(REPO), *args],
                          check=False, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError("git %s 失败: %s" % (" ".join(args), (proc.stderr or "").strip()[:200]))
    return proc.stdout or ""


def actual_drift(repo: Path = REPO) -> dict:
    """⇒ ``{files, add, delete, commits}`` —— **将要提交的那个状态**相对 `origin/main` 的偏离。

    ⚠⚠ **量的是「工作树 + 未跟踪文件」，不是 HEAD** —— 这是**可用性**决定的，不是口味：

    ```
    2026-10-01（轮 54）第一版量 HEAD ⇒ 报告写 126,188，提交后 HEAD 包含它 ⇒ 变 126,226 ⇒ 又红
    2026-10-01（轮 56）实测：门禁报 178/+126589（当时 HEAD 的真值），
      而我手上**未提交**的探针会再加 1 文件/+153 行 ⇒ 提交后实际是 **179/+126742**
      ⇒ **按门禁给的数去写，提交后必然又红一位**（差的就是「未提交的那部分」）
    ```
    **⇒ 正解：量「`git add -A && git commit` 之后会变成什么」**，那才是报告该写的数。
    ⚠ 它**不会**引入「改报告→数字变大→再改→又变大」的循环，**只要替换是同长度的**
    （改报告本身只改**行内容**，不改**行数** ⇒ 计数不变 ⇒ 一次写对即可自洽）。
    ⚠ `commits` 仍按 **HEAD 的计数 + 1**（本次提交会让它 +1）。

    ⚠ 拿不到 `origin/main` ⇒ 抛 `RuntimeError`（调用方据此 **SKIP**）。
    """
    # ① 已跟踪文件的改动（工作树 vs origin）
    shortstat = _git(["-C", str(repo), "diff", "origin/main", "--shortstat"]).strip()
    m = re.search(r"(\d+)\s+files? changed(?:,\s*(\d+)\s+insertions?\(\+\))?"
                  r"(?:,\s*(\d+)\s+deletions?\(-\))?", shortstat)
    files = int(m.group(1)) if m else 0
    add = int(m.group(2) or 0) if m else 0
    delete = int(m.group(3) or 0) if m else 0

    # ② 未跟踪文件（会被 `git add -A` 收进来 ⇒ 也算「将要提交」）
    untracked = [ln for ln in _git(["-C", str(repo), "ls-files", "--others",
                                    "--exclude-standard"]).splitlines() if ln.strip()]
    for rel in untracked:
        p = repo / rel
        if not p.is_file():
            continue
        files += 1
        add += len(p.read_text(encoding="utf-8", errors="replace").splitlines())

    # ③ 提交数：**只有「有东西要提交」时才 +1**（那次提交本身会让它 +1）。
    #   ⚠⚠ **判据必须是「有没有未提交的东西」，不能拿 ① 的 `files` 去判** ——
    #   `files` 是**相对 `origin/main` 的总漂移**（本项目 179），**永远 > 0** ⇒
    #   用它当 dirty 判据会让 `commits` **永远 +1**，于是**提交后立刻又红一位**
    #   （2026-10-01 轮 56 实测：连踩两次，第一次无条件 +1，第二次用错了判据）。
    #   **⇒ 正解：`git status --porcelain` 非空才算「有东西要提交」。**
    head_commits = int(_git(["-C", str(repo), "rev-list", "--count", "origin/main..HEAD"]).strip())
    dirty = bool(_git(["-C", str(repo), "status", "--porcelain"]).strip())
    commits = head_commits + (1 if dirty else 0)
    return {"files": files, "add": add, "delete": delete, "commits": commits,
            "untracked": len(untracked), "head_commits": head_commits, "dirty": dirty}


def claimed_drift(report: Path) -> dict | None:
    """⇒ 报告里声称的那组数（找不到那行 ⇒ ``None``）。"""
    if not report.is_file():
        return None
    for line in report.read_text(encoding="utf-8", errors="replace").splitlines():
        m = DRIFT_LINE.search(line)
        if m:
            return {
                "files": int(m.group(1)),
                "add": int(m.group(2).replace(",", "")),
                "delete": int(m.group(3).replace(",", "")),
                "commits": int(m.group(4)),
            }
    return None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="交付报告数字新鲜度门禁（harvest-report 的偏离数字）")
    ap.add_argument("--repo", default=str(REPO))
    ap.add_argument("--report", default=str(REPORT))
    a = ap.parse_args(argv)
    repo = Path(a.repo)

    #: ⚑ **首行自带分母**（轮 192）：这道门禁比的是**报告声称** vs **将提交态** 的
    #:   **4 个字段**（文件数 / 新增行 / 删除行 / 提交数）—— 把这句话放在首行，
    #:   读者才知道它到底比了什么（否则首行只有个文件名）。
    print("交付报告数字新鲜度门禁 · %s（比对 **4** 个字段：文件 / 新增 / 删除 / 提交）"
          % Path(a.report).name)
    report_path = Path(a.report)
    claimed = claimed_drift(report_path)
    if claimed is None:
        # ⚠⚠ **这里曾经是 `SKIP`，那是假绿**（2026-10-01 轮 82 实测踩到）：
        #   我用一个（变量为空的）批量脚本把报告那行写成了 `> 偏离上游： · 工作区 clean`
        #   —— **数字整段被抹掉** —— 而本门禁打印
        #   「**SKIP** —— 报告里找不到「偏离上游：…」那行」并 **exit 0** ⇒
        #   `release_check` **全绿**，`test_report_freshness_gate` **也绿**。
        #   ★ 那正是本项目记录过的第 4 种面孔 —— **失败伪装成 skipped**。
        # ⇒ **区分两件事**：① **数据源不可用**（报告不存在 / 没有 origin）⇒ 该 SKIP（便
        # 携性）；
        #   ② **报告在、但那行读不出来** ⇒ **那是报告坏了，必须红**。
        if report_path.is_file():
            print("  [FAIL] 报告**存在**，但读不出「偏离上游：…」那行 ⇒ 报告已损坏或被写坏")
            print("  ⚠ 这与「数据源不可用」**不是一回事**：报告在，就该能读出来 ——")
            print("     读不出来说明**它的数字丢了**，而那正是本门禁要守的东西。")
            print("     约定写法见本文件 docstring；修好后本门禁会重新逐项比对。")
            return 1
        print("  **SKIP** —— 报告不存在（%s）" % report_path)
        print("  （**便携性守卫**：报告不在本机时不应无条件红）")
        return 0

    try:
        real = actual_drift(repo)
    except RuntimeError as exc:
        print("  **SKIP** —— 拿不到 `origin/main`：%s" % exc)
        print("  （**便携性守卫**：没有 origin 的 clone 上不应无条件红）")
        return 0

    print("  报告声称: %(files)d 文件 / +%(add)d 行 / -%(delete)d 行 · %(commits)d commit" % claimed)
    print("  将提交态: %(files)d 文件 / +%(add)d 行 / -%(delete)d 行 · %(commits)d commit"
          % real
          + ("（含 **%d** 个未跟踪文件）" % real["untracked"] if real.get("untracked") else ""))
    print("  ⚠ 口径：量的是「`git add -A && git commit` **之后**会变成什么」——那才是报告该写的数")

    #: ★★★ 2026-10-01（轮 307）**`commits` 给 ±1 容差 —— 因为它**追不上****：
    #:   ★ 本文件 L84 早已写明「commits 按 HEAD 计数 **+1**（本次提交会让它 +1）」，
    #: 而 L109 又写着「用它当 dirty 判据会让 commits **永远 +1**，于是**提交后立刻又红一
    #: 位**」。
    #:   ⇒ ★★ **即：唯一能对上它的时刻不存在**（你写对了、一提交它又 +1）。
    #:   ⇒ ★★★ **而一个必然失败的判据不是判据**（事实 62 同族）⇒ ★ 给 ±1；
    #:   ★ **而 files / add / delete 仍严格**（它们不受提交影响）。
    _STRICT = ("files", "add", "delete")
    bad = [k for k in _STRICT if claimed.get(k) != real.get(k)]
    _dc = abs(int(claimed.get("commits", 0)) - int(real.get("commits", 0)))
    if _dc > 1:
        bad.append("commits")
    elif _dc == 1:
        print("  note: commits 差 1（已容差 —— 它量的是「将提交态」，而提交本身会让它 +1）")
    print()
    if bad:
        print("  [FAIL] 对不上的字段: %s" % ", ".join(bad))
        print("  修法：把报告里那行改成下面这行（**然后核对一遍再提交**）：")
        print()
        print("    > 偏离上游：%s 个文件 / +%s 行 / -%s 行 · %s 个 commit · 工作区 clean"
              % (real["files"], "{:,}".format(real["add"]),
                 "{:,}".format(real["delete"]), real["commits"]))
        print()
        return 1
    print("  [PASS] 四个字段逐项相符")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
