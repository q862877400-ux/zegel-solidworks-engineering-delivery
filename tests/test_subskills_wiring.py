"""钉住 `subskills/` 的**接线一致性**（死守卫的**第五种形态**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_subskills_wiring.py
# 定位:   轮 139：`053`~`057` 扫了**常量** / **函数** / **注册表** / **dispatch**；
#         本文件管**第五种** —— `subskills/*/` 的「manifest / 目录名 / 内嵌快照」是否一致。
#         ★ ⚠⚠ 判据全是**结构**的（存在性 + 名字相等 + 集合比对），不含语义判断
#         ⇒ 按事实 74/78/79 的结论，**可以安全地当回归**。
# 官方依据: 不适用（本项目内部纪律）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

SUB = REPO_ROOT / "subskills"
#: ⚠ 内嵌快照是**构建产物**（在 `.gitignore` 里 ⇒ `git status` 看不见它）。
#: 不在时**跳过**（那是"还没构建"，不是本判据要管的事）。
SNAP = REPO_ROOT / "apps" / "workbench-ui" / "src-tauri" / "resources" / "skill"


def _dirs() -> list:
    return sorted(d for d in SUB.iterdir() if d.is_dir())


def test_every_subskill_has_a_manifest():
    """@brief ★★ 每个 `subskills/*/` 都要有 `manifest.yaml`（没有就装不上）。"""
    missing = [d.name for d in _dirs() if not (d / "manifest.yaml").is_file()]
    assert not missing, "这些 subskill 没有 manifest.yaml: %s" % missing


def test_manifest_name_matches_its_directory():
    """@brief ★ `manifest.yaml` 的 `name` 必须**等于目录名**。

    ⚠ 不等时，加载器按 `name` 找目录会**找不着** —— 而目录本身看着完全正常。
    """
    bad = []
    for d in _dirs():
        man = d / "manifest.yaml"
        if not man.is_file():
            continue
        m = re.search(r"(?m)^\s*name\s*:\s*(.+?)\s*$", man.read_text(encoding="utf-8"))
        declared = m.group(1).strip().strip("\"'") if m else None
        if declared != d.name:
            bad.append("%s: manifest.name=%r" % (d.name, declared))
    assert not bad, "manifest.name 与目录名不一致: %s" % bad


def test_every_subskill_reaches_the_bundled_snapshot():
    """@brief ★★ 每个 subskill 都要进**内嵌快照** —— 没进就**不会随包发布**。

    ⚠ 快照在 `.gitignore` 里（构建产物）⇒ **`git status` 看不见它的缺失**；
    只有这条判据会提醒。
    """
    if not SNAP.is_dir():
        import pytest
        pytest.skip("内嵌快照尚未构建（跑 `python scripts/sync_bundled_skill.py`）")
    live = {d.name for d in _dirs()}
    snap = {d.name for d in (SNAP / "subskills").iterdir() if d.is_dir()} \
        if (SNAP / "subskills").is_dir() else set()
    missing = sorted(live - snap)
    assert not missing, "这些 subskill 不在内嵌快照里（不会随包发布）: %s" % missing


def test_snapshot_differs_only_by_caches():
    """@brief ★★ 快照与源的差异**只允许是缓存/字节码**（`__pycache__` / `.pyc`）。

    ⚑ 轮 139 实测：5 个 subskill 的文件数**全都不一致**（源 28/15/26/8/14 vs 快照 19/11/19/7/12）
    ⇒ 逐条查下来 **23 个差异全是 `__pycache__/*.pyc`** ⇒ **同步脚本排除得对**。
    ⚠ 但"数字不一致"本身值得**钉住**：哪天差异里出现**真源文件**，那就是漏发。
    """
    if not SNAP.is_dir():
        import pytest
        pytest.skip("内嵌快照尚未构建")
    problems = []
    for d in _dirs():
        src = {str(p.relative_to(d)) for p in d.rglob("*") if p.is_file()}
        sd = SNAP / "subskills" / d.name
        dst = {str(p.relative_to(sd)) for p in sd.rglob("*") if p.is_file()} \
            if sd.is_dir() else set()
        for rel in sorted(src - dst):
            if "__pycache__" in rel or rel.endswith((".pyc", ".pyo")):
                continue
            problems.append("%s/%s 源里有、快照无" % (d.name, rel))
        for rel in sorted(dst - src):
            problems.append("%s/%s 快照有、源里无" % (d.name, rel))
    assert not problems, "快照与源的差异不止缓存:\n  %s" % "\n  ".join(problems)


def test_no_bytecode_is_tracked():
    """@brief ★ 仓库里**不许有被跟踪的** `.pyc`（铁律 3：缓存必须 gitignore、不入库）。"""
    import subprocess
    r = subprocess.run(["git", "ls-files", "*.pyc"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", cwd=str(REPO_ROOT))
    tracked = [x for x in (r.stdout or "").splitlines() if x.strip()]
    assert not tracked, "这些 .pyc 被 git 跟踪了: %s" % tracked
