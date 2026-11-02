# tangency-labs/solidcraft

<!-- survey: class=H; repr=feature-tree; orchestration=loop; verify=numeric; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `tangency-labs/solidcraft` · https://github.com/tangency-labs/solidcraft · 主页 https://solidcraft.io |
| 许可 | **MIT OR Apache-2.0，双许可任选**（`LICENSE-MIT` + `LICENSE-APACHE`；`ROADMAP.md:71-73` 明写「Versions already released stay available under those licences permanently」）⇒ **可直接并入，只需保留版权声明** |
| 元数据 | stars **13,016** · forks **1,701** · created **2026-10-07** · pushed **2026-11-02** · 语言 Rust · 仓库 264,578 KB · open issues 5,120（来源：`gh api repos/tangency-labs/solidcraft`，2026-11-02 取）|
| 克隆 | `D:\swagent-2026Q4\repos\tangency-labs__solidcraft`（HEAD `3ddd737`，2026-11-02T09:08:23Z，`--depth 1`，147.1 MB，clone 46.9 s）|
| 证据等级 | **读码**（未编译未运行：Rust 工具链与 `crates/` 下 734,867 行源码的构建不在本轮范围，计数命令见 §8；来源：本卡 §8 实测行）|

## 1. 一句话定位

**一个纯 Rust 从零写的开源参数化 CAD 应用（桌面 + 浏览器 + headless CLI + MCP 服务端），建库一个月 13,016 星（来源：`gh api repos/tangency-labs/solidcraft`，2026-11-02 取）；它的价值不在于「替代 SolidWorks」，而在于它是本行业唯一把「解析值 oracle + 独立内核交叉 + STEP 回读」做成 90/90 常绿门的开源 CAD，并且 MCP 面只有 21 个工具就覆盖了全部建模能力（来源：`docs/oracle.md:12`；工具数见 §3.1）。**

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：三条并列的入口，走同一套命令引擎——
- 桌面 UI（egui + wgpu）
- headless CLI：`solidcraft-cli run examples/bracket.json --out bracket.step`（命令脚本是 JSON 命令列表）
- **MCP 服务端**：`solidcraft-cli mcp`（stdio / JSON-RPC 2.0，一条消息一行；协议版本 2025-06-18 / 2025-03-26 / 2024-11-05）

**中间表示**：**参数化特征时间线**（feature tree + timeline），不是代码、不是网格。`crates/doc/` 存文档模型，`crates/kernel/` 是几何内核（当前是 truck，计划迁 NVIDIA SMLib，见 `ROADMAP.md:46`）。设计文件 `*.sc` 是容器格式，带格式号（0.22.0 写 format 35，低版本拒绝打开更高版本）。

**生成**：**不生成代码**。agent 调用的是**同一批引擎命令**，README 原话「An agent models exactly like a person does: every tool runs engine commands, the same ones the toolbar, palette, scripts and control channel use, and never opens a dialog」（`docs/mcp.md:3-6`）。

**编排**：`execute`（单命令）与 `batch`（**单次最多 10,000 条命令**，`crates/mcp/src/tools.rs` 的 `MAX_BATCH`）；另有 `undo`/`redo`/`pending`。

**执行**：引擎命令 → 内核。两种会话形态：headless（进程内自建设计会话）与 **bridged**（连到正在运行的 app，`--connect host:port`，能看到 agent 在建模；控制通道默认开在 `127.0.0.1:27878`，带每次启动新生成的 token）。

**验证**（本卡最重要的部分）：
1. **`expect` 内联断言**：`execute` 与 `batch` 都接受 `expect {volume_mm3, tol, bodies, bbox}`，执行完**自动比对**并回 `expectation {ok, measured, expected, mismatch}`；默认容差 `EXPECT_VOLUME_TOL = 0.002`（0.2%）、`EXPECT_BBOX_TOL_MM = 0.05`（`crates/mcp/src/tools.rs:14-16`）。⇒ **判据跟着调用走，不靠事后人工核对。**
2. **参考用例 oracle**：`tests/oracle/` 下 **90 个 case**，`cargo xtask oracle` 重放，比对 body 数、体积、面积（相对容差 1e-3）、质心、包围盒（在零件尺寸的 1e-3 内）、面数，有 `reference.stl` 的再算**采样对称 Hausdorff 距离**与两套三角化的主二阶矩；**每个件还导出 STEP、校验、再读回**（`docs/oracle.md:3`）。当前 **90/90 pass**，来源 69 解析解 + 21 FreeCAD，**0 个已知失败、0 个无期望值的 case**（`docs/oracle.md:12`）。
3. **期望值不来自商业 CAD**：`docs/oracle.md:10` 明写「No expected value comes from a commercial CAD product」；FreeCAD 是被当**外部独立内核**使用的，不是依赖。

