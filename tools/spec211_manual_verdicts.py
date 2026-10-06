"""★ 规格 211 · B0 的**人工终判表**（★ 每条注明依据；★ 只补空、不覆盖自动结果）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B0）
# 文件:   tools/spec211_manual_verdicts.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B0**。★ 自动台账（`tools/gen_spec211_ledger.py`）
#   只能给**信号**（★ `AccessSelections` 是**关键词共现**、★ 太粗）；★ 本表是**逐项人工读官方页后**的**终判** ✓
#   ★★ 依据**事实 53**：同一个启发式已连续改 **3 次** ⇒ ★ **停止调它**，改成「信号 + 人工终判」✓
# 判据:   ★ 每条 VARCHAR 三选一：
#     `可做`   —— ★ `swapi` 侧有**参数式直接入口**，★ 且**不带 `AccessSelections`** ✓
#     `不做`   —— ★ 带依据：① 四处零命中（官方无入口）· ② 入口要 `AccessSelections`（**事实 47**，★ 不试）✓
#     `待实测` —— ★ 需真机确认（如本机有没有装那个产品）✓
#   ★★ 本表**只补空**：★ 自动结果里已经是"可做"的，本表**不推翻**（★ 一致才写，不一致要写 `override` 并把理由写清）✓
# 官方依据: `C:\swapi\types\*\*.md` 的 `**Signature**` 行 +
#   `D:\AI\SW\AI Solidworks\官方文档\SWhelp\` 的 API 页名（★ 两者覆盖面不同，★ 都要查）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

#: ★★ **21 项人工终判** —— ★ 每条带 `依据`（★ 官方成员名 + 出处）✓
#: 结构：`项名: (域, 终判, 依据)`
VERDICTS = {
    "边界凸台": ("特征", "不做", "★ 入口 = `IBoundaryBossFeatureData`（CHM 有 `~AccessSelections`）⇒ "
                            "属性式**要 ACL** ⇒ **事实 47**（后端限制）· ★ `AutoSelect` 或可绕开但**不试**"),
    #: ★★★★ 2026-10-07（B5 **实测纠正**）：★ 这条**原判「可做」是错的** ✗ —— ★ 链条四步：
    #:   ① ★ 老的参数式入口 **`IModelDoc2::FeatureCurvePattern` 已标 `Obsolete`** ✗
    #:      （★ 官方逐字：See `IFeatureManager::CreateFeature` and the Remarks of
    #:       `ICurveDrivenPatternFeatureData`）★ —— ★★ **宿主是 `IModelDoc2`、不是
    #:       `IFeatureManager`** ⇒ ★ **我台账原先就写错了宿主** ✗
    #:       ★（★ 事实 36 明写：★ 同名接口分属不同族、**用错接口就没反应** ✓）
    #:   ② ★ 现代唯一入口 = `IFeatureManager::CreateFeature` + **`ICurveDrivenPatternFeatureData`**
    #:      ⇒ ★ 那是**属性式** ✗
    #:   ③ ★★ 而那个 Data 接口**带 `AccessSelections`** ✓（★ 逐文件核过：`AccessSelections.md`
    #:      与 `IAccessSelections.md` 都在 ✓）
    #:   ④ ★★ 而 `AccessSelections` 族在 pywin32 后端**不可调用**（**事实 47**，20+ 形态穷尽）✗
    #:   ⇒ ★★★ **所以「曲线驱动阵列」= 不做（后端限制）** ✓
    #:     ★★ 且仓里已有的 `sw_pattern.configure_curve_driven_pattern` **走的正是**那条属性式路
    #:     （★ `with edit_selection(data, model, "ICurveDrivenPatternFeatureData")` ✓）⇒
    #:     ★ **它到不了建成** —— ★ 与**事实 47** 记的 `create_one_bend`/`create_edge_flange`/
    #:     `create_gusset` 三条**同型** ✓
    "曲线驱动阵列": ("特征", "不做", "★★ **后端受限** —— ★ 链条：① 老的参数式入口 "
                             "`IModelDoc2::FeatureCurvePattern` **已标 `Obsolete`** ✗；② 现代唯一入口 "
                             "`IFeatureManager::CreateFeature` + `ICurveDrivenPatternFeatureData`（★ **属性式**）✗；"
                             "③ 该 Data 带 **`AccessSelections`**；④ **事实 47**：该族在 pywin32 后端**不可调用** "
                             "⇒ ★ **不做** ✓ ★（★ 仓里既有实现走的正是那条属性式路 ⇒ **到不了建成** ✓）"),
    "缩放/变形": ("特征", "可做", "★ `IFeatureManager::InsertScale(short Type, …)`（**参数式、无 ACL**）"),
    "特征识别/Instant3D": ("特征", "不做", "★ **四处零命中** ⇒ 官方无 API 入口（铁律 5）· "
                                   "★ CHM 的 9 个 `Instant3D` 页是**用户手册**、★ 不在 API 命名空间"),
    "扫描曲面": ("曲面", "可做", "★ `InsertSweepSurface2` / `InsertSweepSurface3`（**参数式、无 ACL**）"),
    "边界曲面": ("曲面", "可做", "★ `CreateRuledSurface` / `InsertRuledSurfaceFromEdge2`（**参数式、无 ACL**）"),
    #: ★★★★ 2026-10-07（B2 **实测纠正**）：★ 这条**原判「可做」是错的** ✗ ——
    #:   ★ 覆盖表**早就写着**：「`scripts/sw_surface.py` 有实现，但**三条入口真机全不成**
    #:   （**已知事实 417–419**）⇒ 工具面不计」✓
    #:   ★★ 依据 **事实 419**（★ 逐字）：「一类现象单列：**照官方例子把前置完全对上**」
    #:     **而特征仍不建** —— 两个案例（**剔裁曲面** + 投影型分割线）✓
    #:   ⇒ ★★★ **所以「剪裁曲面」= 不做（后端受限）**；★ 而**"取消剪裁"是另一半** ——
    #:     ★ 它在 B2-1 里**补了包装**、★ 负例有真机证据（★ `untrim_surface` = `stitched`）✓
    #:   ⚠ ★ **教训**：★ 我 B0 判"可做"时**只查了"有没有入口"** ✗ ⇒
    #:     ★★ **没查"覆盖表/已知事实里有没有它已经试死的记录"** ✓ ——
    #:     ★ 那正是 AGENTS.md 要求的**「先扫已走死的路」**（`docs/dead-ends.md` + `known-facts.md`）✓
    "剪裁曲面": ("曲面", "不做", "★★ **后端受限** —— ★ 依据**事实 419**：★「**照官方例子把前置完全对上**」"
                            "**而特征仍不建**（★ 案例之一就是**剔裁曲面**）✗ ⇒ ★ **不做** ✓ "
                            "★（★ **「取消剪裁」是另一半** —— ★ B2-1 已补包装、`untrim_surface` = `stitched` ✓）"),
    "成形工具": ("钣金", "可做", "★ `CreateFormTool2` / `InsertFormToolFeature` / `CreateFormTool`（**参数式、无 ACL**）"),
    "展开/折叠": ("钣金", "已覆盖", "★★ **由 `specs/209` 收口**：B2-1 `create_unfold` 与 B4-4 `create_fold` "
                                "**都已 `verified`**（真机建出 `展开1`/`折叠1`）⇒ ★ **核销，不重复建设** ✓"),
    "平板型式/导出 DXF": ("钣金", "可做", "★ `GetFlatPatternCount` / `GetFlatPatterns` / "
                                  "`CreateFlatPatternViewFromModelView3`（**无 ACL**）· ★ 与本仓既有 DXF 导出路径合流"),
    "裁剪/延伸焊件": ("焊件", "可做", "★ `InsertWeldmentTrimFeature2`（**参数式、无 ACL**）· 另 `InsertEndCapFeature` ✓"),
    "角撑板（焊件）": ("焊件", "可做", "★ `InsertGussetFeature3`（**参数式、无 ACL**）⇒ ★ **只走参数式**；"
                                "★ 属性式 `IGussetFeatureData` 有 `AccessSelections` ⇒ **那条不走**（事实 47）"),
    "圆角焊缝": ("焊件", "可做", "★ `InsertFilletBeadFeature3` / `InsertCosmeticWeldBead`（**参数式、无 ACL**）"),
    "焊接符号": ("焊件", "可做", "★ `InsertWeldSymbol3` / `InsertWeldSymbol2`（★ 无 ACL）· 读回用 `GetFirstWeldSymbol` ✓"),
    "爆炸直线": ("装配", "可做", "★ `IAssemblyDoc::InsertExplodeLineSketch()`（**零参数、无 ACL**）· "
                            "配套 `AddExplodeStep2` 族 ✓"),
    "零部件阵列": ("装配", "可做", "★★ **注意**：`swapi` 侧**只有 `DissolveComponentPattern`（解散）**、"
                            "**没有「创建」** ⇒ ★ 创建要走 `CreateDefinition` 类的 **5 个 `swFmLocal*Pattern` 常量** ✓"),
    "SpeedPak": ("装配", "可做", "★ `IAssemblyDoc::CreateSpeedPak(int, …)` · `SetSpeedPakConfigurations` · "
                            "`UpdateSpeedPak`（**参数式、无 ACL**）· 读回 `IsSpeedPak` ✓"),
    "序列 / 说明书（Assembly Visualization）": ("装配", "不做", "★ **四处零命中** ⇒ 官方无 API 入口（铁律 5）· "
                                                       "★ CHM 的 `Sequence` 只命中 **BOM 序号**与**族表序号**（与装配序列无关）"),
    "装配体性能分析": ("装配", "不做", "★ **四处零命中** ⇒ 官方无 API 入口（铁律 5）· "
                                "★ CHM 的 `Performance` 只命中枚举 `swPerformanceFeedback_e` / "
                                "`swSearchIndexingPerformance_e`（**不是分析功能**）"),
    "截面属性": ("评估", "可做", "★ `IModelDocExtension::GetSectionProperties2`（System.object 返回、**无 ACL**）✓"),
    "PDM": ("其他", "待实测", "★ 自动台账只有 1 个候选 ⇒ ★ **需真机确认本机有没有装 PDM**（★ 不装不改系统层）✓"),
}


def verdict_of(item: str):
    """★ 取某项的终判 `(域, 终判, 依据)`；★ 表里没有 ⇒ `None`（★ 不猜）✓"""
    return VERDICTS.get(item)
