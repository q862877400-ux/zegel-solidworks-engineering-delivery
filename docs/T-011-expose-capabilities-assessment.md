# T-011 评估：把已有能力暴露成 MCP 工具

**特性**：`specs/002-merge-template` 的 T-011 · **日期**：2026-10-01 · **状态**：评估完成，给出最小可跑示例

---

## 一、问题（已知事实 25 的直接后果）

```
mcp-server/server.py          引用 25 个 scripts 模块，暴露 45 个工具
scripts/sw_*.py               共 75 个模块
⇒ 未引用的模块                61 个（含护城河 sw_topology）
本仓库真实能力面              72 模块 / 814 个公开函数
```

**⇒ 814 个函数里只有 45 个能被 MCP 调用。** 这是「已有能力 → 可用」的断层，
也是广度地图把我们的能力记为「零」的原因（`build_union_map._our_tools()` 只数工具名）。

---

## 二、为什么**不能**批量自动注册（三条硬约束）

| # | 约束 | 出处 | 为什么挡住自动注册 |
|---|---|---|---|
| 1 | 工具名必须 `solidworks_<域>_<动作>`（或 headless 的 `cadstudio_*`） | `docs/union-conventions.md` 规则 1，**有正则门禁** | 自动生成的 `sw_xxx_yyy` → `solidworks_xxx_yyy` 会造出语义不清的名字；规则要求「域在前、动在后、蛇形」，**需人工判域** |
| 2 | 必须用**声明式 `selection`**，禁止裸坐标 | 同上 规则 3，**有 schema 门禁** | 814 个函数里有大量以「调用方先选好实体」为前置的（如 `apply_fixed_restraint`）；把它们直接暴露成工具等于把**裸选择状态**变成 API，违规则 3 |
| 3 | 长度 `_mm` 后缀、角度 `_deg` 后缀，换算只在边界做一次 | 同上 规则 2 | 每个函数的参数语义要**逐个判**，无法机械映射 |

**成本量化**：

```
server.py 2455 行 / 45 个工具 = 54.6 行/工具
814 个函数 × 54.6 行 ≈ 44,408 行   ⇒ 不现实
```

**⇒ 批量注册既违规则、又不现实。** 只能**精选**。

---

## 三、也不该做的两条捷径

| 捷径 | 为什么不做 |
|---|---|
| **一个「泛型调用」工具**（传模块名+函数名+参数，服务端反射调用） | ① 违规则 3（无法声明 selection）；② 把整个 `scripts/` 变成远程代码执行面；③ 门禁会红（`check_member_names` 无法静态核对动态调用） |
| **只暴露 `capabilities.yaml` 里 `verified` 的那 21 条** | 方向对，但 `capabilities.yaml` 的粒度是**能力域**（29 条），不是**函数**（814 个）；一条能力含多个函数，仍要人工拆 |

---

## 四、可行路径：**精选三批**（按价值/成本排序）

### 第一批（**本评估已给出可用的最小示例**）—— 护城河域
| 工具名 | 包装 | 为什么先它 |
|---|---|---|
| `solidworks_topology_create_study` | `sw_topology.create_topology_study` | **四家全空、只有我们有**（已知事实 20/21） |
| `solidworks_topology_set_goal` | `sw_topology.set_topology_goal` | 已真机验证（连续三次成功） |
| `solidworks_topology_evidence` | `sw_topology.collect_topology_evidence` | 只读，零风险 |

**成本实测**：见 §五 —— 一个工具 **约 40 行**（含 Pydantic 输入模型）。

### 第二批 —— 刚并入/刚修好的域
`solidworks_mold_parting_line`（`sw_mold.insert_parting_line`）·
`solidworks_simulation_static_study`（`sw_simulation.create_static_study`）

### 第三批 —— 其余按「用户会在对话里说出口的动作」筛选
**判据**：用户会自然地说「帮我建个草图 / 加个孔 / 出个工程图」的动作优先；
「内部工具」（`sw_api_*` 的 12 个 API 索引模块、`sw_jlcfa_*` 的 13 个 GUI 步骤模块）**不暴露**
—— 它们不是用户会直接要的**动作**。

**⇒ 由此得到一条筛选规则**（写进模板）：

> **暴露判据**：该函数是不是「用户会用一句自然语言要求的**动作**」？
> 是 ⇒ 候选；不是（内部索引 / GUI 步骤 / 门禁工具）⇒ 不暴露。

按此规则，61 个未引用模块里**约 20 个**含候选动作（其余 41 个是内部工具），
候选函数**约 120 个**（不是 814 个）—— **这才是真实的工作量**。

---

