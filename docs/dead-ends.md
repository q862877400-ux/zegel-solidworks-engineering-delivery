# 已走死的路（★ 开工前该扫一遍）

> ⚑ **本文件由 `tools/gen_dead_ends.py` 从 `capabilities.yaml` 生成** —— 不要手改。
> ★ 它只挑**表示「试完了 / 走不通 / 有硬限制」**的 `limitations`，按能力分组。
> ★★ **为什么有它**：2026-10-02 轮 359–362 我在 `revolve_boss` 的轴上**重走了一遍**
> 前人早已走死的路（轮 153/155 记的「6 种选法全部失败」）—— 而结论**就在那份清单里**。
> 轮 35 的定则：**动手核一条路之前，先读该能力的 `limitations`**。

## 统计

| 口径 | 数 |
|---|---|
| 「死路」条目 | **45** |
| 涉及能力 | **28** |

## 逐条（★ 按能力分组；等级 = 该能力当前等级）

### `animation_export`（stitched）

- ⚠ **`AGENTS.md §九.4`：需要用户提供的东西 ⇒ 停下报告，不自行拍板。**

### `costing`（verified）

- ⚠⚠ **本条的入口问题曾被写错、并因此长期停在 `stitched`**：旧文写「CostManager 由 **Composer 加载项**给出，**本机没装 Composer**，ProgID 查不到 ⇒ 本模块接收调用方传入的对象」。**两条硬证据推翻**：① 官方反射里**有** `IModelDocExtension::GetCostingManager()`；② 注册表里**有** `swcCostingAddin.SwcAddin`（`.34`）等 8 个 ProgID ⇒ **Costing 加载项本机装了**。ⓘ **「4 个 ProgID 全返 None」这个观察是对的**，但**结论「所以拿不到」是错的** —— `GetAddInObject` 本来就不是正解。**⇒ 把「某条路走不通」写成「对象拿不到」，会让模块放弃唯一的正解。**

### `costing_readback`（verified）

- ⚠ `list_bodies` 的实体名回 `'?'` ⇒ ★ 那个 body 对象上取 `Name` 取不到 ⇒ **按名字读**那条路在本机走不通（★ 要改用索引）

### `declarative_hole_creation`（verified）

