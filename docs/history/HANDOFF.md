# 交接文档 —— SolidWorks 自动化仓库（★ 给接手的**新对话**）

> ★ 本文写给**接手这个仓库的下一个新会话**。★ 目标是让接手者**不必重走我已经走过的弯路**。
> ★ 本版更新时间：**2026-10-06** · 仓库 `D:\AI\SW` · ★ **本版新增：规格 209 **全部 15 件活收口完毕****
> ★ 上一版（2026-10-05）讲规格 206/207 的收口与环境陷阱 ⇒ ★ **其内容原样保留在本文后半（见「上一版内容」），本版在最前面**。
> ★ 本版主结论：★★ **规格 209（18 条采纳候选 → 15 件活）15/15 全部收口** ——
> ★ 其中一部分 **verified**、一部分 **stitched**（★ 都是**如实记的负结论 / 半程结论**，不是没做），
> ★ 逐条判据与证据见 [../specs/209-union-adopt-18/tasks.md](../specs/209-union-adopt-18/tasks.md)
> 与 `capabilities.yaml`（★ 每条带 `level` / `evidence` / `limitations`）。
> ★★ **接下来可做的**：① 补规格 209 里**如实记下的「未验 / 未接」分支**（★ 每条都在 `limitations` 里写死了下一步）；
> ② 补 idx 30 `AutoInsertCenterMarks2` 批量路的**单独真机验证**（★ 裁决书 §一 第 2 条点名的缺口）。

---

# ★★★ 本版（2026-10-07）：规格 213 **把没挂工具的能力全挂上** —— ★ 并记下本版**最要紧的一类自查**

> ★ 本版接在「规格 211 / 212 收口」之上。★ **旧版内容原样保留在本文后半** ✓。
> ★ 本版主结论：★★ **`specs/213-hook-up-tools` 的 11 项**全部挂成 MCP 工具** ✓ ——
> ★ 工具数 **448 → 459** · ★ `docs/user-feature-coverage.md` 的**本仓库覆盖 124/145（86%）→ 133/145（92%）** ✓

## 一 · 一句话现状：★ 这不是"加功能"，是**补最后一跳**

★★ **起因（★ 用户实测点破的）**：★ `docs/user-feature-coverage.md` 只量三列里的**第一列「有入口」**，
★ 而它的来源是 **`register_capabilities.all_specs()` 的工具名集合** ✓
⇒ ★★★ **规格 211 收口时做成 `verified` 的能力，没有任何 ToolSpec 引用它们** ✗ ⇒
★ **从「用户可发现、可调用」这个口径看，它们等于不存在** ✓
★ **用户看到的怪现象**：★ 装配域做了爆炸直线 + SpeedPak 两个 `verified` ⇒ 覆盖率**仍 5/10** ；
★ 焊件域做了四项 ⇒ **仍 3/7** ✓

⇒ ★★★ **这是本仓主线「挂柜台」还没走完的那一段**：★ **能力做完了 ≠ 用户能用** ✓ ——
缺的是**最后一跳「能力 → ToolSpec」** ✓

## 二 · 11 项分两类（★ 实测得出、★ 不是估计）

| 类 | 定义 | 做法 |
|---|---|---|
| ★ **A 类 6 项** | ★ **`scripts/` 里已有可复用实现** | ★ **只差 ToolSpec**（★ 纯声明 ✓）|
| ★ **B 类 5 项** | ★★ **只在探针里验过、`scripts/` 里没有模块函数** | ★ **先把探针里已证实的调用序缝进模块**（★ 铁律 3 + 铁律 1 ✓）**再挂** ✓ |

★ 落点：`mcp-server/tool_specs_batch100.py` → `101` → `102`，★ **并登记进 `register_capabilities.py` 的 `BATCH_MODULES` 显式清单** ✓（★ **登记 ≠ 可有可无**：★ 不登记就不生效 ✓）

## 三 · ★★★★★ 本版最要紧的经验：**真机验证要跟"原读数"对，不能只对"通不通"**

★★ B 类 5 项的模块函数是**新写的代码** ⇒ ★ 必须**另写探针走模块函数**再验一次 ✓
（★ 官方纪律逐字：「按 `ToolSpec` 的契约调，**别手调内部实现**」✓）
★ 而本版两次这么做，**都抓出了我自己的错** ✗：

**① 判据太弱** —— ★ 爆炸直线我第一版只记 `ActiveSketch`「**现在有没有**」✗；
★★ 而**原探针**的判据是 **`False → True` 的「侧变化」** ✓ —— ★ 那才对应官方 `Returns` 里的 *inserted* ✓
⇒ ★★★ **「现在有」分辨不了「这次插入了」与「本来就开着」** ✓

**② 读数根本无效** —— ★ 曲线驱动阵列我传 `seed_feature=<草图名>` ✗ ⇒ 真机
`mark1=False · mark2=False` ⇒ ★ **两处前置都没上** ⇒ **这次读数不算数** ✗
★ 而原探针用的是 `凸台-拉伸1`（★ **特征名** ✓）⇒ `mark1=True · mark2=True` ✓
⇒ ★★★★ **若不修，我会拿一个"前置没上"的读数去当"真的不建"的证据** ✗ ——
★ 而那**正是本规格反复吃的那个坑**（★ 「读数无效」与「真的不建」长得一模一样 ✓）

⇒ ★★★ **可复用的定则**：★ **真机复验时，要拿新读数跟**原来的有效读数**逐字段对** ✗ ——
★ 只对"成功/失败"是**对不出这两处**的 ✓

## 四 · ★★★ 四条被门禁教出来的定则（★ 每条都撞过 ≥1 次）

| # | 定则 | 事由 |
|---|---|---|
| ★ 1 | ★★ **钉「关系」、★ 不钉「数字」** | ★ 我在 `batch100` 的测试里写死"工具数 = 448+6" ✗ ⇒ `batch101` 一挂就变红 ✓ |
| ★ 2 | ★★ **加名字、★ 不加行；★ 且注释放在 `try:` 上面** | ★ 相对导入棘轮的判据逐字是 `prev.startswith("try:")` ⇒ ★ **只有紧跟 `try:` 的那一行算有兜底** ✓ —— ★ 函数里写完整的 `try:/except ImportError:` 则**加 0** ✓ |
| ★ 3 | ★★ **参数名要过规则 3**（★ 不只 2 与 2b） | ★ `scale_feature` 的 `x`/`y`/`z` 被拦，逐字：「入参 `x` 是**裸坐标**」✗ ⇒ ★ 它们其实是**无量纲比例** ⇒ ★ 改名 `*_factor` + ★ **`param_alias` 映射回形参** ✓ |
| ★ 4 | ★★ **长字符串里的引号一律用「」** | ★ 本版在 `tool_specs_batch10x` 里撞了**四次** ✗ —— ★ 而★ 我那个"数引号奇偶"的自检**漏掉了成对的裸引号** ✗ ⇒ ★ **权威判据只有 `ast.parse`** ✓ |

## 五 · ★★ 本版的终检（★ 证明"没有漏"）与它的**如实结论**

★ 做法：★ 把 ToolSpec 的 `(module, function)` 集合取出、与 `scripts/` 里"像入口"的公开函数相减 ✓
★ 读数：★ **255 个像入口的函数里，118 个没被 `function=` 直接引用** ✗
★★ **抽样判定后的结论**：★ **绝大多数是"包装函数 / 备用入口"、★ 不是缺口** ✓ ——
★ `export_to_step` 有包装 `export_to_format` 调它 ✓ · ★ `create_through_hole` **有** ToolSpec 引用 ✓
⇒ ★ **我的 `function=` 匹配太窄** ✗

★★★ **终检的真发现（★ 如实记、★ 有意不扩范围）**：
★ 有几个能力存在 **`_report` 兄弟入口**（★ `sw_part.insert_scale_report` ·
★ `sw_export.export_flat_pattern_dxf_report` ✓）—— ★ 它们返回**更富的证据字典** ✓，
★ 而**能力本身已经挂上了** ✓ ⇒ ★★ **一个能力挂两个工具会变成"大杂烩"** ✗ ⇒ ★ **有意保留为内部入口** ✓

★★★ **而更大的普查做不了 —— 原因是结构性的**：
★ `capabilities.yaml` 的 schema 里**没有「能力 → 工具」映射字段** ✗ ⇒
★ **"哪些能力没挂工具"这件事在全仓尺度上无法机械判定** ✓
⇒ ★★ **下一步（★ 属另一个规格）**：★ **给 `capabilities.yaml` 加一个 `tools` 字段**，
★ 然后才能做**全仓严谨普查** ✓

## 六 · ★★★★★ 全量 pytest 抓出一处**聚焦测试看不见的**回归（★ 本版最值钱的一条定则）

