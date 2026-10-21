"""★ 负例测试：`tools/commit_mine.py` 的删除处理必须区分「记录删除」与「路径拼错」。

背景（2026-10-19 实测踩到）：`commit_mine.py` 的 `--allow-deletions` 曾**形同虚设** ——
第 0 步的注释明写「不能拿'路径不存在'去拦删除」，而第 2 步的代码正是那么拦的
⇒ `commit_mine.py` **永远提交不了删除**（清理 68 个工具时只能绕道
`git add` + `git commit -F`）。

★ 本测试固化修复后的三条判据（依据 `docs/known-facts.md` 事实 62：
  门禁/工具「写了」不等于「有效」，负例是唯一证明）：
  ① **已跟踪 + 已删** ⇒ 不带 `--allow-deletions` 必须拒（exit 6）；
  ② **已跟踪 + 已删** ⇒ 带 `--allow-deletions` 必须放行（exit 0）；
  ③ **不存在且未跟踪** ⇒ 一律拒（exit 4，拼错了），与 `--allow-deletions` 无关。

★ 测试**不真删仓库文件**：用 `git ls-tree HEAD` 里确实存在、但可以临时移走再还原的文件。
  若找不到合适文件则跳过（不假绿）。
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "commit_mine.py"

#: ★ 用来做「已跟踪 + 已删」实验的文件：必须足够小、且不与其它测试共享状态。
#: ⚠ 若该文件将来被删/改名，本测试会跳过而不是失败（避免测试自身腐坏成噪声）。
VICTIM = "tools/probe_overlap_closure.py"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(TOOL), *args], cwd=ROOT,
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def _tracked(path: str) -> bool:
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD", "--", path],
                         cwd=ROOT, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    return bool((out.stdout or "").strip())


class CommitMineDeletionTest(unittest.TestCase):
    """★ 判据：删除必须能被记录，但拼错的路径不能被当成删除。"""

    def setUp(self) -> None:
        #: ★ 每次从干净索引开始（`commit_mine` 自己也会 reset，但先清更稳）
        subprocess.run(["git", "reset", "-q"], cwd=ROOT, capture_output=True)

    def tearDown(self) -> None:
        subprocess.run(["git", "reset", "-q"], cwd=ROOT, capture_output=True)

    # ── 判据 ③：不存在且未跟踪 ⇒ 一律拒 ──────────────────────────────
    def test_nonexistent_untracked_path_rejected(self) -> None:
        """★ 拼错的路径必须被拒（exit 4），**即使**带了 `--allow-deletions`。"""
        proc = _run("--allow-deletions", "--dry-run", "tools/this_never_existed_xyz.py")
        self.assertEqual(proc.returncode, 4,
                         "★ 拼错的路径没被拒（exit=%d）：%s"
                         % (proc.returncode, (proc.stdout or "")[-300:]))
        self.assertIn("不存在且未被 git 跟踪", proc.stdout or "",
                      "★ 拒绝理由没说清是「拼错」而不是「要删」")

    # ── 判据 ①：已跟踪 + 已删，不带开关 ⇒ 拒 ────────────────────────
    def test_tracked_deletion_requires_flag(self) -> None:
        """★ 已跟踪 + 已删，但没给 `--allow-deletions` ⇒ 必须拒（exit 6）。"""
        if not _tracked(VICTIM) or not (ROOT / VICTIM).is_file():
            self.skipTest("★ 测试用的文件不存在或未被跟踪：%s" % VICTIM)
        backup = ROOT / (VICTIM + ".testbak")
        shutil.copy2(ROOT / VICTIM, backup)
        try:
            (ROOT / VICTIM).unlink()
            proc = _run("--dry-run", VICTIM)
            self.assertEqual(proc.returncode, 6,
                             "★ 删除未被拦（exit=%d）：%s"
                             % (proc.returncode, (proc.stdout or "")[-300:]))
            self.assertIn("已被删除", proc.stdout or "",
                          "★ 拒绝理由没说清「这是删除」")
        finally:
            shutil.move(str(backup), str(ROOT / VICTIM))

    # ── 判据 ②：已跟踪 + 已删 + 开关 ⇒ 放行 ────────────────────────
    def test_tracked_deletion_allowed_with_flag(self) -> None:
        """★★ 已跟踪 + 已删 + `--allow-deletions` ⇒ 必须放行（exit 0）。

        ★ 这条是本修复的**核心**：修复前它必然 exit 4（路径不存在被拒），
          于是 `--allow-deletions` 成了死开关。
        """
        if not _tracked(VICTIM) or not (ROOT / VICTIM).is_file():
            self.skipTest("★ 测试用的文件不存在或未被跟踪：%s" % VICTIM)
        backup = ROOT / (VICTIM + ".testbak")
        shutil.copy2(ROOT / VICTIM, backup)
        try:
            (ROOT / VICTIM).unlink()
            proc = _run("--allow-deletions", "--dry-run", VICTIM)
            self.assertEqual(proc.returncode, 0,
                             "★★ 修复退化：`--allow-deletions` 仍提交不了删除"
                             "（exit=%d）：%s"
                             % (proc.returncode, (proc.stdout or "")[-400:]))
            self.assertIn(VICTIM, proc.stdout or "",
                          "★ 索引里没看到那个被删的文件")
        finally:
            shutil.move(str(backup), str(ROOT / VICTIM))

    # ── 边界：活文件照旧能提交 ──────────────────────────────────────
    def test_existing_file_still_works(self) -> None:
        """★ 正常路径不受影响（★ 防「修删除把正常提交搞坏」）。

        ⚠ 这条测试**不能依赖工作树里恰好有改动** —— 我第一次写时就踩了：
          提交之后 `commit_mine.py` 变干净，`--dry-run` 索引里 0 个文件 ⇒ 假红。
          ⇒ 改为**自己造一个改动**（临时文件），跑完删掉。
        ★ 另：必须同时给 `--allow-deletions`，因为若 `commit_mine.py` 本身
          有删除行，第 0 步护栏会拦 —— 那是**正确行为**（事实 61），不是回归。
        """
        probe = ROOT / "tools" / "_commit_mine_probe_tmp.py"
        probe.write_text('"""★ 临时探针：供 test_existing_file_still_works 用。"""\n',
                         encoding="utf-8")
        try:
            proc = _run("--allow-deletions", "--dry-run", "tools/_commit_mine_probe_tmp.py")
            self.assertEqual(proc.returncode, 0,
                             "★ 正常文件提交被误伤（exit=%d）：%s"
                             % (proc.returncode, (proc.stdout or "")[-300:]))
            self.assertIn("_commit_mine_probe_tmp.py", proc.stdout or "",
                          "★ 活文件没进索引")
        finally:
            probe.unlink(missing_ok=True)
            subprocess.run(["git", "reset", "-q"], cwd=ROOT, capture_output=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
