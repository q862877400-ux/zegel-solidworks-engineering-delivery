# 裁判汇总 · 四份「对账已完」稿的复核

> **本人只做一件事**：逐份读 A/B/C/D，**回到原文**复核它们各自报的「对不上」。
> ★ **没有跑 SolidWorks、没有跑 pytest、没有改这四份稿**；本文件是本次唯一写入。
> ★ 每条判定都给**可搜索的原文位置 = 文件 + 片段**（★ 按本仓惯例不写行号）；查不到就说查不到（铁律 5）。
> ★ 「核了几处」按**各稿自己声明的口径**取（A=能力条目 / B=高置信行 / C=成员条数 + 源级对账 / D=判据条数），**不是我这轮重新数的**。

---

## 一 · ★ 总表：四件事各核了几处 · 各发现几处对不上

| 稿 | 核的东西 | **核了几处** | **对不上几处** | 稿自己给的判定分布 | 对不上的成色 |
|---|---|---|---|---|---|
| **A** `A-evidence-vs-level` | `capabilities.yaml` 里 `level: verified` 的**每一条**的 `evidence` vs 文件实况 | **97 条**能力<br>（内含 **266 处**路径引用 + **116 个** `output/*.json` 逐个读回） | **7** | 全是「引用链 / 引用内容」问题，★ **等级判错 0 条** | ★★ 最重（1 条证据是否定而条目写肯定） |
| **B** `B-audit-highconfidence` | 30 份 `audit-*.md` 分歧表里**置信度 = 高**的行 | **93** 条 | **4** | 成立 **89** / 不成立 **3** / 存疑 **1** | ★ 轻（3 条「不成立」是条目已过时，不是错判） |
| **C** `C-missing-domains` | 补 `api-02-sheetmetal` / `api-05-drawing` 两域，外加 **6 处源级对账** | **63** 条成员（20 + 43）<br>+ **6** 处源级对账 | **6**（F1–F6） | F1/F3/F4 = 源自身或已声明证据错挂<br>F2 = 官方源自相矛盾<br>F5/F6 = 覆盖缺口 / 重复计数风险 | ★ 中（★ 全是**官方源自己的**坑，不是抄错） |
| **D** `D-gate-anchors` | `GATE-FINAL.md` §三 的 **C1–C12 + 分流 R** | **13** 条判据 | **4** | 成立 **10** / 存疑 **1**（C6）/ 不成立 **1**（C8） | ★ 中（1 条闸没有可读对象） |
| **合计** | — | **272 处**（97 + 93 + 69 + 13） | **21 处**（7 + 4 + 6 + 4） | — | — |

★ **一句话**：**核了 272 处，报出 21 处对不上（7.7%）；我这轮抽查 8 条，7 条成立、1 条不成立 ⇒ 成立率 87.5%。**

---

## 二 · ★★★ 抽查证伪（8 条 · 跨全部 4 份 · 逐条回原文）

判据：**成立** = 我回到原文，逐字复现了它说的那个事实；**不成立** = 回原文看到的是别的；**存疑** = 一半对。

