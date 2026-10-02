"""钉住「门禁/工具里有没有**定义了却从没被调用**的函数」（死守卫的**函数形态**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_no_uncalled_helpers.py
# 定位:   轮 136：`053`/`054` 扫的是**常量**形态的死守卫（规则 2 的两半）；
#         本文件管**函数**形态 —— 门禁/工具模块里定义了却全仓库没人调的辅助函数。
#         ⚑ 已知事实 61 的定则④就说过这类事：
#         「写了一个好用的工具函数，就要在**所有**同类场合用它，别只用在门禁里」。
# 官方依据: 不适用（本项目内部纪律）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))

import probe_uncalled_helpers as probe          # noqa: E402

#: ⚑⚑ **显式豁免**：这些函数「全仓库没人调」是**有理由的**（每条写清为什么）。
#: ⚠ 照 `MANUAL_MAP` / `COMTYPES_CALL_SITES` / `_LEN_SUFFIX_EXEMPT` 的先例：
#: **每条都要写清"为什么它不属于这一条"**，没依据的不许进来。
UNCALLED_EXEMPT: dict[str, str] = {}


def _suspects() -> list:
    """调**探针自己的** `find_uncalled`（不重写逻辑 —— 否则测的不是工具）。"""
    _checked, suspects = probe.find_uncalled()
    return [s for s in suspects if s[2] not in UNCALLED_EXEMPT]


def test_no_uncalled_helpers_in_gates_and_tools():
    """@brief ★★ 门禁/工具里**不该有**"定义了却全仓库没人调"的函数。

    ⚠ 判据是**有界**的：只看 `scripts/check_*` / `audit_*` / `gen_*` 与 `tools/*`，
    且排除入口点（`main` / `register` / `run`）。

    ⚑ 本轮（136）扫 **164 个函数**，命中 **1 个** —— 而那个**是真的死代码**
    （`tools/propose_capability_sources.py::match_modules`，是 `stems_only()` 的**旧版**、
    会**扫文件体**、被取代后一直留着）⇒ 已删除并留墓碑注释。
    ⚠⚠ **样本只有 n=1** ⇒ "假阳性 0%" **不足以**把它升成硬门禁 ⇒ **先留在这里当回归**；
    将来样本多了再考虑接进 `release_check`。
    """
    got = _suspects()
    assert not got, (
        "门禁/工具里有**从没被调用**的函数（死守卫的函数形态）：\n  %s\n"
        "⇒ 要么删掉（并留墓碑注释），要么加进 `UNCALLED_EXEMPT` **并写明理由**。"
        % "\n  ".join("%s L%d %s" % t for t in got))


def test_the_exemption_table_is_reasoned_if_used():
    """@brief 豁免表的每条都要有理由（空表合法）。"""
    for name, reason in UNCALLED_EXEMPT.items():
        assert len(str(reason)) > 30, "%s 的理由太短" % name


def test_probe_flags_a_deliberately_dead_function(tmp_path, monkeypatch):
    """@brief ★★ **负例**（事实 62）：往 `tools/` 里塞一个死函数 ⇒ 探针**必须**报它。

    ⚠ 用 `monkeypatch` 把 `ROOT` 指到临时目录，**不碰真仓库**。
    """
    fake = tmp_path / "tools"
    fake.mkdir()
    (fake / "check_fake.py").write_text(
        "def totally_uncalled_helper():\n"
        "    return 1\n"
        "\n"
        "\n"
        "def main():\n"
        "    return 0\n",
        encoding="utf-8")
    monkeypatch.setattr(probe, "ROOT", tmp_path)
    monkeypatch.setattr(probe, "SEARCH_DIRS", ("tools",))
    monkeypatch.setattr(probe, "PATTERNS", ("tools/check_*.py",))

    names = [n for _f, _ln, n in _fake_suspects(tmp_path)]
    assert "totally_uncalled_helper" in names, names
    assert "main" not in names, "入口点不该被报"


def _fake_suspects(root: Path) -> list:
    """在**指定的 root** 上跑**同一个** `find_uncalled`（给负例用）。"""
    _checked, suspects = probe.find_uncalled(
        root, search_dirs=("tools",), patterns=("tools/check_*.py",))
    return list(suspects)
