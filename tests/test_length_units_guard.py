"""★ 判据 —— **单位纪律门禁本身有效**（★ 业主点破的那一层：★ 报告 ≠ 门禁）。

★★★★★ **业主原话**：「★ **既然你明明知道了之前的错误，那为什么你还会把错误原封不动地再犯一次呢？**」✓
  ★★★ **答案不是「我不记得」** —— ★ 是 `scripts/audit_length_units.py` **没有牙齿**：
    · ★ ① **只打印清单**（`return 0` 恒真）⇒ ★ **它是报告，不是门禁** ✗
    · ★ ② **不在 `release_check.py` 里** ⇒ ★ **发布前根本不跑** ✗
    · ★ ③ **只按形参名**判长度 ⇒ ★ 形参叫 `spec`（dict/dataclass）时
      ★★ **长度名藏在字段里** ⇒ 判「无长度形参」⇒ ★ **整族跳过** ✗
      ★★★ **齿轮族正是这样被跳过的** ✓
  ⇒ ★★★ **三条病各有一条判据守**（★ 本文件就是那三条）✓
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   `scripts/check_length_units_guard.py`（★ 门禁）
#         `scripts/audit_length_units.py`（★ 被守的审计器）
#         `scripts/release_check.py`（★ 门禁的接线点）
#         `docs/gate-classification.json`（★ 接线分类登记表）
# 定位:   ★ 守卫「单位纪律门禁**真的在拦**」—— ★ 起因是业主点破「知道了还再犯」。
# 官方依据: 本仓单位纪律（事实 2）：★ 入参毫米 · COM 侧米 ⇒ 进 COM 前必须换算 ✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   只读（★ 纯离线 —— ★ 静态读源码/JSON）
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts" / "check_length_units_guard.py"
AUDIT = ROOT / "scripts" / "audit_length_units.py"
RELEASE = ROOT / "scripts" / "release_check.py"
CLASSIFICATION = ROOT / "docs" / "gate-classification.json"


def test_the_guard_exists_and_has_a_nonzero_exit_path():
    """★★★★★ **门禁必须有**失败路径**（★ 病 ①：★ 报告 ≠ 门禁）。

    ★★ 判据：★ 源码里必须有 `return 1`（★ 报告器会**恒回 0**）✓
    """
    assert GUARD.is_file(), "★★ 门禁脚本不存在"
    src = GUARD.read_text(encoding="utf-8")
    assert "return 1" in src, (
        "★★★ 门禁**没有失败路径** ⇒ ★ 那是**报告**不是门禁（★ 病 ① 复发）")
    assert "return 0" in src, "★ 门禁没有成功路径"


def test_the_guard_is_wired_into_release_check():
    """★★★★★ **门禁必须接进 `release_check`**（★ 病 ②：★ 不接线就永不跑）。

    ★★ 判据：★ `release_check.py` 里必须**调用**它，★ 且**失败时 raise** ✓
    """
    src = RELEASE.read_text(encoding="utf-8")
    assert "_run_length_units_gate" in src, (
        "★★★ 门禁**没接进 release_check** ⇒ ★ 发布前不跑（★ 病 ② 复发）")
    assert "length_units" in src, "★★ 结果没登记进返回值（★ 元门禁会拦）"
    #: ★★ 且**必须有拦**（★ 不是只记）
    #:   ⚠ 第一版用 `src.find("_run_length_units_gate()")` ⇒ ★ 命中的是**函数定义行**
    #:     （`def _run_length_units_gate() -> …`）⇒ ★ **假红**（★ 本判据自己抓出来的）✗
    #:   ★★ 正解：★ 找**赋值调用**那个形态（`= _run_length_units_gate()`）✓
    i = src.find("= _run_length_units_gate()")
    assert i > 0, "★ 没找到**调用点**（★ 只找到定义）"
    tail = src[i:i + 600]
    assert "raise AssertionError" in tail, (
        "★★★ 调用了但**没拦** ⇒ ★ 那还是报告（★ 病 ① 复发）：%s" % tail[:200])


def test_the_gate_is_classified_in_the_registry():
    """★★★★ **必须登记分类**（★ 元门禁 `check_gate_wiring` 的要求）。

    ★★ 实证：★ 我第一版**漏登记** ⇒ ★ **元门禁当场拦住**（★ `[FAIL] 接线方式有问题`）✓

    ★★ 2026-10-12 更新（★ 规格 324 · Q16）：★ `kind` **扩到四类** ——
      ★ 旧名 `hard` **映射到** `release_static`（★ `LEGACY_KIND_MAP`）。
      ★ 判据不变（**拦发布**），★ 只是**名字换了**。
    """
    d = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
    runners = {e.get("runner") for e in d.get("classification", [])}
    assert "_run_length_units_gate" in runners, (
        "★★★ 没在 `docs/gate-classification.json` 登记 ⇒ ★ `check_gate_wiring` 会红")
    entry = next(e for e in d["classification"]
                 if e.get("runner") == "_run_length_units_gate")
    #: ★★ Q16 四类里，「拦发布」的那一类现在叫 `release_static`
    #:   （★ 旧名 `hard` 也收 —— ★ 向后兼容）
    assert entry.get("kind") in ("release_static", "hard"), (
        "★★ 应登记为 `release_static`（★ 旧名 `hard`）—— ★ 而不是 `diagnostic`")


def test_the_audit_sees_through_a_speclike_parameter():
    """★★★★★ **审计器要能看穿「长度藏在对象里」**（★ 病 ③：★ 整族跳过）。

    ★★ 判据：★ `audit_length_units.py` 必须有**跟一层调用**的机制
      （★ 因为 `create_external_spur_gear_report(model, spec, …)` 的 `spec` 无注解、
      ★ 函数体里也不直接写 `spec.face_width_mm` —— ★ 它**转交**给下游）✓
    ★★★ **红基线已验**：★ 去掉那一步 ⇒ ★ 齿轮从视野里消失 ⇒ ★ **门禁红**（99 < 100）✓
    """
    src = AUDIT.read_text(encoding="utf-8")
    assert "_lengthish_from_callees" in src, (
        "★★★ 审计器没有「跟一层调用」⇒ ★ 形参叫 `spec` 的族会被**整族跳过**（★ 病 ③）")
    assert "SPECLIKE_PARAM" in src, "★★ 没有「像规格对象的形参名」那个判据"


def test_the_guard_actually_passes_on_the_current_tree():
    """★★★ **门禁在当前树上必须绿**（★ 否则它自己就是新的红）。

    ★★ 用**显式解释器**跑（★ 与 `release_check` 同法）✓
    """
    proc = subprocess.run(
        [sys.executable, str(GUARD)], check=False, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=300, cwd=str(ROOT),
        stdin=subprocess.DEVNULL)
    assert proc.returncode == 0, (
        "★★ 门禁在当前树上**红的**：\n%s" % ((proc.stdout or "")[-800:]))


def test_the_guard_has_a_speclike_regression_assertion():
    """★★★★★ **「长度藏在 spec 里」那一族必须仍被守** —— ★ 单列的回归守卫。

    ★★★ **为什么单列**：★ 业主点破的**正是**「那一族被跳过」——
      ★★ 所以「审计器看得穿 `spec`」这件事**本身**要成为判据，
      ★ 否则下次改审计器时又会把它漏掉（★ 与**事实 62**「门禁写了 ≠ 有效」同族）✓

    ★★ **2026-10-10 改判（★ 如实）**：★ 齿轮**工具**已按业主架构指令移出
      （★ 它是方法）⇒ ★ 不能再要求「`solidworks_gear_create_spur` 在工具面上」✗
      ★★★ **改为按**机制**断言**：★ 审计器必须有「跟一层调用」与「像规格对象的形参名」
        ⇒ ★ **只要那两个机制在，那一族就不会被整族跳过** ✓
    """
    guard = GUARD.read_text(encoding="utf-8")
    audit = AUDIT.read_text(encoding="utf-8")
    assert "_lengthish_from_callees" in audit, (
        "★★★ 审计器没有「跟一层调用」⇒ ★ 形参叫 `spec` 的族会被**整族跳过**")
    assert "SPECLIKE_PARAM" in audit, "★★ 没有「像规格对象的形参名」判据"
    #: ★★ 且**门禁必须断言**这件事（★ 不能只写在审计器里）
    assert "_lengthish_from_callees" in guard, (
        "★★★ 门禁**没有断言**那处盲区仍被守 ⇒ ★ 它可以悄悄回来")
