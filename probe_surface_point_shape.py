r"""@brief 探针：`IModeler.CreatePlanarSurface` 的 `Object` 参数到底是什么形状。

## 为什么必须先探而不是猜
`scripts/sw_surface.py` 的头部明写「**本模块为静态签名比对后新写，未在本机实测**」。
它把 ``point`` / ``normal`` 原样透传给 COM，而反射只给类型 **`Object`** ——
**COM 的 `Object` 可以是 VARIANT 数组、SAFEARRAY、IDispatch…** 形状未定。

**⇒ 本项目已经因为「形状猜错」付出过代价**（`CreateMesh` 把毫米当米 ⇒ 1950 万单元 /
20–25 GB；`AddRestraint` 的 `DispArray` 传 None 不报错但无效果）。
**所以这次先测，不猜。**

## 本脚本要定的事
1. `CreatePlanarSurface(point, normal)` 的 `Object` 该传什么：
   - 三元素 **tuple**（pywin32 自动转 VARIANT 数组）？
   - `VARIANT(VT_ARRAY|VT_R8, [x,y,z])`？
   - `win32com.client.VARIANT(VT_ARRAY | VT_VARIANT, (...))`？
2. 返回值是 `ISurface`（非 None）才算成功 —— 这是判据。

## 安全
只调 ``IModeler``（纯几何构造，**不建特征、不改模型**），故**不设** `CommandInProgress`
（要能看见异常对话框；且这些调用极快）。跑完关闭自建文档、不保存。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_surface_point_shape.py
# 定位:   `scripts/sw_surface.py` 的「未在本机实测」要摘掉的第一块；
#         T-011 B 类（「需声明式选择解析」）的前置实验。
# 官方签名依据: `IModeler.CreatePlanarSurface(Object, Object) -> Object`
#         （`SolidWorks.Interop.sldworks.dll` 元数据反射，
#          见 `scripts/sw_surface.py` 的 `SURFACE_CREATION_METHODS`）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；只造几何、不改模型、不保存。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

import pythoncom  # noqa: E402
import win32com.client  # noqa: E402
from win32com.client import VARIANT  # noqa: E402

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part  # noqa: E402
from scripts.sw_surface import get_modeler  # noqa: E402

POINT = (0.0, 0.0, 0.05)
NORMAL = (0.0, 0.0, 1.0)


def try_call(label, point_obj, normal_obj):
    """调一次 CreatePlanarSurface，报告返回值。返回是否成功（非 None）。"""
    try:
        sw, _m, _meta = _SW  # noqa: F821 —— 由 main 注入
        modeler = get_modeler(sw)
        surf = get_com_member(modeler, "CreatePlanarSurface", point_obj, normal_obj)
        ok = surf is not None
        print("  %-46s → %s" % (label, "✓ 非 None（成功）" if ok else "✗ None（失败）"))
        if ok:
            try:
                kind = get_com_member(surf, "IsPlane")
                print("      surf.IsPlane = %r" % (kind,))
            except Exception as exc:
                print("      （读 IsPlane 失败：%s）" % str(exc)[:50])
        return ok
    except Exception as exc:
        print("  %-46s → ✗ 异常 %s" % (label, str(exc)[:70]))
        return False


def main() -> int:
    global _SW
    sw, _model, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    _SW = (sw, _model, _meta)
    handle = get_com_member(sw, "GetModeler")
    print("[0] ISldWorks.GetModeler() 非空 = %r" % (handle is not None))
    title = None
    model = new_document(sw, doc_type="part")
    title = get_com_member(model, "GetTitle")
    sk = sw_part.sketch(model, "Front Plane")
    sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
    sw_part.extrude_boss(model, sk, 0.02)
    print("[1] 参照零件 %r（只为有个文档上下文）" % title)

    print()
    print("=== 试 `point` / `normal` 的各种对象形状（判据：返回非 None）===")
    results = {}

    # ① 裸 tuple（pywin32 常自动转 VARIANT 数组）
    results["裸 tuple"] = try_call("tuple (0,0,0.05) / (0,0,1)", POINT, NORMAL)

    # ② VT_ARRAY | VT_R8（SAFEARRAY of double）
    try:
        a1 = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, list(POINT))
        a2 = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, list(NORMAL))
        results["VT_ARRAY|VT_R8"] = try_call("VARIANT(VT_ARRAY|VT_R8, [...])", a1, a2)
    except Exception as exc:
        print("  构造 VT_ARRAY|VT_R8 失败: %s" % str(exc)[:60])

    # ③ VT_ARRAY | VT_VARIANT
    try:
        b1 = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, list(POINT))
        b2 = VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_VARIANT, list(NORMAL))
        results["VT_ARRAY|VT_VARIANT"] = try_call("VARIANT(VT_ARRAY|VT_VARIANT, [...])", b1, b2)
    except Exception as exc:
        print("  构造 VT_ARRAY|VT_VARIANT 失败: %s" % str(exc)[:60])

    # ④ 用 IModeler 自己造点（官方常写成 CreatePoint(Array)）
    try:
        pt = get_com_member(get_modeler(sw), "CreatePoint", VARIANT(
            pythoncom.VT_ARRAY | pythoncom.VT_R8, list(POINT)))
        print("  %-46s → %s" % ("IModeler.CreatePoint(VARIANT array)",
                                "✓ 非 None" if pt is not None else "✗ None"))
        if pt is not None:
            results["CreatePoint 造的点"] = try_call(
                "CreatePlanarSurface(CreatePoint(...), tuple)", pt, NORMAL)
    except Exception as exc:
        print("  %-46s → ✗ %s" % ("IModeler.CreatePoint(...)", str(exc)[:60]))

    print()
    print("=== 汇总结论 ===")
    win = [k for k, v in results.items() if v]
    print("  成功形状: %r" % (win or "（无 —— 需继续换形状试）"))
    if win:
        print("  ⇒ 采用：%s" % win[0])
    print()
    print("  各形状结果：")
    for k, v in results.items():
        print("    %-26s %s" % (k, "✓" if v else "✗"))

    try:
        sw.CloseDoc(title)
    except Exception:
        pass
    print("收尾完成（文档未保存）")
    return 0 if win else 1


if __name__ == "__main__":
    raise SystemExit(main())
