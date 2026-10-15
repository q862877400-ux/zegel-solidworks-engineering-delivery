r"""@brief 决定性实验：`Create*Surface` 的 **`*2` 新一代变体**是否可达、是否能建出来？

## 为什么这是根因
官方文档明写：
```
CreateCylindricalSurface: "**Obsolete. Superseded by IModeler::CreateCylindricalSurface2.**"
CreateSphericalSurface:   "**Obsolete. Superseded by IModeler::CreateSphericalSurface2.**"
```
**⇒ `sw_surface.py` 包装的全是**非 2**（已过时）的那一代。**
**⇒ 而 AGENTS.md 的并入规范里有一条相近的路由约定（「默认优先同名非 I 方法」）——
这里对应的规则应当是：**优先**最新一代**（带 `2` 的）。**

## 本探针要回答
1. `IModeler` 上**有哪些** `Create*Surface*` 成员？（把两代都列全）
2. 哪些**运行期可达**（`getattr` 拿得到可调对象）？
3. `*2` 那一代**调用后返回非 None 吗**？

**⚠ 与已知事实 28「反射里有 ≠ 运行期调用得到」同源：本探针把**两代**都过一遍，
而不是只测被包装的那一代。**

# ── 来源 ──
# 仓库:   SolidWorks 官方 API 文档（`C:\swapi\types\IModeler\Create*Surface*.md` 的
#         Obsolete/ Superseded 标注）+ 本项目真机实测
# 文件:   `IModeler` 的 `Create*Surface` 家族（见 `scripts/sw_surface.py` 的
#         `SURFACE_CREATION_METHODS`，那里只登记了非 2 的一代）
# 定位:   已知事实 40「圆柱/圆锥返回 None」的**根因**：用的是**已过时的一代**。
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
from scripts import sw_api_sldworks as API  # noqa: E402


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
        print("=== ① IModeler 上**所有** Create*Surface* 成员（两代都列）===")
        # 从 API 索引里取（`sw_api_sldworks` 存的是 {成员名: 参数个数}）
        try:
            imodeler = API.IMODELER_MEMBERS if hasattr(API, "IMODELER_MEMBERS") else None
        except Exception:  # noqa: BLE001
            imodeler = None
        names = sorted(n for n in dir(modeler) if n.startswith("Create") and "Surface" in n)
        print("  运行期 `dir()` 里含 Surface 的 Create*: %d 个" % len(names))
        for n in names:
            print("    %s" % n)
        if not names:
            print("    ⚠ dir() 没列出 —— 迟到绑定常见，改用**逐个 getattr 试**")

        print()
        print("=== ② 逐个 getattr：可达 + 调用 ===")
        candidates = (
            ("CreateCylindricalSurface", "CreateCylindricalSurface2"),
            ("CreateSphericalSurface", "CreateSphericalSurface2"),
            ("CreateConicalSurface", "CreateConicalSurface2"),
            ("CreateToroidalSurface", "CreateToroidalSurface2"),
            ("CreatePlanarSurface", "CreatePlanarSurface2"),
        )
        for old, new in candidates:
            for name in (old, new):
                fn = getattr(modeler, name, None)
                if not callable(fn):
                    print("  %-28s → ✗ 运行期不可达" % name)
                    continue
                # 按各自签名试调（2 那代多一个参数，先只试 4 参形态）
                origin, axis = (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)
                try:
                    if "Cylindrical" in name:
                        v = fn(origin, axis, 0.01)
                    elif "Spherical" in name:
                        v = fn(origin, 0.01)
                    elif "Conical" in name:
                        v = fn(origin, axis, 0.5, 0.01)
                    elif "Toroidal" in name:
                        v = fn(origin, axis, origin, 0.02, 0.005)
                    else:
                        v = fn(origin, axis)
                    print("  %-28s → %s" % (name, "✓ 非 None" if v is not None else "✗ **None**"))
                except Exception as exc:  # noqa: BLE001
                    print("  %-28s → ✗ %s: %s" % (name, type(exc).__name__, str(exc)[:44]))

        print()
        print("=== ③ 官方文档里这一族有多少个被标 Obsolete ===")
        from pathlib import Path
        d = Path(r"C:\swapi\types\IModeler")
        if d.is_dir():
            obs = []
            for f in sorted(d.glob("Create*Surface*.md")):
                txt = f.read_text(encoding="utf-8", errors="replace")
                if "Obsolete" in txt:
                    obs.append(f.stem)
            print("  标 Obsolete 的: %d 个 —— %r" % (len(obs), obs))
            allf = sorted(f.stem for f in d.glob("Create*Surface*.md"))
            print("  该族全部: %d 个" % len(allf))
            print("  ⇒ 未标 Obsolete 的: %r" % [n for n in allf if n not in obs])

        print()
        print("=== 结论 ===")
        print("  若 `*2` 可达且调用非 None ⇒ **根因是「用了已过时的一代」**，修法 = 改用它")
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
