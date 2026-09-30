r"""@brief 判定 `AddRestraint` 的 `DispArray` 在 pywin32 下怎么传（真机）。

官方示例（`_raw\cworksapi\Create_Topology_Study_Example_VBA.txt` L153-158）：
```vb
Set DispatchObj1 = Part.SelectionManager.GetSelectedObject6(1, -1)
Set DispatchObj2 = Part.SelectionManager.GetSelectedObject6(2, -1)
DispArray = Array(DispatchObj1, DispatchObj2)
Set CWRestraintObj = LoadsAndRestraintsManagerObj.AddRestraint(0, (DispArray), Nothing, ErrorCodeObj)
Part.ClearSelection2 True
```
⇒ 第 2 参（`DispArray`）**必须是选中对象组成的 VARIANT 数组**；
   第 3 参（`RefGeom`）官方传 `Nothing`。

⚠ 本脚本要判定的是：**我此前「第 3 参必须包空 Dispatch」的结论是否只在
「第 2 参传了 None」的前提下才成立**。若第 2 参给了真数组，第 3 参或许裸 None 就行。
参数名真源：工作区 `solidpilot-salvage\官方文档\Simulation载荷夹具API签名全表.md`
（`AddRestraint: NRestraintType, DispArray, RefGeom, ErrorCode`）。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_disparray_forms.py
# 定位:   AGENTS.md 铁律 4：官方示例（CHM）+ 参数名表（官方网页）+ 本机实测三源合一。
#         结论回写 scripts/sw_simulation.py 与 scripts/sw_topology.py 的 AddRestraint 调用。
# 官方签名依据: AddRestraint(NRestraintType, DispArray, RefGeom, ErrorCode)；
#         C:\cworks_en\api\Create_Topology_Study_Example_VB.htm
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；不保存任何文档。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

import pythoncom  # noqa: E402
from win32com.client import VARIANT  # noqa: E402

from scripts.sw_connect import (  # noqa: E402
    connect_solidworks,
    create_empty_dispatch_variant,
    get_com_member,
    new_document,
    out_i4,
)
from scripts import sw_part  # noqa: E402


def sel_objects(model, n):
    """取选区里的前 n 个对象（官方示例用 GetSelectedObject6(i, -1)）。"""
    mgr = get_com_member(model, "SelectionManager")
    got = []
    for i in range(1, n + 1):
        try:
            o = get_com_member(mgr, "GetSelectedObject6", i, -1)
        except Exception:
            o = None
        if o is not None:
            got.append(o)
    return got


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=15, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)

        doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                            "CosmosWorks"), "ActiveDoc")
        mgr = get_com_member(doc, "StudyManager")
        n = "DISP_%d" % int(time.time())
        get_com_member(mgr, "DeleteStudy", n)
        study = get_com_member(mgr, "CreateNewStudy3", n, 0, 0, out_i4())  # 0 = static
        print("  静力学研究建成: %r" % (study is not None))
        lrm = get_com_member(study, "LoadsAndRestraintsManager")
        print("  LoadsAndRestraintsManager: %r" % (lrm is not None))
        print()

        # ── 选面（官方路径：SelectByID2 选 → GetSelectedObject6 取）──
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        objs = sel_objects(model, 1)
        print("  选中对象数: %d  （类型 %r）" % (len(objs), type(objs[0]).__name__ if objs else None))
        get_com_member(model, "ClearSelection2", True)
        print()

        def trial(label, fn):
            try:
                r = fn()
                ok = r is not None
                print("  %-58s %s 返回=%s" % (label, "✓" if ok else "○ None", repr(r)[:24]))
                return r
            except Exception as e:
                print("  %-58s ✗ %s" % (label, str(e)[:48]))
                return None

        print("=== 第 2 参（DispArray）的各种形态，第 3 参（RefGeom）固定传裸 None ===")
        # A. 空选区 + None
        trial("A 清选区后：None, None, out_i4()",
              lambda: get_com_member(lrm, "AddRestraint", 0, None, None, out_i4()))
        # B. 有选区 + Python list
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        trial("B 有选区：list(objs), None, out_i4()",
              lambda: get_com_member(lrm, "AddRestraint", 0, list(sel_objects(model, 1)), None, out_i4()))
        # C. 有选区 + tuple
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        trial("C 有选区：tuple(objs), None, out_i4()",
              lambda: get_com_member(lrm, "AddRestraint", 0, tuple(sel_objects(model, 1)), None, out_i4()))
        # D. VARIANT(VT_ARRAY|VT_DISPATCH, [obj])
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        trial("D 有选区：VARIANT(VT_ARRAY|VT_DISPATCH, [o]), None, out_i4()",
              lambda: get_com_member(lrm, "AddRestraint", 0,
                                     VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH,
                                             sel_objects(model, 1)), None, out_i4()))
        # E. 有选区 + list，第 3 参空 Dispatch
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        trial("E 有选区：list(objs), empty_dispatch(), out_i4()",
              lambda: get_com_member(lrm, "AddRestraint", 0, list(sel_objects(model, 1)),
                                     create_empty_dispatch_variant(), out_i4()))
        # F. 无参数实体、只靠选区（有些实现这样）
        sw_part._select_by_id(model.Extension, "", "FACE", append=False, mark=0)
        trial("F 有选区：只传 type + 出参（2 参）",
              lambda: get_com_member(lrm, "AddRestraint", 0, out_i4()))
        print()
        print("  最终 Count（非 0 说明真建上了夹具）: %r" % (get_com_member(lrm, "Count"),))
        return 0
    finally:
        try:
            if title:
                sw.CloseDoc(title)
        except Exception:
            pass
        try:
            sw.CommandInProgress = False
        except Exception:
            pass
        print("收尾完成（文档未保存）")


if __name__ == "__main__":
    raise SystemExit(main())