- | 230 | **一个错误的注释导致了一个真 bug** —— 而它一次解开了两个"谜"（2026-10-01，轮 298）。 ## 一、★★★ 真凶：单位约定写错了（★ 写在注释里） ``` ★ `_point_from_selection` 的注释写着： > ★ **单位** —— 建孔函数的 `center` 要**米**（★ `sw_connect.mm()` 的 docstring 写明「毫米转米」） ⇒ ★★ **于是本函数用 `mm()` 把选区点换算成**米****（★ 而选区点本身是**毫米**，轮 267 三点对照确证）。 ★★ **而真机把那条注释推翻了**： · ★ **用毫米调 `create_countersink_hole` ⇒ 2/2 PASS**（★ 树 7→10 · 10→13）； · ★ **用米调 ⇒ 报「创建圆草图失败: 沉头孔_通孔」**（★ **因为它变成了**亚微米圆****）。 ★ 而链条是：★ `_circle_cut` ⇒ `sketch_circle(model, center[0], center[1], diameter / 2.0)` ⇒ ★★ **`sketch_circle` 是 `sw_part` 的**，★ **而那个模块的单位**就是毫米**（★ 它自己的 docstring 明写） ⇒ ★★★ **所以整条链都是毫米** ⇒ ★ **那条注释错了**。 ``` ## 二、★★★★★ 修法与结果 ``` ★ 修：★ `_point_from_selection` **去掉 `mm()`**，★ 直接回毫米（★ 并**把那条错注释换成真机证据**）。 ★★ **真机复跑（★ 每个孔型都在**全新文档**里）**： `through` ✓ · `blind` ✓（7→9）· `counterbore` ✓（7→11）· **`countersink` ✓（7→10）** · **`semicircular_slot` ✓（7→9）** ⇒ ★★★★ **PASS 5/5** ✓ ⇒ ★★★ **两个"谜"一次解开**： ① ★ **`countersink` 的"失败点漂移"** = **亚微米圆**（★ 米/毫米混用 ⇒ 偶尔建得出、偶尔建不出）； ② ★★ **`semicircular_slot` 的 `<unknown>.SketchManager` + "树 →0"** = ★ **同一个根因** —— ★ **那个失败**破坏了文档对象**** ⇒ ★★★ **即事实 228 的"对象失效"的**原因**就是这个单位 bug**。 ★ ⚠ **而这个 bug 之前**没暴露**的原因**：★ `through` / `blind` / `counterbore` **恰好在亚微米尺度上 也能建出来** ⇒ ★★ **它们同样错，只是没暴露** —— ★★★ **所以"3/5 通过"那个结果具有**误导性****： ★ **它看起来像"3 个孔型对、2 个不行"，★ 而真相是"5 个都用错了单位，★ 其中 3 个碰巧能跑"**。 ``` ## 三、★ 定则 ``` ★★★ **一条"约定"写在注释里，就成了一条**没人验证的断言**** —— ★ 本处的注释写"建孔函数要米"，★ **它是错的**，★ 而**包装照着它做了换算** ⇒ **bug 产生**。 ⇒ ★★ **可操作判据**：★ 注释里写**单位**时，**必须附一条能跑的核查命令或真机证据** （★ 本处正确的写法是：★「★ 真机（轮 298）：用毫米调该函数 2/2 PASS ⇒ **它吃毫米**」）。 ⇒ ★★★ **而这条与项目已有的"规则 2"（换算只在边界做一次）**不冲突但更严**** —— ★ 规则 2 管**参数名**（`_mm` / `_deg`），★ **而它不管"内部约定是谁说了算"**。 ★★ **"部分通过"是最容易骗人的结果** —— ★ 本处 **3/5** 看起来像"3 个 API 可用、2 个不行"， ★ **而真相是"5 个都错，3 个碰巧能跑"** ⇒ ★★ **所以"通过"也要问"它是**怎么**通过的"** —— ★ **若参数差 1000 倍还能过，那说明它落在一个"能容忍 1000 倍误差"的区间里**， ★★ **而那通常是**亚微米 / 超大**这种"不真实"的区间**（★ 与事实 202 的"有副作用的失败"同族： ★ **一个反常的通过，和一个反常的失败一样值得查**）。 ``` **依据**：`output/countersink-mm-probe.json`（★ 毫米 2/2 PASS）· `output/hole-units-fixed-evidence.json`（★ **PASS 5/5**）· `output/countersink-diag-probe.json`（★ 米 ⇒ `创建圆草图失败`）· `output/slot-direct-probe.json`（★ 对象失效）· `scripts/sw_hole_features.py` 的 `_point_from_selection`（★ 修后的注释）· `scripts/sw_part.py` 的 `sketch_circle`（★ 毫米）· 事实 202 / 227 / 228 / 229
- ★★★★★ 2026-10-01（轮 297）**`countersink` 查出一条比"失败"更有信息量的结论：它的失败点**会漂移****： ★ **两次真机（同机、同流程、同一个调用）给出两个不同的报错点**： · **轮 269/296**：★ `RuntimeError: 无法按圆心和半径找到沉头孔入口圆边` （★ 那在 `_find_hole_entry_edge`，★ 即"通孔已建成、找不到它的入口圆边"）； · **轮 297**：★ `RuntimeError: 创建圆草图失败: 沉头孔_通孔` （★ 那在 `_circle_cut`，★ 即**更早一步**、★ 而**树 7 → 7**（★ 什么都没建））。 ⇒ ★★★★ **所以 `countersink` 的失败**不稳定**** —— ★★ 而**"不稳定"比"失败"信息量更大**： ★ **一个稳定的失败指向一个固定的前置不满足**；★ **一个漂移的失败指向"状态残留"** （★ 即：★ 同一个调用在不同次运行时**看到不同的初始状态**）。 ★★ **而这条也修正了我上一轮的推断**：★ 我上一轮从"报错在 `_find_hole_entry_edge`"推出 "差别在倒角那一步"⇒ ★ **而这次它压根没走到那里** ⇒ ★ **所以那个推断**不成立****。 ★ **本轮顺带做的一件事（★ 留着，★ 它下次会有用）**：★ 给 `_find_hole_entry_edge` 装了 **逐环诊断**（★ 旧版 `except Exception: continue` **把"断在哪一环"吞掉了** —— ★ 七种可能只报一句"找不到"）⇒ ★★ **现在失败时会带回** `bodies / faces / edges / curves / circles / params_ok / target / radius / first_error`。 ⇒ ★★ **判定逻辑**一字未改**（★ 仍然找同一条边、同样的容差）· ★ 只加诊断** —— ★ 而那正是本项目一贯要防的"静默吞错"（★ 事实 185/187/198 一族）。 ★ **下一步线索**：★ **查 `_circle_cut` 为什么会在"新建文档 + 建好底板"之后报"创建圆草图失败"** —— ★ 而**那个组合本该是最干净的初始状态**（★ 所以"状态残留"这个解释本身也要被打问号）· ★★ **另一个可能**：★ **`_circle_cut` 与 `_find_hole_entry_edge` 对"哪一步先失败"的**判定**不同** （★ 如 `_circle_cut` **其实建成了**、★ 而它**返回的名字**对不上 ⇒ ★ 报"失败"） ⇒ ★★★ **那要用逐环诊断去问**（★ 而本轮那个诊断**没被触发**，★ 因为失败在更早一步）。

### `drawing_view_operations`（verified）

