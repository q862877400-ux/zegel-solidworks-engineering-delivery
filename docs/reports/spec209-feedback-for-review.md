# 规格 209 收口 · 反馈给高级模型（复核用）

> **文档性质**：这是一份**自足的复核输入** —— 不改任何代码，只把「做了什么 / 凭什么这么说 / 哪些我拿不准 / 请你裁什么」写成可核对的形式。
> **产出时间**：2026-10-06 · 仓库 `D:\AI\SW` · 规格落点 [specs/209-union-adopt-18/](../../specs/209-union-adopt-18/tasks.md)
> **一句话结论**（★ 措辞按**高级模型裁决 §7** 改写）：规格 209 的 **15 项工作均已完成本轮处置** —— 其中 **11 项 `verified`、4 项 `stitched`**，其余边界**按 `limitations` 记录**（★ 逐条见 §二）。**规格范围内由本轮引入的问题均已修复**（R11 违规 4 条 / 陈旧总数断言 7 处 / 无人值守基线 / 收集期导入失败 —— 见 §六）；**全量 pytest 仍有 18 条历史 / 跨线红点**，详见 §六。
> ★ **改这条的理由**：★ 原句「15 件活全部收口」容易被读成「**15 项全部验证通过 + 全仓测试绿**」——
> ★ 而实际是 `verified` / `stitched` 混在一起、且全量 pytest 未全绿 ⇒ ★ 必须把**两个数字**写出来 ✓

---

## 一、请你先看这三件事（最高信息量）

| # | 事项 | 我做了什么 | 为什么要你复核 |
|---|---|---|---|
| 1 | **官方示例的 `Preconditions` ≠ API 的硬前置** | 我按 `Add_Autoballoon_to_Face_Example_VB.md` 的 `Preconditions`（"a drawing **with a BOM table**"）**推断**过「没有 BOM 表就静默无效」，**真机把它否证了**（没有 BOM 表那格 **Δ=1**）| ★ 这条若成立，**官方示例的 `Preconditions` 段在本仓就只能当"例子的环境"读**，不能当契约。★ 这会**改变全仓读官方例子的方式**（尤其 `precondition_diff` 那 324 条，见 `docs/recon-206/pre-code-conflict-lookup.md`）⇒ **请你定这条能不能升为通用判读规则** |
| 2 | **`RecordLine` 的返回值不可用** | 官方 `## Remarks` 逐字说 *Text is only written to macros if macro recording is enabled* —— ★ 而**真机"未开录制"时它照样回 `True`** | ★ 我据此把该能力判 `stitched`（★ 只能到「成对调用可达」）。**请复核这个降级是否过严**：是否"返回值与回读都不足以判"就一律 `stitched` |
| 3 | **两处偏离裁决书的建议，我拍板没照做** | ① `centerline` **没有**与 `auto_center_marks` 合成一条工具；② `model_annotations` **落点从 `sw_drawing.py` 改成 `sw_drawing_create_missing.py`** | ★ 两条我都在 `tasks.md` 里写了可核理由（见 §四）。**请你判这两处偏离是否成立** —— 若你认为该照裁决书做，回退成本不大 |

---

## 二、交付清单（15 件，逐条可核）

★ 每条的**官方依据 / 真机读数 / 证据文件 / limitations** 都在 [tasks.md](../../specs/209-union-adopt-18/tasks.md) 对应条目下，`capabilities.yaml` 里是同源的结构化版本。

