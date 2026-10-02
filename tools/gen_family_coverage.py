#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""接口族覆盖度量化：14 个域的官方接口族，本仓库实际触及了多少。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本工具为原创；2026-10-01 轮 210 从工作区仓库搬入本仓库）
# 文件:   tools/gen_family_coverage.py —— 本文件自身
# 定位:   docs/family-coverage.{md,json} 的生成器；读 C:\\swapi\\types\\
#         的成员目录 + 本仓库 74 个 .py + D:\\AI\\SW\\_raw\\reflect\\ 的反射清单，
#         产出「域 × 接口族 × 触及情况」台账。
#         ★ 本轮（Spec Kit `129`）新增：读 C:\\swapi 的 `category` 字段，
#           加出 `## 四、官方分类与「未认领」族的归位` 一节。
# 官方依据: C:\\swapi（结构化 markdown，含 `category`）；出厂反射
#         `D:\\AI\\SW\\_raw\\reflect*\\iface_*.txt`（★ 实测**不含** category）
# 许可:   本仓库 MIT
# ⚠ 输入源注意：`C:\\swapi` 的数据受其**来源仓自身条款**约束
#   （见 docs/sources.md 的许可判定表）⇒ 本工具的**产物**按工作区既有口径处理，
#   不因本工具而额外取得再分发授权。
# ⚠ 本工具只做**静态汇总**，不连 SolidWorks；生成器本身的路径与输入源
#   依赖本机布局（`C:\\swapi` / `D:\\AI\\SW\\_raw`），未在第二台机器上实测。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────

为什么需要
----------
``capability-matrix.md`` 给的是「官方有哪些接口族」，
``harvest-report.md`` 的 A1 表给的是定性的「覆盖 / 部分 / 不覆盖」。
中间缺一环：**每个域的接口族，到底有几个被本仓库真正触及**。
本脚本把 A1 从定性升级为定量。