## 五、最小可跑示例（**未接入在跑的服务**）

**⚠ 本示例是一份**独立的草稿文件**，没有修改 `mcp-server/server.py`。**
理由：改 `server.py` 会改变**正在运行的** MCP 表面（本会话的 `mcp__solidworks__*` 工具即来自它），
且「单源运行」原则下重启需谨慎（已知事实 24）。**接入与否由人决定。**

草稿见 `D:\AI\SW\mcp-tool-draft\topology_tools.py`（含 Pydantic 模型与 3 个工具定义）。
**接入方式**：把该文件的类与函数**复制**进 `server.py`（照既有工具的写法），
再重启 MCP 服务。

---

## 六、代价与风险

| 项 | 评估 |
|---|---|
| **单工具成本** | ~40 行（1 个 Pydantic 模型 + 1 个 `@mcp.tool` 函数 + 1 个 `op()` 闭包） |
| **第一批 3 个工具** | ~120 行，**可立刻做** |
| **真实全量（按 §四 判据）** | ~120 个函数 × 40 行 ≈ **4,800 行** —— 分多批，每批跑一遍门禁 |
| **风险** | 改 `server.py` 会动**在跑的** MCP 表面；须在**没有任务在跑**时改并重启 |
| **门禁** | 无新增门禁需求 —— 规则 1/2/3 已有正则与 schema 校验，新工具照写即可通过 |

---

## 七、结论

1. **批量注册不可行**（44k 行）且**违三条规则**；
2. **真实工作量是 ~120 个函数**（不是 814），按「用户会自然说出口的动作」筛选；
3. **建议先做第一批 3 个**（护城河域），成本 ~120 行；
4. **不建议**做「泛型调用」工具（违规则 3 且扩大执行面）；
5. **本评估不动在跑的服务** —— 草稿已备好，接入需人决定时机。

---

## 八、进展记录（2026-10-01）：**已开工**

### 8.1 声明式注册器已建成（`mcp-server/tool_registry.py`，283 行，一次性成本）

把 `server.py` 既有 45 个工具的形状（`@mcp.tool` + Pydantic 模型 + `op()` 闭包 + `_run_locked`）
抽成声明式。**实测成本**：

| 做法 | 每工具 | 120 个工具合计 |
|---|---|---|
| 手写（`server.py` 现状：2455 行 / 45 工具 = 54.6 行/工具） | 54.6 行 | **≈ 6480 行** |
| **声明式**（`ToolSpec` + `Param` 列表） | **~10 行** | **≈ 1200 行** + 一次性 283 行 |

**⇒ 约 5 倍降幅。**

**三条机器可判的规则做成了「注册时即报错」的门禁**（`GateError`）：
规则 1 命名正则 · 规则 3 禁裸坐标 · `solidworks_` 与 `cadstudio_` 不混用；
且 `register()` **全有或全无**（有坏声明就一个都不注册）。

**⚠ 不自动猜参数语义**：规则 1/2/3 是**人工判断**，自动猜会造出静默错误 ——
**本项目刚在 `CreateMesh` 上踩过「毫米当米」⇒ 1950 万单元 / 20–25 GB。**
本模块只做「把已判好的东西写成代码」。

### 8.2 第一批 8 条声明已落地（`mcp-server/tool_specs_batch1.py`）

护城河域（拓扑 3 条）+ 模具域（4 条）+ 仿真材料（1 条）。
**全部通过注册器自己的门禁**，**全部通过守卫测试**（`tests/test_tool_specs_batch1.py`，8 条）。

### 8.3 ⚠⚠ 评估里没预见到的一个**真实冲突**（本批最重要的产出）

`scripts/sw_simulation.py::select_face_at(model, x, y, z, …)` 的入参是**裸坐标**，
**违反规则 3** ⇒ 直接暴露会被门禁拒掉。

**⇒ 这不是 bug，是「内部实现」与「对外表面」的合法差异：**
- **内部**：`SelectByID2("", "FACE", x, y, z, …)` **必须**给面上的点 —— 官方 API 的形状
- **对外**：入参必须是**声明式选择**（「哪个面」），由工具内部解析成坐标

**⇒ 修正后的判据**：**能直接暴露的只有「入参本身就是声明式」的函数**；
凡内部用坐标/裸索引的，暴露时**必须加一层显式解析**，且解析规则要**写出来**
（不能藏在默认值里）。`select_face_at` / `select_face_by_index` 之类**留到有解析层再做**。

### 8.4 仍未做（下一步）