★★ **事故**：★ 首轮全量报 `ERROR tests/test_sw_sheet_metal.py`（**收集期**）✗ ——
★ 而★ **单独跑该文件 6 passed** ✓ · ★ **只做收集也通过** ✓ ⇒ ★ **不是稳定复现**，★ 起初以为是偶发 ✗
★★★ **重跑带 traceback 才拿到真因**：
```
scripts\sw_sheet_metal.py:18: from sw_connect import get_com_member, call_com_member, deg
E   ImportError: cannot import name 'deg' from '<unknown module name>' (unknown location)
```
★★ **根因链**（★ 三步，★ 每一步都是我为了"过上一道门禁"而做的）：
1. ★ **第一版**：★ 函数里裸写 `from .sw_connect import mm as _mm` ✗ ⇒ **相对导入棘轮 35 → 36** 被拦 ✓
2. ★ **第二版**：★ 把 `deg` 加进**模块级**那行 ✓ ⇒ ★ **棘轮过了** ✗ ——
   ★★ 而 `tests/test_sw_sheet_metal.py` 只往 `sys.path` 塞 **`scripts/`**（★ **不是包** ✓）⇒
   ★ 该模块的**模块级**相对导入走进**半初始化**路径 ✓ ——
   ★★★ **别的名字在缓存里已有、★ 只有新加的 `deg` 暴露了它** ✗
3. ★ **第三版（正解）**：★ 放回**函数内**、★ 且写**完整的 `try:/except ImportError:`** ✓
   ⇒ ★ 既过棘轮（★ 「紧跟 `try:` 的那一行」✓）、★ 又不碰模块级导入 ✓

⇒ ★★★★ **定则（★ 本版补，★ 而它比前面几条都硬）**：
  ★★★ **改了「模块级导入」⇒ 必须跑一次全量 pytest** ✗ ——
  ★★ 因为那影响的是**收集期**，★ **而聚焦测试看不到收集期** ✓✓
  ★（★ 本版**恰恰**是收口时才跑的 ✓ —— ★ 若那一步省了，这条会**留在库里** ✗）
⇒ ★ **与 `AGENTS.md` 既有纪律合看**：★ 「全量只在两种情况跑：① 发布前 ② **改了 `sw_connect.py`
  或门禁本体**」✗ —— ★★ **本版建议把 ② 扩一条**：★ **改任何模块级导入时也要跑** ✓

---

# ★★★ 本版（2026-10-07）：规格 211 **21 项全部收口** —— ★ 并记下本版**最值钱的三条教训**

> ★ 本版接在「规格 209/210 收口」之上。★ **旧版内容原样保留在本文后半** ✓。
> ★ 本版主结论：★★ **`specs/211-user-feature-gaps` 的 21 项用户功能**全部有结论**** ✓ ——
> ★ 逐项结论表见 [../specs/211-user-feature-gaps/b8-final-table.md](../specs/211-user-feature-gaps/b8-final-table.md)（★ 由
> `tools/gen_spec211_final_table.py` 从两处机器可读来源**合成**、★ **不手写** ✓）。

## 一 · 一句话现状

★ **21 项终判**：★ **可做 10**（★ **已做 10**：`verified` **6** · `stitched` **4**）·
★ **不做 10**（★ **逐条带理由 + 证据**）· ★ **已覆盖 1** · ★ **待实测 0** ✓

★★ **本版新增 / 升级的能力**（★ 全部落在 `capabilities.yaml` ✓）：
| 能力 id | level | 一句话 |
|---|---|---|
| ★ `sweep_surface` | ★★ **`verified`** | ★ 扫描曲面 —— ★ **查了那条从没查过的"路 B"**（`InsertSweepSurface2` + 官方 mark 表 ✓）|
| ★ `forming_tool` | ★★ **`verified`** | ★ 钣金成形工具 —— ★ 真机建成 `circular emboss1` ✓ |
| ★ `explode_line_sketch` | ★★ **`verified`** | ★ 爆炸直线（`ISketchManager`，零参 ✓）|
| ★ `speedpak` | ★★ **`verified`** | ★ SpeedPak（★ "怎么选"只有官方示例说得清 ✓）|
| ★ `weld_symbol` | ★★ **`verified`** | ★ 焊接符号（★ **真入口是另一条 API** ✓）|
| ★ `curve_driven_pattern` · `weldment_trim` · `weldment_gusset` · `fillet_weld_bead` · `untrim_surface` | ★ `stitched` | ★ 有真机读数、★ 未到建成（★ 每条 `limitations` 写死了"还差什么"）|

## 二 · ★★★★★ 本版最值钱的教训：**我可能走的是"另一条 API"**（★ 三次实证）

★ **同一个形态在本版出现三次** ✗ —— ★ **而每一次都是"官方示例"救的场** ✓：
| # | 项 | 我当时以为的"真入口" | 官方示例真正走的 |
|---|---|---|---|
| ★ 1 | ★ **扫描曲面** | ★ 路 A：`CreateDefinition` + `CreateFeature`（★ 静默回 `None`）| ★★ **路 B：`InsertSweepSurface2` + mark 表** ✓ |
| ★ 2 | ★ **焊接符号** | ★ `IDrawingDoc::InsertWeldSymbol`（★ **10 个参数**）| ★★ **`IModelDoc2::InsertWeldSymbol3()`**（★ **零参**）+ `IWeldSymbol` ✓ |
| ★ 3 | ★ **曲线驱动 / 零部件阵列** | ★ `IFeatureManager::FeatureLocalCurveDrivenPattern`（★ 参数式）| ★★ **`CreateDefinition` + `CreateFeature`**（★ 属性式）✓ |
⇒ ★★★★ **可机械执行的判据（★ 本版最有用的操作）**：
  ★★★ **动手之前，先在官方 `examples/` 里搜一遍那个成员名，看官方示例**实际调的是哪一条** ✓** ——
  ★★ **那比读签名更接近真相** ✓（★ 本版三次里，★ 有两次是**签名与 `## Remarks` 都没说清**的事情 ✓）

★★ **配套的第二条定则**（★ 本版第二次翻案时补的）：
  ★★ **「某个入口存在且无 ACL」≠「这个能力可做」** ✗ —— ★★ **因为官方示例可能走**另一条**入口** ✓
  ★（★ 反向那句也成立：★ **「某个入口要 ACL」≠「这个能力要 ACL」** ✓ —— ★ **两句都要** ✓）

## 三 · ★★★★★ 第二条教训：**为每一处前置单独落一个布尔字段**（★ 六次救命）

★★★ **因为「读数无效」与「真的不建」**长得一模一样**** ✗ —— ★ 本版六次实录：
| # | 场景 | 若不看那个字段会怎样 |
|---|---|---|
| ★ 1 | ★ `select_entity_by_index` 的 `append` **默认 `False`** ⇒ 它**清空了 mark 1 的体** | ★ 八组读数**全无效**、★ 而样子与"真的不建"**一样** ✗ |
| ★ 2 | ★ `iter_features_recursive` 取不到特征 ⇒ **`特征树 = []`** | ★ 会把"前置没上"写成"试死" ✗ |
| ★ 3 | ★ `create_base_flange` 传错参数（★ 它**不抛、只回 `None`**）| ★ 会以为"钣金建不出来" ✗ |
| ★ 4 | ★ 官方 Remarks 要"先选面"而我没选 | ★ 同理 ✗ |
| ★ 5 | ★★ **补丁脚本自己的 `print` 里嵌了裸引号** ⇒ 脚本没运行 | ★ 会以为"探针已改" ✗ |
| ★ 6 | ★ `GetComponents(**False**)` 把子装配**里面的零件递归带出来** | ★ 会以为"没选中组件" ✗ |
⇒ ★★★ **配套的三条 | 可机械判定的信号**（★ 本版实测出来的 ✓）：
  ★ **① 行号在两次报错之间变化 ⇒ 文件已被写脏** ✓（★ 用 `git checkout --` 回退、★ 再用 `edit` 工具 ✓）
  ★★ **② 「读回取不到（`None`）」与「读回取到但是 0」是两件事** ✓ —— ★ 后者才说明判据落到位了 ✓
  ★★★ **③ 穷举读数要说清"穷举的是哪几个维度"** ✓ —— ★ 别把"3 形态 × 4 开关 = 12 组"说成"全试过了" ✗

## 四 · ★★★ 第三条教训：**记定则要记到"族"那一层**

★ 我在 SpeedPak 那批记下：「★ **装配体**文档本身就是 `IAssemblyDoc`」✗ ——
★★ 而下一批换成**工程图**时**又踩一次**（★ 写了 `get_com_member(drawing, "GetDrawingDoc")` ✗）
⇒ ★★★ **正解**：★★ **`IModelDoc2` 的族接口（`IAssemblyDoc` / `IDrawingDoc` / `IPartDoc`）
**就是文档对象本身**，★ 不需要 `GetXxxDoc` 那一层** ✓
★ **教训**：★ **定则写窄了 = 下一个人（或下一批的我）会再踩** ✓

## 五 · ★★★★ 全量 pytest 的基线（★ 这一条**必须**看，否则会误判）

★ 本版**跑了全量**（★ 而这一条本身是个教训 ✓）：
★★ **纪律写在 `AGENTS.md` 里**：「★ 收尾链只跑**聚焦测试**；★ **全量只在两种情况跑**：
  ① 发布前 ② **改了 `sw_connect.py` 或门禁本体**」✗ ——
  ★★ **而本版改了** `mcp-server/server.py` · `tool_registry.py` · 多个 `scripts/*.py` · `capabilities.yaml`
  ⇒ ★★★ **那些都会影响被大量测试共用的东西** ✗ ⇒ ★ **早该跑全量** ✓

★★ **读数与拆账**（★ **基线必须用 `git worktree` 量** —— 事实 57 的推论：
  ★「一个红的测试也未必是我弄的」✓）：
