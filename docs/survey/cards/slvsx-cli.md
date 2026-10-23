# slvsx-cli（snoble/slvsx-cli）

<!-- survey: class=H; repr=constraint; orchestration=loop; verify=solver; deliver=mesh; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/snoble/slvsx-cli |
| 许可 | **GPL-3.0-or-later ⇒ 只读思想**（`LICENSE:6-11` 的 GPLv3 声明原文「either version 3 of the License, or (at your option) any later version」；`Cargo.toml:13` 写 `license = "GPL-3.0-or-later"`。`LICENSE` 只有 29 行**声明 + 归属段**，GPLv3 全文在 `libslvs-static/COPYING.txt`（553 行）；`libslvs-static/LICENSE:1-6` 另写「a fork of SolveSpace's libslvs」并给原项目信息。GitHub API 的 `license` 字段因抬头是自定义的 `# SLVSX License` 而报 `NOASSERTION`）|
| 元数据 | stars 1 · forks 0 · open issues 0 · 最近推送 2026-01-28T00:23:12Z · 语言 C++ · 默认分支 `main`（来源：`gh api repos/snoble/slvsx-cli`，2026-10-24 取）|
| 克隆 | `D:\ai3d-survey\repos\snoble__slvsx-cli`（shallow：`git rev-list --count HEAD` 得 1，tip `e92a44e`，提交时间 2026-01-28 00:20:43 +0000；体积 32 MB，来源：`Get-ChildItem -Recurse -File | Measure-Object Length -Sum` 实测 2026-10-24）|
| 证据等级 | **读码**（非「实测」：本机能编译 Rust，但构建要在克隆里跑 cmake 生成 `libslvs-static/build`，那会写脏只读克隆，故未构建、未跑任何 solve）|

## 1. 一句话定位

**把「几何坐标」从模型手里拿走，只让它写「约束」**：输入是一份 `slvs-json/1` 文档（点/线/圆/弧/平面 + 39 种约束 + 参数表达式），输出是 SolveSpace 求解后的**坐标**，加可选 STL/DXF/SVG。约束求解外置这条路线的**最干净样本**。

A–J 里归 `H`：它代理的不是 CAD GUI，而是 **SolveSpace 求解库（libslvs）的 C API**——`ffi/real_slvs_wrapper.c` 是它自己写的 1362 行 C 包装层（`(Get-Content …).Count` 实测）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：JSON 文档，四段固定：`schema`（必须 `slvs-json/1`）、`units`、`parameters`（名→数）、`entities`、`constraints`（`crates/core/src/ir.rs:5-16`）。另有 5 个 CLI 子命令 `validate/solve/export/capabilities/schema`（`crates/cli/src/main.rs:59-89`）。

**中间表示（这就是「约束怎么表达」）**：
- **实体 8 类**：`Point` / `Point2D` / `Line` / `Line2D` / `Circle` / `Arc` / `Cubic`（4 控制点贝塞尔）/ `Plane`（`ir.rs:46-127`）。2D 变体必须带 `workplane` 指到某个 `Plane` 实体，3D 变体不带——**2D/3D 是两种实体，不是一个标志位**。
- **约束 39 类**（`ir.rs:213-407`），全部是 `#[serde(tag = "type", rename_all = "snake_case")]` 的枚举变体，故 JSON 里就是 `{"type":"distance","between":[…],"value":…}`。字段形状有三种粒度：**引用两实体**（`perpendicular{a,b}`）、**引用列表**（`parallel{entities}`、`equal_length{entities}`）、**带值**（`distance{between,value}`、`angle`、`diameter`、`length_ratio`、`point_plane_distance`…）。
- **值可以是表达式**：`ExprOrNumber` 是 `Number(f64) | Expression(String)` 的 `untagged` 枚举（`ir.rs:170-197`），所以 `"value": "$W/2"` 合法。求值器是**手写递归下降**：先试 `parse::<f64>`，再查参数表（`$` 前缀可有可无），再按 `+ -` → `* /` 逆序找最后一个运算符切分（保左结合、括号计深），最后认 `cos/sin/tan/sqrt/abs` 与 `pi`，除法遇到 0 报错（`crates/core/src/expr.rs:14-120`）。
- **两个语义开关写在实体上**：`construction`（辅助几何）与 `preserve`（「被拖拽过」，求解时尽量少动它，`ir.rs:52-55`、`:156-167`）。

