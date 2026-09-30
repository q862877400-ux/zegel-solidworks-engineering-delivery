r"""@brief 找出 `Int32&` 出参在 pywin32 迟到绑定下的正确传法（真机裁决）。

背景：`CreateNewStudy3(String, Int32, Int32, Int32&)` 的第 4 参是出参。
实测两种常见写法都失败：
    传占位 0   → 类型不匹配（0 不是 VARIANT）
    省略       → 「非选择性的参数」（该参必需，不能省）
⇒ 必须传 VARIANT。本脚本把候选形态逐一在真机上试，**用实测裁决，不猜**。

⚠ 这条结论同时影响既有代码：`scripts/sw_simulation.py` 的 `create_static_study`
用的是「传占位 0」，按本实测它**必然同样失败** —— 即该函数从未真正跑通过。

# ── 来源 ──
# 仓库:   本项目自身（判据裁决实测）
# 文件:   D:\AI\SW\probe_outparam_convention.py
# 定位:   AGENTS.md 铁律 4「冲突时以出厂类型库的反射为准」在**运行期**的对应物：
#         静态 arity 说不清 out 参数怎么传，只能实测。结论回写 docs/signature-audit.md。
# 官方签名依据: D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt 的 CreateNewStudy3
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

from scripts.sw_connect import connect_solidworks, get_com_member, new_document  # noqa: E402
from scripts import sw_part  # noqa: E402

TOPOLOGY_STATIC = 13


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=10, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        addin = get_com_member(sw, "GetAddInObject", "SldWorks.Simulation")
        doc = get_com_member(get_com_member(addin, "CosmosWorks"), "ActiveDoc")
        mgr = get_com_member(doc, "StudyManager")
        n = int(time.time())

        def trial(label, fn):
            try:
                r = fn()
                print("  %-50s ✓ 返回=%r" % (label, r))
                return r
            except Exception as e:
                print("  %-50s ✗ %s" % (label, str(e)[:58]))
                return None

        print("=== 候选形态（CreateNewStudy3(name, 13, 0, <出参>)）===")
        trial("A VARIANT(VT_BYREF|VT_I4, 0)",
              lambda: get_com_member(mgr, "CreateNewStudy3", "T%s_A" % n, TOPOLOGY_STATIC, 0,
                                     VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)))
        trial("B VARIANT(VT_I4, 0)",
              lambda: get_com_member(mgr, "CreateNewStudy3", "T%s_B" % n, TOPOLOGY_STATIC, 0,
                                     VARIANT(pythoncom.VT_I4, 0)))
        trial("C VARIANT(VT_BYREF|VT_VARIANT, 0)",
              lambda: get_com_member(mgr, "CreateNewStudy3", "T%s_C" % n, TOPOLOGY_STATIC, 0,
                                     VARIANT(pythoncom.VT_BYREF | pythoncom.VT_VARIANT, 0)))
        trial("D 空 VARIANT(VT_EMPTY, None)",
              lambda: get_com_member(mgr, "CreateNewStudy3", "T%s_D" % n, TOPOLOGY_STATIC, 0,
                                     VARIANT(pythoncom.VT_EMPTY, None)))
        trial("E 用 dispatch 包的 int",
              lambda: get_com_member(mgr, "CreateNewStudy3", "T%s_E" % n, TOPOLOGY_STATIC, 0, 0.0))

        print()
        print("=== 对照：CreateNewStudy2(name, 13, <出参>) ===")
        trial("F VARIANT(VT_BYREF|VT_I4, 0)",
              lambda: get_com_member(mgr, "CreateNewStudy2", "T%s_F" % n, TOPOLOGY_STATIC,
                                     VARIANT(pythoncom.VT_BYREF | pythoncom.VT_I4, 0)))

        print()
        count = get_com_member(mgr, "StudyCount")
        print("  StudyCount 最终 = %r  （>0 说明某形态成功了）" % count)
        if count:
            for i in range(int(count)):
                s = get_com_member(mgr, "GetStudy", i)
                print("     研究[%d] Name=%r AnalysisType=%r"
                      % (i, get_com_member(s, "Name"), get_com_member(s, "AnalysisType")))
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
