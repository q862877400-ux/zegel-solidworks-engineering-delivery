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
---

## 十六、追根因（2026-10-01）：**修好一层、否证一个假设、留两层未明**

### 16.1 为什么值得花一轮追根因
上一轮测出「4/6 不可用」就停了 —— 那只回答了**「不行」**，没回答**「为什么」**。
**⇒ 而「为什么」才是判据 A5 要的功课。** 本轮逐层追（证据 `probe_featuredata_access.py`）。

### 16.2 ① `CreateDefinition(fm)` 实测 —— 决定性的分界
```
✓ CreateDefinition(34) BaseFlange → 非 None
✓ CreateDefinition(37) EdgeFlange → 非 None
✓ CreateDefinition(118) Gusset    → 非 None
✗ CreateDefinition(3)  Draft      → **None**
✗ CreateDefinition(33) OneBend    → **None**
```
**⇒ Draft 与 OneBend 不走 `CreateDefinition`。** 反射里确有专用入口
（`InsertSheetMetal3dBend` / `IInsertSheetMetalEdgeFlange2` / `InsertGussetFeature3` /
`InsertSheetMetalBaseFlange2`，**均存在**）—— **但正确用法未查明**。

### 16.3 ② 一个**被否证的**假设（我自己的）
我原以为「属性设不上 = 缺 `AccessSelections`」（**该文件自己的文档串就这么写**）。
真机逐个试三种 `Component`：
| Component | 结果 |
|---|---|
| Python `None` | `'类型不匹配'`（`TYPE_E_TYPEMISMATCH`） |
| `VARIANT(VT_DISPATCH, None)` | `'服务器出现意外情况'`（`RPC_E_SERVERFAULT`） |
| `False` | `'类型不匹配'` |

**⇒ 全失败。** 官方文档：「Gains access to the selections that **describe this feature**」
—— 那是**编辑已有特征**用的，**不是创建用的**。
**⇒ 我据此加的修改**已全部撤回**（`patch_revert_access.py` 留痕），不让错的东西留在代码里。**

**⚠ 这条值得记进方法论：文档串写的「必须做 X」**不等于**「X 就能让功能跑通」；
X 的**语义**（编辑 vs 创建）决定它适不适用。**

### 16.4 ③ 一个**真的修好了**的缺陷：跨接口属性泄漏
`create_edge_flange` 设的 `data.ReverseDirection` **不属于** `IEdgeFlangeFeatureData`
（43 个成员里**没有**）—— 它是 **`IDraftFeatureData2`**（25 个成员）的成员。
**⇒ 作者把「拔模」接口的属性抄到了「边法兰」代码里**（正是铁律 1 禁止的「凭印象写」）。

删掉后真机报错**从** `Property ... can not be set` **变为** `CreateFeature(37) 创建失败`
⇒ **属性那一层确实通了。**

**⚠ 不臆造替代**：最接近的 `ReverseOffset` / `ReversePositionOffset` 是**偏置**方向，
与「法兰方向」语义不同 —— **边法兰没有「反向」这个开关**。

### 16.5 仍未查明的（如实留白）
- `create_gusset`：`Thickness` **是** `IGussetFeatureData` 的成员（19 个里有）**却设不上**
- 这 4 个的**正确创建路径**（是否该改用专用 `Insert*` 入口）
**⇒ 状态表已写入三层根因结论；工具描述仍是 `*** NOT USABLE ***`。**

### 16.6 对判据 A5 的意义（又深一层）
```
第一层：签名对齐           ← 原有
第二层：运行期可达/可用     ← 上轮加
第三层：**根因层次**        ← 本轮加：是「入口选错」？「属性不属于该接口」？还是「状态没准备」？
⇒ 第三层才是能指导修复的那一层。前两层只能告诉你「不许用」。
```
---

## 十七、追到**最后一层**根因（2026-10-01）：`create_gusset` 的**接口用错了**

### 17.1 决定性发现：官方类型表里有**两个** Gusset 接口
| 接口 | category | 成员数 | 谁在用 |
|---|---|---|---|
| **`ISMGussetFeatureData`** | `Feature Interfaces/**Sheet Metal**` | 28 属性 | ★ **才是对的** |
| `IGussetFeatureData` | `Feature Interfaces/**Weldments**` | 19 成员 | **模块用了这个** |

