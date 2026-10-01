r"""@brief 探针：`CreateDefinition(fm)` 与 `AccessSelections` 到底成不成（**不吞异常**）。

## 要回答的两个问题
1. `CreateDefinition(3)`（Draft）/ `(33)`（OneBend）返回 **None** —— 这两个类型
   是不是根本不走 `CreateDefinition`？（反射里有专用的
   `InsertSheetMetal3dBend` / `IInsertSheetMetalEdgeFlange2` / `InsertGussetFeature3`）
2. `AccessSelections(TopDoc, Component)` 的 `Component` 该传什么？
   ⚠ 第一版传了 Python `None`，调用被 `try/except` **悄悄吞掉** ⇒ 表现为「修了但没变化」。
   **已知事实 12/33 说空 Dispatch 要传 `VARIANT(VT_DISPATCH, None)`** —— 本探针逐个试。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_featuredata_access.py
# 定位:   `scripts/sw_sheet_metal.py` 里 4 个真机失败函数的**根因第二层**。
# 官方签名依据: `AccessSelections(System.object TopDoc, System.object Component) -> System.bool`
#         （`C:\swapi\types\IEdgeFlangeFeatureData\AccessSelections.md` 及同族）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；只造参照几何、不保存。
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
from scripts import sw_sheet_metal as SM  # noqa: E402
from scripts.sw_selection_spec import resolve_selection  # noqa: E402

FM = ((34, "BaseFlange"), (37, "EdgeFlange"), (118, "Gusset"), (3, "Draft"), (33, "OneBend"))


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        SM.create_base_flange(model, "Sketch1",
                              SM.BaseFlangeSpec(thickness=0.002, bend_radius=0.002,
                                                depth=0.05))
        print("[1] 参照：已建基体法兰的零件 %r" % title)

        print()
        print("=== ① `CreateDefinition(fm)` 对每个 fm 是否返回对象 ===")
        mgr = get_com_member(model, "FeatureManager")
        defs = {}
        for fm, label in FM:
            try:
                d = get_com_member(mgr, "CreateDefinition", fm)
                defs[fm] = d
                print("  CreateDefinition(%-3d) [%-10s] → %s"
                      % (fm, label, "✓ 非 None" if d is not None else "✗ **None**"))
            except Exception as exc:  # noqa: BLE001
                defs[fm] = None
                print("  CreateDefinition(%-3d) [%-10s] → ✗ %s" % (fm, label, str(exc)[:52]))

        print()
        print("=== ② `AccessSelections(TopDoc, Component)` 的 Component 该传什么 ===")
        # 先选一个面，让「引用类特征」有东西可接管
        try:
            resolve_selection(model, "index:0", "FACE")
            print("  （已选一个面，计数 %d）" % 1)
        except Exception as exc:  # noqa: BLE001
            print("  ⚠ 选面失败: %s" % str(exc)[:56])
        candidates = (("Python None", None),
                      ("_empty_callout()", sw_part._empty_callout()),
                      ("False", False))
        for fm, label in FM:
            d = defs.get(fm)
            if d is None:
                continue
            fn = getattr(d, "AccessSelections", None)
            if not callable(fn):
                print("  [%s] 没有可调用的 AccessSelections" % label)
                continue
            for cl, comp in candidates:
                try:
                    r = fn(model, comp)
                    print("  [%-10s] AccessSelections(%-16s) → %r" % (label, cl, r))
                except Exception as exc:  # noqa: BLE001
                    print("  [%-10s] AccessSelections(%-16s) → ✗ %s"
                          % (label, cl, str(exc)[:48]))

        print()
        print("=== ③ 官方反射里的**专用**入口（若 ② 仍不成，说明要改用它们）===")
        for name in ("InsertSheetMetal3dBend", "IInsertSheetMetalEdgeFlange2",
                     "InsertGussetFeature3", "InsertSheetMetalBaseFlange2",
                     "InsertSheetMetalEdgeFlange2"):
            v = getattr(mgr, name, "MISSING")
            print("  %-32s → %s" % (name, ("缺失" if v == "MISSING" else "存在")))

        print()
        print("=== 结论 ===")
        none_fm = [("%d(%s)" % (fm, lb)) for fm, lb in FM if defs.get(fm) is None]
        print("  CreateDefinition 返回 None 的: %r" % (none_fm or "无"))
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