| 类 | 数 | 说明 |
|---|---|---|
| ★★ **既有红**（★ 与本次改动无关）| ★ **12 条** | ★ `test_release_check` · `test_tool_specs_batch79` · `test_mcp_protocol_layer` · `test_registry_wiring` · `test_sw_connect_open_document` · `test_sketch_slot_params` · `test_real_gap_triage_contract` · `test_com_member_helpers` · `test_no_bare_byref_args` · `test_no_uncalled_helpers` · `test_gate_negative_cases`（2 条）|
| ★★ **本版引入并已修** | ★ **6 组 22 条** | ★ 见下 |
⇒ ★★★ **最终读数**：★ **12 个套件在基线与当前**完全一致**（7 failed / 99 passed）** ✓✓
  ⇒ ★ **我引入的失败**已清零**** ✓

★ **那 6 组是什么**（★ 每一组的真因都值得记 ✓）：
1. ★★ `test_result_serializer`（4 条）⇒ **`server.py` 里 `_jsonable` → `_tool_error` 之间是"被离线抽取区"** ✗ ——
   ★ 往那里插代码要**自包含**（★ 我插的单位守卫用了 `re`/`os`/`sys`，★ 而测试的注入表没有 ✓）
2. ★★ `test_unattended_equivalence`（7 条）⇒ ★ **`allowed_modes` 是授权维度** ✓ ——
   ★ **R11**：`allowed_modes ⊆ {interactive, reviewed, unattended}` 且 **`level != verified` ⇒ 不含 `unattended`** ✓
   ★（★ 我误把"文档类型"（`part`/`assembly`）当成了"模式" ✗）
3. ★★ `test_language_backend_matrix`（8 条）⇒ ★ **同上**（★ 根因同一处 ✓）
4. ★★ `test_relative_imports_gate`（1 条）⇒ ★ **本仓的棘轮计数"紧跟前一行的 `try:`"** ✗ ——
   ★ **每个文件只有第一行合格**、★ 新增导入行会 +1 ⇒ ★ **优先复用文件内既有能力** ✓
5. ★ `test_signature_audit_freshness_gate`（1 条）⇒ ★ **加了 COM 调用 ⇒ 签名审计表要跟着改** ✓
   ★（★ 该门禁**不要求数字不变**、★ **只要求文档跟得上代码** ✓）
6. ★ `test_matrix_tool_name_normalization`（1 条）⇒ ★ **别把当时的数字写死** ✓ ——
   ★ **工具集会随规格长大** ⇒ ★ 钉"关系"、★ 不钉"数字" ✓

## 六 · ★★ 本版顺带解开的两个"机制死结"（★ 值得继承）

★★★ **① `sw_guard` 的 `--allow-path` 是"声明"、★ 不是"绕过"** ✓ ——
  ★ 会话里有非我方文档时预检**拒绝开始** ✓ ⇒ ★ 而**清理它们要连 COM** ⇒ ★ **死结** ✗
  ★★ 正解：★ **用 `--allow-path` 逐个声明"这是我方打开的文档路径"** ✓ ——
  ★ **实测**：★ 声明 3 个后预检从「非我方 **4** 个」变成「**1** 个」⇒
  ★★★ **护栏逐个核对、★ 把声明的正确排除、★ 仍拦住真正不明的那一个** ✓✓
★★★ **② 配套写了两把工具**（★ 建议保留 ✓）：
  · ★ `tools/probe_list_open_docs.py` —— ★ **只读**列文档（★ `path` / `title` / `visible` / `saved` ✓）
  · ★ `tools/probe_close_our_docs.py` —— ★ **只关我方**：★ 判据**只有三类**（★ ① 路径在 `output/` 下 ·
    ★② 无路径 + SW 默认名 · ★③ 无路径 + `<名字> - 图纸<N>` **且前缀在我方 `output/` 的实据里** ✓），
    ★★ 且**关闭顺序是"先无路径、后有路径"** ✓（★ 工程图/装配打开了那些零件 ✓）
  ★★★ **而它跑之前**用 7 个用例自证**过** ✓ —— ★ 含两个"**不该关**"的安全用例
    （★ `C:\Users\...\用户的零件.sldprt` · ★ `wrench.SLDASM`）✓

## 七 · ★ 本版留下的（未处置，★ 如实写）

1. ★★ **`stitched` 那 5 项各有"下一步判据"**（★ 都在 `capabilities.yaml` 的 `limitations` 里写死了 ✓）：
   ★ `weldment_trim`（★ 两条有效读数皆不建）· ★ `explode_line_sketch` **已 `verified`** ·
   ★ `weldment_gusset` / `fillet_weld_bead`（★ **只到"前置基本对上"**）·
   ★ `curve_driven_pattern`（★ 参数式那条两档有效读数皆不建）· ★ `untrim_surface`（★ 正例未做）
2. ★★ **`output/` 里留了若干落盘的零件/装配/工程图**（★ 那是 `add_component` 要磁盘路径的必然结果 ✓）——
   ★ **该目录 gitignore、不入库** ✓；★ 若有人接手，★ **先用 `probe_close_our_docs.py` 清场** ✓
3. ★★ **`PDM` 那一项的判据有三层**（★ 接口面 + 成员面 + 产品性质）✓ —— ★ 而
   ★ **"本机没装 PDM"没有直接证据** ✗（★ 没查注册表 —— ★ **硬约束明禁动系统层** ✓）；
   ★★ 若将来本机装了 PDM 且授权到位，★ **该项应重开**（★ 而入口仍在 `IApplication`，
   ★ **那条路要先解决怎么拿到 `IApplication`** ✗）
4. ★ **`docs/recon/*` 那 15 项 untracked**（★ 规格 206 的既有产物）—— ★ **本版没碰它们** ✗，
   ★ 入库与否是**另一个决定** ✓

---

# ★★★ 本版（2026-10-06）：规格 210 **B1 · B2 · B4 · B5 已收口；B3 进行中**

★ **本版干的事**：把「**工具到底会改什么状态**」从**口头约定**变成**机器可读的声明 + 真机实证** ✓

## 一 · 一句话现状

| 批 | 状态 | 一句话 |
|---|---|---|
| **B1** 效应声明的静态版 | **完成** | 448 个工具补 `writes`/`requires`（★ **机械初判**，★ 不人工逐条填）；`idempotent` 三态 + 来源；`read_only` 改由 `writes` **派生** |
| **B2** 指纹与灵敏度校准 | **完成** | 九类状态指纹；★ 真机 **sensitive 7** · 不可见 **1** · **后端限定 1** —— ★ **每一类都有结论** |
| **B3** 存活普查 448 | **进行中** | `empty` 组 47 条：★ **`agree` 35** · `missed` **2**（★ 真缺陷）· `undecided` 10 |
| **B4** 自动重试与「不适用」 | **完成** | 7 个**封闭**码 + `ACTION_MAP` + **不对称**重试门控 + **指纹保险** + **按 `inject` 自动生成的预检**（★ 已接进注册层） |
| **B5** 隔离与预检 | **完成** | 两段式预检（启动前 + 连上后）· 共用枚举助手 · copy-in/out · 输出策略 · 夹具哈希清单 |

**★ 三条自查命令**（★ 接手先跑这三条）：
```
python tools/survive_sweep.py --declared empty --limit 8   # ★ 普查（真机；★ 走护栏）
python scripts/check_relative_imports.py                   # ★ 门禁棘轮（★ 应回 35 处）
python tools/gen_fingerprint_calibration.py                # ★ 由真机标定结果重出记录
```

## 二 · ★★★ 本版最值钱的东西：**五个"看起来像对家的缺陷、实际在我这一侧"**

★★★ 本版我**五次**把**自己的错**先归咎于别处 —— ★ 每次都靠**真机读数**翻回来 ✓
★ **记下来**，因为**不记就会被当成"本来就是对的"**：

| # | 我以为是 | 实际是 | 戳穿它的证据 |
|---|---|---|---|
| 1 | ★ `bodies`/`faces`「读不到」 | ★★ **"没有实体"不是"读不到"** | 空零件 `GetBodies2(-1, False)` 回 `None`；**建出实体后回 `tuple(len=1)`** |
| 2 | ★ `display` 是「指纹盲区」 | ★★ 是**后端限定**（`GetDisplayStateSetting` 三种 Option 全抛 `com_error -2147417851`） | 与**事实 47**（`AccessSelections`）**同一个错误族** |
| 3 | ★ 写工具「缺前置」 | ★★ **12/17 只是"我没给参数"** | 逐条读失败信息：`缺必填形参：x_mm` … |
| 4 | ★ `view` 组「读数读不到」 | ★★ **我把视图对象当文档读了** | 六格**同时**空 + **13 行 × 6 格 = 78**，而 **13 = 宿主不是文档的行数** |
| 5 | ★ 「抓指纹会把草图弄没」 | ★★ 是**我施加状态的顺序**错了（`body` 的 `extrude_boss` **退出草图**） | 专写诊断 `tools/diag_read_exits_sketch.py` ⇒ `edit_mode` 前后都是 `'sketch:草图1'` |

★ **共性**：★ **症状指向别处、真因在我这一侧** ⇒ ★★ 定则：★ **先怀疑自己那半，且要用"能反证"的手段去查** ✓
★ 本版**留下 2 个诊断脚本**（★ 下次还会有人怀疑同一处）：`tools/diag_getbodies.py` ·
  `tools/diag_display_select.py` · `tools/diag_read_exits_sketch.py` ✓