枚举 `swFmSMGusset` 的描述明写 "**Sheet metal** gusset"（名字里的 **SM** 就是 Sheet Metal）。
**两者共有成员只有 3 个**（`AccessSelections` / `ProfileType` / `ReleaseSelectionAccess`）。

**⇒ 原代码设的 4 个属性 `Thickness` / `ProfileDistance1` / `ProfileDistance2` /
`ProfileAngle` **全部是焊件接口的名字** ⇒ `CreateDefinition(118)` 返回的对象**不是那个接口**
⇒ **对任何成员都没反应**（真机实测：连**读**都读不到，`read Thickness → ✗ <unknown>.Thickness`）。**

### 17.2 修法与验证（真机读回全部成功）
```
spec.thickness          → GussetThickness      ✓ 回读 0.002
spec.profile_distance_1 → ProfileHeightDim     ✓ 回读 0.01
spec.profile_distance_2 → ProfileLengthDim     ✓ 回读 0.01
spec.profile_angle      → ProfileAngleDim      ✓ 回读 45.0
（对照组）Thickness / ProfileDistance1 → ✗ 仍失败 ⇒ 证明改对了
```

### 17.3 ⚠ 本轮**否证了三个假设**（都是我自己提的）
| 假设 | 怎么否证的 | 结论 |
|---|---|---|
| **专用 `Insert*` 入口就是正解** | `InsertGussetFeature3` 的官方说明明写「for pre-selected faces of a **weldment**」 | **假线索** —— 有专用入口 ≠ 就是那条路 |
| **属性设不上 = 缺 `AccessSelections`** | 真机三种 `Component`（`None` / `VARIANT(VT_DISPATCH,None)` / `False`）**全失败** | 官方说它是「取得描述**该特征**的选区」= **编辑**用，**不是创建用**；**修改已撤回** |
| **属性设不上 = mark 不对** | `SetSelectedObjectMark(1,1/2/4/0,0)` 与 `SelectByID2(mark=1/2/4/0)` **都返回成功**，属性仍设不上 | **mark 不是属性层的真因**（**但可能在**创建**那层起作用** —— 见下） |

### 17.4 现在的状态：**属性层已修，剩最后一层**
`create_gusset` / `create_edge_flange` 的报错**都已从** `Property ... can not be set`
**变为** `CreateFeature(118/37) 创建失败` ⇒ **属性层确实通了。**
**⇒ 剩最后一层：`CreateFeature` 需要**选择状态**。**
官方在同类特征（焊件 gusset）上明写「select two faces ... **with a Mark of 1**」
—— **mark 可能在**创建**这一层才起作用**。**未查明，不猜。**

`create_one_bend` / `create_draft`：`CreateDefinition(3/33)` 返回 None
⇒ **这两个类型不走 `CreateDefinition`**（专用入口存在，但「存在」已被证明不等于「就是这条路」）。

### 17.5 ⚠⚠ 本轮暴露的**门禁盲区**（值得单独记）
`scripts/check_member_names.py` **全程 PASS**，却**没抓到「属性名不属于该接口」** ——
因为它的判据是「这个名字在**某个**接口里存在吗」，**不是**「在**这个**接口里存在吗」。

**⇒ 而 `ReverseDirection`（属拔模）用在边法兰上、`Thickness`（属焊件）用在钣金上，
都是这一类。** 该门禁**自己的文档串**早就写了这个失败模式（「5 个成员全是凭印象从别的族搬来的」）
—— **它知道，但判定粒度不够。**

**⇒ 下一步该做的门禁升级**：把「属性 → 接口」的归属也纳入检查
（数据源已具备：`C:\swapi\types\<Iface>\<Member>.md` 的目录结构本身就是归属表）。

### 17.6 判据 A5 的第四层
```
第一层：签名对齐         ← 原有
第二层：运行期可达/可用   ← §15 加
第三层：根因层次          ← §16 加
**第四层：成员与接口的归属** ← 本轮加：「这个名字属于**这个**接口吗」
⇒ 本轮的 bug 前三层**全部通过**（签名对、成员可达、根因是「接口用错」），
  只有第四层能抓到它。
```
---

## 十八、补上一条**记忆里悬着的**未完成项（2026-10-01）

