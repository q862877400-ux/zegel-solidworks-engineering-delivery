# `pre_call` 候选裁决 —— A / B / C 三份逐条比

> 裁判日期 2026-10-03 · 仓库 `D:\AI\SW` · 候选目录 `specs/202-user-coverage-gaps/recon/precall-cand/`
> **方法**：逐份读三份候选 → 逐条打开官方页（`C:\swapi\types\` · `C:\swapi\examples\` · `C:\swapi\docs\`）与仓内那六个 spec / 目标函数 / 选区底座**核对**，不采信任何候选的自述。
> **覆盖**：mold_parting_line · mold_parting_surface · part_wrap · part_sweep · part_loft · part_axis。
> ⚠ **三份候选都没有在本机跑过**（铁律 2），本裁决只判「依据强度 / 回读纪律 / 字段是否真声明 / mark 是否官方给定」。

---

## 〇 · 一句话结论

- **A** 证据最省（只做模具三条），但**把全部面/边压在一条自己都标「未证实」的 `ISelectData` 路上**，而官方恰恰给了两条**有例子**的路（`SelectByRay` / 按点 `SelectByID2`）它没用 ⇒ 三条模具与包覆**只能排第二**。
- **B** 有一条**致命的事实错误**（`Select4` 的签名），并且对 **`part_sweep` / `part_loft` 的仓内现状陈述是假的**（那两条**已经**有 `pre_call` 和 `param_alias`）⇒ 它的两条 pre_call **不可直接集成**；但它的**证据边界表述**（mark 查不到就写查不到、官方例子 4096k+2 不猜）是三份里最干净的。
- **C** 覆盖面最全、官方页引用**逐条可 grep 命中**、对「没查到什么」最坦白；主要硬伤是**放样引导线 mark 算式写错却声称与官方一致**，以及**它给 sweep/loft 的 `param_alias` 会顶掉仓内已有的映射 ⇒ 集成即 `TypeError`**。
- ★ **推荐以 C 为主干，逐处按本文件 §三 的表格替换。**

---

## 一 · 逐条比（按① 官方依据 ② 回读计数 ③ 字段真声明 ④ mark 是否官方给定）

图例：✅ 达标 · ⚠ 有瑕疵 · ❌ 不达标 · — 该候选不覆盖此条

### ① `solidworks_mold_parting_line`

| 候选 | ① 官方依据 | ② 回读 | ③ 字段真声明 | ④ mark | 判 |
|---|---|---|---|---|---|
| **A** | ✅ `InsertMoldPartingLine.md` §Remarks 整段逐字 + mark 表（**已核对，L23–32 原样**） | ✅ 每步 `_count_by_mark` | ✅ spec `tool_specs_batch1.py:109-121` **逐字对上**（只有 `draft_analysis`，行号也对） | ✅ 1 / 4 官方表 | ⚠ |
| **B** | — | — | — | — | — |
| **C** | ✅ 同页逐字（已核对）＋**更诚实的缺口标注**：「官方没有『创建分型线』的完整例子 ⇒ 『先 1 后 4』只依据 Remarks 的**行序**」 | ✅ 每一档 mark 都回读 | ⚠ 它没核对 batch1 的现状（见 §二·C-3 同源问题） | ✅ 1 / 4 | **✅ 胜** |

**为什么 C 压过 A**：A 的面/边选择**只有** `_select_one_with_mark`（`CreateSelectData`→`Select4`）这一条路，而 **A 自己在 `_pre_parting` 的文档串里写了「★★ 未证实：……本仓没有真机证据」**。C 的主路是 `SelectByRay` / 按点 `SelectByID2` —— 这两条**官方页逐字点名**（`SelectByID2.md` L93「Otherwise, you can call `IModelDocExtension::SelectByRay`」），`Select4(ISelectData)` 在 C 里只是**第三级兜底**。**把「未证实」放在兜底而不是主干，是本条的分水岭。**

### ② `solidworks_mold_parting_surface`

| 候选 | ① | ② | ③ | ④ | 判 |
|---|---|---|---|---|---|
| **A** | ✅ 同上 | ✅ | ✅ `tool_specs_batch9.py:54-70` 八参逐条对上，`param_alias={}` 也对上 | ✅ | **✅ 胜** |
| **C** | ✅ | ✅ | 同上 | ✅ | ⚠ |

**为什么 A 压过 C**：官方那句前置是**有条件的**（「**f a parting line feature does not yet exist in the model**」—— 已核对 `InsertMoldPartingSurface.md` L30 原文如此，且该页的 `ReverseAlignment` 参数描述里也重复了同一条件）。**只有 A 把它落成了可执行的分档**（`has_parting_line=True ⇒ 清选区并跳过`，A 的 `_pre_mold_parting_surface`）。C 的 `_pre_mold_parting_surface` **与分型线那份逐字相同**，条件只写在文档串里（「集成时建议先查有没有分型线特征」）—— **没写代码**。

### ③ `solidworks_part_wrap`

| 候选 | ① | ② | ③ | ④ | 判 |
|---|---|---|---|---|---|
| **A** | ✅ `InsertWrapFeature2.md` §Remarks mark 表逐字（已核对 L26–45）+ `Create_Wrap_Feature_on_Multiple_Faces_Example_VB.md`（**已核对 L53–59**） | ✅ | ✅ `tool_specs_batch50.py:31-54` 逐条对上（`wrap_type`/`thickness_mm`/`reverse`，无 `param_alias`） | ✅ 1/2/4 | ⚠ |
| **B** | ✅ 同上（连 L52 那句「Scribe ⇒ no pull direction entity」都对） | ✅ | ✅ 同上 | ✅ | ⚠ |
| **C** | ✅ **两个官方例子都引**（`Insert_Wrap_Feature_Example_VB.md` L43–46 逐字核对通过） | ✅ 每级都回读 | ⚠ 见 §二·C-3 | ✅ | **✅ 胜** |

**为什么 C 胜**：**只有 C 处理了「`Append=True` 打偏到已选中的实体会把它反选掉」这个坑** —— 它逐字引了 `SelectByID2.md` L30-31 / `SelectByRay.md` L33-34 的语义表（已核对），并因此在 `_select_by_ray` 里**每次打射线前先回读、够了就不打**。A 和 B 都只是「打一次」。

### ④ `solidworks_part_sweep`

| 候选 | ① | ② | ③ | ④ | 判 |
|---|---|---|---|---|---|
| **A** | — | — | — | — | — |
| **B** | ✅ `InsertProtrusionSwept3.md` §Remarks mark 表（**已核对 L39–45 逐字**）+ 例子 L57–60 | ✅ | ❌ **「现状」陈述为假**（见 §二·B-2） | ✅ 1/4/2 | ❌ |
| **C** | ✅ **扫描专文**（`Sweep Features and SweepFeatureData Objects.md` L20/27/39/49 —— **已核对，四个 mark 全中，含 mark=128**）+ `SelectByID2.md` L97/L99 | ✅ | ❌ 见 §二·C-2 | ✅ | **✅ 胜（含保留意见）** |

**C 的独有贡献（三份里只有它有）**：
1. **多段路径的 `SELOBJGROUP` 收口** —— `Select_Multiple_Paths_for_Sweep_Path_Example_VB.md` L61 `SelectByID2("Unknown","SELOBJGROUP",0,0,0,True,4,Nothing,0)`（**已核对**）。它同时**如实登记「没实现、效果未实测」**。
2. **方向向量 mark=128** —— 专文 L49 逐字，三份里只有 C 用到。
3. **端到端只给「中」** —— 因为 `sw_sweep.py` L103-109 已把轮 488 的 A/B 写死：`CreateDefinition(17)` 之后 `AccessSelections` 回 `0x80010105`，**两路都卡住**。

### ⑤ `solidworks_part_loft`

| 候选 | ① | ② | ③ | ④ | 判 |
|---|---|---|---|---|---|
| **B** | ✅ `InsertProtrusionBlend2.md` §Remarks **完整 mark 表**（**已核对 L74–88：1/2/4/8/16/32/64 全中**）+「顺序必须与放样方向一致」（L68 逐字） | ✅ | ❌ 现状陈述为假（同 B-2） | ✅ 轮廓 1 | **✅ 胜** |
| **C** | ❌ **算式写错还声称一致**（见 §二·C-1） | ✅ | ❌ 同 C-2 | ❌ 引导线 | ❌ |

### ⑥ `solidworks_part_axis`

| 候选 | ① | ② | ③ | ④ | 判 |
|---|---|---|---|---|---|
| **B** | ✅★ **最干净的边界表述**：`InsertAxis2.md` **整页无 `## Remarks`**（**已核对，只有 Signature/Parameters/Returns/Examples/See Also**）⇒「官方**没给 mark 表**，下面的 0 不是从 Remarks 推的」 | ✅ | ⚠ 现状：确实**无** `pre_call`（**这条 B 说对了**） | ⚠ **例子推断值 0**（B 自己标了） | **✅ 胜** |
| **C** | ✅ 同上，且额外列明「**我没有做的事**」 | ✅ | ⚠ 同上 | ⚠ 同上 | ✅ |