## 三 · ★★ 本版抓到的**真缺陷**（★ 硬红门禁的产出）

★★ **B3 的硬红门禁**（★「**声明只读却观察到指纹变化**」）**第一次响**，抓到 **2 条**：
· `solidworks_assembly_check_interference` —— ★ 静态 `writes: []`，★ 而真机**改了 `selection`**
  （★ 干涉检查会**选中干涉组件**）✓
· `solidworks_motion_create_study` —— ★ 静态 `[]`，★ 而真机改了 `selection`+`dirty`+`features`
  （★ **名字里就写着 `create_study`**）✓
⇒ ★★ 处置：★ 新 **实证覆盖层** `docs/effect-observed.json` ⇒
  ★ **判序改成「显式声明 → 实证 → 静态 → 未知」**（★ **实证优先**）⇒
  ★ 这两条的 `read_only` **已翻成假** ✓ 且**传导**到 MCP 注解与 B4 的重试门控 ✓

★ **另一条真缺陷**（★ 从 `undecided` 里拆出来的）：
★ `solidworks_simulation_apply_link_connector` ⇒
  **`ImportError: attempted relative import with no known parent package`** ✗
★ 根因：`scripts/sw_simulation_loads.py` **函数体内 17 处**相对导入**没有兜底** ⇒
  ★ 按 `scripts.X` 导入成立、★ **按顶层模块导入就炸** ✓
★ 修法**照仓库自己的既有写法**（`try: from .X import Y` / `except ImportError: from X import Y`）✓
★★ 全仓同款 **54 处 / 22 个文件** ⇒ ★ 按**事实 61**（批量改动风险）**不一次改 22 个文件**，
  ★ 只修**实际炸掉的那个** + 加**门禁棘轮**（`scripts/check_relative_imports.py`，★ 已接进
  `release_check.py`，★ 存量 **35 处**只许变少）✓

## 四 · ★★ 本版总结出的三条**可复用定则**

1. ★★★ **"样本的状态必须由我们控制"** —— ★ B2 里同一套读数、★ 只因把"九类在同一文档上顺序标定"
   改成"**每类各用一个新零件**"，`sensitive` 就 **2 → 6**（★ **量具没变，改的是被测对象干不干净**）✓
   ★ 同族：★ **施加状态的顺序**也是状态的一部分（★ `edit:sketch` 必须**最后**施加）✓
2. ★★★ **"量具的边界"与"被测对象的未知"必须分开成桶** ——
   ★ `KNOWN_UNAVAILABLE`（**后端**限定）· `NOT_APPLICABLE_BY_DOC`（**文档类型**限定）·
   ★ `unknown`（**真的不知道**）⇒ ★★ 混在一起会把**本该 `agree`** 的压成 `undecided` ✗
   （★ 真机：★ 七条 `drawing_*` 只因图纸上 `config` **不适用**，就全被压住了）✓
3. ★★★ **判据升级时，它此前产出的所有读数都要作废重测** ——
   ★ 我修掉「**假一致**」（★ 调用没调成却记 `agree`）之后，★ **旧的 `47/47 agree` 就不成立了** ✗
   ⇒ ★★ **不能只修工具、不管旧结论** ✓

## 五 · ★ 本版留下的（未处置，★ 如实写）

· ★ **B3 还差两组**：★ `nonempty`（135）与 `null`（266）**还没跑**（★ `empty` 组已跑）✓
· ★ **`undecided` 还剩 10 条**（★ `empty` 组）：★ 主要是★ 需要**插件**的组
  （`study` / `cost_manager` / `sw_app`）★ 与 1 条深扫没跟到（`sketch_spline`）✓
· ★ **门禁棘轮还有 35 处**存量（★ 只许变少）✓
· ★ `docs/spec210-b3-undecided-breakdown.md` 是**逐条拆解记录**（★ 两轮）✓

---

## 六 · ★★★ **全量 pytest 的基线**（★ 这一条**必须**看，否则会误判）

★★ 本版收尾时跑了**全量 pytest**：**21 failed / 2239 passed** ✗ —— ★ 一看像是我弄坏的 ✓
★★★ **但用 `git worktree` 回到「规格 210 开始之前」的那个提交**（`9f1834f3`）、
  ★ 跑**同一批测试** ⇒ ★★ **那 33 条就已经红了** ✓
⇒ ★★ **结论：本版把失败从 33 降到 21**（★ 修好 12 条），★ **没有弄坏任何东西** ✓

★ **方法可复用**：★ `git worktree add <目录> <旧提交>` + `python -m pytest <同一批测试>`
  ⇒ ★★ **「基线是多少」这件事必须实测，★ 不能凭「看起来像是我弄的」就认账** ✓
  ★（★ 与**事实 57**「一直是绿的，可能只是环境恰好满足」**同族** ——
    ★★ **红的也可能「本来就红」**，★ **两个方向都要实测才能定性**）✓

★ **属于本版的失败只有 2 组，且都已处置**：
· ★ `test_tool_specs_batch9::test_batch9_is_not_marked_read_only` ——
  ★ 它断言 `read_only is False`，★ 而规格 210 把 `read_only` 改成**由 `writes` 派生**的**三态**
  ⇒ ★ **未知 ⇒ `None`** ⇒ ★ 断言改成 `is not True` ✓
  ★ 判据：★「**未知**」与「**有写**」在「能不能当只读」这件事上**等价** ✓
· ★ `test_rule3_declarative_selection_is_enforced` —— ★ 全量跑时红、**单独跑 9 passed** ⇒
  ★★ 是**顺序 / 状态相关**（★ 不是语义错）✓ ⇒ ★ **如实记，不「修」成假的绿** ✓

★ **本版的收尾读数**：
· ★ 规格 210 相关测试：**74 passed**（★ `effect_declarations` / `observed_effects` / `needs` /
  `synth_args` / `relative_imports_gate` / `fix_cjk_quotes_guard` / `applicability` / `batch9` / `rule3`）✓
· ★ B3 的 `empty` 组 47 条：★ **`agree` 35 · `missed` 2 · `undecided` 10** ✓
· ★★ **硬红门禁：2 条** —— ★ 都是**真缺陷的发现**（★ 已进实证覆盖层、★ 已不再是只读）✓

---

# ★★ 本版（2026-10-06）：规格 209 **全部收口**

★ **15 件活的全貌**（★ 详细读数与证据在 `specs/209-union-adopt-18/tasks.md` 各条下）：

| 批次 | 条 | 结果 | 一句话 |
|---|---|---|---|
| B1 | `rebuild_report` / `sketch_set_construction_geometry` / 显示状态 / 依赖 / `move_copy_body` 等 5 件 | **verified** | 真机建成并回读 |
| B2-1 | idx 336 `unfold` | **verified** | 建出 `展开1`；★ 事实：**`mark 4` 不是必需的**（官方示例让它看着像必需） |
| B2-2 | idx 34 `balloon` | **verified** | ★★ **定案**：装配图上**有没有 BOM 表都插得进去**（各 Δ=1）⇒ 两家外部项目的论断都**不该照抄** |
| B2-3 | idx 52 `centerline` | **stitched** | ★ 选区回读 **1**、而 `InsertCenterLine2` 回 `None`、中心线数 **Δ=0** ⇒ 「选中了也没产出」 |
| B2-4 | idx 175 `blank_sketch` | **verified** | ★ 双向验过（隐藏 / 显示），回读用 `IFeature::Visible` |
| B3-1 | idx 115+145 `edges/faces` | **verified** | ★ 合并成**一条**工具（按裁决书），并用 **Euler `V−E+F=2`** 回读校验 |
| B4-1 | idx 211 `macro_recording` | **stitched** | ★★ 真机证明**返回值不可用**（未开录制 `RecordLine` 也回 `True`）⇒ 只到「成对调用可达」 |
| B4-2 | idx 173 `hem` | **stitched** | ★ 五种形态**全回 `None`** ⇒ 如实记负结论 + 下一步 |
| B4-3 | idx 181 `intersect` | **verified** | ★★ 建出 `相交1`；**布尔 SafeArray 包装双向证实**（排除唯一实体 ⇒ 回 `None`） |
| B4-4 | idx 155 `fold` | **verified** | 建出 `折叠1` |
| B4-5 | idx 205 `model_annotations` | **stitched** | ★ 调用可达 + 回读可用，但★ **夹具里没有可插的标注**（数据相关，不是后端到不了） |

★★★ **本批最值得接手者读的三条**（★ 都是「看起来该成、实际不成」或反之的）：
1. **返回值不可信**：`RecordLine` **未开录制也回 `True`**（B4-1）· `SelectByID2` / `Select4` 的布尔不可信（**事实 8**）
   ⇒ ★ **判据一律用回读**（★ 本批 15 件每一件都这么做的）。
2. **官方示例的 `Preconditions` 是「例子的环境」，不是「API 的契约」**（B2-2 定案）——
   ★ 我据此假设过「没有 BOM 表就静默无效」，**被真机否证** ⇒ 已记 `spec.md` §五 第 12 条。
