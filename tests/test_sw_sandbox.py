"""★ 沙盒策略的契约与负例（规格 210 · B5-3）：外部路径**复制进来再用副本**，原件一个字节都不动。"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/sw_sandbox.py`（★ `copy-in / run / copy-out` 的策略之家）
#      + `scripts/sw_connect.py` 的 `open_document` 咽喉点 + `tools/sw_guard.py` 的 `_child_env`
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B5-3**。★ 外部评审的判决：
#   ★ 要守的**不是**「输出不落在输入旁边」，而是「**SolidWorks 打开的永远不是原件**」——
#   ★ 出事的根因正是「对**原件路径**直接开了分析」 ⇒ ★ 做法是 `copy-in / run / copy-out` ✓
# 判据:   ★★ `resolve_input`：模式 `enforce` 且路径在沙盒外 ⇒ **复制**并返回副本；
#   ★ 在沙盒内 ⇒ 原样；★ **只读共享来源**（官方源 / 模型素材）⇒ 原样；★ 默认 `passthrough` ⇒ 原样 ✓
#   ★★ 三条负例：**原件必须还在**（复制是加法）· **重名不许覆盖** · **没进程/没文件不许假装成功** ✓
# 官方依据: 无 —— ★ 这是**我方策略**，如实标注，不假托官方 ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sw_sandbox as SB                                        # noqa: E402


@pytest.fixture
def sandboxed(tmp_path, monkeypatch):
    """★ 把沙盒与输出根都指到测试自己的临时目录（★ 不碰仓库、不碰用户文件）✓"""
    monkeypatch.setenv("SW_SANDBOX_MODE", "enforce")
    monkeypatch.setenv("SW_SANDBOX_ROOT", str(tmp_path / "sandbox"))
    monkeypatch.setenv("SW_OUTPUT_ROOT", str(tmp_path / "out" / "run-1"))
    monkeypatch.setenv("SW_RUN_ID", "run-1")
    src = tmp_path / "user_part.sldprt"
    src.write_text("PRETEND-CAD-DATA", encoding="utf-8")
    return {"tmp": tmp_path, "src": src}


# ── ① 默认 passthrough：不改变既有行为 ───────────────────────────────────
def test_default_mode_is_passthrough(sandboxed, monkeypatch):
    monkeypatch.delenv("SW_SANDBOX_MODE")
    assert SB.mode() == "passthrough"
    r = SB.resolve_input(sandboxed["src"])
    assert r["materialized"] is False and str(r["path"]) == str(sandboxed["src"])


# ── ② enforce：沙盒外 ⇒ 复制进来，且**原件不动** ─────────────────────────
def test_external_input_is_copied_into_the_sandbox(sandboxed):
    r = SB.resolve_input(sandboxed["src"])
    assert r["materialized"] is True
    assert r["path"] != str(sandboxed["src"])
    assert SB._inside(r["path"], SB.sandbox_root()), r["path"]
    assert Path(r["path"]).read_text(encoding="utf-8") == "PRETEND-CAD-DATA"


def test_original_file_is_never_touched(sandboxed):
    """★★ **负例**：复制是**加法** —— ★ 原件必须**一个字节都不动**（红线：不删用户数据）✓"""
    before = sandboxed["src"].read_bytes()
    SB.resolve_input(sandboxed["src"])
    assert sandboxed["src"].exists() and sandboxed["src"].read_bytes() == before


def test_same_name_never_overwrites_a_previous_input(sandboxed):
    """★★ **负例**：两次同名不同内容 ⇒ ★ **不许覆盖**（覆盖会毁掉上一次的输入 = 删数据）✓"""
    a = sandboxed["src"]
    r1 = SB.resolve_input(a)
    a.write_text("SECOND-VERSION", encoding="utf-8")     # ★ 用户改了原件，同名
    r2 = SB.resolve_input(a)
    assert r2["path"] != r1["path"], "★ 同名被覆盖了"
    assert Path(r1["path"]).read_text(encoding="utf-8") == "PRETEND-CAD-DATA"


def test_path_inside_sandbox_is_not_copied(sandboxed):
    r = SB.resolve_input(sandboxed["src"])
    again = SB.resolve_input(r["path"])
    assert again["materialized"] is False


def test_readonly_shared_source_is_not_copied(sandboxed):
    """★ 官方源 / 模型素材是**共享只读**的 ⇒ 复制纯浪费，★ 原样用 ✓"""
    r = SB.resolve_input(r"C:\swapi\types\ISldWorks\GetDocuments.md")
    assert r["materialized"] is False and "只读共享来源" in r["why"]


def test_missing_file_is_not_faked(sandboxed):
    """★ 源不存在 ⇒ ★ **不许假装成功**（★ 交给上层报错）✓"""
    r = SB.resolve_input(sandboxed["tmp"] / "nope.sldprt")
    assert r["materialized"] is False and "不存在" in r["why"]


# ── ③ copy-out：结果拷到配置的输出根目录，且**沙盒里那份留下** ──────────
def test_collect_outputs_copies_into_the_configured_output_root(sandboxed):
    r = SB.resolve_input(sandboxed["src"])
    got = SB.collect_outputs([r["path"]], note="测试")
    assert len(got) == 1
    dest = Path(got[0]["copied_to"])
    assert dest.read_text(encoding="utf-8") == "PRETEND-CAD-DATA"
    assert "run-1" in str(dest), dest          # ★ 输出根**带 run id** ⇒ 不重名 ✓
    assert Path(r["path"]).exists(), "★ copy-out 是拷贝，★ 沙盒里那份要留下（便于复查）"


def test_output_root_follows_the_run_id(sandboxed, monkeypatch):
    monkeypatch.setenv("SW_RUN_ID", "another-run")
    monkeypatch.delenv("SW_OUTPUT_ROOT")
    assert "another-run" in str(SB.output_root())


# ── ④ 护栏：给探针子进程打开 enforce ────────────────────────────────────
def test_guard_child_env_enforces_the_sandbox(monkeypatch):
    """★★ 开关放在**护栏**这一层：★ 真机跑被保护，★ 离线调用与单测不受影响 ✓"""
    import sw_guard as G
    monkeypatch.delenv("SW_SANDBOX_MODE", raising=False)
    env = G._child_env()
    assert env["SW_SANDBOX_MODE"] == "enforce"
    assert env["SW_SANDBOX_ROOT"] and env["SW_OUTPUT_ROOT"] and env["SW_RUN_ID"]
    #: ★ 只影响**子进程的环境副本**，★ 不影响本进程（否则会把单测也带进 enforce）✓
    assert os.environ.get("SW_SANDBOX_MODE") is None


def test_model_library_is_not_exempt_from_copy_in():
    """★★★ **回归钉**：★ 模型素材库**不许**进只读豁免名单 ——
    ★★ 因为当初出的事故**正是**「对素材库里的件直接开分析 ⇒ 分析产物落在那个目录里」✗
    ★ 只有 `C:\\swapi` 那种**纯文档源**才可豁免 ✓
    """
    names = [str(p) for p in SB.DEFAULT_READONLY_SOURCES]
    assert any("swapi" in n for n in names), names
    assert not any("AI Solidworks" in n for n in names), \
        "★★ 模型素材库被豁免了 ⇒ 会原样重演「产物写进用户目录」那件事"
    assert len(names) == 1, names