- ★★★★★ 2026-10-01（轮 293）**真机抓到三处同类错 → 已修 → 拿到视图级证据**： · ★ **真因**：`get_view_scale` / `set_view_scale` 都调 **`Scale`** —— ★ **而 `IView` 上**没有那个成员****。 ★ 真机表现：★ `AttributeError: <unknown>.Scale`（★ **事实 36 的形态**）。 · ★★ **而真名早就被记下**：★ 同文件的 `get_scale_decimal` 的 docstring 写着「⚑⚑ **更正**：初稿调的是 `GetScaleDecimal`，该成员在 `IView` 上**不存在** —— 反射实测的真实成员是 `ScaleDecimal`（零参属性）， ★ **与同族的 `ScaleRatio` / `UseSheetScale` / `UseParentScale` 同形**」 ⇒ ★★★ **即：真名 `ScaleRatio` 早就写在注释里，而那两个函数没跟着改**。 · ★★★ **官方确证**（`C:\swapi\types\IView\ScaleRatio.md`）：★「Gets or sets the scale of the drawing view, **returning the results in ratio format (n:n)**」· **Returns: Array of 2 doubles** · ★「This property and `IView::ScaleDecimal` contain **the same information**, but use the value in a different way」⇒ ★★ **所以**：① 真名 `ScaleRatio`；② 它回**两个 double**（★ 不是单个 float）。 · ★ **已修**：★ 新增 `get_view_scale_ratio(view)`（★ 回 `(numerator, denominator)`）· ★ `get_view_scale` 改为**由它算**（第 1 个 / 第 2 个）· `set_view_scale` 改走 `ScaleRatio`（按 `n:1` 写）。 · ★★★★ **真机复验（有视图的图 · 3 个视图 `工程图视图1/2/3`）**： · `list_drawing_views_report` ⇒ **`{ok: true, count: 3}`** ✓ · `collect_view_evidence_report` ⇒ **`{ok: true, count: 3}`** ✓ · `get_view_scale_report("工程图视图1")` ⇒ ★★ **`{ok: true, scale: 0.002, scale_decimal: 0}`** ✓ （★ **即 `ScaleRatio` **确实取到了**** —— 而 `0.002` 的**语义待查**：★ 它不像"1:1"该有的 1.0， ★ 可能是"两个数"里的第 1 个被当成了比例 ⇒ ★ **待核**） · ⚠ `set_view_scale_report` ⇒ **仍 `ok: false`**（★ `before/after/asked` 全 `null`）⇒ ★ **待查** · ★★★ **造"有视图的图"的做法（★ 本轮 §5.0 的收获）**：★ 建零件 → 保存 → 新建工程图 → ★ **`sw_drawing.create_standard_views(drw, part_path)`**（★ 回 `True` ⇒ 图里出现 **3 个视图**）。 ★★ **而 `create_standard_views_with_projection(drw, part_path, "first_angle")` 回 `blocked`** （★ `error_code: DRAWING_PROJECTION_API_UNAVAILABLE` · ★ `method: CreateFirstAngleViews2`） ⇒ ★ **所以那条路走不通**（★ 而它**如实报了 blocked + 错误码** —— ★ 好形态）。 · ★★ **一条探测方法的错（★ 需更正上一轮的说法）**：★ 我上一轮说「`scripts/sw_drawing.py` 有 **0 个公开函数** ⇒ 所以没有插视图入口」⇒ ★★★ **那是**假报****：★ `sw_drawing` 实际有 **57 个 callable**， 含 `add_view` / `add_detail_view` / `add_section_view` / `create_standard_views*` / `generate_drawing_from_spec`。★ **错因**：★ 我的探测用 `getattr(f, "__module__", "").endswith(m)` 过滤 —— ★ **而"从别处 import 进来的函数"不满足它** ⇒ ★★ **所以"某模块有 0 个公开函数"这类结论， 必须先核探测方法**（★ 用 `__module__` 过滤会漏掉被 import 进来的）。

### `geometric_tolerance`（stitched）

- ★★★ **2026-10-01（轮 166）穷尽式结论**：`IGtolFrame.AddIndicator` 那半 —— `tools/probe_gtol_indicator_matrix.py` 把 `BorderType`(0..3) × `TolType`（官方 Remarks 允许的 **5 个**：20/22/21/25/13）= **20 组全试**，而**每一组的帧都拿到了**（`GetFrame(1)` 非 NULL）⇒ **20 组全返回 `False`**。⇒ ★ 不是「取值不对」（5 个 tol 都在官方允许清单里），而是**这条后端到不了这一个成员**（与事实 47 那族同类）。★ 所以拆出 `gtol_insert`（**verified**，覆盖「新建 GTol + 帧路径」）；本条目**仍为 `stitched`**（含「加指示符」那半，它在**本机到不了**）。
- ★★ **2026-10-01（轮 120）真机实测：本能力「一半可用、一半到不了」**：
- ❌ **`add_gtol_indicator` 真机到不了** —— 量到的事实（均在**新零件**上）：`GetFrameCount()` 新建后 = **1**；`AddFrame()` 返回 **False**；`GetFrame(0)` / `(1)` / `(2)` **全 None**；`CanConvertFormat()` → True、`ConvertFormat()` → **0（成功）**，转换后 `GetFrameCount()` **掉到 0**，而 `GetFrame(1)` / `(2)` **仍全 None**。⇒ **「2022 格式的帧路径」在本机（SW 2026 SP4.1 / pywin32 迟到绑定）上取不到帧。**
- ⚠ **按已知事实 53 停手**：同一处已试 **3 次**（补帧 / 直接取 / 先 `ConvertFormat`），**不再变着法试**。本模块**保留** `add_gtol_indicator`（**不删**）—— 它是**可复算的证据**，也便于别的后端（如 `comtypes`）上重试；但它**当前不可用**。
- ★ **为什么仍走 `AddIndicator` 而不是 `SetFrameSymbols2`**：官方明写后者「valid only if this Gtol was created in a version of SOLIDWORKS **earlier than 2022**」，且它的符号参数是 `LibraryName-SymbolName` 形态的**字形串**（官方文档里显示为空）⇒ **文本协议传不了**。⚠ 但实测表明**前者在本机也到不了** —— 两条路**都不通**。

### `gtol_insert`（verified）

- ⚠ **不含**「加公差指示符」那一步 —— 它在**本机到不了**（见 `geometric_tolerance` 条目）
- 轮 277 填实（空壳）：sw_gtol.insert_gtol(model) **零参**。真机 tools/verify_gtol_smoke.py **3/5**（insert_gtol 那半通过、加指示符那半到不了 => 见 geometric_tolerance 条目）

### `headless_open_format_writing`（verified）

- ⚠ **2026-10-01 实测（轮 77）：本机没有 `OCP` / `cadquery` / `trimesh`**（`importlib.util.find_spec` 全为 `None`，磁盘上也没有 OCP 目录）。⇒ 本条 limitations 里涉及 **headless-occt** 的声明**在当前这台机器上无法复现**；`tests/` 里对 OCP 后端的用例**都 monkeypatch 掉了后端**（验的是 MCP 层传参，不是 OCP 真跑），`tests/test_headless_cad_writer.py` 更是**显式把 OCP 伪装成不可用**来测降级路径。⇒ 这些声明**不是假的**（代码里确有该路径、且降级行为有测试），但**其运行证据不在本机** ——按铁律 5 如实标注，等装了 `cadquery-ocp` 的机器上重跑才能升级为当机证据。

