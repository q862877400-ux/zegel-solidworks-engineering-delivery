#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按示例**实际用到的官方类型**把 2,839 个官方示例归到 14 个功能域。

为什么不用文件名分类
--------------------
文件名分类试过：2,839 个里有 866 个（30%）落进「未分类」，因为
``Get_xxx``（319 个）这类名字太通用、``Add_ActiveX_Tab_...`` 这类又属于
「加载项 UI 开发」这个独立主题。

本脚本改为解析示例正文里的类型声明（VB/VB.NET/C# 里的
``Dim swApp As SldWorks.SldWorks`` / ``SldWorks.ModelDoc2 swModel;``），
抽取出示例真正调用的官方类型，再按 capability-matrix 已确立的
「类型 → 域」映射归类。这样归类依据是**代码事实**而非标题猜测。

⚠ 只读文件、只做文本解析：不执行示例代码、不导入任何 CAD 模块、
  不连接 SolidWorks（见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

EXAMPLES = Path(r"C:\swapi\examples")
OUT_TXT = Path(Path(__file__).resolve().parents[1] / "_raw" / "examples_by_domain.txt")
OUT_JSON = Path(Path(__file__).resolve().parents[1] / "_raw" / "example_domain_index.json")

# ── 「类型 → 域」映射 ──────────────────────────────────────────────────
# 来源：C:\swapi 的 14 域入口类型清单（sw_know.py domain <域>），
# 即 capability-matrix.md §一 的同源数据。只收各域的入口类型，
# 不做穷举 —— 目的是判定「这个示例属于哪个域」，不是穷尽类型。
TYPE_DOMAIN: dict[str, str] = {}


def _register(domain: str, names: str) -> None:
    for n in names.split():
        TYPE_DOMAIN.setdefault(n, domain)