| 项 | 说明 |
|---|---|
| **注入语义建模** | 把 `inject: Literal["model","sw_app","study"]` 抽出来，让拓扑那 3 条从 `extra_op` 回到声明式 —— **那时才是真的「10 行一个工具」** |
| **声明式选择解析层** | 解决 8.3 的冲突；`solidworks_simulation_select_face(selection=...)` 之类 |
| **接入 `server.py`** | ⚠ 单源原则（已知事实 24）⇒ **由人决定时机**；接入 = 一行 `register(mcp, SPECS)` |
| **第二/三批** | 候选已枚举：**32 个模块 / 229 个候选「动作」函数**（比评估的 ~120 多，因判据更松） |

### 8.5 枚举口径（可重跑）

评估里立的判据：「该函数是不是『用户会用一句自然语言要求的**动作**』？」
- **排除**：12 个 `sw_api_*`（API 索引）· 13 个 `sw_jlcfa_*`（GUI 步骤）· 门禁工具
- **保留**：其余 32 个模块
---

## 九、第二批（2026-10-01）：**修正「~120 个」这个乐观估计**

### 9.1 新增 6 条声明（全部 A 类）
```
solidworks_weldment_evidence                只读    inject=model
solidworks_weldment_ensure_cut_list         写入    inject=model
solidworks_weldment_update_cut_list         写入    inject=model
solidworks_weldment_create_sub_weld_folder  写入    inject=model（显式省略 `folder`）
solidworks_sheet_metal_evidence             只读    inject=model
solidworks_surface_evidence                 只读    inject=sw_app
```
`tests/test_tool_specs_batch1.py` + `batch2.py` + `test_tool_registry.py` 合计 **45 条测试**。

### 9.2 ⚠⚠ 最重要的产出：**四类分类**（修正工作量估计）

第一轮枚举给出「32 个模块 / 229 个候选动作函数」，本档早先说「真实工作量 ~120 个」。
**看清签名之后，这个数是乐观的。** 核心建模域的公开函数按「能否干净暴露」分四类：

| 类 | **判据**（可复核） | 例子 | 缺什么 |
|---|---|---|---|
| **A 直接可暴露** | 只收标量/字符串/bool；宿主对象靠 `inject` | `weldment_evidence(model)` | **无** —— 已做 14 条 |
| **B 需声明式选择解析** | 入参含**坐标/向量** | `create_planar_surface(sw_app, point, normal)` | 「选择器 → 坐标/向量」解析层（**只有面的雏形**，不覆盖点与方向）|
| **C 需 spec 展平层** | 入参含 **typed spec dataclass** | `create_base_flange(model, sketch_ref, spec: BaseFlangeSpec)` | 把 dataclass 字段逐个抄成入参（**不能猜字段**）+ 同时需要 B 层 |
| **D 不该暴露** | 纯 getter / 需「取中间对象」的解析 | `get_sketch_segments(sketch)`、`merge_points(sketch, tol)` | **不该做** |

**⇒ 结论（比数字重要）**：
1. **A 类远少于 120** —— 能直接暴露的其实只有「证据类 + 少量模型级动作」。
2. **B/C 两类各自需要一层基础设施**，是**独立工作项**，不是「多写几条声明」。
3. **D 类不该暴露**：暴露 getter 等于把工具的**选择集状态**变成 API（违规则 3 的精神）。
   用户要的是「这个草图完整吗」「改个尺寸」这类**意图** ⇒ 那类工具应当**新写**，
   而不是把内部 getter 搬出来。
4. **⇒ 真实工作量应按「新建多少面向意图的工具」估**，而不是按「暴露多少既有函数」估。
   **这是一个比原估计更可靠的锚。**

### 9.3 分类表的守卫（机器可验的部分）
`tests/test_tool_specs_batch2.py` 加了三条：
- **点到的函数必须真存在**（≥30 个逐个 `hasattr` 核）—— 抓最糟的一类错：
  分类表里写一个**不存在**的函数名，看起来像做过功课，实际是编的
- **每类必须写判据/理由/缺什么** —— 否则就是「凭感觉分堆」，后续批次无法照办
- **同一函数不得落在两类**

### 9.4 已建成的两项基础设施（本档 §8.4 的「下一步」已完成）
| 项 | 状态 |
|---|---|
| **注入语义建模** | ✅ `inject="model"/"sw_app"/"study"`，解析器由调用方提供 ⇒ 注册器保持宿主无关 |
| **声明式选择解析层（面）** | ✅ `sw_simulation.resolve_face_selector` / `select_face_by_selector`（`FACE_SELECTORS` 用**外法向**命名）|
| 声明式选择解析层（**点 / 方向**） | ⛔ 未做 —— B 类的阻塞点 |
| spec 展平层 | ⛔ 未做 —— C 类的阻塞点 |