**生成**：不生成几何，把 IR 逐条翻成 libslvs 调用。实体走 `solver.rs:71-405`（每个实体分支里现算坐标/法向归一化，并维护 `entity_id_map` 字符串→内部整数 ID）；约束走**唯一一个 match**（`crates/core/src/constraint_registry.rs:43-473`），39 个变体全覆盖，其中 `Collinear` 与 `EqualAngles` 是**展开型**——前者造一条隐式线再挂 `point_on_line`（`constraint_registry.rs:400-426`），后者在相邻线对之间挂 `angle`/`equal_angle`（`:428-470`）。

**编排**：无内部循环，一次 CLI 调用一次求解（`crates/cli/src/commands.rs:56-74`）。`loop` 指的是它被设计成的用法：文档把「固定参考 → 加结构 → 加关系 → 参数化 → 逐步加复杂度」写成流程，且要求每步都解一遍（`docs/ITERATIVE_DESIGN.md:9-90`）。

**执行**：`Slvs_Solve(&s->sys, 1)`（`ffi/real_slvs_wrapper.c:721-739`），内部 ID 用固定偏移避让 SolveSpace 的保留句柄（实体 `1000+id`、约束 `10000+id`，见 `real_slvs_wrapper.c:709-711` 与 `:746`）；`KNOWN_ISSUES.md:1-20` 记着一次真实事故——重构时把这个偏移删了，导致 `Cannot find handle` 断言。

**验证**：三段，全部在看 §3.2/§3.3。

**交付**：`export -f svg|dxf|slvs|stl`（`commands.rs:105-127`），产物是**求解后的坐标**导出（`commands.rs:88-96` 先 solve 再 export）；`.slvs` 走 SolveSpace 的文本格式、8 位小数（`crates/exporters/src/slvs.rs:5-40`）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 ★ 求解器怎么报 DoF / 冗余：**三条通道，两条是断的**

**通道一 —— 返回码（唯一真实生效的）**：SolveSpace 只回 4 个结果码，C 包装把它们压成 0/1/2/3（`ffi/real_slvs_wrapper.c:727-738`），Rust 侧再映射成 4 个错误变体（`crates/core/src/ffi.rs:1252-1264`），最后由 `Solver::map_ffi_error` 落成业务错误（`crates/core/src/solver.rs:38-56`）：

| SolveSpace 结果 | 包装层返回 | Rust 错误 | 含义 |
|---|---|---|---|
| `SLVS_RESULT_OKAY`(0) | 0 | 无 | 解出来了 |
| `SLVS_RESULT_INCONSISTENT`(1) | 1 | `Overconstrained` | 约束互相打架 |
| `SLVS_RESULT_DIDNT_CONVERGE`(2) | 2 | `SolverConvergence{iterations}` | 不收敛（`iterations` 填的是**配置值**，不是真实迭代数，`solver.rs:428-431`）|
| `SLVS_RESULT_TOO_MANY_UNKNOWNS`(3) | 3 | `Underconstrained{dof: 0}` | 欠约束（**dof 写死 0**，`solver.rs:46-49`）|

定义见 `libslvs-static/include/slvs.h:199-203`。

**通道二 —— `sys.dof`（算出来了，但从未传出去）**：`slvs.h:196` 里 `dof` 是求解结果结构体的字段；C 包装**专门写了一个取 DoF 的函数** `real_slvs_get_dof`（`real_slvs_wrapper.c:857-860`），但 Rust 的 FFI 声明区（`ffi.rs:44-400` 的 `extern "C"` 块）**没有声明它**，全仓 `crates/**/*.rs` 对 `get_dof` 的引用数为 **0**（`Select-String -Pattern get_dof` 实测）。⇒ **DoF 数值永远到不了输出**。

