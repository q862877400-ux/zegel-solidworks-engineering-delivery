r"""★ 判据：两道门禁的**边界必须可见**（spec 223 / US2）。

背景：
  · F2 —— `scripts/check_undefined_names.py` 对整文件**静默跳过**，从不报「跳过了谁」。
    本轮实测静默跳过 **7** 个文件，含 `scripts/sw_part.py`（★ 222 那个
    `from typing import Any` 致命缺陷**正藏在它的跳过里**）。
  · F3 —— `scripts/check_enum_values_vs_reflection.py` 只 glob `scripts/sw_*.py`，
    且要求小写键 + `# swXxx` 注释 ⇒ **边界外的表静默不报**
    （★ F1 那两张伪造表正是这样漏过的）。

判据只锁**可见性**，不改判定强度：两道门禁的**退出码都不许变**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_gate_boundary_transparency.py —— 本文件自身
# 定位:   spec 223 US2 的判据；被测对象是两道门禁脚本的**输出**。
# 官方依据: 不适用（本项目自身门禁的契约）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import io
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
PY = sys.executable

OLD_GLOB_FILES = len(list(SCRIPTS.glob("sw_*.py")))


def _run(script: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PY, "-B", str(SCRIPTS / script)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(REPO_ROOT), stdin=subprocess.DEVNULL, timeout=300,
    )


# ── FR-010：未定义名门禁必须报告「跳过了谁」──────────────────────────

def test_undefined_names_gate_reports_skipped_files():
    proc = _run("check_undefined_names.py")
    out = proc.stdout
    m = re.search(r"跳过\s*\*\*(\d+)\*\*\s*个文件", out)
    assert m, (
        "门禁没有报告「跳过」段 ⇒ 静默跳过 = 看不见的豁免\n--- stdout ---\n%s" % out)
    n = int(m.group(1))
    assert n > 0, "本仓实测应跳过 7 个文件（`globals()` 注入族），不该是 0"
    details = re.findall(
        r"^\s+(star-import|globals-update|globals-subscript)\s+(\S+\.py)\s*$", out, re.M)
    assert len(details) == n, (
        "跳过计数 %d 与明细行 %d 不一致 ⇒ 报告不完整" % (n, len(details)))
    files = {f for _reason, f in details}
    assert any(f.endswith("scripts/sw_part.py") for f in files), (
        "`scripts/sw_part.py` 必须被列出 —— 222 的致命缺陷正藏在它的跳过里\n实际：%s"
        % sorted(files))


def test_undefined_names_gate_exit_code_unchanged():
    """★ 跳过**不是失败** ⇒ 退出码必须仍是 0（要的是可见，不是判罪）。"""
    assert _run("check_undefined_names.py").returncode == 0


# ── FR-011 / FR-012：枚举值门禁必须打印覆盖清单 ──────────────────────

def test_enum_gate_reports_coverage_inventory():
    proc = _run("check_enum_values_vs_reflection.py")
    out = proc.stdout
    m = re.search(
        r"覆盖清单[^\n]*扫描\s*\*\*(\d+)\*\*\s*个文件[^\n]*模块级整数表\s*\*\*(\d+)\*\*\s*张"
        r"[^\n]*已覆盖\s*\*\*(\d+)\*\*[^\n]*未覆盖\s*\*\*(\d+)\*\*", out)
    assert m, (
        "门禁没有打印覆盖清单 ⇒ 边界外的表仍静默不报\n--- stdout ---\n%s" % out)
    scanned, total, covered, uncovered = (int(x) for x in m.groups())
    assert covered + uncovered == total, (
        "清单自相矛盾：已覆盖 %d + 未覆盖 %d ≠ 总表数 %d" % (covered, uncovered, total))
    m2 = re.search(r"门禁盲区）\s*：\s*\*\*(\d+)\*\*\s*张", out)
    assert m2, "没有「自称官方却无 # swXxx 标注（门禁盲区）」计数行"
    blind = int(m2.group(1))
    details = re.findall(r"^\s+未覆盖：(\S+):(\d+)\s+(\S+)（(\d+) 项）\s*$", out, re.M)
    assert len(details) == min(blind, 20), (
        "盲区明细 %d 条 ≠ min(盲区 %d, 上限 20)" % (len(details), blind))
    if blind > 20:
        assert re.search(r"另有\s*%d\s*张未列出" % (blind - 20), out), (
            "盲区 %d 张但没给「另有 N 张未列出」的续行" % blind)


def test_enum_gate_scans_beyond_old_glob():
    """FR-012：扫描面必须比旧的 `scripts/sw_*.py` 宽。"""
    out = _run("check_enum_values_vs_reflection.py").stdout
    m = re.search(r"覆盖清单[^\n]*扫描\s*\*\*(\d+)\*\*", out)
    assert m, "没有覆盖清单"
    scanned = int(m.group(1))
    assert scanned > OLD_GLOB_FILES, (
        "扫描文件数 %d 未超过旧 glob 的 %d 个 `scripts/sw_*.py`" % (scanned, OLD_GLOB_FILES))


def _gate_module():
    """加载门禁模块（只为调它的 `parse_code()`，不跑 `main()`）。"""
    sys.path.insert(0, str(REPO_ROOT))
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_enum_gate_probe", SCRIPTS / "check_enum_values_vs_reflection.py")
    gate = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    assert spec.loader is not None
    spec.loader.exec_module(gate)
    return gate


def test_enum_gate_covers_pattern_tables():
    """F1 的两张表修正后必须**首次进入覆盖**（`sw_pattern.py` 的行数 ≥7）。"""
    rows = [r for r in _gate_module().parse_code() if r[0] == "sw_pattern.py"]
    assert len(rows) >= 7, (
        "sw_pattern.py 只贡献 %d 条覆盖行（2 条既有 + 修正后的 5 条 = 7）⇒ 两张表仍未被覆盖"
        % len(rows))


def test_enum_gate_covers_camel_case_keys():
    """FR-012：**驼峰键**的标注行也必须被覆盖（原先键字符集 `[a-z0-9_]+` 匹配不到 ⇒ 静默边界）。"""
    rows = [r for r in _gate_module().parse_code() if r[0] == "sw_ref_geometry.py"]
    assert len(rows) >= 10, (
        "sw_ref_geometry.py 只贡献 %d 条覆盖行（`REF_PLANE_CONSTRAINTS` 的 10 条驼峰键行应全部被覆盖）"
        % len(rows))


def test_enum_gate_exit_code_unchanged():
    """★ 未覆盖**不判失败** ⇒ 退出码必须仍是 0。"""
    assert _run("check_enum_values_vs_reflection.py").returncode == 0


# ── 直接运行 ─────────────────────────────────────────────────────────

def _main():
    failures = []
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
        except Exception as exc:  # noqa: BLE001
            failures.append((test.__name__, exc))
            print(f"  FAIL  {test.__name__}: {exc}")
    print(f"\n{len(tests) - len(failures)}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    raise SystemExit(_main())
