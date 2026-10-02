"""示例 09: 原生钣金全流程（基体法兰 → 扫掠法兰 → 证据回读）

对应官方示例
------------
``C:\\swapi\\examples\\Create_Swept_Flange_Example_VBNET.md``
（VB.NET，96 行；另有 CSharp 版）

本示例是该 VB 示例的 **Python 迟到绑定翻译**，并按官方调用序列逐行对齐：
    1) InsertSheetMetalBaseFlange2 建基体法兰     ← 扫掠法兰的前置
    2) 选轮廓草图 → GetSelectedObject6 → ClearSelection2
    3) 选路径边   → GetSelectedObject6 → ClearSelection2
    4) CreateDefinition(swFmSweptFlange)
    5) 逐个设 14 个属性
    6) CreateFeature(featData)

⚠ 本文件是**文档与参考实现**，编写过程中未在本机运行（见 AGENTS.md 铁律 2）：
  它会连接并驱动真实 SolidWorks。首次使用前请自行核对官方示例与本仓库
  `scripts/sw_sheet_metal.py` 的签名（`docs/signature-audit.md` 有比对表）。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 使用示例（非开源项目，无第三方许可）
# 文件:   C:\swapi\examples\Create_Swept_Flange_Example_VBNET.md
#         另见 C:\swapi\examples\Create_Swept_Flange_Example_CSharp.md
# 定位:   本文件是上面那份 VB.NET 示例的 Python 迟到绑定翻译。
#         官方序列（第 37-88 行）→ 本文件 main() 的步骤编号一一对应：
#           官方 37-53  InsertSheetMetalBaseFlange2   → 本文件 步骤 1
#           官方 60-66  选轮廓草图 + GetSelectedObject6 → 本文件 步骤 2
#           官方 68-71  选路径边   + GetSelectedObject6 → 本文件 步骤 3
#           官方 73     CreateDefinition(swFmSweptFlange) → 本文件 步骤 4
#           官方 74-87  设 14 个属性                  → 本文件 步骤 5
#           官方 88     CreateFeature(swFeatData)      → 本文件 步骤 6
# 官方未采用: 官方这条路径**不**调 AccessSelections / ReleaseSelectionAccess
#         （那是 Access_Selections_Example 那类"编辑既有特征"才需要的），
#         故本文件同样不调。
# 被调用的实现: scripts/sw_sheet_metal.py::create_base_flange
#              scripts/sw_sheet_metal.py::create_swept_flange
#              scripts/sw_sheet_metal.py::BaseFlangeSpec / SweptFlangeSpec
#              scripts/sw_part.py::_select_by_id
# 覆盖:   全文件 —— 本文件是自包含示例，各步骤注释已就地标明对应的官方行号。
# ⚠ 本文件为静态翻译，未在本机实测（见 AGENTS.md 铁律 2）
# ⚠ 本文件会连接并驱动真实 SolidWorks，编写过程中未运行过。
# ────────────────────────────────────────────────────────────────────
import sys

sys.path.insert(0, r"../scripts")

from sw_connect import connect_solidworks, new_document  # noqa: E402
from sw_part import _select_by_id  # noqa: E402
from sw_sheet_metal import (  # noqa: E402
    BaseFlangeSpec,
    SweptFlangeSpec,
    create_base_flange,
    create_swept_flange,
    sheet_metal_evidence,
)


def main():
    # ── 0. 连接 ────────────────────────────────────────────────────
    # ⚠ 本函数会启动/附着 SolidWorks。编写与核对本示例的过程中**没有执行过**它。
    # connect_solidworks() 返回 (sw, model) —— 见 scripts/sw_connect.py:287。
    # 返回的 model 可能是 None（取决于是否有可复用的活动文档），
    # 故下面的「新建零件」在 model 为空时才建。
    print("连接 SolidWorks...")
    sw, model = connect_solidworks()

    if model is None:
        print("新建零件文档...")
        model = new_document(sw, "part")
    else:
        print(f"复用活动文档: {model.GetTitle()}")

    # ── 1. 步骤 1 · 基体法兰（官方第 53 行 InsertSheetMetalBaseFlange2）──
    # 官方先建基体法兰再建扫掠法兰。厚度与 K 因子都落在基体上，
    # 扫掠法兰默认从基体继承（UseMaterialSheetMetalParameters）。
    print("步骤 1 · 建基体法兰（扫掠法兰的前置）...")
    # ⚠ 实际使用时应先画一张草图并选中它；草图画法见 examples/01_basic_part.py。
    #   官方示例的顺序是：InsertSketch(True) → SelectByID2("Front","PLANE",...)
    #   → 画轮廓 → CreateCornerRectangle → ClearSelection2 → 建基体法兰。
    #   这里从「草图已画好且被选中」接手，与 scripts/sw_sheet_metal.py 的
    #   create_base_flange 约定一致（它内部会调 _ensure_sketch_selected）。
    base = create_base_flange(
        model,
        "Sketch1",                      # 已选中的草图名
        BaseFlangeSpec(
            thickness=0.001,              # 1 mm
            bend_radius=0.001,
            depth=0.02,
            k_factor=0.5,                 # 官方示例用 0.5
            relief_ratio=0.5,
        ),
    )
    print(f"  基体法兰已建: {base}")

    # ── 2. 步骤 2 · 选轮廓草图（官方第 60-66 行）───────────────────
    # 官方：SelectByID2("Sketch6","SKETCH",...) → GetSelectedObject6(1,-1)
    #      → ClearSelection2(True)
    # ⚠ _select_by_id 的第一个参数是 **Extension** 不是 model ——
    #   见 scripts/sw_part.py:66 的签名与 :762/:805 的上游用法。
    print("步骤 2 · 选轮廓草图...")
    _select_by_id(model.Extension, "Sketch6", "SKETCH")
    profile = model.SelectionManager.GetSelectedObject6(1, -1)
    model.ClearSelection2(True)

    # ── 3. 步骤 3 · 选路径边（官方第 68-71 行）────────────────────
    # 官方用 SelectByRay 选边；此处沿用上游 sw_part._select_by_id 的
    # SelectByID2 写法（铁律 3：沿用既有惯例，不自创选区方式）。
    print("步骤 3 · 选路径边...")
    _select_by_id(model.Extension, "Edge1", "EDGE")
    path = model.SelectionManager.GetSelectedObject6(1, -1)
    model.ClearSelection2(True)

    # ── 4-6. 步骤 4/5/6 · 建扫掠法兰 ─────────────────────────────
    # 官方把 14 个属性逐条设完再 CreateFeature。create_swept_flange 内部
    # 已按官方示例对齐（见其来源块），thickness 传 None 即表示
    # 「继承基体法兰」，这正是官方的默认行为。
    print("步骤 4-6 · 建扫掠法兰...")
    flange = create_swept_flange(
        model,
        path_ref=path,
        profile_ref=profile,
        spec=SweptFlangeSpec(
            start_offset=0.0,             # 官方 StartOffset = 0
            end_offset=0.0,               # 官方 EndOffset = 0
            thickness=None,               # 官方不设 → 从基体法兰继承
            use_default_radius=True,      # 官方 UseDefaultRadius = False，
                                          # 改 True 以免 BendRadius 越界；见下方注
            flange_position=1,            # swSweptFlangePositionType_MaterialInside
            flatten_along_path=False,     # 官方 False
            trim_side_bends=False,        # 官方 False
            use_default_bend_relief=True, # 官方 True
            use_gauge_table=False,        # 官方 False
            use_material_parameters=False,        # 官方 False
            override_default_sheet_metal_parameters=False,  # 官方 False
            reverse_direction=False,      # 官方 False
        ),
    )
    print(f"  扫掠法兰已建: {flange}")

    # ── 7. 证据回读 ────────────────────────────────────────────────
    print("回读钣金证据...")
    evidence = sheet_metal_evidence(model)
    print(f"  特征类型      : {evidence['feature_types']}")
    print(f"  基体法兰参数  : {evidence['base_flange_parameters']}")
    print(f"  是否全为钣金体: {evidence['all_solid_bodies_are_sheet_metal']}")
    return evidence


# ⚠ 与官方示例的唯一刻意偏差（已在上面 create_swept_flange 调用处标注）:
#   官方设 UseDefaultRadius = False，本示例设 True。
#   原因是本仓库的 SweptFlangeSpec 在 use_default_radius=False 时会把
#   bend_radius 写进 FeatureData，而默认 bend_radius=0；官方示例同样
#   没设 BendRadius，靠 SolidWorks 自己的默认值兜底。此处取 True 更稳，
#   但**这属于本示例的工程判断，不是官方要求**，请按自己的需要复核。


if __name__ == "__main__":
    main()
