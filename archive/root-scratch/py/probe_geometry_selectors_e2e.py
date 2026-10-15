r"""@brief 端到端实测：**声明式点/方向解析器 → 真建出曲面**。

## 要回答的
`scripts/sw_geometry_selectors.py` 的解析器能不能喂给 `sw_surface` 那 4 个
**运行期可达**的创建器（已知事实 28：14 个里只有 5 个可达），并**真拿到非 None 的曲面**？

**⇒ 若能，B 类解锁就是实的（不是纸面声明）。**

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_geometry_selectors_e2e.py
# 定位:   B 类（「需声明式选择解析」）的**底层验收**。
# 官方签名依据: `IModeler.CreateCylindricalSurface(Object, Object, Double)` 等
#         （见 `scripts/sw_surface.py` 的 `SURFACE_CREATION_METHODS`）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；只造参照几何 + 调 `IModeler`（**纯几何构造，不建特征**）、不保存。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part  # noqa: E402
from scripts import sw_surface as S  # noqa: E402
from scripts import sw_geometry_selectors as G  # noqa: E402

PASS, FAIL = [], []


def expect_error(label, fn, exc_type=Exception):
    """**期望抛错**才算通过。

    ⚠ **本会话第三次**犯同一个判定错**（前两次：契约测试、曲面探针）：
    把「期望的报错」当失败 ⇒ 让**正确的行为看起来像 bug**。
    ⇒ 判据要照**契约**写：该报错的，报了才算对。
    """
    try:
        v = fn()
        print("  ✗ %-52s → 竟然没报错，返回 %r" % (label, str(v)[:40]))
        FAIL.append((label, "未按契约报错"))
        return None
    except exc_type as exc:
        print("  ✓ %-52s → 正确报错: %s" % (label, str(exc)[:48]))
        PASS.append(label)
        return exc
    except Exception as exc:  # noqa: BLE001
        print("  ✗ %-52s → 报了**别的**异常 %s: %s" % (label, type(exc).__name__, str(exc)[:40]))
        FAIL.append((label, str(exc)[:80]))
        return None


def check(label, fn):
    try:
        v = fn()
        print("  ✓ %-52s → %r" % (label, str(v)[:44]))
        PASS.append(label)
        return v
    except Exception as exc:  # noqa: BLE001
        print("  ✗ %-52s → %s: %s" % (label, type(exc).__name__, str(exc)[:62]))
        FAIL.append((label, str(exc)[:90]))
        return None


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        print("[1] 参照零件 %r（100×60×20 mm 板）" % title)

        print()
        print("=== ① 点选择器解析（真机）===")
        pts = {}
        for sel in ("origin", "bbox:min", "bbox:max", "bbox:center"):
            pts[sel] = check("resolve_point(%r)" % sel,
                             lambda s=sel: G.resolve_point(model, s))
        print("      → bbox:min %r / max %r（板应为 ±0.05 / ±0.03 / 0..0.02）"
              % (pts.get("bbox:min"), pts.get("bbox:max")))
        check("resolve_point('centroid')", lambda: G.resolve_point(model, "centroid"))
        expect_error("resolve_point(裸坐标) **应报错**",
                     lambda: G.resolve_point(model, "(0.1,0.2,0.3)"),
                     G.GeometrySelectorError)

        print()
        print("=== ② 用解析出来的点/方向**真建曲面**（4 个可达创建器）===")
        origin = pts.get("bbox:center") or (0.0, 0.0, 0.0)
        axis = G.resolve_direction("+z")
        print("      origin=%r  axis=%r" % (origin, axis))

        check("create_cylindrical_surface(origin, axis, 0.01)",
              lambda: S.create_cylindrical_surface(sw, origin, axis, 0.01))
        check("create_spherical_surface(origin, 0.01)",
              lambda: S.create_spherical_surface(sw, origin, 0.01))
        check("create_conical_surface(origin, axis, 0.5, 0.01)",
              lambda: S.create_conical_surface(sw, origin, axis, 0.5, 0.01))
        check("create_toroidal_surface(origin, axis, origin, 0.02, 0.005)",
              lambda: S.create_toroidal_surface(sw, origin, axis, origin, 0.02, 0.005))

        print()
        print("=== ③ 对照：不可达的那几个**应给出带原因的错误** ===")
        expect_error("create_planar_surface **应报带原因的错**",
                     lambda: S.create_planar_surface(sw, origin, axis), RuntimeError)
        expect_error("require_runtime_available('CreatePlanarSurface') **应报错**",
                     lambda: S.require_runtime_available("CreatePlanarSurface"), RuntimeError)

        print()
        print("=== 结论 ===")
        print("  通过 %d / 失败 %d" % (len(PASS), len(FAIL)))
        for label, msg in FAIL:
            print("    ✗ %s\n        %s" % (label, msg))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if title:
                sw.CloseDoc(title)
                print("  [收尾] 文档已关闭（未保存）")
        except Exception:  # noqa: BLE001
            pass
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
