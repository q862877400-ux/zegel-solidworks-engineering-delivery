# 规格 211 · B0-4 负例条件（★ 必须「必然失败」，且**有官方依据**）

> ★★ 本仓教训：**假负例等于没有** —— 负例必须用**必然失败**的条件。
> ★ 历史实录：`extend_surface` 的负例原设计是"**不选面**应失败"，★ 而真机推翻了这个假设
> （**不显式选面它也会自己找到面并成功**）⇒ ★ 负例改成 **`distance_mm ≤ 0`** ✓
> ⇒ ★★ 故本表的每一条**都要有官方 `## Remarks` 的依据**，★ 不许凭印象写 ✓

★ **覆盖范围**：本表先做 **B1 + B2 的 5 项**；★ 其余项在**各自批次**里做（★ 避免"15 条凭印象写的负例"）✓

---

## B1-1 · 截面属性 — `IModelDocExtension::GetSectionProperties2(Sections)`

- ★ **官方依据（逐字）**：「The objects in the `Sections` parameter **are added to the current selection set**.
  If the objects are already in the current selection set…」
- ★★ **两个结论**：
  1. ★ **负例**：`Sections` 传 **空数组** ⇒ ★ 没有可算的截面 ⇒ **必然失败** ✓
  2. ★★★ **它是"读操作但有选择副作用"** ⇒ ★ 按**规格 210** 的效应声明体系，
     ★★ **它不该被标 `read_only`** ⇒ ★ 本批要用**指纹差分**验证（★ 调它前后 `selection` 会不会变）✓
- ★ 回读判据：★ 返回的**截面属性数组**（面积/惯性矩/形心）+ ★★ **`selection` 计数**（★ 副作用的证据）

## B1-2 · 缩放/变形 — `IFeatureManager::InsertScale(Type, Uniform, XScale, YScale, ZScale)`

- ★ **官方依据（逐字）**：「`YScale`: Y direction scale factor; **valid only if `Uniform` is false**」
  （同理 `ZScale`）
- ★ **负例（两项，都要试）**：
  1. ★ **`XScale = 0`** ⇒ ★ 零倍缩放 ⇒ 特征无意义 ⇒ **必然失败** ✓
  2. ★ **`Type` 取值不在 `swScaleType_e` 内**（如 `999`）⇒ **必然失败** ✓
- ★ 回读判据：★ 特征树 `+1`（出现"缩放"特征）+ ★ **体积/包围盒按比例变化**（★ 回读，不看返回值）

## B2-1 · 剪裁曲面（取消剪裁）— `IFeatureManager::InsertUntrimSurface2(...)`

- ★★ **官方依据（逐字）**：「**is valid only for surface parts**」
- ★★ **负例**：★ **在"普通零件"（非曲面零件）上调** ⇒ **必然失败** ✓
  ★（★ 这条依据**最硬**：官方把"只对曲面零件有效"写成了前置）
- ★ 附带负例：★ `FaceUntrimType` 不在 `swFaceUntrimType_e` 内 ⇒ 必然失败 ✓
- ★ 回读判据：★ 面数变化 / 曲面体数变化（★ 回读）

## B2-2 · 扫描曲面 — `IFeatureManager::InsertSweepSurface2(Propagate, TwistCtrlOption, …)`

- ★ **官方依据（逐字）**：「When `UseAutoSelect` is **false**, the user **must select the bodies**
  that the feature will affect.」
- ★★ **负例**：★ **`UseAutoSelect = false` 且不选任何体** ⇒ **必然失败** ✓
  ★（★ 对照正例：`UseAutoSelect = true` ⇒ 应成功 ⇒ ★ 这一对是**最干净的负例/正例对照**）✓
- ★ 记忆补充：★ 本仓记录里「**从没查过 `InsertSweepSurface2`**」⇒ ★ 本批是**第一次读它** ✓
- ★ 回读判据：★ 曲面体数 / 特征树（★ 回读）

## B2-3 · ~~边界曲面~~ ⇒ ★★★ **改为「查不到官方入口」（★ 本段作废）**

> ★★★★★ **2026-10-07（B8 实测纠正）：本段原先写的负例是**建立在一个混淆上的** ✗** ——
> ★ 我原把「**边界曲面**」当成 `IModeler::CreateRuledSurface(Curve1In, Curve2In, Apex)` ✗ ——
> ★★ **而那是「直纹曲面」**（★ **另一件东西** ✓ —— ★ 覆盖表自己就分两行：
> 「曲面 / **边界曲面** ❌」·「曲面 / **直纹曲面** ✅」✓）。
> ★★★ **实测**：★ 全扫 `C:\swapi\types` **没有任何 `*BoundarySurface*` 入口** ✗ ——
> 最接近的两个都不是它：★ `IFeatureManager::SetFreeformBoundaryContinuity`（**自由形**边界连续性）·
> ★ `IFillSurfaceFeatureData::*Boundary*`（**填充曲面**的边界）✓
> ★★ 且 `docs/toolbar-ledger.md` **早就写着**「边界曲面 | **待查**」✓
> ⇒ ★★★ **故「边界曲面」判「查不到官方入口」（铁律 5）**，★ **本段的负例设计随之作废** ✓
> ★★ **保留本段**（而不是删掉）★ 是为了留下**这次混淆的实物** ——
> ★ 它与 `tools/spec211_manual_verdicts.py` 里那条纠正**互相印证** ✓

### ★ 原（**作废**）内容，仅作混淆的实物保留

- ★ 原写：「**官方依据**：`IModeler::CreateRuledSurface` 的 `## Remarks` 逐字「**Valid input curves are
  b-curves**」⇒ 负例：传非 b-curve」✗
- ★★ **那条依据本身是对的** ✓（`CreateRuledSurface` 确实要求 b-curves ✓）——
  ★ **只是它属于「直纹曲面」、不属于「边界曲面」** ✗✓

- ★★ **官方依据（逐字）**：「**Valid input curves are b-curves**.」
- ★★ **负例**：★ **传非 b-curve**（例如一条草图直线段 `ISketchSegment`、或一条实体边）⇒ **必然失败** ✓
  ★（★ 官方把输入类型写死了 ⇒ ★ 这是**类型级**的必然失败，★ 比"数值越界"更硬）✓
- ★ 回读判据：★ 曲面体数 +1（★ 回读）· ★ 返回对象**不是 `None`** ⇒ ★★ 但仍要**回读**确认建出来了
  （★ 本仓教训：`IModeler.Create*Surface` 的**返回值跨次不稳定**，★ 事实 40）✓

---

## ★ 三条**贯穿本规格**的负例纪律

1. ★★ **不许用"不选东西"当负例** —— ★ 历史实录：★ `extend_surface` 不选面**也会成功** ✗
   （★ 除非**官方 Remarks 明写**"must select"，★ 如 `InsertSweepSurface2` 的 `UseAutoSelect=false`）✓
2. ★★ **负面清单优先用"官方写死的约束"**：★ 文档类型（`only for surface parts`）·
   ★ 输入类型（`Valid input curves are b-curves`）· ★ 参数联动（`valid only if Uniform is false`）✓
3. ★★ **判据一律回读**：★ 特征树 / 体数 / 面数 / 包围盒 / 体积 —— ★ **不看返回值**（★ 铁律 2 + 事实 8）✓
