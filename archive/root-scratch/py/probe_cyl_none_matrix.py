r"""@brief 探针：`CreateCylindricalSurface` / `CreateConicalSurface` 返回 `None` 的**条件**。

## 已知道的
| 创建器 | 上一次实测（origin=(0,0,-0.01), axis=(0,0,1)）|
|---|---|
| `CreateSphericalSurface(center, r)` | ✓ 非 None |
| `CreateToroidalSurface(o, a, c, R, r)` | ✓ 非 None |
| `CreateCylindricalSurface(o, a, r)` | ✗ **None** |
| `CreateConicalSurface(o, a, half, r)` | ✗ **None** |

**⚠ 而更早的 `probe_surface_array_shape.py` 里，`CreateCylindricalSurface` 用
`origin=[0,0,0]` / `axis=[0,0,1]` / `radius=0.01` **五种包装全都返回非 None**。**

**⇒ 两次结果不一致 ⇒ 一定有个变量在起作用。本探针**单变量**地找它：**
* origin：原点 / bbox 中心 / 体外一点
* axis：+z / +x / 非单位向量 / 零向量
* radius：0.01 / 0.001 / 0.05
* **调用形态**：`_invoke`（模块包装）vs **直接** `modeler.CreateCylindricalSurface(...)`

**⚠ 最后一个变量最可疑**：`_invoke` 会做 arity 自检再转发，而 `get_com_member` 与
`getattr(...)` 直调在 pywin32 下**可能是两条路径**。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_cyl_none_matrix.py
# 定位:   已知事实 40 里「圆柱/圆锥返回 None」的**定性实验**（未定性 → 找条件）。
# 官方签名依据: `IModeler.CreateCylindricalSurface(Object, Object, Double)`
#         `IModeler.CreateConicalSurface(Object, Object, Double, Double)`
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；只调 `IModeler`（纯几何构造，不建特征）、不保存。
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

RESULTS = []


def trial(label, fn):
    try:
        v = fn()
        ok = v is not None
        RESULTS.append((label, ok, None if ok else "None"))
        print("  %s %-62s → %s" % ("✓" if ok else "✗", label,
                                   "非 None" if ok else "**None**"))
        return ok
    except Exception as exc:  # noqa: BLE001
        RESULTS.append((label, False, str(exc)[:60]))
        print("  ✗ %-62s → %s: %s" % (label, type(exc).__name__, str(exc)[:48]))
        return False


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
        print("[参照] 零件 %r（100×60×20 mm 板）" % title)
        modeler = S.get_modeler(sw)

        print()
        print("=== ① 复现上一次的失败（origin=bbox中心, axis=+z）===")
        center = S.get_modeler and (0.0, 0.0, -0.01)
        trial("_invoke 包装: cyl(center, +z, 0.01)",
              lambda: S.create_cylindrical_surface(sw, center, (0.0, 0.0, 1.0), 0.01))
        trial("**直调** modeler.CreateCylindricalSurface(center, +z, 0.01)",
              lambda: get_com_member(modeler, "CreateCylindricalSurface",
                                     center, (0.0, 0.0, 1.0), 0.01))

        print()
        print("=== ② 换 origin：原点（更早那次**成功**的组合）===")
        trial("_invoke: cyl((0,0,0), +z, 0.01)",
              lambda: S.create_cylindrical_surface(sw, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 0.01))
        trial("直调: CreateCylindricalSurface((0,0,0), +z, 0.01)",
              lambda: get_com_member(modeler, "CreateCylindricalSurface",
                                     (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 0.01))

        print()
        print("=== ③ 换 axis ===")
        for ax in ((0.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 0.0)):
            trial("cyl((0,0,0), axis=%r, 0.01)" % (ax,),
                  lambda a=ax: get_com_member(modeler, "CreateCylindricalSurface",
                                              (0.0, 0.0, 0.0), a, 0.01))

        print()
        print("=== ④ 换 radius ===")
        for r in (0.01, 0.001, 0.05, 0.0):
            trial("cyl((0,0,0), +z, radius=%r)" % r,
                  lambda rr=r: get_com_member(modeler, "CreateCylindricalSurface",
                                              (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), rr))

        print()
        print("=== ⑤ 圆锥同样试 ===")
        trial("conical((0,0,0), +z, 0.5, 0.01)",
              lambda: get_com_member(modeler, "CreateConicalSurface",
                                     (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 0.5, 0.01))
        trial("conical((0,0,0), +z, 0.0, 0.01) 半角=0（退化成圆柱？）",
              lambda: get_com_member(modeler, "CreateConicalSurface",
                                     (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 0.0, 0.01))

        print()
        print("=== 结论 ===")
        ok = [l for l, o, _ in RESULTS if o]
        bad = [(l, e) for l, o, e in RESULTS if not o]
        print("  成功 %d / 失败 %d" % (len(ok), len(bad)))
        if ok:
            print("  **成功的组合**（这是要学的东西）：")
            for l in ok[:8]:
                print("    ✓ %s" % l)
        print("  失败的：")
        for l, e in bad[:8]:
            print("    ✗ %s   %s" % (l, e))
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if title:
                sw.CloseDoc(title)
        except Exception:  # noqa: BLE001
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
