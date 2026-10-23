# freecad-ai（ghbalf/freecad-ai）

<!-- survey: class=H; repr=feature-tree; orchestration=loop; verify=numeric; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | https://github.com/ghbalf/freecad-ai |
| 许可 | **LGPL-2.1-or-later ⇒ 只读思想**（`LICENSE-CODE:1-2` 是 GNU LGPL v2.1 全文；`package.xml:8` 写 `<license file="LICENSE-CODE">LGPL-2.1-or-later</license>`。图标单独 `CC0-1.0`，`package.xml:9`）。**不许抄代码、不许抄文本**，只能借机制 |
| 元数据 | stars 586 · forks 95 · open issues 2 · 最近推送 2026-10-16T18:34:25Z · 语言 Python · 默认分支 `master` · 版本 `0.33.0-alpha`（来源：`gh api repos/ghbalf/freecad-ai` 与 `package.xml:5`，2026-10-24 取）|
| 克隆 | `D:\ai3d-survey\repos\ghbalf__freecad-ai`（shallow：`git rev-list --count HEAD` 得 1，tip `08d637d1`，提交时间 2026-10-16 20:34:21 +0200；体积 5.8 MB，来源：`Get-ChildItem -Recurse -File | Measure-Object Length -Sum` 实测 2026-10-24）|
| 证据等级 | **读码**（非「实测」：本机无 FreeCAD——`Get-Command freecadcmd`/`freecad` 均空，实测 2026-10-24；仓内测试需 FreeCAD AppImage 才能跑集成项，`pyproject.toml:9-10` 的 `addopts = "-m 'not integration'"` 就是为此）|

## 1. 一句话定位

**装在 FreeCAD 里的 AI 工作台，走「受限操作集」路线**：给模型的不是自由写代码的自由，而是一张**结构化操作表**（本文数到 56 个 `ALL_TOOLS` + 1 个 FEM + 4 个参数表工具，共 61 个注册项），每个操作带显式类型参数；只有操作表覆盖不到时才回落到 `execute_code`（提示词里明写它是「last resort」，`freecad_ai/core/system_prompt.py:89`）。几何正确性用**声明式的数值校验清单**验，不用「有没有报错」验（`freecad_ai/extensions/skill_validator.py`）。

`class=H`（FreeCAD GUI/API 代理）；`repr=feature-tree`——所有建模工具都往 PartDesign 的特征树里追加特征，提示词专门要求「保参数历史、别用 Part 布尔把历史压平」（`system_prompt.py:85`）。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：面板里的自然语言；系统提示由 6 段拼成——身份 / Plan-or-Act 模式 / FreeCAD API 参考 / 代码约定 / 当前文档上下文 / `AGENTS.md`（`freecad_ai/core/system_prompt.py:1-12`）。

**中间表示**：**特征树 + 参数**。工具全部作用于 `PartDesign::Body` 里的现有特征或新建特征，`create_primitive` 会自动建 Body、`operation="subtractive"` 表示切成切除（`system_prompt.py:52`）；参数既可以是字面值，也可以写成**表达式**（`set_expression`，`freecad_ai/tools/freecad_tools.py:3429`），并可放进 VarSet / 电子表格（`create_variable_set`/`create_spreadsheet`，`freecad_tools.py:3271,3344`）。

**生成**：模型选一个工具 + 填参数，**不是**写几何代码；`create_sketch(support=…, face=…)` 这种「把草图贴到选中面上」的操作由工具负责 AttachmentSupport/MapMode 与平面性校验（`system_prompt.py:54` 明写「do NOT hand-write a macro that sets `AttachmentSupport`/`MapMode`」）。

**编排**：agent 工具循环。轮数上限 `max_tool_turns` 默认 30、`0` 表示无限（`freecad_ai/config.py:604`）；循环退出判据是纯函数 `should_continue_loop`/`resolve_turn_outcome`——被用户打断优先停、输出被截断也停（截断的回包可能带半个工具调用，issue #52）（`freecad_ai/core/loop_control.py:4-25`；`freecad_ai/ui/chat_widget.py:419`）。失败自动重投：`max_retries` 默认 3（`config.py:601`），每次把 stderr + **一张视口截图**一起回灌给模型（`chat_widget.py:2858-2887`）。