### 9.5 当前规模
```
声明式注册器        mcp-server/tool_registry.py        ~300 行（一次性）
第一批              mcp-server/tool_specs_batch1.py     8 条
第二批              mcp-server/tool_specs_batch2.py     6 条
守卫测试            tests/test_tool_*.py                45 条
```
---

## 十、第三批尝试：**「运行期可达性」的通用化 —— 结论是「泛化方法，不泛化工具」**（2026-10-01）

### 10.1 起因
第二轮发现 `sw_surface.py` 的 14 个曲面创建入口**运行期只有 5 个可取**（AGENTS.md 已知事实 28）。
**⇒ 自然的问题是：这是不是普遍现象？如果是，判据 A5（签名对齐）就缺了一半。**

### 10.2 做了什么
写了 `tools/audit_runtime_reachability.py`：静态抽出 `scripts/` 里所有
`get_com_member(obj, "成员")` 的成员名，再在一组**规范对象**上逐个 `getattr`（只读、零副作用）。

### 10.3 ⚠ 结果**不可用**，并查明两个**结构性上限**
```
第一版（10 个通用对象）:      424 个成员里 365 个报「不可达」= **86%**
补了 Simulation 族（14 个）:  仍报 360 个
```
**两个上限（已写进工具注释）：**
| # | 上限 | 表现 |
|---|---|---|
| 1 | **对象集完整性** | 缺一族对象，那一族成员**全报不可达**。`AddForce` / `BeginEdit` / `ActiveStudy` 挂在 Simulation 族上，通用对象里没有 ⇒ 全是假阳性 |
| 2 | **对象集依赖文档状态** | 裸零件**没有研究** ⇒ `ICWStudy` 族（`ICWMesh` / `ICWLoadsAndRestsraintsManager` / `ICWTopologyStudyManager` / `ICWResults`）整族取不到 ⇒ 又一片假阳性 |

**⇒ 结论：这个「全局扫一遍」的形态不可靠。86% 的报错率使其**无法当门禁**（接进去会因假阳性而红）。**

### 10.4 ✅ 可靠的是什么：**在**已知对象**上逐个穷举**
`IModeler` 那次（`probe_surface_array_shape.py`）为什么扎实？
- **对象是确定的**（`sw.GetModeler`，我拿到了它）
- **逐个成员穷举**（10 个，一个不漏）
- **判据是「调一次看是否非 None」**，不只是 `getattr`

**⇒ 那次的 5/14 是可信的；这次的 360/424 不是。**
**⇒ 纪律：泛化**方法**（已知对象 + 逐个穷举 + 调一次验非 None），不泛化**工具**（猜对象集 + 全局扫）。**

### 10.5 一个**顺带抓到的真实门禁盲区**（本轮的实质产出）
写那个审计工具时我把 `CWStudy GetStudy(Int32)`（**一个参数**）传成两个 ⇒ COM 报
`'无效的参数数目'`。查为什么 arity 审计没抓到 ⇒ **它只审 `scripts/`，不审 `tools/`**，
而 `tools/` 里有 **3 个文件 / 42 处 COM 调用**（三个证据脚本 + 该审计工具）全在覆盖之外。

**⇒ 已修**：`scripts/audit_call_arity.py` 加 `--all`（一次审 `scripts/` + `tools/`）。
**⇒ 全量结果：13 处问题全部已知**（OCCT 假阳性 ×8 + 已文档化的有意为之 ×4 + makepy 代理 ×2），
**`tools/` 0 处新问题**（42/42 通过）。

**⚠ 这个模式值得记：**「**项目自己的代码全对、错的是新写的那处**」正是门禁该防的 ——
若门禁早就覆盖 `tools/`，它会在提交前就红。

### 10.6 对判据 A5 的影响（**结论：需要补一条，但补法要变**）
A5 现在只覆盖**签名层**（参数顺序与类型与官方签名对齐）。
**运行期可达性是另一半，但它**不能**靠「全局扫一遍」来验**
（对象集猜不全 ⇒ 假阳性淹没真信号）。
**⇒ 可行的补法**：对**每一个 `verified` 能力**，在其**已确立的对象**上逐个穷举它用到的成员
（像 `IModeler` 那次），把结果写进该能力的 `evidence`。
**⇒ 这是**逐能力**的工作，不是**一次全局**的工具。** 登记为待办，本轮不硬塞。
---

## 十一、第三批（2026-10-01）：C 类落地 2 条 + **C 类精确分类（三种 ref 约定）**

