r"""@brief 探针：**实体（边/面）能否按名字选**？—— 「按名字选择」解析层的前置实验。

## 为什么这是关键实验
`scripts/sw_part._ensure_sketch_selected` 示范了**按名字选**的形态，但它选的是
**草图特征**（`SelectByID2(name, "SKETCH", 0, 0, 0, …)`）—— 特征有名字，能这样选。

而 C2/C3 那 4 个钣金函数要选的是**边 / 面**（`face_ref` / `path_ref` / `profile_ref`）。
**边和面有没有「名字」？`SelectByID2` 收不收？** 这决定解析层能不能做成一个样子：

- **若能按名字选** ⇒ 解析层收 `selection: str`（名字或 `__current_selection__`），与草图那条**同形**
- **若不能** ⇒ 必须有「名字 → 坐标/对象」的另一条路（如遍历特征树找边、或按序号 + 包围盒）

**⚠ 本会话已两次因为「形状猜错」付出代价**（`CreateMesh` 毫米当米；`GetStudy` 参数个数），
**所以这次先测再写。**

## 安全
只在一个**自建**零件上选择与读回，**不建特征、不改模型**（除了造参照几何）、不保存、跑完关文档。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_entity_select_by_name.py
# 定位:   T-011 §11.3 的 C2/C3 前置实验；也服务 B 类的「选择解析层」。
# 官方签名依据:
#   `IModelDocExtension.SelectByID2(String Name, String Type, Double X, Double Y, Double Z,
#       Boolean Append, Int32 Mark, Callout Callout, Int32 SelectOption) -> Boolean`
#   `IBody2.GetEdges() -> Object` / `IFace2` 的遍历入口
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；零模型改动（只造参照几何）、不保存。
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
from scripts.sw_part import _empty_callout  # noqa: E402  # 已知事实 12


def sel_count(model):
    sm = get_com_member(model, "SelectionManager")
    return int(get_com_member(sm, "GetSelectedObjectCount2", -1) or 0)


def clear(model):
    try:
        get_com_member(model, "ClearSelection2", True)
    except Exception:
        pass


def try_select(model, label, name, kind, x=0.0, y=0.0, z=0.0):
    """试一次 SelectByID2，报告返回值与**回读计数**（返回值不可信，已知事实 8）。"""
    clear(model)
    try:
        ext = get_com_member(model, "Extension")
        # ⚠⚠ `Callout` 必须用 `_empty_callout()`（= `VARIANT(VT_DISPATCH, None)`），
        #   传 `None` 会得到 `'类型不匹配'`（**AGENTS.md 已知事实 12 早就记了，我第一版忘了**）。
        raw = get_com_member(ext, "SelectByID2", name, kind, float(x), float(y), float(z),
                             False, 0, _empty_callout(), 0)
        cnt = sel_count(model)
        print("  %-44s → 返回 %-6r 计数 **%d**" % (label, raw, cnt))
        return cnt
    except Exception as exc:  # noqa: BLE001
        print("  %-44s → ✗ %s" % (label, str(exc)[:56]))
        return -1


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    model = new_document(sw, doc_type="part")
    title = get_com_member(model, "GetTitle")
    sk = sw_part.sketch(model, "Front Plane")
    sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
    sw_part.extrude_boss(model, sk, 0.02)
    print("[参照] 零件 %r（100×60×20 mm 板）" % title)

    results = {}

    print()
    print("=== ① 特征（基准面 / 草图）按名字选 —— 已知可行，作对照 ===")
    results["feature_front_plane"] = try_select(model, 'SelectByID2("Front Plane","PLANE")',
                                                "Front Plane", "PLANE")
    results["feature_sketch"] = try_select(model, 'SelectByID2("Sketch1","SKETCH")',
                                           "Sketch1", "SKETCH")

    print()
    print("=== ② 实体按名字选（核心问题）===")
    for nm, kd in (("Edge1", "EDGE"), ("Edge1", "EDGE"), ("Face1", "FACE"),
                   ("Face1", "FACE"), ("", "EDGE"), ("", "FACE")):
        key = "%s|%s" % (nm or "<空名>", kd)
        if key in results:
            continue
        results[key] = try_select(model, 'SelectByID2(%r,"%s")' % (nm, kd), nm, kd)

    print()
    print("=== ③ 实体按**坐标**选（对照：已知可行，见 sw_simulation.select_face_at）===")
    # 板是 ±0.05 × ±0.03 × 0..0.02；取顶面中心 (0,0,0.02)
    results["face_by_point_zmax"] = try_select(model, "FACE @ (0,0,0.02) 顶面", "", "FACE", 0, 0, 0.02)
    # 一条边的中点（x=0.05, y=-0.03, z=0）
    results["edge_by_point"] = try_select(model, "EDGE @ (0.05,-0.03,0.01) 竖边", "", "EDGE",
                                          0.05, -0.03, 0.01)

    print()
    print("=== ④ 有没有「按名字取实体」的官方入口（遍历特征树找边）===")
    bodies = get_com_member(model, "GetBodies2", 0, True)
    print("  固体体数: %d" % (len(bodies) if bodies else 0))
    if bodies:
        edges = get_com_member(bodies[0], "GetEdges")
        print("  第一个体的边数: %d" % (len(edges) if edges else 0))
        if edges:
            e0 = edges[0]
            for member in ("GetType", "GetID", "GetCurve", "GetCurveParams"):
                try:
                    v = get_com_member(e0, member)
                    print("    edge.%s → %r" % (member, str(v)[:56]))
                except Exception as exc:  # noqa: BLE001
                    print("    edge.%s → ✗ %s" % (member, str(exc)[:44]))
            # `IEntity.Select4(Append, Callout)` —— 用**对象**直接选
            try:
                clear(model)
                ok = get_com_member(e0, "Select4", False, _empty_callout())
                print("    edge.Select4(False, None) → 返回 %r 计数 **%d**"
                      % (ok, sel_count(model)))
                results["edge_select4_by_object"] = sel_count(model)
            except Exception as exc:  # noqa: BLE001
                print("    edge.Select4 → ✗ %s" % str(exc)[:50])

    print()
    print("=== 结论 ===")
    ok_names = [k for k, v in results.items() if v and v > 0]
    print("  计数 > 0 的选法: %r" % ok_names)
    print()
    print("  逐项：")
    for k, v in results.items():
        print("    %-34s %s" % (k, ("✓ 计数 %d" % v) if v and v > 0 else ("✗ %r" % v)))

    try:
        sw.CloseDoc(title)
    except Exception:
        pass
    print("收尾完成（文档未保存）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