3. **空 Dispatch 形参不能传 Python `None`**（**事实 33**）—— ★ 我在 B2-3 **又踩一次**
   （`GetVisibleEntities2` 的组件形参传 `None` ⇒ 四种类型全报「类型不匹配」，
   ★ **看着像「读不到」、实际是我传错了**）⇒ ★ 一律 `create_empty_dispatch_variant()`。

★ **本版新增的工具**（★ 以后都该用）：
- `tools/fix_cjk_quotes.py` —— ★ 把「中文散文里的 ASCII 引号」批量换成「」（★ 我在本规格里**手改了 6 次以上**）。
  ⚠ ★ 它对「引号当字符串分隔符」的形态**会误伤** ⇒ ★ 内置了「**改完语法不过就不写盘**」的安全阀；
  ★★ 更稳的做法是**事实 48**：**长文本先写成独立文件（`.json` / `.md`），再用最短脚本搬运**
  （★ 本版最后一次就是这么做的：`_s209_b4f_caps.json` + 十来行搬运脚本）。

---

# ★★ 上一版（2026-10-06）：规格 209 · B1 批收口

## 〇 · 一句话现状 + 三条自查命令

```powershell
python -c "import sys;sys.path.insert(0,'mcp-server');import register_capabilities as rc;print(len(rc.all_specs()))"   # ⇒ 439
python -m pytest tests\test_tool_specs_batch92.py -q                                                                    # ⇒ 25 passed
(Select-String -Path specs\209-union-adopt-18\tasks.md -Pattern '^\s*-\s*\[ \]').Count                                  # ⇒ 10（B2 4 + B3 1 + B4 5）
```

## 一 · 这一版干了什么

按上一版 §二「下一件该干的活：实现那 18 条」**起了规格 209**，并把裁决书列的 **B1 批**做完：

| idx | op | 落点 | 真机判据（**全是回读**） |
|---|---|---|---|
| 235+236 | `rebuild` | `scripts/sw_session.py` | 三档都 `ok=True` · `needs_rebuild 0→0` · 树 7→7 · 包围盒前后逐位相同 |
| 79 | `construction_geometry` | `scripts/sw_sketch_edit_ops.py` | 置位/复位双向 `ok=True`；★★ **定死"连调两次 = 置位（幂等）"** |
| 97 | `display_states` | `scripts/sw_render_material.py` | 建第二条 → 激活另一条 ⇒ `changed=True`；负例不猜 |
| 244 | `referenced_documents` | `scripts/sw_document_data.py` | 自建 1 零件 + 1 装配 ⇒ `count=1` · `raw_len=2` |
| 209 | `move_body` | `scripts/sw_body_ops.py`（新） | 移动 25 mm ⇒ x `-30/30→-5/55`；复制 ⇒ 实体 1→2 |

★ 6 个新工具（`register_capabilities.all_specs()` 433 → **439**），`capabilities.yaml` **117 条**。
★ 证据：`output/union-adopt-b1-evidence.json`（★ `output/` 被 gitignore ⇒ 重跑那条命令即可复现）。

## 二 · ★★ 本版最值钱的东西：**6 处「官方文档与真机读数不一致」**（照文档写会静默错）

`specs/209-union-adopt-18/spec.md` §五 逐条记账，这里列**最要命的三条**：

1. ★★★ **`InsertMoveCopyBody2` 的长度参数是「文档长度单位」（mm），不是米** ——
   官方页**没写单位**。★ 套「COM 惯例=米」换算传 `0.025` ⇒ **只挪了 0.025 mm**，
   ★★ 而那是个**静默的 1000× 错误**，**而且它能过「包围盒变了」那条判据** ⇒ 谁都发现不了。
   ★★ 定则：**本仓的"米"惯例不能套到没写单位的成员上** —— 逐接口实测。
2. ★★ **`EditRebuild3` 是方法，而 pywin32 下「读」就等于「调」** ——
   三家外部项目都当**属性**读（`_get(doc,'EditRebuild3')`）⇒ 读到的是**返回值 `bool`**、**恒为真**
   ⇒ 拿它当判据**永远为真**（★ 注意：**不是**裁决书写的"bound method"，本仓按真机读数改了口径）。
3. ★★ **`InsertMoveCopyBody2` 的参数名与实际作用轴 X↔Z 互换**（`RotAngleX` 实际绕 Z、`RotAngleZ` 实际绕 X）
   ★ 判据用「只给一个角、看**哪一轴跨度不变**」三格互证定出；★ 补偿后 `rotate_angle_z_deg=30`
   得到跨度 `71.9615 = 60cos30+40sin30` **逐位吻合** ⇒ 单位与轴同时被几何证实。

另三条：只读信息串真机回 `"FALSE"`（官方例子是**空串**，★ 按"非空即只读"会判反）·
`CreateConstructionGeometry` 实测是**置位**不是 toggle · 「第一个名字即活动显示状态」**装配里不成立**。

## 三 · ★★ 本版抓到的**我自己的**错（★ 记下来，因为不记就会被当成"本来就是对的"）

★★ **`rebuild_report` 的包围盒判据是空转的**：`sw_part.get_bounding_box` 回的是**字典**，
而我按可迭代对象写 ⇒ `float("min")` 抛异常**被 `except` 吞掉** ⇒ 回 `None`
⇒ **`bbox_changed` 永远 `False`** —— ★★ **判据看着在、其实没在判** ✓
⇒ ★ 修法：① 取对字段；② 返回值里**显式给 `bbox_comparable`**（**`None`「读不到」与 `False`「没变」必须分得开**）；
③ 加回归测试。★ 同批还修了探针自己的两处错判据（负例以为会抛异常；用"本来就是活动的"那条去验变化）。

⇒ ★★ **可复用的手法**：★ **凡"没读到"与"没变化"落到同一个值上，判据就废了** ——
一律拆成两个字段（**能不能读** / **读到了什么**）✓ 见 `spec.md` §六 全表。

## 四 · ★ 这一版留下的（未处置）

| # | 事项 | 为什么我没动 |
|---|---|---|
| 1 | **B2/B3/B4 共 10 件活未做** | ★ 本轮做到 B1 收口；★ 每件的**硬约束已在 `tasks.md` 逐条写好**（含 B2 的"官方没给 mark"、B4-1 的"StopMacro 会弹 Save As"） |
| 2 | **既有的一处 release_check 红**：`tools/verify_union_349.py:112` 的变换未自证 | ★ 该文件自 `38bd4f3c` 起**未改过**，**不是我造成的**；★ 而本仓红线写着「tools/ 的探针/证据脚本**只报不动**」⇒ **未处置，留给该文件的作者** |
| 3 | `docs/*.md` 的几个生成物**在我开工前就是脏的**（另一条线留下的） | ★ 遵循「两个对话同仓 ⇒ 只写自己那一个文件」⇒ **没有顺手扫进我的提交** |
| 4 | 上一版 §六 的 6 条（273 缓办 · recon-206 漂移 · `RunMacro2` Remarks · `auto_center_marks` · SW 归属 · 逐字复述 2 处） | ★ 全部**原样未动**（★ 仍是业主待决项） |

## 五 · 本版提交（可 `git log` 复核；两次收尾链均绿，聚焦测试 25 passed）

```
3384c8b  规格 209 · B1 批收口：idx 209 move_body 落地 + 修掉我自己写的一处「静默空转判据」
8c868a4  规格 209 · B1 批：把规格 207 的 4 件采纳候选落地（真机全过 + 抓到 2 处官方与真机不一致）
```

---

# ★★ 本版（2026-10-05）：规格 206 / 207 收口

## 〇 · 一句话现状 + 三条自查命令

```powershell
python tools\close_spec207.py      # ⇒ verify 273/273 · deep 76/76 ⇒ 349/349；SC 全绿 exit 0
python tools\list_adoptable.py     # ⇒ 采纳 18 · 缓办 11 · 不做 47
(Select-String -Path specs\206-c1c6-harvest\tasks.md -Pattern '^\s*-\s*\[ \]').Count   # ⇒ 0
```

## 一 · 规格 207 干了什么，结论是什么

**把一份 349 条的「四家外部项目有、我们可能没有」缺口清单逐条核实。**

| 口径 | 值 |
|---|---|
| 分类器**自述**（不是实测） | 273/349 = **78.2%** 打成「①已有等价物」 |
| **逐条实测**（273/273 全覆盖） | 确认已有 **208** · 其实没有 **62** · 查不到 **3** |
| ★★ 「已有」这一标的**错判率** | **62/270 = 23.0%**，**100% 单向乐观**（反向 0） |
| deep 档 76 条逐条读完 | **采纳 18** · 缓办 11 · **不做 47** |

**三条主结论**（见 `docs/recon-207/union-verify-summary.md`，已写成**事实 559**）：
1. **词面覆盖率（`best_cov`）没有判别力**：① 档错法是**乐观**、②③ 档错法是**悲观**，还有**第三种**——
   `cov=0.0` 把**抽取噪声**判成强候选（`217` 是别家 demo 参数字典的键名 · `221` 是文档类型字符串）。★ **调阈值救不了**。
2. **「缺口清单的长度」几乎是噪声**：349 条的清单，真实待办 **18 条（5%）**。
3. **深调（bunny 逐条读官方）的价值高于分类器**：它逼人去读官方**做同一件事的别的入口**。
   ★ 实例：我曾断言「宏录制成员零命中 ⇒ 别家幻觉」，**只对一半** —— 名字确实不存在，
   但能力可达（真入口 `RecordLine` + `RunCommand` + 事件通知，三样都在官方源里）。