### 11.1 新机制 `ToolSpec.derived_args`（「spec 展平层」）
C 类函数的入参是 **typed spec dataclass**，MCP 表面收不了 ⇒ 展平成标量入参。

**⚠ 为什么不复用 `extra_op`（本轮守住的东西）**：
| | `extra_op` | `derived_args` |
|---|---|---|
| 作用 | **替换整个调用** | **只派生一个额外实参**（如 `spec=`） |
| 代价 | 用了就**放弃声明式**（`module`/`function` 都不要了） | `module`/`function`/同名直传**都还在** |

**⇒ 能不退就退。** 单位换算放这里且**只做一次**（规则 2）：spec 说「米」、表面用 `_mm` ⇒ `/1000`；
角度**本来就是度** ⇒ 原样传。

### 11.2 第三批 2 条
```
solidworks_sheet_metal_create_base_flange    derived_args 装回 BaseFlangeSpec（7 字段）
solidworks_sheet_metal_create_one_bend       derived_args 装回 OneBendSpec（4 字段）
```
`sketch_name` → 实现里的 `sketch_ref`（**显式别名**，不靠猜）。

### 11.3 ⚠⚠ 核心发现：**C 类不止「展平 spec」，还有三种互不相同的 ref 约定**
逐一读函数体后（**不是猜**）：

| 函数 | ref 参数 | 约定 | 能否暴露 |
|---|---|---|---|
| `create_base_flange` | `sketch_ref` | **草图名**（转给 `sw_part._ensure_sketch_selected`） | ✅ **已做** |
| `create_one_bend` | `sketch_ref` | **草图名** | ✅ **已做** |
| `create_edge_flange` | 无 | 文档串：「调用前必须先用 `_select_by_id` 把目标边入选区」 | ⛔ 需「选择」入参 |
| `create_gusset` | 无 | 同上（吃当前选区） | ⛔ 同上 |
| `create_draft` | `face_ref` | **对象** | ⛔ 需「选择→对象」桥 |
| `create_swept_flange` | `path_ref` / `profile_ref` | **对象**（文档串明写 `GetSelectedObject6(1,-1)` 取得） | ⛔ 同上 |

**⇒ 修正后的判据：C 类要按 ref 约定再分三小类（C1/C2/C3）。6 个里只有 2 个能现在暴露。**

**★ 好消息（这决定了下一步该怎么做）**：另 4 个需要的「selection」概念
**正是规则 3 要求的形态**，而 `sw_part._ensure_sketch_selected` **已经示范了它的样子**：
- **按名字选**（而不是坐标）
- 支持特殊的 `__current_selection__`（复用当前选区，不重选）
- 有**多级回退**（活动草图 → 缓存 → 按名选特征 → 按候选名选 SKETCH）
- 选不到就 `ClearSelection2` + **抛带原因的错误**（不静默成功）

**⇒ 照它做一层「按名字/类型选边、选面」的解析层，C2 与 C3 **同源、可一次做成**。**

### 11.4 守卫测试（`tests/test_tool_specs_batch3.py`，8 条）
最重要的一条：**`spec` 的每个字段都必须在 MCP 表面有对应入参**
—— 否则**静默丢字段**（用户设不了它，实现用 dataclass 默认值代替，**看代码看不出来**）。

### 11.5 本轮自己踩的两个错（已修，值得记）
1. **`param_alias={"spec": None}`** —— `spec` **不是**声明参数（由 `derived_args` 提供）
   ⇒ 门禁红「param_alias 指向未声明的参数」。**门禁抓对了。**
2. **守卫测试第一版把判据写成 `declared == real`** ⇒ 必然失败，因为声明里的其余入参
   是 **spec 的字段**、不是函数形参。**⇒ 判据应是「非 spec 形参必须被覆盖」（子集）**。
   **⚠ 这是「测试自己的逻辑错了，不是代码错了」—— 遇到要先问「这个测试想验什么」。**

### 11.6 当前规模
```
声明式注册器    mcp-server/tool_registry.py        ~340 行（一次性）
第一批 8 条 · 第二批 6 条 · 第三批 2 条            **合计 16 条**
守卫测试        tests/test_tool_*.py                **53 条**
```
---

## 十二、选择解析层落地（2026-10-01）：**实测推翻了「按名字选」**

### 12.1 关键实验与结论（`D:\AI\SW\probe_entity_select_by_name.py`）
在自建的 100×60×20 mm 板（12 边 / 6 面）上逐个试：

