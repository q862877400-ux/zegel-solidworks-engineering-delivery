# vespo92/SolidworksMCP-TS

<!-- survey: class=H; repr=feature-tree; orchestration=single; verify=none; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `vespo92/SolidworksMCP-TS` · https://github.com/vespo92/SolidworksMCP-TS |
| 许可 | MIT（`LICENSE:1-3` 原文 `MIT License` + `Copyright (c) 2025 ESPO Corporation`）⇒ 可借鉴，移植须保留版权行；★ 与 `andrewbartels1` 同版权人（同一家族，见 `sw-andrewbartels1.md` §3.4）|
| 元数据 | stars 243 · 最近推送 2026-09-20T00:41:22Z · 语言 TypeScript · 仓库 5059 KB（来源：`gh api repos/vespo92/SolidworksMCP-TS`，2026-10-24 取）|
| 克隆 | `C:\swprojects\SolidworksMCP-TS`（HEAD `ea5539`，2026-09-19 19:41:20 -0500；与远端 `pushed_at` 隔一天 ⇒ 基本同步）|
| 证据等级 | 读码（未跑 `npm test`：克隆内跑测会写 `node_modules`/覆盖率产物，违反「不改 C:\swprojects」纪律）|

## 1. 一句话定位

**Node/TypeScript 侧的 winax COM 网关**：把 SolidWorks 包成 96 个工具对象（默认只注册 86 个），靠「简单操作直连 COM、复杂操作生成 VBA 宏再 `RunMacro2`」的复杂度路由兜住 winax 的参数上限；README 自己写「**most tools have not been validated against a live SolidWorks instance**」。（来源：本卡 §8 证据清单）

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：MCP stdio。工具是**纯对象数组**——`{ name, description, inputSchema: z.object({...}), handler }`（`src/tools/modeling.ts:4-20` 起），不是 SDK 的注册 API，最后由 `src/index.ts:174-268` 拼成 `allTools`。

**中间表示**：无几何 IR，但有两层参数对象：工具的 zod schema → 适配器的 `ExtrusionParameters`/`LoftParameters`/`SweepParameters`/`RevolveParameters`（`src/adapters/types.ts`）。状态靠「当前模型」单例 + 选择集。

**生成**：**VBA 宏文本生成器**是一等公民——`src/adapters/macro-generator.ts` 把参数翻成 VBA（毫米→米、角度→弧度、end condition 常量映射），`src/tools/vba-*.ts` 五个模块出 28 个 `vba_*` 工具（多数只**返回文本**，不执行）。

**编排**：无。一次工具调用一个 `handler`；`index.ts` 另挂 5 个内联工具（`macro_start_recording`/`macro_stop_recording`/`macro_export_vba`/`design_table_create`/`design_table_refresh`）与 1 个条件工具（`pdm_configure`，取决于 `config.enablePDM`）。

**执行**：winax 直连 `new winax.Object('SldWorks.Application')`（`src/adapters/winax-adapter.ts:61-64`）。★关键设计：**参数复杂度触发宏回退**——`requiresMacroFallback()` 检查 `draftWhileExtruding/offsetDistance/offsetReverse/translateSurface/flipSideToCut/startCondition/endCondition/thinFeature/thinThickness` 任一出现就改走宏（`winax-adapter.ts` 的 `requiresMacroFallback`）。`RunMacro2` 单独封装在 `src/solidworks/run-macro2.ts`。

**验证**：**没有几何门**。工具 handler 把异常转成字符串（`return \`Failed to open model: ${error}\``），成功也只回一句人话或对象；`analysis` 的 6 个工具读回数字但不做断言。全仓无「建完回读几何再判成败」的路径。（来源：本卡 §8 证据清单）

**交付**：`export_file`/`export_with_options`/`batch_export`/`capture_screenshot`（`src/tools/export.ts`）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 工具清单与粒度：**96 个声明 / 86 个真注册（实测），无 `operation` 分派**（来源：本卡 §8 证据清单）