| 条 | 外部 idx | 结果 | 真机证据（`output/`） | 一句话 |
|---|---|---|---|---|
| B1 ×5 | 235+236 / 79 / 97 / 244 / 209 | **verified** | `union-adopt-b1-evidence.json` 等 | 真机建成并回读 |
| B2-1 | 336 `unfold` | **verified** | `spec209-unfold-fold.json` | 建出 `展开1` |
| B2-2 | 34 `balloon` | **verified** | `spec209-balloon.json` | 有没有 BOM 表**都**插得进去（各 Δ=1） |
| B2-3 | 52 `centerline` | **stitched** | `spec209-centerline.json` | 选区回读 **1**，而 `InsertCenterLine2` 回 `None`、Δ=0 |
| B2-4 | 175 `blank_sketch` | **verified** | `spec209-blank-sketch.json` | 隐藏/显示双向过 |
| B3-1 | 115+145 `edges/faces` | **verified** | `spec209-b3-entities.json` | 合并成一条工具；**Euler `V−E+F=2`** 回读 |
| B4-1 | 211 `macro_recording` | **stitched** | `spec209-macro-recording.json` | 返回值不可用（见 §一 #2） |
| B4-2 | 173 `hem` | **stitched** | `spec209-hem-diag.json` / `-units.json` | 五种形态**全回 `None`** |
| B4-3 | 181 `intersect` | **verified** | `spec209-intersect.json` | 建出 `相交1`；布尔 SafeArray **双向证实** |
| B4-4 | 155 `fold` | **verified** | `spec209-unfold-fold.json` | 建出 `折叠1` |
| B4-5 | 205 `model_annotations` | **stitched** | `spec209-model-annotations.json` | 可达 + 回读可用，但**夹具没有可插的标注** |

★ 收口时的仓态：**工具 448** · **`capabilities.yaml` 126 条**（verified 110 / stitched 14 / not_implemented 2）。

---

## 三、本轮新增的「官方 vs 真机」分歧（已记账到 `spec.md §五`）

★ 请重点看 **11 与 12** —— 它们不是"某条成员怎么调"，而是**读官方文档的方式**：

| # | 位置 | 官方说 | 真机是 | 若误读会怎样 |
|---|---|---|---|---|
| 7 | `IEdge` | —— | **没有 length 成员** | 会写出一个不存在的成员名 |
| 8 | `SetSelectedObjectMark(AtIndex, Mark, Action)` | 文档给了 Action | ★ Action **必须是 `swSelectionMarkSet`(0)**；传 `-1` **返回 false、不报错、mark 静默未设** | ★ **我曾据此得出"展开建不出来"的错误结论** |
| 9 | 钣金 FeatureData 长度 | 多处写"in meters" | ★ 是**文档单位（mm）** | 传 0.002 会建出 0.002 mm 的箔 |
| 10 | `ICustomBendAllowance.Type` | `## Remarks` 要求**最后设** | 一致；不照做会被覆盖 | 设置静默失效 |
| 11 | `InsertSheetMetalUnfold` 的 `mark 4` | `## Remarks` **没给 mark**；官方示例打了 `mark 4` | ★ **不给 `mark 4` 也建得出 `展开1`** | ★ 把示例当"必需" ⇒ 凭空一条强约束 |
| **12** | **官方示例的 `Preconditions` 段** | 示例说需要 BOM 表 | ★ **没有 BOM 表也插得进去** | ★★ **凭空给能力加一条不存在的前置** |

---

## 四、我拍板的偏离（请裁决）

| 偏离 | 裁决书原话 | 我没照做的理由 | 代价 |
|---|---|---|---|
| `centerline` 未与 idx 30 合并 | 「bunny 建议与 idx 30 `auto_center_marks` **合并成一条工具的两种模式**，我同意」 | 两条入口**入参形状不同**：本条形参可全标量；`auto_center_marks` 收的是**结构化 requirements 列表**（`[{"id","view","targets","count"}]`）⇒ `Param` 表达不了 ⇒ 硬合并会造出"一半参数对一半模式无意义"的工具 | 工具面多一条入口；★ 若你认为该合并，需先给 `requirements` 定一个能过 `Param` 的形状 |
| `model_annotations` 落点变更 | 「落 `scripts/sw_drawing.py`」 | `sw_drawing.py` **只有 29 行、是桥接壳**（`exec_module` 加载 subskill 再 `globals().update`）⇒ 往里加会被覆盖；★ 而带 `_iter_views`/`_sum_over_views`/`_delta` 的实现在 `sw_drawing_create_missing.py`，★ 裁决书自己要求"复用该文件已有的读侧助手" | 无（模块仍在 `scripts/` 白名单内）|
| `blank_sketch` 工具名 | 裁决书建议 `…_set_all_blanked` | ★ 那会**承诺并不存在的"all"语义** ⇒ 我用了 `solidworks_sketch_set_blanked` | 无 |
| 批测试的"绝对总数"断言 | —— | ★★ **这是我的设计缺陷**：我原来在每批测试里写 `assert len(all_specs()) == 443/444/…` ⇒ **每加一批就让前面所有批次全红**（★ 焦点测试看不见，全量才暴露）⇒ 已改成不可能因新增而变红，绝对数**只留一处** | 已修 |

