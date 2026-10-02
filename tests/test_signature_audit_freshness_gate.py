"""@brief 签名审计表新鲜度门禁的契约测试（**含负例**）。

# ── 来源 ──
# 仓库:   本项目自身（测试，非第三方移植）
# 文件:   tests/test_signature_audit_freshness_gate.py
# 定位:   给 `scripts/check_signature_audit_freshness.py`（轮 55 新增的**硬门禁**）补契约测试。
#         ⚠ 按本仓库纪律：**门禁必须有负例**（「一个存在但没人用的守卫与没有守卫等价」）。
#         依据是 2026-10-01 实测：`signature-audit.md` 的逐模块表 **3/6 失真**
#         （`drawing_workflow` 140→198 · `sw_simulation` 34→44 · `sw_topology` 45→49）。
# 官方签名依据: 不适用（纯静态：读 markdown + 跑本仓库的静态审计工具，**不连 SolidWorks**）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load():
    spec = importlib.util.spec_from_file_location(
        "check_signature_audit_freshness", ROOT / "scripts" / "check_signature_audit_freshness.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_signature_audit_freshness"] = mod
    spec.loader.exec_module(mod)
    return mod


MOD = _load()


def test_current_table_is_fresh() -> None:
    """★ 当前 `signature-audit.md` 的逐模块表必须与实跑相符（否则门禁该红）。"""
    assert MOD.main(["--repo", str(ROOT)]) == 0


def test_parse_table_reads_both_column_forms(tmp_path: Path) -> None:
    """★ 两张表**列数不同**（批次 5 是 6 列、批次 7 是 5 列）⇒ 两种都要能解析。

    ⚠ 这是实测里的真实形态，不是构造的。
    """
    d = tmp_path / "doc.md"
    d.write_text(
        "| 目标 | 调用点 | 通过 | 存疑 | 查不到 | 动态 |\n"
        "|---|---|---|---|---|---|\n"
        "| `drawing_workflow.py` | 198 | **194** | 0 | 1 | 3 |\n"
        "| 模块 | 调用点 | 通过 | 存疑 | 查不到 |\n"
        "|---|---|---|---|---|\n"
        "| `sw_topology.py` | 49 | **49** | 0 | 0 |\n",
        encoding="utf-8")
    got = MOD.parse_table(d)
    assert got["drawing_workflow.py"] == {"calls": 198, "passed": 194}, got
    assert got["sw_topology.py"] == {"calls": 49, "passed": 49}, got


def test_parse_table_returns_empty_without_table(tmp_path: Path) -> None:
    """没有表 ⇒ 空 dict（调用方据此 SKIP）。"""
    d = tmp_path / "doc.md"
    d.write_text("# 没有表\n", encoding="utf-8")
    assert MOD.parse_table(d) == {}


def test_missing_doc_skips(tmp_path: Path) -> None:
    """★ **便携性守卫**：文档不在 ⇒ **SKIP（exit 0）**。"""
    assert MOD.main(["--repo", str(ROOT), "--doc", str(tmp_path / "nope.md")]) == 0


def test_missing_reflection_skips(tmp_path: Path) -> None:
    """★ **便携性守卫**：拿不到 `iface_*.txt` ⇒ **SKIP（exit 0）**。

    ⚠ 否则任何没有反射转储的机器上，这个门禁会**无条件红**。
    """
    d = tmp_path / "doc.md"
    d.write_text("| `sw_mold.py` | 17 | **17** | 0 | 0 |\n", encoding="utf-8")
    assert MOD.main(["--repo", str(ROOT), "--doc", str(d),
                     "--raw", str(tmp_path / "no-raw")]) == 0


def test_resolve_module_prefers_source_over_bundled_snapshot() -> None:
    """★★ **假命中守卫**：同名文件在同一仓里可能有两份 —— **源**与**桌面内嵌快照**。

    实例：`drawing_workflow.py` 同时在
    `subskills/solidworks-engineering-drawing/scripts/`（**源**）与
    `apps/workbench-ui/src-tauri/resources/skill/subskills/...`（**gitignore 的构建产物**）。
    ⇒ 解析器若不排除快照，会判「不唯一」而放弃 ⇒ **6 个模块里白丢 1 个**。
    """
    p = MOD.resolve_module("drawing_workflow.py", ROOT)
    assert p is not None, "解析不了 drawing_workflow.py"
    assert "resources" not in p.parts, "解析到了**快照**而不是源：%s" % p
    assert p.parts[-3:] == ("solidworks-engineering-drawing", "scripts", "drawing_workflow.py"), p


def test_resolve_module_finds_scripts_and_subskills() -> None:
    """`scripts/` 下的与子技能下的都要能解析。"""
    assert MOD.resolve_module("sw_topology.py", ROOT).parent.name == "scripts"
    assert MOD.resolve_module("drawing_workflow.py", ROOT) is not None


def test_resolve_module_returns_none_for_unknown() -> None:
    """★ **负例**：不存在的模块 ⇒ `None`（**不瞎猜**）。"""
    assert MOD.resolve_module("definitely_not_a_module_xyz.py", ROOT) is None
