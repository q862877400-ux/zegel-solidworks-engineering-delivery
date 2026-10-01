"""给可达性审计补 **Simulation 对象族**（第一版只有 10 个通用对象 ⇒ 86% 假阳性）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁，非第三方移植）
# 文件:   D:\\AI\\SW\\patch_reachability_sim.py
# 定位:   第一版 `tools/audit_runtime_reachability.py` 只构造 10 个**通用**对象
#         ⇒ 424 个成员里报了 365 个「不可达」（**86%，明显是假阳性**）：
#         因为 `AddForce` / `BeginEdit` / `ActiveStudy` 等挂在 **Simulation 的对象族**上
#         （`ICWModelDoc` / `ICWStudyManager` / `ICWStudy` / `ICWLoadsAndRestraintsManager` /
#          `ICWTopologyStudyManager` / `ICWMesh` / `ICWResults`），而那 10 个里没有它们。
#         **⇒ 工具的输出上限就是对象集。** 本补丁把 Simulation 族加进去 ——
#         构造它们的知识来自本项目已跑通的探针（拓扑闭环、仿真整链）。
# 官方签名依据: 不适用（只 getattr，不调方法）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

TOOL = Path(r"C:\swprojects\sw-skill-fork\tools\audit_runtime_reachability.py")

OLD = '''    objs["IModeler"] = safe(sw, "GetModeler")
    try:
        addin = get_com_member(sw, "GetAddInObject", "SldWorks.Simulation")
        objs["ISldWorks.Simulation"] = addin
    except Exception:
        objs["ISldWorks.Simulation"] = None
    return objs
'''

NEW = '''    objs["IModeler"] = safe(sw, "GetModeler")

    # ── Simulation 对象族（2026-10-01 补）────────────────────────────
    # ⚠ 第一版只有上面那 10 个通用对象 ⇒ 424 个成员里 365 个报「不可达」（86%），
    #   **那是假阳性**：这些成员挂在 Simulation 的对象族上，通用对象里没有它们。
    #   **⇒ 本工具的输出上限就是对象集** —— 缺一族就多一片假阳性。
    #   下面这族的构造方式来自本项目**已跑通**的探针
    #   （`probe_topology_loop.py` / `capture_simulation_evidence.py`）。
    try:
        addin = get_com_member(sw, "GetAddInObject", "SldWorks.Simulation")
        objs["ISldWorks.Simulation"] = addin
        cosmos = safe(addin, "CosmosWorks") if addin is not None else None
        objs["ICosmosWorks"] = cosmos
        cw_doc = safe(cosmos, "ActiveDoc")
        objs["ICWModelDoc"] = cw_doc
        mgr = safe(cw_doc, "StudyManager")
        objs["ICWStudyManager"] = mgr
        # 取一个研究（第一个），再挂它的子对象
        study = None
        if mgr is not None:
            try:
                studies = get_com_member(mgr, "GetStudyCount")
                if studies:
                    from scripts.sw_connect import out_i4
                    study = get_com_member(mgr, "GetStudy", 0, out_i4())
            except Exception:
                study = None
        objs["ICWStudy"] = study
        if study is not None:
            objs["ICWMesh"] = safe(study, "Mesh")
            objs["ICWLoadsAndRestraintsManager"] = safe(study, "LoadsAndRestraintsManager")
            objs["ICWTopologyStudyManager"] = safe(study, "TopologyStudyManager")
            objs["ICWTopologyStudyOptions"] = safe(study, "TopologyStudyOptions")
            objs["ICWResults"] = safe(study, "Results")
            objs["ICWSolidManager"] = safe(study, "SolidManager")
    except Exception:
        pass
    return objs
'''

OLD_COUNT = '''    print("静态抽取：`scripts/sw_*.py` 里 get_com_member 用到的成员名 **%d** 个"
          % len(members))'''
NEW_COUNT = '''    print("静态抽取：`scripts/sw_*.py` 里 get_com_member 用到的成员名 **%d** 个"
          % len(members))
    print("⚠ 本审计的**上限就是对象集**：缺一族对象，那一族的成员就全报「不可达」（假阳性）。")
    print("  2026-10-01 的教训：第一版只有 10 个通用对象 ⇒ 365/424 报不可达（86%），"
          "几乎全是假阳性。")'''


def main() -> int:
    t = TOOL.read_text(encoding="utf-8")
    if OLD not in t:
        print("  ✗ 未匹配 build_objects 的尾部")
        return 1
    t = t.replace(OLD, NEW, 1)
    t = t.replace(OLD_COUNT, NEW_COUNT, 1)
    TOOL.write_text(t, encoding="utf-8")
    print("  ✓ 已补 Simulation 对象族；并在输出里写明「上限就是对象集」")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