**两者打平的原因**：`sw_part.create_axis_report`（L1588）回读的是 **`GetSelectedObjectCount2(-1)`（全选区）** —— **它压根不看 mark** ⇒ mark 对不对都不影响功能。B 的优势在于**把结论推到尽头**：「若 Lead 认为『无 Remarks 背书』就不能落 mark ⇒ 那本条只能标 `stitched`、且 pre_call 应只回读总数」。C 的优势在**选择器更好用**（`plane:`/`axis:`/`+z`/`index:` 四种）。

---

## 二 · 每一份的错（逐条，均已开官方页 / spec 核对）

### A —— 2 处

**A-1 ★★（可复现的集成缺陷）** A 在文末给的退路：
> 「把 `_select_one_with_mark` 的函数体换成 `return sw_part._select_com_object(obj, append=append, mark=mark)` 即可」

**这一句漏了 `model=model`。** `sw_part.py:331` 的分支是 **「`if model is not None` 才先走 `Select4` + `ISelectData`」** ⇒ 不传 `model`，`_select_com_object` 就**跳过修复后的第一条路，直接落到 ② `Select2(append, mark)`（官方已标 Obsolete）** —— **正是 A 声称要避开的那条**。⇒ 照抄 A 的退路，会把 2026-10-03（轮 535）刚修好的 mark 路径**退回废弃成员**。正确写法是 `_select_com_object(obj, append=append, mark=mark, **model=model**)`。