### `helix_and_spiral`（verified）

- ⚠ 官方 `GetLastFeatureAdded` 的 Remarks 提醒：它**可能返回子特征**（配合、工程图视图等）—— 本模块的用途（取刚建的螺旋线）下未遇到，但**未穷尽验证**。

### `holes_and_finishing`（verified）

- | 230 | **一个错误的注释导致了一个真 bug** —— 而它一次解开了两个"谜"（2026-10-01，轮 298）。 ## 一、★★★ 真凶：单位约定写错了（★ 写在注释里） ``` ★ `_point_from_selection` 的注释写着： > ★ **单位** —— 建孔函数的 `center` 要**米**（★ `sw_connect.mm()` 的 docstring 写明「毫米转米」） ⇒ ★★ **于是本函数用 `mm()` 把选区点换算成**米****（★ 而选区点本身是**毫米**，轮 267 三点对照确证）。 ★★ **而真机把那条注释推翻了**： · ★ **用毫米调 `create_countersink_hole` ⇒ 2/2 PASS**（★ 树 7→10 · 10→13）； · ★ **用米调 ⇒ 报「创建圆草图失败: 沉头孔_通孔」**（★ **因为它变成了**亚微米圆****）。 ★ 而链条是：★ `_circle_cut` ⇒ `sketch_circle(model, center[0], center[1], diameter / 2.0)` ⇒ ★★ **`sketch_circle` 是 `sw_part` 的**，★ **而那个模块的单位**就是毫米**（★ 它自己的 docstring 明写） ⇒ ★★★ **所以整条链都是毫米** ⇒ ★ **那条注释错了**。 ``` ## 二、★★★★★ 修法与结果 ``` ★ 修：★ `_point_from_selection` **去掉 `mm()`**，★ 直接回毫米（★ 并**把那条错注释换成真机证据**）。 ★★ **真机复跑（★ 每个孔型都在**全新文档**里）**： `through` ✓ · `blind` ✓（7→9）· `counterbore` ✓（7→11）· **`countersink` ✓（7→10）** · **`semicircular_slot` ✓（7→9）** ⇒ ★★★★ **PASS 5/5** ✓ ⇒ ★★★ **两个"谜"一次解开**： ① ★ **`countersink` 的"失败点漂移"** = **亚微米圆**（★ 米/毫米混用 ⇒ 偶尔建得出、偶尔建不出）； ② ★★ **`semicircular_slot` 的 `<unknown>.SketchManager` + "树 →0"** = ★ **同一个根因** —— ★ **那个失败**破坏了文档对象**** ⇒ ★★★ **即事实 228 的"对象失效"的**原因**就是这个单位 bug**。 ★ ⚠ **而这个 bug 之前**没暴露**的原因**：★ `through` / `blind` / `counterbore` **恰好在亚微米尺度上 也能建出来** ⇒ ★★ **它们同样错，只是没暴露** —— ★★★ **所以"3/5 通过"那个结果具有**误导性****： ★ **它看起来像"3 个孔型对、2 个不行"，★ 而真相是"5 个都用错了单位，★ 其中 3 个碰巧能跑"**。 ``` ## 三、★ 定则 ``` ★★★ **一条"约定"写在注释里，就成了一条**没人验证的断言**** —— ★ 本处的注释写"建孔函数要米"，★ **它是错的**，★ 而**包装照着它做了换算** ⇒ **bug 产生**。 ⇒ ★★ **可操作判据**：★ 注释里写**单位**时，**必须附一条能跑的核查命令或真机证据** （★ 本处正确的写法是：★「★ 真机（轮 298）：用毫米调该函数 2/2 PASS ⇒ **它吃毫米**」）。 ⇒ ★★★ **而这条与项目已有的"规则 2"（换算只在边界做一次）**不冲突但更严**** —— ★ 规则 2 管**参数名**（`_mm` / `_deg`），★ **而它不管"内部约定是谁说了算"**。 ★★ **"部分通过"是最容易骗人的结果** —— ★ 本处 **3/5** 看起来像"3 个 API 可用、2 个不行"， ★ **而真相是"5 个都错，3 个碰巧能跑"** ⇒ ★★ **所以"通过"也要问"它是**怎么**通过的"** —— ★ **若参数差 1000 倍还能过，那说明它落在一个"能容忍 1000 倍误差"的区间里**， ★★ **而那通常是**亚微米 / 超大**这种"不真实"的区间**（★ 与事实 202 的"有副作用的失败"同族： ★ **一个反常的通过，和一个反常的失败一样值得查**）。 ``` **依据**：`output/countersink-mm-probe.json`（★ 毫米 2/2 PASS）· `output/hole-units-fixed-evidence.json`（★ **PASS 5/5**）· `output/countersink-diag-probe.json`（★ 米 ⇒ `创建圆草图失败`）· `output/slot-direct-probe.json`（★ 对象失效）· `scripts/sw_hole_features.py` 的 `_point_from_selection`（★ 修后的注释）· `scripts/sw_part.py` 的 `sketch_circle`（★ 毫米）· 事实 202 / 227 / 228 / 229
- ★★★★★ 2026-10-01（轮 297）**`countersink` 查出一条比"失败"更有信息量的结论：它的失败点**会漂移****： ★ **两次真机（同机、同流程、同一个调用）给出两个不同的报错点**： · **轮 269/296**：★ `RuntimeError: 无法按圆心和半径找到沉头孔入口圆边` （★ 那在 `_find_hole_entry_edge`，★ 即"通孔已建成、找不到它的入口圆边"）； · **轮 297**：★ `RuntimeError: 创建圆草图失败: 沉头孔_通孔` （★ 那在 `_circle_cut`，★ 即**更早一步**、★ 而**树 7 → 7**（★ 什么都没建））。 ⇒ ★★★★ **所以 `countersink` 的失败**不稳定**** —— ★★ 而**"不稳定"比"失败"信息量更大**： ★ **一个稳定的失败指向一个固定的前置不满足**；★ **一个漂移的失败指向"状态残留"** （★ 即：★ 同一个调用在不同次运行时**看到不同的初始状态**）。 ★★ **而这条也修正了我上一轮的推断**：★ 我上一轮从"报错在 `_find_hole_entry_edge`"推出 "差别在倒角那一步"⇒ ★ **而这次它压根没走到那里** ⇒ ★ **所以那个推断**不成立****。 ★ **本轮顺带做的一件事（★ 留着，★ 它下次会有用）**：★ 给 `_find_hole_entry_edge` 装了 **逐环诊断**（★ 旧版 `except Exception: continue` **把"断在哪一环"吞掉了** —— ★ 七种可能只报一句"找不到"）⇒ ★★ **现在失败时会带回** `bodies / faces / edges / curves / circles / params_ok / target / radius / first_error`。 ⇒ ★★ **判定逻辑**一字未改**（★ 仍然找同一条边、同样的容差）· ★ 只加诊断** —— ★ 而那正是本项目一贯要防的"静默吞错"（★ 事实 185/187/198 一族）。 ★ **下一步线索**：★ **查 `_circle_cut` 为什么会在"新建文档 + 建好底板"之后报"创建圆草图失败"** —— ★ 而**那个组合本该是最干净的初始状态**（★ 所以"状态残留"这个解释本身也要被打问号）· ★★ **另一个可能**：★ **`_circle_cut` 与 `_find_hole_entry_edge` 对"哪一步先失败"的**判定**不同** （★ 如 `_circle_cut` **其实建成了**、★ 而它**返回的名字**对不上 ⇒ ★ 报"失败"） ⇒ ★★★ **那要用逐环诊断去问**（★ 而本轮那个诊断**没被触发**，★ 因为失败在更早一步）。
- ⚑ 2026-10-01（轮 125）**再把 3 个孤儿接上**（上轮接了 1 个）—— `list_fastener_types` / `list_fastener_table_types` 已可用；`get_fastener_table` **到不了**（见下）。★ 链路：标准（15）→ 紧固件类型（14）→ 表类型（`[0,1,2]`）。
- ✅★★ **2026-10-03（轮 499）真机推翻了上一条的「到不了」定性** —— `GetFastenerTable` **能调**，而当年只是**包装形态选错了一个类型标记** ⚠ ★ **官方签名**：`System.bool GetFastenerTable(String StandardName, int FastenerID, int TableID, **IHoleDataTable& HoleTable**)`。 ★★ **真机逐形态实测**（SW 2026 SP4.1，结论与 `out_i4` 那族**完全对偶**）： `VARIANT(VT_BYREF | VT_DISPATCH, None)` ✓ **通过**（返 `False` = “没查到该表”） `VARIANT(VT_BYREF | VT_VARIANT, None)` ✗ 类型不匹配（第 4 参）← **当年试的就是这个** `VARIANT(VT_DISPATCH, None)` ✗ 类型不匹配（第 4 参） 裸 `None` ✗ 类型不匹配（第 4 参） ★★ **定则：`out` 参数一律「`VT_BYREF | VT_<该出参的类型>`」**——★ 而**不是** `VT_VARIANT`、也**不是**省掉 `BYREF` ✓ ★ 新增包装：`scripts/sw_connect.py` 的 **`out_dispatch()`**（`out_i4()` 的对偶，★ 已真机验证通过）。 ⚠ **仍未查**：那次返 `False` 是**参数 / 前置**问题（`("ANSI Inch", 0, 0)` 可能不对）⇒ ★ 要拿到真实存在的表才能验到 `True`。

