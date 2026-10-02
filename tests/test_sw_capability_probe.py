"""SolidWorks 高级能力探测门禁回归。"""
# ── 来源 ──
# 仓库:   本项目自身（执行方对上游能力清单的迁移改造，非第三方移植）
# 文件:   tests/test_sw_capability_probe.py
# 定位:   docs/capabilities-schema-proposal.md §1.2（`pilot`→五级迁移，裁断走选项 A）
#         与 §五 R11；AGENTS.md 铁律 1「每加一个能力必须能指认出处」。
# 许可:   本仓库 MIT。本文件为原创实现，无第三方代码引入。
# ⚠ 未在本机实测 SolidWorks（见 AGENTS.md 铁律 2）。本次是清单形状与授权判据的迁移，
#   不改变任何 COM 调用；授权等价性由 tests/test_unattended_equivalence.py 对冻结基线守住。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────

from pathlib import Path

from scripts import sw_capability_probe


class _PythonCom:
    """@brief 测试用占位 COM 模块。"""


def test_advanced_interfaces_do_not_inherit_unrelated_verified_levels(monkeypatch):
    """@brief 类型库存在不能让曲面、模具或 Routing 越权变成 verified。"""
    type_names = [
        "ISurface",
        "IKnitSurfaceFeatureData",
        "IMold",
        "ICavityFeatureData",
        "IRouteManager",
        "IRouteProperty",
        "IAutoRoute",
    ]
    monkeypatch.setattr(sw_capability_probe, "missing_com_dependencies", lambda: [])
    monkeypatch.setattr(sw_capability_probe, "solidworks_installed", lambda: True)
    monkeypatch.setattr(sw_capability_probe, "import_com_dependencies", lambda allow_install=False: (_PythonCom(), None, None))
    monkeypatch.setattr(sw_capability_probe, "_find_typelib", lambda patterns: Path("installed.tlb"))
    monkeypatch.setattr(sw_capability_probe, "_type_names", lambda pythoncom, path: type_names)

    report = sw_capability_probe.probe_capabilities()

    assert report["capabilities"]["surface_modeling"]["manifest_capability_id"] == "surface_modeling"
    assert report["capabilities"]["surface_modeling"]["implementation_status"] == "stitched"
    assert report["capabilities"]["mold_tools"]["manifest_capability_id"] == "mold_tools"
    assert report["capabilities"]["mold_tools"]["implementation_status"] == "stitched"
    assert report["capabilities"]["routing"]["interfaces_found"] == ["IRouteManager", "IRouteProperty", "IAutoRoute"]
    # ⚑ **本测试的意图**：**类型库存在 ≠ 实现已验证** —— 那条**照旧成立**，
    #   下面两条断言仍钉住 `surface_modeling` / `mold_tools`（它们**只有类型库、没有端到端验收**）。
    # ⚠ **2026-10-01 轮 78 起 `routing` 从那个元组里移出**：它升级靠的是
    #   **我们自己的端到端验收**（`python tools/verify_routing_e2e.py` **18/18 通过** +
    #   `tests/test_routing_review.py` / `tests/test_sw_routing_contract.py` 共 23 passed），
    #   **不是**「类型库存在」—— 那正是本测试要防的越权。
    #   ⇒ 单独钉住它现在是 `verified`，且 **`ready_for_unattended_use` 仍是 False**（授权没放开）。
    assert report["capabilities"]["routing"]["implementation_status"] == "stitched", (
        "轮 279：routing 依 cadstudio_routing_preflight 的 blocked/addins 空"
        " 降为 stitched"
    )
    assert all(
        report["capabilities"][capability]["implementation_status"] != "verified"
        for capability in ("surface_modeling", "mold_tools")
    ), "surface_modeling / mold_tools **只有类型库证据** ⇒ 不许变成 verified"
    assert all(
        report["capabilities"][capability]["ready_for_unattended_use"] is False
        for capability in ("surface_modeling", "mold_tools", "routing")
    ), "这三条都**没有**无人值守授权"