| # | 来自 | 稿的主张（原文） | **我回原文看到的** | 判定 |
|---|---|---|---|---|
| **1** | **A** | 「★ 唯一一条「**引的三份证据全部记否，条目写成「真机建成 ✓」**」」—— `surface_delete_hole` 的 evidence 挂着 `output/delete-hole-for-surface-evidence.json` 等三份 | ★ 三份**都在**，且**三份都记否**：`for-surface` → `passed=0 total=3 verdict=successor_also_fails`；`inner-loop` → `passed=0 verdict=inner_loop_still_fails`；`on-surface` → `passed=0 total=4 verdict=delete_hole_still_noop_on_surface`。★ 而 `capabilities.yaml` 的 `surface_delete_hole` 条目 `label` 写着「★ **真机建成**」、`evidence` 第 1 条写「★★ 2026-10-03（轮 564）**真机建成**（零弹窗）…✓」，第 2 条**逐字点名那三份否证文件**。★ A 说支持「建成」的真跑在**未被引用的** `output/planar-region-and-delete-hole-evidence.json`（`verdict=planar_region_and_delete_hole_work`）—— ★ 该文件也在，`passed=2 total=2`。 | **成立** |
| **2** | **A** | 「`output/simulation-evidence.json` / `output/topology-evidence.json` **❌ 不存在**」，而条目把 `7,310 个单元` / `GetPlotCount == 4` / `suggested_size_mm: 4.933908705960544` 写死在条目里 | ★ `output/` 下 `*simulation*` 只有 6 份（`addin-by-clsid` / `addin-status` / `loadaddin-by-path` / `loads-evidence` / `study-evidence` / `study-shapes`），`*topolog*` 只有 `topology-readback-evidence.json` ⇒ ★ **两份都不在**。⇒ A 说这串数字「回原文核不到」是对的。 | **成立** |
| **3** | **A** | `simulation_solver_options` 把「`list_setter_summary` ok=True（9 个族 / 202 个 setter 名）」挂到 `output/batch37-evidence.json`，而 ★「该文件里 **搜不到 `setter`**」 | ★ 顶层逐字：`passed=1 of=4 verdict=partial`；`steps` 四步 `create_study` / `set_option_ComputeFreeBodyForce` / `set_option_ContactPenaltyStiffnessScaleFactor` / `set_options`；★ 全文件 `setter` 命中数 = **0**。 | **成立** |
| **4** | **B** | §3.1「官方原文**引错一个字**（存疑）」—— 条目引 `- **IsWarning**: …false to not`，真文是 `false if not` | ★ `C:\swapi\types\IFeature\GetErrorCode2.md` 逐字：`- **IsWarning**: True if the error is a warning, false if not` ⇒ ★ 引文确实多了一个 `to`。★ 另注：`false to not` 在**别的**官方页确实成篇出现（如 `IFeature\MoveFreezeBarTo.md`）⇒ 这是**抄错一行**，不是官方通例。 | **成立** |
| **5** | **B** | §3.4「`scripts/sw_review.py` 的 `zoom_to_fit` / `clear_selection_for_preview` 里各有一次 `GraphicsRedraw2`」—— ★ 当前只剩 docstring 里的官方引文，**无可执行调用** ⇒ 条目已过时 | ★ `scripts/sw_review.py` 全文 `GraphicsRedraw` 命中只有 3 处：模块注释里逐字引官方「★ 官方 `types/IModelDoc2/GraphicsRedraw2.md` 逐字：「**Obsolete. Superseded by [[IModelView::GraphicsRedraw]] …**」」+ 一处 `get_com_member(view, "GraphicsRedraw", None)`。★ **零个 `GraphicsRedraw2` 调用**。★ 同型的 §3.2（`sw_part.py`）与 §3.3（`sw_sketch_modify_ops.py` 的 `_active_sketch_name`）我也核了：`GetActiveSketch2` 只出现在「★ 2026-10-03（接手轮）**换走后继入口** —— 原来是 `get_com_member(model, "GetActiveSketch2")`」这类注释里，**同样零可执行调用** ⇒ ★ 三条同判。 | **成立** |
| **6** | **C** | F1「`api-03-weldment.md` 把一个数字挂到了错误的树上」—— 声称 `sldworksapi\`（.NET 树）该通配 = **285**，**289 是 VBA 树（`sldworksapivb6\`）** 的计数 | ★ 四次计数逐字复现：.NET 全名通配 = **285** · .NET `*IFeatureManager~*` = **285** · VBA `SldWorks~FeatureManager~*` = **289** · VBA `*IFeatureManager*` = **0**。⇒ ★ 285/289 与「289 挂错树」**逐字成立**（且 A 所说 `api-03-weldment.md` 那句另一行「VBA 树按 IFeatureManager 过滤 = 0」**仍然成立**，C 自己也声明了这不是同一处错）。 | **成立** |
| **7** | **D** | C8「**全仓 grep `refuted-patterns` 只有 3 处命中，全是散文** ⇒ ★ **该文件在仓里不存在**」⇒ 判**不成立**，即「这条闸今天没有可读对象」 | ★ `Test-Path D:\AI\SW\docs\refuted-patterns.json` = **False**；★ `docs/` 下的 `.json` 共 11 份（`judge-registry.json` / `gate-classification.json` / `gate-wiring-exemptions.json` / …）⇒ ★ **没有 `refuted-patterns.json`**。★ 其余锚点也对得上：`docs/judge-registry.json` 在、`docs/gate-classification.json` 在。 | **成立** |
| **8** | **D** | C6 存疑：「枚举里的 **`tree_delta` / `unique_name` / `file_sha256` 这三个 token 在全仓只出现在 GATE-FINAL.md 自己**」 | ★ `GATE-FINAL.md` 的 `fix.readback` 枚举逐字是 `count_plus_one \| tree_delta \| unique_name \| file_sha256 \| none`（5 个，与 D 说的对得上）。★ 但 —— `tree_delta` 在仓里**有 15 处真实用法**，全在 `scripts/` 里作 `verified_by` 的取值：`sw_curve_and_split.py`（4 处 `"verified_by": "tree_delta+…"` / `"return_values + tree_delta"`）· `sw_ref_geometry.py`（`r["verified_by"] = "tree_delta"` + 2 处）· `sw_surface_edit_ops.py`（5 处）· `sw_surface_ref_ops.py`（2 处）。★ `unique_name` 全仓唯一命中是 `tests/test_sw_assembly_doc_contract.py` 里一个**测试函数名**的子串（`…exceed_unique_names_because_of…`）⇒ 作为 token 确实无出处；★ `file_sha256` 全仓 **0 命中**。⇒ ★ **「三个 token 全仓只在 GATE-FINAL」这句对 `tree_delta` 是错的**（它恰恰是仓里既有的事实判据用法），只有 `file_sha256` 真的一处都没有。 | **★ 不成立**（`tree_delta` 那半句）<br>★ 而 C6 判「存疑」的方向**仍站得住**：`docs/judge-registry.json` 的 4 条 `id` 逐字是 `loads_count_plus_one` / `count_property_on_a_fresh_study` / `loads_count_plus_one_first_load` / `load_objects_by_index` ⇒ ★ **枚举 5 个取值里没有一个在登记表里**，C6 的**结论**不必改，**只有那个计数理由要改**。 |

### ★ 成立率

> ### **抽查 8 条 → 成立 7 · 不成立 1 · 存疑 0　⇒　★ 成立率 87.5%**

★ 分稿看：A **3/3**（+ 脚注 A-④ 见下也是成立）· B **2/2** · C **1/1** · D **1/2**。
★ 不成立的那 1 条**不改变 D 的 C6 判定**（存疑方向对，计数理由错）⇒ ★ **21 处「对不上」里，我推翻 0 处、修正 1 处的支撑理由。**

### ★ 脚注：同批**另外**核过、同样成立的 6 条（不计入上面 8 条的分子分母）

| 来自 | 主张 | 复核结果 |
|---|---|---|
| A-④ | `loom-type-evidence.json` / `out-cut-list-property-names-evidence.json` 是**死链**，仓里真名是 `loft-type-evidence.json` / `cut-list-property-names-evidence.json` | ★ 成立：`output/` 下 `*loft*` 6 份、**零 `loom*`**；`*cut-list*` 4 份、**零 `out-*`**。`capabilities.yaml` 两处拼错逐字在（`… · loom-type-evidence.json` / `…（out-cut-list-property-names-evidence.json PASS）`） |
| C-F2 | `ISheet/GetProperties.md` 写「array of **seven** doubles」却列了 **8** 个名字，且 `sameCustomPrp` 无定义；`GetProperties2.md` 写 **eight** 并补上 `sameCustomProp` | ★ 成立：两份文件逐字复现（`seven`/`sameCustomPrp` vs `eight`/`sameCustomProp` + `*sameCustomProp* = Value is a boolean packed into a double…`） |
| C-F3 | `IDrawingDoc` 5 处死链（`IICreateAngDim4`/`IICreateLinearDim4`/`IICreateOrdinateDim4` · `IDrawngDoc` · `ISkethcManager`/`MakeSketchBlockSelected` · `1stAngleViews2` · `UnInsertBreakVertical`） | ★ 成立：源文件里 5 处错拼逐字复现；**5 个真名全部 `Test-Path=False`**，而 `ICreateAngDim4` / `Create1stAngleViews2` / `InsertBreakVertical` / `ISketchManager\MakeSketchBlockFromSelected` 全部 `True`；`types\IDrawngDoc\` 与 `types\ISkethcManager\` **两个目录都不存在** |
| C-F4 | `swLoftedBendFacetOptions_e` 只有 4 个成员，`swSegmentLength` / `swSegmentAngle` **两套官方源都没有** | ★ 成立：`enums\swLoftedBendFacetOptions_e.md` 逐字只有 `swAngleBetweenSegments 3` / `swBendsPerTransitionSegment 1` / `swChordTolerance 0` / `swMaxSegmentLength 2` |
| C-F5 | `ISheet` / `IView` / `INote` / `ITableAnnotation` / `IModelView` / `ISectionViewData` 在 CHM **.NET 树整域缺席**（各 0 页、接口首页也不存在） | ★ 成立：6 个接口逐个 `Get-ChildItem` 计数**全为 0 / 0** |
| D-问3 | C11 附注「全仓提及只有 **3** 处 ⇒ **对不上**：实际全仓 **16 处、分布在 5 个文件**」 | ★ 成立（**逐字**）：排除 D 自己的报告与 `vd50-D-3.md` 后，`classify_audit_divergences` 在 `patterns-shard-1.md`(2) + `patterns-shard-3.md`(1) + `gate-cand-C-loop.md`(6) + `GATE-FINAL.md`(5) + `PROMPT-B-batch-generator.md`(2) = **16 处 / 5 个文件**；★ 且 `tests/` + `scripts/` 命中 = **0** ⇒ C11 的结论「无门禁引用、无测试」**成立** |
| D-C12 | `output/obsolete-usage-in-repo.json` 改后读数 `2026-10-03 23:42:25` / 646 / 677 / 876，键集只有 6 个 | ★ 成立：`at=2026-10-03 23:42:25 scanned=646 rows=677 occ=876`，键集逐字 = `at` / `official_obsolete_members` / `scanned_files` / `hit_rows` / `hit_occurrences` / `rows` |
| D-C9 | C9 是全套里唯一能逐个复算的（25 / 8 / 30 / 3 / 5 / 22） | ★ **集合代数部分全部复现**：`marked=25 union=30 inter=[505,509,511] seedonly=[502,504,506,507,510] markedonly=22`。★ 但**分母已过期**：现在的读数是 `rows 512 · max 514`（D 记的是 `rows 509 · max 511`）⇒ ★ `known-facts.md` 在 D 之后又长了 3 条 ⇒ **C9 的数仍成立（它只依赖标记集与种子集），但那两个总数要标成「截至 D 轮」** |

---

## 三 · ★★ 分级（★ 只按「要不要立刻处理」分，不按严重性排版）

### ★★ A 级 · **要立刻改**（★ 3 条 · 都会误导后续排期）

| # | 位置 | 为什么必须立刻改 | 建议动作 |
|---|---|---|---|
| **A-1** | `capabilities.yaml` 的 `surface_delete_hole` 条目（`label` + `evidence` 第 1/2 条） | ★ **这是本次点名的那一类**：被引的**三份证据文件自己记的是失败**（`passed:0` + `verdict` 带 `fails`/`noop`），条目却写「★ **真机建成**…✓」⇒ ★ **任何人顺着 evidence 读一遍都会得到相反结论** | ★ 把 `evidence` 第 2 条的指针换成**真正支持它的那份** `output/planar-region-and-delete-hole-evidence.json`（`passed=2 total=2` · `verdict=planar_region_and_delete_hole_work`），并把那三份**降级标注成「负例 / 反例（夹具不符）」** ⇒ ★ **能力与 `level: verified` 不必动**（它有实据），要动的只是**指针** |
| **A-2** | `capabilities.yaml` 的 `simulation_solver_options` 条目（`evidence` 最后一条） | ★ 条目把「`list_setter_summary` ok=True（9 个族 / 202 个 setter 名）」挂在一份**顶层 `passed=1 of=4 · verdict=partial`、且 `setter` 零命中**的文件上；★ 而那份文件的三步 `ok:false` **条目其余 evidence 一字未提** | ★ 要么把断言改挂到真正含该结果的文件上，要么**在条目里如实补写「`batch37-evidence.json` 本身是 1/4 partial」** ⇒ ★ 现状是「挑了那一份里最像的一句」，这在排期上等同于**把 1/4 写成 PASS** |
| **A-3** | `GATE-FINAL.md` §三 的 **C8** | ★ 它自称「★★ **唯一常驻硬门禁**」，而**判据的唯一依据 `docs/refuted-patterns.json` 在仓里不存在**（全仓只有散文提及）⇒ ★ 这条闸**今天跑不起来**，而文档口径会让人以为它在跑 | ★ 在 `GATE-FINAL` 的 C8 上标 **BLOCKED · 缺 `docs/refuted-patterns.json`**（同 D 的口径），或把台账补出来 ⇒ ★ 它**其余锚点全部命中**（事实 503/509 / `sw_surface_features.py` 那两处旧注释 / `_run_judge_preflight_gate` / 接线五层）⇒ ★ **缺的就是那一份文件**，不是判据本身有问题 |

### ★ B 级 · **要记档**（★ 6 条 · 补上事实/待办即可，不必今天动代码）

| # | 位置 | 要记什么 |
|---|---|---|
| B-1 | `capabilities.yaml` 的 `simulation_and_fea` / `mesh_size_sanity_gate` / `topology_optimization` | ★ `output/simulation-evidence.json` 与 `output/topology-evidence.json` **产物不在（脚本在）** ⇒ ★ 条目里那串**具体数字**（`7,310 个单元` / `GetPlotCount == 4` / `suggested_size_mm: 4.933908705960544`）**回不到原文** ⇒ ★ 按铁律 5 在条目里写「**该产物未落盘，数字查不到**」，或把产出脚本重跑一遍把文件补回仓 |
| B-2 | `capabilities.yaml` 的 `loft_and_sweep` / `weldment_cut_list` | ★ 两处**文件名笔误**（`loom-`↔`loft-`、`out-cut-list-`↔`cut-list-`）⇒ ★ 意图文件都在，改引用即可；★ 但它们按判据「逐个 `path.exists`」是**死链**，会污染后续的证据可达性检查 |
| B-3 | `recon/audit-vs-official/audit-03-weldment-C.md` #1 | ★ 引文把官方的 `false if not` 抄成 `false to not` ⇒ ★ **抄进 `api-05-drawing.md` 之前先改**（★ 注意：官方**别的**页确实通篇是 `false to not`，所以这不是「官方通例」，是**抄错这一行**） |
| B-4 | `api-pre/api-03-weldment.md` 第 19 行 | ★ 逐条把 **289 改成 285**（289 是 **VBA 树** `sldworksapivb6\` 的数）⇒ ★ 顺带记下同句的另一半**仍然成立**（VBA 树按 `IFeatureManager` 过滤 = 0），别把两处混为一谈 |
| B-5 | 官方源已知坑（**F2/F3/F4**） | ★ 建一条共享的「**官方源自身的错**」清单，供两份摘要抄录时对照：① `ISheet.GetProperties` 说 **seven** 却列 **8** 个名字且 `sameCustomPrp` 无定义（`…2` 说 eight 并补上定义，且名字是 `sameCustomProp`）· ② `IDrawingDoc` **5 处死链**（`IICreate*` 三条 · `IDrawngDoc` · `ISkethcManager`/`MakeSketchBlockSelected` · `1stAngleViews2` · `UnInsertBreakVertical`）· ③ `swLoftedBendFacetOptions_e` 只有 **4** 个成员，`swSegmentLength`/`swSegmentAngle` 两套源都没有（`DSegLength`/`DSegAngle` 的语义对得上 `swMaxSegmentLength`(2)/`swAngleBetweenSegments`(3)）⇒ ★ **抄的时候不要"顺手修正"**，官方文本要逐字保留 |
| B-6 | `GATE-FINAL.md` 的 **C6** + **C9** + **C4** + **C11** 四处附注 | ★ C6：把「三个 token 全仓只在 GATE-FINAL」改成「`file_sha256` 全仓 0 命中；`tree_delta` 实为仓内既有的 `verified_by` 用法（15 处，在 `scripts/sw_{curve_and_split,ref_geometry,surface_edit_ops,surface_ref_ops}.py`）；`unique_name` 仅命中一个测试函数名的子串」★ C9：把 `rows 509 · max 511` 标成「截至 D 轮」（**现在 512 · 514**，但 25/30/3/5/22 与两个集合**全部仍成立**）★ C4：记下 `11557` 与 `12123` 是**两个口径**（差值 566 = 每接口一个 `_overview`）★ C11：把「3 处」直接改成实测的「**16 处 / 5 个文件**」 |

### ★ C 级 · **不用管**（★ 4 条 · 我抽查判不成立 / 或已无对象可动）

| # | 位置 | 为什么不用管 |
|---|---|---|
| C-1 | `audit-06-features-C.md` #7（B 判**不成立**） | ★ 我确认 B 判对了：`scripts/sw_part.py` 里 `GetActiveSketch2` **只剩注释**（「★ 2026-10-03（接手轮）**换走后继入口** —— 原来是 `get_com_member(model, "GetActiveSketch2")`」）★ 官方 `GetActiveSketch2.md` 首行的 `Obsolete. Superseded by [[SketchManager::ActiveSketch]].` 逐字在 ⇒ ★ **仓里已修完**，这条审计条目**按原样留在档里即可**，不必回改 |
| C-2 | `audit-07-sketch-C.md` #1（B 判**不成立**） | ★ 同型：`scripts/sw_sketch_modify_ops.py` 的 `_active_sketch_name` 里 `GetActiveSketch2` **同样只剩注释** ⇒ ★ **不用管**。★ ★ 但同域 #2（`scripts/sw_sketch_edit.py` 的 `_seg_count`）**仍**是先 `GetActiveSketch2` 再回退 `ActiveSketch` ⇒ ★ B 的「#2 成立 / #1 不成立」这个**区分**必须保留，别把两条一起归掉 |
| C-3 | `audit-10-misc-C.md` #6（B 判**不成立**） | ★ `scripts/sw_review.py` 的 `GraphicsRedraw2` **零可执行调用**（只剩 docstring 里逐字引官方 Obsolete 行）⇒ ★ **已修完，不用管** |
| C-4 | D 的 C6 里「`tree_delta` 全仓只在 GATE-FINAL」那半句 | ★ **我判不成立**：`tree_delta` 在 `scripts/` 下有 **15 处**真实 `verified_by` 用法 ⇒ ★ ★ **不要按 D 的说法去「整改」仓** —— 仓里本来就该有它；★ 要改的只是 D 的**表述**（见 B-6），而 **C6「存疑」这个判定本身不必动**（`judge-registry.json` 的 4 条 `id` 里确实一个都对不上那 5 个枚举值） |

---

## 四 · ★ C 那份单独看（补两域的摘要）

| 项 | 钣金（拟 `api-02-sheetmetal.md`） | 工程图（拟 `api-05-drawing.md`） | **合计** |
|---|---|---|---|
| **成员数** | **20**（§一 表，逐条读过 20/20） | **43**（§一 表，逐条读过 43/43） | **★ 63** |
| 已读出**逐字调用序**的成员 | **4**（`CreateCustomBendAllowance` · `InsertSheetMetalBaseFlange2` · `InsertSheetMetalEdgeFlange2` · `InsertSheetMetalHem2`；另 `InsertConvertToSheetMetal` 的实参是从 base-flange 例子里抄到的） | **3**（`CreateSectionViewAt5` · `CreateDetailViewAt4` · `CreateRelativeView`，+ 各域 §2.8/§3.1 等散记） | ★ 钣金域的**可抄配方密度明显更高**（20 条里 4 条；工程图域 43 条里 3 条） |
| md 列了 `## Examples` 但**本轮未读**（⇒ 逐字调用序仍「查不到」） | **5**（`InsertSheetMetalBaseFlange2` 的另两个语言版 · `InsertSheetMetalLoftedBend2`（★ 该 `.md` 在本机**长度=1、空壳**）· `InsertSheetMetalGussetFeature3` 的三个 · `GetSheetMetalFolder` / `GetFlatPatternFolder` 各三个） | **3 族**（`CreateDrawViewFromModelView3` · `BreakView`/`UnBreakView` 的 `Create_Broken_View_Example_*` · `CreateDetailViewAt4`） | — |
| **成节的「查不到」清单** | ★ **有**：§2.12 **7 条**（含 6 个成员无 `## Remarks` 段 · `EdgeFlange` 13 个形参全 `No description` · `Hem2`/`Gusset3` 无 mark 数字 · 4 处调用序未读 · `ICustomBendAllowance.Type/KFactor` 未读 · `swSegmentLength/Angle` 不存在 · `swSheetMetalRelievObround` 拼写） | ✗ **没有成节清单** —— 散在 §3.1–§3.10 各成员表的「②`## Remarks`」「③例子」格里（如 `CreateAuxiliaryViewAt2` / `CreateDetailViewAt4` 现行版**都没有 Remarks 段**） | — |
| 「查不到」**出现次数**（全文 grep） | **58** 次 | **34** 次 | **96** 次（另 §〇 F1–F6 段 **4** 次 ⇒ 全文 **96** 次，分布在 **89** 行） |