### 18.1 起因：先查项目自己的记忆
按 `hindsight_search_knowledge_pages` 找到「SolidWorks skill 官方 API 全覆盖缝合」页，
其中记着一条**具体未完成项**：
> 「AST 审计发现 **18 个裸 by-ref 出参**（6 在 `sw_simulation.py` / 11 在 `sw_topology.py` /
> 1 在 `sw_render_material.py`），`fix_bare_outparams.py` 可修」

**⇒ 核实：那个工具**不存在**，所以这条**一直悬着**（既没人修，也没人再查）。**

**⚠ 这正是记忆库的用途**：它记下了「知道但没做完」的事 —— 而代码本身看不出来。

### 18.2 新增 `scripts/audit_byref_args.py`
**判据与 `audit_call_arity.py` **同源**（不另立一套）**：
`Int32&` 这类**标量出参计入**「调用方要传的实参」，`Object&` / `Variant&` / `Dispatch&` **不计入**
⇒ 「第 i 个实参 ↔ 第 i 个计位形参」是确定的，可以逐位核对。

**违规判据**：某计位形参以 `&` 结尾（且是标量）、而对应实参**不是** by-ref 包装器
（`out_i4()` / `_out_i4()` / `VARIANT(VT_BYREF…)` / 从这些构造赋来的变量）。

### 18.3 实测结果：**0 处**（检查 674 个调用点）
**⇒ 当前口径下没有裸传。** 记忆里的 18 处**要么已被后续工作修掉、要么口径不同**
—— **如实记为「记忆快照与当前不一致」，不宣称是我修的。**

### 18.4 ⚠ 工具自己犯过 3 个假阳性（全修了 —— 这也是本轮的实质工作）
| 假阳性 | 真因 | 修法 |
|---|---|---|
| `_out_i4()` 被报 | 正则只认 `out_` 开头，**没允许前导下划线** | 改 `_?out_\w*` |
| 同一调用点报两遍 | `break` 放在内层循环 | 提到外层 + `reported` 标志 |
| `v_size` 被报 | 它上一行**就是** by-ref 构造（`VARIANT(VT_BYREF\|VT_R8, 0.0)`），只是先存进变量 | **加局部数据流** `byref_variables()` |

**⇒ 教训：一个只报「裸传」的工具，自己就可能制造三类假阳性。**
**⇒ 而假阳性会让人不再信这个工具** —— 所以修它们和写工具一样重要。

### 18.5 不变量（`tests/test_no_bare_byref_args.py`，3 条）
1. **0 处裸传**，且**检查量 ≥300** —— 后者防的是「审计器坏了导致假绿」
2. **负例：种一个裸传进临时文件，审计器必须报出来**
   —— **这条比第 1 条更重要**：一个永远返回 0 的审计器也能让第 1 条通过
3. CLI 可跑（`--help`）

### 18.6 方法论收获：**「防假绿」本身要写进测试**
本项目已有的门禁都是「断言通过」，但**没有一条断言「门禁自己还能抓到东西」**。
本轮的负例测试补上了这个缺口 —— **建议后续给 `check_member_names` / `check_provenance`
也各加一条负例**（种一个违规，断言门禁报出来）。
---

## 十九、给四条门禁各加**负例测试**（2026-10-01）

### 19.1 起因
上一轮给裸 by-ref 审计加负例时发现：**本项目没有任何一条「门禁能抓到」的测试** ——
所有门禁测试都是「断言通过」。
**⇒ 一个永远返回 0 的坏门禁，能让所有「断言通过」的测试全绿。**

**⇒ 新原则（已落进本档）：先证明门禁有牙齿，再相信它的沉默。**

### 19.2 新增 `tests/test_gate_negative_cases.py`（8 条）
| 门禁 | 负例（种违规，断言报出） | 正例（断言不误杀） |
|---|---|---|
| `check_provenance` | 无来源块的模块 ⇒ 必须报 | 带合规来源块的同样代码 ⇒ 必须放行 |
| `check_diff_markers` | 行首空白 + `+ ` 的补丁前缀 ⇒ 必须报 | 干净文件 ⇒ 不报 |
| `check_member_names` | 官方成员集必须**能分辨**真假（`CreateFeature` 在、编造名不在）| — |
| `check_union_conventions` | 两种不同许可不得归一成同一值 | 全角括号附注必须被去掉 |
| **本文件自己** | — | **本测试文件自己必须通过来源门禁** |