### `loft_and_sweep`（verified）

- ★★★ 2026-10-01（轮 313）**本条是「四家有我们没有」里**核实的真缺****： ★ 全仓 grep `loft` ⇒ **工具 0 · 函数 0**（`sw_api_sldworks` 反射表除外），`sweep` 同样 0。 ★ 而**放样与扫描是 SolidWorks 最基本的两种特征**（★ 与拉伸 / 旋转并列）—— ★ 我们有拉伸、旋转、肋、抽壳、圆顶，**就是没有这两种**。 ★ 四家并集（349）里正有 **`loft`**（★ Slacker-LLC 提供）与 `sweep`。 ★★ **判据已换成硬的**（2026-10-01 轮 314）：真机定出 **放样特征 `GetTypeName2()` 回 `Blend`**（★ 对照拉伸回 `Extrusion`）， ★ 本包装现在**要求类型名 = `Blend`**（★ 它比"体积期望"可靠： 体积依赖我造几何的能力，★ 而类型名只依赖 API 对不对）。 ⚠ **而体积仍未验**： ★★ **扫描（轮 315）**：★ 入口是 `CreateDefinition(swFmSweep=17)` → `ISweepFeatureData` → `CreateFeature` （★ `InsertProtrusionSwept*` 整族已被 SOLIDWORKS 2018 标为 **obsolete** —— 官方 Remarks 原文）。 ★ mark：**轮廓=1 · 路径=4** · 引导线=2 · 方向向量=128（官方专文）。 ⚠ **官方硬约束**：路径的**起点必须落在轮廓所在平面上** —— 真机上违反它就建不成（★ 本次 `Right Plane` 那一例就是）。 ⚠ `AccessSelections(model, 空Dispatch)` 在本机报 **`0x80010105`**（★ 事实 47 的后端限制） —— ★★ **而它非必需**：真机上它报错时**特征仍然建成**。

### `mold_parting_geometry`（stitched）

