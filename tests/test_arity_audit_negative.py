"""判据有效性测试：`audit_call_arity.py` 必须抓得住那个固化的负例。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_arity_audit_negative.py
# 定位:   已知事实 62 ——「一个门禁『写了』不等于它『有效』，负例测试是唯一的证明」。
#         批次 6/7 的负例住在 `%TEMP%` 里（**不可复现**）⇒ 轮 123 固化进
#         `tools/arity_negative_case.py` 并在这里钉住。
# 官方依据: 出厂反射 `iface_*.txt`
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT = REPO_ROOT / "scripts" / "audit_call_arity.py"
NEG = REPO_ROOT / "tools" / "arity_negative_case.py"
RAW = Path(Path(__file__).resolve().parents[1] / "_raw")


def _refs() -> list:
    return [str(p) for p in RAW.rglob("iface_*.txt")]


@pytest.fixture(scope="module")
def audit_output() -> str:
    refs = _refs()
    if not refs:
        pytest.skip("没有反射转储（D:\\AI\\SW\\_raw\\**\\iface_*.txt）⇒ 跳过")
    if not NEG.is_file():
        pytest.skip("负例文件不在")
    # ⚠ 必须给 encoding（事实 58：中文 Windows 上父进程默认 GBK 会炸）
    cp = subprocess.run([sys.executable, str(AUDIT), str(NEG), *refs],
                        capture_output=True, text=True,
                        encoding="utf-8", errors="replace", cwd=str(REPO_ROOT))
    return (cp.stdout or "") + (cp.stderr or "")


def test_negative_case_is_git_tracked_not_in_temp():
    """@brief 负例必须**在仓库里**（不能住在 `%TEMP%` 里 ⇒ 否则不可复现）。"""
    assert NEG.is_file(), "负例文件必须固化进仓库"
    assert "Temp" not in str(NEG) and "TEMP" not in str(NEG)


def test_audit_flags_the_arity_mismatches(audit_output):
    """@brief 两个 arity 不符的调用必须被报出来（少传 / 多传各一）。"""
    assert "CreateNewStudy3" in audit_output, audit_output[:800]
    assert "arity=4" in audit_output, "少传那个应报「官方 arity=4」"
    assert "InsertWeldmentFeature" in audit_output, audit_output[:800]
    assert "arity=0" in audit_output, "多传那个应报「官方 arity=0」"


def test_audit_flags_the_unknown_member(audit_output):
    """@brief 成员名不存在必须报「查不到」。"""
    assert "TotallyBogusMemberName" in audit_output, audit_output[:800]
    assert re.search(r"查不到", audit_output), audit_output[:800]


def test_negative_case_itself_declares_it_is_deliberately_wrong():
    """@brief 负例文件必须**自己写明**"故意写错、不要照抄"（否则会被当成活代码改掉）。"""
    t = NEG.read_text(encoding="utf-8")
    assert "故意" in t
    assert "不要照抄" in t or "不要修好它" in t


def test_arity_rule_counts_all_reflection_params():
    """@brief ★ 轮 123 的修正：arity **就是反射里的参数个数**，不做 by-ref 类型特例。

    来历：真机实验（`tools/probe_outparam_object_byref.py`）证明
    `Object&` 出参**是必填的** ⇒ 旧规则「`Object&` / `Variant&` / `Dispatch&` 一律排除」是错的。
    ⚠ 谁把特例加回来，这条会红。
    """
    t = AUDIT.read_text(encoding="utf-8")
    assert "count = len(_params)" in t, "arity 口径必须是『反射参数个数』"
    assert "_is_required_out" not in t.split("# ── 来源")[-1], "旧的特例函数不该回到实现里"
    assert "非选择性的参数" in t, "来源要写明真机裁断的依据"