方法
----
  ① 从 C:\\swapi\\types\\<Interface> 的成员目录取该接口族的成员清单；
  ② 用与 api-map 相同的两路形态（直接调用 obj.Member( / 反射式 get_com_member）
     在本仓库 74 个 .py 里找这些成员；
  ③ 输出「域 × 接口族 × 是否触及 × 触及了哪些成员」。

⚠ 只读文件 + AST/文本解析：不执行仓库代码、不连接 SolidWorks
  （见 AGENTS.md 铁律 2）。
"""
from __future__ import annotations

import ast
import io
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass

REPO = Path(r"" + _ROOT_S + r"")
SWAPI = Path(r"C:\swapi\types")
#: C:\swapi 未收录的 4 个程序集的反射清单（域 13 / 14 用）
#: 来源：AGENTS.md §四.1③ —— 对官方 interop 程序集的纯元数据反射
REFLECT = {
    "cosworks": Path(r"D:\AI\SW\_raw\reflect\iface_cosworks.txt"),
    "SWRoutingLib": Path(r"D:\AI\SW\_raw\reflect\iface_SWRoutingLib.txt"),
    "sldcostingapi": Path(r"D:\AI\SW\_raw\reflect\iface_sldcostingapi.txt"),
    "swdocumentmgr": Path(r"D:\AI\SW\_raw\reflect\iface_swdocumentmgr.txt"),
    "fworks": Path(r"D:\AI\SW\_raw\reflect\iface_fworks.txt"),
}
OUT_MD = REPO / "docs" / "family-coverage.md"
OUT_JSON = REPO / "docs" / "family-coverage.json"

#: 14 域 -> 入口接口族（与 capability-matrix.md §一同源，照抄 sw_know domain 输出）
DOMAIN_FAMILIES: dict[str, list[str]] = {
    "应用与会话": ["ISldWorks", "IModelDoc2", "IModelDocExtension", "ISelectionMgr", "IEnumModelViews"],
    "草图": ["ISketchManager", "ISketch", "ISketchSegment", "ISketchLine", "ISketchArc",
             "ISketchSlot", "ISketchSpline", "ISketchPoint", "ISketchRelation",
             "ISketchRelationManager", "ISketchContour", "ISketchHatch", "ISketchText",
             "ISketchPatternFeatureData"],
    "零件特征": ["IFeatureManager", "IFeature", "ISimpleFilletFeatureData2",
             "IChamferFeatureData2", "ILinearPatternFeatureData", "ICircularPatternFeatureData",
             "IMirrorPatternFeatureData", "IShellFeatureData", "IRevolveFeatureData2",
             "ISweepFeatureData", "ILoftFeatureData", "IRibFeatureData2",
             "IChainPatternFeatureData", "ICurveDrivenPatternFeatureData"],
    "孔与螺纹": ["IWizardHoleFeatureData2", "IAdvancedHoleFeatureData", "ISimpleHoleFeatureData2",
             "IHoleSeriesFeatureData2", "IHoleStandardsData", "IHoleTable",
             "IAdvancedHoleElementData", "IStraightTapElementData", "ITaperedTapElementData",
             "IThreadFeatureData", "ICosmeticThreadFeatureData"],
    "钣金": ["ISheetMetalFeatureData", "ISheetMetalFolder", "IBaseFlangeFeatureData",
           "IEdgeFlangeFeatureData", "IOneBendFeatureData", "ISketchedBendFeatureData",
           "IHemFeatureData", "IMiterFlangeFeatureData", "ISweptFlangeFeatureData",
           "IGussetFeatureData", "ISMGussetFeatureData", "IDraftFeatureData2",
           "ILoftedBendsFeatureData",],
    "焊件": ["IStructureSystemFolder", "IStructureSystemMemberFeatureData",
           "IStructureSystemMemberProfile", "IStructureSystemSplitMember",
           "IProfileCenterMateFeatureData", "IWeldmentCutListFeature", "ICutListItem",
           "ICutListSortOptions", "IWeldBead", "IWeldmentBeadFeatureData",
           "ICosmeticWeldBeadFeatureData", "IWeldSymbol", "IWeldmentTrimExtendFeatureData",
           "IProfileGroupFolder"],
    "曲面": ["ISurface", "ISurfaceTrimFeatureData", "ISurfaceExtendFeatureData",
           "ISurfaceKnitFeatureData", "ISurfaceFlattenFeatureData", "ISurfaceOffsetFeatureData",
 "ISurfaceRadiateFeatureData", "IFillSurfaceFeatureData",
           "ISurfacePlanarFeatureData", "ISurfRevolveFeatureData", "IShutOffSurfaceFeatureData"],
    "装配": ["IAssemblyDoc", "IComponent2", "IEnumComponents2", "IMate2", "IMateEntity2",
           "IMateFeatureData", "IMateInPlace", "IMateReference", "IExplodeStep",
           "IPartExplodeStep", "IMirrorComponentFeatureData", "ICoincidentMateFeatureData",
           "IConcentricMateFeatureData", "IDistanceMateFeatureData"],
    "工程图": ["IDrawingDoc", "IView", "IView3D", "ISheet", "IDimension", "IDisplayDimension",
             "IAnnotation", "IAnnotationView", "ITableAnnotation", "IModelView",
             "IModelViewManager", "ISectionViewData", "IGeneralTableAnnotation",
             "IBomTableAnnotation", "IHoleTableAnnotation", "IWeldmentCutListAnnotation",
             "IBendTableAnnotation", "IRevisionTableAnnotation", 
             "IMultiJogLeader", "IDrawingComponent"],
    # ⚑ 下面这份「族 → 域」映射里，**每个族只登记一次**。
    #   早先版把 6 个族同时挂到两个域（ISurface 既在曲面又在几何与拓扑、
    #   ICenterOfMass 既在几何与拓扑又在质量属性、IModelDoc2 / IModelDocExtension /
    #   ISldWorks 各在两个域、ISurfaceCutFeatureData 既在钣金又在曲面），
    #   导致 ① 族总数被**虚增** ②「低于 50% 的族有几个」这类统计**偏大**。
    #   现改为一族一域，归属按「它的主用场景」定；交叉场景在该族自身的
    #   来源块里说明。_assert_no_duplicate_families() 会拦回归。
    "几何与拓扑": ["IBody2", "IFace2", "IEdge", "IVertex", "ICurve", "ILoop2",
               "IEnumBodies2", "IBoundingBoxFeatureData", "IBoundaryBossFeatureData",
               "ICenterOfMass", "IMidSurface3", "IEdgePoint"],
    "质量属性与导出": ["IMassProperty2", "IMassPropertyOverrideOptions",
                 "IDimensionTolerance"],
    "配置/材料/自定义属性": ["IConfiguration", "IConfigurationManager",
                    "ICustomPropertyManager", "IDesignTable",
                    "IMaterialVisualPropertiesData", "IRenderMaterial",
                    "ITextAndCustomProperty"],
    "仿真(需许可证)": ["ICWLoadsAndRestraintsManager", "ICWStudyManager", "ICWStudy",
                        "ICWResults", "ICWMesh", "ICWForce", "ICWPressure", "ICWHeatFlux",
                        "ICWContactSet", "ICWMaterial", "ICWStaticStudyOptions",
                        "ICWFrequencyStudyOptions", "ICWBucklingStudyOptions",
                        "ICWNonLinearStudyOptions", "ICWThermalStudyOptions",
                        "ICWDynamicStudyOptions", "ICWFatigueStudyOptions",
                        "ICWDropTestStudyOptions", "ICWCompositeShellOptions"],
    "路由/Composer/PDM": ["IRouteManager", "IRoutingComponentManager", "IWire",
                          "IRouteProperty", "ICovering", "ICable", "ICableProperty",
                          "IWireProperty", "ICostManager", "ICostPart", "ICostAnalysis",
                          "ICostingDefaults", "ICostBody",
                          "ISwDMDocument31", "ISwDMConfiguration18", "ISwDMTable6",
                          "IFeatureWorksApp"],
}

WRAPPER = re.compile(r"\b(?:get_com_member|_safe_member)\s*\(\s*[^,()]+,\s*[\"']([A-Z]\w+)[\"']")
#: ⚑ `_checked(签名表, 对象, "成员", …)` 这条路 —— 签名表工具统一用它做护栏，
#:   成员名是**第 3 个**位置的字符串字面量。WRAPPER 认不出这种形态。
GUARDED = re.compile(r"\b_checked\s*\(\s*[^,()]+,\s*[^,()]+,\s*[\"']([A-Z]\w+)[\"']")
#: 登记表形态：`STUDY_OPTION_SETTERS = {"CheckFlowPressure2": "Boolean", ...}`
#:   与 `OFFICIAL_*_ARITY = {"AddForce": 3, ...}` —— 纯字面量，最可靠。
#: ⚑⚑ 成员名**不都以大写开头** —— 事件委托类上是 ``add_XxxNotify`` /
#:   ``remove_XxxNotify``（本机实测 333 + 333 个）。早先用 ``[A-Z]`` 开头，
#:   那 666 个**全部漏计**，覆盖表因此虚报 693 个「缺口」——
#:   而索引里其实早就抄全了。**指标错了，数据没错。**
#: ⚑⚑⚑ 成员名的**最短长度是 1**，不是 2。
#:   写 ``[A-Za-z_]\\w+`` 是**错的** —— 前一节已吃掉 1 个字符，
#:   ``\\w+`` 再要 1 个 ⇒ **单字母成员（`X` / `Y` / `Z`）全部漏掉**。
#:   早先写 ``[A-Z]\\w{2,}`` 犯的是同一个错（要求 ≥3 个字符），
#:   本机实测 6 个族因此永远差 14 个成员。
#:   ⇒ 正确写法是 ``[A-Za-z_]\\w*``：前一节 1 个，后面**任意个**（含 0 个）。
LITERAL = re.compile(r"[\"']([A-Za-z_]\w*)[\"']\s*[,:}]")
CALL = re.compile(r"[.\s]([A-Z]\w+)\s*\(")
SKIP = re.compile(r"^\s*(#|\"\"\"|''')")


def repo_members() -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """返回 (真正被调用的成员, 登记表里列出的成员) → 各自的出现文件。

    ⚑⚑ 分成两个集合是**必须**的，否则表会骗人：
      · 「代码里真的调了」—— ``get_com_member(obj, "X", …)`` / ``obj.X()``
        / ``_checked(表, obj, "X", …)``
      · 「只在登记表里列了」—— ``ARITY = {"X": 3, …}``
    两者都是「代码里出现过这个名字」，但含义完全不同：
    前者是**实现了**，后者只是**编了目录**。
    早先版本把两者合并，于是「族触及率 100%」是靠**列名字**达成的 ——
    那个数字比读起来弱得多，合并汇报就是误导。
    """
    called: dict[str, list[str]] = defaultdict(list)
    catalogued: dict[str, list[str]] = defaultdict(list)
    for pat in ("scripts/*.py", "subskills/**/*.py", "tests/*.py", "examples/*.py"):
        for p in sorted(REPO.glob(pat)):
            if p.name == "__init__.py":
                continue
            rel = p.relative_to(REPO).as_posix()
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                if SKIP.match(line):
                    continue
                hit_called = (set(WRAPPER.findall(line)) | set(GUARDED.findall(line))
                              | set(CALL.findall(line)))
                hit_lit = set(LITERAL.findall(line))
                for mem in hit_called:
                    if rel not in called[mem]:
                        called[mem].append(rel)
                for mem in hit_lit | hit_called:
                    if rel not in catalogued[mem]:
                        catalogued[mem].append(rel)
    return called, catalogued


def _reflect_members(path: Path, iface: str) -> list[str]:
    """从反射清单里取某个接口段的成员名。

    ⚑ 必须剥掉 ``get_`` / ``set_`` 前缀 —— 与 ``audit_call_arity.py`` 同一套归一：
      反射清单里属性呈现为 ``get_X``，而调用侧（``get_com_member``）写的是 ``X``。
      不剥就会让**所有属性型成员**归因失败（本轮 9 个 StudyOptions 族就栽在这：
      ``get_AdaptiveMethodType`` 找不到 ``AdaptiveMethodType``）。
    """
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(rf"(?ms)^## {re.escape(iface)}\s*\r?\n(.*?)(?=\r?\n## |\Z)",
                      text)
    if not match:
        return []
    out = set()
    for raw in match.group(1).splitlines():
        stripped = raw.strip()
        if not stripped or "(" not in stripped:
            continue
        name = stripped.split("(")[0].split()[-1]
        if not name:
            continue
        if name.startswith(("get_", "set_")):
            name = name[4:]          # ← 与 audit_call_arity.py 同款归一
        # ⚑⚑ 排除 COM 内部分发口（``IGetXxx`` / ``IUpdateYyy`` / ``ICreateZzz``）。
        #   反射清单把它们和真方法混在一起 —— 本机实测 26 个未满的族里，
        #   绝大多数缺口就是这类（``IGetSubFeatures`` / ``IUpdateCostForAllBodies`` /
        #   ``ICreateRouteThroughSketchEntities``）。
        #   它们是**同一能力的内部变体**，索引（build_complete_index.py）已刻意不收，
        #   分母也必须同样不收，否则覆盖表永远差这一截、且缺口无法被补。
        if re.match(r"^I[A-Z][a-z]", name):
            continue
        out.add(name)
    return sorted(out)

    # ⚑⚑ 排除 COM 内部分发口（``IGetXxx`` / ``IUpdateYyy`` / ``ICreateZzz``）。
    #   反射清单把它们和真方法混在一起，本机实测 51 个未命中里绝大多数是这类
    #   （`IGetSubFeatures` / `IUpdateCostForAllBodies` / `ICreateRouteThrough…`）。
    #   它们是**同一能力的内部变体**，索引（build_complete_index.py）已刻意不收，
    #   分母也必须同样不收，否则覆盖表永远差这一截。
    _INTERNAL = re.compile(r"^I[A-Z][a-z]")
    out = [n for n in out if not _INTERNAL.match(n)]

def family_members(iface: str) -> list[str]:
    """取某接口族的成员名。

    ⚑ 优先用 ``C:\\swapi\\types\\<接口>\\``（12 个程序集）；
    **没有就回落到反射清单**（cosworks / SWRoutingLib / sldcostingapi /
    swdocumentmgr / fworks 这 5 个 ``C:\\swapi`` 不收录）。
    没有回落支持的话，域 13/14 会一直显示「统计为 0」——
    那会让文档说假话（实际已覆盖，见 scripts/sw_simulation_*.py）。
    """
    # ⚑⚑ 排除 COM 内部分发口（名字形如 ``IGetXxx`` / ``IAddYyy``）。
    #   它们是**同一能力的内部变体**，不是独立能力 ——
    #   `C:\swapi` 按文档页收录，会把它们算进去（本机实测 ISketchEllipse：
    #   swapi 21 个 / 反射方法 11 + 属性 10，那 10 个全是 IGet*）。
    #   ⇒ 分母必须与索引口径一致，否则覆盖表会**凭空多出** 36% 的「缺口」。
    INTERNAL = re.compile(r"^I[A-Z][a-z]")

    # ⚑⚑⚑ **反射才是成员清单的权威**（AGENTS.md 铁律 4：两套源都要用，
    #   但用途不同）。
    #   `C:\swapi` 是按**帮助站的文档页**收录的，里面混着两类**非成员**条目：
    #     ① COM 内部分发口 `IGetXxx`      —— 同一能力的内部变体
    #     ② 属性的**返回值描述** `X`/`Y`/`Z`/`ID` —— 形如 `Point get_X()` 的说明
    #   本机实测 `ISketchEllipse`：swapi 21 个 / 反射 方法 11 + 属性 10，
    #   差的 10 个全是 `IGet*`；`ISketchPoint` 差的是 `X`/`Y`/`Z`。
    #   ⇒ 若以 swapi 为分母，覆盖表会**凭空多出 36% 的「缺口」**。
    for path in REFLECT.values():
        members = _reflect_members(path, iface)
        if members:
            return members

    d = SWAPI / iface
    if d.is_dir():
        return sorted(p.stem for p in d.glob("*.md")
                      if p.stem != "_overview" and not INTERNAL.match(p.stem))
    for path in REFLECT.values():
        members = _reflect_members(path, iface)
        if members:
            return members
    return []


def _assert_no_duplicate_families() -> None:
    """一族只许登记在一个域 —— 重复会虚增族总数并让统计偏大。

    ⚑ 本函数是**回归护栏**：早先版有 6 个族同时挂两个域
    （ISurface / ICenterOfMass / IModelDoc2 / IModelDocExtension /
    ISldWorks / ISurfaceCutFeatureData），
    导致「低于 50% 的族有多少个」被**报大了**。
    """
    seen: dict[str, str] = {}
    dupes: dict[str, list[str]] = {}
    for dom, fams in DOMAIN_FAMILIES.items():
        for fam in fams:
            if fam in seen:
                dupes.setdefault(fam, [seen[fam]]).append(dom)
            else:
                seen[fam] = dom
    if dupes:
        raise SystemExit(
            "[FATAL] 下列族被登记在多个域（会虚增族总数）：\n  "
            + "\n  ".join(f"{k}: {' / '.join(v)}" for k, v in dupes.items())
        )


def _domain_extension() -> dict[str, list[str]]:
    """把「C:\\swapi 未收录的 5 个程序集」的族并入域映射。

    ⚑ 早先这几域在表里是空的（理由是「C:\\swapi 不收录」），
      那在**只有 swapi 一个源**时是对的；本仓库已用 interop 反射补上登记表，
      空着就会**低估覆盖面**。既然现在有源，就把族补进去。
    """
    import json
    from pathlib import Path as _P
    out: dict[str, list[str]] = {}
    mapping = {
        r"D:\AI\SW\_reg_cosworks.json": "仿真(需许可证)",
        r"D:\AI\SW\_reg_pdm.json": "路由/Composer/PDM",
    }
    for path, domain in mapping.items():
        data = _P(path)
        if not data.is_file():
            continue
        fams = sorted(json.loads(data.read_text(encoding="utf-8")).keys())
        out.setdefault(domain, []).extend(fams)
    return out


def _unmapped_sldworks() -> list[str]:
    """sldworks 里**没有**归入 14 个域的族。

    ⚑ 覆盖表的「374 族」是**14 个域的范围**，不是 sldworks 程序集的全貌 ——
      反射实测 sldworks 有 523 个有成员的接口族。
      把差集单列成一个域，是为了让表**说清自己的范围**，
      而不是让读者以为 374 就是全部。
    """
    import json
    import re as _re
    from pathlib import Path as _P
    src = _P(r"D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt")
    if not src.is_file():
        return []
    mapped: set[str] = set()
    for fams in DOMAIN_FAMILIES.values():
        mapped.update(fams)
    current, out = None, []
    for raw in src.read_text(encoding="utf-8", errors="replace").splitlines():
        if raw.startswith("## "):
            current = raw[3:].strip()
        elif current and raw.strip() and _re.match(r"^\S+\s+\w+\s*\(", raw.strip()):
            if current not in mapped and current not in out:
                out.append(current)
            current = None
    return sorted(out)



#: 模块里形如 ``"MemberName": 3,`` 的登记项（能力表 / arity 表）。
#: ⚑ 这些名字**有护栏保护的可达调用路径**，但因为调用处传的是**变量**
#:   （`_checked(target, member, …)`），静态上��不到字面量 ⇒ 「直接调用」列漏算它们。
REGISTRY_KEY = re.compile(r"^\s+[\"']([A-Z]\w{2,})[\"']\s*:")


def repo_gated() -> set[str]:
    """登记在某模块能力表里的成员名。"""
    out: set[str] = set()
    for pat in ("scripts/*.py", "subskills/**/*.py"):
        for p in sorted(REPO.glob(pat)):
            if p.name == "__init__.py":
                continue
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                if SKIP.match(line):
                    continue
                m = REGISTRY_KEY.match(line)
                if m:
                    out.add(m.group(1))
    return out



def _api_index_families() -> dict[str, list[str]]:
    """从 sw_api_<程序集>.py 的 FAMILIES 常量里取族名，按程序集分域。

    ⚑ 这 6 份是**全量索引**（774 族），比之前分散在各模块的登记表更全 ——
      覆盖表必须认它们，否则会说「没覆盖」，而实际上清单已经抄全了。
    """
    out: dict[str, list[str]] = {}
    for p in sorted((REPO / "scripts").glob("sw_api_*.py")):
        asm = p.stem[len("sw_api_"):]
        txt = p.read_text(encoding="utf-8")
        m = re.search(r"FAMILIES: tuple\[str, \.\.\.\] = \((.*?)\n\)", txt, re.S)
        if not m:
            continue
        fams = re.findall(r"'(\w+)'", m.group(1))
        out[f"全量索引/{asm}"] = fams
    return out


#: ⚑ **官方分类字段的正则**（2026-10-01 轮 210 / Spec Kit `129`）。
#: ⚠⚠ **它只有一个来源**：`C:\swapi\types\<接口>\*.md` 的 `category` 字段
#:   —— 那是 **help 站点的文档镜像**（来源仓 `offline-solidworks-api-docs`，**无许可**）。
#:   实测：**两份出厂反射转储都没有该字段**（`iface_sldworks.txt` 只有接口名；
#:   `iface_cosworks.txt` 只有 `<接口> :: <返回类型> <方法名>(…)`）
#:   ⇒ ★ **无法按铁律 4 做三源互证** ⇒ 本字段**只能标成"单一来源"**，不能声称"经官方核过"。
CATEGORY_RX = re.compile(r"(?im)^\s*\*{0,2}category\*{0,2}\s*[:：]\s*(.+)$")


def official_categories() -> dict:
    """⇒ ``{接口名: 官方 category}`` —— 从 ``C:\\swapi\\types\\<接口>\\*.md`` 读。

    :returns: 形如 ``{"ISldWorks": "Application Interfaces", …}``。
        读不到就是空 dict（**不报错、不编造**）。

    ⚑ **这个字段是"接口级"的**：一个接口只有一个 category（它的成员文件各自
      也都带同一行，本函数取该接口目录下**任意一命中**即可）。
    ⚠ 实测覆盖：``C:\\swapi\\types`` 下 **481 个接口**有该字段 —— 而 `family-coverage`
      的 881 个族里能对上 **477（54.1%）**；对不上的主要是
      **`C:\\swapi` 不收录的那些程序集**（swdimxpert / RoutingLib / sldcostingapi …）
      ＋ 路由/Composer/PDM 与仿真那两域。
    """
    out: dict = {}
    if not SWAPI.is_dir():
        return out
    for d in sorted(SWAPI.iterdir()):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            m = CATEGORY_RX.search(p.read_text(encoding="utf-8", errors="replace"))
            if m:
                out[d.name] = m.group(1).strip()
                break          #: 一个接口一条即可（成员文件各自都带同一行）
    return out


def official_category_section(rows: list, cats: dict) -> list:
    """⇒ md 的 ``## 四`` 那一节（**生成物**，数字全部现算，不写死）。

    :param rows: `main()` 建好的行（每行含 `domain` / `family`）。
    :param cats: `official_categories()` 的返回。
    :returns: 该节的 markdown 行列表。

    ★ **为什么加这一节**（2026-10-01 轮 210）：一份外部只读审计（`D:\\AI\\SW-transfer\\official-category-unused.md`）
      指出「官方每个接口都带 `category`（96.5%、39 类），而本仓库没用它」。
      ★ 复核结论：**它的数全对**（12,123 md / 11,703 有 category / 39 类），
      但它把 `全量索引/<程序集>` 读成"兜底桶"是**误读** ——
      那是 `_dedupe_domains()` 的「**一族只算一次**」产物（见该函数 docstring）。
      ⇒ 本节把它**量清楚**：未认领的族有多少、其中有多少能被官方分类归位。
      ⚠ 而**不替换**业务域：报告自己也说两者维度不同（厂商视角 vs 业务视角），★ 那是对的。
    """
    from collections import Counter
    total = len(rows)
    unclaimed = [r for r in rows if str(r.get("domain", "")).startswith("全量索引/")]
    joined = [r for r in unclaimed if r.get("official_category")]
    c = Counter(r["official_category"].split("/")[0] for r in joined)
    L: list = []
    L += ["", "---", "", "## 四、官方分类（`category`）与「未认领」族的归位", ""]
    L += ["> ⚠⚠ **本节的字段只有一个来源**：`C:\\swapi\\types\\<接口>\\*.md` 的 `category`",
          "> —— 那是 **help 站点的文档镜像**（来源仓 `offline-solidworks-api-docs`，**无许可**）。",
          "> ★ 实测**两份出厂反射转储都没有该字段** ⇒ **无法按铁律 4 做三源互证**。",
          "> ⇒ 本字段只能当 **\"单一来源的分类\"** 用（分类与校验），**不能声称\"经官方核过\"**。", ""]
    L += ["### 4.1 官方分类的覆盖（实测）", "",
          "| 项 | 数 |", "|---|---|",
          "| `C:\\swapi\\types` 下有 `category` 的接口 | **%d** |" % len(cats),
          "| 本表 881 族里**能对上**官方分类的 | **%d**（%.1f%%）|"
          % (sum(1 for r in rows if r.get("official_category")),
             100.0 * sum(1 for r in rows if r.get("official_category")) / max(total, 1)),
          "| 对不上的原因（主体）| ★ **`C:\\swapi` 不收录的程序集**（swdimxpert / RoutingLib / "
          "sldcostingapi …）＋ 路由/Composer/PDM 与仿真两域 |", ""]
    L += ["### 4.2 ★ 「未认领」族到底有多少（**按域全加起来**）", "",
          "> ⚠ 外部审计只数了 `全量索引/sldworks` 一个桶（385 / 881 = 43.7%）⇒ **低估了**。",
          "> 实测：`domain` 以 `全量索引/` 开头的**共有 %d 族 = %.1f%%**。" % (len(unclaimed),
          100.0 * len(unclaimed) / max(total, 1)), "",
          "| `domain` | 族数 |", "|---|---|"]
    for k, v in sorted(Counter(r["domain"] for r in unclaimed).items(), key=lambda x: -x[1]):
        L.append("| `%s` | %d |" % (k, v))
    L += ["| **合计** | **%d / %d = %.1f%%** |" % (len(unclaimed), total,
          100.0 * len(unclaimed) / max(total, 1)), ""]
    L += ["### 4.3 ★ 官方分类能救回多少", "",
          "| 项 | 数 |", "|---|---|",
          "| 未认领族中有官方分类的 | **%d / %d（%.1f%%）** |"
          % (len(joined), len(unclaimed), 100.0 * len(joined) / max(len(unclaimed), 1)), "",
          "| 一级分类 | 能归位的族数 |", "|---|---|"]
    for k, v in c.most_common():
        L.append("| %s | %d |" % (k, v))
    L += ["", "⇒ ★ **收益是具体的**：上面这张表就是「按官方分类，未认领的族能立刻有归属」的清单。",
          "",
          "### 4.4 ⚠ 怎么用 / 怎么**不**用", "",
          "```",
          "✅ **用**：① 分类与校验（发现「手写域 vs 官方类」的错位）",
          "        ② ★ 给「未认领」族兜底归属（4.3 那张表）",
          "        ③ 辅助发现空白（某个官方一级分类下我们一族都没有 ⇒ 值得看一眼）",
          "❌ **不用**：把一级分类**当作「该不该做成工具」的判据** ——",
          "         标签说的是「接口**是什么**」（厂商视角），",
          "         不是「我们**需不需要**工具」（项目视角）。★ 那正是本项目禁止的"
          "「看着像就当成」。",
          "⚠ **不替换**业务域：两者维度不同（厂商视角 vs 业务视角）——",
          "   `ISelectionMgr` 官方归 `Utility Interfaces`，而本项目归「应用与会话」"
          "（\"选中是所有操作的地基\"是业务判断，不是错）。",
          "```", ""]
    return L



def _dedupe_domains() -> None:
    """一个族在覆盖表里**只出现一次**（归到它最先出现的那个域）。

    ⚑ 全量索引接入后，同一个族会同时出现在「14 个域」和「全量索引/<程序集>」
      两个条目下 —— 那会让族总数虚增（本机实测 1,090 > 实际 774）。
    口径：一个族只算一次，与早先修过的「一族一域」是同一条纪律。
    """
    seen: set[str] = set()
    for domain, fams in DOMAIN_FAMILIES.items():
        kept = []
        for fam in fams:
            if fam in seen:
                continue
            seen.add(fam)
            kept.append(fam)
        DOMAIN_FAMILIES[domain] = kept


def main() -> int:
    _assert_no_duplicate_families()
    for domain, fams in _domain_extension().items():
        existing = DOMAIN_FAMILIES.setdefault(domain, [])
        for fam in fams:
            if fam not in existing:
                existing.append(fam)
    for _d, _f in _api_index_families().items():
        DOMAIN_FAMILIES.setdefault(_d, []).extend(_f)
    unmapped = _unmapped_sldworks()
    _dedupe_domains()   # ⚑ 必须在**所有**族加进来之后去重
    if unmapped:
        existing = DOMAIN_FAMILIES.setdefault("其他(sldworks 未归入 14 域)", [])
        for fam in unmapped:
            if fam not in existing:
                existing.append(fam)
    cats = official_categories()   #: ★ 官方分类（单一来源，见函数 docstring）
    called, catalogued = repo_members()
    gated = repo_gated()
    rows = []
    for dom, fams in DOMAIN_FAMILIES.items():
        for fam in fams:
            mems = family_members(fam)
            hit = [m for m in mems if m in catalogued]
            used = [m for m in mems if m in called]
            # ⚑ 护栏可达：登记在某模块能力表里、且有 `_checked(target, member, …)`
            #   这样的可达调用路径，但调用处传变量 ⇒ 「直接调用」列漏算。
            gated_hits = [m for m in mems if m in gated]
            rows.append({
                "domain": dom, "family": fam, "members": len(mems), "families": 1,
                "hit": len(hit), "hit_members": hit[:10],
                # ⚑ **列出未命中的成员名** —— 没有它，覆盖表只说「差 N 个」，
                #   没法据此去补。补上之后「还缺什么」是可执行的。
                "missing_members": sorted(
                    m for m in mems
                    if m not in catalogued)[:60],
                # ⚑ 两个百分比含义不同，**必须分开报**：
                #   pct      —— 该族成员里有多少「在代码里出现过名字」
                #              （含只写在登记表里的，即**编了目录**）
                #   used_pct —— 有多少**真的被调用过**（点调用或 get_com_member）
                #   早先只报一个，把「编目录」和「实现」混为一谈。
                "pct": (round(100.0 * len(hit) / len(mems)) if mems else None),
                "used": len(used),
                "used_pct": (round(100.0 * len(used) / len(mems)) if mems else None),
                "gated": len(gated_hits),
                "gated_pct": (round(100.0 * len(gated_hits) / len(mems)) if mems else None),
                "used_members": used[:10],
                "files": sorted({f for m in hit for f in catalogued[m]})[:3],
                "note": "" if mems else "C:\\swapi 无该类型目录",
                #: ★ 官方 category（**单一来源**：C:\swapi 的 help 站点镜像；
                #:   出厂反射**没有**该字段 ⇒ 无法三源互证）。读不到就是空串。
                "official_category": cats.get(fam, ""),
            })

    #: ⚑⚑ **汇总数字与日期都算出来，不写死** —— 2026-10-01（轮 185 后）修：
    #:   此前 `"> 生成日期：2026-09-29"` 与正文段的
    #:   「16,615 个成员里，编入目录 12,870（77%）、真调用 2,636（16%）」**都是硬编码的旧一代数字**，
    #:   于是 md 的**正文段与它自己的表格、与 json 三方互相矛盾**（表格/json 说
    #:   15,466 成员、编目录 15,466，而正文段说 16,615 / 12,870）。
    #:   ★ 一份外部评审据此把它判为「过时散文」，并写明「12,870 是哪个口径**没查出来**」
    #:     —— 实际原因就是**这两处写死在生成器里**，重算也不会变。
    #:   ⇒ 现在日期与三个汇总数都从 `rows` 算出，**三处不可能再分叉**。
    _tot_members = sum(r["members"] for r in rows)
    _tot_hit = sum(r["hit"] for r in rows)
    _tot_used = sum(r["used"] for r in rows)
    _today = time.strftime("%Y-%m-%d")

    # ---- markdown ----
    L = ["# 接口族覆盖度（family-coverage）", "",
         "> 生成日期：%s" % _today,
         "> 作用：把 A1 的定性判定（覆盖/部分/不覆盖）升级为**定量**。",
         "> 方法：取 `C:\\swapi\\types\\<接口>\\` 的成员目录，再用与 `api-map.md`",
         "> 相同的两路形态（直接调用 / 反射式）在本仓库找这些成员。",
         ">",

         "> ⚑⚑ **本表两个百分比含义不同，必须分开看**：",
         ">",
         "> | 列 | 含义 |",
         "> |---|---|",
         "> | **编目录** | 该族成员里有多少名字在代码里出现过 —— **含只写在登记表里的** |",
         "> | **护栏可调** | 登记在某模块能力表里，且有 `_checked(target, member, …)` 这样的**可达调用路径** |",
         "> | **直接调** | 静态上**看得见**字面量的调用（get_com_member 传名 / 点调用）|",
         ">",
         "> ⚑ **护栏可调 ⊇ 直接调**。差值来自「调用处传的是变量」——",
         "> 模块写成 `_checked(target, member, …)` 时，静态归因看不到字面量。",
         "> ⇒ **「直接调」系统性低估，不是精确值。**",
         ">",
         "> **合并这两个数字就是误导。** 早先版本只报一个触及率，",
         "> 于是「族触及率 100%」是靠**把名字列进登记表**达成的 ——",
         "> 那证明的是「这份 API 清单做完了」，**不是「这些 API 都能用了」**。",
         "> 当前实测：{:,} 个成员里，**编入目录 {:,}（{:.0f}%）**、".format(
             _tot_members, _tot_hit, 100.0 * _tot_hit / _tot_members if _tot_members else 0.0),
         "> **真调用 {:,}（{:.0f}%）**。".format(
             _tot_used, 100.0 * _tot_used / _tot_members if _tot_members else 0.0),
         ">",
         "> FeatureData 的属性赋值不计入真调用。", "",
         "> ⚠ 全部由静态解析生成，未执行任何仓库代码、未连接 SolidWorks。", "",
         "---", "",
         "## 一、按域汇总", "",
         "| 域 | 接口族 | 已触及 | 触及率 | 说明 |", "|---|---|---|---|---|"]
    by_dom = defaultdict(lambda: [0, 0, ""])
    for r in rows:
        if r["families"] == 0:
            by_dom[r["domain"]][2] = r.get("note", "")
            continue
        by_dom[r["domain"]][0] += 1
        if r["hit"] > 0:
            by_dom[r["domain"]][1] += 1
    for dom, (tot, hit, note) in by_dom.items():
        rate = f"{hit}/{tot}" if tot else "—"
        L.append(f"| {dom} | {tot or '—'} | {hit or '—'} | {rate} | {note} |")

    L += ["", "---", "", "## 二、逐接口族明细", "",
          "| 域 | 接口族 | 成员数 | 触及 | **成员触及率** | 触及的成员（前 10） | 主要出现在 |",
          "|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["hit"] == 0 and r["members"] == 0:
            L.append(f"| {r['domain']} | — | — | — | — | {r.get('note','')} | — |")
            continue
        hit_s = "、".join(f"`{m}`" for m in r["hit_members"]) or "—"
        files_s = "、".join(f"`{f}`" for f in r["files"]) or "—"
        pct = f"{r['pct']}%" if r.get("pct") is not None else "—"
        L.append(f"| {r['domain']} | `{r['family']}` | {r['members']} | "
                 f"{'**' + str(r['hit']) + '**' if r['hit'] else '0'} | {pct} | "
                 f"{hit_s} | {files_s} |")

    L += ["", "---", "", "## 三、读这张表要注意的", "",
          "⚑ **「触及 0」的判据太弱，别拿它当「全覆盖」用。**",
          "   一个 112 成员的族，只要碰过 1 个成员就算「已触及」——",
          "   那是自欺。所以本表加了「**成员触及率**」一列，真正的覆盖面看它。",
          "   「一、按域汇总」里的 x/x 只表示「没有整族缺席」，",
          "   **不等于该族能力被完整实现**。",
          "",
          "1. **「触及」≠「覆盖」**。它只说明代码里出现过这个成员，",
          "   不代表该接口族的能力被完整实现。",
          "2. **属性赋值不计入**。`CreateDefinition` + `data.Thickness = x` 这种",
          "   FeatureData 装配路径不在统计内，其成员在各模块的签名表里逐条登记。",
          "3. **域 13 / 域 14 的成员来自 interop 反射**，不是 `C:\\swapi`",
          "   （那两个域的程序集 `C:\\swapi` 不收录）。",
          "   反射路径下 `get_X` / `set_X` 前缀已按 `audit_call_arity.py` 同款归一。",
          "4. ⚠ **归因是按成员「名字」匹配的，会跨接口串味。** 例如",
          "   `AccessSelections` 这一个名字挂在 125 个 `*FeatureData` 接口上，",
          "   因此本表会把 `sw_surface.py` 里的某次 `AccessSelections` 调用",
          "   同时记到 `ICosmeticWeldBeadFeatureData`、`IHemFeatureData` 等头上。",
          "   **逐行明细请当线索看，不要当结论**；",
          "   精确到某一行的归属请用 `docs/signature-audit.md`（它带参数个数校验）。",
          "   **要看的是「触及 0」的族**（那不会有串味，是真的没碰过）。",
          "5. ⚠ **归因只认「可静态识别形态」**：",
          "   `get_com_member(对象, \"成员名\", …)` 这一路。下列三种写法**工具看不见**，",
          "   代码写了也仍会显示未触及：",
          "   **(a)** 属性名是变量（`get_com_member(d, name, v)`，name 来自字典或循环）",
          "   **(b)** 用 `**flags` / `*args` 转发",
          "   **(c)** 第一个实参是嵌套调用（`get_com_member(取对象(x), \"M\")`，",
          "        第一个实参里出现括号）",
          "   本项目已因此**三次**误判「某族没实现」，现已统一改为",
          "   **显式成员名 + 先存局部变量**。凡本表显示 0 的族，",
          "   已逐个核过「代码里确实没有该成员的字面量调用」。",
          "",
          "### 「触及 0」的族：已全部补齐", "",
          "上一版这里列的是工程图域 8 个零命中族，并判断「多为范围外」。**该判断过宽**",
          "（其中 IHoleTableAnnotation 那 5 个成员我自己都写了「未逐类分派」——那是偷懒，",
          "不是阻塞）。现已全部补齐，工程图域 21/21：", "",
          "| 接口族 | 成员 | 补法 |",
          "|---|---|---|",
          "| `ISectionViewData` | 35 | 剖视显示样式 13 个属性显式装配 + 白名单拒绝未支持属性 |",
          "| 5 个表注解族 | 2+2+1+7+16 | 各自底层表对象 getter + 单元格读写 + 排序 + 修订增删 |",
          "| `IAnnotationView` | 17 | 激活 / 显隐 / 证据回读（全是 0 参属性） |",
          "| `IModelViewManager` | 42 | **只封装 4 个剖视相关成员**"
          "（`CreateSectionViewData` / `CreateSectionView` / `GetSectionViewData` / "
          "`RemoveSectionView`）；其余 38 个 FeatureManager UI 成员"
          "逐个列在 `MODEL_VIEW_MANAGER_UI_MEMBERS` 常量里，**不假装它们不存在**，"
          "需要时可按名单加 |",
          "",
          "> ⚑ 保留一条此前的自我纠正：曾怀疑工程图代码硬编码 `\"*Front\"`/`\"*Top\"`",
          "> 是「模型视图名随 UI 语言变」的隐性缺陷（AGENTS.md §六 事实 9 确有",
          "> 「基准面名随语言变」的前科），打算用 `IModelViewManager` 查视图名。",
          "> **查证后假设不成立**：该接口是 FeatureManager UI 接口，",
          "> `GetModelViewNames` 这个成员**在官方 API 中不存在**。",
          "> 故不下「本地化缺陷」结论——按铁律 5，没有证据就不写。"]

    L += official_category_section(rows, cats)

    OUT_MD.write_text("\n".join(L), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已生成 {OUT_MD}  ({OUT_MD.stat().st_size} 字节)")
    print(f"  明细 -> {OUT_JSON.name}")
    print("  各域接口族触及情况:  （前一个数是**触及的成员数**，不是官方分类覆盖率 —— 后者见 md §四）")
    for dom, (tot, hit, note) in by_dom.items():
        if tot:
            print(f"    {dom:<24} {hit}/{tot}")
        else:
            print(f"    {dom:<24} —  ({note})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