- ★★ 2026-10-03（轮 392）`insert_shut_off_surface` 已试三次（无孔 / 有孔 / 孔+分型线+分型面）⇒ 都回 true 而特征树不变 ⇒ ★ 穷尽式结论：不是缺前置，而是「没有可关的断面」（★ 假设：孔需穿过分型面）。★ 不再换条件试（事实 53）。★ 下一步只剩 `insert_core_cavity_solids` —— 它要一整条链（分离成型芯/型腔片体 + 建模坯草图），留作单独一轮。

### `mold_tools`（stitched）

- ⚠ **2026-10-01 实测（轮 77）：本机没有 `OCP` / `cadquery` / `trimesh`**（`importlib.util.find_spec` 全为 `None`，磁盘上也没有 OCP 目录）。⇒ 本条 limitations 里涉及 **headless-occt** 的声明**在当前这台机器上无法复现**；`tests/` 里对 OCP 后端的用例**都 monkeypatch 掉了后端**（验的是 MCP 层传参，不是 OCP 真跑），`tests/test_headless_cad_writer.py` 更是**显式把 OCP 伪装成不可用**来测降级路径。⇒ 这些声明**不是假的**（代码里确有该路径、且降级行为有测试），但**其运行证据不在本机** ——按铁律 5 如实标注，等装了 `cadquery-ocp` 的机器上重跑才能升级为当机证据。

### `motion_study`（verified）

- 🔴 **同时修掉一个真 bug**：本模块 `import` 区**没有 `from pathlib import Path`**，而 `_motion_typelib_candidates()` 里用了 `Path(executable)` ⇒ **`NameError`** ⇒ **整条 Motion 路径在真机上根本走不通**。该 bug 能存活至今，是因为 `tests/test_sw_motion_audit.py` 把 `get_motion_study_manager` / `ensure_motion_type_library` **两个入口整个 monkeypatch 掉了** ⇒ **入口零覆盖**。⇒ 契约测试已补「入口可调用且不抛 NameError」的断言（不连真机）。

### `part_and_features`（verified）

- ⚠⚠ **2026-10-01（轮 155）按事实 53 强停止**：累计 **6 种选法全部失败**（草图整体 / 实体边 / 草图段 × 各两种选法）⇒ ★★★ **卡点查明**：`IEntity.Select4` **没有 mark 参数**（选完 mark 仍是 0），而 `SelectByID2` 需要**名字**、**边与草图段都没有名字**（草图段的 `GetID` 是**端点对** `'(0, 1)'`）。⇒ **「选中 2 个实体 + mark=1」这个官方前提，在这条后端上我没能同时满足**。⚑ **候选解释列为未验证**（如「该后端下结构性不可用」，与事实 47 同类）—— **没有证据，不写进结论**；⇒ `composite_curve` **不升级**、`insert_composite_curve` **已写但未取证**。
- ⚠ **2026-10-01（轮 153）又试了 3 种选法（合计 4 种）**：① 整个草图 × 2（**官方示例原样**）· ② `IEntity.Select4` 选 2 条边（计数 2）· ③ 按面上的点 + **mark=1** · ④ 按名字选边（0，事实 32）—— **全部返回 `False`** ⇒ 按事实 53 **停止试**。★ 另记一个观察：`GetSelectedObjectCount2(-1)` = 2 而 **`GetSelectedObjectCount2(1)` = 0**★ **2026-10-01（轮 154）判别实验把它查清了**：`mark=1/2/0` 都能精确落到对应 mark 上（`GetSelectedObjectCount2(N)` = 1）⇒ **mark 与读法都没问题**；★★★ 真因是 **`SelectByID2` 返回 `True` 却什么都没选中**（事实 94）⇒ ★ **可复用判据**：判「选上没有」**一律回读** `GetSelectedObjectCount2(<mark>)`，**不要看 `SelectByID2` 的返回值**。⇒ ⚑ **真因未查明**，`composite_curve` **不升级**。
- ★★★ **2026-10-01（轮 148）查出一个「守了每轮收尾」的检查在**漏检**：此前 **21 个工具**各复制了一份「查残留模态框」的代码，**每份都带 `IsWindowVisible` 过滤**；而实测 SolidWorks 的 **49 个顶层窗口里只有 1 个可见** ⇒ **那个过滤漏掉 48 个（约 98%）**。⚠ 精确说法**不是**「它从未验证过任何东西」（它确实扫到那 1 个），而是「**它漏掉了 48 个**」——⇒ **可能漏掉真正的模态框**，而模态框会把会话**永久挂起**（铁律 2 的头号风险）。⇒ 处置：抽成**共享**函数 `sw_connect.residual_dialogs(pid, only_visible=False)`，**默认不过滤可见性**，并**把扫到的窗口总数一并返回**（空列表才能与「没扫到」区分开）。★ **2026-10-01（轮 149）21 份已全量迁移**：每份的 `modal_dialogs` 都改成**委托** `sw_connect.residual_dialogs`（函数内双路导入，照本仓既有模式），并**把扫到的窗口总数一并返回/打印** ⇒ ★ 端到端实测输出变成「**扫了 49 个窗口 · 无模态框**」（此前只写「无」，无法区分「没有」与「没扫到」）。⚠ 唯一豁免：`tools/probe_window_vs_graphics.py`（它的 `main_windows()` **本身**要用可见性做对照实验，且**不在收尾路径上**）。
- ⚠ **未查明**：① 我传 `Height=8`（毫米），而 Z 方向实测增长 **14.2222** —— **两者不等**，`Height` 的语义（圆顶是曲面，其包围盒高度与参数不是同一件事？）**未查明**；② **特征树里哪一个是圆顶未查明**（`FeatureByPositionReverse` 的顺序语义没查清）；③ `IDomeFeatureData2` 的读回（官方示例那条路）**到不了** ⇒ 标为**不可达**（官方示例写 `data.AccessSelections(...)`，而那族在 pywin32 迟到绑定下到不了 —— 事实 47/68）。⚠ 另外 `GetFeatureCount` 是**属性**不是方法（调它会得到 `'int' object is not callable`）。
- ⚠ **未查证**：那 12/16/22 个 `float` 的**具体含义**未逐位核；`get_splines` / `get_polylines` / `get_sketch_points` 等**其余取法的形状未测**（`get_splines` 量到 0 是**因为样条画不出来**，不是取法本身的问题）；`CreateSpline3` 的 BYREF 末参**没有再去试**（事实 47 已穷尽 20+ 形态）。