---

## 五、我自己的错（`spec.md §六` 共 10 条，这里给最该看的四条）

1. **`bbox_changed` 曾是"空判据"**：`get_bounding_box` 回的是 **dict**，我却当序列迭代 ⇒ **恒为 `False`**（判据永远"没变"）。已改成读 `bb["min"]/["max"]`，并**新增区分 `None`（读不到）与 `False`（没变）**。
2. **`EditRebuild3` 经 `getattr` 会"执行"**：pywin32 下 `getattr(obj, "EditRebuild3")` 直接调用它 ⇒ 拿到的是 `bool`（恒真）。★ 我一度把它当成"绑定的方法"记错了形态。
3. **`SetSelectedObjectMark` 的 Action 传 `-1`**：返回 `false`、**不报错**、mark 静默未设 ⇒ ★ **我据此判过"展开这条能力建不出来"**（假结论）。
4. **空 Dispatch 形参不能传 Python `None`**（本仓**已知事实 33**）—— ★ 我在 `centerline` 那条**又踩一次**：`GetVisibleEntities2` 的组件形参传 `None` ⇒ 四种实体类型**全报"类型不匹配"**，★ **看着像"读不到"，实际是我传错了**。

★ 另一条**方法论**上的自查：`hem` 那条我**连续两种前置顺序、五种形态**去试（含"先打 CBA 再选边"的顺序修正）。按**事实 53**（同一启发式连续修补 ≥3 次就该停）我**停下了**，改成如实记负结论 + 写死下一步，★ 请你判这个"停"是否停对了。

---

## 六、全量 pytest：**18 failed / 2105 passed / 20 skipped（444.76 s）**

★ 首轮是 **38 failed + 7 errors**。修完的（**都是我造成的**）：

| 类别 | 是什么 | 结果 |
|---|---|---|
| **R11 违规 4 条** | `hem` / `model_annotations` / `center_lines` / `macro_recording` 的 `level=stitched` 却带了 `unattended` 授权 ⇒ R11 逐字禁止 | 已去掉；`test_unattended_equivalence` 从 **7 ERROR → 7 passed** |
| **"绝对总数"断言 7 处** | 见 §四 | 已改成 `>=`，绝对数只留 `test_server_wiring.py`（更新为 448） |
| **无人值守黄金基线** | 新增 11 条 verified 能力带 `unattended` ⇒ 基线不匹配 | 按它的用意**显式**更新并写日期说明 |
| **收集期导入失败 1 处** | `test_sw_part_sketch_selection.py` 的**桩**缺 `safe_get_com_member`（真模块后来加了它；★ 该文件注释里本就写着"桩要跟着真模块走"） | 从 **ERROR + 2 failed → 8 passed** |

**剩下的 18 条**（★ **我没有把 18 条全部逐条定性**，这里只列已定性的）：

