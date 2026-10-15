"""把可用性守卫**接进** `sw_surface` 的 14 个公开包装器；并修一处**文档串说谎**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机实测结论；非第三方移植）
# 文件:   D:\\AI\\SW\\probe_surface_array_shape.py（可取性证据）
#         D:\\AI\\SW\\probe_geometry_selectors_e2e.py（2026-10-01 撞上本缺陷的证据）
# 定位:   2026-10-01 实测发现的**两个缺陷**：
#
#   **① 守卫存在但从未被接上**（真 bug）
#     `require_runtime_available()` 是第 13 轮加的，**但没人调它** ⇒
#     真机调 `create_planar_surface` 拿到的仍是
#     `TypeError: 'NoneType' object is not callable`（**指向不了真因**）。
#     ⇒ 本补丁让 14 个公开包装器**先调** `require_runtime_available(method)`。
#
#   **② `_invoke` 的文档串在说谎**
#     它写着「统一在此处做**两层自检**：1. 参数个数 … 2. **运行期可取性**」，
#     而第 13 轮为了不挡住契约测试，**把第 2 层从代码里撤了，却没改文档串**。
#     ⇒ 本补丁把文档串改成**只讲 arity**，并把「可用性由调用方在调用前问」写清楚。
#
#  ⚠ 为什么不把可用性检查放回 `_invoke`（第 13 轮撤它的原因）：
#    `tests/test_sw_surface_signature_contract.py` 用**桩 modeler** 验
#    「`create_planar_surface` 把 2 个参数传给 `CreatePlanarSurface`」这个**签名形状**；
#    守卫若在 `_invoke` 里，调用被拦就**验不了形状**。
#    **⇒ 保持职责分离：`_invoke` = 形状；守卫 = 调用方在调用前问。**
#
# 官方签名依据: `IModeler.Create*Surface` 家族（见 `SURFACE_CREATION_METHODS`）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SURF = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_surface.py")

OLD_DOC = '''    """按 SURFACE_CREATION_METHODS 的签名表调用 Create*Surface。

    统一在此处做**两层自检**：
    1. **参数个数**：签名表是照官方反射抄的，传错个数立刻抛带方法名的 `TypeError`；
    2. **运行期可取性**（2026-10-01 加）：若该方法在本机实测**取不到**，
       抛带**原因**的 `RuntimeError` —— 否则调用方只会看到
       `'NoneType' object is not callable`，指向不了真因。
    """'''
NEW_DOC = '''    """按 SURFACE_CREATION_METHODS 的签名表调用 Create*Surface。

    ⚠ 本函数**只做一件事**：**参数个数自检**（签名表照官方反射抄的，传错个数立刻抛
    带方法名的 `TypeError`）。

    ⚠⚠ **可用性检查不在这里**（职责分离，2026-10-01 定的）：
    它由 `require_runtime_available(method)` 承担，**由调用方在调用前显式问**。
    原因：`tests/test_sw_surface_signature_contract.py` 用**桩 modeler** 验
    「参数按签名传」这个**形状**；守卫若放在本函数里，调用被拦就**验不了形状**。

    ⚠ **本文档串曾与代码不符**：第 13 轮撤掉可用性检查时没改文档串，
    它一度声称「做两层自检」。**⇒ 文档串必须与代码同步，否则它比没有更糟。**
    """'''

# 每个公开包装器的首行：插入守卫调用
GUARD = "    require_runtime_available(\"%s\")\n"


def main() -> int:
    t = SURF.read_text(encoding="utf-8")
    if OLD_DOC not in t:
        print("  ✗ 未匹配 _invoke 的文档串")
        return 1
    t = t.replace(OLD_DOC, NEW_DOC, 1)
    print("  ✓ ① _invoke 的文档串已改成只讲 arity（不再说谎）")

    # 给 14 个包装器插守卫
    pat = re.compile(
        r'^(def (create_\w+)\(([^)]*)\):\n)(    """[^"]*"""\n)?(    return _invoke\()',
        re.M)
    count = 0

    def rep(m):
        nonlocal count
        head, fname, _args, doc, ret = m.groups()
        method = {
            "create_planar_surface": "CreatePlanarSurface",
            "create_cylindrical_surface": "CreateCylindricalSurface",
            "create_spherical_surface": "CreateSphericalSurface",
            "create_conical_surface": "CreateConicalSurface",
            "create_toroidal_surface": "CreateToroidalSurface",
            "create_offset_surface": "CreateOffsetSurface",
            "create_extrusion_surface": "CreateExtrusionSurface",
            "create_revolution_surface": "CreateRevolutionSurface",
            "create_ruled_surface": "CreateRuledSurface",
            "create_swept_surface": "CreateSweptSurface",
            "create_bspline_surface": "CreateBsplineSurface",
            "create_coons_b_surface": "CreateCoonsBSurface",
            "create_sheet_from_surface": "CreateSheetFromSurface",
        }.get(fname, fname)
        count += 1
        return head + (doc or "") + GUARD % method + ret

    t2 = pat.sub(rep, t)
    if count == 0:
        print("  ⚠ 一个包装器都没匹配到 —— 形状可能不同，未改")
    else:
        t = t2
        print("  ✓ ② %d 个包装器已插入 require_runtime_available 守卫" % count)
    SURF.write_text(t, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
