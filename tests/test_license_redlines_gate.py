"""@brief A6 许可红线门禁的契约测试（**含负例**）。

# ── 来源 ──
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_license_redlines_gate.py
# 定位:   给 `scripts/check_license_redlines.py`（轮 57 新增的**门禁**）补契约测试。
#         ⚠ 按本仓库纪律：**门禁必须有负例**（「一个存在但没人用的守卫与没有守卫等价」）。
#         依据是 `AGENTS.md §二 铁律 6` 的许可表（AGPL/GPL/无许可/全版权保留 = 只读思想）。
# 官方签名依据: 不适用（纯静态：读来源块 + 查文件存在性，**不连 SolidWorks**）
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
        "check_license_redlines", ROOT / "scripts" / "check_license_redlines.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_license_redlines"] = mod
    spec.loader.exec_module(mod)
    return mod


MOD = _load()


def _w(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "m.py"
    p.write_text(textwrap.dedent(body).lstrip(), encoding="utf-8")
    return p


def test_current_tree_passes() -> None:
    """★ 当前仓库应 0 越界（否则门禁该红）。"""
    assert MOD.main(["--repo", str(ROOT)]) == 0


def test_third_party_with_mit_passes(tmp_path: Path) -> None:
    """点名第三方 + 许可写 MIT ⇒ 通过。"""
    p = _w(tmp_path, """
        # 仓库:   microsoft/UFO  (MIT License, Copyright (c) Microsoft Corporation)
        # 许可:   MIT（UFO）· 本仓库 MIT（本文件原创）
    """)
    assert MOD.scan_file(p) == []


def test_third_party_without_allowed_license_is_reported(tmp_path: Path) -> None:
    """★ **负例①**：点名第三方，而许可里**没有任何白名单词** ⇒ 报。

    ⚠ 我第一版把这个负例写成「许可: 本仓库 MIT」，**测试失败了 —— 而且是测试错**：
    「本仓库 MIT」**本身就含 `MIT`** ⇒ 门禁（正确地）放行。
    ⇒ 负例必须用**确实不含**白名单词的措辞（如「未声明」）。
    """
    p = _w(tmp_path, """
        # 仓库:   microsoft/UFO
        # 许可:   未声明
    """)
    probs = MOD.scan_file(p)
    kinds = {k for k, _ in probs}
    assert "third-party-without-allowed-license" in kinds, probs


def test_apache_source_must_say_apache(tmp_path: Path) -> None:
    """★★ **负例①b（本门禁最有价值的那条）**：来源是 Apache-2.0，而许可只写「本仓库 MIT」⇒ 报。

    ⚠ 这条是**实测逼出来的**：第一版只判「有没有白名单词」，而「本仓库 MIT」含 `MIT`
    ⇒ 「来源 `Slacker-LLC`（Apache-2.0）／许可 本仓库 MIT」被**误判为通过**，
    漏掉的正是**唯一带 NOTICE 硬义务**的那一档。**这是假阴性，且漏在最要命处。**
    """
    p = _w(tmp_path, """
        # 仓库:   Slacker-LLC/solidworks-mcp
        # 许可:   本仓库 MIT；来源 MIT，版权声明见 THIRD-PARTY-NOTICES.md。
    """)
    kinds = {k for k, _ in MOD.scan_file(p)}
    assert "apache-source-without-apache-notice-line" in kinds, MOD.scan_file(p)


def test_apache_source_with_apache_line_passes(tmp_path: Path) -> None:
    """来源是 Apache-2.0 且许可**明写 Apache** ⇒ 通过。"""
    p = _w(tmp_path, """
        # 仓库:   Slacker-LLC/solidworks-mcp
        # 许可:   Apache-2.0（来源）· 本仓库 MIT（本文件原创）；NOTICE 见 THIRD-PARTY-NOTICES.md
    """)
    assert MOD.scan_file(p) == []


def test_agpl_claimed_as_source_is_reported(tmp_path: Path) -> None:
    """★ **负例②**：把 AGPL 当作来源许可 ⇒ 报（铁律 6：AGPL 只读思想）。"""
    p = _w(tmp_path, """
        # 仓库:   某 AGPL 项目
        # 许可:   AGPL-3.0
    """)
    probs = MOD.scan_file(p)
    kinds = {k for k, _ in probs}
    assert "forbidden-license-claimed" in kinds, probs


def test_no_license_and_all_rights_reserved_are_reported(tmp_path: Path) -> None:
    """★ **负例③**：无许可 / 全版权保留 也是禁类。"""
    for claim in ("无许可", "全版权保留", "All rights reserved", "专有"):
        p = _w(tmp_path, """
            # 仓库:   某个项目
            # 许可:   %s
        """ % claim)
        kinds = {k for k, _ in MOD.scan_file(p)}
        assert "forbidden-license-claimed" in kinds, (claim, MOD.scan_file(p))


def test_project_own_blocks_are_not_flagged(tmp_path: Path) -> None:
    """本项目自身 / 官方 API 签名的来源块**不该**被报（它们不是第三方）。"""
    p = _w(tmp_path, """
        # 仓库:   本项目自身（本任务新增的能力层）
        # 许可:   本仓库 MIT。无第三方代码引入。
        # 仓库:   SolidWorks 官方 API 签名（sldworks.dll 纯元数据反射）
        # 许可:   本仓库 MIT。无第三方代码引入。
    """)
    assert MOD.scan_file(p) == []


def test_source_blocks_are_paired_in_order(tmp_path: Path) -> None:
    """⚠ 一个文件可以有**多对**来源块 ⇒ 要按顺序配对（本项目确有这种文件）。"""
    p = _w(tmp_path, """
        # 仓库:   microsoft/UFO (MIT)
        # 许可:   MIT
        # 仓库:   本项目自身
        # 许可:   本仓库 MIT。无第三方代码引入。
    """)
    blocks = MOD.source_blocks(p)
    assert len(blocks) == 2, blocks


def test_apache_without_notices_is_reported(tmp_path: Path, monkeypatch) -> None:
    """★ **负例④**：声明 Apache-2.0 而 `THIRD-PARTY-NOTICES.md` 不在 ⇒ 报。

    ⚠ 用 `monkeypatch` 换掉 `NOTICES` 与扫描目录，**在假仓库上跑**（不碰真仓库）。
    """
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "m.py").write_text(
        "# 仓库:   microsoft/UFO\n# 许可:   Apache-2.0\n", encoding="utf-8")
    monkeypatch.setattr(MOD, "NOTICES", repo / "THIRD-PARTY-NOTICES.md")
    assert MOD.main(["--repo", str(repo)]) == 1


def test_apache_with_notices_passes(tmp_path: Path, monkeypatch) -> None:
    """声明 Apache-2.0 且 `THIRD-PARTY-NOTICES.md` 在 ⇒ 通过。"""
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "m.py").write_text(
        "# 仓库:   microsoft/UFO\n# 许可:   Apache-2.0\n", encoding="utf-8")
    (repo / "THIRD-PARTY-NOTICES.md").write_text("# Third-Party Notices\n", encoding="utf-8")
    monkeypatch.setattr(MOD, "NOTICES", repo / "THIRD-PARTY-NOTICES.md")
    assert MOD.main(["--repo", str(repo)]) == 0