| 红点 | 我的定性 | 依据 |
|---|---|---|
| 顺序污染（**一条根因，疑似吃掉多格**） | `test_sw_part_sketch_selection.py` **把假 `sys.modules["sw_connect"]` 泄漏给后续测试**（导入完不还原）| ★ `pytest tests/test_tool_specs_batch92.py` ⇒ **25 passed**；跟在它后面跑 ⇒ **成批 FAILED** |
| `tools/verify_union_349.py:112`（`check_negative_input_selfproof`）| **既有红**，非本次改动 | 文件自 `38bd4f3c` 起未改 |
| `test_rule2_length_suffix_is_enforced` | **非我** —— `solidworks_view_set_frame/top_px` 的豁免理由措辞 | 我没碰过 view frame |
| `test_sketch_slot_params` | **非我** —— 剥注释后解析不出 `CreateSketchSlot` 实参 | `git log -S` 指向阶段3/5 那条线 |
| `test_sw_connect_open_document` | **非我** —— 替身返回 `bool`（`'bool' object has no attribute 'get'`）| 同上 |
| `test_tool_specs_batch79` | **非我** —— 17 个宏工具没全进 specs | 同上 |

★ **请你判**：这 18 条里凡**非本次改动**的，是不是应当由**引入它们的那条线**负责，而不是在本规格里顺手改掉？（我按"不越界改别人的东西"处理了，只修了我自己造成的 + 那条桩。）

---

## 七、我明确**没做到**的（诚实边界，别当成了）

1. **`DSldWorksEvents::{BeginRecordNotify, EndRecordNotify}` 未接**（宏录制事件）—— 裁决书提到的三样里，我只做了 `RecordLine` + `RunCommand` 两样。
2. **裁决书 §一 第 2 条点名的缺口未补**：批量路 `AutoInsertCenterMarks2` **从未单独真机验证**（★ 单点 `InsertCenterMark3` 已实测阴性）。
3. **`hem` 只到负结论**：成员名/签名/5 个枚举**都核实正确**，但**真机上建不出**。下一步我写的是：用真实折弯件做夹具 / 试 Obsolete 的 `InsertSheetMetalHem` / 先 `InsertSheetMetalFold` 造出折弯。
4. **`centerline` 的官方前置只复现一半**：官方示例是**先选 `COMPONENT`、再按点选 `FACE`**（且视图来自**装配**），我只复现了"选实体"那半、夹具是**零件**视图 ⇒ ★ **结论限定在这条路径上**。
5. **`model_annotations` 是"数据相关"的失败**：我们的零件是**纯坐标画出来的**（一个尺寸都没有），而本仓的 `add_horizontal_dimension` **需要先选中实体**才建得出尺寸 ⇒ **夹具里没有可插的东西**。★ 这不等于能力不行。
6. **18 条全量红里，我只定性了 6 类**（见 §六）。

---

## 八、请你回答的问题（这就是"反馈"的落点）

1. **§一 #1**：官方示例的 `Preconditions` 能否升为通用判读规则（"例子的环境，不是 API 的契约"）？若可以，是否要回去复查 `precondition_diff` 那 324 条？
2. **§一 #2**：返回值与回读**都不足以判**时，是否一律 `stitched`？还是允许"返回值 + 语义前提都满足"算 `verified`？
3. **§四**：两处偏离裁决书（`centerline` 不合并 / `model_annotations` 改落点）**成立吗**？
4. **§五**：`hem` 那条"试到第 5 种形态就停"是否停对了？还是应当继续（例如换装配级夹具）？
5. **§六**：非本次改动的红点，是否应当**留给定性为"非我"的那条线**去修，而不是在本规格里顺手清？
6. **是否要我把 §三 的 12 条分歧里**属于"读官方方式"的那两条（11/12）**提到 AGENTS.md 级别**（那样每轮自动注入），而不是只留在规格的 `§五`？

---

## 八之二、裁决已收到（2026-10-06）与对应动作

★ 上面 §八 的 6 个问题**已经裁决**。★ 原话摘要与我的落地动作如下 —— ★ **本节是闭环记录，不是提问**：