★ 起点数字「103 个工具 / 7 个测试 0 live」来自本仓 `AGENTS.md` §四 台账。**实测：103 在克隆里找不到任何对应口径**——声明 96（对 `src/tools/*.ts` 里 `name: '<tool>'` 逐个计数：native-macro 8、sketch 17、modeling 7、analysis 6、template-manager 6、drawing 5、vba 5、vba-advanced 5、vba-drawing 5、vba-part 5、export 4、vba-assembly 4、vba-file-management 4、drawing-analysis 8、enhanced-drawing 3、macro-security 2、diagnostics 1、extrusion-helper 1）；**默认真注册 86**（`index.ts:174-268` 只 spread 了 modeling/drawing/sketch/export/vba/analysis/template-manager/native-macro 八组 = 81 个，加 5 个内联；`pdm_configure` 由 `enablePDM` 门控，默认 `false`，`index.ts:62`、`:82`，故最多 87）。★注意 `AGENTS.md` §四 该行域计数合计 **89**，更接近它自己 `SWChecklist.md:4` 的「88 个工具」（Node 时代快照），与本卡实测的 96/86 都不是一回事。

**五个模块从未被 `index.ts` import**（15 个工具在服务里根本不存在）：`drawing-analysis.ts`(8)、`enhanced-drawing.ts`(3)、`macro-security.ts`(2)、`diagnostics.ts`(1)、`extrusion-helper.ts`(1)。更糟的是 `src/tools/__tests__/tool-schemas.test.ts` **把这五个死模块全 import 进来逐个校验 schema**——测试绿，工具不可达，属「测试给了假信心」的典型。

**粒度**：比 `Eduardof0nt` 粗、比 `andrewbartels1` 细。草图 17 个原子工具，零件只有 `create_extrusion` 一个（旋/放样/扫掠只在适配器接口与 VBA 生成器里存在，没有对应工具）；`vba_*` 28 个里大多是「生成一段 VBA 文本」，不是可执行能力。（来源：本卡 §8 证据清单）

### 3.2 桥接方式与单实例互斥

**桥接**：进程内 COM（winax 原生 addon）＋以 `.swp` 宏为第二通道（`RunMacro2`）。无外部 exe、无插件、无 IPC。

**单实例互斥：没有**——全仓 `mutex/singleInstance` 零命中。相反它做了 `ConnectionPoolAdapter`（「parallel operations / load balancing / 连接复用」，`src/adapters/connection-pool.ts:1-14`）、`circuit-breaker.ts`、`edge-adapter.ts`（Edge.js 通道）。在「一个 SolidWorks 会话一个 COM apartment」的前提下，**连接池是反模式**：并行调用只会争抢同一个 STA 消息队列。

**可迁移的四件机制**：

1. **`RunMacro2` 的 OUT 参数类型**（`src/solidworks/run-macro2.ts:1-17`）：第 5 个参数 `OUT Error As Long` 在 SW 2024+ 是**必填且必须 byref**——传字面量 `0` 报 type mismatch、省略报 non-optional；winax 要用 `'pint32'`（= `VT_BYREF|VT_I4`）而**不是 `'plong'`**（winax 把 `long` 映射成 8 字节 `VT_I8`）。这是四家里对这条坑写得最清楚的一处，对我们是直接可用的知识（pywin32 等价 `VARIANT(VT_BYREF|VT_I4, 0)`）。
2. **「复杂参数走宏」的失败复盘**：`createExtrusionViaMacro` 的注释写明——**纯文本写 `.swp` 永远跑不起来**，因为 SolidWorks 要求 `.swp` 是 OLE 复合文档（issue #25），所以最终改成**直接调 `FeatureExtrusion3` 全参数**（`winax-adapter.ts` 该方法注释）。⇒ 「参数多就生成宏」这条路在我们这边也别走，除非用 SolidWorks 自己产的 `.swp`。
3. **MCP schema 的致命细节**（`src/tools/__tests__/tool-schemas.test.ts:1-12`）：`z.array(z.any())` 经 `zod-to-json-schema` 会产出**没有 `items` 的 `{"type":"array"}`**，严格客户端（Copilot 等）**直接拒绝整个 server**；改 `z.array(z.unknown())` 得到合法的 `items: {}`。我们做 schema 时必须有一条同样的负例测试。
4. **版本/环境探测**（`src/utils/environment.ts`、`solidworks-config.ts`，配 22+15 个单测）：把 SolidWorks 安装路径、版本、COM 可用性做成可测函数——比在业务代码里散落 `if version` 好。

