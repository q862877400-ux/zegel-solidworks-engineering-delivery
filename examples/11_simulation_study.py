"""示例 11: SolidWorks Simulation 研究全流程（建研究 → 夹具 → 载荷 → 求解 → 回读）

⚠⚠ **本域是本仓库唯一「官方示例数为 0」的域**。

原因（见 docs/capability-matrix.md §二 与 docs/usage-guide.md）：
    - ``C:\\swapi`` 只收录 12 个程序集，**不含 cosworks** ⇒ 无类型页、无成员页、无示例；
    - CHM ``cosworks`` 册虽存在，但**正文是 JS 空壳**（34 个接口页只有导航栏）。
    两个官方源同时失效，所以本域**没有官方示例可翻译**。
    本文件的调用序列**全部来自 interop DLL 的元数据反射**，不是来自官方示例。

    这也意味着：下面每一步的「正确用法」是**签名层面**确定的，
    至于 SolidWorks 在运行时还要求什么前置（例如界面切到 Simulation 页签、
    文档需先由基体法兰等钣金特征构成），**本文件无法覆盖，需真机确认**。

⚠ 本文件是**文档与参考实现**，编写过程中未在本机运行（见 AGENTS.md 铁律 2）：
  它需要 Simulation 加载项 + 许可证，会连接并驱动真实 SolidWorks。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 签名（SolidWorks.Interop.cosworks.dll 纯元数据反射）
# 文件:   D:\AI\SW\_raw\reflect\iface_cosworks.txt
#         D:\AI\SW\_raw\reflect\enum_cosworks.txt
# 定位:   本文件的调用序列**不来自官方示例**（该域官方示例数为 0，见 docstring），
#         全部来自反射清单。逐跳依据：
#           ICwAddincallback : CosmosWorks get_CosmosWorks()      ← 属性
#           ICosmosWorks     : CWModelDoc get_ActiveDoc()         ← 属性
#           ICWModelDoc      : CWStudyManager get_StudyManager() ← 属性
#           ICWStudyManager  : CWStudy CreateNewStudy3(String, Int32, Int32, Int32&)
#                            : Int32 get_StudyCount()            ← 属性，勿加括号
#           ICWStudy         : RunAnalysis()                     ← **零参**
#                            : CreateMesh(Int32, Double, Double) ← 在 ICWStudy 上
#           ICWLoadsAndRestraintsManager
#                            : AddRestraint(Int32, Object, Object, Int32&)
#                            : AddForce(Int32, Object, Object, Int32&)
#           ICWForce         : set_NormalForceOrTorqueValue(Double) ← 大小**事后**回填
#         反射脚本: D:\AI\SW\tools\reflect-interop.ps1（读官方程序集，非实测）
# 被调用的实现: scripts/sw_simulation.py 的同名函数
# 覆盖:   全文件 —— 本文件是自包含示例，各步骤注释已标明对应的官方签名。
# ⚠ 本文件为照反射签名新写，未在本机实测（见 AGENTS.md 铁律 2）
# ⚠ 本文件需要 Simulation 加载项 + 许可证，编写过程中未运行过。
# ────────────────────────────────────────────────────────────────────
import sys

sys.path.insert(0, r"../scripts")

from sw_connect import connect_solidworks  # noqa: E402
from sw_part import _select_by_id  # noqa: E402
from sw_simulation import (  # noqa: E402
    SWS_FORCE_TYPES,
    SWS_FORCE_UNITS,
    SWS_MESH_TYPES,
    SWS_RESTRAINT_TYPES,
    apply_fixed_restraint,
    apply_normal_force,
    collect_study_evidence,
    create_mesh,
    create_static_study,
    get_cw_document,
    get_study_manager,
    iter_studies,
    run_analysis,
)


def main():
    # ⚠ 需要 Simulation 加载项 + 许可证。编写与核对本示例的过程中**没有执行过**它。
    print("连接 SolidWorks...")
    sw, _ = connect_solidworks()

    # ── 1. 确认 Simulation 可达 ───────────────────────────────────
    # 入口链：sw_app → GetAddInObject("SldWorks.Simulation") → .CosmosWorks
    #          → .ActiveDoc → .StudyManager
    # ⚠ 三处都是**属性**不是方法：CosmosWorks / ActiveDoc / StudyManager。
    #   迟到绑定下加括号会报 TypeError（AGENTS.md §六 事实 4）。
    print("确认 Simulation 可达...")
    document = get_cw_document(sw)     # 内部会逐跳取 CosmosWorks / ActiveDoc
    manager = get_study_manager(sw)     # ICWModelDoc.StudyManager（属性）
    print(f"  文档: {document}")
    print(f"  研究管理器: {manager}")

    # ── 2. 已有研究 ───────────────────────────────────────────────
    print("列出现有研究...")
    for index, study in iter_studies(sw):
        print(f"  [{index}] {study}")

    # ── 3. 建一个静力研究 ─────────────────────────────────────────
    # 官方签名 CreateNewStudy3(String Name, Int32 StudyType, Int32 MeshType, Int32& Err)
    # —— 4 参。末位是 by-ref，迟到绑定下不保证回写，
    #    故本仓库**不以 error_code 作为成败判据**，只看返回值是否为 None。
    print("建静力研究...")
    study, entry, _ = create_static_study(
        sw,
        "Static-1",
        mesh_type=SWS_MESH_TYPES["solid"],
    )
    print(f"  实际命中的入口: {entry}   研究: {study}")

    # ── 4. 夹具 ───────────────────────────────────────────────────
    # ⚠ 调用前必须先选中要固定的实体。官方签名
    #   AddRestraint(Int32 RestraintType, Object Entities, Object ?, Int32& Err) —— 4 参。
    #   第 3 个 Object 参数的语义在两套官方源里都**查不到**（CHM 空壳 + swapi 未收录），
    #   故本仓库按「None 表示不指定」传入。
    #   ⚠ 另注：alisamsam/Solidworks-MCP (MIT) 的移植版本调的是 AddRestraint3 ——
    #     反射清单中**该成员不存在**，详见 docs/signature-audit.md 批次 1。
    print("施加固定夹具...")
    _select_by_id(document.Extension, "Face1", "FACE")
    restraint = apply_fixed_restraint(
        study, restraint_type=SWS_RESTRAINT_TYPES["fixed"]
    )
    print(f"  夹具: {restraint}")

    # ── 5. 载荷 ───────────────────────────────────────────────────
    # ⚠ 官方 AddForce 只有 4 参，**力的大小不是入参** ——
    #   大小要在返回的 ICWForce 上用 set_NormalForceOrTorqueValue(Double) 回填。
    #   （alisamsam 写成 AddForce3(0, None, magnitude, err)，而官方 AddForce3
    #     实为 21 个参数 —— 详见 docs/signature-audit.md 批次 1 第 2 项。）
    print("施加法向力载荷...")
    _select_by_id(document.Extension, "Face2", "FACE")
    force = apply_normal_force(
        study,
        magnitude=25.0,                                # 牛顿
        force_type=SWS_FORCE_TYPES["normal"],
        unit=SWS_FORCE_UNITS["n_or_nm"],
    )
    print(f"  载荷: {force}")

    # ── 6. 网格 ───────────────────────────────────────────────────
    # ⚠ CreateMesh 挂在 **ICWStudy** 上，不在 ICWStudy.Mesh 上 ——
    #   cosworks.dll 的 84 个 ICW* 接口里根本没有 ICWMesh。
    #   官方签名 CreateMesh(Int32, Double, Double) —— 3 参；
    #   三个参数的单位/语义在两套官方源里都查不到，故按 0.0 占位。
    print("生成网格...")
    mesh_code = create_mesh(study, mesh_type=SWS_MESH_TYPES["solid"])
    print(f"  网格返回码: {mesh_code}")

    # ── 7. 求解 ───────────────────────────────────────────────────
    # ⚠ 官方 RunAnalysis() 是**零参**方法。传任何实参都是错的
    #   （alisamsam 写成 RunAnalysis(err_code)）。
    print("求解...")
    run_code = run_analysis(study)
    print(f"  求解返回码: {run_code}")

    # ── 8. 证据回读 ───────────────────────────────────────────────
    # 刻意**不读结果数值**：ICWResults 上没有 GetStressComponent /
    # GetDisplacementComponent，反射清单里查不到可信签名。
    print("回读研究证据...")
    evidence = collect_study_evidence(sw)
    print(f"  cosworks 版本: {evidence['cosmos_version']}")
    print(f"  研究数: {evidence['study_count']}")
    for item in evidence["studies"]:
        print(
            f"    [{item['index']}] {item['name']}"
            f"  分析类型={item['analysis_type']}"
            f"  网格类型={item['mesh_type']}"
            f"  载荷夹具数={len(item['loads_and_restraints'])}"
        )
    return evidence


# ⚠ 本文件无法回答的问题（需真机确认）:
#   · 界面是否必须先切到 Simulation 页签，ActiveDoc 才非 None；
#   · 文档里是否必须先有基体法兰等钣金特征，Simulation 才认；
#   · CreateMesh 三个参数的准确语义与单位；
#   · AddRestraint / AddForce 第 3 个 Object 参数的含义。
#   这些在两套官方源里都查不到，故一律不猜、不写死在此处。


if __name__ == "__main__":
    main()