**通道三 —— `diagnostics.dof`（硬编码的假值）**：`SolveResult` 里确有 `diagnostics{iters, residual, dof, time_ms}` 结构（`ir.rs:420-426`），但组装时四个字段全部写死：`iters: 1, residual: 0.0, dof: 0, time_ms: 1`（`solver.rs:574-584`）。`examples/*_solution.json` 里 12 个非空样例**逐文件都是同一组** `"iters":1,"residual":0.0,"dof":0,"time_ms":1`（`examples/02_triangle_solution.json:1-7`；`ConvertFrom-Json` 逐文件读 `diagnostics` 实测，2026-10-24）。

**冗余约束的现状：会被报成「矩阵奇异」，而且这条分支本身是错映射**。`slvs.h:203` 定义了 `SLVS_RESULT_REDUNDANT_OKAY = 4`（「冗余但能解」），C 包装的 if 链**没有 4 这个分支**，落到末尾 `return -1`（`real_slvs_wrapper.c:728-738`）→ Rust 把 -1 映射成 `InvalidSystem`（`ffi.rs:1260`）→ 用户看到的是「constraint matrix is singular，通常是冗余约束」这段**猜测式**文案（`crates/core/src/error.rs:26-31`）。⇒ 冗余与真正奇异**分不开**，而且「冗余但可解」的模型会被判失败。

### 3.2 ★ 失败怎么回传：**stderr + 一个从未被使用的退出码表；stdout 上没有错误 JSON**

- 求解失败时 `handle_solve` 直接把 `?` 抛上去（`commands.rs:69`），`main` 返回 `anyhow::Result`（`main.rs:91`）⇒ 进程按 `Termination` 默认行为打印 `Error: …` 到 stderr、退出码 **1**。
- 仓库里**专门定义了一张退出码表**：参数/schema 错 2、不收敛 3、过约束 4、欠约束 5、FFI 6、奇异 7（`error.rs:53-63`），并配了单测（`error.rs:71-94`）。但全仓 `crates/**` 与 `mcp-server/**` 对 `exit_code()` 的调用数为 **0**（`Select-String -Pattern exit_code` 实测，只有定义与测试命中）⇒ **那张表是死的**，写脚本的 agent 无法靠退出码区分「过约束」和「欠约束」。
- **stdout 在失败时是空的**，错误只走 stderr：`commands.rs:69-72` 只有 `solve` 成功才 `serde_json::to_string_pretty(&result)` 写出，失败路径没有 JSON 出口。旁证：`examples/` 下 16 个 `*_solution.json` 里有 **4 个是 0 字节**（`03_overconstrained`、`05_parallel_perpendicular`、`08_angles`、`09_coincident`；`Get-ChildItem examples\*_solution.json | Select Length` 实测），包括那份专门叫 overconstrained 的。
- **MCP 壳把 stderr 当错误载荷**：`subprocess.run(..., check=True)`，失败时回 `{"status":"error","error": e.stderr or str(e)}`（`mcp-server/slvsx-mcp.py:56-76`）⇒ 错误串里通常混着 `Error: System is inconsistent` 之类；成功则回 `{"status":"success","solution":{…}}`（`:68-71`）。
- **求解前的验证器是真正的报错主力**：校验器按 6 个步骤顺序跑——schema 版本、实体 ID 唯一、单位枚举、约束引用存在、实体引用「必须后向引用」、约束的实体类型合法（`crates/core/src/validator.rs:12-20`）；报错带 JSON Pointer（`pointer: Some("/constraints/3")`，`validator.rs:159-174`）。两类**先验拒绝**写得像人话并给替代写法：3D 里禁用 `symmetric`（改 `symmetric_horizontal`/`_vertical` + workplane，`validator.rs:199-210`）、`tangent` 不接受圆只接受弧/三次/线（`validator.rs:213-241`，`ir.rs` 的 schema 描述里也写了「Arc or line (NOT circle)」，`commands.rs:364-366`）。
- **表达式求值失败会被悄悄当成 0**：约束装配里对表达式用的是 `evaluator.eval(e).unwrap_or(0.0)`（`constraint_registry.rs:56-61,71-76,437-440`）⇒ 打错一个参数名，得到的是「距离=0」的约束，而不是报错。

