"""★ 判据前置门禁的**负例自证**（事实 62：一个门禁"写了"不等于它"有效"）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（测试）
# 文件:   tests/test_judge_preflight_gate.py
# 定位:   ★ 2026-10-03（轮 420）`specs/150-judge-first-rollout/spec.md` 的 **T0.2 验收**：
#   ★★ 「脚本能跑出 exit 0/1，★ 且**对"缺登记"的情形真的会红**（★ 用负例自证 —— **事实 62** 的手法）」。
#   ★★ 为什么非要负例：★ 本仓事实 62 明写 —— ★ **「一个门禁『写了』不等于它『有效』，
#     负例测试是唯一的证明」**；★ 而那一轮的实例是门禁**第一版抓不到真 bug 的形态**。
#   ⇒ ★ 本测试拿**故意坏的**登记表去跑 `tools/check_judge_preflight.py`，★ 逐条断言它会红。
#   ★ 用法：`DSL_JUDGE_REGISTRY` 环境变量把登记表指向临时文件（★ 因此本测试**不碰真表**）。
# 官方依据: 不适用（本仓自有的判据纪律）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "tools" / "check_judge_preflight.py"
#: ★ 真实存在的一份 pass 证据与一份非 pass 证据（★ 从工作区取；不在则跳过该例）
WORKSPACE = Path(os.environ.get("DSL_WORKSPACE", Path(__file__).resolve().parents[1]))
PASS_EV = "output/loads-groupa3-evidence.json"
NONPASS_EV = "output/first-load-rule-evidence.json"


def _run_with(registry: dict) -> subprocess.CompletedProcess:
    """★ 用一张**临时**登记表跑检查器（★ 不碰真表）。"""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "judge-registry.json"
        path.write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
        env = dict(os.environ, DSL_JUDGE_REGISTRY=str(path))
        return subprocess.run([sys.executable, str(CHECKER)], check=False,
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", env=env, cwd=str(REPO_ROOT), timeout=120)


def _judge(**over) -> dict:
    base = {"id": "j", "kind": "judge", "what": "w", "where": "where",
            "known_good_scenario": "tools/prove_loads_groupa3.py",
            "evidence": PASS_EV, "usable_on": ["x"]}
    base.update(over)
    return base


def _has_pass_evidence() -> bool:
    return (WORKSPACE / PASS_EV).is_file() and (WORKSPACE / NONPASS_EV).is_file()


def test_real_registry_is_green() -> None:
    """★ 正向：**真的**登记表必须绿（★ 否则本测试自身没意义）。"""
    proc = subprocess.run([sys.executable, str(CHECKER)], check=False,
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", cwd=str(REPO_ROOT), timeout=120)
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_missing_field_turns_red() -> None:
    """★ 负例①：`judge` **缺** `known_good_scenario` ⇒ 必须红。"""
    proc = _run_with({"judges": [_judge(known_good_scenario="")]})
    assert proc.returncode == 1, proc.stdout
    assert "缺字段" in proc.stdout


def test_judge_with_nonpass_evidence_turns_red() -> None:
    """★ 负例②：`judge` 的证据**不是** pass ⇒ 必须红（★ 那正是"没真验过"）。"""
    if not _has_pass_evidence():
        return                                            #: ★ 数据源不可达 ⇒ 跳过（便携性）
    proc = _run_with({"judges": [_judge(evidence=NONPASS_EV)]})
    assert proc.returncode == 1, proc.stdout
    assert "不是 pass" in proc.stdout


def test_refuted_with_pass_evidence_turns_red() -> None:
    """★ 负例③：`refuted`（被否的假设）的证据**却是** pass ⇒ 必须红（★ 自相矛盾）。"""
    if not _has_pass_evidence():
        return
    proc = _run_with({"judges": [_judge(kind="refuted", known_good_scenario="", evidence=PASS_EV)]})
    assert proc.returncode == 1, proc.stdout
    assert "不该是 pass" in proc.stdout


def test_missing_evidence_file_turns_red() -> None:
    """★ 负例④：`evidence` **文件不存在** ⇒ 必须红（★ "已知成功"不能是空话）。"""
    proc = _run_with({"judges": [_judge(evidence="output/__no_such_evidence__.json")]})
    assert proc.returncode == 1, proc.stdout
    assert "不存在" in proc.stdout


def test_no_usability_note_turns_red() -> None:
    """★ 负例⑤：`usable_on` 与 `unusable_on` **都空** ⇒ 必须红（★ 那条登记没有信息量）。"""
    proc = _run_with({"judges": [_judge(usable_on=[])]})
    assert proc.returncode == 1, proc.stdout
    assert "缺说明" in proc.stdout