**执行**：四条通道。① 工具在 GUI 主线程跑；② `execute_code` 走「静态扫描 → 子进程沙箱干跑 → undo 事务 → 自动备份」四层（`freecad_ai/core/executor.py:706-711`）；③ `execute_code_headless` 另起 `freecadcmd` 子进程，专门承接会段错误的重活（`executor.py:518-542` 的 `mode="headless"`）；④ `run_macro` 跑 `.FCMacro`。

**验证**：两层数值。① **对象级**：执行后读对象状态，`null shape`/`invalid shape`/`Invalid state` 三类问题上报，**且与执行前的基线做差**——本来坏的对象不记在这次代码头上（`executor.py:244-297`），并把「空草图 / 空 Body / Arch 容器」列入 `null_shape_ok_types` 白名单，避免假阳性（`:282-283`，注释里写这是 issue #18 的教训）。② **几何级**：`VALIDATION.md` 声明式清单，11 种检查（`total_bodies`/`exists`/`bbox`/`bbox_position`/`volume`/`section_area`/`solid_count`/`valid_solid`/`has_holes`/`has_feature`/`min_children`，`freecad_ai/extensions/skill_validator.py:397,414,438,466,495,508,570,583,596,615,630`），带容差与 `when` 条件分支，公式用 `ast` 白名单求值（只放 `sqrt/abs/min/max/pi`，`skill_validator.py:16-40`）。

**交付**：`export_model` 支持 `stl|step|iges`（`freecad_tools.py:3625-3633`）；另有 `capture_viewport`/`set_view` 做视觉旁证（`freecad_tools.py:5234,5308`）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 ★ 操作集怎么划分：**61 个注册工具，6 个类别，按「对象生命周期」切、不按 CAD 命令切**（来源：本卡 §8 证据清单）

`create_default_registry` 注册三批：`ALL_TOOLS`（56 个，`freecad_tools.py:5957-6013`）+ `RUN_FEM_ANALYSIS`（1 个，`fem_tools.py:58`）+ `PARAMETER_TOOLS`（4 个，`parameter_tools.py:496,511,727,743`）= **61 个**（`freecad_ai/tools/setup.py:22-26`）：

| 类别 | 数量 | 成员（`category=` 所在行） |
|---|---|---|
| `modeling` | 35 | 建体/草图/基准（`create_primitive`:211、`create_body`:256、`create_sketch`:869、`create_datum_plane`:1054、`create_datum_line`:1206）、草图编辑与成特征（`edit_sketch`:1503、`pad_sketch`:1613、`pocket_sketch`:1704、`revolve_sketch`:1778、`loft_sketches`:1866、`sweep_sketch`:1945）、对象级（`boolean_operation`:2032、`transform_object`:2125、`duplicate_object`:2212、`delete_object`:2292、`fillet_edges`:2369、`chamfer_edges`:2447、`scale_object`:4534、`section_object`:4622、`linear_pattern`:4696、`polar_pattern`:4768、`shell_object`:4844、`mirror_feature`:4933、`multi_transform`:5113）、参数化（`create_variable_set`:3271、`create_spreadsheet`:3344、`set_expression`:3429、`modify_property`:3559）、**领域封装**（`create_inner_ridge`:4064、`create_snap_tabs`:4189、`create_enclosure_lid`:4309、`create_wedge`:4455）、装配（`create_assembly`:5738、`add_assembly_joint`:5859、`add_part_to_assembly`:5937）|
| `query` | 10 | `measure`:2547、`describe_model`:2671、`list_faces`:2809、`list_edges`:3063、`list_documents`:3137、`switch_document`:3176、`get_document_state`:3209、`undo_history`:3985、`report_skill_params`:5499、`use_skill`:5565 |
| `general` | 6 | `execute_code`:3658、`execute_code_headless`:3736、`run_macro`:3819、`undo`:3896、`redo`:3943、`run_skill_script`:5645 |
| `view` | 3 | `capture_viewport`:5234、`set_view`:5308、`zoom_object`:5361 |
| `file` | 1 | `export_model`:3625 |
| `interactive` | 1 | `select_geometry`:5181（让用户在视口里点）|

划分逻辑有三条**判据**，值得整段借：

