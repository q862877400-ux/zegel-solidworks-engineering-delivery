"""★ 规格 211 · B0 的**人工终判表**（★ 每条注明依据；★ 只补空、不覆盖自动结果）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B0）
# 文件:   tools/spec211_manual_verdicts.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B0**。★ 自动台账（`tools/gen_spec2
#           11_ledger.py`）
# 只能给**信号**（★ `AccessSelections` 是**关键词共现**、★ 太粗）；★ 本表是**逐项人工读
# 官方页后**的**终判** ✓
# ★★ 依据**事实 53**：同一个启发式已连续改 **3 次** ⇒ ★ **停止调它**，改成「信号 + 人工
# 终判」✓
# 判据:   ★ 每条 VARCHAR 三选一：
#     `可做`   —— ★ `swapi` 侧有**参数式直接入口**，★ 且**不带 `AccessSelections`** ✓
# `不做`   —— ★ 带依据：① 四处零命中（官方无入口）· ② 入口要 `AccessSelections`（**事实
# 47**，★ 不试）✓
#     `待实测` —— ★ 需真机确认（如本机有没有装那个产品）✓
# ★★ 本表**只补空**：★ 自动结果里已经是"可做"的，本表**不推翻**（★ 一致才写，不一致要写
# `override` 并把理由写清）✓
# 官方依据: `C:\swapi\types\*\*.md` 的 `**Signature**` 行 +
#   `D:\AI\SW\AI Solidworks\官方文档\SWhelp\` 的 API 页名（★ 两者覆盖面不同，★ 都要查）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

#: ★★ **21 项人工终判** —— ★ 每条带 `依据`（★ 官方成员名 + 出处）✓
#: 结构：`项名: (域, 终判, 依据)`
VERDICTS = {
    "边界凸台": (
        "特征",
        "不做",
        "★ 入口 = `IBoundaryBossFeatureData`（CHM 有 `~AccessSelections`）⇒ "
        "属性式**要 ACL** ⇒ **事实 47**（后端限制）· ★ `AutoSelect` 或可绕开但**不试**",
    ),
    #: ★★★★★ 2026-10-07（B8 **第二次翻案被翻回来**）：★ 这条**原判「不做」其实是对的** ✗
    #:  ——
    #: ★★ 我 B8 曾把它改判「可做」，★ 依据是"参数式 `IFeatureManager::FeatureLocalCurveD
    #: rivenPattern`
    #:     存在且无 `AccessSelections`" ✗ ——
    #:   ★★★ **而那条例子里漏了一件事：★ 官方示例根本不用那个入口** ✓**
    #: ★★★★ **官方示例逐字**（★ `C:\swapi\examples\Create_and_Access_Curve-driven_Patter
    #: n_Feature_Example_VB.md`）：
    #: `Set swCurveDrivenPatternFeatureData = swFeatureMgr.CreateDefinition(swFmCurvePat
    #: tern)`
    #:       `Set swFeature = swFeatureMgr.CreateFeature(swCurveDrivenPatternFeatureData)`
    #:     ⇒ ★ **官方走的是**属性式**那条**（★ `CreateDefinition` + `CreateFeature` ✗）✓
    #:   ★★★ 而那条路的 Data 是 **`ICurveDrivenPatternFeatureData`** ⇒
    #: ★★ **逐文件核过：★ 它带 `AccessSelections`** ✗（`AccessSelections.md` + `IAccessS
    #: elections.md` 都在 ✓）
    #:   ⇒ ★★★ **事实 47 一挡就到不了建成** ✓
    #: ★★ 而★ **我 B8 调参数式那条的真机读数**是「★ **两档有效读数皆不建**」✗（第 0 / 1
    #: 档
    #:     `mark1=True · mark2=True · 选区=2` 而新增 `[]` ✓）⇒ ★★ **那条路真机也不通** ✓
    #:   ⇒ ★★★★★ **所以终判回到「不做（后端受限）」** ✓
    #:   ★★★ **两次翻案的教训是同一条**（★ 第一次是「焊接符号」）：
    #:     ★★★★ **「某个入口存在且无 ACL」≠「这个能力可做」** ✗ ——
    #:       ★★ **因为官方示例可能走**另一条**入口** ✓✓
    "曲线驱动阵列": (
        "特征",
        "不做",
        "★★★★ **后端受限** —— ★★ **官方示例逐字**（`Create_and_Access_"
        "Curve-driven_Pattern_Feature_Example_VB.md`）走的是 **`CreateDefinition"
        "(swFmCurvePattern)` + `CreateFeature`** ✗ ⇒ ★ 那条路的 Data "
        "**`ICurveDrivenPatternFeatureData` 带 `AccessSelections`** ✗（逐文件核过）"
        "⇒ **事实 47 一挡就到不了建成** ✓ ★★ 而参数式 `FeatureLocalCurveDrivenPattern` "
        "那条**真机两档有效读数皆不建** ⇒ ★ 一并记在此 ✓ "
        "★⚠ **本项经历过一次错误的翻案**：★ 我曾按「参数式存在且无 ACL」改判可做 ✗ —— "
        "★★ **漏了「官方示例不用那个入口」** ✓",
    ),
    "缩放/变形": (
        "特征",
        "可做",
        "★ `IFeatureManager::InsertScale(short Type, …)`（**参数式、无 ACL**）",
    ),
    "特征识别/Instant3D": (
        "特征",
        "不做",
        "★ **四处零命中** ⇒ 官方无 API 入口（铁律 5）· "
        "★ CHM 的 9 个 `Instant3D` 页是**用户手册**、★ 不在 API 命名空间",
    ),
    "扫描曲面": (
        "曲面",
        "可做",
        "★ `InsertSweepSurface2` / `InsertSweepSurface3`（**参数式、无 ACL**）",
    ),
    #: ★★★★★ 2026-10-07（B8 **实测纠正**）：★ 这条**原判「可做」是错的** ✗ ——
    #:   ★★ **我把「边界曲面」与「直纹曲面」混成一个了** ✗✓ —— 证据：
    #: ★ **覆盖表自己就分两行**：★「曲面 / **边界曲面** ❌」· ★「曲面 / **直纹曲面** ✅
    #: 」✓
    #:   ★★★ 而全扫 `C:\swapi\types`：★ **没有任何 `*BoundarySurface*` 的入口** ✗ ——
    #: 只有 `IFeatureManager::SetFreeformBoundaryContinuity`（★ **自由形**的边界连续性 ✗
    #: ）·
    #:     `IFillSurfaceFeatureData::*Boundary*`（★ **填充曲面**的边界 ✗）⇒ ★ **都不是它** ✓
    #:   ★★ 且 `docs/toolbar-ledger.md` **早就写着**：「边界曲面 | **待查**」✓
    #:   ⇒ ★★★ **判「查不到官方入口」**（★ **铁律 5**：★ 查不到就说查不到 ✓）
    #: ★★ 而**"直纹曲面"是另一件东西**、★ 仓里**已有**（★ `sw_surface_edit_ops.insert_ru
    #: led_surface`
    #:       走 `InsertRuledSurfaceFromEdge2` ✓）—— ★ 而它**不在本规格的 21 项里** ✓
    "边界曲面": (
        "曲面",
        "不做",
        "★★★ **查不到官方入口**（★ 铁律 5）—— ★ 全扫 `C:\\swapi\\types` 无 "
        "`*BoundarySurface*` 入口；★ 最接近的是 `SetFreeformBoundaryContinuity`"
        "（**自由形**边界连续性）与 `IFillSurfaceFeatureData::*Boundary*`（**填充曲面**边界）"
        "⇒ **都不是它** ✗ ★★ 且本仓 `docs/toolbar-ledger.md` 早就写着「边界曲面 | **待查**」✓ "
        "★⚠ **纠一处混淆**：★ 我原判把它当成了 `CreateRuledSurface`/`InsertRuledSurfaceFromEdge2` ✗ —— "
        "★ 那是**直纹曲面**（★ **仓里已有**、★ 且**不在本规格的项里** ✓）",
    ),
    #: ★★★★ 2026-10-07（B2 **实测纠正**）：★ 这条**原判「可做」是错的** ✗ ——
    #:   ★ 覆盖表**早就写着**：「`scripts/sw_surface.py` 有实现，但**三条入口真机全不成**
    #:   （**已知事实 417–419**）⇒ 工具面不计」✓
    #:   ★★ 依据 **事实 419**（★ 逐字）：「一类现象单列：**照官方例子把前置完全对上**」
    #:     **而特征仍不建** —— 两个案例（**剔裁曲面** + 投影型分割线）✓
    #:   ⇒ ★★★ **所以「剪裁曲面」= 不做（后端受限）**；★ 而**"取消剪裁"是另一半** ——
    #:     ★ 它在 B2-1 里**补了包装**、★ 负例有真机证据（★ `untrim_surface` = `stitched`）✓
    #:   ⚠ ★ **教训**：★ 我 B0 判"可做"时**只查了"有没有入口"** ✗ ⇒
    #:     ★★ **没查"覆盖表/已知事实里有没有它已经试死的记录"** ✓ ——
    #: ★ 那正是 AGENTS.md 要求的**「先扫已走死的路」**（`docs/dead-ends.md` + `known-fac
    #: ts.md`）✓
    "剪裁曲面": (
        "曲面",
        "不做",
        "★★ **后端受限** —— ★ 依据**事实 419**：★「**照官方例子把前置完全对上**」"
        "**而特征仍不建**（★ 案例之一就是**剔裁曲面**）✗ ⇒ ★ **不做** ✓ "
        "★（★ **「取消剪裁」是另一半** —— ★ B2-1 已补包装、`untrim_surface` = `stitched` ✓）",
    ),
    "成形工具": (
        "钣金",
        "可做",
        "★ `CreateFormTool2` / `InsertFormToolFeature` / `CreateFormTool`（**参数式、无 ACL**）",
    ),
    "展开/折叠": (
        "钣金",
        "已覆盖",
        "★★ **由 `specs/209` 收口**：B2-1 `create_unfold` 与 B4-4 `create_fold` "
        "**都已 `verified`**（真机建出 `展开1`/`折叠1`）⇒ ★ **核销，不重复建设** ✓",
    ),
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
    #: ★★ **所以它是**用户可决定**的**：★ 若用户允许「为导出而临时保存」⇒ **本项即可做**
    #:  ✓
    #: ★★★★★ 2026-10-07（收口后加做 · **用户授权解除封条**）：★ 用户原话「★ **D 我允许你
    #: 做**」✓
    #:   ⇒ ★★ 本项**从「不做」改判「可做」，并当场真机建成** ✓
    #:   ★★★ 判据**一正两负**（★ 事实 62：★ 门禁只靠负例证明 ✓）：
    #:     ★ 负例① 默认（`allow_temporary_save=False`）仍拒 ✓
    #:     ★★ 负例② 授权了、★ 而临时目录在**仓库外** ⇒ 拒、★ 且**拒绝发生在另存之前** ✓
    #:     ★★★ 正例 授权 + 仓库内目录 ⇒ 临时另存 + 导出 DXF，★ 回读 **20219 字节** ✓
    #: ★★★ **授权是**场景性的****（★ 「为导出而临时保存」）—— ★★ **不是全仓废止硬约束⑦**
    #:  ✓：
    #:     ★ `allow_temporary_save` **默认 `False`** ⇒ ★ 其它任何保存动作仍受原约束 ✓
    #:   ★★ 实现里**修过一版真 bug**：★ 仓库内判据第一版是**子串前缀** ✗ ⇒
    #:     `D:\AI\SW-evil\x` 会被判成"仓库内"通过 ✗ —— ★ 由那条「负例的负例」抓出 ✓
    #:   ★ 能力条目：`capabilities.yaml` 的 `flat_pattern_dxf`（★ `level: verified` ✓）
    "平板型式/导出 DXF": (
        "钣金",
        "可做",
        "★★★★★ **用户 2026-10-07 授权后真机建成**（★ 原话"
        "「★ **D 我允许你做**」✓）—— ★★ 实现：`scripts/sw_export.py` 的 "
        "`export_flat_pattern_dxf` 新增 `allow_temporary_save`（★ **默认 `False`** "
        "⇒ ★ 行为与从前**完全一致** ✓）与 `temporary_save_dir` ✓；"
        "★★★ 判据**一正两负**（`tests/test_spec211_flat_pattern_save.py` **4 passed** + "
        "`tools/probe_spec211_flatsave.py`）⇒ ★ 回读 DXF **20219 字节** ✓ "
        "★★ 授权是**场景性的**、★ **不是**全仓废止硬约束⑦ ✓",
    ),
    "裁剪/延伸焊件": (
        "焊件",
        "可做",
        "★ `InsertWeldmentTrimFeature2`（**参数式、无 ACL**）· 另 `InsertEndCapFeature` ✓",
    ),
    "角撑板（焊件）": (
        "焊件",
        "可做",
        "★ `InsertGussetFeature3`（**参数式、无 ACL**）⇒ ★ **只走参数式**；"
        "★ 属性式 `IGussetFeatureData` 有 `AccessSelections` ⇒ **那条不走**（事实 47）",
    ),
    "圆角焊缝": (
        "焊件",
        "可做",
        "★ `InsertFilletBeadFeature3` / `InsertCosmeticWeldBead`（**参数式、无 ACL**）",
    ),
    "焊接符号": (
        "焊件",
        "可做",
        "★ `InsertWeldSymbol3` / `InsertWeldSymbol2`（★ 无 ACL）· 读回用 `GetFirstWeldSymbol` ✓",
    ),
    "爆炸直线": (
        "装配",
        "可做",
        "★ `IAssemblyDoc::InsertExplodeLineSketch()`（**零参数、无 ACL**）· "
        "配套 `AddExplodeStep2` 族 ✓",
    ),
    #: ★★★★★ 2026-10-07（B8 **第二次翻案被翻回来**）：★ 这条**原判「不做」其实是对的** ✗
    #:  ——
    #: ★★ 我 B8 曾改判「可做」（★ 依据是"参数式 `FeatureLocalCurveDrivenPattern` 无 ACL"
    #: ）✗ ——
    #:   ★★★ **而官方示例根本不用那个入口** ✓**
    #: ★★★★ **官方示例逐字**（★ `C:\swapi\examples\Create_Local_Curve-driven_Pattern_Exa
    #: mple_CSharp.md`）：
    #: `swLocalCurvePatternFeat = (LocalCurvePatternFeatureData)swFeatMgr.CreateDefiniti
    #: on(`
    #:       `    (int)swFeatureNameID_e.swFmLocalCurvePattern);`
    #:       `swFeat = (Feature)swFeatMgr.CreateFeature(swLocalCurvePatternFeat);`
    #: ★ 且它的 `Postconditions` 逐字：★ 「**Selects the component and edge** for the lo
    #: cal
    #:       curve-driven pattern feature.」✓ ⇒ ★★ **那是**装配**语境（component + edge）** ✓
    #:   ★★★ 而那条路的 Data 是 **`ILocalCurvePatternFeatureData`** ⇒
    #:     ★★ **逐文件核过：★ 它带 `AccessSelections`** ✗（`AccessSelections.md` ✓）
    #:   ⇒ ★★★ **事实 47 一挡就到不了建成** ✓
    #: ★★ 而★ 参数式那条**与「曲线驱动阵列」同一个入口、★ 同一批真机读数**（★ 两档有效皆
    #: 不建 ✗）✓
    #:   ⇒ ★★★★★ **所以终判回到「不做（后端受限）」** ✓
    #: ★★ **旁证留档**：★ `ILocalSketchPatternFeatureData` **也带 `AccessSelections`** ✗
    #:  ——
    #:     ★ 即**这一族（`swFmLocal*Pattern`）的 Data 全都带** ✗✓
    "零部件阵列": (
        "装配",
        "不做",
        "★★★★ **后端受限** —— ★★ **官方示例逐字**（`Create_Local_Curve-driven_"
        "Pattern_Example_CSharp.md`）走的是 **`CreateDefinition(swFmLocalCurvePattern)` + "
        "`CreateFeature`** ✗，★ 且其 `Postconditions` 逐字「**Selects the component and edge**」"
        "⇒ **装配语境** ✓ ⇒ ★ 那条路的 Data **`ILocalCurvePatternFeatureData` 带 "
        "`AccessSelections`** ✗（逐文件核过）⇒ **事实 47 一挡就到不了建成** ✓ "
        "★ 旁证：★ **同族的 `ILocalSketchPatternFeatureData` 也带** ✗ —— ★ 即这一族的 Data 全都带 ✓ "
        "★⚠ **本项与「曲线驱动阵列」同时经历过一次错误的翻案** ✓",
    ),
    "SpeedPak": (
        "装配",
        "可做",
        "★ `IAssemblyDoc::CreateSpeedPak(int, …)` · `SetSpeedPakConfigurations` · "
        "`UpdateSpeedPak`（**参数式、无 ACL**）· 读回 `IsSpeedPak` ✓",
    ),
    "序列 / 说明书（Assembly Visualization）": (
        "装配",
        "不做",
        "★ **四处零命中** ⇒ 官方无 API 入口（铁律 5）· "
        "★ CHM 的 `Sequence` 只命中 **BOM 序号**与**族表序号**（与装配序列无关）",
    ),
    "装配体性能分析": (
        "装配",
        "不做",
        "★ **四处零命中** ⇒ 官方无 API 入口（铁律 5）· "
        "★ CHM 的 `Performance` 只命中枚举 `swPerformanceFeedback_e` / "
        "`swSearchIndexingPerformance_e`（**不是分析功能**）",
    ),
    "截面属性": (
        "评估",
        "可做",
        "★ `IModelDocExtension::GetSectionProperties2`（System.object 返回、**无 ACL**）✓",
    ),
    "PDM": (
        "其他",
        "不做",
        "★ 自动台账只有 1 个候选 ⇒ ★ **需真机确认本机有没有装 PDM**（★ 不装不改系统层）✓",
    ),
}


def verdict_of(item: str):
    """★ 取某项的终判 `(域, 终判, 依据)`；★ 表里没有 ⇒ `None`（★ 不猜）✓"""
    return VERDICTS.get(item)
