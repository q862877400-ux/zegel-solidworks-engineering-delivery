# vd50-A · features 域：能力 level 与真机证据 逐条核对

★ 只读核 · 未改动仓内任何文件（唯一写入：本文件）
★ 域口径：`features` = 实现落在 `scripts/sw_part.py` / `scripts/sw_feature_entry_ops.py` / `scripts/sw_feature_readback.py` 的能力条目；
★ 「相邻」= 同属特征族、实现落在别的 `sw_*.py`、但条目把上面三个模块当依据引用的（本次一并核了，因为它们的结论直接依赖这三个模块的真机记录）。

---

## 一、核了哪些条目（13 条，全部 `level: verified`）

| # | id | label | 实现落点 | 结论 |
|---|---|---|---|---|
| 1 | `part_and_features` | 参数化零件与基础特征 | `sw_part.py` | ★ **对不上（成立）** |
| 2 | `feature_readback_criterion` | 特征建成回读判据 | `sw_feature_readback.py` | 存疑 |
| 3 | `modeling_feature_readback_tools` | 建模闭环补全 | `sw_part.py` | 存疑 |
| 4 | `feature_build_extrude` | 拉伸族 | `sw_part.py` | 一致 |
| 5 | `chamfer_fillet_on_selection` | 倒角 / 圆角 | `sw_part.py` | 一致 |
| 6 | `pattern_and_mirror` | 阵列与镜像 | `sw_part.py` | 一致 |
| 7 | `feature_revolve_cut` | 旋转切除 | `sw_part.py::revolve_cut` | 一致 |
| 8 | `feature_cosmetic_thread` | 螺纹线 | `sw_feature_entry_ops.py` | 一致 |
| 9 | `feature_hole_wizard5` | 异型孔向导 | 相邻（`sw_hole_features.py`） | 一致 |
| 10 | `feature_loft_cut` | 放样 / 边界切除 | 相邻（`sw_loft.py`） | 一致 |
| 11 | `surface_flatten` | 曲面展平 | `sw_feature_entry_ops.py` | 一致 |
| 12 | `holes_and_finishing` | 孔槽、螺纹、圆角与倒角 | 相邻（引 `sw_part.py`） | 存疑 |
| 13 | `sketch_build` | 建草图与画基本几何 | `sw_part.py` | 一致 |

★ 三件事的总体结果：
① **evidence 文件存在性**：13 条里被引用的仓内文件路径共 **55 条**，**缺 1 条**（见 F4）。
② **结论一致性**：**4 条对不上**（F1 成立 · F2 / F3 / F4 存疑），**9 条逐字对得上**。
③ **「证据否定、条目肯定」**：**1 条成立**（F1），其余条目凡有负面证据的都在 label / evidence 里**如实披露**（见 §三）。

---

## 二、对不上的 4 条

### ★★★ F1 ·【成立】`part_and_features` —— 三个数字都与它自己引的证据文件相反

**判定：成立** · **一句话依据**：条目说「66 对逐一试 / 8/8 / 含边 0 的组合都成」，而证据文件记的是 **试了 12 对、其中 4 对含边 0 的**明确失败**。

**仓内那一段**（`capabilities.yaml` · `part_and_features` · `evidence[0]` 原文）：

> `★★ 判据用了事实 53 的处方：**把猜测变成一张穷举表** —— 对盒体 12 条边的**两两共 66 对**逐一试。真机（走 `sw_guard`，7.1 s 无弹窗）：成功的边对是 `[0,1] [0,2] [0,3] [0,4] [0,7] [0,8] [0,11] [1,2]`（**8/8**，到上限就停）—— ★★ **含边 0 的组合都成，连 `[0,1]` 这种相邻边都成**。证据 output/dimension-edge-pairs-evidence.json。`

**目标那一段**（`output/dimension-edge-pairs-evidence.json` 原文）：