### 3.3 工具/操作集清单与粒度

- **CLI 5 个子命令**：`validate` / `solve` / `export` / `capabilities` / `schema`（`main.rs:59-89`）。粒度是「一次调用处理一整份文档」，没有增量编辑、没有会话状态。
- **MCP 面 4 个方法**：`solve` / `export_svg` / `validate` / `capabilities`（`mcp-server/slvsx-mcp.py:120-134`），是对 CLI 的 `subprocess` 包装，**不是**真 MCP 协议（`MCP_DESIGN.md` 设计的 `rmcp` 版服务端并未落地，见 §5）。
- **约束操作集 39 种**（`ir.rs:213-407`）、**实体 8 种**（`ir.rs:46-127`）、**FFI 的 `add_*` 方法 46 个**（`crates/core/src/ffi.rs` 里 `pub fn add_` 计数）、**C 侧导出函数 51 个**（`pub fn real_slvs_` 计数）——约束数 39 与后两个同量级，说明「操作集」是按 SolveSpace 的原语一一映射，而不是按用户任务切。
- **自描述能力有两份，都落后于代码**：`capabilities` 硬编码只列 13 个约束（`commands.rs:136-140`），`schema` 硬编码只列 16 个约束（`commands.rs:288-423`），而 IR 是 39 个。

## 4. 运行条件与依赖

- Rust workspace 三 crate：`crates/core`、`crates/cli`、`crates/exporters`（`Cargo.toml:1-6`），`rust-version = "1.75"`、edition 2021（`Cargo.toml:11,15`）。
- 要 **C/C++ 工具链 + cmake**：`build.rs` 用 `cc` 编译 `ffi/real_slvs_wrapper.c`，并链接**预构建**的 `libslvs-static/build` 静态库 `slvs-combined`（`crates/core/build.rs:13-34`）；`libslvs-static/` 是 SolveSpace 的 fork，内含 eigen 等 extlib（`libslvs-static/LICENSE:1-6`）。
- 本机（Windows / Py3.14.7 / RTX 4080S 16GB）：`cargo` 与 `cmake` 都在（`Get-Command cargo/cmake` 实测），但 `libslvs-static/build` 目录**不存在**（`Test-Path` 为 False，2026-10-24）⇒ 必须先在克隆里跑 cmake 才能编。**我没跑**：那会往只读克隆写构建产物。`build.rs` 只处理 linux/macos 的系统库（`build.rs:36-46`），**Windows 的链接路径没有对应分支**，能否编成未验。显存无关（纯 C++/Rust，无模型）。
- 发布形态是**静态单文件**二进制（`README.md:11`），CI 另有 linux/macos 产物（`slvsx-linux/`、`slvsx-macos/`）；WASM 绑定存在但需 `--features wasm`（`crates/core/src/wasm.rs:1-25`）。

## 5. 失败模式与已知坑