**A-2 ★** A 断言「`sw_part._select_com_object` ……**先试** `Select2(append, mark)`」（来源块 L45–46、文末 L531–534）。**这句在 2026-10-03 之后已不成立**：该函数现在的顺序是 **① `Select4`+`ISelectData`（仅当传了 `model`）→ ② `Select2` → ③ `Select4`+空 Callout**（`sw_part.py:331-360`）。
　※ 严格说，A 在谈 **batch74 的调用点**时是对的 —— `tool_specs_batch74.py:127` 确实是 `_select_com_object(face, append=…, mark=mark)`、**没传 `model`** ⇒ 那一处今天仍然走 `Select2`。**但 A 把一个调用点的性质说成了整个函数的性质，于是错过了唯一正确的解法（传 `model`）。**

**A 的优点（也要记）**：`has_parting_line` 分档是三份里唯一**可执行**的条件处理；`_pull_direction` 允许「有名字的基准面/轴」与「面」两条路分流；`param` 描述里把每个字段的官方出处写进 description。

### B —— 6 处

**B-1 ★★★（致命，架构前提错）** B 的来源块 L31–34 与 L289–290：
> 「★ `Select4` **没有 mark 参数**（只有 `Append, Callout`）⇒ 走对象选择的 mark 会丢」

**官方签名是 `System.bool Select4( System.bool Append, SelectData Data )`**（`C:\swapi\types\IEntity\Select4.md` L14，**已核对**）—— 第 2 参是 **`ISelectData`**，不是 `Callout`。传 `Callout` 的那种形状是**仓内 `sw_part.py` 的第三级遗留回退分支**（L352–359，注释自己写着「⚠ 它丢 mark，已知」），**不是官方签名**。
⇒ **B 把一个遗留分支当成了接口定义**，而它整套「禁止 `Select4`、一切走 `SelectByID2`/`SelectByRay`」的选择架构**建立在这条错误前提上**。