| 选法 | 结果 |
|---|---|
| `SelectByID2("Edge1", "EDGE")` | **计数 0** ⇒ **边没有可用的名字** |
| `SelectByID2("Face1", "FACE")` | **计数 0** ⇒ **面也没有** |
| `SelectByID2("", "EDGE", 0, 0, 0, …)` | **计数 0** ⇒ 原点不在边上 |
| `SelectByID2("", "FACE", x, y, z, …)` | **计数 1** ✓ ⇒ 按**面上的点**选面可行 |
| **`edge.Select4(False, callout)`** | **计数 1** ✓ ⇒ ★ **按**对象**选实体可行** |

**⇒ 两条设计结论：**
1. **实体没有名字** ⇒ 「按名字选」**对实体不成立**（对**特征**成立 ——
   `sw_part._ensure_sketch_selected` 走的就是那一路）
2. **正解是 `IEntity.Select4(Append, Callout)`** ⇒ 解析层要产出**对象**，不是名字、也不是坐标

### 12.2 落地模块 `scripts/sw_selection_spec.py`（三种解析器）
| 选择器 | 语义 | 为什么需要 |
|---|---|---|
| `__current_selection__` | 用**当前已选中**的东西 | ★ 对 AI 驱动最自然；与 `sw_part` 已有约定一致 |
| `index:<n>` | 体上第 n 个实体 | 确定性、可脚本化；⚠ 序号顺序官方未承诺稳定，**不作持久引用** |
| 一个 **COM 对象** | 已是对象，直接 `Select4` | 组合上层工具（如 `path_ref`）|

**⚠ 刻意**不**开坐标后门**：公开函数参数里**没有** `x`/`y`/`z`（规则 3）。
需要按坐标定位时用上层已有的 `sw_simulation.select_face_by_selector`。

### 12.3 端到端实测：**12 项通过 / 0 失败**（`probe_selection_spec_e2e.py`）
- `entities_on_body` → **12 边 / 6 面**（与几何相符）
- `index:0` / `index:11` / `index:0`(FACE) → 计数均 **1**
- `__current_selection__`：空选区**正确报错**、有选中时**正确取到**
- 直接传 COM 对象 → 计数 **1**
- 4 个「该报错就报错」全部正确报错（非法类型 / 越界 / 非法选择器 / 空选区）
- **复现了「`SelectByID2` 对边/面的名字选不中」**（两者计数均为 0）

**⇒ 按铁律 2，模块里四处「未在本机实测」已改成实测结论 + 证据出处。**

### 12.4 ⚠ 本会话踩得最值的一次：`Callout` 传 `None`
第一版探针**全部**报 `'类型不匹配'`（`0x80028CA0`）—— 连**已知可行**的「按点选面」也失败。
**⇒ 差点据此得出「选择不可能」的错误结论。**
真因：`SelectByID2` / `Select4` 的 `Callout` **必须**传 `VARIANT(VT_DISPATCH, None)`
（`sw_part._empty_callout()`），**而 AGENTS.md 已知事实 12 早就记了** —— **我忘了自己文档里的东西**。

**⇒ 已升格为已知事实 33**（含「该错误看不出是 Callout 的问题」这条）。

### 12.5 对 B/C 两类的影响（**这是本档一直在找的那个收敛点**）
| 类 | 之前缺什么 | 现在 |
|---|---|---|
| **C2**（`create_edge_flange` / `create_gusset`，无 ref、吃当前选区） | 「选择」入参 | ✅ **本模块的 `select_entity_by_index` / `resolve_selection` 直接够用** |
| **C3**（`create_draft(face_ref)` / `create_swept_flange(path_ref, profile_ref)`，ref 是对象） | 「选择 → 对象」桥 | ✅ **`resolve_entity` 就产出对象** |
| **B**（`point` / `normal` / `axis`，坐标向量） | 「选择器 → 坐标/向量」 | 🟡 **一半** —— 面已有（`select_face_by_selector`），**点与方向仍缺** |

**⇒ 下一步明确：C2/C3 已解锁，可以补第三批剩下那 4 条；B 类还差「点 / 方向」。**
---

## 十三、第四批（2026-10-01）：C2/C3 落地 4 条 + **修两个真实运行时 bug**

### 13.1 新机制 `ToolSpec.pre_call`（调用**前的副作用**钩子）
C2 类的实现里**明写**「调用前必须先选好」（`create_edge_flange` 的文档串、
`create_gusset` 的来源块）⇒ MCP 工具必须在**调用前**完成选择。

**三个机制各管一件事（不混、不合并）：**
| 机制 | 管什么 | 典型 |
|---|---|---|
| `inject` | 注入**宿主对象** | `model` / `sw_app` / `study` |
| `derived_args` | 派生**一个额外实参** | `spec=BaseFlangeSpec(...)` |
| **`pre_call`** | 调用**前**做**副作用**，**不产出实参** | 选中实体 |