### ★ 对这份的裁判意见

- ★ **成员数 63（20 + 43）站得住**：两份摘要在 §一 各自声明「逐条读过的 `.md`」= 成员数（20/20 · 43/43），★ 本人抽查的 6 处原文引用（`ISheet` 2 份、`IDrawingDoc` 5 处、`swLoftedBendFacetOptions_e` 1 份）**全部逐字复现** ⇒ ★ **没有编造的引文**。
- ★ **6 处「对不上」的性质要说清**：F1 是**已声明的证据挂错树**（仓内自己的错，要改）；F2/F3/F4 是**官方源自己的错**（★ 原样带进摘要，抄录时逐字保留，别"修"）；F5/F6 是**覆盖缺口与重复计数风险**（`InsertSheetMetalCornerTrim` 已被 `api-03-weldment.md` §8.1 抄过，**C 只做交叉引用没重抄** ⇒ ★ 无重复计数）。
- ★ **两份摘要的成熟度不对等**：钣金域有 §2.12 成节的「查不到」清单（7 条，可 grep）；**工程图域没有对应的一节** ⇒ ★ 建议在 `api-05-drawing.md` 落盘时补一节同格式的「查不到」清单（当前这 34 处散在 10 张成员表里），否则后续核账无法机器统计。

---

## 五 · ★ 我这一轮的边界声明

- ★ **没有跑 SolidWorks、没有跑 pytest、没有改这四份稿**；本文件是本次唯一写入。
- ★ 「成立 / 不成立」的判据是**回原文逐字复现**，不是「读起来合理」。
- ★ ★ **D 的 C9 我只复算了集合代数**（25 / 30 / 3 / 5 / 22 全部对），**没有**逐个核那份「22 条清单」的成员身份；★ **C 的 63 条成员我只抽了 6 条**逐字核，未逐条重核。
- ★ 4 份稿的**基准时点不同**（A/B/C/D 各写于不同时刻，`known-facts.md` 与 `verify-done/` 里后来又多了文件）⇒ ★ 凡涉及**计数**的结论（B-6 那四处）都标了「截至原轮」。
- ★ **被我判不成立的只有 1 条**（D-C6 的 `tree_delta` 半句）⇒ ★ **21 处「对不上」没有被推翻的**。