### 3.3 覆盖域（实测按工具名归类；★「仅文本」= 只生成 VBA 文本、不执行）

| 域 | 有/无 | 说明与代表工具 |
|---|---|---|
| 会话 | 有 | `open_model` `create_part` `close_model` `rebuild_model` |
| 参考 | **无** | 仅 `vba_create_reference_geometry`（仅文本）；无 COM 建平面/轴的工具 |
| 草图 | 有 | 17 个：`create_sketch` `sketch_line` `sketch_arc` `add_sketch_constraint` `sketch_offset` `sketch_mirror` |（来源：本卡 §8 证据清单）
| 尺寸 | 有 | `get_dimension` `set_dimension` `add_sketch_dimension` `add_dimensions`（工程图） |
| 零件 | 有（薄） | COM 只有 `create_extrusion`；`vba_advanced_features`/`vba_pattern_features` 仅文本 |
| 曲面 | **无** | 仅 `vba_surface_modeling`（仅文本） |
| 钣金 | **无** | 仅 `vba_sheet_metal`（仅文本） |
| 焊件 | **无** | —— |
| 模具 | **无** | —— |
| 装配 | **无** | COM 无 `create_assembly`/`add_mate`；仅 4 个 `vba_assembly_*`（仅文本） |（来源：本卡 §8 证据清单）
| 工程图 | 有 | `create_drawing_from_model` `add_drawing_view` `add_section_view` `update_sheet_format` + 6 个模板管理 + 5 个 `vba_drawing_*` |（来源：本卡 §8 证据清单）
| 检查 | 有 | `get_mass_properties` `check_interference` `measure_distance` `analyze_draft` `check_geometry` `get_bounding_box` |
| 仿真 | **无** | 仅 `vba_simulation_setup`（仅文本） |
| 外观 | 有（弱） | 仅 `capture_screenshot`；`set_view_grayscale_enhanced` 在未注册模块里 |
| 宏 | 有（强） | `native-macro` 8（含原生宏录制/暂停/批量）+ `vba` 5 + 3 个内联录制工具 |（来源：本卡 §8 证据清单）
| 高级 | 有（部分） | 6 个模板管理 + 2 个 design table；配置仅 `vba_configurations`（仅文本） |（来源：本卡 §8 证据清单）

**7/16 域有真 COM 能力，其中 2 个是「薄/弱」**（会话、草图、尺寸、零件（薄）、工程图、检查、外观（弱）），其余多为「生成 VBA 文本」——**覆盖矩阵若按工具名数就会严重虚高**，这是本卡最该记住的一条。（来源：本卡 §8 证据清单）

### 3.4 文档内自相矛盾（一家两份说法）

- `README.md:13`：**most tools have not been validated against a live SolidWorks instance**（诚实负声明，唯一一处可信证据）。
- `docs/VERSION_COMPATIBILITY.md:9-14`：SW 2021–2025 全标 `✅ Full / ✅ Yes / ✅ Yes`，`2024` 注为「Primary test version」——与上一句直接冲突，且无任何测试/报告支撑。
- `docs/ADAPTER_ARCHITECTURE.md:5`：「all 88 existing tools」——又一个历史数字。

## 4. 运行条件与依赖