**⚠ 为什么不把选择塞进 `derived_args`**：能跑，但会让「派生实参」这个名字
**承担它没有的含义** —— 本项目一贯反对给字段安它没有的含义。

### 13.2 第四批 4 条
```
solidworks_sheet_metal_create_edge_flange     C2  pre_call 选边 + spec 展平
solidworks_sheet_metal_create_gusset          C2  pre_call 选面 + spec 展平
solidworks_sheet_metal_create_draft           C2  pre_call 选面 + spec 展平（省略静默参数）
solidworks_sheet_metal_create_swept_flange    C3  两个选择器解析成**对象** + spec 展平
```
**⇒ C 类 6 条全部落地**（C1 2 条 + C2 3 条 + C3 1 条）。

### 13.3 ⚠⚠ 缺陷 1：`create_draft` 的 `face_ref` **从未被使用**
逐行读函数体（**不是猜**）：
```
def create_draft(model, face_ref, spec: DraftFeatureSpec):
    spec.validate()
    def _apply(data):
        data.Angle = float(spec.angle)                     # 只用了 spec
        data.ReverseDirection = float(spec.reverse_direction)
    return _create_from_definition(model, SW_FM_DRAFT, _apply)
    # ↑ `face_ref` 从头到尾**没出现**
```
**⇒ 一个「看起来有意义、实际什么都不做」的参数** —— 本项目纪律要抓的**静默无效**。
**⇒ 处理**：显式 `omitted_params=("face_ref",)`，工具描述里写明原因；
真正的选择由 `pre_call` 的 `selection` 承担。**不擅自改 `scripts/` 的既有签名。**

### 13.4 ⚠⚠ 缺陷 2：**被消费的参数必须显式标记，否则真机 TypeError**
守卫测试抓到：
```
TypeError: fake_target() got an unexpected keyword argument 'bend_radius_mm'
```
注册器把**所有**声明参数都当 kwarg 传，而 **spec 字段由 `derived_args` 消费**、
目标函数**并不接受**它们。

**⇒ batch3 的 2 条同样中招** —— 上一轮写的，当时那批测试**只查了单向**
（「真形参都被覆盖」），**没查反方向**（「声明参数都有归宿」）⇒ 绿灯但真机跑不了。

**⇒ 修复**：用**已有**的 `param_alias={name: None}`（语义本就是「被消费、不传」），
加 `_consumed(*names)` 帮手批量构造。**不新增第 4 个机制 —— 能复用就复用。**

**⇒ 并回补守卫（双向检查）**：每个声明参数必须有归宿，**没有第四种**：
① 映射到真形参；② `param_alias[name]=None`；③ 由 `derived_args` 装进 spec。

### 13.5 本轮自己踩的另外两个错
1. **模块文档串里嵌了 `"""…"""`** ⇒ 外层文档串提前截断 ⇒ `SyntaxError`
   （**教训**：文档串里引用别的文档串，用 `'''` 或改写，别嵌同类引号）
2. **测试用直接 `sys.modules[...] = fake`** ⇒ 假模块**泄漏到后面的用例**（5 个连带失败）
   ⇒ 必须 `monkeypatch.setitem`；且**假模块也要带真的 dataclass**（`derived_args` 会 import 它）

### 13.6 当前规模
```
声明式注册器    mcp-server/tool_registry.py        ~370 行（一次性）
四批声明        8 + 6 + 2 + 4 = **20 条**
守卫测试        tests/test_tool_*.py                **64 条**
```
---

## 十四、**接线完成**（2026-10-01）：20 条声明变成真的 MCP 工具（**45 → 65**）

### 14.1 为什么这是本档最重要的一个转折
在此之前，本档记的全部是**声明**与**基础设施** —— **对用户的价值是零**。
按任务里那句「不要为了修房子创建公司」，本轮把它接上。

### 14.2 实测
```
import server 成功
**工具总数 65**（上游 45 + 声明式 20）
新增的 20 个是否都在: True
```

### 14.3 改动（**对上游 `server.py` 的唯一一次改动**）
| 文件 | 改动 |
|---|---|
| `mcp-server/register_capabilities.py` | **新增** —— 全部接线逻辑（注入解析器、批次汇总、全有或全无） |
| `mcp-server/server.py` | **只加两句**（一个 import + 一次调用） |

**⚠ 已知事实 26 原本写「`server.py` 是上游的，**我们一行没改**」⇒ 本轮更新为
「**只改了一处**：接线的那两句」。** 这是本档第一次让那句事实失效，**如实登记**。