_register("应用与会话", """
    SldWorks ISldWorks IModelDoc IModelDoc2 IModelDocExtension ISelectionMgr
    IEnumModelViews ISldWorksApp ISldWorksEvents ICommandManagerEvent
    IPropertyManagerPage IPropertyManagerPage2 IPropertyManagerPageHandler
    IPropertyManagerPageHandler2 IPropertyManagerPageHandler5
    IPropertyManagerPageHandler6 IPropertyManagerPageHandler7
    IPropertyManagerPageHandler8 IPropertyManagerPageHandler9
    ITaskpaneHandler ITaskpaneHandler2 ICommandGroup ICommandGroupButton
    IMenuItem IModelDocEvents IAppEvents IActiveXControlHandler
""")
_register("草图", """
    ISketchManager ISketch ISketchSegment ISketchLine ISketchArc ISketchSlot
    ISketchSpline ISketchPoint ISketchRelation ISketchRelationManager
    ISketchContour ISketchHatch ISketchText ISketchPatternFeatureData
    ISketchSegments ISketchPoints ISketchEquations ISketchFillet
""")
_register("零件特征", """
    IFeatureManager IFeature ISimpleFilletFeatureData2 IChamferFeatureData2
    ILinearPatternFeatureData ICircularPatternFeatureData
    IMirrorPatternFeatureData IShellFeatureData IRevolveFeatureData2
    ISweepFeatureData ILoftFeatureData IRibFeatureData2
    IChainPatternFeatureData ICurveDrivenPatternFeatureData
    IExtrudeFeatureData2 IOffsetSurfaceFeatureData2 IDraftFeatureData2
    ICompositeCurveFeatureData2 ITrimSheetFeatureData2 IDirectEditFeatureData
    IDirectEditPointFeatureData IRefineFeatureData IBossFeatureData
    IDeleteBodyFeatureData2 IFlatPatternFeatureData
""")
_register("孔与螺纹", """
    IWizardHoleFeatureData2 IAdvancedHoleFeatureData ISimpleHoleFeatureData2
    IHoleSeriesFeatureData2 IHoleStandardsData IHoleTable
    IAdvancedHoleElementData IStraightTapElementData ITaperedTapElementData
    IThreadFeatureData ICosmeticThreadFeatureData IHoleFeatureData
""")
_register("钣金", """
    ISheetMetalFeatureData ISheetMetalFolder IBaseFlangeFeatureData
    IEdgeFlangeFeatureData IOneBendFeatureData ISketchedBendFeatureData
    IHemFeatureData IMiterFlangeFeatureData ISweptFlangeFeatureData
    IGussetFeatureData ISMGussetFeatureData IDraftFeatureData2
    ILoftedBendsFeatureData ISurfaceCutFeatureData IRibFeatureData2
    IFormingFeatureData IBendFeatureData IConvertToRefSurfaceFeatureData
""")
_register("焊件", """
    IStructureSystemFolder IStructureSystemMemberFeatureData
    IStructureSystemMemberProfile IStructureSystemSplitMember
    IProfileCenterMateFeatureData IWeldmentCutListFeature ICutListItem
    ICutListSortOptions IWeldBead IWeldmentBeadFeatureData
    ICosmeticWeldBeadFeatureData IWeldSymbol IWeldmentTrimExtendFeatureData
    IProfileGroupFolder IStructureSystem ITrimSheetFeatureData2
""")
_register("曲面", """
    ISurface ISurfaceTrimFeatureData ISurfaceExtendFeatureData
    ISurfaceKnitFeatureData ISurfaceFlattenFeatureData
    ISurfaceOffsetFeatureData ISurfaceCutFeatureData ISurfaceRadiateFeatureData
    IFillSurfaceFeatureData ISurfacePlanarFeatureData ISurfRevolveFeatureData
    ISurfaceParameterizationData IShutOffSurfaceFeatureData IModeler
""")
_register("装配", """
    IAssemblyDoc IComponent2 IEnumComponents2 IMate2 IMateEntity2
    IMateFeatureData IMateInPlace IMateReference IExplodeStep IPartExplodeStep
    IMirrorComponentFeatureData ICoincidentMateFeatureData
    IConcentricMateFeatureData IDistanceMateFeatureData
    IAngleMateFeatureData IParallelMateFeatureData IPerturbMateFeatureData
    IInsertComponentFeatureData IFixComponentFeatureData2
    ISketchBlockFeatureData ILightweightComponentFeatureData2
""")
_register("工程图", """
    IDrawingDoc IView IView3D ISheet IDimension IDisplayDimension IAnnotation
    IAnnotationView ITableAnnotation IModelView IModelViewManager
    ISectionViewData IGeneralTableAnnotation IBomTableAnnotation
    IHoleTableAnnotation IWeldmentCutListAnnotation IBendTableAnnotation
    IRevisionTableAnnotation IDimensionTolerance IMultiJogLeader
    IDrawingComponent ITableAnnotationCategory IDisplayedDimension
    ISectionView ISheetLocation IViewPort ILeaders ILeader
""")
_register("几何与拓扑", """
    IBody2 IFace2 IEdge IVertex ICurve ISurface ILoop2 IEnumBodies2
    IBoundingBoxFeatureData IBoundaryBossFeatureData ICenterOfMass
    IMidSurface3 IEdgePoint IMeasure IClosestPoint IPoint IPoint2 ILine
    ICircle IEllipse IParabola IHyperbola ISpline2 ITrimmedCurve
""")
_register("质量属性与导出", """
    IMassProperty2 IMassPropertyOverrideOptions ICenterOfMass
    ISaveAsOptions ISaveAsInfo IPackAndGo IPackAndGoGetData
    IMassProperty IExportStepData IExportStandaloneGeometryData
""")
_register("配置·材料·自定义属性", """
    IConfiguration IConfigurationManager ICustomPropertyManager IDesignTable
    IMaterialVisualPropertiesData IRenderMaterial ITextAndCustomProperty
    IDisplayState IDisplayStateBlock IComponentDisplayStateData
    IDerivedProperty IParameter IEquationMgr IMaterial IAppearanceStep
""")
_register("仿真(需许可证)", """
    ICWModelDoc ICWResults ICWStudyManager ICWStudy ICosmosWorks
    ICWLoadsAndRestraintsManager ICWMesh CWMesh ICWSolidManager ICWMaterial
    CWModelDoc CWStudy CWStudyManager ICwAddincallback
""")
_register("路由/Composer/PDM", """
    IComposerIComponent IComposerDoc IRouteManager IRouteSegment
    IRouteAssemblyCosting ICostingManager ISustainabilityManager
""")

#: 加载项 UI 开发：官方没有独立功能域，但上游有 sw_addin_host.py，单独归一类
UI_HOST_KEYWORDS = (
    "activex", "taskpane", "task_pane", "context-sensitive", "menuitem",
    "commandgroup", "propertymanagerpage", "add-in", "addin", "handler",
    "progressbar", "statusbar", "modeless", "callbacks", "icon",
)

#: 类型声明抽取
_RE_VB = re.compile(r"\bAs\s+SldWorks\.\s*(\w+)", re.I)
_RE_CS_DECL = re.compile(r"^\s*(?:public|private|internal|static|readonly|\s)*SldWorks\.\s*(\w+)\s+\w+", re.M)
_RE_NEW = re.compile(r"\bNew\s+SldWorks\.\s*(\w+)", re.I)
_RE_I = re.compile(r"\bSldWorks\.I(\w+)\b")


