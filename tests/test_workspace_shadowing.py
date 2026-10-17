"""工作区遮蔽依赖包的守卫（**不连 SolidWorks**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   scripts/check_workspace_shadowing.py
# 定位:   2026-10-01 实测接线时撞上 `D:\\AI\\SW\\mcp.py` 遮蔽真 `mcp` 包
#         ⇒ `server.py` 在该 CWD 下 import 不了。本测试把这条做成可查项。
# 官方签名依据: 不适用（Python 的 `sys.path[0]` 语义）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK = REPO_ROOT / "scripts" / "check_workspace_shadowing.py"
WORKSPACE = Path(Path(__file__).resolve().parents[1])


def _load():
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("ws_shadow", CHECK)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ws_shadow"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_checker_runs_and_reports():
    """检查器必须能跑起来并给出结论（**跑不起来也是问题**）。"""
    if not CHECK.is_file():
        pytest.skip("检查器不在")
    proc = subprocess.run([sys.executable, str(CHECK)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=120,
                          cwd=str(REPO_ROOT), stdin=subprocess.DEVNULL)
    assert proc.stdout.strip(), "检查器没有任何输出"
    assert ("[PASS]" in proc.stdout) or ("[FAIL]" in proc.stdout), proc.stdout[-200:]


def test_checker_detects_a_planted_shadow(tmp_path):
    """**负例**：种一个同名 `mcp.py`，检查器必须报出来。

    ⚠ 与 `tests/test_gate_negative_cases.py` 同一纪律：**先证明工具有牙齿。**
    """
    mod = _load()
    fake_ws = tmp_path / "ws"
    fake_ws.mkdir()
    (fake_ws / "mcp.py").write_text("x = 1\n", encoding="utf-8")
    hits = mod.shadowing(fake_ws, {"mcp", "pydantic"})
    names = {h[0] for h in hits}
    assert "mcp" in names, "**检查器没报出种下的 mcp.py 遮蔽** ⇒ 假门禁"
    assert "pydantic" not in names, "报了不存在的遮蔽物 ⇒ 误报"


def test_checker_passes_on_a_clean_workspace(tmp_path):
    """**正例**：干净目录必须 PASS（否则它会因误报而被忽略）。"""
    mod = _load()
    clean = tmp_path / "clean"
    clean.mkdir()
    assert mod.shadowing(clean, {"mcp", "pydantic"}) == []


def test_known_shadow_is_recorded_with_a_fix_recipe():
    """`mcp.py` 这个**已知**遮蔽物必须在检查器的输出里给出**修法**（不是只报错）。"""
    if not CHECK.is_file():
        pytest.skip("检查器不在")
    text = CHECK.read_text(encoding="utf-8")
    assert "把那些历史脚本移出工作区根" in text or "改名" in text, (
        "检查器只报错、没给修法 ⇒ 用处减半"
    )
    assert "不删任何东西" in text or "**不删**" in text, (
        "检查器必须写明**不自动删**（工作区脚本是历史产物）"
    )