### `pattern_and_mirror`（verified）

- ★★ **`FeatureLinearPattern*` 在 pywin32 这条后端上到不了「建成」**（★ 2026-10-03 轮 454 · 事实 369 · `output/linear-pattern-generations-evidence.json`）。★★ **三层论证**：① **arity 正确的不报错**（`FeatureLinearPattern3` 是 **10** 参 · `4` 是 **20** 参 —— 按对的个数传都「接受」了）；② **选区也对**（`_select_by_id(..., "BODYFEATURE", mark=4)` 回 `True`，而**同族的 `circular_pattern` 用同一套选区且能成**）；③ ★★ **三代都不改几何**（包围盒一模一样）—— 而阵列**必须**改变包围盒。⚠ **故不要再试**（事实 53）；★ 而它的 **arity 表**（8/9/10/20/22）已记在事实 369。★ `circular_pattern` **不受影响**（走 `FeatureCircularPattern4` · 7 参 · 能用）。

### `preview_and_review_report`（verified）

- ⚠ **未验（铁律 5：查不到就说查不到）**：**回读当前视图名**这条路**真机上走不通** —— `IModelDoc2.ActiveView` 拿回来的是 `CDispatch`，而 `Name` / `GetName2` / `GetViewName` / `Type` **全部报 `<unknown>.X`**（★ 事实 36 形态）⇒ ★ 本族只报 `ok`，不声称回读可用。

### `routing`（stitched）

- ★★★ 2026-10-01（轮 279）**由 verified 降为 stitched**，依据是**可执行的探测**：cadstudio_routing_preflight 回 **blocked** / readyForNativeWrite=false / error_code=routing_addin_or_license_unavailable，blocker=「未检测到 SOLIDWORKS Routing 加载项注册或许可证可用证据」。★ 而同一次探测显示**类型库在**（SWRoutingLib.tlb）· **IRouteManager/IRouteProperty/IAutoRoute 三个接口都在**（interfaceCoverage=1.0）· **3 个 routing DLL 都在** —— ★★ 所以缺的是**加载项/许可**，不是接口定义。★★ sw_routing 的 22 个公开函数**故意不取得 route_manager**（模块 docstring 明写本机没注册 Routing 加载项，全部函数接收调用方传进来的 IRouteManager）=> ★ 那 22 个**不该按缺口处理**，而是**等加载项**；★ 而它们**也没有挂工具**（★ 挂了也到不了）

### `sheet_metal`（verified）

- **真机实测状态（2026-10-01，SW 2026 SP4.1）：6 个创建入口里 2 个可跑** —— ✓ `create_base_flange`（但**只对闭轮廓成立**，开放折线的轮廓法兰实测失败）· ✓ `sheet_metal_evidence`；✗ `create_one_bend` / `create_edge_flange` / `create_gusset` **受 pywin32 指针接口限制到不了**（见 `backend_catalog.solidworks-com-pywin32` 的相应条目）· ✗ `create_draft` 用的 `swFmDraft(3)` **不在 `CreateDefinition` 接受的 35 个常量里**。**已修掉的缺陷**：`create_one_bend` 的常量（`swFmOneBend(33)` → `swFmSketchBend(35)`，报错前推到 `CreateFeature(35)`）；`create_gusset` **整步缺失的官方步骤 3**（`ProfileDimensionScheme` / `UseOffset` / `UseAngleDimForProfile`，真机**属性层 8/8 读回成功**）；`create_edge_flange` 的 `ReverseDirection` 跨接口泄漏。**⇒ 「属性设对了」与「特征建成了」是两件事，必须分开取证。**

### `sheet_metal_creation`（stitched）

- ⚠⚠ **三条达不到**（★ 都在 known-facts 47/43 里记着）：`create_one_bend`（`0x80010105` 后端限制）· `create_edge_flange`（同族）· `create_gusset`（同族）· `create_draft`（`CreateDefinition(3)` 回 None）

### `simulation_and_fea`（verified）

- 轮 272 新增求解器设置 5 个（不动 RESOLVERS：注入 study + 包装内部 study_options_of 取 options）。★★ 真机定性（轮 273）：create_study **ok=True**（CreateNewStudy3 / code 0）；list_setter_summary（零参）**ok=True**（给出 9 个族 / 202 个 setter 名）；⚠ 5 个配置工具**真机未通过**，两类原因都查清：① TypeError 'bool' object is not callable => 真机上该成员已是 bool 值（不是 setter）=> 能读不能写；② (-2147417851) = 0x80010105 => pywin32 后端限制（与事实 47 同码同族），该族选项对象只能取一次

### `sketch_chamfer`（verified）

- 轮 281 填实（空壳）：sw_sketch_edit.create_sketch_chamfer。★ 注意与特征倒角(solidworks_chamfer)不是一回事；★ 而事实 47 的后端限制说的是**特征**倒角，草图倒角另算。证据 tools/verify_sketch_edit_smoke.py（真机）

### `sketch_edit_ops`（stitched）