> `"tried": 12,`
> `{"pair": [0, 5], "selected": 2, "created": false, "err": "选中了 2 个实体而 \`AddDimension2\` **回 None** ⇒ 没建成尺寸…"},`
> `{"pair": [0, 6], "selected": 1, "created": false, "err": "选中了 1 个实体而 \`AddDimension2\` **回 None** ⇒ 没建成尺寸…"},`
> `{"pair": [0, 9], "selected": 2, "created": false, …}`
> `{"pair": [0, 10], "selected": 1, "created": false, …}`
> `"verdict": "pass"`

三处对不上，逐条对照：

| 条目写的 | 证据文件写的 | 性质 |
|---|---|---|
| 「**两两共 66 对**逐一试」 | `"tried": 12` | **夸大范围**（12 ≠ 66；`successes` 只有 8 项，`pairs` 数组只有 12 项） |
| 「成功的边对 …（**8/8**）」 | 8 次成功 / **12 次尝试** | **把成功数写成了通过率**（真值 8/12） |
| 「★★ **含边 0 的组合都成**」 | `[0,5] [0,6] [0,9] [0,10]` 四格**全 `created: false`** | ★★★ **否定结果被写成肯定** |

★ 同一句断言在同一条目的 `limitations` 里又出现一次（`⚠ 2026-10-03（轮 405）…纯盒体上 **8/8 边对**都成…`），
★ 并且已经原样扩散到 MCP 工具描述：`mcp-server` 侧 `solidworks_add_dimension` 的说明写着
★ 「★ 真机证据：纯盒体上 **8/8 个边对**都建出了尺寸（`output/dimension-edge-pairs-evidence.json`）」。
⇒ ★ **这三处都需要改**；**证据文件是对的，条目与工具描述是错的**。

---

### ★★ F2 ·【存疑】`feature_readback_criterion` —— 条目说的成员名，与它引的证据文件里写着的不一样

**判定：存疑** · **一句话依据**：条目写「改用 `Extension.GetWhatsWrongCount` ⇒ 取到」，而它引的那份证据文件里逐字写的是 `GetWhatsWrong2`（该成员在两套官方源里都查不到）。

**仓内那一段**（`capabilities.yaml` · `feature_readback_criterion` · `evidence[1]` 原文）：

> `★ **三轮真机打磨**：① 直接调 \`GetWhatsWrong2\` ⇒ 取不到；② 改用 \`Extension.GetWhatsWrongCount\` ⇒ 取到（0 条错）；③ 过滤从「枚举容器名」改成「\`GetTypeName2\` 非空」（★ 与 UI 语言无关）`

**目标那一段**（`output/modeling-readback-evidence.json` —— 同一次采集落下的文字，逐字）：

> `"★": "规则 6：特征在树里 + EditRebuild3 真 + GetWhatsWrong2 数 0"`

**官方那一段**（`C:\swapi\types\` 检索结果）：

- 存在：`C:\swapi\types\IModelDocExtension\GetWhatsWrongCount.md` ⇒ `**Signature**: \`System.int GetWhatsWrongCount()\``
- 存在：`C:\swapi\types\IModelDocExtension\GetWhatsWrong.md`
- **`GetWhatsWrong2` 在 `C:\swapi\types\` 下 0 个 md（查不到）**

★ 为什么只判**存疑**而不是「不成立」：仓内 `scripts/sw_feature_readback.py` 的 docstring **自己写明了这件事**
（`⚠ **\`GetWhatsWrong2\` 在本机两套源里都不存在** ⇒ ★ 而 \`docs/union-conventions.md\` **规则 6 的措辞**写的正是 \`GetWhatsWrong2\` ⇒ ★ **那是规则文本的一处失真**`），
★ 且代码实际调用的确是 `GetWhatsWrongCount`、结果 `count=0` —— **实质结论没错，错的是产物里留下的那段字**。
★ ⇒ 属**命名残留**，不是能力虚标；但它已烧进落盘证据产物，会误导下一轮复核。

---

### ★★ F3 ·【存疑】`modeling_feature_readback_tools` —— 条目给的「单位判决」，证据文件里没有；且文件自己事先规定的判据没过

**判定：存疑** · **一句话依据**：条目断言「单位判决 = 毫米」，而该证据文件只记了两次体积下降，且它**事先写死的首要判据 `drop_ratio ≈ expected_ratio` 实际不成立**。

