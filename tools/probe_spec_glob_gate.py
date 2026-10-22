r"""@brief 负例：`check_spec_acceptance_paths` 对 glob 的处理必须**两边都对**。

## 背景（2026-10-01 轮 83，Spec Kit `007`）
该门禁的 ② 分支原先用 `p.is_file()` 判「带仓库目录前缀的 token」，而本仓库的验收判据
**惯用 grep 形态**（`Select-String scripts\check_*.py -Pattern …`）⇒ **带 `*` 的必然误报**。
已改成：含 glob 元字符 ⇒ 用 `repo.glob()` 展开，**匹配到 ≥1 个**才算通过。
⇒ 本探针证明**两边都对**：
* **正例**：glob 能匹配到 ⇒ 通过（不误报）；
* **负例**：glob **一个都匹配不到** ⇒ **仍然红**（换了个原因名，但没放过）。

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_spec_glob_gate.py
# 定位:   为 `scripts/check_spec_acceptance_paths.py` 的 glob 分支取证（负例是唯一的证
#           明）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

#: ★ 本仓库根（★ 2026-10-03 合并后自定位）
_ROOT_S = str(Path(__file__).resolve().parents[1])
REPO = Path(r"" + _ROOT_S + r"")
GATE = REPO / "scripts" / "check_spec_acceptance_paths.py"
sys.stdout.reconfigure(encoding="utf-8")

ARROW = "\u2192 \u9a8c\u6536:"  # → 验收:


def _run(specs_root: Path) -> tuple:
    p = subprocess.run(
        [sys.executable, str(GATE), "--specs-root", str(specs_root)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO),
        stdin=subprocess.DEVNULL,
    )
    return p.returncode, (p.stdout or "")


def _case(label: str, acceptance: str) -> int:
    root = Path(tempfile.mkdtemp()) / "specs" / "999-probe"
    root.mkdir(parents=True)
    (root / "tasks.md").write_text(
        "# probe\n\n`%s` `%s`\n" % (ARROW, acceptance), encoding="utf-8"
    )
    rc, out = _run(root.parent)
    print("  %-46s ⇒ exit=%d" % (label, rc))
    for l in out.splitlines():
        if "[FAIL]" in l or "glob-no-match" in l or "missing-in-repo" in l:
            print("      %s" % l.strip()[:98])
    shutil.rmtree(root.parent.parent, ignore_errors=True)
    return rc


def main() -> int:
    print("══ `check_spec_acceptance_paths` 的 glob 处理（正例 / 负例）══")
    rc_ok = _case(
        "正例 glob 能匹配", r"Select-String scripts\check_*.py -Pattern 'SKIP'"
    )
    rc_bad = _case(
        "负例 glob 一个都匹配不到", r"Select-String scripts\nonexistent_*.py -Pattern x"
    )
    rc_lit = _case("负例 字面文件不存在", r"Select-String scripts\nope.py -Pattern x")

    print()
    print("  ── 判定 ──")
    expect = (rc_ok == 0, rc_bad == 1, rc_lit == 1)
    print("    正例 exit 0        : %s" % ("✓" if expect[0] else "**✗**"))
    print("    glob 无匹配 exit 1 : %s" % ("✓" if expect[1] else "**✗**"))
    print("    字面不存在 exit 1  : %s" % ("✓" if expect[2] else "**✗**"))
    return 0 if all(expect) else 1


if __name__ == "__main__":
    raise SystemExit(main())