1. **「能追加进 Body」优先于「另起对象」**：同一件事有两个工具时，提示词规定用「在 Body 内追加特征」那个，并给出理由——Part 布尔会把原草图/凸台埋掉、让历史不可编辑（`system_prompt.py:85`）。⇒ 操作集的分界不是「功能重复要不要合并」，而是**「哪一种保住参数历史」**。
2. **观测/操作分离且观测给足**：观测面被拆成「列对象」与「列面/列边」两层——`list_faces` 给面名+语义标签（top/bottom/front…）、`list_edges` 给边名+语义标签（top-front horizontal…），提示词直接说这两个工具是给 `shell_object`/`fillet_edges` 选参数用的（`system_prompt.py:69-70`）；选不出来的再由 `select_geometry`（`interactive` 类）请用户在视口里点（`freecad_tools.py:5181`）。
3. **领域封装层压在通用层之上**：`create_enclosure_lid`/`create_snap_tabs`/`create_inner_ridge` 三个工具把「壳体+卡扣」这套多步工序封成一个调用，提示词给出完整的装配序列（外盒 pad → 偏移 H 的 pocket → `create_enclosure_lid` → `transform_object translate_z=H-3` → `create_inner_ridge` → `create_snap_tabs`，`system_prompt.py:91-97`）。⇒ 通用原语之上叠一层**任务级算子**，普通模型只需填 4 个尺寸。
4. **逃逸口只有一个名字、且被降级**：`execute_code`/`execute_code_headless`/`run_macro` 三个都标 `general`，描述里自陈「LAST-RESORT fallback」，并要求每个调用**自包含**（每次新命名空间、变量不跨调用存活，`freecad_tools.py:3659`）。

### 3.2 其它可迁移机制

- **沙箱是「先用真引擎干跑一遍」**：把待执行的代码塞进 harness，开一个 `freecadcmd` 子进程跑（`QT_QPA_PLATFORM=offscreen`），**在工作副本上跑**（`executor.py:740-765` 先 `shutil.copy2` 当前文档）；返回码为负 = 被信号打死，直接判「这段代码会打死 FreeCAD，不安全」（`executor.py:578-585`）。沙箱不可用时不阻断（返回 `(True, "")` 放行，`executor.py:551-553`）——**fail-open**，是明确的取舍不是疏忽。
- **控制台通道单独设闸**：FreeCAD 的 C++ 层把附件失败/重算失败写到 fd 2，**且 warning 与 error 没有严重级前缀**；靠 `App.Console.SetStatus("Console","Wrn",False)` 在源头把 warning 关掉，只让 error 过（`executor.py:342-357`）；如果这步失败，父进程**忽略整条流**而不是瞎猜（`executor.py:598-599` + issue #82 的假阳性教训）。
- **基线差分**：只有「新出现的」坏对象才算这次代码的锅（`executor.py:244-262`）。注释给了真实理由：一个 OCC-invalid 的导入实体每次都出现在副本里，曾让无关代码连错三次、模型一路追幻影 bug。
- **数值校验清单可被 skill 作者声明**：`VALIDATION.md` 有参数段 + 检查段 + `when` 条件段，容差可写 `0.5` 或 `5%`（`docs/specs/2026-03-17-geometry-validation-design.md:36-66`）；这使「同一个 skill 换一种盖子结构」也能验（press-fit vs snap-fit 走不同 `when` 分支）。
- **错误回灌带截图**：重投时把 stderr + 视口快照一起交回去，专治「跑成功了但结果不对」（`chat_widget.py:2879-2887`）。
- **一套工具、两种外壳**：同一注册表既给面板里的 agent 用，也由 `mcp_server_entry.py` 起 FreeCAD 控制台、以 MCP stdio 暴露（`mcp_server_entry.py:1-17`；`freecad_ai/mcp/server.py:100-214` 同时处理新旧两代协议）。

## 4. 运行条件与依赖