def types_in(text: str) -> set[str]:
    found: set[str] = set()
    for rx in (_RE_VB, _RE_CS_DECL, _RE_NEW):
        found.update(rx.findall(text))
    # 去掉裸 I 前缀，便于与 I* 类型的另一种写法对上
    for rx in (_RE_I,):
        found.update("I" + m for m in rx.findall(text))
    return {t for t in found if t and not t.isdigit()}


#: 几乎每个示例都会声明的**样板类型**。若不剔除，任何示例都会被
#: SldWorks / ModelDoc2 / ModelDocExtension 这几个类型投票带偏到
#: 「应用与会话」——首版就是这样，1,188/2,839 全落进一个域。
#: 剔除后只用**域特有类型**投票。
BOILERPLATE = {
    "SldWorks", "ISldWorks", "ModelDoc", "IModelDoc", "ModelDoc2", "IModelDoc2",
    "ModelDocExtension", "IModelDocExtension", "SelectionMgr", "ISelectionMgr",
    "EnumModelViews", "IEnumModelViews", "MathUtility", "IMathUtility",
    "IModelDocEvents", "IAppEvents", "ISldWorksEvents", "IModelDocExtensionEvents",
    "IAssemblyDocEvents", "IPartDocEvents", "IDrawingDocEvents",
    "IModelerEvents", "IAttribute", "IAttributeDef", "IPartDoc",
    "IAssemblyDoc", "IDrawingDoc", "IComponent2", "IConfiguration",
    "MathPoint", "MathVector", "MathTransform", "IMathPoint", "IMathVector",
    "IMathTransform", "IMeasure", "IMeasurement", "ICommandManager",
    "ICommandManagerEvent", "IModelDocExtensionPersistReferenced",
}


def build_member_index() -> dict[str, set[str]]:
    """从反射清单建 {成员名: {宿主接口}}。

    依据 D:\\AI\\SW\\_raw\\reflect_sldworks\\iface_sldworks.txt
    （对 SolidWorks.Interop.sldworks.dll 的纯元数据反射，20,627 成员）。

    为什么改用「成员调用」而不是「类型声明」：
      - 只看类型声明时，几乎每个示例都只声明 swApp/swModel 这类样板类型
        （首版 1,188/2,839 全被判成「应用与会话」）；
      - 剔除样板类型后又几乎全空（2,808/2,839 落进未分类）；
      - **真正稳定的信号是成员调用**：FeatureExtrusion3 → 零件特征、
        CreateDrawViewFromModelView3 → 工程图、AddRestraint → 仿真。
    """
    idx: dict[str, set[str]] = defaultdict(set)
    iface = None
    sig = re.compile(r"^\s+(\S+)\s+(\w+)\((.*)\)\s*$")
    for raw in Path(Path(__file__).resolve().parents[1] / "_raw" / "reflect_sldworks" / "iface_sldworks.txt") \
            .read_text(encoding="utf-8", errors="replace").splitlines():
        h = re.match(r"^##\s+(\w+)\s*$", raw)
        if h:
            iface = h.group(1)
            continue
        m = sig.match(raw)
        if m and iface:
            idx[m.group(2)].add(iface)
    return idx


#: 成员调用抽取：obj.Member(  /  Member(
_RE_CALL = re.compile(r"[.\s]([A-Z]\w+)\s*\(")
# ⚑ 2026-10-03（轮 470）：这里曾有一个 `domains_of_members(members, midx)` ——
#   它把示例里调用到的成员映射到域（取宜主接口域的并集），
#   是**建库阶段**统计用的一次性助手。
#   ★ 实测：全仓出现 **1** 次（就只有这一处定义）⇒ 真死代码。
#   ★ 依据：本仓先例（`tools/propose_capability_sources.py` L136-137 对 `match_modules` 的处理）
#   与门禁 `tests/test_no_uncalled_helpers.py`。


def domain_of(types: set[str], stem: str) -> str:
    votes: dict[str, int] = defaultdict(int)
    for t in types:
        if t in BOILERPLATE:
            continue                      # 样板类型不参与投票
        d = TYPE_DOMAIN.get(t)
        if d:
            votes[d] += 1
    if votes:
        return max(votes.items(), key=lambda kv: (kv[1], kv[0]))[0]
    low = stem.lower()
    for k in UI_HOST_KEYWORDS:
        if k in low:
            return "加载项/UI 开发"
    return "未分类"