**B-2 ★★★（事实错误 + 集成即坏）** B 的 `INTEGRATION_NOTES` 写：
> ① sweep「现状：params 只有 `cut`(bool)；无 pre_call；无任何 selection 参数」
> ② loft「现状：params 只有 `closed`(bool) / `use_selected_profiles`(bool)；无 pre_call」

**两句都是假的。** 仓内现状（**已核对**）：
- `tool_specs_batch48.py:51` —— `pre_call=_pre_sweep_sketches`（从 `tool_specs_batch4` 导入），`param_alias={"profile_sketch": None, "path_sketch": None}`，`params` 里 `profile_sketch`/`path_sketch`/`cut` **都已声明**。
- `tool_specs_batch47.py:40` —— `pre_call=_pre_loft_profiles`，`param_alias={"profile_sketches": None}`，`Param("profile_sketches", list, …)` **已声明**。
⇒ B 会**用一份「现状是空白」的方案去覆盖两段已存在、且带回读门禁（`_select_sketches_in_order` 不够就抛）的代码。**

**B-3 ★★** B 的 `_model()` 理由：
> 「为什么不用 `connect_solidworks()` 直接连：`pre_call` 跑在 `RESOLVERS["model"]` **之后** ⇒ ★ 再自己连一次会**第二次清选区**」

**`register_capabilities.resolve_model` 就是 `connect_solidworks`** —— `register_capabilities.py:47-60`：`resolve_model` → `_connect()` → `connect_solidworks(wait_seconds=20, return_metadata=True)`。⇒ **B 自己走的那条路同样会再清一次**（隔离证据 `output/selection-lifetime-evidence.json` 第 8 步 `mark1: 2 → 0` 就发生在这一步，**已核对**）。⇒ **理由不成立，两条路等价**；B 只是因为自己先 `_clear` 了才没出事。

**B-4 ★** B 用 `output/mark-semantics.json` 论证「`Select4` 走的那一次**没有 mark** ⇒ 不带 mark 的选择落在 **0 号桶**」。
**该文件的内容是 `"select4_counts": {"-1": 0, "0": 0, "1": 0, "2": 0}`** —— `all = -1` 也是 0 ⇒ **那一次是「一个都没选上」**，不是「选上了但落在 0 号桶」。**B 的读法超出了证据**。（同文件的 `trials` 三组「mark_arg=N → N 号桶计数=1」倒是真的支撑 B 另一半主张：`SelectByID2` 的 mark 会落桶。）

**B-5 ★** `_select_face_at` 文档串与代码不符：
- 文档串写「② 从该点**沿外法向反向抬起**再打射线 ⇒ 保证射线从体外进来」—— **代码没有抬起**，`x, y, z` 原样传（`precall-cand-B.py:157-160`）。
- 文档串写「退回按该方向的反向再试一次（覆盖轴对齐零件的**任意一面**）」—— **代码只试 `(0,0,-1)` 与 `(0,0,1)` 两个 z 向**，覆盖不了 ±x / ±y 面。⇒ **文档承诺的面比代码能给的多。**

**B-6 ★** 类型串用错（官方例子里那两类实体都不是 `SKETCH`）：
- 放样引导线：官方 `Insert_Protrusion_Blend_Example_VB.md` L77–80 用 **`"REFERENCECURVES"`**（`swSelREFERENCECURVES = 26`），B 的 `_pre_part_loft` 用 `_select_named(model, sel, "SKETCH", 2, …)`。
- 扫描路径：`Select_Multiple_Paths_for_Sweep_Path_Example_VB.md` L59–60 用 **`"EXTSKETCHSEGMENT"`**，B 的 `_pre_part_sweep` 用 `"SKETCH"`。
⇒ `Type` 过滤不匹配 ⇒ `SelectByID2` 回 `False` 且计数不涨（官方 L73「If Type is specified, this method returns false if it cannot find the matching object type」）。

### C —— 4 处