**交付物**：`specs/207-union-gap-verify/` · `docs/recon-207/adjudication.md`（**九节五批**逐条裁决 + 三条横向纪律）·
`docs/recon-207/union-verify-summary.md` · 事实 **559** · 工具 `close_spec207.py` / `check_spec207_sc.py` /
`build_union_verify_349.py` / `list_adoptable.py` / `verify_union_349.py` / `report_false_positive_rate.py` / `audit_bunny_routing.py`。

## 二 · ★★ 下一件该干的活：实现那 18 条

`docs/recon-207/adjudication.md` 每条都有：官方成员（**逐字签名**）· mark 表 · 建议工具名与落点模块 · 验证判据 ·
**风险（含"本机 pywin32 后端能不能到"）**。**排活顺序裁决书已给**：

| 批 | 条目 | 为什么这个顺序 |
|---|---|---|
| **B1**（最干净） | `209 move_body` · `97 display_states` · `79 construction_geometry` · `235+236 rebuild`（**合并成一条三档 mode**）· `244 referenced_documents` | 官方页最全（`209` 有 signature + 逐字 mark 表 1/2/4/8 + 示例调用序）；零参或普通 COM；落点都是**已有模块** |
| **B2**（须真机定前置） | `336 unfold` · `34 balloon` · `52 centerline` | 官方**没给 mark** 或**两家结论矛盾** ⇒ 必须先真机定出可建形态 |
| **B3**（先小验证） | `115 edges` + `145 faces`（**一条工具**，FACE/EDGE/VERTEX） | ★ 本会话**已真机确证** `IBody2::GetEdges` / `GetFaces` **可用**（欧拉公式 `V−E+F=2` 成立）⇒ 可动手 |

**★ 三条只有裁判能加的硬约束（照做，否则会做出静默错的东西）**：
1. `235/236`：`EditRebuild3` 是**方法不是属性** —— 别家都当属性读，照抄会拿到 bound method，**拿它当判据会永远为真**。
2. `97`：官方逐字——「多个显示状态同时活动」时那条"第一个名字即活动"的规则**不成立** ⇒ 输出必须带 `ambiguous`，不许替调用方猜。
3. `244`：官方逐字——**Library features 不会返回** ⇒ doc 必须写明这个盲区。

**★ 一条危险项（不许当普通缺口补）**：`execute_workflow`（idx 123）—— 别家是**空壳 + 自标 simulated**，
而它字面承诺的 "parallel execution" **正面撞上事实 24**（单实例 COM 并发会死锁）。

## 三 · 规格 206：7 项全收口

★ **其中 5 项是「交付物早已存在、只缺机械核一遍」**（T5-1 · T5-2 · T5-3 · T3-2 · T4-3）—— 每项都带**可复跑证据**：
- **T5-1**：`scripts/check_fact_single_home.py`（告警级 exit 0）**且已真正接进 `release_check.py`**
  （**5 处**：helper + 调用点 + `_gate_results` + 返回体 + `docs/gate-classification.json`）
  ⇒ 元门禁 `[PASS] 30 个门禁全部已接线`。
- **T3-2**：★ 证据最硬 —— `tools/t3_2_spelling_pairs.py` **复跑**输出「真名 1529 · spelling 554 · 配对 130」
  与文档**逐字吻合**。
- **T5-2 / T5-3 / T4-3**：提交号 / 文件字节数 / `AGENTS.md` 行号可核。

**T2-6 真机验证**（本会话新做）：①②③④ **真机确认**（判据 = **回读计数**或**几何预期**，不是返回值）：
`GetEdges` 回 **12** 条边 · `GetBodies2` 前置成立 · `GetSelectedObject6` 选中→回读 **1** ·
`ClearSelection2` 清空后回读 **0** · 且满足**欧拉公式** `V−E+F = 8−12+6 = 2`。
★ ⑤ `AccessSelections` **不重跑** —— `probe_access_selections.py` 与**事实 47** 已给真机结果
（`0x80010105` 同码 · **20+ 形态穷尽**）；★ 重跑正违反本仓规矩「不要再用『换个参数试试』的方式继续试」。

## 四 · ★ 怎么干活（照这个来，别自创）

```powershell
# 每轮收尾（一条命令）
pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests\<改过的>.py
# ★ 全量 pytest 只在两种情况下跑：发布前 · 改了 sw_connect.py 或门禁本体

# 提交（★ 纪律，别绕）
git reset -q                                        # ★ 先清索引，见 §五 trap 1
python tools\commit_mine.py -m <信息文件> <路径…>     # ★ 信息先写成文件

# 真机（★ 2026-10-05 授权已变更：可自行拉起、用完必须关闭）
$env:PYTHONIOENCODING='utf-8'                       # ★ 不加会因 GBK 打印 ✓/✗ 而崩
python tools\reclaim_solidworks.py --restart        # 起（自带安全判定：有别人的文档就拒绝）
python tools\reclaim_solidworks.py --close          # 关（★ 只关归属标记是自己启动的那个）

# 派活（★ 必须走 bunny）+ 实证路由
python tools\audit_bunny_routing.py --marker <你这批产物路径关键词>   # ⇒ 期望「合规 N · 异常 0」
```

**派活形状（★ 用事故换来的）**：一片 **≤8 条** · ★ **「每判完一条就立刻写文件」写成硬约束** ·
★ **「查不到」是合法交付不是失败**，并明确**不许为了凑数而猜**（只差几条时压力最大，最容易发生）。

## 五 · ★★ 本版新增的 4 个陷阱（照单避开）

1. ★★★ **`round_chain.ps1` 里有三处 `git add -A`**（L84/L117/L142）⇒ 跑完链，**索引里会塞进几百个别线的文件**
   （`specs/203-*`、`specs/204-*`、`docs/recon/*`、生成物…）。**直接 `git commit` 会全扫进去**。
   ⇒ ★ **永远先 `git reset -q`，再 `git add <只你自己的路径>`**。`commit_mine.py` 的**删除守卫**会拦；
   ★ **那是守卫在尽职** —— 别用 `--allow-deletions` 糊过去，**先看清那 N 行是不是你的**。
2. ★★ **`.git/index.lock` 会变陈旧锁**（我遇到 0 字节残留）⇒ `reset/add/commit` **全部静默失败**
   （只报 "Another git process seems to be running"）。**先确认没有 git 进程，再删锁**。
3. ★★ **「0 个新文件」≠「空转」** —— 我因此**误杀过两个 bunny**（其中一个正在写）。
   ★ 正确判据是**最后写入时间**：
   `Get-ChildItem output\<目录> -Filter *.json | Sort-Object LastWriteTime -Descending | Select -First 3`。
   ★ 且 **`wait_agent` 只在成员状态/信箱变化时唤醒，写文件不触发** ⇒ 超时**不代表**没进展。
4. ★★ **判据会静默读过时产物** —— 我的 SC 检查器曾报「330/349」而逐条实为 335。
   ★ 修法：**先算生数、与产物里的数比对，不一致就大声报**。
   ★ 同类：**会喊狼的守卫会被无视**（三例：`list_agents` 对 inactive 误报 · 审计器把 Lead 自己报成违规 ·
   我的 SC-8 判据把**"防它的文档"**报成违规）⇒ ★ 修法：**排除自身 + 把"引用"与"断言"分开**，
   并把判据的**已知边界写进输出**。

## 六 · ★ 我留下、需要你决定的（未处置）

| # | 事项 | 为什么我没动 |
|---|---|---|
| 1 | **18 条采纳候选未实现** | 规格 207 只做「核实」不做「实现」⇒ **该起新规格** |
| 2 | `docs/recon-206/more-specific-audit.md` 的 **7+/8− 漂移** | 两条路都要业主定：接受重新生成的版本 / 把那句人工结论写进生成器模板 |
| 3 | `RunMacro2` 的官方页**有** Remarks，而 `capabilities.yaml` 写着"是空的" | 按铁律 4 应以官方源为准更正，但那是**别处的清单**，我只记录 |
| 4 | `auto_center_marks` 的**批量路 `AutoInsertCenterMarks2` 从未单独真机验证** | 现有 `verified` 标签**覆盖不到那条路** |
| 5 | SolidWorks **此刻可能在跑**（重启后 `PID=38500`） | ★ **归属证不出来** ⇒ 按纪律「**证不出归属就不动**」**我没关它** |
| 6 | `check_fact_single_home.py` 认出 **2 处逐字复述**（`docs/dead-ends.md` 复述事实 230 · `specs/202-*/.../vd50-A-surface.md` 复述事实 303） | 两处都在**别人的规格目录/生成物**里，写盘边界不由我改 |

## 七 · 本版提交（可 `git log` 复核；链均绿 8 passed）

```
10e55dee 补齐本会话产出但一直未入库的 5 个工具
4b6dbe3a spec 206 · T2-6 收口：5 条前置全部有判据
d386839a spec 206 · T2-6 第二批真机结果（③④ 成立）
5d9411db spec 206 · T2-6 第一批真机结果 + 按授权改纪律
683410f5 spec 207 · 收尾措辞：把"部分/未定案"改成定案值
788a19f  spec 207 · 收尾：deep 76/76 ⇒ SC 全绿 + 第五批裁决
2359e9b  spec 207 · 新增收尾链 tools/close_spec207.py
623a63d  spec 207 · SC 检查器退出码语义：只有"全绿"才 exit 0
c1b1af4  spec 207 · V7-1b 聚合件（SC-1/SC-5 的落地件）
086303e  spec 206 · T5-1 接线完成（5 处全落地，元门禁放行）
```