| 项目 | 裁决 | 我的动作 |
|---|---|---|
| 示例 `Preconditions` 是否等于 API 前置 | **否**；作为**通用判读规则**升级，★ 但措辞加「除非 API / 实测证明」 | ✅ 写进 [docs/official-docs-first.md](../official-docs-first.md) **定则 ②** + 根 `AGENTS.md` 一行常驻令。★ 措辞**未**用"不是 API 契约"（太绝对），改按裁决原文 |
| `precondition_diff` 那 324 条是否全部复查 | **不需要**；先分**四类**，**优先 C 类**（官方未说明、代码曾自行推断） | ✅ 分类法写进**定则 ②** 末尾 |
| `RecordLine` 判 `stitched` | **正确** | ✅ 不改 |
| 「返回 True + 语义合理」能否 `verified` | **不能** —— 证据不足就 `stitched` | ✅ 落成 **L1–L5 证据阶梯**（见下） |
| `centerline` 不合并 | **成立** | ✅ 不改 |
| `model_annotations` 改落点 | **成立** | ✅ 不改 |
| `hem` 第五种形态后停止 | **本轮停止正确，≠ 最终能力否定** | ✅ 措辞改成「**在当前夹具与已验证调用路径下未能建成**」（`capabilities.yaml` + `tasks.md`）—— ★ 明确**不许**写「API 不支持」 |
| 18 条历史红点是否越界修 | **原则上不修**；★ **例外**：阻塞验收链的**测试基础设施**问题**可单独修** | ✅ 顺序污染那条按例外**单独**提交 `fix(test-isolation): …`（★ 未混进任何能力提交） |
| §三 的 11/12 是否进 `AGENTS.md` | **方法论进；具体 API 事实留 spec / evidence** | ✅ 只把**规则**写进 `AGENTS.md` 与两个"家"；★ 具体事实（`mark 4` 不必需 / 无 BOM 也能插 / 某接口返回值）**留在** `spec.md §五` 与 `capabilities.yaml` |

★★ **裁决新增的方法论（§九）：证据分层 L1–L5** —— 已落成**一处正文 + 两处指针**（★ 一事一家）：

| 级 | 证据形态 | 够 `verified` 吗 |
|---|---|---|
| **L1** | 文档说支持 | ✗ |
| **L2** | 代码能调用（签名 / 枚举对齐、import 得到、契约测试绿） | ✗ |
| **L3** | 成对调用可达（调用不抛异常） | ✗ |
| **L4** | 真机行为可观察 | △ 要配 L5 |
| **L5** | **真机结果可回读**（判据是**回读**，不是被调成员的返回值） | ✓ |

★ 正文：[docs/union-conventions.md](../union-conventions.md) 规则 4 的「证据阶梯」；
★ 常驻令：根 `AGENTS.md` §一 A1–A10 表后（1 行 + 指针）；★ `Preconditions` 规则的常驻令在 §「官方文档是第 0 步」。

## 八之三、仍待裁决（★ 5 条，带数字；其中 Q1/Q2 我自己不该拍）

★ 前 6 问已裁决并落地（见 §八之二）。★ 下面这 5 条是**落地之后才浮出来的新问题** ——
★ 每条都标了「**若你不答我会怎么做**」，所以它们**不阻塞**，只是不该由我单方面定。

### Q1（最要紧，牵动 **110 条 `verified`**）：L1–L5 是否**追溯**适用于仓里已有的 `verified` 条目？

- **背景**：`capabilities.yaml` 现在有 **110 条 `verified`**。★ 其中相当一部分是按**旧口径**判的 ——
  ★ 只看「调用没抛异常」或「返回值非 `None`」—— ★★ **而新裁的 L1–L5 恰恰否定了这两种判据**。
- **三个选项**：**(a) 只对新条目生效**（★ 后果：两套口径并存，A7「不许把 `stitched` 写成 `verified`」变成**时间相关**的）；
  **(b) 全量追溯审计**（★ 规模未知，可能很大）；**(c) 只追溯高风险子集** —— ★ 判据里**只出现返回值 / 只出现「不抛异常」**的那些。
- ★ **我建议 (c)**，做法：先出一份**只读扫描清单**（候选条目 + 每条现在的 `evidence` 原文），**不动任何 `level`**，再请你定改哪些。

### Q2：L1–L5 要不要**门禁化**？

