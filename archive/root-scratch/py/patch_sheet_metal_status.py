"""给 `sw_sheet_metal.py` 加**真机实测状态**与**带原因的守卫**（照 `sw_surface.py` 的先例）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机实测结论，非第三方移植）
# 文件:   D:\\AI\\SW\\probe_sheet_metal_e2e.py（证据脚本）
# 定位:   2026-10-01 真机实测（SW 2026 SP4.1）：该模块 6 个创建入口里
#         **只有 2 个能跑**：
#
#           ✓ create_base_flange    → 真建出特征（特征树出现「钣金6 / 基体-法兰1 / 平展型式6」）
#           ✓ sheet_metal_evidence  → 读回正确（thickness_m=0.002、has_base_flange=True、
#                                     all_solid_bodies_are_sheet_metal=True）
#           ✗ create_one_bend       → `CreateDefinition(33)` 返回 None
#           ✗ create_draft          → `CreateDefinition(3)` 返回 None
#           ✗ create_edge_flange    → `Property 'ReverseDirection' can not be set`
#           ✗ create_gusset         → `Property 'Thickness' can not be set`
#
#         **⇒ 这 4 个已经作为 MCP 工具暴露出去（T-011 接线，45→65），但真机跑不了。**
#         本补丁按 `sw_surface.py` 的先例：把实测结论**写进模块**，并让失败**带原因**，
#         而不是让用户看到裸 COM 错误。
#
#  ⚠ 本补丁**只加记录与守卫，不删任何既有函数** —— 那 4 个函数的**正确形状尚未查明**
#    （是 `swFm` 取值错？是 FeatureData 属性名错？是缺 AccessSelections？），
#    删掉会让线索丢失。**⇒ 记录在案、响亮报错、留给后续查明。**
#
# 官方签名依据: 不适用（本补丁不改 COM 调用形状）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SM = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_sheet_metal.py")

STATUS_BLOCK = '''
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**真机实测结论**，非第三方移植）
# 文件:   D:\\AI\\SW\\probe_sheet_metal_e2e.py（证据脚本）
# 定位:   模块级**运行期实测状态表**（2026-10-01，SW 2026 SP4.1）。
#  ⚠⚠ 结论：本模块 6 个创建入口里**只有 2 个能跑**；另 4 个已作为 MCP 工具暴露
#    （T-011 接线）但真机失败。失败原因见下表 —— **不是「未测」，是「测了，不行」**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本常量整体（自本行至 `}` 结束）
# ⚠ 本表只覆盖**本机实测过**的入口；未测的按「未知」处理（不假设可用）。
# ────────────────────────────────────────────────────────────────────
#: 入口名 → (是否可用, 真机失败原因或成功证据)
SHEET_METAL_RUNTIME_STATUS = {
    # ✓ 实测可跑
    "create_base_flange": (True,
        "真机建成：特征树出现「钣金6 / 基体-法兰1 / 平展型式6」"),
    "sheet_metal_evidence": (True,
        "真机读回正确：thickness_m=0.002、has_base_flange=True、"
        "all_solid_bodies_are_sheet_metal=True"),
    # ✗ 实测失败（原因是真机报错原文）
    "create_one_bend": (False,
        "CreateDefinition(33) 返回 None ⇒ 该 swFm 取值没能取到特征数据"),
    "create_draft": (False,
        "CreateDefinition(3) 返回 None ⇒ 该 swFm 取值没能取到特征数据"),
    "create_edge_flange": (False,
        "设 `ReverseDirection` 时 COM 报 `Property ... can not be set` "
        "⇒ 该属性在拿到的 FeatureData 上不可写（或属性名不对）"),
    "create_gusset": (False,
        "设 `Thickness` 时 COM 报 `Property ... can not be set` "
        "⇒ 该属性在拿到的 FeatureData 上不可写（或属性名不对）"),
    # 未测（需要扫掠路径 + 轮廓两个选择，本轮没造出来）
    "create_swept_flange": (None, "未在本机实测（需要扫掠路径与轮廓两个选择）"),
}


def require_verified(entry: str) -> None:
    """**调用前**的守卫：该入口若在本机实测失败/未测，就抛**带原因**的错误。

    ⚠ 为什么必须这样：那 4 个入口已经作为 MCP 工具暴露给用户，
    失败时用户看到的是裸 COM 错误（`Property ... can not be set`），
    **完全指向不了真因**，也**无从知道这是已知问题**。
    """
    status = SHEET_METAL_RUNTIME_STATUS.get(entry)
    if status is None:
        return                       # 表里没有 ⇒ 不阻止（宁放行不误杀）
    ok, reason = status
    if ok is True:
        return
    if ok is None:
        raise RuntimeError(
            "%s **未在本机实测**（%s）—— 先在真机上验证再依赖它。"
            % (entry, reason)
        )
    raise RuntimeError(
        "%s **在本机实测失败，已知不可用**（2026-10-01，SW 2026 SP4.1）：%s。"
        "⇒ 正确形状尚未查明（是 swFm 取值错？FeatureData 属性名错？缺 AccessSelections？）；"
        "见 scripts/sw_sheet_metal.py 的 SHEET_METAL_RUNTIME_STATUS 与 "
        "D:\\\\AI\\\\SW\\\\probe_sheet_metal_e2e.py。" % (entry, reason)
    )

'''


def main() -> int:
    t = SM.read_text(encoding="utf-8")
    anchor = "def _feature_type(feature: Any) -> str:"
    if anchor not in t:
        print("  ✗ 未找到插入锚点")
        return 1
    t = t.replace(anchor, STATUS_BLOCK.strip() + "\n\n\n" + anchor, 1)

    # 导出
    t = t.replace('__all__ = [\n    "iter_features",',
                  '__all__ = [\n    "SHEET_METAL_RUNTIME_STATUS",\n'
                  '    "require_verified",\n    "iter_features",', 1)
    if '"SHEET_METAL_RUNTIME_STATUS"' not in t:
        # 形状不同就找第一个 __all__ = [
        idx = t.index("__all__ = [")
        t = t[:idx] + '__all__ = [\n    "SHEET_METAL_RUNTIME_STATUS",\n    "require_verified",\n' + t[idx + len("__all__ = [\n"):]
    SM.write_text(t, encoding="utf-8")
    print("  ✓ sw_sheet_metal.py：已加 SHEET_METAL_RUNTIME_STATUS + require_verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