**交付**：STEP（AP242，带 body 名/颜色/组件装配；回转面导出为原生 plane/cylinder/cone/sphere/torus）、IGES 5.3、3MF、STL、OBJ、glTF、DXF（当前视图）、URDF。导入 STEP AP203/214/242、IGES、FreeCAD `.FCStd`、Rhino `.3dm`。

## 3. 技术方案要点（可迁移的机制）

### 3.1 MCP 工具面：**21 个**（实测计数：`[regex] '\btool\(\s*"([a-z_]+)"'` 在 `crates/mcp/src/tools.rs` 命中 21 次）

名字全集：`list_commands` `describe_command` `execute` `batch` `inspect_design` `measure` `body_topology` `set_parameter` `check_parameters` `screenshot` `compare_picture` `export` `crash_reports` `running` `pending` `undo` `redo` `new_design` `open` `save` `skill_reference`。

**这是「少工具 + 万能代码口」路线的教科书样本**，与我方 **439 个工具**（2026-10-06 台账读数，口径见 `docs/state/INDEX.md`）形成直接对照：
- 建模动作全在 `execute`（单命令）与 `batch`（≤10,000 条，`crates/mcp/src/tools.rs` 的 `MAX_BATCH`）里，具体命令由 `list_commands` / `describe_command` **运行时发现**，不是编译期铺进工具表；
- 一个 `skill_reference` 工具把「怎么用」以文本形式交给 agent，而不是把知识编进工具描述。

### 3.2 参数契约三档：`--param-check off|warn|strict`

`docs/mcp.md:66-84`：命令带类型化参数契约时，`strict` **拒调用且设计保持原样**，`warn` 执行并在结果附 `param_warnings`（例：``unknown key `operaton`; did you mean `operation`?``），默认 `off`。bridged 模式下服务端先问 app「你自己查不查」，避免新 app 的键被旧服务端的契约误拒。⇒ **比「有 schema 就假定正确」强一档，且失败是显式的。**

### 3.3 MCP 注解按「能做什么」分四档