**C-1 ★★★（算错且自称对）** C 的放样引导线：
> 头 L68：「4 条 `REFERENCECURVES` mark=**4098 / 8194 / 12290 / 16386**（= 2 × 1..4，即「引导线 mark 2」按序号进位）」
> 代码 L826：`mark = LOFT_GUIDE_MARK * (i + 1)`，注释「★ 与官方例子的 4098/8194/12290/16386 **同算式**」

**实际算式是 `4096·(i+1) + 2`**（4098=4096+2 · 8194=8192+2 · 12290=12288+2 · 16386=16384+2，**官方例子 L77–80 已核对**）。C 的 `2*(i+1)` 给出 **2/4/6/8**，**与官方例子的四个值一个都不相等**，而 C 两处都写「一致」。
⇒ **对照：B 在同一处做对了** —— B 明写「官方例子给 4098/8194/…，而 §Remarks 那一栏写的是 2；★ 我**没查到**那个高位位的官方定义 ⇒ ★ 本候选**只按 §Remarks 的 2**（★ 不猜）」。

**C-2 ★★★（集成即 `TypeError`）** C §4.1 给 sweep/loft 的挂法：
> sweep：`param_alias={"profile": None, "path": None, "guide_curves": None, "direction_vector": None}`
> loft：`param_alias={"profiles": None, "guide_curves": None, "centerline": None}`

**这两条都会顶掉仓内已有的映射。** `tool_registry.py:495-498`：只有**列在 `param_alias` 里且值为 `None`** 的参数才被跳过；其余一律 `kwargs[p.name] = getattr(params, p.name)` 直接下传。
⇒ 顶掉 `profile_sketch: None` / `path_sketch: None`（batch48）或 `profile_sketches: None`（batch47）之后，**那个仍然 `params` 里声明着**的参数会被下传给
`sw_sweep.create_sweep_report(model, cut)` / `sw_loft.create_loft_report(model, closed, use_selected_profiles)` ⇒ **`TypeError: unexpected keyword argument`**。
⇒ **正确做法：是在既有 `param_alias` 上「增量加键」，不是整张替换。**

**C-3 ★** C 的 `_select_named` 直接用原名调 `SelectByID2`：
```python
_get(ext, "SelectByID2", str(name), str(type_str), 0.0, 0.0, 0.0, bool(append), int(mark), _callout(), 0)
```
**没有走仓内的中英文候选表**，而 C 自己在报错文案里写着「中文 UI 是「草图1」，不是 "Sketch1"（事实 9）」。⇒ **文案说了、代码没做**：调用方传 `Sketch1` 时**选不中**，然后收到一条「请传中文名」的提示。
⇒ 对照：A 走 `sw_part._get_sketch_name_candidates` + `_select_first_candidate`（**两者签名与调用形状已核对**，`_get_sketch_name_candidates(sketch_name)` / `_select_first_candidate(extension, candidate_names, entity_type, append=, mark=)`）；B 走 `_get_sketch_name_candidates`。

**C-4（次要）** `_select_by_object` 里 `return bool(_get(obj, "Select2", …))` 之后的 `return False` 与其注释块是**死代码**；另 `_get(sd, "Mark", int(mark))` 是拿 `get_com_member(obj, member, *args)` 当**属性 setter** 用（能工作：见 `sw_connect.py:156` 「有实参 ⇒ 一定调用」），但仓内**有专门的 `set_com_member`**（`sw_connect.py:581`）—— A 用的就是它。⇒ 建议对齐仓内路径。

---

## 三 · 推荐（逐工具 · 可混搭）

