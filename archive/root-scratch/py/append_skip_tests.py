"""追加到 tests/test_gate_negative_cases.py 的第四层测试（独立文件便于安全追加）。"""
from __future__ import annotations

import sys
from pathlib import Path

TARGET = Path(r"C:\swprojects\sw-skill-fork\tests\test_gate_negative_cases.py")

BLOCK = '''

# ══ ⑨ 门禁「第四层」：`skipped` 的**依据**必须合法（轮 73 加）════════════

_SKIP_CASES = [
    (
        "故障（超时/OSError）返回 skipped",
        "def f():\\n"
        "    try:\\n"
        "        pass\\n"
        "    except OSError as exc:\\n"
        '        return {"status": "skipped", "reason": str(exc)}\\n',
        False,
    ),
    (
        "非 git 工作树返回 skipped（合理）",
        "def f():\\n"
        "    if not _git_available():\\n"
        '        return {"status": "skipped", "reason": "非 git"}\\n',
        True,
    ),
    (
        "脚本约定 exit 2（合理）",
        "def f():\\n"
        "    if proc.returncode == 2:\\n"
        '        return {"status": "skipped", "reason": "读不到锚点"}\\n',
        True,
    ),
    (
        "脚本自报 [SKIP] 驱动变量（合理）",
        "def f():\\n"
        '    skipped = any(l.startswith("[SKIP]") for l in out)\\n'
        "    if skipped:\\n"
        '        status = "skipped"\\n',
        True,
    ),
]


def test_skip_depends_on_whitelisted_evidence():
    """★★ **核心负例**：`skipped` 的**依据**必须落在白名单内。

    ⚠ 这是同一个问题的**第四层**：门禁**接好了**（轮 71）· **方式对了**（轮 72），
      但**它跳过的时候**呢？调用点只看 `"fail"` ⇒ **`skipped` 会被静默放行**。
      实测：`release_check.py` 里原有 **5 处**「**无法启动**（`TimeoutExpired`/`OSError`）」
      返回 `skipped` —— **那是故障，不是便携性**，已全部改成 `fail`。

    ⚠ 本测试把四种形态一次钉死：只有「数据源缺失 / 脚本约定 / 脚本自报 `[SKIP]`」算合理。
    """
    cgw = _load("check_gate_wiring")
    for name, src, want in _SKIP_CASES:
        branches = cgw.skip_branches(src)
        hit = any(any(tok in ctx for tok in cgw.ALLOWED_SKIP_CONDITIONS)
                  for _ln, _cond, ctx in branches)
        assert hit == want, "用例「%s」：白名单命中 %s，应为 %s" % (name, hit, want)


def test_skip_branch_looks_at_the_variable_source_not_only_the_test():
    """★★ **判据要看变量的来源**，不能只看 `if` 的 `test`。

    ⚠ 实测踩过（轮 73）：第一版判据只看 `If.test`，而
      `_run_interface_ownership_probe` 里那条 `if skipped:` 的条件是**变量**，
      来源在它**上一行**（`skipped = any(... startswith("[SKIP]") ...)`)
      ⇒ 那条**合法的** `skipped` 被**误报成违规**。
    ★ 与已知事实 51 同族：判据的范围必须贴合它要抓的那件事。
    """
    cgw = _load("check_gate_wiring")
    src = (
        "def f():\\n"
        '    skipped = any(l.startswith("[SKIP]") for l in out)\\n'
        "    if skipped:\\n"
        '        status = "skipped"\\n'
    )
    branches = cgw.skip_branches(src)
    assert branches, "应当识别出这条 skipped 分支"
    _ln, cond, ctx = branches[0]
    assert "startswith" in ctx, "判据的上下文必须覆盖变量的**来源**，实际只拿到：%r" % cond


def test_real_release_check_only_skips_for_whitelisted_reasons():
    """★ 对**真仓库**的断言：`release_check.py` 里每处 `skipped` 的依据都在白名单内。

    ⚠ 这一条同时守住「以后有人新加一个 `except …: return skipped`」的回归。
    """
    cgw = _load("check_gate_wiring")
    src = (Path(__file__).resolve().parents[1] / "scripts" / "release_check.py").read_text(
        encoding="utf-8")
    for ln, cond, ctx in cgw.skip_branches(src):
        assert any(tok in ctx for tok in cgw.ALLOWED_SKIP_CONDITIONS), (
            "L%d 的 `skipped` 依据 `%s` 不在白名单内" % (ln, cond))
'''

text = TARGET.read_text(encoding="utf-8")
if "test_skip_depends_on_whitelisted_evidence" in text:
    print("  已追加过，跳过")
else:
    TARGET.write_text(text + BLOCK, encoding="utf-8")
    print("  OK 已追加（%d -> %d 行）" % (len(text.splitlines()),
                                        len((text + BLOCK).splitlines())))
sys.stdout.reconfigure(encoding="utf-8")