### 19.3 ⚠ 两条「失败」是**我误解了门禁的契约**（不是门禁坏了）
1. **我种了 git 冲突记号 `<<<<<<< HEAD`** —— 而 `check_diff_markers` 查的是
   **被粘贴进来的补丁行**（行首空白 + `+`/`*` + 空白/EOL，且括号深度 ≤ 0）。
   git 冲突记号在行首**必然让 `py_compile` 报语法错** ⇒ 那是 `compileall` 的活；
   **本门禁补的正是「编译抓不到」的那一类**（该门禁的文档串写着「三轮踩坑才做对」）。
2. **我要求 `normalize_license` 做大小写归一**（`MIT` == `mit`），
   而它的文档串只说「归一化到白名单比对用的基名」——**大小写不在它承诺的范围里**。

**⇒ 教训：写负例前先把**契约**读清楚。**
**⇒ 因为「以为门禁坏了」和「门禁真坏了」后果一样糟 —— 都会让人不再信它。**

### 19.4 一种更省事的负例写法（本轮用到的）
`check_provenance.check_file(path, whole_file)` 与 `check_diff_markers.scan(path)`
**都收路径** ⇒ 可以**在临时目录里种**违规，**完全不碰真仓库**。
**⇒ 给门禁加负例时，优先选「能收路径的内部函数」这一形态** —— 若某条门禁只能读真仓库，
可以考虑把它的判据抽成收路径的纯函数（**不是为了测试而重构，而是为了让判据可被独立验证**）。

---

## 二十一、⚠ **更正一处事实错误**（2026-10-01）

### 21.1 我第 22 轮说错了什么
本档「十八」里我写着：
> 「核实：那个工具**不存在**，所以这条一直悬着」