## 八 · 一句话给接手的人

**别信"清单长度"，信逐条读数；别信返回值，信回读；别信别家的名字，信官方页；
别信"我记得做了"，信一条能重跑的命令。** —— ★ 这四句是本会话每一次翻车的根因。

---

# 上一版内容（2026-10-04 · ★ 原样保留）

> ⚠ 下面是上一版交接（24h 三阶段主线 / 环境陷阱 / 工具栏台账）。★ 它讲的两条线（`specs/202-user-coverage-gaps`
> 等）**与本版不是同一批活** ⇒ 若你要接的是那些线，读下面这段；★ 若接的是规格 206/207，**读上面的本版即可**。

---

## 〇、一句话现状

> ★ 仓库同时在跑**两条线**：
> ★ **线 A · 工具栏「不能项」攻关** —— 台账 **119** 条 ⇒ 已能 **83** · 可攻关 **3** · 待查 20 · 待验证 6 · 后端到不了 7。
> ★ **线 B · 24h 三阶段主线**（`specs/202-user-coverage-gaps`）—— **先把「已完成」核真 → 再把「没核过的」核全 → 最后才补新能力**。
> ★ 手法固定为：**查官方三源 → 按六条铁律立柱 → 实现包装 → 真机实测 → 加静态门禁**。

| 指标 | 当前值（★ 2026-10-04 实测） |
|---|---|
| 提交数 | **998** |
| `capabilities.yaml` | **110** 条（`verified` **97** · `stitched` **11** · `not_implemented` **2**） |
| `docs/known-facts.md` | **4138** 行 · 编号最大 **515** · 条目 **513** |
| `docs/toolbar-ledger.json` | **119** 条 |
| `release_check.py` 的 `_run_*gate` 函数 | **30** 个 |
| 真机证据 | `output/` 下 **481** 个 `.json` |
| 测试文件 | `tests/test_*.py` **249** 个 |

★ **线 B 的三阶段结论**（详见 `docs/final-report-24h.md`，那边每轮刷新）：
① 收口核对：判据 A 可疑 **0 条**、判据 B 证据路径覆盖 **96/96 = 100%**；
② 废弃成员：真命中 **37**（生产 **6**，**全部已处置 ⇒ 生产侧待办 = 0**）；
③ 缺口地图三条收敛判据**全达标**（无处可放率 **7.85%** ≤ 20 · 空格率 **19.33%** ≤ 60 · 双源一致率 **44.42%** ≥ 30）。
⚠ ③ 的 ①② 是**轮 99「补词」**做的，**不是**近期做的 —— 别把功劳算错。

---

## 一、★ 先读这六份（顺序别换）

```
① D:\AI\SW\AGENTS.md                        ← ★ 常驻纪律（六条铁律 / 验收标准 / 红线）
② docs/known-facts.md                       ← ★ 事实表（513 条；★ 遇事先查它，别重走）
③ docs/dead-ends.md                         ← ★ 走死的路（由 gen_dead_ends.py 生成，别手改）
④ docs/toolbar-ledger-verified.json         ← ★ 台账（★ 每条带 tier + note，★ note 里常写着"下一步"）
⑤ docs/toolbar-gaps-backend-limits.md       ← ★ 后端到不了的**依据**集中在这
⑥ docs/final-report-24h.md                  ← ★ 线 B 的收口报告（做成了 / 没做成 / 为什么 / 下一步）
```

★ 另有 **`~/.dsh/AGENTS.md`**（用户全局层，每轮自动注入）与 **`~/.dsh/纪律/`**（纪律正文，含**资源与环境**）。
★ 另有 **[`docs/team-roles.md`](team-roles.md)** —— ★ 怎么派便宜模型助手（★ 含本轮的实测坑）。
★ 另有 **[`docs/kickoff-bunny-sideline.md`](kickoff-bunny-sideline.md)** —— ★ 给**支线对话**的第一句话模板（批量辅助活全派 Bunny）。
★ 另有 **[`docs/recon/`](recon/)** —— ★ 批量产物落点（含 `README.md` 记着判据与待决断）。

---

## 二、★★★ 环境陷阱（★ 这一节最值钱 —— 都是**实测踩出来的**）

### 2.1 ★ SolidWorks 相关

| 陷阱 | 事实编号 | 正确做法 |
|---|---|---|
| **实体（边/面）按坐标选**（`SelectByID2("","EDGE",x,y,z,…)`）**选不中** | 32 / 482 / 483 | ★ 用 **`IEntity.Select4`（按对象选）**；本仓封装：`sw_selection_spec.entities_on_body` + `select_object` |
| ★ **`Select4` 没有 `mark` 参数** | — | ★ 选完用 **`ISelectionMgr.SetSelectedObjectMark(i, mark, -1)`** 补设 |
| ★ **发射线前不 `ClearSelection2(True)` 会留残留对象** | 479 | ★ 发射线前**先清选区** |
| ★ **官方 `## Examples` 段给的是"调用序"** | 480 / 482 | ★ **读例子**（签名与 Remarks 都给不出调用序） |
| ★ **台账/文档里 `api` 名可能是已废弃的旧入口** | 433 / 476 | ★ **读那个 md 头顶那句 `Obsolete`** —— 继任者名字就在那句里 |
| ★ 能力层**回 `False` / `None` 不等于失败** | 482 | ★ 例：`SketchOffsetOnSurface` 回 `False` 是**正常的** |
| ★ **跑真机一律走护栏** | — | ★ `python tools/sw_guard.py --timeout N -- python <脚本>` |

### 2.2 ★★ 资源与环境（★ 本轮业主当场点破两件事）

| 陷阱 | 正确做法 |
|---|---|
| ★ **用完了不关 SolidWorks** | ★ 纪律逐字：**「一轮真机活收尾时它是关着的」**、**「跨轮不许留 —— 收尾链跑完就关」**。★ 本轮实测代价：`cwbcbfmesh` 一度涨到 **24.6 GB**（纪律记的另一例是 8286 MB）⇒ **"我会记得"不是机制** |
| ★ **关的时候误杀别的会话** | ★ **只关自己启动的**。正解：`sw_connect` 在**它自己启动**实例那一刻把 PID 落进 `output/.sw-started-by-us.json`；`tools/reclaim_solidworks.py --close` **只认那个标记**，没有标记就**拒绝关闭** |
| ★ **`--restart` 不能当"关"用** | ★ 它是"停完**重连**" ⇒ **重连又把它拉起来**（实测：kill 掉 28539 MB 那 9 个进程后几秒它回来、PID 全新） |
| ★ **`_OURS = (零件\|Part)\d+\|^MCP_` 这种按文档名的判据分不出是谁的** | ★ 别人的会话也多半开着 `零件N`；★ 而**若别人没开文档** ⇒ 判据通过 ⇒ 照样误杀 |

### 2.3 ★★ 工具/操作相关（★ 它们反复咬我）

| 陷阱 | 症状 | 正确做法 |
|---|---|---|
| ★★ **`git add -A` 放进索引的东西，后续 `git add <路径>` 撤不出来** | 只想加自己的 6 个文件，暂存区里却有别人的在途件 | ★ 先 **`git reset`**（只清索引、不动工作树），再按路径 add |
| ★★ **`git checkout -- <file>` 的源是**索引**、不是 HEAD** | 已 `git add` 过坏内容 ⇒ 恢复不掉 | ★ 用 **`git checkout HEAD -- <file>`** |
| ★★ **两个对话同仓，作者名分不开** | 最近提交作者全写 `DSH Lead` | ★ **只用显式路径 add**；★ **临时文件名带自己前缀**（本轮差点覆盖别人同名的 `_commit_msg_810.txt`，是文件系统"先读再写"策略挡住的） |
| ★★ **job 返回通道会截断** | 175 KB 的批量结果**被截在 60,159 字节丢了** | ★ **大批量产物落成文件**，返回通道只传摘要 |
| ★ **`edit` 的 `old_string` 不匹配** | 明明文件里有那行 | ★ 文件里存的可能是**字面转义文本** ⇒ **按磁盘上的真实形态匹配** |
| ★ **长内容内联进 Python 源码** | 引号被吃 / `IndentationError` | ★ **先写成独立文件**，再用最短脚本搬运（★ 事实 48） |
| ★ **脚本语法错 ⇒ 内容没落盘，而 `git commit` 照跑** | 「假提交」 | ★ 批量脚本跑完**必须回读目标文件** |
| ★ **`Path("D:")` 不是盘根** | 路径缺反斜杠 | ★ 用 `Path("D:/")`（★ 事实 59） |
| ★ **PowerShell 把单元素数组拆成标量** | 取 `$parts[0]` 得到的是**第一个字符** | ★ 用 `@()` 兜住（★ 本轮 Bunny 自己发现并记下） |
| ★ **`python -c` 里带引号/反引号的中文串** | `SyntaxError: unterminated string literal` | ★ 写文件，别写 `-c` |

---

## 三、★ 每轮的标准动作（★ 照抄即可）

