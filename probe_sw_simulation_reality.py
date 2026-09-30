r"""@brief 核实既有 `sw_simulation` 的函数是否真的跑得通（真机）。

背景：`sw_simulation.create_static_study` 用「传裸 0」给出参，而真机实测该写法对
`Int32&` 必然抛 `类型不匹配` ⇒ 怀疑它**从未跑通过**，但 `capabilities.yaml` 里
`simulation_and_fea` 是 `verified`。**声明与事实冲突，必须用实测裁决**（铁律 4/5）。

本脚本只读式地调那几个函数，不改用户模型；收尾不保存。

# ── 来源 ──
# 仓库:   本项目自身（既有代码的事实核查）
# 文件:   D:\AI\SW\probe_sw_simulation_reality.py
# 定位:   AGENTS.md 铁律 2「本机实测」+ 铁律 5「查不到就说查不到」的对应动作：
#         对已声明 verified 的能力做反证尝试。结论回写 capabilities.yaml 的 level 与 evidence。
# 官方签名依据: ICWStudyManager.CreateNewStudy3(String, Int32, Int32, Int32&)
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；不保存任何文档。
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
from scripts import sw_simulation as sim  # noqa: E402


def trial(label, fn):
    try:
        r = fn()
        print("  %-52s ✓ %r" % (label, r))
        return r
    except Exception as e:
        print("  %-52s ✗ %s" % (label, str(e)[:60]))
        return None


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
        print("  已建单实体零件 %r" % title)
        print()

        print("=== ① sw_connect.out_i4 新 helper ===")
        from scripts.sw_connect import out_i4
        v = trial("out_i4() 构造", lambda: out_i4())
        print()

        print("=== ② 既有 sw_simulation.create_static_study（传裸 0 的老写法）===")
        study = trial("create_static_study(sw, 'REALITY_CHECK')",
                      lambda: sim.create_static_study(sw, "REALITY_CHECK"))
        print()

        print("=== ③ 若 ② 失败：绕开它，直接用正确出参形态建同类研究 ===")
        try:
            doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                                "CosmosWorks"), "ActiveDoc")
            mgr = get_com_member(doc, "StudyManager")
            s2 = trial("CreateNewStudy3(name, 0=static, 0, out_i4())",
                       lambda: get_com_member(mgr, "CreateNewStudy3", "STATIC_VIA_OUTI4", 0, 0, out_i4()))
            if s2 is not None:
                print("     ⇒ 用正确出参形态，**静态研究建成了** ⇒ ②失败纯属出参写法")
        except Exception as exc:
            print("  ✗ 绕行也失败: %s" % str(exc)[:70])
        print()

        print("=== ④ apply_fixed_restraint（它依赖建好的研究 + 选区）===")
        if study is not None:
            trial("apply_fixed_restraint(study)", lambda: sim.apply_fixed_restraint(study))
        else:
            print("  ○ 跳过：②没建成研究，无对象可施夹具")
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