| 工具 | 推荐用哪一份的哪段 | 具体动作 |
|---|---|---|
| **mold_parting_line** | **C 的 `_pre_parting` 全部**（射线→按点→对象三级 `_select_marked` + 顺序纪律） | 照抄 C 的 `_pre_parting` / `_pre_mold_parting_line`；★ A 的 `_pull_direction`「有名字 vs 面」分流可以并进去作为 `plane:`/`axis:` 前缀支持 |
| **mold_parting_surface** | **A 的 `has_parting_line` 分档**（`_pre_mold_parting_surface` 的 if/else）+ **C 的 `_select_marked`** | ★ 只取 A 那段 if/else，**选区实现用 C 的**；C 的同名函数**不要**用 |
| **part_wrap** | **C 的 `_select_by_ray` / `_select_marked`**（含「Append 反选」回读护栏）+ **A 的草图选法**（`_select_first_candidate` + `_get_sketch_name_candidates`） | ★ C 的 `_select_named` **必须换成 A 的**（修 C-3）；`_pre_part_wrap` 其余留用 |
| **part_sweep** | **C 的 `_pre_part_sweep`**（SELOBJGROUP 的「未实现/未实测」登记 + mark 128 + 端到端只给「中」）＋ **B 报出的 `create_sweep_report` 缺 `return`** | ★★ **B 的 `param_alias` 整张替换方案不可用**（B-2）；C 的 `param_alias` 也**必须改成增量加键**（C-2）。★ **另立一条单独立项**：`scripts/sw_sweep.py` 的 `create_sweep_report` 在 L117-121 算完 `feat` 后**函数直接结束**（L119 的 `return` 在 `except` 里，L121 就是下一个 `def`）⇒ **成功路径回 `None`**（**已核对**）。这是目标函数的 Python 缺陷，**任何 pre_call 都修不了它**，接上 `pre_call` 工具照样回 `None` |
| **part_loft** | **B 的证据纪律段**（只用 §Remarks 的 mark=2；把「例子给 4098/8194/… 而 Remarks 写 2」**如实写下来**）＋ **C 的选择器骨架**（`sketch:` 前缀 + 顺序即方向 + 「≥2 个」回读） | ★★ **必须删掉 C 的 `2*(i+1)`**（C-1）。★ **两条 spec 已有 `pre_call`（`_pre_loft_profiles` / `_pre_sweep_sketches`）** ⇒ 集成应是**往既有 `param_alias` 上增量加键**（加 `guide_curves`/`centerline`），**不是替换**。★ B 报的「引导线要 `"REFERENCECURVES"` 类型」（B-6）要一并采纳 |
| **part_axis** | **B 的证据边界表述**（mark 无据 ⇒ 只回读 `-1`）＋ **C 的 `_pre_part_axis` 选择器实现**（`plane:`/`axis:`/`+z`/`index:`） | ★ **判据只用 `GetSelectedObjectCount2(-1)`**（`sw_part.py:1588` 就是这么读的）⇒ ★ **`AXIS_MARK=0` 不要进判据**，只在返回值里如实登记「例子推断值」 |

---

## 四 · ★★ 「不可直接集成」红线

### R1 依赖未证实取值
| # | 内容 | 处置 |
|---|---|---|
| **R1-1** | **`ISelectData` 的 mark 能不能真落到桶里** —— A 的**全部**面/边路径、C 的第三级兜底都建在它上面。**A 自己写了「★★ 未证实……本仓没有真机证据」，C 写了「本仓从未验证过」**（事实 47 的后端限制就在隔壁） | ★★ **集成前必须先单独 A/B 一次**：`CreateSelectData()` → 设 `.Mark` → `Select4(append, sd)` → 回读 `GetSelectedObjectCount2(mark)`。**A 的验证清单第 ④ 条说的就是这件事，应当最先跑。** 不通 ⇒ 全部退回 `SelectByRay` / 按点 `SelectByID2` |
| **R1-2** | **`AXIS_MARK = 0`** —— `InsertAxis2.md` **整页无 Remarks**（已核对），0 只来自 `Create_Revolve_Features_Example_VB.md` L29-30 的**例子** | ★ 只能标 `stitched`；**不进判据**（目标函数读 `-1`）；圆柱面/圆锥面/两点三类源**完全未证实** |
| **R1-3** | **放样引导线多条时的 mark** —— 官方例子 4098/8194/12290/16386 与 §Remarks 的 `2` **官方自己不一致**，高位位定义**查不到** | ★ **只发 `mark=2`**（B 的处置）；**严禁**用 C 的 `2*(i+1)`（既不是 2、也不是 4096k+2） |
| **R1-4** | **扫描多段路径的 `SELOBJGROUP` 收口** —— 官方例子 L61 确有，但**那个 `Unknown` 实体不在体上、不进选区计数**，效果**未实测** | ★ 只能写在「未实现」段；**不得**宣称「支持多段路径」 |
| **R1-5** | **面定位精度** —— `IFace2.GetBox.md` L20 逐字「**approximate … should not be used for comparison or calculation purposes**」（已核对）⇒ 包围盒中点**未必落在曲面上** | ★ 轴对齐件可用；**斜面/曲面必然抛错**（这是设计上的显式拒，不是 bug），但**工具文档必须写明**，否则用户会以为是能力坏了 |