**仓内那一段**（`capabilities.yaml` · `modeling_feature_readback_tools` · `evidence[3]` 原文）：

> `★ \`python tools/probe_shell_thickness_units.py\` ⇒ 单位判决 = 毫米（t=2 ⇒ 空腔 96×56×18；t=4 ⇒ 92×52×16）· ⚠ 官方文档写 meters 对本机不成立`

**目标那一段**（`output/shell-thickness-units.json` 原文）：

> `"unit_conflict": { "official": "meters", "module_header": "millimetres" },`
> `"runs": { "2.0": { … "volume_before": 120000.0, "volume_after": 23232.0, "drop": 96768.0 … }, "4.0": { … "volume_after": 43456.00000000001, "drop": 76544.0 … } },`
> `"verdict": { "drop_ratio": 0.791, "expected_ratio": 2.0, "★": "★ 事先规定：若两次**都成功**且**下降之比 ≈ 厚度之比** ⇒ **口径与传入值一致**；…再结合「下降是否落在毫米量级」 ⇒ 判它是不是毫米。" }`

★ 对不上的点：文件里**没有任何地方写着「毫米」这个判决**；而它自己**事先规定**的首要判据（`drop_ratio ≈ expected_ratio`）实测 **0.791 vs 2.0、不成立**。
★ 次要判据（下降量落在毫米量级）成立：`96768 = 96×56×18`、`76544 = 92×52×16`，与条目括注的两个数**逐字吻合**。
★ ⇒ 条目的**数对、判决是推出来的、且没写明首要判据未过**。属**表述超出来源**，不是数据造假。

---

### ★ F4 ·【存疑】`holes_and_finishing` —— 它列的「依据」里有一个文件在本机不存在

**判定：存疑** · **一句话依据**：`limitations` 的「依据」链里点名了 `output/slot-direct-probe.json`（★ 对象失效），而该文件在 `D:/AI/SW` 全树 0 命中 —— 同一条依据链上的另外三个文件都在。

**仓内那一段**（`capabilities.yaml` · `holes_and_finishing` · `limitations[1]` 尾部原文）：

> `**依据**：\`output/countersink-mm-probe.json\`（★ 毫米 2/2 PASS）· \`output/hole-units-fixed-evidence.json\`（★ **PASS 5/5**）· \`output/countersink-diag-probe.json\`（★ 米 ⇒ \`创建圆草图失败\`）· \`output/slot-direct-probe.json\`（★ 对象失效）· \`scripts/sw_hole_features.py\` 的 \`_point_from_selection\`（★ 修后的注释）· \`scripts/sw_part.py\` 的 \`sketch_circle\`（★ 毫米）· 事实 202 / 227 / 228 / 229`

**目标那一段**：**给不出 —— 查不到。**（按铁律 3，不拿相似名字顶替）

- `D:/AI/SW/output/slot-direct-probe.json` ⇒ **不存在**
- `D:/AI/SW` 全树 `slot-direct-probe*` 递归搜索 ⇒ **0 命中**
- 同一条依据链上的另三个：`countersink-mm-probe.json` **存在** · `hole-units-fixed-evidence.json` **存在** · `countersink-diag-probe.json` **存在**
- 另有 `output/` 下 542 个文件、且 `git ls-files` 对 `output/**` **0 命中** ⇒ 该目录是 gitignore 的构建产物区

★ 为什么只判**存疑**：这条引用在 `limitations` 而不在 `evidence` 列表里（该条目的 4 条 `evidence` 全部指向存在的文件），
★ 且 `output/` 是可变的本地产物区 —— **「文件不存在」是硬事实，「因此条目失实」不是**。

---

## 三、对得上的 9 条（逐条抄录原文对照，防止下轮重复核）