- Windows 10/11 + **Node.js ≥20**（`package.json` engines）+ 真机 SolidWorks 2021–2025（`README.md:26`）。
- `winax` 是 **optionalDependency**（`package.json`），必须在目标机本地编译（README 明写「global npm install 不工作」）。
- 依赖偏重：`@modelcontextprotocol/sdk`、`zod` + `zod-to-json-schema`、`handlebars`（VBA 模板）、`winston`、`chromadb`（知识库）、`mssql` + `pg`（design table/PDM 数据源）、`dotenv`。
- 测试：`vitest`（`npm test`）；`npm run test:integration` 指向 `vitest.integration.config.ts`——**该文件不存在**（见 §5）。

## 5. 失败模式与已知坑

1. **集成测试命令是坏的**：`package.json:22` `"test:integration": "USE_MOCK_SOLIDWORKS=false vitest run --config vitest.integration.config.ts"`，而仓内无 `vitest.integration.config.ts`（`Get-ChildItem` 只找到 `biome.json`/`tsconfig.json`）⇒ 唯一的「真机测试入口」一跑就报找不到配置。
2. **测试规模与覆盖不匹配**：7 个测试文件（`index.test.ts` 13 例、`version.test.ts` 2、`solidworks/api.test.ts` 5、`solidworks/run-macro2.test.ts` 5、`tools/__tests__/tool-schemas.test.ts` 1、`utils/__tests__/environment.test.ts` 22、`solidworks-config.test.ts` 15 = 63 例，本卡实测），**0 个真实 COM 测试**；`README.md:13` 与 `TESTING.md:5-13` 都自认「mock 通过 ≠ 真机可用」。
3. **15 个工具不可达**（§3.1）：声明数 96 与可达数 86 之间有 15 个工具落在 5 个从未被 import 的模块里，客户端看不到也调不到。（来源：本卡 §8 证据清单）
4. **`AGENTS.md` 台账数字对不上**（103 vs 96/86/89/88）：说明外部台账的口径没跟代码同步——凡引用必须回源。
5. **VBA 宏通道的历史坑**（`.swp` 必须是 OLE 复合文档，`winax-adapter.ts` 注释 + issue #25）：决定了「生成宏」路线在它这里已被放弃；但 `native-macro.ts` 仍在跑 `RunMacro2`，说明「跑已有宏」可用、「写新宏文本」不可用。
6. **文档三层数字不一致**（README 无数字、ADAPTER_ARCHITECTURE 88、VERSION_COMPATIBILITY 全绿）。
7. **连接池与单实例冲突**（§3.2）。

## 6. 对我方目标的可用处（机制层面）

**能学**：
- **`RunMacro2` 的 byref 类型规则**（§3.2-1）：一条就能省掉我们一轮真机试错；写法比我们现有材料更精确（`pint32` vs `plong` 的 4 字节/8 字节差别）。
- **「别用纯文本写 `.swp`」的结论**（§3.2-2）：把一条死路预先标出来，避免我们重走「生成宏 → RunMacro2」。
- **MCP schema 负例**（`z.array(z.any())` 让整个 server 被拒）：成本极低、收益极高，应进我们的工具 schema 门禁。
- **工具对象的纯数据形态**（`{name, description, inputSchema, handler}` 数组）：没有装饰器魔法，工具表可以被程序化遍历/校验——与我们「清单形状门禁」契合。
- **README 的诚实负声明**（`README.md:13`）：「架构就绪但多数工具未验证」这种话，是证据等级的正面样板；比 `Eduardof0nt` 的「Verified on 2024」可信得多。

