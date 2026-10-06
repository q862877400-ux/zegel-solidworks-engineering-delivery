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
    #: ★★★★★ 2026-10-07（B8 **翻案**）：★ 这条**原判「不做」也错了** ✗ ——
    #:   ★★ 我 B5 的链条里**漏了一个入口**：★★ **`IFeatureManager::FeatureLocalCurveDrivenPattern`** ✓
    #:     ★★★ 官方签名（★ 逐字读过）：**纯参数式 13 参、不带 `AccessSelections`** ✓✓
    #:       `Feature FeatureLocalCurveDrivenPattern(bool FlipDir1, int Num1, bool EqualSpacing1,
    #:        double Spacing1, int ReferencePoint, int CurveMethod, int AlignMethod, bool Direction2,
    #:        bool FlipDir2, int Num2, bool EqualSpacing2, double Spacing2, bool PatternSeedOnly)` ✓
    #:   ★★ 名字里的 **`CurveDriven`** 就是它 —— ★ **它才是「曲线驱动阵列」的直接入口** ✓
    #:   ★★★ 我原链条的两条**都只说了别的入口**：★ ① `IModelDoc2::FeatureCurvePattern`（**已 Obsolete**）✗
    #:     ② `CreateFeature` + `ICurveDrivenPatternFeatureData`（**要 ACL**）✗ ⇒ ★ **两条都不覆盖本条** ✓
    #:   ★★ 而 `## Parameters` 里 `ReferencePoint` 写着「Type of **selected** reference point」✗ ⇒
    #:     ★★ **它可能要预选一个参考点**（★ 那正是下一步真机要验的 ✓）
    #:   ★★★ **且本项与「零部件阵列」共用这个入口** —— ★ 覆盖表把它们分在**特征域 / 装配域**两行，
    #:     ★★ 而**官方入口是同一个** ⇒ ★ **两项同判「可做」** ✓（★ 同一份证据同时定两项 ✓）
    #:   ★★ **教训**：★ **「某个入口要 ACL」≠「这个能力要 ACL」** ✗ ——
    #:     ★ 判「不做」之前要把**同族的入口全列一遍** ✓
    "曲线驱动阵列": ("特征", "可做", "★★★ **参数式入口存在且无 ACL** —— ★★ `IFeatureManager::FeatureLocalCurveDrivenPattern`"
                             "（★ **13 参、不带 `AccessSelections`** ✓，★ 名字里的 `CurveDriven` 就是它 ✓）；"
                             "★★ 我原判「不做」**只看了另两个入口**（★ `IModelDoc2::FeatureCurvePattern` **已 Obsolete** ✗ · "
                             "★ `CreateFeature` + `ICurveDrivenPatternFeatureData` **要 ACL** ✗）⇒ **不覆盖本条** ✓ "
                             "★ 待验：★ `ReferencePoint` 官方写「Type of **selected** reference point」⇒ **可能要先选参考点** ✓"),
    "缩放/变形": ("特征", "可做", "★ `IFeatureManager::InsertScale(short Type, …)`（**参数式、无 ACL**）"),
    "特征识别/Instant3D": ("特征", "不做", "★ **四处零命中** ⇒ 官方无 API 入口（铁律 5）· "
                                   "★ CHM 的 9 个 `Instant3D` 页是**用户手册**、★ 不在 API 命名空间"),
    "扫描曲面": ("曲面", "可做", "★ `InsertSweepSurface2` / `InsertSweepSurface3`（**参数式、无 ACL**）"),
    #: ★★★★★ 2026-10-07（B8 **实测纠正**）：★ 这条**原判「可做」是错的** ✗ ——
    #:   ★★ **我把「边界曲面」与「直纹曲面」混成一个了** ✗✓ —— 证据：
    #:     ★ **覆盖表自己就分两行**：★「曲面 / **边界曲面** ❌」· ★「曲面 / **直纹曲面** ✅」✓
    #:   ★★★ 而全扫 `C:\swapi\types`：★ **没有任何 `*BoundarySurface*` 的入口** ✗ ——
    #:     只有 `IFeatureManager::SetFreeformBoundaryContinuity`（★ **自由形**的边界连续性 ✗）·
    #:     `IFillSurfaceFeatureData::*Boundary*`（★ **填充曲面**的边界 ✗）⇒ ★ **都不是它** ✓
    #:   ★★ 且 `docs/toolbar-ledger.md` **早就写着**：「边界曲面 | **待查**」✓
    #:   ⇒ ★★★ **判「查不到官方入口」**（★ **铁律 5**：★ 查不到就说查不到 ✓）
    #:     ★★ 而**"直纹曲面"是另一件东西**、★ 仓里**已有**（★ `sw_surface_edit_ops.insert_ruled_surface`
    #:       走 `InsertRuledSurfaceFromEdge2` ✓）—— ★ 而它**不在本规格的 21 项里** ✓
    "边界曲面": ("曲面", "不做", "★★★ **查不到官方入口**（★ 铁律 5）—— ★ 全扫 `C:\\swapi\\types` 无 "
                            "`*BoundarySurface*` 入口；★ 最接近的是 `SetFreeformBoundaryContinuity`"
                            "（**自由形**边界连续性）与 `IFillSurfaceFeatureData::*Boundary*`（**填充曲面**边界）"
                            "⇒ **都不是它** ✗ ★★ 且本仓 `docs/toolbar-ledger.md` 早就写着「边界曲面 | **待查**」✓ "
                            "★⚠ **纠一处混淆**：★ 我原判把它当成了 `CreateRuledSurface`/`InsertRuledSurfaceFromEdge2` ✗ —— "
                            "★ 那是**直纹曲面**（★ **仓里已有**、★ 且**不在本规格的项里** ✓）"),
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
    #: ★★★★★ 2026-10-07（B8 **实测纠正 + 查到理由**）：
    #:   ★★ **实现早就有**：`scripts/sw_export.py` 的 `export_flat_pattern_dxf` /
    #:     `export_flat_pattern_dxf_report`（★ 走 `ExportToDWG2` ✓）✓
    #:   ★★★ **而理由查到了**（★ `docs/plan-24h-v2-convergence.md` 第 53 行**逐字**）：
    #:     「★★ **轮 407 真的造了一个钣金件**（回读三项全 true）而它**仍拒绝** ——
    #:      真前置是「**已保存**的钣金件」，★ 而**保存是硬约束⑦ 明禁**的 ⇒ …」✓✓
    #:   ★★ 同型旁证：`docs/A9-solve-attempts.md:84`「所有脚本都**不保存**文档
    #:     （`CloseDoc` 前未 `SaveAs`）」✓
    #:   ⇒ ★★★★ **故终判 = 不做**，★ 而**理由是**新的一类**：
    #:     ★★ **「官方前置要求保存文档、而本仓硬约束不许保存」** ✗ ——
    #:     ★ 这与「剪裁曲面」（★ 事实 419：**前置全对上仍不建**）**不同族** ✗：
    #:       ★ 那是「能力到不了」✗、★ **本项是「能力可达、★ 而与本仓纪律冲突」** ✓
    #:   ★★ **所以它是**用户可决定**的**：★ 若用户允许「为导出而临时保存」⇒ **本项即可做** ✓
    "平板型式/导出 DXF": ("钣金", "不做", "★★★ **被本仓硬约束挡住**（★ 而**实现早就有** ✓）—— "
                                    "★ `scripts/sw_export.py` 的 `export_flat_pattern_dxf`/"
                                    "`export_flat_pattern_dxf_report`（★ 走 `ExportToDWG2` ✓）✓；"
                                    "★★ 理由**逐字**见 `docs/plan-24h-v2-convergence.md:53`："
                                    "「★ **轮 407 真的造了一个钣金件**（回读三项全 true）而它**仍拒绝** —— "
                                    "真前置是「**已保存**的钣金件」，★ 而**保存是硬约束⑦ 明禁**的」✗ "
                                    "★ 旁证 `docs/A9-solve-attempts.md:84`「所有脚本都**不保存**文档」✓ "
                                    "⇒ ★★ **「官方前置要求保存、本仓不许保存」** —— ★ 与「剪裁曲面」"
                                    "（前置全对上仍不建）**不同族** ✗；★ **若用户允许为导出而临时保存 ⇒ 本项即可做** ✓"),
    "裁剪/延伸焊件": ("焊件", "可做", "★ `InsertWeldmentTrimFeature2`（**参数式、无 ACL**）· 另 `InsertEndCapFeature` ✓"),
    "角撑板（焊件）": ("焊件", "可做", "★ `InsertGussetFeature3`（**参数式、无 ACL**）⇒ ★ **只走参数式**；"
                                "★ 属性式 `IGussetFeatureData` 有 `AccessSelections` ⇒ **那条不走**（事实 47）"),
    "圆角焊缝": ("焊件", "可做", "★ `InsertFilletBeadFeature3` / `InsertCosmeticWeldBead`（**参数式、无 ACL**）"),
    "焊接符号": ("焊件", "可做", "★ `InsertWeldSymbol3` / `InsertWeldSymbol2`（★ 无 ACL）· 读回用 `GetFirstWeldSymbol` ✓"),
    "爆炸直线": ("装配", "可做", "★ `IAssemblyDoc::InsertExplodeLineSketch()`（**零参数、无 ACL**）· "
                            "配套 `AddExplodeStep2` 族 ✓"),
    #: ★★★★★ 2026-10-07（B8 **翻案**）：★ 本条原写「创建要走 `CreateDefinition` 类的 5 个 `swFmLocal*Pattern` 常量」✗
    #:   —— ★★ **那是**属性式**那条路**（★ `swFmLocal*Pattern` ⇒ `CreateFeature` + `ICurveDrivenPatternFeatureData`，
    #:   而那个 Data **带 `AccessSelections`** ✗ ⇒ **事实 47 一挡就到不了建成** ✓）
    #:   ★★★ **而参数式入口是存在的**：★★ **`IFeatureManager::FeatureLocalCurveDrivenPattern`** ✓
    #:     ★ 官方签名**逐字**：**13 参、不带 `AccessSelections`** ✓✓（★ 见同文件「曲线驱动阵列」那段 ✓）
    #:   ★★★ **所以本条与「曲线驱动阵列」**共用同一个入口**** ✓ —— ★ 覆盖表把它们分在**装配域 / 特征域**两行，
    #:     ★★ 而**官方入口是同一个** ⇒ ★ **两项同判「可做」** ✓（★ 同一份证据同时定两项 ✓）
    #:   ★★ 旁证：★ `*LocalPattern*` **全扫为空** ✗（★ 即那张「5 个 `swFmLocal*Pattern`」的说法**查不到落实** ✓）
    "零部件阵列": ("装配", "可做", "★★★ **与「曲线驱动阵列」共用参数式入口** —— ★★ "
                             "`IFeatureManager::FeatureLocalCurveDrivenPattern`（★ **13 参、不带 `AccessSelections`** ✓）；"
                             "★★ 原写「创建要走 `CreateDefinition` 类的 5 个 `swFmLocal*Pattern` 常量」✗ —— "
                             "★ 那条是**属性式**路（★ 其 Data **带 `AccessSelections`** ✗ ⇒ **事实 47 挡死** ✓）；"
                             "★ 旁证：★ `*LocalPattern*` 全扫为空 ✗（★ 那「5 个常量」的说法**查不到落实** ✓）"
                             "★ 待验：★ 与「曲线驱动阵列」**同一批真机**验（★ 一次验两项 ✓）"),
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
