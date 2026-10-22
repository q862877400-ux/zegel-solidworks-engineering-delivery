r"""@brief 验收命令的可跑性门禁：`→ 验收:` 行点到的脚本必须**在仓库里**。

## 为什么要有它（**已现 2 例**）
ROADMAP §〇 的三条纪律之三写着「**验收必须是可跑的命令** —— 『我检查过了』不算」。
但**命令指到的脚本可能在仓库里根本不存在** —— 探索期在工作区根就地写的脚本，
被写进 spec 当了验收命令，**却从没搬进仓库** ⇒ **换台机器 / CI 跑不了**。

```
2026-10-01 实测两例（都对不上）：
  · `specs/002-merge-template/tasks.md` T-005  →  `D:\AI\SW\capability_gap.py`   ✗ 不在仓库
  · `specs/001-topology-result-readout/spec.md` SC-001 → `probe_results_api_surface.py` ✗ 不在仓库
```

## 判据（**三路，按特异性排序**）
对每个 `→ 验收:` 行里出现的脚本记号：
| 形态 | 例子 | 判定 |
|---|---|---|
| ① **绝对路径** | `D:\AI\SW\capability_gap.py` | ⚠ **报**（**仓库外** —— 换机器就没有） |
| ② **带仓库目录前缀** | `tools\capture_topology_evidence.py` | 查该路径**在仓库里存在吗** |
| ③ **裸文件名** | `capability_gap.py` | 在仓库里**按名搜**；找不到 ⇒ ⚠ **报** |

⚠ **便携性**：`--specs-root` 默认指向本机工作区；**目录不存在就 SKIP 并说明**
（不是 fail）—— 否则别的机器上这个门禁会无条件红。
⚠ **不做的事**：**不自动改** spec（那些行记录的是当时的真实形态，有历史价值）；
**只报「哪一行、指到哪个不在仓库的路径」**。

## 与既有门禁的分工（**不重造**）
`check_provenance`（出处）/ `check_member_names`（成员名）/ `check_diff_markers`（diff 记号）
/ `check_union_conventions`（并入规范）/ `check_env_pitfalls`（环境坑）
—— 都管**代码与清单**；本门禁管**计划制品（specs）里的命令可跑性**。

# ── 来源 ──
# 仓库:   本项目自身（门禁实现）
# 文件:   scripts/check_spec_acceptance_paths.py —— 本文件自身
#         tests/test_spec_acceptance_paths_gate.py（契约测试 + 负例）
# 定位:   把「验收必须是可跑的命令」（ROADMAP §〇 纪律三）从「人记得」升级为「门禁守着
#           」；
#         依据是 2026-10-01 实测到的 **2 例仓库外验收脚本**。
# 官方签名依据: 不适用（纯静态：读 markdown + 查仓库文件，**不连 SolidWorks**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

#: 2026-10-03（接手轮）强制 stdout 为 UTF-8 —— 本门禁会 print 中文与箭头/勾这类符号，
#:   而 stdout 是管道时（测试正是用管道抓输出）默认按 locale（本机 GBK）编码
#:   ⇒ UnicodeEncodeError: 'gbk' codec can't encode character … ⇒ 门禁自己崩掉。
#:   known-facts 58 那一族（中文 Windows 上两侧默认编码不一致 —— 病灶在输出侧）；
#:   而测试那侧的 subprocess.run 已经带了 encoding='utf-8'。
sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]

#: 仓库里**允许被验收命令点到的目录**（其余顶层目录不是代码落点）
REPO_DIRS = ("scripts", "tools", "tests", "docs", "mcp-server", "apps", "subskills")

#: 验收行的标记（本项目的约定统一用「→ 验收:」）
ACCEPT = re.compile(r"→\s*验收\s*[:：]")

#: ① 绝对路径（Windows 盘符开头）指向一个 `.py`
ABS_SCRIPT = re.compile(r"([A-Za-z]:[\\/][^\s`'\"|）)]*?\.py)")

#: ② 带仓库目录前缀（正/反斜杠都认）
REPO_SCRIPT = re.compile(r"(?<![\w\\/])((?:%s)[\\/][^\s`'\"|）)]*?\.py)" % "|".join(REPO_DIRS))

#: ③ 裸文件名（前后不是路径分隔符）
BARE_SCRIPT = re.compile(r"(?<![\w\\/.])([A-Za-z_]\w*\.py)")


def _strip_repo_scripts(line: str) -> str:
    """把 ② 形态先从行里抠掉，免得它们的尾巴又被 ③ 抓一次。"""
    return REPO_SCRIPT.sub(" ", line)


def check_line(line: str, repo: Path) -> list:
    """⇒ ``[(kind, token, detail)]``：该验收行里的问题记号。

    ⚠⚠ **第一版有一处假阳性**（轮 53 首跑就撞上）：我把**任何绝对路径**都报成「仓库外」，
    而 `→ 验收: Select-String C:\\swprojects\\sw-skill-fork\\tools\\capture_simulation_evidence.py …`
    里的绝对路径**就在仓库根下面**（文件**在仓库里**，只是写成了绝对形式）。
    **⇒ 修正：绝对路径要判「是否在 `repo` 之下」** —— 在 ⇒ 通过（可提示改相对）；
    不在 ⇒ 才是真的仓库外。
    """
    out = []
    rest = _strip_repo_scripts(line)

    for m in ABS_SCRIPT.finditer(rest):
        tok = m.group(1)
        try:
            p = Path(tok)
            inside = repo in p.resolve().parents or p.resolve() == repo
        except (OSError, ValueError):
            inside = False
        if not inside:
            out.append(("outside-repo", tok, "**绝对路径且不在仓库根下** ⇒ 只在写它的那台机器上有"))
    rest = ABS_SCRIPT.sub(" ", rest)

    # ② 带前缀的：要真的在仓库里
    for m in REPO_SCRIPT.finditer(line):
        tok = m.group(1)
        # ⚠⚠ **glob 不是字面路径**（2026-10-01 轮 83 实测到的假阳性）：
        #   本仓库的验收判据**惯用 grep 形态**（如 `Select-String scripts\check_*.py -Pattern …`），
        #   而这里原先直接 `p.is_file()` ⇒ **带 `*` 的必然判"仓库里没有这个文件"** ⇒ 误报。
        #   ★ 与本函数 docstring 里记的那次假阳性（轮 53：绝对路径**在仓库里**却被报「仓库外」）
        #     **是同一族**：判据要贴合**实际的书写形态**。
        #   ⇒ 含 glob 元字符的 token 用 `repo.glob()` 展开：**匹配到 ≥1 个**才算通过；
        #     一个都没匹配到 ⇒ 报 `glob-no-match`（**仍然会红**，只是换了原因）。
        if any(ch in tok for ch in "*?["):
            if not any(repo.glob(tok.replace("\\", "/"))):
                out.append(("glob-no-match", tok,
                            "带 glob 的仓库内路径，但**一个都没匹配到**"))
            continue
        p = repo / tok.replace("\\", "/")
        if not p.is_file():
            out.append(("missing-in-repo", tok, "带仓库目录前缀，但**仓库里没有这个文件**"))

    # ③ 裸文件名：在仓库里按名搜
    for m in BARE_SCRIPT.finditer(rest):
        tok = m.group(1)
        if not any(repo.rglob(tok)):
            out.append(("bare-not-found", tok, "**裸文件名**，且仓库里搜不到"))
    return out


def scan(specs_root: Path, repo: Path) -> list:
    """⇒ ``[(file, lineno, line, problems)]``（只收有问题的行）。"""
    hits = []
    for md in sorted(specs_root.rglob("*.md")):
        for i, line in enumerate(md.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if not ACCEPT.search(line):
                continue
            probs = check_line(line, repo)
            if probs:
                hits.append((md, i, line.strip(), probs))
    return hits


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="验收命令可跑性门禁（→ 验收: 行点到的脚本须在仓库里）")
    #: ★★★ 2026-10-17 修正（★ 环境搬迁暴露的 bug）：★ 原默认值**写死** `Path(__file__).resolve().parents[1] / "specs"` ✗ ——
    #:   ★ 仓库搬到便携版工作区后，它**扫的是旧副本**、却拿**新仓库根**去判
    #:   ⇒ ★ 旧副本里的 `D:/AI/SW/...` 全被判「仓库外」⇒ **21 条假红** ✓
    #:   ★★ 更糟的是：★ 若旧副本被删，它会走 SKIP 分支（exit 0）⇒ **静默不检查任何东西** ✗
    #:   ⇒ ★ 改为**从本文件位置推出仓库根**（与 `REPO` 同一口径）✓ —— ★ 便携性守卫仍在（不存在则 SKIP）✓
    ap.add_argument("--specs-root", default=str(REPO / "specs"),
                    help="specs 目录（默认**本仓库**的 specs；**不存在则 SKIP**）")
    ap.add_argument("--repo", default=str(REPO))
    a = ap.parse_args(argv)

    specs_root = Path(a.specs_root)
    repo = Path(a.repo)

    if not specs_root.is_dir():
        print("验收命令可跑性门禁：**SKIP** —— specs 目录不在本机（%s）" % specs_root)
        print("  （这是**便携性守卫**：别的机器上没有工作区 ⇒ 不应无条件红）")
        return 0

    n_lines = sum(1 for md in specs_root.rglob("*.md")
                  for ln in md.read_text(encoding="utf-8", errors="replace").splitlines()
                  if ACCEPT.search(ln))
    hits = scan(specs_root, repo)

    #: ⚑ **首行自带分母**（轮 192）：`n_lines` 已经在手边（原先下一行才打印）⇒ 提到首行。
    print("验收命令可跑性门禁 · 扫 %s（**%d** 处 `→ 验收:` 行）" % (specs_root, n_lines))
    print("  **%d** 处 `→ 验收:` 行；仓库根 = %s" % (n_lines, repo))
    print()
    if hits:
        print("  [FAIL] %d 行的验收命令点到**仓库外/不存在**的脚本：" % len(hits))
        for md, i, line, probs in hits:
            print("    %s:%d" % (md.name, i))
            print("      行: %s" % line[:120])
            for kind, tok, detail in probs:
                print("      · [%s] %s —— %s" % (kind, tok, detail))
        print()
        print("  修法：把脚本按仓库规范收进 `tools/`（来源块 + 只读 + 不连 SolidWorks），"
              "或把验收命令改写成**仓库内**的等价命令。")
        return 1
    print("  [PASS] 0 行 —— 所有 `→ 验收:` 行点到的脚本都在仓库里")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
