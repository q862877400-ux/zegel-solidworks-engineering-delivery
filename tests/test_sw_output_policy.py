"""★ 产品模式的契约与负例（规格 210 · B5-4）：产物进**命名子目录**、路径**写进返回值**、**绝不覆盖**。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_sandbox.py` 的 `policy` / `product_output_dir` / `snapshot_dir` /
#      `new_since` / `tidy_outputs` / `output_report`
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B5-4**。★ 业主已拍板：
#   ★ 产品模式（用户让智能体改**他自己的**模型）下，★ **分析类产物默认进一个明确命名的子目录**，
#   ★ 并在**工具返回值里报出实际路径**，★ 不再静默落在零件旁边 ✓
# 判据:   ⚠ **必须说清的限度**：★ 分析产物的**落点是 SolidWorks 自己决定的**，那一步**不经过我们的调用**
#   （评审确认：「内部写不经过你们的调用，所以应用层守卫对它无效」）⇒
#   ★★ 所以本批**不假装能控制它**，★ 只保证「**产物有名字、有去处、能被报出来**」✓
#   ★ 三条安全负例：**只搬点名的那些**（不做目录级清理）· **目标已存在不覆盖** · **搬不动如实报** ✓
# 官方依据: 无 —— ★ 这是**我方策略**，如实标注，不假托官方 ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_sandbox as SB                                        # noqa: E402


@pytest.fixture
def product_mode(tmp_path, monkeypatch):
    """★ 产品模式：一个「用户的零件」目录（★ 测试自己的临时目录，不碰仓库、不碰用户文件）✓"""
    monkeypatch.setenv("SW_OUTPUT_POLICY", "product")
    doc_dir = tmp_path / "user_design"
    doc_dir.mkdir()
    doc = doc_dir / "part_a.sldprt"
    doc.write_text("CAD", encoding="utf-8")
    return {"dir": doc_dir, "doc": doc}


# ── ① 子目录命名与策略开关 ────────────────────────────────────────────────
def test_default_policy_is_sandbox(monkeypatch):
    monkeypatch.delenv("SW_OUTPUT_POLICY", raising=False)
    assert SB.policy() == SB.POLICY_SANDBOX


def test_product_output_dir_is_explicitly_named(product_mode):
    """★ 名字**必须明确**（含零件名）—— ★ 不能散落在零件旁边（那正是当初出事的样子）✓"""
    d = SB.product_output_dir(product_mode["doc"])
    assert d.name == "part_a_MCP_output"
    assert d.parent == product_mode["dir"]


# ── ② 检测「跑完多了什么」（★ 这是唯一可靠的办法：拦不住，但看得见）─────────
def test_snapshot_is_read_only(product_mode):
    """★ 拍快照**不许改任何东西**（★ 它只是读）✓"""
    before = SB.snapshot_dir(product_mode["dir"])
    after = SB.snapshot_dir(product_mode["dir"])
    assert before == after and len(before) == 1


def test_new_since_detects_files_solidworks_wrote_beside_the_part(product_mode):
    """★★ 模拟「SolidWorks 自己往零件旁边写结果文件」 ⇒ ★ 必须**被检测出来** ✓"""
    before = SB.snapshot_dir(product_mode["dir"])
    (product_mode["dir"] / "part_a-静应力分析.CWR").write_text("RESULT", encoding="utf-8")
    found = SB.new_since(before, product_mode["dir"])
    assert any(p.endswith("part_a-静应力分析.CWR") for p in found), found


# ── ③ 搬进子目录，且路径**写进返回值** ───────────────────────────────────
def test_tidy_moves_products_into_the_named_subdir(product_mode):
    stray = product_mode["dir"] / "part_a-静应力分析.CWR"
    stray.write_text("RESULT", encoding="utf-8")
    tidy = SB.tidy_outputs([stray], product_mode["doc"])
    assert tidy["moved"] and len(tidy["moved"]) == 1
    moved_to = Path(tidy["moved"][0]["to"])
    assert moved_to.parent.name == "part_a_MCP_output"
    assert moved_to.read_text(encoding="utf-8") == "RESULT"
    assert not stray.exists(), "★ 搬走之后原位置不该再留着"


def test_output_report_carries_the_real_paths(product_mode):
    """★★ 判据：**返回值里必须有产物的实际路径**（★ 业主拍板的那一条）✓"""
    stray = product_mode["dir"] / "part_a-静摩擦.CWR"
    stray.write_text("R", encoding="utf-8")
    rep = SB.output_report(product_mode["doc"], [stray], run_id_value="run-9")
    assert rep["policy"] == "product" and rep["run_id"] == "run-9"
    assert rep["files"] and all(Path(p).is_absolute() for p in rep["files"])
    assert any("part_a_MCP_output" in p for p in rep["files"]), rep["files"]


def test_sandbox_mode_report_points_at_the_output_root(product_mode, monkeypatch):
    monkeypatch.setenv("SW_OUTPUT_POLICY", "sandbox")
    monkeypatch.setenv("SW_OUTPUT_ROOT", str(product_mode["dir"] / "outroot"))
    rep = SB.output_report(product_mode["doc"], [])
    assert rep["policy"] == "sandbox" and rep["output_dir"].endswith("outroot")


# ── ④ 安全负例 ────────────────────────────────────────────────────────────
def test_tidy_never_overwrites_an_existing_product(product_mode):
    """★★ **负例**：同名产物已存在于子目录 ⇒ ★ **不许覆盖**（覆盖会毁掉上一次的产物）✓"""
    dest_dir = SB.product_output_dir(product_mode["doc"])
    dest_dir.mkdir()
    (dest_dir / "x.CWR").write_text("FIRST", encoding="utf-8")
    stray = product_mode["dir"] / "x.CWR"
    stray.write_text("SECOND", encoding="utf-8")
    tidy = SB.tidy_outputs([stray], product_mode["doc"])
    assert len(tidy["moved"]) == 1
    assert (dest_dir / "x.CWR").read_text(encoding="utf-8") == "FIRST", "★ 旧产物被覆盖了"
    assert Path(tidy["moved"][0]["to"]).name != "x.CWR"


def test_tidy_only_touches_the_named_files(product_mode):
    """★★ **负例**：★ 只搬**调用方点名**的那些 ⇒ ★ 旁边别的文件**一个都不许动** ✓"""
    keep1 = product_mode["dir"] / "重要-用户自己的件.sldprt"
    keep1.write_text("USER", encoding="utf-8")
    stray = product_mode["dir"] / "a.CWR"
    stray.write_text("R", encoding="utf-8")
    SB.tidy_outputs([stray], product_mode["doc"])
    assert keep1.exists() and keep1.read_text(encoding="utf-8") == "USER"
    assert product_mode["doc"].exists(), "★ 零件本体也不许动"


def test_tidy_reports_unmovable_files_instead_of_faking_success(product_mode):
    """★ 不存在的路径 ⇒ ★ **记进 `skipped` 并如实报出**，★ 不假装成功 ✓"""
    tidy = SB.tidy_outputs([product_mode["dir"] / "nope.CWR"], product_mode["doc"])
    assert tidy["moved"] == [] and len(tidy["skipped"]) == 1
    assert "不是文件" in tidy["skipped"][0]["why"]


def test_guard_reports_files_that_appeared_during_the_run(tmp_path, monkeypatch):
    """★★ 护栏跑完必须**报出「多出来什么」** —— ★ 这就是「拦不住它写、但看得见它写了什么」✓

    ★ 并顺手钉住一个**我自己引入过的回归**：★ `sandbox_before` 曾被写在 `run_guarded` 里、
      却在 `main` 里用 ⇒ ★ **每次跑完护栏都 NameError 崩掉**（退出码 1）✗
      ⇒ ★ 所以这条测试直接从 `main` 的那条路径上取助手来用 ✓
    """
    import sw_guard as G
    monkeypatch.setenv("SW_SANDBOX_ROOT", str(tmp_path / "sb"))
    monkeypatch.setenv("SW_OUTPUT_ROOT", str(tmp_path / "out"))
    before = G.snapshot_sandbox()
    (tmp_path / "sb" / "inputs").mkdir(parents=True)
    (tmp_path / "sb" / "inputs" / "part-分析.CWR").write_text("R", encoding="utf-8")
    got = G.collect_sandbox_outputs(before)
    assert len(got["appeared"]) == 1 and got["appeared"][0].endswith("part-分析.CWR"), got
    assert len(got["copied"]) == 1 and got["output_root"].startswith(str(tmp_path / "out"))