### 14.4 注入解析器（`tool_registry` 保持宿主无关）
| 注入名 | 解析器 | 行为 |
|---|---|---|
| `model` | 活动文档 | 取不到就**报错**（不返回 None 让下游崩在别处） |
| `sw_app` | `ISldWorks` | |
| `study` | 按 `study_name` 解析 | 空名取第一个；找不到就报错 |

### 14.5 失败策略：**全有或全无 + 响亮失败**
任一声明过不了门禁 ⇒ `register()` 抛错、**一个都不注册** ——
**不让「半套工具」进到运行期**（那比不注册更糟）。

### 14.6 接线守卫（`tests/test_server_wiring.py`，8 条）
- **上游那 45 个没被挤掉**（含 `cadstudio_*` ≥10 个 —— 规则 1 说两者不混用）
- **四批 20 条一条不少**地出现在工具表里
- 声明式工具**都**是 `solidworks_` 前缀
- **每种注入都有解析器**（否则运行期才炸）
- 每个注册工具的描述**非空**
- ⚠ 缺 `mcp` 库时整文件 **skip**

### 14.7 ⚠ 仍未做的（如实）
- **接线本身没在本机跑 MCP 客户端**；静态验证覆盖「注册数 / 命名 / 注入 / 描述」四项
- 20 条工具里，**只有 A 类那 14 条**有真机实测过的底层函数；
  钣金 6 条（C 类）的底层 `sw_sheet_metal.py` 仍自述**未实测** ⇒ 接线不改变这一点

### 14.8 规模
```
声明式注册器    mcp-server/tool_registry.py            ~370 行（一次性）
接线层          mcp-server/register_capabilities.py    ~120 行
四批声明        8 + 6 + 2 + 4 = **20 条**（**已注册可用**）
守卫测试        tests/test_tool_*.py + test_server_wiring.py   **72 条**
server 工具数   **45 → 65**
```
---

## 十五、真机验收那 6 条钣金（2026-10-01）：**只有 2 条能跑**

### 15.1 为什么必须做
上一轮把 20 条声明接进 `server.py`（45 → 65）—— 而那 6 条钣金工具的底层模块
`scripts/sw_sheet_metal.py` **自述「未在本机实测」**。
**⇒ 工具已在用户面前，底子却是空的。** 本轮在真机上跑了一遍（`probe_sheet_metal_e2e.py`）。

### 15.2 ⚠⚠ 结果
| 入口 | 真机结果 |
|---|---|
| `create_base_flange` | ✓ **真建出特征**（特征树出现「钣金6 / 基体-法兰1 / 平展型式6」） |
| `sheet_metal_evidence` | ✓ 读回正确（`thickness_m=0.002`、`has_base_flange=True`、`all_solid_bodies_are_sheet_metal=True`） |
| `create_one_bend` | ✗ `CreateDefinition(33)` 返回 None |
| `create_draft` | ✗ `CreateDefinition(3)` 返回 None |
| `create_edge_flange` | ✗ 设 `ReverseDirection` 报 `Property ... can not be set` |
| `create_gusset` | ✗ 设 `Thickness` 报同款 |

**⇒ 4 条已暴露的工具真机跑不了 —— 这比不暴露更糟。**

### 15.3 处理（照 `sw_surface.py` 的先例，**不删任何既有函数**）
1. `SHEET_METAL_RUNTIME_STATUS`（入口 → (可用?, 真机原因)）—— **不是「未测」，是「测了，不行」**
2. `require_verified(entry)` 守卫：**失败带原因**，而不是让用户看到裸 COM 错误
   （`Property ... can not be set` **完全指向不了真因**）
3. 5 条工具的描述里写明 `*** NOT USABLE ON THE TEST MACHINE ***` + 原因
4. **不删那 4 个函数** —— 正确形状尚未查明（swFm 取值错？FeatureData 属性名错？
   缺 `AccessSelections`？），删掉会让线索丢失

### 15.4 ⚠ 判据 A5 的又一块拼图
A5 现在有**两层**：签名对齐（原有）+ **运行期可达/可用**（新增）。
本轮证明第二层**不是形式主义** —— 6 条里 4 条签名层完全对、运行层直接失败。

### 15.5 本会话**第 5 次**踩「来源块覆盖范围不足」，这次终于机器可抓
- 形式：**一个来源块后面有两个代码单元**（常量 + 函数）⇒ 默认只覆盖第一个
- **⇒ `check_provenance` 现在直接打印两条最常见原因 + 修法**（含
  「`覆盖: 后续同级定义` 那行**不要**加 markdown 粗体」）
- 已实测验证：临时制造未覆盖 ⇒ 诊断确实打印；还原 ⇒ PASS