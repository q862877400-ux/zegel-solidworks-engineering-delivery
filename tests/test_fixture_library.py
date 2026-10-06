"""★ 夹具库的契约与负例（规格 210 · B5-5）：只快照一次、冻结哈希、**测试只认夹具库**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `tools/fixtures.py` + `tools/make_fixture_library.py`
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B5-5**。★ 评审**收回**了「给原目录设 ACL」那条
#   （★ SolidWorks 单进程 ⇒ 拒写会**连用户自己的保存一起堵住**）⇒ ★ 改成：
#   ★★ **夹具只快照一次**（一次性复制 + 冻结哈希），★ 此后**没人再碰原目录** ✓
# 判据:   ★★ 最要紧的一条：**`fixture_path` 只在夹具库内解析，绝不去原目录取** ——
#   ★ 若测试还「顺手」从用户目录拿件，★ 那「没人再碰它」就**不成立**、ACL 的替代也就落空了 ✗
#   ★ 另三条负例：**哈希一变就报污染** · **同名不同哈希不覆盖** · **纯加法（不删清单外的文件）** ✓
# 官方依据: 无 —— ★ 我方策略，如实标注 ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import fixtures as FX                                          # noqa: E402


@pytest.fixture
def lib(tmp_path, monkeypatch):
    """★ 每次测试用**自己的**夹具库与自己的源目录（★ 不碰仓库的库、更不碰用户件）✓"""
    monkeypatch.setenv("SW_FIXTURE_LIBRARY", str(tmp_path / "lib"))
    src = tmp_path / "user_dir"
    src.mkdir()
    (src / "part_a.sldprt").write_text("CAD-A", encoding="utf-8")
    (src / "part_b.SLDASM").write_text("CAD-B", encoding="utf-8")
    (src / "notes.txt").write_text("not-cad", encoding="utf-8")      # ★ 非 CAD ⇒ 不许收
    return {"root": tmp_path / "lib", "src": src}


# ── ① 只收 CAD 件 ────────────────────────────────────────────────────────
def test_collect_sources_only_takes_cad_files(lib):
    names = [p.name for p in FX.collect_sources([lib["src"]])]
    assert names == ["part_a.sldprt", "part_b.SLDASM"], names


# ── ② 快照 + 冻结哈希 ────────────────────────────────────────────────────
def test_build_copies_and_freezes_hashes(lib):
    r = FX.build(FX.collect_sources([lib["src"]]))
    assert len(r["copied"]) == 2
    man = FX.load_manifest()
    assert set(man["files"]) == {"part_a.sldprt", "part_b.SLDASM"}
    assert man["files"]["part_a.sldprt"]["sha256"] == FX.sha256_of(lib["src"] / "part_a.sldprt")
    assert FX.verify()["ok"] is True


def test_build_is_idempotent_on_identical_content(lib):
    """★ 同名同哈希 ⇒ **跳过**（★ 重复跑不产生第二份，也不动已有那份）✓"""
    FX.build(FX.collect_sources([lib["src"]]))
    r2 = FX.build(FX.collect_sources([lib["src"]]))
    assert r2["copied"] == [] and len(r2["skipped"]) == 2


# ── ③ ★★ 最要紧：测试只认夹具库 ─────────────────────────────────────────
def test_fixture_path_never_falls_back_to_the_original_directory(lib):
    """★★★ **负例中的负例**：源件存在于**原目录**、但**没进夹具库** ⇒ `fixture_path` **必须返回 None**。

    ★ 为什么这条是 B5-5 的全部要点：★ 若它会回退到原目录，★ 那「**此后没人再碰原目录**」
      —— 也就是评审**收回 ACL 方案的前提** —— **就不成立了** ✗
    """
    (lib["src"] / "never_copied.sldprt").write_text("X", encoding="utf-8")
    assert FX.fixture_path("never_copied.sldprt") is None
    assert (lib["src"] / "never_copied.sldprt").exists(), "★ 夹具库不该去动原目录"


def test_fixture_path_resolves_inside_the_library(lib):
    FX.build(FX.collect_sources([lib["src"]]))
    got = FX.fixture_path("part_a.sldprt")
    assert got is not None and got.parent == lib["root"], got


# ── ④ 污染与安全负例 ─────────────────────────────────────────────────────
def test_verify_detects_a_contaminated_fixture(lib):
    """★★ **负例**：夹具被改过 ⇒ ★ 必须报出（★ 评审的判据：「哈希一变就不算留出集」）✓"""
    FX.build(FX.collect_sources([lib["src"]]))
    (lib["root"] / "part_a.sldprt").write_text("TAMPERED", encoding="utf-8")
    v = FX.verify()
    assert v["ok"] is False and v["changed"] == ["part_a.sldprt"], v


def test_verify_detects_a_missing_fixture(lib):
    FX.build(FX.collect_sources([lib["src"]]))
    (lib["root"] / "part_b.SLDASM").unlink()
    v = FX.verify()
    assert v["ok"] is False and v["missing"] == ["part_b.SLDASM"], v


def test_same_name_different_content_is_not_overwritten(lib):
    """★★ **负例**：同名不同哈希 ⇒ **换名**，★ 覆盖会毁掉上一次那份夹具 ✓"""
    FX.build(FX.collect_sources([lib["src"]]))
    (lib["src"] / "part_a.sldprt").write_text("CAD-A-V2", encoding="utf-8")
    r = FX.build(FX.collect_sources([lib["src"]]))
    assert r["copied"], r
    assert (lib["root"] / "part_a.sldprt").read_text(encoding="utf-8") == "CAD-A"
    assert FX.verify()["ok"] is True


def test_build_never_deletes_anything(lib):
    """★ **纯加法**：夹具库里清单外的文件**不许被删**（★ 不删数据）✓"""
    FX.build(FX.collect_sources([lib["src"]]))
    extra = lib["root"] / "别的东西.bin"
    extra.write_text("KEEP", encoding="utf-8")
    FX.build(FX.collect_sources([lib["src"]]))
    assert extra.exists() and extra.read_text(encoding="utf-8") == "KEEP"
    assert FX.verify()["extra"] == ["别的东西.bin"], FX.verify()["extra"]