**不能学**：
- **「工具多但零测试」的变体**：96 声明 / 86 可达 / 0 真机测试，且 15 个死工具连注册都没注册——工具数与能力数必须分开报（我们的覆盖矩阵要按「有 COM 实现」计，不按名字计）。（来源：本卡 §8 证据清单）
- **把能力写成 VBA 生成器充数**：`vba_sheet_metal`、`vba_surface_modeling`、`vba_simulation_setup` 会让人以为覆盖了钣金/曲面/仿真；实际只是发一段文本。
- **连接池/熔断/负载均衡**：与单 COM 会话的物理约束相反，属于把 Web 服务范式硬套 CAD。
- **文档多层各自维护数字**：没有单一权威计数源（对比 `andrewbartels1` 至少有 AST 门禁）。
- **重型数据依赖**（mssql/pg/chromadb）绑进 MCP 主体：我们要的是「能建出规范参数化模型」，不是套一件企业数据平台。

## 7. 许可与红线

MIT（`LICENSE:1-3`，`Copyright (c) 2025 ESPO Corporation`）：可读/改/商用，义务是保留版权声明与许可全文；无 NOTICE 义务。★与 `andrewbartels1` 同版权人，**同一机制别两头各记一次来源权重**。★红线：它仓内的 `SWChecklist.md` 是 76 工具时代的 Node 快照（`:1-8` 自述历史文档），其中的「All Fixed and Operational」不能当当前证据引用。

## 8. 证据清单

- `C:\swprojects\SolidworksMCP-TS\src\index.ts:174-268`（`allTools` 拼装：8 组 spread + 5 内联 + 1 条件 PDM）· `:270-278`（`ListToolsRequestSchema` 只回 `allTools`）
- 计数：`src/tools/*.ts` 逐文件 `^\s+name:\s*'` ⇒ 96；按 `index.ts` import 的模块求和 ⇒ 81，加 5 内联（`index.ts:185,197,206,218,232`）= 86；`pdm_configure`（`:252`）默认关，最多 87
- 未注册模块：`src/tools/drawing-analysis.ts`(8)、`enhanced-drawing.ts`(3)、`macro-security.ts`(2)、`diagnostics.ts`(1)、`extrusion-helper.ts`(1)——`index.ts:44-52` 的 import 列表里均无
- `C:\swprojects\SolidworksMCP-TS\src\solidworks\run-macro2.ts:1-17`（byref `pint32` 规则）· `src/adapters/winax-adapter.ts:61-64`（winax 连接）· 同文件 `requiresMacroFallback`（9 个复杂参数清单）
- `C:\swprojects\SolidworksMCP-TS\src\tools\__tests__\tool-schemas.test.ts:1-12`（`z.array(z.any())` → 缺 `items` → 整 server 被拒）
- `C:\swprojects\SolidworksMCP-TS\README.md:11-13`（Alpha + 未验证声明）· `:26`（SW 2021-2025）· `docs/VERSION_COMPATIBILITY.md:9-14`（全绿矛盾）· `docs/ADAPTER_ARCHITECTURE.md:5`（88）
- `C:\swprojects\SolidworksMCP-TS\package.json:22`（坏掉的 `test:integration`）· `src/adapters/connection-pool.ts:1-14`（并行池）
- `C:\swprojects\SolidworksMCP-TS\TESTING.md:5-13`（自认测试不足）
- `gh api repos/vespo92/SolidworksMCP-TS`（2026-10-24 取：stars/pushed_at/language/size）

## 9. 未确认事项

1. 起点数字「103」的来源口径——**查不到**：96（声明）/86（可达）/89（`AGENTS.md` 域合计）/88（历史清单）没有一个等于 103。
2. 86 个已注册工具里有多少在真机跑通过——**查不到**任何运行记录；README 明说多数未验证。（来源：本卡 §8 证据清单）
3. `NativeMacroTools` 的 8 个工具（含 `create_initialized_macro`）在 SW 2024+ 是否真能生成可运行的 `.swp`——只读了注释（`run-macro2.ts` 的修复提交说明），未验证。
4. `pdm_configure` 默认不注册（`enablePDM` 默认 `false`，需 `ENABLE_PDM=true`，`index.ts:62,82`）⇒ 「86」是默认值、「87」是最大值的口径已确认；但未实测启动日志里的实际条数。