def main() -> int:
    if not EXAMPLES.is_dir():
        print(f"[FATAL] 找不到示例目录: {EXAMPLES}", file=sys.stderr)
        return 2

    files = sorted(EXAMPLES.glob("*.md"))
    midx = build_member_index()
    by_domain: dict[str, list[dict]] = defaultdict(list)
    langs: dict[str, int] = defaultdict(int)
    lang_rx = re.compile(r"_Example_(CSharp|VBNET|VB|CPlusPlus_COM|Java|ObjC)$")
    code_rx = re.compile(r"```[a-z+#]*\n(.*?)```", re.S)

    for p in files:
        stem = p.stem
        m = lang_rx.search(stem)
        lang = m.group(1) if m else "?"
        langs[lang] += 1
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            continue
        # 只在代码块里找成员调用，避免正文描述文字污染
        code = "\n".join(code_rx.findall(text)) or text
        members = {c for c in _RE_CALL.findall(code) if c in midx}
        # 多标签：一个示例天然横跨多个域（Select4 几乎每个示例都调）。
        # 强制单标签会失真，故按「该域命中的成员数」加权，逐域累加。
        dom_weight: dict[str, int] = defaultdict(int)
        dom_members: dict[str, set[str]] = defaultdict(set)
        for mem in members:
            for iface in midx.get(mem, ()):
                d = TYPE_DOMAIN.get(iface)
                if d:
                    dom_weight[d] += 1
                    dom_members[d].add(mem)
        if not dom_weight:
            dom = domain_of(types_in(text), stem)
            dom_weight[dom] = 0
        for d, w in dom_weight.items():
            by_domain[d].append({
                "file": p.name,
                "lang": lang,
                "weight": w,
                "types": sorted(dom_members[d])[:10],
            })

    total = len(files)
    order = ["应用与会话", "草图", "零件特征", "孔与螺纹", "钣金", "焊件", "曲面",
             "装配", "工程图", "几何与拓扑", "质量属性与导出", "配置·材料·自定义属性",
             "仿真(需许可证)", "路由/Composer/PDM", "加载项/UI 开发", "未分类"]

    lines = [
        "# 官方示例按域归类（依据代码实际用到的类型，非标题猜测）",
        "",
        f"来源：C:\\swapi\\examples\\ 共 {total} 个官方示例。",
        "归类依据：解析示例正文中的类型声明（`As SldWorks.X` / `SldWorks.X y;`），",
        "取出示例真正调用的官方类型，再按「类型 → 域」映射归类。",
        "只读文件与文本解析，不执行任何示例代码（AGENTS.md 铁律 2）。",
        "",
        "## 语言分布",
    ]
    for lang, n in sorted(langs.items(), key=lambda kv: -kv[1]):
        lines.append(f"  {lang:<16} {n}")
    lines += ["", "## 各域示例数"]
    for d in order:
        lines.append(f"  {d:<24} {len(by_domain.get(d, []))}")
    lines += ["", "=" * 78]
    for d in order:
        items = by_domain.get(d, [])
        if not items:
            continue
        items.sort(key=lambda it: (-it["weight"], it["file"]))
        # 权重 0 = 只靠文件名/类型兜底归的域，可信度低，单列出来
        strong = [it for it in items if it["weight"] > 0]
        weak = [it for it in items if it["weight"] == 0]
        lines.append(f"\n## {d}（{len(items)} 个；其中按成员调用判定 {len(strong)} 个）")
        lines.append("### 强相关（示例确实调用了本域 API 成员，按命中数排序）")
        for it in strong:
            tp = ",".join(it["types"][:6])
            lines.append(f"  [{it['weight']:>2}] [{it['lang']:<6}] {it['file'][:-3]}" + (f"   ← {tp}" if tp else ""))
        if weak:
            lines.append(f"### 弱相关（仅按名称/类型兜底归类，共 {len(weak)} 个，可信度低）")
            for it in weak[:15]:
                lines.append(f"       [{it['lang']:<6}] {it['file'][:-3]}")
            if len(weak) > 15:
                lines.append(f"       ... 其余 {len(weak) - 15} 个见 JSON 索引")

    OUT_TXT.write_text("\n".join(lines), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(
        {"total": total, "languages": dict(langs), "by_domain": by_domain},
        ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"示例总数 {total} -> {OUT_TXT}")
    print("语言: " + ", ".join(f"{k}={v}" for k, v in sorted(langs.items(), key=lambda kv: -kv[1])))
    print("各域示例数:")
    for d in order:
        print(f"  {d:<24} {len(by_domain.get(d, []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