- ★★★ **2026-10-01（轮 164）更正轮 122 的定性**：轮 122 看到 `type=2` 报`com_error 0x80010105` 就判它「**架构性限制、到不了**」并停手 —— **那是误判**。★ 轮 164 用 `tools/probe_chamfer_forms.py` **逐类型试 + 回读线段数**（`tools/probe_chamfer_forms.py`）：`type=0`（默认）/ `type=1` ⇒ 段数 **2 → 2**（没变）且返回 `None`；**`type=2`（`distance_equal`）⇒ 段数 `2 → 3`（倒角真的建出来了）**，只是**返回对象拿不到**（`com_error 0x80010105`）。⇒ ★★ 真正的限制是「**拿不到返回对象**」，**不是**「做不了倒角」。★ 根因：轮 122 **只看异常、没回读副作用** —— 与事实 94 那一族（**不信返回值，回读状态**）同源。⇒ ★ 已把倒角拆成独立条目 `sketch_chamfer`（`level: verified`，真机 **10/10**）；本条目**仍为 `stitched`**：`sketch_mirror` 与 `convert_entities` **本轮未单独取证**。
- ❌ **`create_sketch_chamfer` 到不了** —— 选中 2 条后调 `CreateChamfer` 报 `pywintypes.com_error: (-2147417851, '服务器出现意外情况')`。★ `0x80010105` **正是已知事实 47 / 28 那个错误码** ⇒ 属「pywintypes 迟到绑定到不了需要真实指针的接口」这一**架构性限制**，**不是参数没调对**。⚠ 按**事实 53** 停手。

### `surface_modeling`（stitched）

- ⚠ **2026-10-01 实测（轮 77）：本机没有 `OCP` / `cadquery` / `trimesh`**（`importlib.util.find_spec` 全为 `None`，磁盘上也没有 OCP 目录）。⇒ 本条 limitations 里涉及 **headless-occt** 的声明**在当前这台机器上无法复现**；`tests/` 里对 OCP 后端的用例**都 monkeypatch 掉了后端**（验的是 MCP 层传参，不是 OCP 真跑），`tests/test_headless_cad_writer.py` 更是**显式把 OCP 伪装成不可用**来测降级路径。⇒ 这些声明**不是假的**（代码里确有该路径、且降级行为有测试），但**其运行证据不在本机** ——按铁律 5 如实标注，等装了 `cadquery-ocp` 的机器上重跑才能升级为当机证据。

### `topology_iteration_options_backend_limited`（stitched）

- ★ 47：「`ISketchedBendFeatureData` 的 `AccessSelections` / `SetFixedFace` 在 pywin32 迟到绑定下**不可调用** —— 这是**架构性限制**，不是参数没找对」（改传 `VARIANT(VT_DISPATCH, None)` 后报的**正是**这一个错误码）
- ★ 67：「`ISketchManager.CreateChamfer` 在 pywin32 后台上到不了（架构性限制，与事实 47 同族）」
- ★★ **据 `capabilities.yaml` 的后端限制段**：「**不能调用官方标记为仅进程内非托管 C++ 的指针接口**」
- ★ **可复用的判据（本条最大的价值）**：★ **同一个错误码 = 同一类后端限制** —— 以后见到 `0x80010105` 不必重新穷举形态（★ 事实 47 是「两轮 20+ 种形态」换来的）

### `topology_optimization`（verified）

- ✅ **需要用户提供的东西**：`SOLIDWORKS Simulation Professional` 或 `Premium` 许可（或单独含拓扑优化的许可）。**在此之前，本能力无法在本机升到 `verified`**，且这不影响 `stitched` 之下的**每一段已分别真机验证**这一事实。

### `topology_readback`（stitched）

- ★★ 2026-10-02（轮 383）**真机 7/8**：★ **读数与设参的 7 项全部真机通过**（★ 含 `set_goal` 的「设置生效」判据：`before_taken 0 → after_taken 1`）；★ **唯一不过的是 `set_topology_iteration_options`**，报 **`0x80010105`**（`com_error: (-2147417851, '服务器出现意外情况。')`）—— ★ 与**事实 47 / 28 同一个错误码**，★ 定性为**后端限制**（pywin32 迟到绑定调不到那种指针接口），★ **不是代码问题**。⇒ ★ 定则：★ **不要再「换个参数试试」**（事实 47：20+ 种形态已穷尽）。⚠ 另一条（`solidworks_topology_run`）需要跑求解 ⇒ 见 `analysis_run_readback` 的同族限制。

### `weldment_profile_and_curve`（verified）

- ★★ **结构系统（Structure System）那条链在 pywin32 上到不了「建成」**（★ 2026-10-03 轮 441–446 · 事实 356 / 360 / 361 · `output/structure-system-evidence.json`）。★★ **入口查得到**（而在 **`IModelDocExtension`** 上：`CreateStructureSystemMemberData(MemberType)` ⇒ `IStructureSystemMemberFeatureData` · `CreateStructureSystem(primary[], secondary[])` ⇒ `IFeature`）—— ★ **而走不通**：① `ext.CreateStructureSystem` 在**迟到绑定下取不到**（`getattr` 回 `None`）；② `SetPathSegments` 只在 `IPrimaryMemberPathSegmentFeatureData` 上，而**换接口要 QI** —— 而 **pywin32 里换不了**（`QueryInterface` 报 `no interface object registered`，与「注册表 TypeLib 检索 591 个条目里 0 个 SOLIDWORKS」吻合）。⚠ **故 `configure_member_profile` / `configure_split_member` 判「不做」**，★ 而理由**不是「查不到」**（那已被推翻）而是「**在这条后端上到不了**」· 与**事实 47** 同族。★★ 而**完整官方序列已入库**（事实 358）⇒ **换个后端就能接着做**。