**⇒ 错了。** `fix_bare_outparams.py` **存在**，在**工作区根目录**：
```
D:\AI\SW\fix_bare_outparams.py          5.0 KB  改于 2026-10-01 03:17
D:\AI\SW\find_bare_outparam_sites.py    4.2 KB  改于 2026-10-01 03:16
```
**我**只在代码副本 `C:\swprojects\sw-skill-fork\` 里找，没在工作区 `D:\AI\SW\` 里找**，
就断言「不存在」。

**⇒ 这正是「查不到就说查不到」要防的错：把「我这一处没找到」说成「不存在」。**

### 21.2 连带影响
第 22 轮那个「**0 处**」的结果，很可能是**这两个脚本已经跑过**的结果。
我当时写的是「要么已被后续工作修掉、要么口径不同」—— **推测方向对，但我没去核实**。
**⇒ 现在核实了：工具在，且其时间戳（03:16/03:17）与那批工作同期。**
**⇒ 「0 处」这个**结论**仍然成立（我用独立写的审计器复核过），
但「工具不存在」这个**前提**是错的。**

### 21.3 教训（值得进 AGENTS.md 层面）
> **查「某个东西在不在」时，必须把**两个仓库**都查过**：
> 代码副本 `C:\swprojects\sw-skill-fork\` **与**工作区 `D:\AI\SW\`。
> **只查一处得出的「不存在」，是「我没找到」的另一种说法。**

### 21.4 ⚠ 顺带治住一个**真实陷阱**：工作区根遮蔽依赖包
**这是本轮的另一个实质发现，来自实测接线时撞上：**
```
D:\AI\SW\mcp.py   ← Python 把**当前目录**放在 sys.path[0]
⇒ 任何以 D:\AI\SW 为 CWD 的 Python 进程里，`import mcp` 拿到的是**那个脚本**
⇒ ModuleNotFoundError: No module named 'mcp.server'; 'mcp' is not a package
⇒ **`mcp-server/server.py` 在该 CWD 下根本 import 不了**
```
**⚠ 而那个错误信息**看不出是「被本地文件遮蔽」** —— 指向不了真因。**

**⇒ 新增 `scripts/check_workspace_shadowing.py`**：对 `server.py` 用到的顶层第三方包，
检查工作区根有没有同名 `.py`/目录 ⇒ 有就报出 + **给修法**。
**⚠ 它**不自动删任何东西**（工作区里的 ~600 个脚本是历史产物，删不删由人定）。**

**⇒ 并配 4 条测试**（含**负例**：种一个 `mcp.py`，断言检查器报出来）。


---

## 二十二、B 类落地 + 修一个**真 bug**（2026-10-01）

### 22.1 新增 `scripts/sw_geometry_selectors.py`（B 类「点/方向」）
`sw_surface` 里 **4 个运行期可达**的创建器都收 `Object` 型的点/向量 ⇒ 直接暴露**违规则 3**
⇒ 加一层**声明式解析**（选择器**全部从模型派生**或**命名轴**，**绝不接受裸坐标**）：
```
点:   origin / bbox:min / bbox:max / bbox:center / centroid
方向: +x / -x / +y / -y / +z / -z   （与 sw_simulation.FACE_SELECTORS **同一套命名**）
```
**⇒ 真机实测 12/12 通过**（`probe_geometry_selectors_e2e.py`）。

### 22.2 ⚠⚠ 真 bug：守卫写了却**从没被接上**
```
真机 create_planar_surface → TypeError: 'NoneType' object is not callable
```
而 `require_runtime_available()` **第 13 轮就加了** —— **但没人调它**。
**⇒ 现在 13 个公开包装器先调守卫** ⇒ 报错变成
`RuntimeError: CreatePlanarSurface 在**本机运行期取不到**（getattr 得 None）—— …本机实测可取的入口：[…]`。

**⚠ 这条缺陷的性质值得记：**一个**存在但没人用**的守卫，与**没有守卫**等价，
而且更糟 —— 因为它会让人以为已经防住了。**

### 22.3 顺带修一处**文档串说谎**
`_invoke` 的文档串声称做「两层自检」（含运行期可取性），
而第 13 轮为不挡契约测试**撤掉了第 2 层却没改文档串**。
**⇒ 已改成只讲 arity，并写明可用性由调用方在调用前问。**
**⚠ 文档串与代码不符，比没有文档串更糟**（它会让人按不存在的行为去用）。

### 22.4 契约测试改到**新的职责边界**（15 passed，+1）
| 层 | 职责 | 怎么测 |
|---|---|---|
| `_invoke` | **形状**：参数个数 + 转发 | 用桩 modeler 调**私有的** `_invoke` |
| 公开包装器 | **形状 + 守卫** | **新增** `test_unavailable_method_raises_a_reasoned_error` |
**⇒ 既保住了第 13 轮「形状可测」的理由，又把守卫接上了。**

### 22.5 ⚠ 一个新发现（如实记，**未定性**）
真机建曲面：`spherical` / `toroidal` 返回**非 None**（真建出来），
`cylindrical` / `conical` 返回 **None**。
**⚠ 而 `sw_surface` 的包装器**不检查返回值** ⇒ 这是**静默失败**类。**
已知事实 30 早记过「可取 ≠ 调用成功」，但**没记过「同一批里哪些真的成」**。
**⇒ 未定性**（可能与参数有关），**不猜**。

### 22.6 ⚠ 本会话**第三次**犯同一个判定错
探针把「期望的报错」记成失败（3 项）⇒ 加 `expect_error`。
前两次：`test_sw_surface_signature_contract`、曲面探针。
**⇒ 这次把教训写进了探针本身（免得第四次）。**


---

## 二十三、`IModeler.Create*Surface` 的返回值**不可靠**（2026-10-01，四轮探针定性）

### 23.1 四轮探针的结果（**同一个调用跨次会变**）
| 轮次 | 探针 | 结果 |
|---|---|---|
| 13 | `probe_surface_array_shape.py` | `CreateCylindricalSurface` **成功** |
| 26 | `probe_geometry_selectors_e2e.py` | `spherical` / `toroidal` 成；`cylindrical` / `conical` **None** |
| 27 | `probe_cyl_none_matrix.py` + `probe_cyl_order_vs_axis.py` | **只有 `axis=(1,0,0)` 成**；受控实验**排除了顺序与单例状态** |
| 27 | `probe_surface2_correct_arity.py` | **只有 `CreateSphericalSurface`（非-2）成**；`*2` 全 **None** |

**⇒ 结论：返回值**不可靠** —— 不是「有些能有些不能」，而是**同一个调用跨次也会变**。**
**⚠ 这比「已知事实 30 的可取 ≠ 调用成功」更深一层：**连「这一族里哪些能用」都不是稳定事实**。**

### 23.2 顺带查清的官方事实
```
官方标记 Obsolete 的 4 个：CreateConicalSurface / CreateCylindricalSurface /
                          CreatePlanarSurface / CreateSphericalSurface（该族共 18 个）