- FreeCAD 1.0+（`package.xml:26` 的 `freecadmin`；README 自述测过 1.0.2 与 1.1.0，`README.md:34`），Python ≥ 3.11（`pyproject.toml:5`；`package.xml:27` 又写 `pythonmin 3.10`，**两处不一致**）。
- **零外部依赖**：只用 Python 标准库 `urllib/json/threading/ssl`（`README.md:30`）；24 个 provider 全是 HTTP 直连（`README.md:24`）。
- 安装形态是 FreeCAD 的 Mod 插件（符号链接或复制到 `%APPDATA%\FreeCAD\Mod\`），FreeCAD 1.1+ 起要用版本化目录 `Mod\v1.1\`（`README.md:44-68`）。
- **本机（Windows / Py3.14.7 / RTX 4080S 16GB）跑不了**：没有 FreeCAD 可执行文件（无 `freecadcmd`），而它的一切都跑在 FreeCAD 自带的 Python 里。显存与它无关——没有本地模型，LLM 全在外部 API 或本机 Ollama。（来源：本卡 §8 证据清单）

## 5. 失败模式与已知坑

- **README 自陈 alpha**：「Expect rough edges, breaking changes, and the occasional FreeCAD crash from LLM-generated code」（`README.md:3`）。
- **工具数量文档落后**：`README.md:11` 写「50 structured FreeCAD operations」，代码注册的是 61 个（§3.1）。差 11 个，正好是多出来的 FEM/参数表/装配/领域封装那一批。
- **`VALIDATION.md` 覆盖率极低**：9 个 skill 目录（`create-validation`/`enclosure`/`fastener-hole`/`gear`/`lattice`/`optimize-skill`/`sketch-from-image`/`skill-creator`/`thread-insert`）里**只有 1 个**带 `VALIDATION.md`（`Get-ChildItem skills -Recurse -Filter VALIDATION.md` 实测），即 `skills/enclosure/VALIDATION.md`。⇒ 数值验证这条链在绝大多数 skill 上是空的，设计文档自己也承认「正确性指标从未被填充」（`docs/specs/2026-03-17-geometry-validation-design.md:5-8`）。
- **沙箱 fail-open**：找不到 `freecadcmd` 就直接放行（`executor.py:551-553`），此时四层护栏只剩三层。
- **「跑成功但结果错」是首要失败模式**：数值校验只覆盖 1 个 skill，其余靠 `measure` 回读 + 模型自己判断；这正是 issue #18（空草图被判 null shape）与 #82（warning 被当成 error）那类假阳/假阴的来源（`executor.py:263-283,345-354`）。
- **提示词里塞了大量「别这么做」**：30 条工具路由规则 + 4 段黑名单式告诫（`system_prompt.py:52-81`，逐行数得 30 条以短横线起始的行，实测 2026-10-24；告诫在 `:85,87,89`）——工具越多、提示词越长，这是受限操作集路线的固有成本。作者为此加了 `reranker`（按关键词或小模型把工具表裁到 top-N，`freecad_ai/tools/reranker.py:1-22`）。
- **依赖注入式风险**：`execute_code` 在危险模式下跳过静态检查 + 沙箱 + 超时（只留 undo 与备份，`executor.py:716-718`；`freecad_ai/core/dangerous_mode.py:1-30`）。
- **版本与许可声明分散**：许可在 `LICENSE-CODE` + `package.xml:8`，`pyproject.toml` 里**没有** `license` 字段（`pyproject.toml:1-10` 只有 name/version/description/requires-python 与 pytest 配置）。

## 6. 对我方目标的可用处（机制层面，含边界）

1. **「受限操作集」的划分判据**（§3.1 三条）是本文最该借的东西：**按「哪一种保住参数历史」切分工具**，而不是按 CAD 菜单切。SolidWorks 侧同理——同一个「钻孔」在 Body 内加切除特征 vs 新建布尔体，前者保历史。
2. **任务级算子叠在通用原语上**（`create_enclosure_lid` 这类）：普通模型不需要懂「卡扣怎么建」，只需填 4 个尺寸。这与我方「让普通模型建出规范模型」的目标同构。（来源：本卡 §8 证据清单）
3. **观测工具是操作工具的前置**：`list_faces`/`list_edges` 给语义标签（top/front/…）后再让模型选参数——直接对上我方「实体没有可用名字」（本仓已知事实 32）这个死结：**与其让模型猜名字，不如提供带语义标签的枚举**。
4. **数值校验清单的形态可整段借**：`bbox/volume/section_area/solid_count/valid_solid/has_holes` + 容差 + `when` 分支 + 公式白名单求值，正好是「可验证的参数化模型」的判据模板（实现是 LGPL，只借形态）。
5. **基线差分 + 白名单**（`null_shape_ok_types`）解决了「验证器自己制造假阳性」这个更隐蔽的问题——验证器误报会让模型去修不存在的问题，比不验更糟。
6. **沙箱用真引擎干跑**：比自己写静态规则可靠得多，且能把「会被信号打死」的代码挡在外面。
7. **边界一**：它的验证是**对象级 + 少量几何级**，没有「草图是否完全定义」「配合是否过约束」这类装配级判据；装配工具只有 3 个（§3.1），约束/配合的数值验证完全没有。（来源：本卡 §8 证据清单）
8. **边界二**：交付只有 STL/STEP/IGES 文件，**没有工程图**（无 drawing 工具）。
9. **边界三**：LGPL-2.1 ⇒ **代码一个字都不能进我方仓库**；本文所有内容只能作为机制参考，且不能复制其函数体、注释或文档段落。

## 7. 许可与红线

- **LGPL-2.1-or-later ⇒ 只读思想**（`LICENSE-CODE:1-2` 全文 + `package.xml:8` 声明）。不抄代码、不抄文本、不抄注释。
- 图标 `CC0-1.0`（`LICENSE-ICON:1-3`；`package.xml:9`）——这一项本身无义务，但混在同仓里不改变代码部分的 LGPL。
- 红线：`execute_code`/`run_macro` 在 FreeCAD 进程内执行任意 Python（危险模式还跳过沙箱），任何形态的借用都要保留我方三条护栏（抑制态、超时、收尾释放）。
- 克隆仓库只读，未改动任何文件（未跑测试，故未生成 `__pycache__`）。

## 8. 证据清单

- `LICENSE-CODE:1-2`；`LICENSE-ICON:1-3`；`package.xml:5,8,9,26,27`；`pyproject.toml:1-10`
- `README.md:3,11,24,30,34,44-68`
- `freecad_ai/core/system_prompt.py:1-12,15,20,28,37,52-97`
- `freecad_ai/tools/freecad_tools.py:211,256,869,1054,1206,1503,1613,1704,1778,1866,1945,2032,2125,2212,2292,2369,2447,2547,2671,2809,3063,3211,3271,3344,3429,3559,3625-3633,3658,3670-3673,3736,3819,3896,3943,3985,4064,4189,4309,4455,4534,4622,4696,4768,4844,4933,5113,5181,5234,5308,5361,5499,5565,5645,5738,5859,5937,5957-6013`
- `freecad_ai/tools/setup.py:10-12,22-26`；`freecad_ai/tools/fem_tools.py:58`；`freecad_ai/tools/parameter_tools.py:496,511,727,743,765`
- `freecad_ai/tools/registry.py:29-60,72-118`；`freecad_ai/tools/reranker.py:1-22`
- `freecad_ai/core/executor.py:244-297,342-357,500-542,545-599,699-768`；`freecad_ai/core/loop_control.py:4-25`；`freecad_ai/core/dangerous_mode.py:1-30`
- `freecad_ai/extensions/skill_validator.py:16-40,194-200,397,414,438,466,495,508,570,583,596,615,630,674-684`
- `freecad_ai/ui/chat_widget.py:419,2845-2887`；`freecad_ai/config.py:589-604`
- `freecad_ai/mcp/server.py:100-214`；`mcp_server_entry.py:1-17`
- `docs/specs/2026-03-17-geometry-validation-design.md:5-8,36-66`
- `skills/enclosure/VALIDATION.md`；`Get-ChildItem skills -Recurse -Filter VALIDATION.md` 计数 = 1（2026-10-24）
- https://github.com/ghbalf/freecad-ai（`gh api` 元数据，2026-10-24）

## 9. 未确认事项

1. **没跑过任何工具、没跑过测试**：本机无 FreeCAD，`pyproject.toml:9-10` 又把 integration 标记默认排除，故 61 个工具与 143 个测试文件（`Get-ChildItem tests -Recurse -Filter test_*.py` 计数）的实际通过情况未知。
2. 61 这个数是**静态注册计数**；运行期 `--` 之外还有用户扩展工具与 MCP 工具会动态注册（`setup.py:28-46`），实际 `tools/list` 条数会更多，未验。
3. 11 种校验检查的真实行为（尤其 `section_area` 的 `Shape.slice` 失败会被吞成 `actual_area = 0.0`，`skill_validator.py:553-557`）未实测——这条吞异常可能把「几何复杂」误报成「面积 0」。
4. `pyproject.toml:5` 的 `requires-python >=3.11` 与 `package.xml:27` 的 `pythonmin 3.10` 冲突，以哪个为准未确认。
5. README 的「50 个操作」与代码的 61 个：我数的是注册项，不排除作者口径只算 `modeling`+`query`（45）或只算 `ALL_TOOLS`（56），未能确认他数的是哪一批。（来源：本卡 §8 证据清单）
