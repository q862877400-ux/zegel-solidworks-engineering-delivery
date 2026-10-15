r"""@brief 裁决「裸 None 当 Dispatch 参数」的正确形态（真机）。

已知事实 12 说空 Dispatch 参数要包 `VARIANT(VT_DISPATCH, None)`
（`sw_connect.create_empty_dispatch_variant()`），但 `sw_simulation` 的
`AddRestraint` / `AddForce` 传的是**裸 None**，真机实测在第 3 参抛「类型不匹配」。
本脚本把候选形态逐一试，**用实测裁决**。

# ── 来源 ──
# 仓库:   本项目自身（判据裁决实测）
# 文件:   D:\AI\SW\probe_dispatch_variant.py
# 定位:   AGENTS.md 已知事实 12 在运行期的验证；结论回写 sw_simulation 与 signature-audit.md。
# 官方签名依据: ICWLoadsAndRestraintsManager.AddRestraint(Int32, Object, Object, Int32&)
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

from scripts.sw_connect import (  # noqa: E402
    connect_solidworks,
    create_empty_dispatch_variant,
    get_com_member,
    new_document,
    out_i4,
)
from scripts import sw_part  # noqa: E402


def trial(label, fn):
    try:
        r = fn()
        print("  %-46s ✓ %r" % (label, r))
        return r
    except Exception as e:
        print("  %-46s ✗ %s" % (label, str(e)[:56]))
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

        doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                            "CosmosWorks"), "ActiveDoc")
        mgr = get_com_member(doc, "StudyManager")
        study = get_com_member(mgr, "CreateNewStudy3", "DISP_%d" % int(time.time()), 0, 0, out_i4())
        print("  已建静力学研究: %r" % bool(study))
        lrm = get_com_member(study, "LoadsAndRestraintsManager")
        print("  LoadsAndRestraintsManager: %r" % bool(lrm))
        print()

        empty = create_empty_dispatch_variant()
        print("=== ① SelectByID2 的 Callout 参数（第 8 参）===")
        trial("A 裸 None", lambda: get_com_member(model.Extension, "SelectByID2",
              "", "FACE", 0, 0, 0.01, False, 0, None, 0))
        trial("B empty_dispatch()", lambda: get_com_member(model.Extension, "SelectByID2",
              "", "FACE", 0, 0, 0.01, False, 0, create_empty_dispatch_variant(), 0))
        sel_n = get_com_member(get_com_member(model, "SelectionManager"), "GetSelectedObjectCount2", -1)
        print("     选区计数 = %r" % sel_n)
        print()

        print("=== ② AddRestraint 的两个 Object 参数（第 2、3 参）===")
        trial("A None, None（现状）",
              lambda: get_com_member(lrm, "AddRestraint", 0, None, None, out_i4()))
        trial("B empty_dispatch(), None",
              lambda: get_com_member(lrm, "AddRestraint", 0, create_empty_dispatch_variant(), None, out_i4()))
        trial("C None, empty_dispatch()",
              lambda: get_com_member(lrm, "AddRestraint", 0, None, create_empty_dispatch_variant(), out_i4()))
        trial("D empty_dispatch(), empty_dispatch()",
              lambda: get_com_member(lrm, "AddRestraint", 0, create_empty_dispatch_variant(),
                                     create_empty_dispatch_variant(), out_i4()))
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
        print("  收尾完成（文档未保存）")


if __name__ == "__main__":
    raise SystemExit(main())