| 条目 | 条目原文（节选） | 证据文件原文 | 判定 |
|---|---|---|---|
| `feature_build_extrude` | `extrude_boss(10) ⇒ ★ **包围盒 size [40,20,10]**；…extrude_midplane(总深 10) ⇒ size [40,20,10] 且 min/max **±5**` | `"boss_size_mm": [40.0, 20.0, 10.0]` · `"midplane_size_mm": [40.0, 20.0, 10.0]` · `"min": [-20,-10,-5]` `"max": [20,10,5]` · `"negative_missing_sketch": {"ok": true, "raised": "ValueError"}` · `"verdict": "pass"` | 一致 |
| `chamfer_fillet_on_selection` | `选 index:0 → chamfer(2mm) ⇒「**倒角1**」（19→20）；index:1 → fillet(3mm) ⇒「**圆角1**」（→21）…负例：index:9999 ⇒ EntitySelectionError（给出上界 18）` | `"n_before": 19, "n_after": 20` · `"feature": "圆角1", "n_after": 21` · `"msg": "EDGE 序号 9999 越界（体 0 上共 18 个）"` | 一致 |
| `pattern_and_mirror` | `镜像 ⇒ **\`镜向1\`** · type=**\`MirrorPattern\`**；阵列 ⇒ **\`阵列(圆周)1\`** · type=**\`CirPattern\`**（★ 前置 \`基准轴1\`）` | `"axis_features": ["基准轴1"]` · `"new": ["基准轴1","阵列(圆周)1"], "type": "CirPattern"` · `"new": [… ,"镜向1"], "type": "MirrorPattern"` | 一致 |
| `feature_revolve_cut` | `**树新增 \`切除-旋转1\`**，★ **体积 0.8255 倍**…对照组 \`IsCut=False\` ⇒ \`旋转1\`、体积 **1.1745 倍**` | `"new": ["切除-旋转1"], "vol_ratio": 0.8255` · `"tag": "对照：旋转**凸台**（IsCut=False）" … "new": ["旋转1"], "vol_ratio": 1.1745` | 一致 |
| `feature_cosmetic_thread` | `选**圆柱面的一条圆边** ⇒ … ⇒ **名 \`装饰螺纹线1\`** · **型 \`CosmeticThread\`**`；并如实写出两格对照「选圆柱面本身 ⇒ 不成 ✗ / 什么都不选 ⇒ 不成 ✗」 | `"pick": "edge", "ok": true, "ret_name": "装饰螺纹线1", "ret_type": "CosmeticThread"`；`"pick": "face" … "ok": false`；`"pick": "none" … "ok": false`；`"passed": 1, "total": 3` | 一致（**负面格已披露**） |
| `feature_hole_wizard5` | `**特征 7 → 8**，新增 **\`M8 间隙孔1\`**`；并如实写出 5 格里 4 格 `SSize` 形态返回 `None` | `"before": 7 … "returned": "CDispatch", "new_features": ["M8 间隙孔1"]`；另 4 例 `"returned": "None"`；`"passed": 1, "total": 5` | 一致（**负面格已披露**） |
| `feature_loft_cut` | `建成 \`切除-放样1\`·**类型名 \`BlendCut\`**·★ **体积 0.9714 倍**`；对照组凸台 `体积 1.0286 倍` | `"feature_name": "切除-放样1", "type_name": "BlendCut", "vol_ratio": 0.9714, "args_count": 12`；对照 `"type_name": "Blend", "vol_ratio": 1.0286, "args_count": 18` | 一致 |
| `surface_flatten` | 四格对照 `① 面(1)+锚点(16) ⇒ **成** ✓ / ② 面(1)+引导边(2) ⇒ **不成** ✗ / ③ 面+锚点+引导边 ⇒ **成** ✓ / ④ 只给面(1) ⇒ **不成** ✗` | 四例逐条一致（`① ok:true ret_type FlattenSurface` / `② ok:false returned None` / `③ ok:true` / `④ ok:false`）；`"passed": 2, "total": 4` | 一致（**负面格已披露**） |
| `sketch_build` | `bbox-smoke` **8/8**、`ellipse-smoke` **11/11**、`centerline-smoke` **8/8** | `"passed": 8, "total": 8` / `"passed": 11, "total": 11` / `"passed": 8, "total": 8`，且 `size=[10.0,50.0,50.0]` 与「半径 25 ⇒ 跨度 50」逐字对上 | 一致 |