- **文档承诺的 DoF 反馈根本不存在**：`docs/USAGE_EXAMPLES.md:175-179` 教「solve 后看 `diagnostics.dof`：0 = 完全约束，>0 = 欠约束」，`docs/MCP_DESIGN.md:253-264` 甚至画了带 `"dof": -2` 与 `problematic_constraints` 的错误载荷——**代码里 dof 恒 0、`status` 恒 `"ok"`、`problematic_constraints` 不存在**（`solver.rs:574-584`）。
- **能力清单三处不一致**：IR 39 / schema 16 / capabilities 13（§3.3）。照 `capabilities` 写约束的 agent 会以为只有 13 种。
- **两个模块是空壳**：`crates/core/src/translator.rs:12-18` 的 `translate()` 校验完引用就返回，注释写着「Translation logic will go here」，真正的翻译在 `solver.rs`+`constraint_registry.rs`；`crates/core/src/schema_validator.rs:5-6` 自陈「Simple … Will be replaced with jsonschema crate when linking issues are resolved」。
- **配置项是摆设**：`SolverConfig.tolerance`(1e-6) 与 `timeout_ms` 从未被读取（`solver.rs:7,9` 定义；`solver.rs:23` 给整个 `config` 字段挂 `#[allow(dead_code)]`）；`max_iterations`(1000) 只在拼错误信息时被读一次（`solver.rs:428-431`）。
- **FFI 层的历史事故**：`KNOWN_ISSUES.md:1-20` 记「约束处理全线失效」的根因是 ID 偏移被删，触发 `libslvs-static/src/dsc.h:534` 的 `Cannot find handle` 断言；`KNOWN_ISSUES.md:29-35` 记 SIGABRT 是 mimalloc 与系统 malloc 混用，已移除 mimalloc。`docs/DEBUG_METHODOLOGY.md:29-40` 另记「改了 C 文件 Rust 不一定重编」的坑，解法是 `touch` + `cargo clean -p slvsx-core`。
- **并发/句柄问题**：`docs/DEBUG_METHODOLOGY.md:10,26` 把「Handle isn't unique」列为常见断言，建议 `RUST_TEST_THREADS=1` 跑测试 ⇒ 这个库在同一进程内并发建多个求解系统是不安全的。
- **`Circle` 的半径在「圆心引用某点」这条路径上取的是 IR 值而非求解值**：注释直说「Radius comes from the IR since we can't easily get it from FFI for this case」（`solver.rs:475-483`）⇒ 若半径本该由求解器算出，这里会回一个陈旧值。

## 6. 对我方目标的可用处（机制层面，含边界）

1. **「只写约束、坐标交给求解器」这条路线的最小可用接口**：39 个约束变体 + 8 种实体 + 表达式参数，就是一份可直接对照的**约束 IR 设计清单**；它证明了「模型不写坐标也能把形状定死」在 2D/3D 点线圆层面上是成立的。（来源：本卡 §8 证据清单）
2. **约束的三种字段粒度**（引用两实体 / 引用列表 / 带值）是个好模板：普通模型最容易错在「哪个约束要几个实体」，把 arity 写进 schema 形状里比写进自然语言提示更有效。
3. **展开型约束**（`collinear` → 隐式线 + N 个 `point_on_line`；`equal_angles` → 相邻对挂 `angle`）是**降低模型表达负担**的正确做法：给高层语义、在内部展开成原语，且展开用的 ID 有高位偏移避免撞号（`constraint_registry.rs:413,421,452`）。
4. **先验拒绝的写法**（3D 禁用 symmetric、tangent 不收圆）比「让求解器最后报奇异」好得多——**错误信息里直接给替代写法**，这是普通模型能自我修正的关键（`validator.rs:199-210,213-241`）。
5. **反面教训一**：求解器的诊断如果只回一个枚举码，再叠一层「dof 写死 0」，那么**看起来有诊断、实际没有**——这比不返回更坏，因为提示词和文档都会教模型去读它（§5 第一条）。我方任何 solver 型反馈都必须端到端验一遍「数值真的从内核到了 JSON」。
6. **反面教训二**：退出码表定义了却不用，等于没有（§3.2）。调用方只能靠 stderr 文本判错，无法机器判别。
7. **边界一**：它只有**点/线/圆/弧/贝塞尔/平面**，没有实体、没有布尔、没有特征、没有草图平面上的尺寸标注语义——离「参数化零件」还差一整层（拉伸/切除/圆角这些都不是约束）。
8. **边界二**：交付物是网格（STL）或 2D 图（DXF/SVG），**没有 STEP**；且 STL 是由已解坐标三角化的（`crates/exporters/src/stl.rs`），不含参数历史。
9. **边界三**：**GPL-3.0-or-later，代码一个字都不能进我方仓库**；能拿的只有「约束 IR 怎么设计、诊断怎么回传」这两类**思想**。