`Effect` 枚举 = `ReadOnly` / `Edits`（可撤销的改）/ `Replaces`（替换设计，未保存改动丢失）/ `Files`（可读写删磁盘文件）→ 映射到 MCP 的 `readOnlyHint` / `destructiveHint` / `idempotentHint` / `openWorldHint`。注释写明动机：「Clients that auto-approve on these hints must not be told less than the truth (#205)」（`crates/mcp/src/tools.rs`）。⇒ **这是把「工具危险性」变成机器可读契约的做法，不是文档里写一句「注意」。**

### 3.4 文件访问边界（`docs/mcp.md:86-135`）

只允许：打开设计的所在目录（且必须在用户主目录内、非隐藏）、本会话内打开/保存过的目录（最多 16 个）、恢复目录、服务端自己的私有临时目录、显式 `--allow-path`。**路径先规范化再比较**，`..` 与越界符号链接被拒；Windows 上拒绝 UNC / 设备路径 / 备用数据流 / 保留设备名 / 8.3 短名。⇒ 与「agent 能跑任意代码」的路线相比，这是**把攻击面写进工具契约**。

### 3.5 持久命名（本仓最想要的机制）

`ROADMAP.md:19`：「**Faces and edges keep their names through edits, so references survive changes**」。代码里 `crates/doc/src/face_anchor.rs` 与 `crates/doc/src/construct.rs` 等承载。⇒ 直接对应 **SolidPilot 自述仍是 make-or-break 而未解决的同一问题**（本仓 `docs/sources.md:63` 记 SolidPilot「持久引用解析器」是其 ahead 模块）。区别是：**SolidCraft 声称已经做成并作为日常工作特性发布，SolidPilot 仍列为未完成。**

### 3.6 验证方法论的三个可搬点（比代码更重要）

1. **解析闭式解做期望值**：`tools/oracle-analytic/` 用 Pappus/Green/Steiner 等算体积、面积、质心、矩；90 个 case 里 69 个用解析解（`docs/oracle.md:12`）。
2. **独立内核交叉**：21 个 case 用 FreeCAD（OpenCASCADE）当**外部程序**跑同一份 `recipe.json`，只比体积与面积（形状允许不同处明说）；报告里逐件给出 **Hausdorff 距离 max/mean**（最好 0.033 mm，最差 0.007–0.033 mm 量级）。
3. **交付物回读**：每个件导出 STEP 再读回校验 —— **不是只信内存里的数**。

### 3.7 诚实的失败面

`docs/capabilities.md:5-9` 自述「**Status: early but usable for simple parts**」，并紧接一句「These checks do not establish complete geometric or workflow equivalence」；`docs/oracle.md:14` 主动记下「Case 95 的解析质心参考在成功跑之后被更正，其旧 pass 状态属历史，需重放」——**自己记自己的账不平**。

## 4. 运行条件与依赖

- **纯 Rust**（`Cargo.toml` + `rustfmt.toml` + `clippy.toml` + `deny.toml`）；1509 个 `.rs`、**734,867 行**（`Get-ChildItem crates -Recurse -Filter *.rs` 后 `Measure-Object -Line`）。
- 桌面：egui + wgpu；浏览器：wasm32（`cargo xtask ci` 含 wasm 构建）。
- 预编译包：Windows MSI、macOS DMG（Developer ID 签名 + 公证）、Linux AppImage/Snap/deb/rpm/Flatpak、浏览器版。
- 无商业 CAD 依赖；FreeCAD 只在测试里当外部 oracle。
- 版本节奏：**每日发版**（v0.22.x + nightly），格式号递增，旧版打不开新版文件。

## 5. 失败模式与已知坑

1. **工程图基本没有**：`ROADMAP.md:38` — Drawings 里程碑 **3/21**（2 个进发布、1 个在 `drawings` 分支），今天只有「导出当前视图为 DXF」。⇒ **对中国机械设计的交付（GB 图样）来说，这条是硬缺口。**
2. **无 CAM**：`ROADMAP.md:51` — Manufacturing 里程碑「1 pieces tracked, none done」。
3. **曲面 6/14**：`ROADMAP.md:50`。
4. **SolidWorks 文件导入仍未做**：`ROADMAP.md:43` — Import & export 里程碑 7/39，其中「FreeCAD, **SolidWorks** and point-cloud import」属未完成项。⇒ **它不能读 .SLDPRT，也不能驱动 SolidWorks。**
5. **内核正在换**：truck → NVIDIA SMLib（usd-brep, Apache-2.0），在 `kernel-smlib` 分支，未进发布（`ROADMAP.md:46`），意味着几何底层仍有迁移风险。
6. **体量对贡献者不友好**：`crates/` 下 734,867 行源码、5,120 个 open issue（来源：`gh api repos/tangency-labs/solidcraft`，2026-11-02；行数命令见 §8）。
7. **「早期但可用」是它自己的定性**：简单零件可用，不是全功能 CAD。

## 6. 对我方目标的可用处（能学 / 不能学）

**能学（机制，按价值排序）**：

1. **★★★ `expect` 内联断言**：工具调用自带期望体积/包围盒/体数，执行完自动比对并回 `mismatch`。这直接解我们的「回读验证」——现在我们是「建完再单独查一次」，它是「判据跟着动作走」。**可直接移植概念：给 `part_extrude` 这类工具加可选 `expect_volume_mm3` / `expect_bbox_mm` 参数。**
2. **★★★ oracle 三段式**：解析闭式解 + 独立内核交叉 + 交付物回读。我们 `E1–E7` 的采集器/判定器分离正是缺这一层；它的 90 个 case 是**可照抄的结构**（每 case 一个 `recipe.json` + 一个 `expected.json` + 可选 `reference.stl`）。
3. **★★★ 21 工具 + `execute`/`batch` + `list_commands`/`describe_command` 运行时发现**：这是「439 个工具」的直接解药（21 见 `crates/mcp/src/tools.rs` 实测；439 见 `docs/state/INDEX.md` 口径）。我们已知的痛点是「零依赖 BM25 在 433 个工具上前 5 命中率仅 40%」（来源：Hindsight 记忆记录的本仓实测，本轮未复核），而它的答案是**不给模型看工具表，给模型看命令表**。
4. **★★ 参数契约 `strict` 档**：拒调用且设计不变。我们的工具层现在遇到坏参数多半是 COM 报错或静默忽略。
5. **★★ `Effect` 四档 → MCP annotations**：把危险性变成机器可读，客户端能据此审批。
6. **★ 文件访问白名单 + 路径规范化**：我们让 agent 直接跑 Python，攻击面比它大。
7. **★ 持久命名的存在性证据**：它说「面/边跨编辑保名」已工作 —— 证明这件事**在纯软件参数化 CAD 里做得成**，可作为我们评估 SolidWorks 持久引用方案时的对照基线。

**不能学 / 不能替代**：
- **它不能驱动 SolidWorks**（无 COM、无 .SLDPRT 读写）。所以对「让 Agent 在 SolidWorks 里建模」这个原题，它**不是解**，是**另一条路的实证**。
- **工程图/CAM/曲面/焊件/模具/仿真**都缺，覆盖不了中国机械设计的交付面。
- **它的日更节奏与 5,120 个 open issue** 不适合我们当底座再维护（来源：`gh api repos/tangency-labs/solidcraft`，2026-11-02 取）。

## 7. 许可与红线

**MIT OR Apache-2.0 双许可（任选）**。MIT 只需保留版权与许可声明；Apache-2.0 需保留 NOTICE 并声明改动。⇒ **这是我们本轮见到的最宽松的大体量 CAD 代码库**，代码与文档都能并入，不像 SolidPilot（AGPL）只能读思想。
`NOTICE` 里明确其独立性与商标归属（不隶属 Autodesk/Dassault/PTC/Siemens）。

## 8. 证据清单

- `docs/oracle.md:3`（oracle 比对项与容差）· `:10`（期望值不来自商业 CAD）· `:12`（90/90 pass，69 analytic + 21 freecad）· `:14`（Case 95 自记待重放）
- `docs/capabilities.md:5-9`（75/76 自述 + 明确「这些检查不建立完全等价」）
- `docs/mcp.md:3-6`（agent 与人是同一套引擎命令、从不弹框）· `:66-84`（`--param-check off|warn|strict`）· `:86-135`（文件访问白名单与路径规范化）
- `crates/mcp/src/tools.rs`（`MAX_BATCH = 10_000`；`EXPECT_VOLUME_TOL = 0.002`；`EXPECT_BBOX_TOL_MM = 0.05`；`Effect` 四档枚举；`tool()` 注册函数）
- `ROADMAP.md:19`（持久命名）· `:38`（Drawings 3/21）· `:43`（Import & export 7/39，SolidWorks 导入未完成）· `:46`（内核迁 SMLib）· `:50`（Surfacing 6/14）· `:51`（CAM 0 完成）· `:71-73`（MIT OR Apache-2.0 永久）
- `README.md`（"75 of 76 public reference parts match…"；内置 MCP）
- 实测命令（2026-11-02）：`gh api repos/tangency-labs/solidcraft`（stars/forks/created/pushed/license）· `git clone --depth 1`（46.9 s / 147.1 MB）· `Get-ChildItem crates -Recurse -Filter *.rs` → 1509 files、734867 lines · `[regex]'\btool\(\s*"([a-z_]+)"'` on `crates/mcp/src/tools.rs` → 21 · `(Get-ChildItem tests\oracle -Directory).Count` → 90 · `(Get-ChildItem skills -Recurse -Filter SKILL.md).Count` → 17

## 9. 未确认事项

1. **未编译未运行**：Rust 工具链未在本机跑过，`cargo xtask oracle` 的 90/90 是**它 CI 的宣称**，本轮未复现。
2. **持久命名的实际强度未验**：README/ROADMAP 说「面与边跨编辑保名」，但**没读 `face_anchor.rs` 的实现**，也未做「改参数后旧引用是否仍指向同一面」的实验 ⇒ 只能记【宣称】。
3. **MCP 21 个工具是编译期静态注册数**，`list_commands` 在运行时能列出多少条引擎命令**未数**（`docs/features.md` 有全表但未逐条统计）。
4. **bridged 模式的 token/端口细节**只读到文档层，未实测。
5. **它与 SolidWorks 的几何等价性**完全没有证据 —— 也没人做过；这是「换底座」路线的根本未知。
6. **13,016 星的一个月增长**是否含刷星/媒体效应，未查（Trendshift 徽章显示上过榜，但未核实来源）。