```powershell
# ① 收尾链（★ 一条命令：生成器 + release_check 18 道门禁 + 聚焦测试 + ★ 关 SolidWorks）
pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests\<改过的>.py

# ② 真机探针（★ 一律带护栏）
python -u tools\sw_guard.py --timeout 900 -- python tools\<探针>.py

# ③ 提交（★ 一律用文件；★ 先 git reset 再按路径 add）
git reset; git add <我改过的那几个路径>; git add <消息文件>.txt
& git -c user.name='DSH Lead' -c user.email='dsh@local' commit -F '<消息文件>.txt'
```

★ **全量 pytest 只在两种情况跑**：① 发布前；② 改了 `sw_connect.py` 或门禁本体（★ ~160 s）。
★ **改了门禁之后必须**：接进 `release_check.py`（三处）+ 登记 `docs/gate-classification.json` + 写**负例测试**（★ 事实 62）。

---

## 四、★★ 团队与批量扇出（★ 本版**大改** —— 上一版这一节已过期）

```
★ `spawn_teammate` 有名额上限 **8**（实测报 `Team member limit 8 reached`），且**没有"移除成员"的工具**。
★ 要规模 ⇒ 用 **`workflow`**：写一段 JS，`parallel(thunks)` 或 `pipeline(items, 阶)` 把活扇出到任意多子代理。
   ★★ 实测已跑过 **100 路**（`parallel`），回 99 路、失败 1 路，**逐路失败名单可读**。

★★ 三条实测坑（不写会重踩）：
   ① **`agent()` 的 opts 里 `provider` 与 `model` 必须成对写。**
      只写 `model: "space-bunny-free"` ⇒ **整批静默失败**：`{requested:100, returned:0, rows:[]}`，
      **返回值里没有任何错误信息**。正解：`provider: "opencode-zen", model: "space-bunny-free"`。
   ② **并发默认只放 16 路，其余排队**（不是失败）。
      源码 `packages/workflow/workflow-ptc/src/index.ts` 逐字：
        maxConcurrentAgents: this.config.maxConcurrentAgents === 0
          ? Math.min(16, Math.max(1, availableParallelism() - 2)) : this.config.maxConcurrentAgents
      ★ **`min(16, …)` 是硬上限**（本机 28 核 ⇒ 16），且**与模型无关** —— 别把它当成"Bunny 比较慢"。
      ★ 要突破：在 `~/.dsh/profiles/web/cordis.patch.yml` 的**两个** `workflow-ptc` 块的 `config:` 下加
        `maxConcurrentAgents: <N>`（缩进 18 空格），**重启 DSH 才生效**。
   ③ **先跑 2–3 路"判据探针"再铺全量** —— 挑**极端形态**的样本（全属性族 / 全 `ISet*` 族），
      不是随机挑。★ 本轮就是漏了这步：先验了"管子通不通"，没验"水流出来干不干净"。

★ **模型必须选 Bunny**（业主明确：DeepSeek 做子代理**太贵**）。
   `role="artist"` 路由到 `space-bunny-free`；`$DSH_HOME/team-roles.yaml` 里 `worker`/`reviewer`/`researcher`
   也已指向 Bunny。★ workflow 里则显式写 `provider` + `model`。
```

---

## 五、★★★ 一条**本轮最值钱**的方法论（★ 比任何单个能力都值钱）

**把判据交出去批量执行，能得到我自己逐个读发现不了的样本量。**
本轮 100 路同时指出我给的判据有**四个洞**（详见 `docs/recon/family-scan-100-criteria-defects.md`）：
① **指针串常常不在 `## Returns` 段**（`IMacroFeatureData` 17 个全在 `## Parameters` ⇒ 报 0）；
② **废弃标记有变体**（`INote` 严格 13 vs 宽松 **31**）；
③ **「零参可读」把属性也算进去**（`IDSPBRMaterial` **52 = 52 个属性** ⇒ 该列退化成成员总数）；
④ **官方原文有笔误**（`in-porcess`）。
⇒ **四条都在 8 个以上的族里独立复现** —— 人工抽读永远发现不了。

**⇒ 两条定则**：
- ★★ **判据里"合并"是危险的**：把「方法」与「属性」合成一个"零参可读"、把「Returns 段命中」与
  「别处命中」合成一个"指针"，**列名在两族里就会含义不同 ⇒ 不能跨族比较**。能拆就拆。
- ★★ **凡"结果要能完整落盘"的批量活，产出必须落成文件** —— 返回通道只传摘要。

---

## 六、★ 剩下的活

### 6.1 线 A（工具栏）
- **可攻关 3 条**（★ 每条 `note` 里已写明卡在哪）；**待查 20 · 待验证 6**（★ 都在台账 `tier` 字段里）；
- **后端到不了 7 条**（★ 共同依据：那些 `*FeatureData` 带 `AccessSelections`，★ 而它第 2 参四种形态全到不了，★ 事实 474）⇒ ★ **别重复攻**。

### 6.2 线 B（24h 主线，★ 详见 `docs/final-report-24h.md`）
- ★ **未定案三条**：`rib` 在真机建不成（★ 连试 6 次、换 4 个变量 ⇒ **按事实 53 结题**，别再无变量地重试）·
  `ISweepFeatureData` 一族里仍有部分口径待定 · 阶段 4「补 `api-pre` 缺的两域」只开了头。
- ★ **工程图读侧**已做两批（注释族 + 折弯线/螺纹/基准/中心线四个计数），★ **`IView` 的零参可读候选还有约 200 个**。
- ★ **判据的洞要修，但别擅改已发布的数字**：修法建议是**拆列**（见 §五），不是就地改判据。

---

## 七、★★ 方法论（★ 上一版的血泪 + 本轮新增）

1. ★ **官方文档是第 0 步，不是"试不出来再去查"**（★ 顺序：官方页 → `dead-ends.md` → 该能力 `limitations` → `known-facts.md` → 动手）
2. ★ **官方材料的排序**：★ **`## Examples` > `## Remarks` > 签名**（★ 只有例子给得出**调用序**）
3. ★ **"一个探针全面失败时，先看错误信息写的是谁的名字"** —— ★ 写着自己函数名的就是我的错
4. ★ **失败几乎总是我这边**
5. ★ **两格都回同一对象时，"回了对象"不是判据** ⇒ ★ 去读**那个对象自己的成员**（★ 空壳 vs 真对象）
6. ★ **"十格全 `None` 而全不报错"是有信息量的否证**
7. ★ **排除一个候选因，就是一步进展**
8. ★ **把结论挂在被结论所指的那条记录上**（★ 台账那行的 `note`）
9. ★★ **本轮新增 · 「查不到」≠「我搜的名不对」** —— 目录名可能带 `I` 前缀（`SketchManager` vs `ISketchManager`）；
   ★ **先按词根搜目录，再说查不到**。
10. ★★ **本轮新增 · 读别人的产物前先把它打出来**（`type` + `len` + 第一项）—— ★ 本轮**同一天三次**取错字段/猜错形状，
    其中**两次直接把结论拉反**。
11. ★★ **本轮新增 · 收尾链报红时，先看红的是不是我改的东西** —— 本仓有并行对话，门禁有**竞态窗口**。
12. ★★ **本轮新增 · "我会记得"不是机制** —— 该每轮做的事（关 SolidWorks / 清理 / 计数同步）都要**接进收尾链**。

---

## 八、★ 红线（★ 任何模式都不豁免）

```
· ★ 不 git push（任何远端）· 不建目标远端仓库 · 不发 release
· ★ 不删用户数据 · 不动注册表 / 系统环境变量（★ 只改用户级 $DSH_HOME）
· ★ 破解相关零接触
· ★ `origin` 故意留空（★ 防裸 push 误推上游）；上游叫 `upstream`（★ 只登记未 fetch）
· ★ 提交一律 `git commit -F <文件>`；★ 且先 `git reset` 再按路径 add
· ★ 不手改生成物：docs/toolbar-ledger.json / -verified.json / dead-ends.md（★ 都由 tools/ 下生成器产出）
· ★ 探针/证据脚本（tools/）**只报不动**（★ 改了会破坏"证据不可变"）
· ★ 两个对话同仓 ⇒ **只写自己那一个文件**，不要顺手整理、不要批量重排
```

---

## 九、★ 一条可复制的"攻关单元"模板

```
① ★ 从台账里挑一条 tier == "可攻关"（★ 先读它的 note —— 常常已写明卡在哪）
② ★ 读官方页三样：签名 + ## Remarks + ## **Examples**（★ 例子优先）
③ ★ 若 api 是旧入口 ⇒ ★ 读 md 头顶的 Obsolete 找继任者
④ ★ 写探针（★ 带来源块：六字段 + 写明读的是哪一页/哪个例子）
⑤ ★ 真机跑（★ sw_guard.py），★ 判据 = 特征树增量 / 段数增量（★ 规则 6）
⑥ ★ 成 ⇒ 登记 capabilities.yaml（★ level: verified + evidence + limitations）；
      ★ 不成 ⇒ 记 known-facts.md（★ **含"下一步"**）
⑦ ★ 更新台账那行的 note
⑧ ★ 收尾链 + 提交
⑨ ★★ **收工关 SolidWorks**（★ `python tools/reclaim_solidworks.py --close` —— 只关自己启动的）
```
