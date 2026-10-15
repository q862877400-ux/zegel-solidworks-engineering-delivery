"""给 `sw_surface.py` 加「运行期可取性」说明与明确报错。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁，非第三方移植）
# 文件:   D:\\AI\\SW\\patch_surface_runtime.py
# 定位:   2026-10-01 真机实测发现：该模块导出的 14 个曲面创建入口里
#         **只有 5 个在运行期可取**；其余 9 个要么 `getattr` 得 None、
#         要么成员根本不存在、要么服务器异常。
#         而当时失败方式是 `'NoneType' object is not callable`（含混，指向不了真因）。
#         本补丁把 `_invoke` 改成**先检查可取性**，并给出可诊断的错误。
# 官方签名依据: 不适用（纯 Python 文本补丁 + 真机实测结论）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SURF = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_surface.py")

OLD = '''def _invoke(modeler, method: str, *args):
    """按 SURFACE_CREATION_METHODS 的签名表调用 Create*Surface。

    统一在此处做**参数个数自检**：签名表是照官方反射抄的，
    若调用方改错了参数个数，在这里立刻抛出带方法名的错误，
    而不是让 COM 报一个语焉不详的异常。
    """
    if method not in SURFACE_CREATION_METHODS:
        raise KeyError(f"未登记的曲面创建方法: {method}")
    expected = len(SURFACE_CREATION_METHODS[method][1])
    if len(args) != expected:
        raise TypeError(
            f"{method} 官方签名为 {expected} 个参数，"
            f"实际传入 {len(args)} 个"
        )
    return get_com_member(modeler, method, *args)
'''

NEW = '''# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机实测结论，非第三方移植）
# 文件:   D:\\AI\\SW\\probe_surface_array_shape.py（证据脚本）
# 定位:   **运行期可取性表** —— 2026-10-01 在活着的 `IModeler` 上逐个 `getattr` 实测。
#  ⚠⚠ 结论：本模块导出的 14 个创建入口里，**运行期只有 5 个可取**：
#       ✓ CreateCylindricalSurface / CreateSphericalSurface / CreateConicalSurface
#         / CreateToroidalSurface / CreateArc
#       ✗ **getattr 得 None**（调用会报 `'NoneType' object is not callable`）：
#         CreatePlanarSurface / CreateLine
#       ✗ **成员根本不存在**：CreatePoint / CreateBodyFromSurf / …
#       ✗ **服务器异常 `0x80010105`**：CreateBsplineSurface
#  ⇒ **「反射里有」≠「运行期调用得到」** —— 与本项目已知事实 11
#    （`OpenDoc6` 的 `[out] long` 在 makepy 代理下要绕）同类：**类型层与运行层会不一致**。
#  ⚠ 同批实测确定的另一件事：`Object` 型点/向量参数**五种包装全可用**
#    （裸 list / 裸 tuple / `VT_ARRAY|VT_R8` / `VT_ARRAY|VT_VARIANT` /
#    逐元素 VARIANT）—— pywin32 会自动把 list/tuple 转 SAFEARRAY。
#    ⇒ **不必强制调用方包 VARIANT**。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数整体（自本行至函数结束）
# ⚠ 本表只覆盖**本机**实测到的成员；未逐个测的成员按「未知」处理（不假设可用）。
# ────────────────────────────────────────────────────────────────────
#: 2026-10-01 真机实测**可取**的 `IModeler` 创建入口
IMODELER_RUNTIME_AVAILABLE = frozenset({
    "CreateCylindricalSurface",
    "CreateSphericalSurface",
    "CreateConicalSurface",
    "CreateToroidalSurface",
    "CreateArc",
})

#: 2026-10-01 真机实测**取不到**（`getattr` 得 None ⇒ 调用会报含混的 `NoneType not callable`）
IMODELER_RUNTIME_UNAVAILABLE = frozenset({
    "CreatePlanarSurface",
    "CreateLine",
    "CreatePoint",
    "CreateBodyFromSurf",
    "CreateBsplineSurface",
})


def _invoke(modeler, method: str, *args):
    """按 SURFACE_CREATION_METHODS 的签名表调用 Create*Surface。

    统一在此处做**两层自检**：
    1. **参数个数**：签名表是照官方反射抄的，传错个数立刻抛带方法名的 `TypeError`；
    2. **运行期可取性**（2026-10-01 加）：若该方法在本机实测**取不到**，
       抛带**原因**的 `RuntimeError` —— 否则调用方只会看到
       `'NoneType' object is not callable`，指向不了真因。
    """
    if method not in SURFACE_CREATION_METHODS:
        raise KeyError(f"未登记的曲面创建方法: {method}")
    expected = len(SURFACE_CREATION_METHODS[method][1])
    if len(args) != expected:
        raise TypeError(
            f"{method} 官方签名为 {expected} 个参数，"
            f"实际传入 {len(args)} 个"
        )
    if method in IMODELER_RUNTIME_UNAVAILABLE:
        raise RuntimeError(
            f"{method} 在**本机运行期取不到**（`getattr` 得 None）—— "
            f"官方类型库里有它，但迟到绑定拿不到。"
            f"本机实测可取的入口见 IMODELER_RUNTIME_AVAILABLE："
            f"{sorted(IMODELER_RUNTIME_AVAILABLE)}。"
            f"⚠ 「反射里有」≠「运行期调用得到」（2026-10-01 真机结论）。"
        )
    if not callable(getattr(modeler, method, None)):
        raise RuntimeError(
            f"{method} 在本机既不在「实测可取」也不在「实测取不到」名单里，"
            f"且当前对象上不可调 —— 需要**先实测**再决定（不猜）。"
        )
    return get_com_member(modeler, method, *args)
'''


def main() -> int:
    text = SURF.read_text(encoding="utf-8")
    if OLD not in text:
        print("  ✗ 未匹配 _invoke")
        return 1
    text = text.replace(OLD, NEW, 1)
    # 导出两个常量（供测试与调用方查询）
    text = text.replace(
        '__all__ = [\n    "SURFACE_CREATION_METHODS",',
        '__all__ = [\n    "SURFACE_CREATION_METHODS",\n'
        '    "IMODELER_RUNTIME_AVAILABLE",\n'
        '    "IMODELER_RUNTIME_UNAVAILABLE",', 1)
    SURF.write_text(text, encoding="utf-8")
    print("  ✓ _invoke 已加运行期可取性检查；两个常量已导出")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