- **实测**：`scripts/check_union_conventions.py` 里**没有任何**回读 / 证据等级的检查 ⇒ ★ 现在它**只是纪律文本**。
- **难点（要你权衡）**：★「判据是不是回读」在**静态上几乎判不了**（要判就得读探针代码的语义）。
- **选项**：**(a) 只留纪律**；**(b) 弱门禁** —— 例如 `verified` 条目的 `evidence` 文本里必须出现可 grep 的**证据词**
  （「回读」/ `Get*Count` / 「增量」…），否则报红。
- ★ **我建议 (b)**（★ 它能抓住「只写了一句『调用成功』」的条目），★ 但**有假阳性风险**（措辞不同就误伤），**要不要上请你定**。

### Q3：324 条 `precondition_diff` 的 **C 类复查归哪个规格**？

- 裁决说「先分类筛 C」，★ 但**没定**：① 它是不是**一个新规格**；② 复查发现「当年推断错了」**要不要降那些条目的 `level`**（★ 直接接到 Q1）。
- ★ **若你不答**：我先产出**只读的分类清单**（A/B/C/D 四类计数 + C 类逐条列名），**不改任何东西**，等你定要不要开规格。

### Q4：测试隔离的**规模与边界**

- **实测**：仓里 **42 个测试文件**装了 `sys.modules[...]` 替身；★ 我修的只是**其中会泄漏的那一个**。
- **问**：这算「**阻塞验收链的基础设施**」（按例外可修）还是「**历史技术债**」（不修）？★ 若修，是**一次性统一**
  （加一个共享的 `install_stub_modules()` 上下文管理器）还是逐处改？
- ★ **若你不答**：我先只读扫出「**装了不还原**」的清单，再一次性用共享 helper 收口，**单独**成 `fix(test-isolation)` 提交。

### Q5：规格 209 的两项「未接」归谁？

- ① `DSldWorksEvents::{BeginRecordNotify, EndRecordNotify}` —— ★ 裁决书原文提到三样（`RecordLine` / `RunCommand` / **事件**），我只做了**两样**；
- ② 裁决书 §一 第 2 条点名的 `AutoInsertCenterMarks2` **批量路单独验证**。
- **问**：补进规格 209，还是记为**范围外**另开一件？
- ★ **若你不答**：两条都**照实留在** `tasks.md` 的未完成项里（★ 不静默丢掉）。

---

## 九、可复现路径（你自己跑一遍就能核对）

```powershell
cd D:\AI\SW
# 每件活的真机证据（★ 全程护栏，0 弹窗）
python -u tools/sw_guard.py --timeout 900 -- python tools/probe_spec209_b2_balloon.py
python -u tools/sw_guard.py --timeout 900 -- python tools/probe_spec209_b4_intersect.py
# 收尾链（生成器 + release_check + 聚焦测试）
pwsh -File tools/round_chain.ps1 -Tests tests/test_tool_specs_batch97.py
# 全量（★ 只在发布前 / 改了门禁本体时跑：约 7.5 分钟）
python -m pytest -q
```

★ 逐条读数在 `output/spec209-*.json`；★ 每条能力的 `level` / `evidence` / `limitations` 在 `capabilities.yaml`（含"未验"分支）。

---

## 十、提交记录（按路径提交，逐个可 `git show`）

| commit | 内容 |
|---|---|
| `6633aa3c` | B4-1 原生宏录制（idx 211） |
| `a63eb80` | 收口：修 R11 违规 + 陈旧总数断言 + 无人值守基线 |
| `5a4ae7b` | 收口（续）：修收集期导入失败 + 定性顺序污染 |
| `9d04335` | 收口：tasks.md（SC-3 结果 + SC-4 剩余红点） |

★ 更早的 B2/B3/B4 各条提交见 `git log --oneline`（`1cbf957e` 相交 · `be54d2b1` 气泡 · `18cad05` 中心线 · `8b1c6ae6` 模型标注 · `069a1ed9` 展开/折叠/卷边 …）。
