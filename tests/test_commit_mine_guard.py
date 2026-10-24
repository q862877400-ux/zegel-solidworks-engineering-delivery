"""★ 提交纪律护栏的契约测试（含负例）—— 地雷来自 `round_chain.ps1` 的三处 `git add -A`。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tests/test_commit_mine_guard.py
# 定位:   给 `tools/commit_mine.py`（★ 本轮新增，处置事实 555 那个地雷）补契约测试。
# ★★ 为什么必须有负例（本仓纪律）：那个地雷的**默认行为**就是「误提交别人的文件」——
#   ★ 一个只在「我做对了」时才通过的判据，对这类地雷**没有证明力**（事实 62）✓
# ★★ 测试**不碰真索引**：全程 monkeypatch `_git`（★ 否则一条测试就会把使用者
#   工作树里别人**待提交**的东西 reset 掉 —— ★ 那正是被处置的那个伤害本身）✓
# 官方依据: 不适用（本仓 git 纪律；`round_chain.ps1` 的 L84/L117/L142 三处 `git add -A` 是事实）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib.util
import subprocess
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    """★ 按路径加载 `tools/commit_mine.py`（★ 它不在包里）。"""
    spec = importlib.util.spec_from_file_location("commit_mine", ROOT / "tools" / "commit_mine.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["commit_mine"] = mod
    spec.loader.exec_module(mod)
    return mod


MOD = _load()


class _FakeIndex:
    """★★ 一个**忠实的**假索引（★ 这是本测试的关键，不是装饰）：

    ★ 第一版我让 `_git` 对**任何**调用都回同一段 `numstat` ⇒ ★★ 于是「reset 之后索引非空」
      这道守卫**永远**为真 ⇒ 三条测试红得莫名其妙 ✓✗
    ★★★ 根因是我的假 git **无声地撒了谎**：真 git 在 `reset` 之后索引**是空的**、
      `add` 之后才有点名的那些 ⇒ ★ 假实现必须**同样随状态变**，否则测的不是真行为（★ 事实 57 同族）✓
    """

    def __init__(self):
        self.entries: dict[str, tuple[int, int]] = {}   #: 路径 ⇒ (增, 删)
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, *args: str) -> subprocess.CompletedProcess:
        self.calls.append(args)
        if args[:1] == ("reset",):
            self.entries = {}                            #: ★ 真 git reset = 清空索引
        elif args[:2] == ("add", "--"):
            for p in args[2:]:
                self.entries[p] = (1, 0)                 #: ★ 新文件 ⇒ +1/-0
        if args[:2] == ("diff", "--cached"):
            out = "".join("%d\t%d\t%s\n" % (a, d, p) for p, (a, d) in self.entries.items())
            return subprocess.CompletedProcess(("git",) + args, 0, out, "")
        if args[:1] == ("commit",):
            return subprocess.CompletedProcess(("git",) + args, 0, "[fake] committed\n", "")
        if args[:1] == ("show",):
            return subprocess.CompletedProcess(("git",) + args, 0, "", "")
        return subprocess.CompletedProcess(("git",) + args, 0, "", "")

    def preload(self, path: str, add: int, dele: int) -> None:
        """★ 直接往索引里塞一条（★ 用来模拟「别人已经暂存的东西」）。"""
        self.entries[path] = (add, dele)


def _real_files(*paths: str) -> list[str]:
    """★ 用**仓库里真实存在**的文件名跑（★ `main` 会查存在性；★ 用 `tools/` 下的稳定文件）。"""
    return [p for p in paths if (ROOT / p).is_file()]


# ── 守卫：源文件抽得到 ───────────────────────────────────────────────────
def test_source_is_reachable():
    """★ 守卫：本测试得真的测到那个模块（★ 加载失败时别让下面静默全通过）。"""
    assert hasattr(MOD, "_git"), "commit_mine 里没有 _git"
    assert hasattr(MOD, "staged"), "commit_mine 里没有 staged"
    assert (ROOT / "tools" / "round_chain.ps1").is_file(), "找不到 round_chain.ps1"


def test_round_chain_really_does_stage_everything():
    """★★ 地雷本体：`round_chain.ps1` 里**确实**有 `git add -A`（★ 本护栏存在的理由）。

    ★ 这条断言把「地雷存在」写死 —— ★ 若哪天上游把 `git add -A` 去掉了，
      ★★ 本测试会红，**提醒后人护栏可以撤**（★ 而不是让一个空转的护栏永远留着）✓
    """
    text = (ROOT / "tools" / "round_chain.ps1").read_text(encoding="utf-8", errors="replace")
    assert text.count("git add -A") >= 1, (
        "round_chain.ps1 里没有 `git add -A` 了 ⇒ ★ 请复核 commit_mine.py 是否还需要")


# ── 主断言：只留点名的文件 ───────────────────────────────────────────────
def test_only_named_files_stay_staged(monkeypatch):
    """★★ 主断言：索引里先塞满「别人的文件」⇒ 护栏后**只剩点名的那一个** ✓"""
    mine = "tools/commit_mine.py"
    fake = _FakeIndex()
    fake.preload("docs/PLAN.md", 56, 0)             #: ★ 别人的
    fake.preload("docs/metrics.md", 5, 5)              #: ★ 别人的（含删除）
    monkeypatch.setattr(MOD, "_git", fake)
    #: ★ 删除预载会先触发第 0 步 ⇒ 这里给它放行权限，专测「只留点名的」
    rc = MOD.main(["--dry-run", "--allow-deletions", mine])
    assert rc == 0, "护栏应放行，实际 rc=%r" % rc
    assert ("reset", "-q") in fake.calls, "★ 没有先 `git reset` ⇒ 别人的文件会被一起提交"
    assert ("add", "--", mine) in fake.calls, "★ 没有只 add 点名的文件"
    assert not any(c[:1] == ("add",) and "-A" in c for c in fake.calls), "★ 出现了 `git add -A`"
    assert list(fake.entries) == [mine], "★ 索引里还有别人的文件：%r" % list(fake.entries)


def test_negative_untouched_index_is_refused(monkeypatch):
    """★★ 负例：`reset` 之后索引**仍非空** ⇒ 必须**拒绝提交**（★ 不静默继续）。"""
    fake = _FakeIndex()

    class _Stubborn(_FakeIndex):
        def __call__(self, *args):
            r = super().__call__(*args)
            if args[:1] == ("reset",):
                self.entries["someone_else.md"] = (1, 0)   #: ★ 模拟"reset 没清干净"
            return r

    stubborn = _Stubborn()
    monkeypatch.setattr(MOD, "_git", stubborn)
    assert MOD.main(["--dry-run", "tools/commit_mine.py"]) == 3, "索引没清干净却继续了"
    assert fake.entries == {}


def test_negative_deletions_are_refused(monkeypatch):
    """★★ 负例（★ 同事实 61）：索引里有**删除行** ⇒ 默认拒绝，除非显式 `--allow-deletions`。"""
    target = "tools/fix_exemption_escapes.py"
    fake = _FakeIndex()
    fake.preload(target, 0, 232)                        #: ★ 232 行删除（事实 61 那个形状）
    monkeypatch.setattr(MOD, "_git", fake)
    assert MOD.main(["--dry-run", target]) == 6, "232 行删除没被拦住 ⇒ 事实 61 那个事故可以重演"
    #: ★ 显式放行时必须通过（★ 否则判据是死的）
    assert MOD.main(["--dry-run", "--allow-deletions", target]) == 0, \
        "给了 --allow-deletions 仍被拦 ⇒ 护栏把合法删除也挡了"


def test_negative_deletion_via_rename_is_seen(monkeypatch):
    """★★ 负例：**改名/移动**在 numstat 里是「N 增 N 删」⇒ 也要被当删除拦住。"""
    fake = _FakeIndex()
    fake.preload("tools/commit_mine.py", 0, 3)         #: ★ 改名留下的删除侧
    fake.preload("tools/t2_intersect_past_errors.py", 3, 0)
    monkeypatch.setattr(MOD, "_git", fake)
    assert MOD.main(["--dry-run", "tools/t2_intersect_past_errors.py"]) == 6, \
        "改名产生的删除没被看到"


def test_negative_missing_path_is_refused(monkeypatch):
    """★★ 负例：点了一个**不存在**的路径 ⇒ 拒绝（★ 免得 `git add` 静默少加）。"""
    fake = _FakeIndex()
    monkeypatch.setattr(MOD, "_git", fake)
    assert MOD.main(["--dry-run", "no/such/file_xyz.md"]) == 4, "不存在的路径没被拦住"


def test_negative_no_paths_is_refused(monkeypatch):
    """★★ 负例：**一个路径都不点** ⇒ 拒绝（★ 点不出文件就说明调用方想用 `git add -A`）。"""
    fake = _FakeIndex()
    monkeypatch.setattr(MOD, "_git", fake)
    assert MOD.main(["--dry-run"]) == 2, "不点文件却放行了 ⇒ 护栏可被绕过"