`*2` 后继**运行期可达**（给错 arity 时报 `非选择性的参数` = DISP_E_PARAMNOTOPTIONAL）
  它**多一个 `RefDirection`**（官方 Parameters 段）
**⚠ 但按正确 arity 调 `*2`，**仍然返回 None ⇒ 换一代解决不了**。**
```

### 23.3 ⇒ 修法：**让失败可见**（唯一不依赖 COM 不稳定行为的改进）
`sw_surface._invoke` 现在对 `None` 返回值**抛带原因的 `RuntimeError`**，而不是把 `None` 悄悄交给调用方。
**⇒ 静默失败是本项目反复踩的头号敌人（已知事实 8 / 30 / 40）—— 这一改把它堵在源头。**

### 23.4 ⚠ 本轮又一次「文档串必须与代码同步」
`_invoke` 的文档串原本只写「参数个数自检」—— 而它**现在做两件事**（arity + 返回值检查）。
**⇒ 上一轮刚记过这条教训，本轮立刻用上。**


---

## 二十四、一个**否定结果**：「成员交集为空」判据抓不到它本来要抓的 bug（2026-10-01）

### 24.1 目标
已知事实 36 记着真阳性：`create_gusset` 用了**焊件**接口的成员名（`Thickness`），
却走 **钣金** 那条 `swFmSMGusset` 路 ⇒ 真机连读都读不到。
`check_member_names.py` **抓不到这一类**（只判「名字在**某个**接口里存在」）。

### 24.2 设想（零推断）
同一 `CreateDefinition` 得到的对象上用的成员**必须同属一个接口** ⇒
「拥有这些成员的接口**交集为空**」即确定有错。**⇒ 不需要 `CONST→接口` 映射表。**

### 24.3 🔴 结果：判据**不成立**（种负例证伪）
```
把 create_gusset 的 4 个成员名换回**焊件**那套（= 原 bug 原样）⇒ 检查**仍报 PASS**
```
**原理**：原 bug 那套名字**互相自洽**（全属 `IGussetFeatureData`）⇒
**代码并不自相矛盾**，只是**对上下文用错了接口**。
⇒ 「交集为空」只能抓「混用**互斥**接口的成员」，**抓不到「整体用错接口」**。

**⚠ 假阳性**：`BendRadius`/`Path`/`Profile`/`Thickness` 这类**通用名**遍布多个接口 ⇒
「交集非空」常是**蒙对的**（实测某组 16 个成员的「交集 1 个」即此）。

### 24.4 结论：本轮产出**不是一个门禁**，而是三条
1. 工具**按「诊断」定位** —— 退出码只反映「检查量不足」，**不冒充门禁**
   （**一个抓不到目标类别的门禁，会让人以为防住了**）。
2. 文档串与输出里**显式写出否定结果与原理**（后来者不必重走）。
3. 要抓那一类**必须有 `CONST → 接口` 映射表**；**可核验**的做法是从官方
   `swFeatureNameID_e` 的枚举描述里取，**不要手写**。

### 24.5 途中修掉**三处自己的错**（都记在文档串里）
| # | 错 | 真因 |
|---|---|---|
| ① | `检查过的块：0` 却报 PASS | **假绿**：`CreateDefinition` 实际是 `get_com_member(m, "CreateDefinition", N)`（**字符串+逗号**），正则只认括号形式 |
| ② | 23 个成员的**假阳性** | 分析范围「到下一个 `CreateDefinition`」**横跨几百行、吞掉多个函数** ⇒ 要贴合**所在函数** |
| ③ | 嵌套 `_apply(data)` **一个都没找到** | 正则 `^def` **只认顶格**，而实际形状是**缩进定义的嵌套函数** |

**⇒ 修完 `checked`：0 → 2 → 7；并加了「检查量 < 5 即 FAIL」的下限守卫**
（与 `audit_byref_args.py` 的「≥300」同源：**检查量太少本身就是假绿**）。


---

## 二十五、`create_one_bend` 真因查明并修复 + 一条**可核验的 `CONST → 接口` 映射**（2026-10-01）

### 25.1 官方 `CreateDefinition.md` 只接受 **35 个**常量
```
有:  swFmSketchBend (sheet metal sketched bend)
有:  swFmBaseFlange / EdgeFlange / SMGusset / SweptFlange / …
**没有: swFmOneBend**   ← 模块原用的那个
**没有: swFmDraft**     ← create_draft 用的那个
```
**⇒ 返回 `None` **是应然的** —— 合法枚举成员 ≠ `CreateDefinition` 接受的类型。**

### 25.2 修复：`SW_FM_ONE_BEND(33)` → `SW_FM_SKETCH_BEND(35)`
**真机复验：报错**往前推进了一层**：**
```
修前: CreateDefinition(33) 返回 None
修后: **CreateFeature(35) 创建失败**
```
**⚠ 仍标不可用**（真建出折弯还需选中折弯线/固定面），但**原因已具体化**。

### 25.3 🔴 统一诊断：三条现在**卡在同一层**
```
create_one_bend    → CreateFeature(35)  创建失败
create_edge_flange → CreateFeature(37)  创建失败
create_gusset      → CreateFeature(118) 创建失败
create_draft       → CreateDefinition(3) 未返回特征数据  ← **它的常量也错**
```
**⇒ 后续应集中攻 `CreateFeature` 那一层，而不是逐个猜。**

### 25.4 ★ 可核验的 `CONST → 接口` 映射（不手写）
`D:\AI\SW\gen_const_iface_map.py`：用**两侧官方文本**匹配
（`CreateDefinition.md` 的括注 × 接口 `_overview.md` 的 Description）：
**20 条唯一命中 / 4 歧义（不猜）/ 11 未映射（措辞不同）**。
**⇒ 这正是第 29 轮否定结果（事实 42）所缺的那张表，且**来源可核验**。**

### 25.5 ⚠ 两套官方源在这一族**分工不同**（重要）
| 源 | 给什么 | 不给什么 |
|---|---|---|
| `C:\swapi\enums\swFeatureNameID_e.md` | 成员名 + **描述** | **数值** —— 它的「Value」列**装的是描述** |
| `D:\AI\SW\_raw\**\enum_values_sldworks.txt`（反射） | **数值**（130 个成员） | 描述 |
**⇒ 查常量数值必须去反射；查描述去 swapi 枚举页。**


---

## 二十六、`create_gusset` 补上**整步缺失的官方步骤 3** + 两层分开取证（2026-10-01）

### 26.1 官方 Remarks 把 gusset 创建写成 **4 步**
```
1. CreateDefinition
2. **Pre-select** faces/lines/edges/vertices/points（legs）
3. **Specify `ProfileDimensionScheme` and modify other properties**   ← ★ 模块整步跳过
4. CreateFeature
```
**模块的 `_apply` 只设了 4 个**尺寸**属性，而步骤 3 的**头一句**从未设过。**
官方属性页还明写：
* `UseAngleDimForProfile`：「**valid only if `ProfileDimensionScheme` is set to 1**」
* `UseOffset`：「设为 true 后**必须设 offset distance**；**若未设参照点**，offset 作用于**假定参照点**」
  + Remarks 第 2 步：「**若未预选，则必须把 `UseOffset` 设为 true**」

### 26.2 ⚠ 修掉一处**自己引入的**不一致
第一版**无条件**把 `UseAngleDimForProfile` 置 True，而 spec 的角度默认 `0.0`
⇒ **「用角度维」却给 0 角度**。
**⇒ 改为条件式**（官方在 scheme=1 下给了两种**互斥**方案）：
```
有角度 ⇒ ProfileLengthDim + ProfileAngleDim + UseAngleDimForProfile=**true**
无角度 ⇒ ProfileLengthDim + ProfileHeightDim + UseAngleDimForProfile=**false**
```

### 26.3 ★ 两层**分开取证**（不把「改对属性」说成「修好工具」）
```
① 属性层（probe_gusset_props_readback.py）：按 _apply 原样设一遍再读回 ⇒ **8/8 成功**
② 创建层：同一个 data 直接 CreateFeature(118) ⇒ **None**
⇒ **失败原因不在属性层**；剩余阻塞在**步骤 2 的预选**
   （官方要求「一个折弯的两个平面」，夹具是**平板**）
```
**⇒ 本次修复**除掉了一个确证的缺陷**，但**不宣称 `create_gusset` 可用**。**

### 26.4 顺带修一处**文档与代码不符**
`create_one_bend` 上方的来源块仍写 `IOneBendFeatureData` / `swFmOneBend(33)`，
而上一轮已改用 `swFmSketchBend(35)` ⇒ **注释没跟上，已更正**。
**⇒ 文档与代码不符比没有文档更糟。**
