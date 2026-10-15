"""★ 给「自称官方却无 `# swXxx` 覆盖」的模块级整数表**逐张补表级出处声明**（spec 224）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（施工工具）
# 文件:   tools/apply_enum_dispositions.py
# 定位:   spec `specs/224-enum-table-disposition/` 的 FR-004 落地工具。
#   ★ 为什么做成**工具**而不是一次性脚本：44 处声明的**分类本身就是结论**
#     （哪张表是官方枚举、哪张不是），把它留在代码里 ⇒ **可复核、可重跑、可审计**；
#     写成一次性脚本则分类随脚本消失，下一个人仍要重新人肉判一遍。
#   ★ `--check` 模式**只读**：断言「44 张全部已表态」且「分类与源码一致」，不写任何文件。
# 官方依据: 三源 —— ① `_raw/enum_values_sldworks.txt` · `_raw/reflect/enum_cosworks.txt`（出厂反射）
#           ② `C:\swapi\types\<Iface>\<Member>.md`（官方成员页）· ③ 各表上方的既有来源注释块。
#           逐张的枚举名/成员名**都是本轮在 ①/② 里核过的**，不是从注释里照抄的
#           （★ 反例：`sw_topology` 的注释写 `swsTopologyGoalType_e`，而 ① 第 2908 行写
#             `swsTopologyStudyGoalType_e` ⇒ 本表**以 ① 为准**）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.stdout.reconfigure(encoding="utf-8")

#: ★★ **本轮的核心结论表**：`(文件, 表名) -> (code, arg, 一句话理由)`。
#:   ★ 词表与语义见 `specs/224-enum-table-disposition/spec.md` FR-002。
#:   ★ **必须与 `find_uncovered_claimed_tables()` 的张数相等（44）** —— `--check` 会钉死。
DISPOSITIONS = {
    # ── `enum`：值是**命名官方枚举**的取值（门禁校验 值集 ⊆ 该枚举）────────────────
    ("sw_automation_knowledge.py", "DIALOG_SUPPRESSORS"):
        ("enum", "swUserPreferenceToggle_e", "值取自 swconst 的 swUserPreferenceToggle_e（键即官方成员名）"),
    ("sw_drawing_create_missing.py", "MODEL_ITEM_SOURCES"):
        ("enum", "swImportModelItemsSource_e", "官方 IDrawingDoc::InsertModelAnnotations4 的 Option 取值域"),
    ("sw_drawing_create_missing.py", "ANNOTATION_TYPE_BITS"):
        ("enum", "swInsertAnnotation_e", "26 个成员一个不漏；★ 键即官方成员名"),
    ("sw_drawing_create_missing.py", "VIEW_ENTITY_TYPES"):
        ("enum", "swViewEntityType_e", "官方 IView::GetVisibleEntities2 的 EntityType"),
    ("sw_macro.py", "RUN_MACRO_ERRORS"):
        ("enum", "swRunMacroError_e", "全 28 个成员；两源逐一比对一致"),
    ("sw_ref_geometry.py", "REF_POINT_TYPES"):
        ("enum", "swRefPointType_e", "官方 swRefPointType_e"),
    ("sw_ref_geometry.py", "REF_POINT_ALONG_CURVE_TYPES"):
        ("enum", "swRefPointAlongCurveType_e", "官方 swRefPointAlongCurveType_e"),
    ("sw_ref_geometry.py", "GLOBAL_BBOX_FIT_OPTIONS"):
        ("enum", "swGlobalBoundingBoxFitOptions_e", "官方 swGlobalBoundingBoxFitOptions_e"),
    ("sw_ref_geometry.py", "GLOBAL_BBOX_RESULT"):
        ("enum", "swGlobalBoundingBoxResult_e", "官方 swGlobalBoundingBoxResult_e（Success=0）"),
    ("sw_sheet_metal.py", "HEM_TYPES"):
        ("enum", "swHemTypes_e", "官方 swHemTypes_e 五个成员一个不漏"),
    ("sw_sheet_metal.py", "HEM_RELIEFS"):
        ("enum", "swSheetMetalReliefTypes_e", "官方 swSheetMetalReliefTypes_e"),
    ("sw_sheet_metal.py", "HEM_RELIEF_TEARS"):
        ("enum", "swReliefTearTypes_e", "官方 swReliefTearTypes_e"),
    ("sw_sheet_metal.py", "SELECTION_MARK_ACTION"):
        ("enum", "swSelectionMarkAction_e", "SetSelectedObjectMark 第 3 参"),
    ("sw_simulation_results.py", "SWS_NODAL_STRESS_COMPONENTS"):
        ("enum", "swsStaticResultNodalStressComponentTypes_e", "cosworks 反射；分量 SX/SY/SZ"),
    ("sw_sketch_edit_ops.py", "TRIM_CHOICES"):
        ("enum", "swSketchTrimChoice_e", "官方 swSketchTrimChoice_e"),
    ("sw_sketch_edit_ops.py", "OFFSET_CAPS"):
        ("enum", "swSkOffsetCapEndType_e", "官方 swSkOffsetCapEndType_e"),
    ("sw_sketch_edit_ops.py", "OFFSET_CONSTRUCTION"):
        ("enum", "swSkOffsetMakeConstructionType_e", "官方 swSkOffsetMakeConstructionType_e"),
    ("sw_sketch_relations.py", "RELATION_TYPES"):
        ("enum", "swConstraintType_e",
         "★ 键**不是**官方成员名（COINCIDENT vs swConstraintType_COINCIDENT）⇒ 只做**值集包含**校验"),
    ("sw_topology.py", "SWS_ANALYSIS_STUDY_TYPES"):
        ("enum", "swsAnalysisStudyType_e", "cosworks 反射"),
    ("sw_topology.py", "SWS_TOPOLOGY_GOAL_TYPES"):
        ("enum", "swsTopologyStudyGoalType_e",
         "★ 源码注释写的 `swsTopologyGoalType_e` **少了 `Study`**；真名见 enum_cosworks.txt:2908 ⇒ 以反射为准"),
    ("sw_topology.py", "SWS_TOPOLOGY_MASS_PREFERENCES"):
        ("enum", "swsTopologyStudyMassConstraintOption_e",
         "★ 源码注释写的名字少了 `Study`；真名见 enum_cosworks.txt:2913"),
    ("sw_topology.py", "SWS_TOPOLOGY_PRESERVED_REGION_OPTIONS"):
        ("enum", "swsTopologyPreservedRegionOption_e",
         "★ 依赖 FR-001 才解析得到（成员名 `PreservedRegion_LoadsOnly` 不带 sw 前缀）"),
    ("sw_topology.py", "SWS_TOPOLOGY_ITERATION_OPTIONS"):
        ("enum", "swsTopologyIterationOption_e",
         "★ 依赖 FR-001 才解析得到（成员名 `IterationOption_Auto` 不带 sw 前缀）"),

    # ── `member`：值来自**该官方成员的页内文档**，官方**没有**命名枚举 ────────────
    ("sw_body_ops.py", "BODY_MARKS"):
        ("member", "InsertMoveCopyBody2", "mark 表逐字抄自该页 ## Remarks"),
    ("sw_boolean_ops.py", "REGION_TYPES"):
        ("member", "PreIntersect2", "RegionType 三值逐字抄自该页 ## Parameters"),
    ("sw_net_blend.py", "BLEND_TYPE"):
        ("member", "InsertNetBlend", "Type 枚举逐字抄自该页参数表"),
    ("sw_net_blend.py", "INFLUENCE_TYPE"):
        ("member", "SetNetBlendDirectionData", "InfluenceType 逐字抄自该页参数表"),
    ("sw_sheet_metal.py", "UNFOLD_MARKS"):
        ("member", "InsertSheetMetalFold", "mark 表逐字取自官方 Insert/Fold 示例"),
    ("sw_sketch_edit.py", "SKETCH_MIRROR_MARK"):
        ("member", "SketchMirror", "选中标记（不是参数），官方页无命名枚举"),
    ("sw_surface_features.py", "SWEEP_MARKS"):
        ("member", "InsertSweepSurface2", "mark 表逐字抄自该页 ## Remarks（1=Profile/2=Guide/4=Path）"),
    ("sw_weldment.py", "WELDMENT_TRIM_MARKS"):
        ("member", "InsertWeldmentTrimFeature2", "mark 表；官方页无命名枚举"),
    ("sw_weld_bead.py", "BEAD_TYPE"):
        ("member", "InsertFilletBeadFeature2", "Type1/2 的 0/1/2 逐字抄自该页参数语义"),
    ("sw_weld_bead.py", "PENETRATION_TYPE"):
        ("member", "InsertFilletBeadFeature2", "PenetrationType1/2 的 0/1/2 同上"),
    ("sw_weld_bead.py", "FLAG"):
        ("member", "InsertFilletBeadFeature2", "Flag 的 0/1/2/3 同上"),

    # ── `not-enum`：**不是**官方枚举值 ────────────────────────────────────────────
    ("sw_assembly_doc.py", "ASSEMBLY_DOC_ARITY"):
        ("not-enum", "arity", "IAssemblyDoc 各成员的**实参个数**，机械生成"),
    ("sw_automation_knowledge.py", "DIALOG_AND_NOTIFY"):
        ("not-enum", "arity", "成员名 + 实参个数，反射逐条确认"),
    ("sw_body_ops.py", "AXIS_INDEX"):
        ("not-enum", "index", "官方三参 (RotAngleX/Y/Z) 里**真正作用于该轴**的下标"),
    ("sw_body_ops.py", "ROTATION_AXIS_MAP"):
        ("not-enum", "derived", "★ 本仓**推导**的映射（官方参数名与实际轴不一致的处置），非官方枚举"),
    ("sw_hole_features.py", "WZD_FASTENER_ANSI_METRIC_SIMPLE"):
        ("not-enum", "observed", "★ **真机观测**的 FastenerTypeIndex；官方三源查不到（铁律 5 不改不猜）"),
    ("sw_mass_property.py", "SECTION_INDEX"):
        ("not-enum", "index", "官方 24 元返回数组的**下标定义**"),
    ("sw_pattern.py", "PATTERN_MEMBER_ARITY"):
        ("not-enum", "arity", "两个 FeatureData 共有方法型成员的实参个数"),
    ("sw_simulation_loads.py", "OFFICIAL_LOAD_SIGNATURES"):
        ("not-enum", "arity", "28 个封装的官方 VB 声明**实参个数**"),
    ("sw_simulation_results.py", "RESULTS_ARITY"):
        ("not-enum", "arity", "ICWResults/ICWMesh 各封装的实参个数"),
    ("sw_simulation_study.py", "STUDY_MANAGER_ARITY"):
        ("not-enum", "arity", "ICWStudyManager/ICWStudy 各封装的实参个数"),
}

HEAD = "#: enum-gate: %s %s"


def _load_gate():
    spec = importlib.util.spec_from_file_location(
        "enum_gate", ROOT / "scripts" / "check_enum_values_vs_reflection.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _targets(gate) -> dict:
    """⇒ `{(文件, 表名): (起始行, 结束行, 条目数)}`（只取**门禁盲区**里的那些）。"""
    out = {}
    by_key = {}
    for fname, lo, hi, name, n in gate.find_int_tables():
        by_key.setdefault((fname, name), []).append((lo, hi, n))
    for fname, lo, name, n in gate.find_uncovered_claimed_tables():
        out[(fname, name)] = (lo, by_key[(fname, name)][0][1], n)
    return out


def run(check_only: bool) -> int:
    gate = _load_gate()
    targets = _targets(gate)
    missing_cls = sorted(set(targets) - set(DISPOSITIONS))
    extra_cls = sorted(set(DISPOSITIONS) - set(targets))
    bad = 0
    if missing_cls:
        bad += 1
        print("[FAIL] 盲区里有 %d 张表**没有分类**：" % len(missing_cls))
        for f, n in missing_cls:
            print("         %s  %s" % (f, n))
    if extra_cls:
        bad += 1
        print("[FAIL] 分类里有 %d 项**不在盲区**（盲区清单变了，需重核）：" % len(extra_cls))
        for f, n in extra_cls:
            print("         %s  %s" % (f, n))
    if bad:
        return 1

    print("盲区表 **%d** 张 · 分类 **%d** 项 ⇒ 一一对应 ✓" % (len(targets), len(DISPOSITIONS)))
    by_file: dict = {}
    for (fname, name), (lo, _hi, _n) in targets.items():
        by_file.setdefault(fname, []).append((lo, name))
    written = already = 0
    for fname in sorted(by_file):
        path = ROOT / "scripts" / fname
        lines = path.read_text(encoding="utf-8").splitlines()
        todo = []
        for lo, name in by_file[fname]:
            code, arg, _why = DISPOSITIONS[(fname, name)]
            head = HEAD % (code, arg)
            if lines[lo - 2].strip() == head:
                already += 1
                continue
            todo.append((lo, name, head))
        if check_only:
            if todo:
                print("[FAIL] %s 还有 %d 处未落：%s"
                      % (fname, len(todo), ", ".join(n for _l, n, _h in todo)))
                bad += 1
            continue
        #: ★ **从下往上**插入，避免行号漂移（同一文件内多处）。
        for lo, _name, head in sorted(todo, reverse=True):
            lines.insert(lo - 1, head)
            written += 1
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if check_only:
        print("--check：已落 **%d** 处 · 未落 **%d** 处 ⇒ %s"
              % (already, len(DISPOSITIONS) - already, "OK" if not bad else "FAIL"))
        return 1 if bad else 0
    print("插入 **%d** 行声明（另有 %d 处已存在，跳过）" % (written, already))
    return 0


if __name__ == "__main__":
    raise SystemExit(run(check_only="--check" in sys.argv))