### R2 改了不可逆 / 破坏性状态
| # | 内容 | 处置 |
|---|---|---|
| **R2-1** | ★ **六个 `pre_call` 全部调 `ClearSelection2(True)`** —— 这会**清掉用户在图形区里已有的选中态**。这与仓内既有 `_pre_sweep_sketches` / `_pre_loft_profiles` / `_select_faces_for` 的做法一致（先例成立），但它**确实是破坏性的** | ★ 在工具 doc 里**明写**「本工具会清空当前选区」；★ 不要在同一次会话里连着调两条会清选区的工具后指望选区还在 |
| **R2-2** | ★ `connect_solidworks()` / `RESOLVERS["model"]` **本身就会清空选区**（隔离证据 `output/selection-lifetime-evidence.json` 第 8 步 `mark1: 2→0`，已核对） | ★ 这是 `pre_call` **必须**自己重建选区的**真正理由**；★ **B-3 那条理由（"resolver 不会二次清"）是错的**，别拿它当设计依据 |
| **R2-3** | ★ **`part_sweep` 端到端仍然不通** —— `sw_sweep.py` L103-109 的轮 488 A/B：两条常量（17/62）都卡在 `AccessSelections` 的 `0x80010105`；**加上** L117-121 成功路径缺 `return` | ★★ **红线**：接上 `pre_call` **不等于**工具能用。★ 集成这一条**必须**同时修 `create_sweep_report` 的缺 `return`，否则会出现「pre_call 接上了、工具还是回 `None`」 |
| **R2-4** | ★ `param_alias` 整张替换会**静默改变下传实参集** ⇒ 集成时 `TypeError` | ★★ **只允许增量加键**；改完必须跑 `scripts/release_check.py`（含判据「声明名 ∈ 形参」那道门禁） |

---

## 五 · 三份共同的、可直接复用的部分

1. **机制前提三份都对**（且已逐行核对 `tool_registry.py:490-525`）：`kwargs[inject]=resolver(params)`（L507）→ `pre_call(params)`（L510-513）→ `derived_args`（L514）→ `mod.fn(**kwargs)`（L525）；`param_alias` 值为 `None` ⇒ 跳过下传（L495-496）。
2. **`pre_call` 里必须先自己 `ClearSelection2`** —— 三份都做了，**理由**见 R2-2。
3. **判据一律是 `GetSelectedObjectCount2(mark)` 的回读，绝不信 `SelectByID2`/`SelectByRay`/`Select4` 的 bool**（事实 8）—— 三份都写对了，**这是本仓最该守住的一条**。
4. **官方 mark 值本身**：六条的 mark（模具 1/4 · 包覆 1/2/4 · 放样 1/2/4 · 扫描 1/2/4/128）**三份引用的官方页我都核对过，逐字一致，没有一条抄错**。分歧只出在「怎么把 mark 写进去」和「多条/条件怎么处理」上。

---

## 六 · 一句话给 Lead 的执行顺序

1. **先跑 A 的验证清单第 ④ 条**（`CreateSelectData` → `.Mark` → `Select4` 能否落桶）—— 它决定 R1-1，进而决定 A 与 C 的面/边路径能不能用。
2. **修 `sw_sweep.py::create_sweep_report` 缺 `return`**（R2-3），否则 part_sweep 一切白做。
3. 按 §三 的表格取件；**sweep/loft 的 `param_alias` 一律增量加键**（R2-4）。
4. 全部落地后跑 `pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests/<改过的>.py`。

**错误统计：A 2 处 · B 6 处 · C 4 处 = 12 处。**