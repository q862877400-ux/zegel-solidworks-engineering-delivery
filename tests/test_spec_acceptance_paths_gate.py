"""@brief 验收命令可跑性门禁的契约测试（**含负例**）。

# ── 来源 ──
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_spec_acceptance_paths_gate.py
# 定位:   给 `scripts/check_spec_acceptance_paths.py`（轮 53 新增的**门禁**）补契约测试。
#         ⚠ 按本仓库纪律：**门禁必须有负例**（「一个存在但没人用的守卫与没有守卫等价」）。
#         依据是 2026-10-01 实测到的 **2 例仓库外验收脚本**。
# 官方签名依据: 不适用（纯静态：读 markdown + 查仓库文件，**不连 SolidWorks**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "check_spec_acceptance_paths", ROOT / "scripts" / "check_spec_acceptance_paths.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_spec_acceptance_paths"] = mod
    spec.loader.exec_module(mod)
    return mod


MOD = _load()


def _mk(tmp_path: Path, body: str) -> Path:
    d = tmp_path / "specs" / "001-x"
    d.mkdir(parents=True)
    (d / "tasks.md").write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return d


#: 一个**最小假仓库**（tests 里不去碰真仓库，免得结论随仓库状态漂）
def _repo(tmp_path: Path) -> Path:
    r = tmp_path / "repo"
    (r / "tools").mkdir(parents=True)
    (r / "scripts").mkdir(parents=True)
    (r / "tools" / "real_tool.py").write_text("x = 1\n", encoding="utf-8")
    return r


def test_current_tree_passes() -> None:
    """当前工作区的 specs 应 0 问题（否则门禁该红）。"""
    assert MOD.main(["--specs-root", r"D:\AI\SW\specs", "--repo", str(ROOT)]) == 0


def test_missing_specs_root_skips(tmp_path: Path) -> None:
    """★ **便携性守卫**：specs 目录不在本机 ⇒ **SKIP（exit 0）**，不是 fail。

    ⚠ 否则别的机器上（没有 `D:\\AI\\SW\\`）这个门禁会**无条件红**。
    """
    assert MOD.main(["--specs-root", str(tmp_path / "nope"), "--repo", str(ROOT)]) == 0


def test_absolute_outside_repo_is_reported(tmp_path: Path) -> None:
    """★ **负例①**：绝对路径且**不在仓库根下** ⇒ 报。"""
    _mk(tmp_path, """
        # X
        `→ 验收:` `python D:\\AI\\SW\\capability_gap.py` 输出逐域表
    """)
    r = _repo(tmp_path)
    assert MOD.main(["--specs-root", str(tmp_path / "specs"), "--repo", str(r)]) == 1
    hits = MOD.scan(tmp_path / "specs", r)
    kinds = {k for _, _, _, probs in hits for k, _, _ in probs}
    assert "outside-repo" in kinds, kinds


def test_absolute_inside_repo_is_not_reported(tmp_path: Path) -> None:
    """★★ **防假阳性**（**首跑就撞上的那个**）：绝对路径**在仓库根下** ⇒ **通过**。

    实例：`→ 验收: Select-String C:\\swprojects\\sw-skill-fork\\tools\\capture_…py`
    —— 写成绝对形式只是为了 Select-String 方便，**文件在仓库里**。
    """
    r = _repo(tmp_path)
    inside = r / "tools" / "real_tool.py"
    _mk(tmp_path, """
        # X
        `→ 验收:` `Select-String %s -Pattern 'x'`
    """ % str(inside).replace("\\", "\\\\"))
    assert MOD.scan(tmp_path / "specs", r) == [], MOD.scan(tmp_path / "specs", r)


def test_bare_name_not_in_repo_is_reported(tmp_path: Path) -> None:
    """★ **负例②**：裸文件名且仓库里搜不到 ⇒ 报。"""
    _mk(tmp_path, """
        # X
        `→ 验收:` `capability_gap.py` 的模具行
    """)
    r = _repo(tmp_path)
    hits = MOD.scan(tmp_path / "specs", r)
    kinds = {k for _, _, _, probs in hits for k, _, _ in probs}
    assert "bare-not-found" in kinds, kinds


def test_bare_name_in_repo_is_not_reported(tmp_path: Path) -> None:
    """裸文件名但**仓库里搜得到** ⇒ 通过。"""
    _mk(tmp_path, """
        # X
        `→ 验收:` `real_tool.py` 的输出
    """)
    r = _repo(tmp_path)
    assert MOD.scan(tmp_path / "specs", r) == []


def test_prefixed_missing_is_reported(tmp_path: Path) -> None:
    """带仓库目录前缀但**文件不存在** ⇒ 报。"""
    _mk(tmp_path, """
        # X
        `→ 验收:` `python tools\\nonexistent_tool.py`
    """)
    r = _repo(tmp_path)
    hits = MOD.scan(tmp_path / "specs", r)
    kinds = {k for _, _, _, probs in hits for k, _, _ in probs}
    assert "missing-in-repo" in kinds, kinds


def test_non_acceptance_lines_are_ignored(tmp_path: Path) -> None:
    """**只查验收行** —— 正文里提到的仓库外路径不该被报（那不是验收命令）。

    ⚠ 第一版我在这段 docstring **外面**的用例正文里**写了那个标记本身**去描述「没有标记」，
    结果那行**含标记** ⇒ 门禁**正确地**把它当验收行处理 ⇒ 测试失败。
    **⇒ 是测试错了，不是门禁错了**（同 003 converge 里「先读清契约再写负例」那条教训）。
    ⇒ 用例正文**绝不能出现那个标记**，否则这个负例自我否定。
    """
    _mk(tmp_path, """
        # X
        正文里提到 `D:\\AI\\SW\\probe_something.py`，但这一行不是验收行（无标记）。
    """)
    r = _repo(tmp_path)
    assert MOD.scan(tmp_path / "specs", r) == []