## 7. 许可与红线

- **GPL-3.0-or-later ⇒ 只读思想，不抄代码、不抄文本**（`LICENSE:6-11`、`Cargo.toml:13`）。整仓传染性：`libslvs-static` 是 SolveSpace 的 GPLv3 fork（`libslvs-static/COPYING.txt:1-5`，553 行全文），`ffi/real_slvs_wrapper.c` 是 SolveSpace C API 的包装，随整仓一并 GPL。
- 可读的东西：IR 的**枚举清单与字段形状**、求解器诊断的**设计取舍**、文档里对失败模式的分析。不可做的事：把任何 `.rs`/`.c`/`.h` 代码或文档段落搬进我方仓库。
- 克隆仓库只读，未改动任何文件（未构建，故未生成 `target/`、`libslvs-static/build`）。

## 8. 证据清单

- `LICENSE:1-29`；`Cargo.toml:1-6,13-16`；`libslvs-static/COPYING.txt:1-5`；`libslvs-static/LICENSE:1-6`
- `libslvs-static/include/slvs.h:196,199-203`
- `crates/core/src/ir.rs:5-16,46-127,170-197,213-407,420-426`
- `crates/core/src/expr.rs:14-120`
- `crates/core/src/solver.rs:5-25,38-56,71-405,428-431,437-571,574-584`
- `crates/core/src/constraint_registry.rs:43-473,400-426,428-470`
- `crates/core/src/ffi.rs:44-400,1252-1264,1266-1302`
- `crates/core/src/validator.rs:12-20,159-174,199-210,213-241`
- `crates/core/src/error.rs:17-31,53-63,71-94`
- `crates/core/src/translator.rs:12-18`；`crates/core/src/schema_validator.rs:5-6`
- `crates/cli/src/main.rs:59-89,91-124`；`crates/cli/src/commands.rs:56-74,105-127,136-140,288-423,364-366`
- `ffi/real_slvs_wrapper.c:709-711,721-739,746,857-860`
- `crates/exporters/src/slvs.rs:5-40`；`crates/exporters/src/stl.rs`
- `mcp-server/slvsx-mcp.py:56-76,120-134`
- `examples/02_triangle_solution.json:1-7`；`examples/` 下 16 个 `*_solution.json`（其中 4 个 0 字节）
- `docs/USAGE_EXAMPLES.md:175-179`；`docs/MCP_DESIGN.md:253-264`；`docs/ITERATIVE_DESIGN.md:9-90`；`docs/DEBUG_METHODOLOGY.md:10,26,29-40`
- `KNOWN_ISSUES.md:1-20,29-35`；`README.md:11,15`
- https://github.com/snoble/slvsx-cli（`gh api` 元数据，2026-10-24）

## 9. 未确认事项

1. **没有构建、没有跑过任何 solve**：`libslvs-static/build` 不存在、Windows 链接分支缺失（`crates/core/build.rs:36-46`），所以「DoF 传不出来」「冗余→奇异」这些都是**读码结论**，未经运行验证。
2. `SLVS_RESULT_REDUNDANT_OKAY`(4) 落到 `return -1` 的推论，依赖「SolveSpace 确实会返回 4」这一前提；我没有找到能触发它的样例，`examples/03_overconstrained.json` 也没有对应的非空输出（§3.2）。
3. `capabilities`/`schema` 里的 13 与 16 是逐条数 `commands.rs` 得来的静态数；运行期 `slvsx capabilities` 的实际输出未验。
4. `examples/*_solution.json` 里那 4 个 0 字节文件是「失败路径不产 JSON」的旁证，但也可能是生成器当时出错留下的空文件——我没有它们的生成过程记录，无法区分。
5. `crates/core/tests/` 与 `tests/` 下的测试数、通过率未跑（10 个测试文件里含 1 个 `.js`，`get-ChildItem tests -Recurse` 实测），故本卡对「作者跑过什么」不做断言。
