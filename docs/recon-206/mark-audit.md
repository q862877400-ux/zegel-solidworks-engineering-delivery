# mark_diff 冲突的机械判读：我们的调用点用没用「能带 mark 的选择 API」

> 生成物 —— 由 `tools/t4_mark_audit.py` 产出，不要手改。
> 输入：`c4-merged.json`（只读）+ 本仓 `scripts/` `mcp-server/` `tools/`。

## 一 · 口径（★ 先说判据，再说数）

| 项 | 值 |
|---|---|
| `mark_diff` 冲突 | **10** 条 |
| 涉及成员 | **8** 个 |
| ★ 判据 | 真调用点（`ast` 判）前后 **12 行**内：有 `mark=` / `SelectByID2(` / `_select_by_id(` ⇒ **带 mark**；**只有** `Select4(` ⇒ **不带 mark**（★ `Select4` 没有 mark 形参，已知事实 32）|

★★ **本表「不算什么」**（★ 缺了它这张表会被误用）：

- ★ **不等于**「我们写错了」—— 它只说**我们的调用点带不带 mark**；
  ★ 官方那一侧的 `mark_diff` 是 **Remarks 与示例互相矛盾** ⇒ ★★ **两类各自都可能对**，
  ★ 结论要**逐条读官方页**才能下（★ 本表只给机械事实）；
- ★ **窗口 12 行**是启发式 ⇒ ★ 调用点离选择很远时会误判（★ 标 `unknown`）；
- ★ 只覆盖**我们真调用过**的成员 —— ★ 没调用的不在表里 ✓

## 二 · 逐成员

### `AutoDimension2`（1 条冲突）

- ★ `Remarks`：Select and mark a unique vertical edge, vertex, sketch point, or vertical sketch line as the datum for the horizontal dimensioning scheme, using swAutodimMarkHorizontalDatum as the mark value.
- ★ 示例：`bRet = swSketchSegVert.Select4(True, Nothing)`

- 调用点 `scripts\sw_part.py:805` ⇒ ★ 窗口内看不出选择 API ⇒ unknown
- 调用点 `tools\probe_fullydefinesketch.py:71` ⇒ ★ 窗口内看不出选择 API ⇒ unknown

### `EditMate3`（1 条冲突）

- ★ `Remarks`：The two mated items must be selected with a selection mark of 1.
- ★ 示例：`        '   IAssemblyDoc::EditMate3 requires that mate entities
        '   be selected with mark of 1 except for:
        '       swMateCAMFOLLOWER
        '  `

★ **我们没真调用过** ⇒ 这条冲突对我们当前无直接影响 ✓

### `FeatureExtruRefSurface2`（2 条冲突）

- ★ `Remarks`：Sketch; call [[IModelDocExtension::SelectByID2]] with selection mark 0.
- ★ 示例：`boolstatus = swModelDocExt.SelectByID2("Sketch1", "SKETCH", 0, 0, 0, false, 4, null, 0);`
- ★ `Remarks`：Sketch; call [[IModelDocExtension::SelectByID2]] with selection mark 0.
- ★ 示例：`status = swModelDocExt.SelectByID2("Sketch1", "SKETCH", 0, 0, 0, false, 4, null, 0);`

★ **我们没真调用过** ⇒ 这条冲突对我们当前无直接影响 ✓

### `FeatureLinearPattern4`（1 条冲突）

- ★ `Remarks`：- 8388608 to mark a seed instance reference when FromCentroid1 or FromCentroid2 is false
- ★ 示例：`status = swModelDocExt.SelectByID2("Boss-Extrude2", "SOLIDBODY", 0, 0, 0, True, 256, Nothing, 0)`

- 调用点 `tools\probe_linear_pattern_baseline.py:115` ⇒ ★ 窗口内看不出选择 API ⇒ unknown
- 调用点 `tools\prove_linear_pattern_generations.py:94` ⇒ ★ 窗口内有带 mark 的选择

### `InsertCutSwept5`（2 条冲突）

- ★ `Remarks`：- 1 = Sketch profile or tool body
- ★ 示例：`status = swModelDocExt.SelectByID2("", "EDGE", -0.0372983839416747, 0.0393904284381961, 0.0495042874504179, true, 4, null, 0);`
- ★ `Remarks`：- 2 = Guide curve, if provided

- 4 = Sweep path
- ★ 示例：`status = swModelDocExt.SelectByID2("Boss-Extrude1", "SOLIDBODY", 0, 0, 0, true, 2048, null, 0);`

★ **我们没真调用过** ⇒ 这条冲突对我们当前无直接影响 ✓

### `InsertMoveCopyBody2`（1 条冲突）

- ★ `Remarks`：Rotation edge, vertex, coordinate system

2
- ★ 示例：`status = swModelDocExt.SelectByID2("", "VERTEX", -0.085, 0, 0.065, True, 4, Nothing, 0)
status = swModelDocExt.SelectByID2("", "VERTEX", -0.085, -0.09, 0.065, T`

★ **我们没真调用过** ⇒ 这条冲突对我们当前无直接影响 ✓

### `InsertProtrusionBlend2`（1 条冲突）

- ★ `Remarks`：- 2 = guide curve selections
- ★ 示例：`status = swModelDocExt.SelectByID2("Sketch3", "SKETCH", 0, 0, 0, true, 4098, null, 0);`

- 调用点 `scripts\sw_loft.py:87` ⇒ ★ 窗口内有带 mark 的选择

### `InsertWeldmentTrimFeature2`（1 条冲突）

- ★ `Remarks`：- 1 = Body or bodies to trim

- 2 = Trimming boundaries (body or face)
- ★ 示例：`= Part.Extension.SelectByID2("Structural Member1[2]", "SOLIDBODY",
0, 0, 0, true, 2, null, 0);
boolstatus
= Part.Extension.SelectByID2("Structural Member1[1]", `

- 调用点 `tools\probe_t302_four_families_v2.py:190` ⇒ ★ 窗口内看不出选择 API ⇒ unknown

## 三 · ★ 下一步（★ 仍需人读官方页的那部分）

★ 对每条：读该成员的官方 `## Remarks` ⇒ 判「它要求的 mark 是不是**必须**的」；
★ 若必须、而我们窗口内没有 ⇒ ★ **这才是真缺陷**（★ 且要找真机证据才改）✓

