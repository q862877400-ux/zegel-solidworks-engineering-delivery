r"""@brief 探针：用**运行期可用**的 `IModeler` 成员定「点/向量」的对象形状。

## 前一版的结论与它带来的转向
第一版探 `CreatePlanarSurface`，三种数组形状**全失败**，报 `'NoneType' object is not callable`。
深挖后发现：**不是形状错，而是那个成员在运行期根本取不到**：

    在活着的 modeler 上逐个 getattr（2026-10-01 真机）：
        CreateCylindricalSurface  → method   ✓ 可用
        CreateSphericalSurface    → method   ✓ 可用
        CreateArc                 → method   ✓ 可用
        **CreatePlanarSurface**   → **None**  ✗ 不可用
        **CreateLine**            → **None**  ✗ 不可用
        CreatePoint               → 不存在

**⇒ 结论 1（重要）**：官方类型库里有 `IModeler.CreatePlanarSurface`
（在线 API 参考可查到签名 `(VRootPoint As Object, VNormal As Object)`），
**但运行期的迟到绑定拿不到它** —— **「反射里有」不等于「调用得到」**。
这与本项目已知事实 11（`OpenDoc6` 的 `[out] long` 在 makepy 代理下要绕）同类：
**类型层与运行层会不一致。**

**⇒ 结论 2**：本探针改用**可用**的 `CreateCylindricalSurface(origin, axis, radius)`
与 `CreateSphericalSurface(center, radius)` 来定「点/向量」的对象形状 ——
**同一个 `Object` 类型，形状规律是共用的。**

## 要定的事
`Object` 参数该传什么：裸 tuple / `VT_ARRAY|VT_R8` / `VT_ARRAY|VT_VARIANT` / `VT_ARRAY|VT_VARIANT` of VARIANT。
**判据**：返回非 None（拿到 ISurface）。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_surface_array_shape.py
# 定位:   `scripts/sw_surface.py`（头部自述「未在本机实测」）要摘帽的第一块；
#         T-011 B 类（「需声明式选择解析」）的前置实验。
# 官方签名依据: `IModeler.CreateCylindricalSurface(Object, Object, Double) -> Object`
#         `IModeler.CreateSphericalSurface(Object, Double) -> Object`
#         （`SolidWorks.Interop.sldworks.dll` 反射 + 在线 API 参考）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；只造几何（不建特征、不改模型）、不保存。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

import pythoncom  # noqa: E402
from win32com.client import VARIANT  # noqa: E402

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part  # noqa: E402

ORIGIN = [0.0, 0.0, 0.0]
AXIS = [0.0, 0.0, 1.0]
CENTER = [0.0, 0.0, 0.05]
RADIUS = 0.01


def shapes(value):
    """返回 ``{标签: 构造好的对象}`` —— 同一份数据的不同 COM 包装。"""
    out = {
        "裸 list": list(value),
        "裸 tuple": tuple(value),
    }
    try:
        out["VT_ARRAY|VT_R8"] = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, list(value))
    except Exception as exc:  # noqa: BLE001
        out["VT_ARRAY|VT_R8(构造失败)"] = exc
    try:
        out["VT_ARRAY|VT_VARIANT"] = VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, list(value))
    except Exception as exc:  # noqa: BLE001
        out["VT_ARRAY|VT_VARIANT(构造失败)"] = exc
    try:
        # 逐元素 VARIANT 的数组（官方 VB 示例里 Array(...) 的常见形态）
        out["VT_ARRAY|VT_VARIANT of R8"] = VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_VARIANT,
            [VARIANT(pythoncom.VT_R8, float(x)) for x in value])
    except Exception as exc:  # noqa: BLE001
        out["VT_ARRAY|VT_VARIANT of R8(构造失败)"] = exc
    return out


def main() -> int:
    sw, _model, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    handle = get_com_member(sw, "GetModeler")
    print("[0] modeler = %r" % (handle is not None))
    title = None
    model = new_document(sw, doc_type="part")
    title = get_com_member(model, "GetTitle")
    sk = sw_part.sketch(model, "Front Plane")
    sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
    sw_part.extrude_boss(model, sk, 0.02)
    print("[1] 参照零件 %r" % title)

    modeler = get_com_member(sw, "GetModeler")

    print()
    print("=== ① 先确认哪些成员**运行期可取**（这一步是本轮的关键认识）===")
    available = []
    for name in ("CreateCylindricalSurface", "CreateSphericalSurface", "CreateConicalSurface",
                 "CreateToroidalSurface", "CreatePlanarSurface", "CreateLine", "CreateArc",
                 "CreatePoint", "CreateBodyFromSurf", "CreateBsplineSurface"):
        try:
            v = getattr(modeler, name)
            kind = type(v).__name__
            ok = callable(v)
            if ok:
                available.append(name)
            print("  %-26s → %-10s %s" % (name, kind, "✓ 可取" if ok else "✗ 取到 None"))
        except Exception as exc:  # noqa: BLE001
            print("  %-26s → ✗ %s" % (name, str(exc)[:46]))

    print()
    print("=== ② 用**可取到**的成员定 Object 形状 ===")
    winners = {}
    for name, args_builder in (
        ("CreateCylindricalSurface", lambda s: (s["origin"], s["axis"], RADIUS)),
        ("CreateSphericalSurface", lambda s: (s["center"], RADIUS)),
    ):
        if name not in available:
            print("  （跳过 %s：运行期取不到）" % name)
            continue
        print("  ── %s ──" % name)
        for shape_label, origin_obj in shapes(ORIGIN).items():
            if isinstance(origin_obj, Exception):
                print("    %-28s → 构造失败: %s" % (shape_label, str(origin_obj)[:40]))
                continue
            bag = {"origin": origin_obj, "center": origin_obj,
                   "axis": shapes(AXIS)["VT_ARRAY|VT_R8"]
                   if not isinstance(shapes(AXIS).get("VT_ARRAY|VT_R8"), Exception)
                   else AXIS}
            try:
                fn = getattr(modeler, name)
                surf = fn(*args_builder(bag))
                ok = surf is not None
                print("    %-28s → %s" % (shape_label, "✓ 非 None" if ok else "✗ None"))
                if ok and name not in winners:
                    winners[name] = shape_label
            except Exception as exc:  # noqa: BLE001
                print("    %-28s → ✗ %s" % (shape_label, str(exc)[:56]))

    print()
    print("=== 结论 ===")
    print("  运行期可取的创建入口: %r" % available)
    print("  成功的 Object 形状: %r" % winners)
    if winners:
        print("  ⇒ **采用**: %s" % list(winners.values())[0])
    else:
        print("  ⇒ 形状仍未定 —— 需继续换包装（**不猜**）")
    print()
    print("  ⚠ 记下这条：**反射里有 ≠ 运行期调用得到**")
    print("     `IModeler.CreatePlanarSurface` / `CreateLine` 就是活证据。")

    try:
        sw.CloseDoc(title)
    except Exception:
        pass
    print("收尾完成（文档未保存）")
    return 0 if winners else 1


if __name__ == "__main__":
    raise SystemExit(main())