★ 另**顺带核过、结论为真**的签名类断言（每条都有官方原文那一段，故列在此处而非 §二）：

- `feature_revolve_cut.source_evidence`：「`FeatureRevolve2.md` 的 **20 参**签名（第 4 个是 **`IsCut`**）」
  ⇒ `C:\swapi\types\IFeatureManager\FeatureRevolve2.md`：`Feature FeatureRevolve2( System.bool SingleDir, System.bool IsSolid, System.bool IsThin, **System.bool IsCut**, … )` —— **恰好 20 参、第 4 位确为 `IsCut`** ✔
- `feature_build_extrude.source_evidence`：「`FeatureExtrusion3` 的 **23 参数**」
  ⇒ `C:\swapi\types\IFeatureManager\FeatureExtrusion3.md`：`Feature FeatureExtrusion3( System.bool Sd, System.bool Flip, … System.bool FlipStartOffset )` —— **数出 23 参** ✔
- `part_and_features.evidence`：「官方 `IModelDoc2.EditUndo2(int Steps)`，**1 参**」
  ⇒ `C:\swapi\types\IModelDoc2\EditUndo2.md`：`void EditUndo2( System.int Steps )` ✔

---

## 四、★ 特别说明：`modeling_feature_readback_tools` 不是「否定写成肯定」

该条目 `level: verified`，而它的 `evidence` 里**确实有 4 个工具里 2 个失败**：

- 仓内原文（`label`）：`建模闭环补全（抽壳 ✅ / 圆顶 ✅ 真机通过 · 筋 未验 · 复合曲线 真机失败）`
- 仓内原文（`evidence[2]`）：`⚠ \`python tools/verify_composite_curve_smoke.py\` ⇒ 7/8 · verdict: fail，而它写明「前置成立 ⇒ 这是真失败」（★ 不是前置不可达那种免责失败）`
- 目标原文（`output/modeling-readback-evidence.json`）：`"rib": { "ok": false, … "reason": "特征名 '筋1' 不在特征树里…" }` · `"insert_composite_curve": { "ok": false, … "error": "RuntimeError: IModelDoc2.InsertCompositeCurve 返回 False ⇒ 合成曲线没建出来。" }` · `"judgement": { "tools_ok": 2, "tools_total": 4 }`

⇒ ★ **否定结果在 label 与 evidence 里都写明了**（`复合曲线 真机失败` / `7/8 · verdict: fail`），**不属第三类**，判**一致**。
★ 唯一可议之处：落盘文件顶层 `"verdict": "pass"` 只由 `judgement.selfcheck + tools_ok≥1` 决定，**不是 4/4** —— 但条目已如实写「2/4」，故不另立条目。

---

## 五、本次没做的（按铁律 3「查不到就说查不到」）

- `part_and_features` 的多条证据只引了 `tools/*.py` 脚本与 `pytest` 命令、**没有落盘证据文件**
  （`probe_window_vs_graphics.py` / `_list_sw_windows_all.py` / `tests/test_modal_dialogs_can_fire.py` / `probe_add_relation_forms.py`）⇒ **无对象可核，不报**。
- `chamfer_fillet_on_selection.limitations` 引的 `tests/live/test_live_sw_add_chamfer_tool.py`
  ★ 是**外部 MIT 来源**的路径，本机克隆里**确实存在**（`C:\swprojects\andrewbartels1\tests\live\test_live_sw_add_chamfer_tool.py`）⇒ **不是缺陷，不报**。
- `preview_and_review_report.source_evidence` 写「sw_part 的 `set_standard_view`」，而该函数**在 `sw_part.py` 里没有**（在 `scripts/sw_review.py`，MCP 工具也指向 `sw_review`）
  ⇒ ★ **属 review 域、非本片 features 域，且不是 evidence 类断言** ⇒ 按「宁少勿滥」**不计入对不上**，仅在此备注。
- 未跑 SolidWorks、未跑 pytest、未改动任何仓内文件（铁律 1）。