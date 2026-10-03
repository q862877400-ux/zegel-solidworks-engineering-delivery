# audit-07 · 域 07-sketch · 核对 C（废弃链与枚举取值）

**核对员**：逐条核对（只读）· **日期**：2026-10-03
**范围（两框交集）**：域 `07-sketch` ∩ 核对 `C`
**我这边读的文件**：`scripts/sw_sketch.py` · `scripts/sw_sketch_edit.py` · `scripts/sw_sketch_modify_ops.py` · `scripts/sw_sketch_edit_ops.py`（四个都在，无需 glob 兜底）
**官方源**：`C:\swapi\types\` · `C:\swapi\enums\` · `C:\swapi\examples\`
**做法**：只报「两段原文对不上」的条目；给不出两段可搜索原文的一律不写；不判谁对，不给建议。

| # | 我们的原文（文件 + 片段） | 官方的原文（文件 + 片段） | 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | `scripts/sw_sketch_modify_ops.py` · `_active_sketch_name()`：`sk = get_com_member(model, "GetActiveSketch2")`（**该函数只走这一条路，没有 `SketchManager.ActiveSketch` 回退**） | `C:\swapi\types\IModelDoc2\GetActiveSketch2.md`：`Obsolete. Superseded by [[SketchManager::ActiveSketch]].` | 我们调的 `GetActiveSketch2` 官方已标 **Obsolete**；官方点名的后继是 `SketchManager::ActiveSketch`，而这一处**只调了 Obsolete 那个** | 高 |
| 2 | `scripts/sw_sketch_edit.py` · `create_sketch_chamfer._seg_count()`：`sk = get_com_member(model, "GetActiveSketch2")` / 下一行 `sk = get_com_member(get_com_member(model, "SketchManager"), "ActiveSketch")` | `C:\swapi\types\IModelDoc2\GetActiveSketch2.md`：`Obsolete. Superseded by [[SketchManager::ActiveSketch]].` | 同一官方页：`GetActiveSketch2` 是 Obsolete；我们是**先调 Obsolete、再回退后继**（回退有，后继不在首位） | 高 |
| 3 | `scripts/sw_sketch_modify_ops.py` · `sketch_flip()`：`⚠ AxisFlag 的**取值表官方两个源都没给** ⇒ ★ 按铁律 5 **原样透传 int，不猜语义**`；返回里 `"axis_flag_semantics": "官方 swapi 与 CHM 均未给取值表 —— 原样透传"` | `C:\swapi\types\IModelDoc2\SketchModifyFlip.md`：`- **AxisFlag**: Axis about which to flip the sketch:` ／ `  - X = 1` ／ `  - Y = 2` | 我们写「官方两个源都没给取值表」；官方 swapi 页**给了取值表**（X = 1、Y = 2），故那段"原样透传不猜"的依据与原文不符 | 高 |
| 4 | `scripts/sw_sketch_edit.py` · `SKETCH_CHAMFER_TYPE`：`"distance_distance": 1,     # swSketchChamfer_DistanceDistance（⚠ md 写 -1，反射写 1，采用 1）`（该值经 `int(chamfer_type)` 传给 `ISketchManager.CreateChamfer` 的 `Type`） | `C:\swapi\enums\swSketchChamferType_e.md`：成员表 `\| swSketchChamfer_DistanceAngle \| 0 \|`、`\| swSketchChamfer_DistanceDistance \| -1 \|`、`\| swSketchChamfer_DistanceEqual \| 2 \|`（`enum_member_count: 3`） | 作为枚举字面量传的 `1` 在官方枚举页里**不是任何成员的值**（该成员官方为 `-1`）。★ 两源不一致（swapi 写 -1、出厂反射写 1，我们按铁律 4 采用反射）—— **不判谁对** | 高 |
| 5 | `scripts/sw_sketch.py` · `SKETCH_CROSS_HATCH` 上方注释：`#: ⚠ swapi 只列了其中 3 个（`Include/Exclude/AndExplodeOnly`），**值相同**，无冲突。` ＋ `#: 反射里还有 `swCrossHatchOnly = 2` · `swSolidHatchOnly = 4`。` | `C:\swapi\enums\swCrossHatchFilter_e.md`：`enum_member_count: 5`，成员表含 `\| swCrossHatchAndExplodeOnly \| 3 \|`、`\| swCrossHatchExclude \| 1 \|`、`\| swCrossHatchInclude \| 0 \|`、`\| swCrossHatchOnly \| 2 \|`、`\| swSolidHatchOnly \| 4 \|` | 我们称"swapi 只列了 3 个、另两个仅见于出厂反射"；官方 swapi 枚举页**本身列全了 5 个**，且 `swCrossHatchOnly=2` / `swSolidHatchOnly=4` 两值与反射相同（表中 5 个值与我们 `SKETCH_CROSS_HATCH` 的 0/1/2/3/4 全部一致） | 高 |

---

**核过的、确认「无分歧」的地方（不计入上表，只记账）**：`swSketchTrimChoice_e`（7 值与 `TRIM_CHOICES` 全对）、`swSkOffsetCapEndType_e`（3 值全对）、`swSkOffsetMakeConstructionType_e`（4 值全对）、`swConstrainedCornerAction_e`（`CreateFillet.ConstrainedCorners` 默认 `0` = `swConstrainedCornerInteract`，是合法成员）、`SketchMirror` 的 mark 1/2、`swCrossHatchFilter_e` 的实际取值。

**域外一条（不计入本表与计数，仅备查）**：`scripts/sw_sketch.py` 三处写「官方文档**没写**返回结构」／「官方返回结构可能变了」，而官方页写了 —— `ISketch\GetLines2.md`：`This set of data repeats for each line in the sketch. The number of doubles returned is (lineCount * 12).`（与我们 `ELEMS_PER_LINE = 12` 相符）、`ISketch\GetArcs2.md`：`The size of the array is (NumArcs * 16).`（与 `ELEMS_PER_ARC = 16` 相符）、`ISketch\GetEllipses3.md`：`The size of the array is (NumEllipses * 20).`（★ 与本仓实测记录的 22/个 不同）。**这条不属于核对 C，未计入统计。**

---

**都核了几处**：50 处成员（废弃标记逐个对 `C:\swapi\types\` 页面：ISketch 24 · ISketchManager 10 · IModelDoc2 12 · IFeature 1 · IModelDocExtension 1 · ISelectionMgr/IEntity 2）＋ 6 个 `C:\swapi\enums\` 枚举页 ＋ 8 处字面量表（共 26 个值）＝ 64 处。
**报了几条**：5 条（第 1–5 条）。
**高置信**：第 1、2、3、4、5 条 —— 5 条全部为高置信（每条的两段原文均已逐字抄录、可 grep）。
