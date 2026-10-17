"""★ 规格 209 · B2-1/B4-2/B4-4：把 unfold / fold / hem 三条能力写进 capabilities.yaml。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具/一次性施工脚本）
# 文件:   `tools/add_s209_b2_capabilities.py`
# 定位:   ★ 追加 **3 条**能力（`sheet_metal_unfold` · `sheet_metal_fold` · `sheet_metal_hem`），
#   并把本轮实测出来的**单位结论**补进既有的 `sheet_metal` 条目（★ 只加不改数）✓
#   ★★ 落盘纪律：`capabilities.yaml` 实测是 `json.dumps(indent=2, ensure_ascii=False)` 的**精确往返**
#     ⇒ load→改→dump 的 diff 极小；★ 但仍先看 `git diff --stat` 有没有意外的 deletions ✓
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
from pathlib import Path

CAPS = Path(Path(__file__).resolve().parents[1] / "capabilities.yaml")

HEM_EVID = ("★★★ 真机（2026-10-06 · 规格 209 的 **B2 批**）："
            "`python tools/sw_guard.py --timeout 900 -- python tools/probe_spec209_hem_diag.py` 与 "
            "`… probe_spec209_hem_units.py` ⇒ 60×40 的板、**五种形态**全部回 `None`。")
UNFOLD_EVID = ("★★★ 真机（2026-10-06 · 规格 209 的 **B2 批**）："
               "`python tools/sw_guard.py --timeout 900 -- python tools/probe_spec209_unfold_fold.py` ⇒ ")

UNIT_LIMITATION = (
    "★★★ **单位定案（2026-10-06 · 规格 209 实测）**：钣金 FeatureData 的长度参数按"
    "**文档长度单位**（本机 **毫米**）解释，**不是米** —— ★ 判据是**厚度棱的长度**"
    "（`IEdge::GetStartVertex/GetEndVertex` → `IVertex::GetPoint` 自己算；"
    "★★ `IEdge` 上**没有**长度成员）：传 `thickness=0.002` ⇒ 边长集合 `{0.002, 40.0, 60.0}`；"
    "传 `2.0` ⇒ `{2.0, 40.0, 60.0}` ⇒ ★★ **传 0.002 造出来的是 0.002 mm 的箔片**。"
    "⚠ `BaseFlangeSpec` 的 docstring 原写「全部长度单位为米」**是错的**（本轮**只更正文档、未改行为**）· "
    "★ 证据 `output/spec209-hem-units.json` ✓"
)

ENTRIES = [
    {
        "id": "sheet_metal_unfold",
        "label": "钣金展开（`IModelDoc2::InsertSheetMetalUnfold`，零参）—— ★ 真机建成 `展开1`",
        "level": "verified",
        "verified_versions": ["2026"],
        "backends": ["solidworks-com-pywin32"],
        "dependencies": ["solidworks"],
        "evidence": [
            UNFOLD_EVID + "特征树增量 **+1**、新特征 **`展开1`**；★★ **选择契约逐条回读**为 "
            "`total_count=2 · marks=[1, 4]`（固定面 **1** · 实体特征 **4**，★ mark 表逐字取自官方示例 "
            "`Insert_and_Access_Fold_Feature_Example_VB.md`）· 平展型式个数 `1`（`GetFlatPatternFolder` → "
            "`IFlatPatternFolder::GetFlatPatternCount`）✓ ★ 证据 `output/spec209-unfold-fold.json`、"
            "`output/spec209-unfold-contract.json`",
            "★ 官方依据逐页读过：`C:\\swapi\\types\\IModelDoc2\\InsertSheetMetalUnfold.md`（`void`，零参；"
            "`## Remarks` 逐字「**Select the objects for the unfold feature before calling this method.**」"
            "—— ★ **没给 mark**）· ★★ `examples\\Insert_and_Access_Fold_Feature_Example_VB.md`"
            "（**mark 与调用序的唯一出处**）· `ISelectionMgr\\{SetSelectedObjectMark,"
            "GetSelectedObjectMark}.md` · `enums\\swSelectionMarkAction_e.md` · "
            "`IFeatureManager\\GetFlatPatternFolder.md` · `IFlatPatternFolder\\GetFlatPatternCount.md`",
        ],
        "limitations": [
            "★★ **一条我原先写下的「负例」被真机证伪（按读数改口径）**：**不选任何 `mark 4` 对象**"
            "（只给固定面 mark 1）时**照样建出 `展开1`** ⇒ ★★ **`mark 4` 不是必需的** —— "
            "官方示例里选那些折弯是「照着做」，**不是「必需」** ✓",
            "★★★ **第一轮「没建出来」的真因是我自己的 bug**：`SetSelectedObjectMark` 的**第 3 参**是 "
            "`swSelectionMarkAction_e`，**必须传 `swSelectionMarkSet`(0)** —— ★ 传 `-1` 会"
            "**静默不生效**（返回 `false`、**不报错**）⇒ ★★ **失败的原因在我这边**（记下来）✓",
            "★ **面不能按名字选**（事实 32）⇒ 固定面走 `IEntity.Select4` **再补 mark**"
            "（★ `Select4` **没有** mark 形参）；★ 而 `face_index` 的**序号顺序官方未承诺稳定**"
            "（与体的拓扑生成顺序有关）⇒ **别当持久引用** ✓",
            "⚠ **未验**：★ 只在本机 SW 2026 SP4.1 的**闭轮廓基体法兰平板**上验过；"
            "★ **带真实折弯的钣金件**、多折弯、装配里的钣金件**均未验** ✓",
        ],
        "source_evidence": "★ 本仓自建（按官方签名 + 官方示例的**调用序与 mark** 立）："
                           "`C:\\swapi\\types\\IModelDoc2\\InsertSheetMetalUnfold.md` · "
                           "官方示例 `Insert_and_Access_Fold_Feature_Example_VB.md` · "
                           "`ISelectionMgr\\SetSelectedObjectMark.md` · `enums\\swSelectionMarkAction_e.md` "
                           "—— ★ **逐页读过** ✓ ★ 落点 `scripts/sw_sheet_metal.py`（已有模块，铁律 3）· "
                           "★ **不来自任何外部项目** ✓",
        "source": "original",
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "mcp_tools": ["solidworks_sheet_metal_create_unfold"],
    },
    {
        "id": "sheet_metal_fold",
        "label": "钣金折叠（`IModelDoc2::InsertSheetMetalFold`，零参）—— ★ 真机建成 `折叠1`",
        "level": "verified",
        "verified_versions": ["2026"],
        "backends": ["solidworks-com-pywin32"],
        "dependencies": ["solidworks"],
        "evidence": [
            UNFOLD_EVID + "**`unfold → fold` 一条链**（★ 与官方示例同形）：先建出 `展开1`，"
            "再以它当**前置特征（mark 0）**调 `InsertSheetMetalFold` ⇒ 特征树 **+1**、"
            "新特征 **`折叠1`**、`marks_readback=[1, 4]` ✓ "
            "★ 证据 `output/spec209-unfold-fold.json`",
            "★ 官方依据：`C:\\swapi\\types\\IModelDoc2\\InsertSheetMetalFold.md` · "
            "★★ 同一份官方示例 `Insert_and_Access_Fold_Feature_Example_VB.md` 的 **Fold 那一段**"
            "（★ 它比 Unfold 多一步：**先选已存在的 `Unfold1`**，mark 0）✓",
        ],
        "limitations": [
            "★★ **前置特征那一步必须在 `ClearSelection2` 之后** —— ★ 本仓第一版把它放在调用前，"
            "会被选择函数开头的清选区**清掉**（★ 顺序错、**静默失效**）✓",
            "★ 其余同 `sheet_metal_unfold`（mark 表 [1, 4] · 判据全回读 · 面不能按名字选）· "
            "⚠ **未验**：不带前置 `Unfold` 特征的 Fold、多折弯、装配里的 Fold ✓",
        ],
        "source_evidence": "★ 本仓自建（同 `sheet_metal_unfold` 的官方依据 + 官方示例的 Fold 段）✓ "
                           "★ 落点 `scripts/sw_sheet_metal.py` · ★ **不来自任何外部项目** ✓",
        "source": "original",
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "mcp_tools": ["solidworks_sheet_metal_create_fold"],
    },
    {
        "id": "sheet_metal_hem",
        "label": "钣金折边（`IFeatureManager::InsertSheetMetalHem2`，16 形参）—— "
                 "★★ **本机建不出**（如实记，标 stitched）",
        "level": "stitched",
        "verified_versions": ["2026"],
        "backends": ["solidworks-com-pywin32"],
        "dependencies": ["solidworks"],
        "evidence": [
            HEM_EVID + "★ 每一次都是一个**可证伪的假设**（★ 不是「换个参数再试」）："
            "① 边 `index:0`（可能是 2 mm 厚度棱）· ② 边 = **最长边**（`index:4`，60 mm 外缘）· "
            "③ 长度参数**整体 ×1000**（毫米口径）· ④ `UseDefaultRelief=True` · "
            "⑤ 板厚从 **0.002（箔片）改成 2.0（真 2 mm）** ⇒ ★★ 全部回 `None` ✓ "
            "★ 证据 `output/spec209-hem-diag.json` · `output/spec209-hem-units.json`",
            "★ 官方依据逐页读过：`C:\\swapi\\types\\IFeatureManager\\InsertSheetMetalHem2.md`"
            "（**16 形参** + `## Remarks` 的**四步前置**）· "
            "`examples\\Insert_Sheet_Metal_Hem_Example_VB.md`（调用序）· "
            "`IFeatureManager\\CreateCustomBendAllowance.md` · `ICustomBendAllowance\\Type.md` · "
            "`enums\\{swHemTypes_e,swHemPositionTypes_e,swSheetMetalReliefTypes_e,swReliefTearTypes_e}.md`",
        ],
        "limitations": [
            "★★★ **五种形态全部回 `None` ⇒ 本机（SW 2026 SP4.1 + pywin32）建不出折边** "
            "⇒ ★ 按**事实 53**（同一启发式连续修补 ≥3 次即停）**当场停止**，★ **不再凑形态** ✓ "
            "★ 而**成员名与 16 参顺序、五个枚举值已逐条核对官方无误**；"
            "官方 `## Remarks` 的四步前置（`CreateCustomBendAllowance` → 初始化 → 赋 `PCBA` → "
            "**再**选边）**已按序照做**（★ 我第一版顺序反了，已修）仍 `None` ✓",
            "★★ **价值在别处（裁决书原话：「dp5 的发现比实现本身更值」）**：别家调的 "
            "`InsertHemFeature2` 在官方全树**零命中**（真名 `InsertSheetMetalHem2`）· "
            "别家把 `swHemTypes_e` 的 `Open=0`/`Closed=1` **正好互换** · **漏掉 `Double=4`** "
            "⇒ ★★ 这三处已做成**常量表 + 静态断言**（`tests/test_tool_specs_batch93.py`："
            "五个成员一个不漏 · 幻觉名不许进代码）✓",
            "★★ **下一步（写清楚，免得后人重走）**：① 找一个**现成的带折弯钣金件**当夹具"
            "（★ 本机磁盘上**没有**这种模型 —— 全盘扫过 `.SLDPRT`）；② 或换 `InsertSheetMetalHem`"
            "（**已 Obsolete** 的前代）；③ 或**先做成 `InsertSheetMetalFold` 造出折弯**再回来 ✓",
            "★ `ICustomBendAllowance::Type` 的 `## Remarks` 逐字：「use this property to set the value "
            "for the type … **If you do not set this property last, the ICustomBendAllowance property "
            "set last automatically overrides any previously set custom bend allowance type.**」"
            "⇒ ★ 本仓**先设 `KFactor`、最后设 `Type`**（★ 官方示例顺序相反，但 `KFactor` 恰好也等于 2 "
            "⇒ 它**靠巧合成立**）✓",
        ],
        "source_evidence": "★ 本仓自建（按官方签名 + Remarks + 官方示例立）· 落点 "
                           "`scripts/sw_sheet_metal.py`（已有模块，铁律 3）· "
                           "★ 官方真名由 `*InsertHem*` **全树扫描**确认（别家的 `InsertHemFeature2` 零命中）· "
                           "★ **不来自任何外部项目**（而本次恰恰是**核实别家的三处错误**）✓",
        "source": "original",
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "mcp_tools": ["solidworks_sheet_metal_create_hem"],
    },
]


def main() -> int:
    text = CAPS.read_text(encoding="utf-8")
    data = json.loads(text)
    caps = data["capabilities"]

    added = 0
    for e in ENTRIES:
        if any(c.get("id") == e["id"] for c in caps):
            print("★ %s 已存在 ⇒ 跳过" % e["id"])
            continue
        caps.append(e)
        added += 1
    #: ★ 把**单位结论**补进既有的 `sheet_metal` 条目（★ 只加一条 limitation，不改别的数）
    hit = [c for c in caps if c.get("id") == "sheet_metal"]
    if len(hit) == 1 and "0.002 mm 的箔片" not in json.dumps(hit[0], ensure_ascii=False):
        hit[0].setdefault("limitations", []).insert(0, UNIT_LIMITATION)
        print("★ sheet_metal：补入单位定案 limitation")
    else:
        print("★ sheet_metal：条目数 %d 或已补过 ⇒ 跳过" % len(hit))

    out = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    json.loads(out)
    CAPS.write_text(out, encoding="utf-8")
    print("★ 追加 %d 条 ⇒ capabilities 共 %d 条" % (added, len(caps)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
