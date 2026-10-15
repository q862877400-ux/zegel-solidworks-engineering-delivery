r"""@brief 决定性测试：按**正确 arity** 调 `Create*Surface2`（带 `RefDirection`）。

## 官方签名（反射 + 文档）
```
CreateCylindricalSurface  (Object, Object, Double)               ← **已过时**
CreateCylindricalSurface2 (Object, Object, **Object**, Double)    ← 现行
   Center / Direction / **RefDirection** / Radius
CreateSphericalSurface2   (Object, Object, Object, Double)        Center / Axis / RefDir / Radius
CreateConicalSurface2     (Object, Object, Object, Double, Double) Center / Direction / RefDir / Radius / SemiAngle
```
**⇒ `*2` 那一代**多一个 `RefDirection`**（参考方向，3 个 double）。**

## 上一轮拿到的错
```
CreateCylindricalSurface2 → com_error (-2147352561, '**非选择性的参数**')
⇒ 那是 DISP_E_PARAMNOTOPTIONAL —— **可达，只是我少传了一个参数**。
```

**⇒ 本探针按**正确的参数个数**再试，看能否拿到非 None 的曲面。**

# ── 来源 ──
# 仓库:   SolidWorks 官方 API 文档（`C:\swapi\types\IModeler\Create*Surface2.md` 的
#         Parameters 段）+ 反射（`iface_sldworks.txt` 的 Signature 行）
# 文件:   `CreateCylindricalSurface2(Object, Object, Object, Double)` 等 —— **现行一代**
# 定位:   已知事实 40「圆柱/圆锥返回 None」的**根因与修法**：
#         `sw_surface.py` 包装的是**已过时的一代**（官方标 Obsolete），
#         而现行一代 `*2` **运行期可达**、只是多一个 `RefDirection`。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；只调 `IModeler`、不保存。
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

O = (0.0, 0.0, 0.0)
AX = (0.0, 0.0, 1.0)
REF = (1.0, 0.0, 0.0)

OK, BAD = [], []


def trial(label, fn):
    try:
        v = fn()
        if v is not None:
            OK.append(label)
            print("  ✓ %-58s → 非 None" % label)
        else:
            BAD.append((label, "None"))
            print("  ✗ %-58s → **None**" % label)
    except Exception as exc:  # noqa: BLE001
        BAD.append((label, str(exc)[:58]))
        print("  ✗ %-58s → %s" % (label, str(exc)[:52]))


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
        modeler = S.get_modeler(sw)
        print("[参照] 零件 %r" % title)

        print()
        print("=== ① **现行一代**（`*2`，带 RefDirection）——正确 arity ===")
        trial("CreateCylindricalSurface2(Center, Dir, RefDir, Radius)",
              lambda: get_com_member(modeler, "CreateCylindricalSurface2", O, AX, REF, 0.01))
        trial("CreateSphericalSurface2(Center, Axis, RefDir, Radius)",
              lambda: get_com_member(modeler, "CreateSphericalSurface2", O, AX, REF, 0.01))
        trial("CreateConicalSurface2(Center, Dir, RefDir, Radius, SemiAngle)",
              lambda: get_com_member(modeler, "CreateConicalSurface2", O, AX, REF, 0.01, 0.5))

        print()
        print("=== ② 对照：**已过时的一代**（上一轮返回 None 的那些）===")
        trial("CreateCylindricalSurface(Center, Dir, Radius)  [Obsolete]",
              lambda: get_com_member(modeler, "CreateCylindricalSurface", O, AX, 0.01))
        trial("CreateConicalSurface(Center, Dir, Radius, SemiAngle)  [Obsolete]",
              lambda: get_com_member(modeler, "CreateConicalSurface", O, AX, 0.01, 0.5))
        trial("CreateSphericalSurface(Center, Radius)  [Obsolete]  ← **上一轮成功过**",
              lambda: get_com_member(modeler, "CreateSphericalSurface", O, 0.01))

        print()
        print("=== ③ `RefDirection` 换成别的方向，看是否还成 ===")
        for ref in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (1.0, 0.0, 0.0)):
            trial("cyl2(..., RefDir=%r, 0.01)" % (ref,),
                  lambda r=ref: get_com_member(modeler, "CreateCylindricalSurface2",
                                               O, AX, r, 0.01))
        print("  （注：RefDir 与 Dir 平行时几何退化，可能本就该失败）")
        trial("cyl2(..., RefDir 与 Dir **平行**=(0,0,1), 0.01)",
              lambda: get_com_member(modeler, "CreateCylindricalSurface2",
                                     O, AX, (0.0, 0.0, 1.0), 0.01))

        print()
        print("=== 结论 ===")
        print("  现行一代成功 %d / 失败 %d" % (len(OK), len(BAD)))
        for l, e in BAD:
            print("    ✗ %s   %s" % (l[:56], e))
        if OK:
            print("  ✅ **成功的组合** —— 这些就是应当包装的入口：")
            for l in OK:
                print("      ✓ %s" % l)
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
