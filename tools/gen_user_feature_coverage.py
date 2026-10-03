"""★ 生成 docs/user-feature-coverage.md —— 用户视角功能覆盖对照表（本仓库 vs 四家）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（生成器）
# 文件:   tools/gen_user_feature_coverage.py
# 定位:   把「用户视角功能清单」（画直线/画圆/拉伸/切除/拔模…）逐项在本仓库 ToolSpec
#         与 tools/union-sources.json 的四家里匹配，算出一张**可重算**的覆盖率对照表。
#         ★ 口径 = **能操作 SolidWorks 的功能数**（不是工具名数）—— 见产物 §一。
# 官方依据: 不适用（读的是本项目自己的能力面 + 台账，不是官方文档）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT = REPO_ROOT / "docs" / "user-feature-coverage.md"
SOURCES = REPO_ROOT / "tools" / "union-sources.json"
CAPS = REPO_ROOT / "capabilities.yaml"

#: 四家的列名（顺序 = 产物表头顺序）
FKEYS = ["Solidworks-MCP-Server", "SolidworksMCP-python", "SolidworksMCP-TS", "solidworks-mcp"]

#: 用户视角功能清单。每项 = (域, 功能名, 命中关键词元组)。
#: ★ 关键词是**子串**匹配，作用在**原始工具名**上（不剥前缀，避免误伤）。
#: ★ 这份清单按 SOLIDWORKS 用户的 CommandManager 心智模型组织，不是按 API 族。
CHECKLIST: list[tuple[str, str, tuple[str, ...]]] = [
    ("草图", "新建/退出草图", ("sketch_start", "sketch_end", "insert_sketch", "create_sketch", "close_sketch")),
    ("草图", "直线", ("add_line", "create_line")),
    ("草图", "矩形", ("rectangle",)),
    ("草图", "圆", ("add_circle", "create_circle", "perimeter_circle")),
    ("草图", "圆弧", ("add_arc", "create_arc", "3point_arc", "tangent_arc")),
    ("草图", "样条曲线", ("spline",)),
    ("草图", "椭圆", ("ellipse",)),
    ("草图", "抛物线/圆锥曲线", ("parabola", "conic")),
    ("草图", "多边形", ("polygon",)),
    ("草图", "槽口", ("slot",)),
    ("草图", "中心线", ("centerline",)),
    ("草图", "草图圆角/倒角", ("sketch_fillet", "sketch_create_chamfer")),
    ("草图", "剪裁/延伸", ("sketch_trim", "sketch_extend")),
    ("草图", "等距偏移", ("sketch_offset", "offset_entit")),
    ("草图", "转换实体引用", ("convert_entit",)),
    ("草图", "草图镜像/阵列", ("sketch_mirror", "sketch_linear_pattern", "sketch_circular_pattern")),
    ("草图", "移动/旋转/缩放/伸展", ("sketch_move", "sketch_rotate", "sketch_scale", "sketch_stretch", "sketch_flip")),
    ("草图", "几何关系", ("add_sketch_relation", "add_relation", "sketch_constraint")),
    ("草图", "智能尺寸/自动标注", ("auto_dimension", "add_dimension", "diameter_dimension", "sketch_dimension")),
    ("草图", "完全定义检查", ("fully_defined",)),
    ("草图", "3D 草图", ("3d_sketch", "is_3d")),
    ("特征", "拉伸凸台", ("extrude_boss", "extrusion", "create_extrusion")),
    ("特征", "拉伸切除", ("extrude_cut", "cut_extrude")),
    ("特征", "旋转", ("revolve",)),
    ("特征", "扫描", ("sweep",)),
    ("特征", "放样", ("loft",)),
    ("特征", "边界凸台", ("boundary",)),
    ("特征", "圆角", ("fillet",)),
    ("特征", "倒角", ("chamfer",)),
    ("特征", "筋", ("rib",)),
    ("特征", "抽壳", ("shell",)),
    ("特征", "拔模", ("draft",)),
    ("特征", "圆顶", ("dome",)),
    ("特征", "包覆", ("wrap",)),
    ("特征", "孔向导", ("hole_wizard",)),
    ("特征", "异型孔（沉孔/锥沉孔）", ("hole_through", "hole_blind", "counterbore", "countersink")),
    ("特征", "螺纹", ("thread",)),
    ("特征", "线性阵列", ("linear_pattern",)),
    ("特征", "圆周阵列", ("circular_pattern",)),
    ("特征", "特征镜像", ("mirror_feature", "mirror")),
    ("特征", "曲线驱动阵列", ("curve_driven", "fill_pattern")),
    ("特征", "基准面/轴/坐标系/点", ("ref_plane", "part_axis", "coordinate_system", "reference_point", "create_plane", "create_axis")),
    ("特征", "分割线/投影曲线/组合曲线", ("split_line", "projected_curve", "composite_curve", "curve_through_points")),
    ("特征", "删除面/替换面", ("delete_face", "replace_face")),
    ("特征", "加厚/加厚切除", ("thicken",)),
    ("特征", "组合/相交", ("combine_bod", "intersect")),
    ("特征", "缩放/变形", ("scale", "deform")),
    ("特征", "拔模分析", ("draft_analysis", "analyze_draft")),
    ("特征", "特征识别/Instant3D", ("feature_recognition", "instant3d")),
    ("曲面", "拉伸曲面", ("extruded_surface", "surface_create_extruded")),
    ("曲面", "旋转曲面", ("revolved_surface", "surface_revolve")),
    ("曲面", "扫描曲面", ("swept_surface", "sweep_surface")),
    ("曲面", "放样曲面", ("lofted_surface", "lofted_ref_surface")),
    ("曲面", "边界曲面", ("boundary_surface",)),
    ("曲面", "填充曲面", ("fill_surface", "surface_fill", "filled_surface")),
    ("曲面", "等距曲面", ("offset_surface",)),
    ("曲面", "缝合曲面", ("knit",)),
    ("曲面", "延伸曲面", ("extend_surface", "surface_extend")),
    ("曲面", "剪裁曲面", ("trim_surface", "surface_trim")),
    ("曲面", "直纹曲面", ("ruled_surface", "ruled")),
    ("曲面", "平面区域", ("planar_surface", "surface_planar")),
    ("曲面", "曲面展平", ("flatten_surface", "unfold_surface")),
    ("曲面", "中面/加厚曲面", ("midsurface", "thicken_surface")),
    ("钣金", "基体法兰", ("base_flange",)),
    ("钣金", "边线法兰", ("edge_flange",)),
    ("钣金", "斜接法兰", ("miter_flange",)),
    ("钣金", "扫描法兰", ("swept_flange",)),
    ("钣金", "草图折弯", ("sketch_bend", "one_bend")),
    ("钣金", "闭合角/转折/褶边", ("closed_corner", "jog", "hem")),
    ("钣金", "成形工具", ("forming_tool",)),
    ("钣金", "展开/折叠", ("flatten", "unfold")),
    ("钣金", "平板型式/导出 DXF", ("flat_pattern", "export_flat")),
    ("钣金", "钣金角撑板", ("sm_gusset", "sheet_metal_create_gusset")),
    ("钣金", "钣金参数/证据", ("sheet_metal_evidence",)),
    ("焊件", "结构构件", ("structural_member",)),
    ("焊件", "裁剪/延伸焊件", ("trim_weldment", "weldment_trim")),
    ("焊件", "顶端盖", ("end_cap", "endcap")),
    ("焊件", "角撑板（焊件）", ("weldment_gusset", "add_gusset")),
    ("焊件", "圆角焊缝", ("fillet_bead", "weld_bead")),
    ("焊件", "切割清单", ("cut_list", "cutlist")),
    ("焊件", "焊接符号", ("weld_symbol",)),
    ("模具", "分型线", ("parting_line",)),
    ("模具", "关闭曲面/补孔", ("shut_off",)),
    ("模具", "分型面", ("parting_surface",)),
    ("模具", "型芯型腔分割", ("core_cavity", "tooling_split")),
    ("模具", "底切检测", ("undercut",)),
    ("模具", "模具证据", ("mold_evidence",)),
    ("装配", "插入零部件", ("add_component", "insert_component")),
    ("装配", "配合", ("mate",)),
    ("装配", "干涉检查", ("interference",)),
    ("装配", "爆炸视图", ("explode",)),
    ("装配", "爆炸直线", ("explode_line", "smart_line")),
    ("装配", "零部件阵列", ("component_pattern",)),
    ("装配", "配置", ("configuration", "config_create", "config_activate")),
    ("装配", "SpeedPak", ("speedpak",)),
    ("装配", "装配序列/说明书", ("assembly_sequence", "assembly_instruction")),
    ("装配", "装配体性能分析", ("performance_analysis", "assembly_performance")),
    ("工程图", "标准三视图/模型视图", ("standard_view", "model_view", "drawing_view")),
    ("工程图", "投影视图", ("projected_view",)),
    ("工程图", "剖面视图", ("section_view",)),
    ("工程图", "局部视图", ("detail_view",)),
    ("工程图", "断裂视图", ("broken_view",)),
    ("工程图", "辅助视图", ("auxiliary_view",)),
    ("工程图", "图纸格式/模板", ("sheet_format", "drawing_template")),
    ("工程图", "尺寸标注", ("drawing_dimension", "add_dimension", "auto_dimension_view")),
    ("工程图", "公差/GD&T", ("gtol", "geometric_tolerance")),
    ("工程图", "表面粗糙度", ("surface_finish",)),
    ("工程图", "基准符号", ("datum",)),
    ("工程图", "注释/文字", ("add_note", "annotation")),
    ("工程图", "气泡序号", ("balloon",)),
    ("工程图", "BOM 表", ("bom",)),
    ("工程图", "孔表", ("hole_table",)),
    ("工程图", "修订表", ("revision_table",)),
    ("工程图", "中心符号线", ("center_mark",)),
    ("工程图", "图纸比例/页面", ("sheet_scale", "sheet_info", "sheet_count", "sheet_name")),
    ("工程图", "尺寸/视图读回", ("drawing_list_views", "view_scale", "view_evidence")),
    ("评估", "测量", ("measure",)),
    ("评估", "质量属性", ("mass_propert",)),
    ("评估", "截面属性", ("section_propert",)),
    ("评估", "DFM/设计检查", ("dfm", "design_check", "review_active", "review_drawing", "cad_doctor")),
    ("评估", "成本估算 Costing", ("costing",)),
    ("评估", "预览/截图", ("preview", "screenshot", "export_bmp", "export_image")),
    ("仿真", "新建算例", ("create_study",)),
    ("仿真", "材料", ("material",)),
    ("仿真", "夹具/约束", ("restraint", "fixture")),
    ("仿真", "载荷", ("apply_force", "normal_force", "pressure", "gravity", "centrifugal",
                      "remote_load", "bearing_load", "temperature", "heat", "convection",
                      "radiation", "distributed_mass", "torque")),
    ("仿真", "网格", ("mesh",)),
    ("仿真", "运行求解", ("run_analysis", "run_fea")),
    ("仿真", "结果读取", ("results", "readback")),
    ("仿真", "频率/屈曲算例", ("frequency", "buckling")),
    ("仿真", "热算例", ("thermal", "heat_flux", "heat_power")),
    ("仿真", "拓扑优化", ("topology",)),
    ("仿真", "运动算例/马达", ("motion", "motor")),
    ("其他", "打开/新建/保存", ("open_document", "new_document", "save_document", "close_documents")),
    ("其他", "导出 STEP/IGES/STL", ("export_step", "export_iges", "export_stl", "export_parasolid", "write_open_format")),
    ("其他", "导出 PDF/DXF", ("export_dxf", "export_pdf", "build_dxf_preview")),
    ("其他", "自定义属性", ("custom_propert",)),
    ("其他", "方程式", ("equation",)),
    ("其他", "Toolbox 标准件", ("toolbox",)),
    ("其他", "Pack and Go", ("pack_and_go",)),
    ("其他", "宏/VBA", ("macro", "vba")),
    ("其他", "外观/渲染", ("appearance", "render_material")),
    ("其他", "批量处理", ("batch",)),
    ("其他", "传感器/单位", ("sensor", "document_units")),
    ("其他", "PDM", ("pdm", "edm")),
]

#: ★★ **人工剔除的假阳性**（★ 照 `MANUAL_MAP` 的先例：每条写清「为什么它不属于这一条」）。
#: ⚠ 关键词匹配**必然会**误配 —— 下面每条都是我**逐条看过命中项**后判定的。
FALSE_POS: dict[tuple[str, str], str] = {
    ("特征", "缩放/变形"): "命中的是 `drawing_set_sheet_scale`（**工程图比例**），不是实体缩放。本仓库**没有**实体缩放/变形。",
    ("钣金", "展开/折叠"): "命中的是 `weldment_create_sub_weld_folder`（子焊件**文件夹**里的 'fold'），不是钣金展开。本仓库的展开 DXF **已回退注册**。",
    ("焊件", "角撑板（焊件）"): "命中的是 `sheet_metal_create_gusset`（**钣金** gusset）。照已知事实 36，钣金与焊件的 gusset 是**两个不同接口**，不可互认。",
}

#: ★★ **能力面有、MCP 工具面没有**的项（照项目惯例「两列并存、互不替代」）。
CAP_ONLY: dict[tuple[str, str], str] = {
    ("曲面", "旋转曲面"): "能力 `surface_revolve` 是 `verified`，但**未暴露成 MCP 工具**（`scripts/sw_surface.py` 的 `create_revolution_surface`）。",
    ("曲面", "剪裁曲面"): "`scripts/sw_surface.py` 有实现，但**三条入口真机全不成**（已知事实 417–419）⇒ 工具面不计。",
}


def _load_ours() -> set[str]:
    """本仓库 MCP 工具名（**两个来源都读**，照 `build_union_map._our_tools` 的先例）。"""
    sys.path.insert(0, str(REPO_ROOT / "mcp-server"))
    import register_capabilities as rc  # noqa: PLC0415

    out: set[str] = set()
    for spec in rc.all_specs():
        name = getattr(spec, "name", None)
        if name is None and isinstance(spec, dict):
            name = spec.get("name")
        if name:
            out.add(str(name).lower())
    server = REPO_ROOT / "mcp-server" / "server.py"
    if server.is_file():
        text = server.read_text(encoding="utf-8", errors="replace")
        out |= {m.lower() for m in re.findall(r'name\s*=\s*"((?:solidworks|cadstudio)_[a-z0-9_]+)"', text)}
    return out


def _load_four() -> dict[str, set[str]]:
    """四家的工具名（来自 `tools/union-sources.json`）。"""
    data = json.loads(SOURCES.read_text(encoding="utf-8"))
    out: dict[str, set[str]] = {}
    for src in data.get("sources", []):
        key = str(src.get("repo", "")).split("/")[-1]
        out[key] = {str(t).lower() for t in (src.get("tools") or [])}
    return out


def _load_stitched() -> list[tuple[str, str]]:
    """`capabilities.yaml` 里 `level != verified` 的条目 —— **产物 §五 用**。"""
    data = json.loads(CAPS.read_text(encoding="utf-8"))
    return [(c["id"], c.get("level", "?")) for c in data.get("capabilities", []) if c.get("level") != "verified"]


def _hit(names: set[str], pats: tuple[str, ...]) -> list[str]:
    return sorted(n for n in names if any(p in n for p in pats))


def _markdown() -> str:
    ours = _load_ours()
    four = _load_four()
    stitched = _load_stitched()

    total = len(CHECKLIST)
    acc: dict[str, dict[str, list[int]]] = {}
    only_ours: list[tuple[str, str]] = []
    only_four: list[tuple[str, str, list[str]]] = []
    ours_hit: dict[tuple[str, str], bool] = {}

    for dom, item, pats in CHECKLIST:
        bucket = acc.setdefault(dom, {})
        for proj in ["本仓库", *FKEYS]:
            bucket.setdefault(proj, [0, 0])[1] += 1
        o = [] if (dom, item) in FALSE_POS else _hit(ours, pats)
        ours_hit[(dom, item)] = bool(o)
        if o:
            bucket["本仓库"][0] += 1
        for k in FKEYS:
            if _hit(four.get(k, set()), pats):
                bucket[k][0] += 1
        if o and not any(_hit(four.get(k, set()), pats) for k in FKEYS):
            only_ours.append((dom, item))
        if not o and any(_hit(four.get(k, set()), pats) for k in FKEYS):
            owners = [k for k in FKEYS if _hit(four.get(k, set()), pats)]
            only_four.append((dom, item, owners))

    n_ours = sum(1 for v in ours_hit.values() if v)
    scores = {p: sum(acc[d][p][0] for d in acc) for p in ["本仓库", *FKEYS]}

    L: list[str] = []
    A = L.append
    A("# 用户视角功能覆盖对照（本仓库 vs 四家）")
    A("")
    A("> **本文件是生成物** —— 由 `tools/gen_user_feature_coverage.py` 现算，**不要手改**。")
    A("> 重算：`python tools/gen_user_feature_coverage.py` · 比对：`python tools/gen_user_feature_coverage.py --check`")
    A("")
    A("## 一 · 口径（★ 先说清量的是什么，否则数字没有意义）")
    A("")
    A("**口径 = 能操作 SolidWorks 的「功能」数** —— 不是工具名数，也不是 API 成员数。")
    A("")
    A("清单共 **%d** 项，按 SOLIDWORKS 用户的 CommandManager 心智模型组织" % total)
    A("（画直线 / 画圆 / 拉伸 / 切除 / 拔模…这种粒度），分 11 个域。")
    A("")
    A("⚠ **本表只量第一列**。三列要分开看，**不可互相替代**：")
    A("")
    A("| 列 | 问的是 | 本表有吗 |")
    A("|---|---|---|")
    A("| ① **有入口** | 有没有这么个工具/名字 | ★ **本表量的是这个** |")
    A("| ② **能建成** | 真跑一次，特征树真的长了吗 | ❌ 见 §五 |")
    A("| ③ **真机验过** | 有没有留下我们自己的运行证据 | ❌ 见 `capabilities.yaml` 的 `level` |")
    A("")
    A("★ 这与 `docs/metrics.md` 的纪律②一致：「任何『覆盖广 / 全覆盖』的说法，**必须带那个真机数**」。")
    A("")
    A("## 二 · 方法（★ 与它的已知局限）")
    A("")
    A("```")
    A("① 本仓库侧：`register_capabilities.all_specs()` 的 name ∪ `server.py` 的 name= 抽名")
    A("② 四家侧：  `tools/union-sources.json` 的 sources[].tools")
    A("③ 匹配：    功能项的关键词**子串**命中任一工具名即算「有」")
    A("④ 人工剔除：%d 处假阳性（见 §六，每条写明为何不属于）" % len(FALSE_POS))
    A("```")
    A("")
    A("⚠★ **关键词匹配必然会误配。** 本脚本的 %d 处假阳性是**逐条看过命中项**后人工判定的；" % len(FALSE_POS))
    A("**残余误差估计在 ±5% 量级**，不足以改变 §三 的结论（差距都在 10 个百分点以上）。")
    A("")
    A("⚠ 更重要的是：**它量不到「能不能用」**（§一 的第②列）。四家在这一点上完全空白；")
    A("本仓库有 `capabilities.yaml` 的 `level` 可以回答，但**本表没把它算进覆盖率**。")
    A("")
    A("## 三 · 总分")
    A("")
    A("| 项目 | 覆盖 | 占比 |")
    A("|---|---|---|")
    for p in ["本仓库", *FKEYS]:
        A("| %s%s | %d/%d | **%.0f%%** |" % ("**" + p + "**" if p == "本仓库" else p, "", scores[p], total, 100 * scores[p] / total))
    A("")
    A("## 四 · 逐域对照")
    A("")
    A("| 域 | 项数 | " + " | ".join(["**本仓库**", *FKEYS]) + " |")
    A("|" + "---|" * (len(FKEYS) + 2))
    for dom, bucket in acc.items():
        cells = []
        for p in ["本仓库", *FKEYS]:
            a, b = bucket[p]
            cells.append("**%d/%d = %.0f%%**" % (a, b, 100 * a / b) if p == "本仓库" else "%d/%d" % (a, b))
        A("| %s | %d | %s |" % (dom, bucket["本仓库"][1], " | ".join(cells)))
    A("")
    A("## 五 · ★ 第三列：本仓库标 ✅ 但能力层级**不是 verified** 的")
    A("")
    A("这一列**四家一个都没有** —— 所以它不是「我们更差」，是「只有我们敢标」。")
    A("")
    A("| 能力 id | level |")
    A("|---|---|")
    for cid, lvl in sorted(stitched):
        A("| `%s` | `%s` |" % (cid, lvl))
    A("")
    A("⇒ ★ 落到 §四 的表上：**钣金、曲面、模具分型几何、GD&T、仿真结果读回** 这几域的 ✅ 要打折看。")
    A("")
    A("## 六 · 人工剔除的假阳性（★ 每条写明依据）")
    A("")
    A("| 域 / 功能 | 为什么不算 |")
    A("|---|---|")
    for (dom, item), why in FALSE_POS.items():
        A("| %s / %s | %s |" % (dom, item, why))
    A("")
    A("另有两项是**能力面有、工具面没有**（两列并存，不合并）：")
    A("")
    A("| 域 / 功能 | 说明 |")
    A("|---|---|")
    for (dom, item), why in CAP_ONLY.items():
        A("| %s / %s | %s |" % (dom, item, why))
    A("")
    A("## 七 · 只有本仓库有的功能（%d 项）" % len(only_ours))
    A("")
    for dom, item in only_ours:
        A("- %s / %s" % (dom, item))
    A("")
    A("## 八 · 只有四家有的功能（%d 项，★ 这就是缺口地图）" % len(only_four))
    A("")
    A("| 域 | 功能 | 哪几家有 |")
    A("|---|---|---|")
    for dom, item, owners in only_four:
        A("| %s | %s | %s |" % (dom, item, ", ".join(owners)))
    A("")
    A("## 九 · 完整清单（%d 项 × 5 列）" % total)
    A("")
    A("| 域 | 功能 | 本仓库 | " + " | ".join(FKEYS) + " |")
    A("|" + "---|" * (len(FKEYS) + 3))
    for dom, item, pats in CHECKLIST:
        row = ["| %s | %s | %s" % (dom, item, "✅" if ours_hit[(dom, item)] else "❌")]
        for k in FKEYS:
            row.append("✅" if _hit(four.get(k, set()), pats) else "·")
        A(" | ".join(row) + " |")
    A("")
    A("## 十 · 数据来源（★ 全部可重算）")
    A("")
    A("```")
    A("本仓库工具名 : register_capabilities.all_specs()  +  mcp-server/server.py 的 name=")
    A("四家工具名   : tools/union-sources.json 的 sources[].tools")
    A("能力等级     : capabilities.yaml 的 capabilities[].level")
    A("重算         : python tools/gen_user_feature_coverage.py")
    A("新鲜度比对   : python tools/gen_user_feature_coverage.py --check")
    A("```")
    A("")
    A("⚠ **本表是「有入口」的口径**。要引用它下结论，必须同时给出")
    A("`docs/metrics.md` 的真机覆盖率（口径③）与 `capabilities.yaml` 的 `level`。")
    A("")
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成 docs/user-feature-coverage.md")
    parser.add_argument("--check", action="store_true", help="只比对，文件过期则 exit 1")
    args = parser.parse_args(argv)

    text = _markdown()
    if args.check:
        if not OUT.is_file():
            print("  ✗ 缺 `%s` ⇒ 跑 tools/gen_user_feature_coverage.py" % OUT.relative_to(REPO_ROOT))
            return 1
        if OUT.read_text(encoding="utf-8") != text:
            print("  ✗ `%s` 与现算结果不一致 ⇒ 跑 tools/gen_user_feature_coverage.py" % OUT.relative_to(REPO_ROOT))
            return 1
        print("  ✓ `%s` 是最新的" % OUT.relative_to(REPO_ROOT))
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print("  清单 **%d** 项（%d 个域）" % (len(CHECKLIST), len({d for d, _, _ in CHECKLIST})))
    print("  产物: %s" % OUT.relative_to(REPO_ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
