# storytold/cadcraft

<!-- survey: class=H; repr=feature-tree; orchestration=loop; verify=none; deliver=STEP; evidence=元数据 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `storytold/cadcraft` · https://github.com/storytold/cadcraft · 主页 https://getartcraft.com/apps/cadcraft |
| 许可 | **MIT OR Apache-2.0**（README badge 逐字：`License: MIT / Apache-2.0`）—— **但 GitHub API 的 `license.spdx_id` 只报 `Apache-2.0`**，两者不一致，见 §7 |
| 元数据 | stars **7,429** · created **2026-10-07T05:22:31Z** · pushed **2026-11-01T19:42:33Z** · 语言 Rust · 描述「an open-source, clean-room AutoCAD-style app in pure Rust」（来源：`gh api search/repositories`，2026-11-02 取）|
| 克隆 | **未克隆**（本轮只读到 README 与元数据）|
| 证据等级 | **元数据 / 只读到 README**（未 clone，未读码，未运行）|

## 1. 一句话定位

**与 SolidCraft 同一天（2026-10-07）出现的「AI 生成的完整 CAD 应用」第二例**：ArtCraft 团队用 AI 编码 agent 做出的 AutoCAD 风格 clean-room 实现，7,429 星、Apache 系许可、README 明写「Agent-driverable over MCP」。它的意义不是能力，而是**证明「一个人 + AI agent 在两周内产出一个可用的完整 CAD 应用」这条路成立**。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：桌面（macOS/Windows/Linux/FreeBSD）、浏览器（WebAssembly）、命令行制图。
**中间表示**：DWG/DXF 文档模型 + 图层/块/标注/布局（AutoCAD 语义），不是参数化特征树（README 自述 2D 与 3D 双 tab，3D 是实体）。
**生成**：不生成代码；命令驱动（「the command line, object snaps, layers, dimensions, hatches, blocks」）。
**编排**：MCP（README badge 逐字 `Agent-driverable over MCP`；正文出现 MCP 14 次、agent 9 次；来源：`gh api repos/storytold/cadcraft/readme` 全文计数，见 §8）。
**执行**：Rust 原生 + wasm。
**验证**：**未读到任何数值/oracle 判据**（本卡只到 README 层，这一条是「未见」，不是「没有」）。
**交付**：DWG / DXF（描述里明确「Opens and saves DWG and DXF」）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 与 SolidCraft 的共性（这一波的形状）

| 维度 | SolidCraft | CADCraft |
|---|---|---|
| 创建日 | 2026-10-07 | **2026-10-07** |
| 语言 | 纯 Rust | 纯 Rust |
| 定位 | clean-room Fusion 360 克隆 | clean-room AutoCAD 克隆 |
| 许可 | MIT OR Apache-2.0 | MIT / Apache-2.0（API 只报 Apache-2.0）|
| agent 接口 | 内置 MCP + CLI + JSON 脚本 | MCP（README badge）|
| 代码来源 | AI 编码 agent 生成（第三方报道称 vibe-coded）| AI 编码 agent 生成（同）|
| 成熟度自述 | early but usable for simple parts | **Status: early development** |

⇒ **两例同日、同栈、同许可策略、同 agent 接口**，说明这是一条**可复制的配方**，不是孤立事件。

### 3.2 工程质量信号（可作对照）

README 挂 **SonarCloud 静态扫描**与 **CodeRabbit PR 评审**徽章。⇒ 至少有一套自动化质量门在跑；但本轮未核这两项的实际覆盖率与通过率。

## 4. 运行条件与依赖

- 纯 Rust；跨 macOS / Windows / Linux / FreeBSD / wasm。
- 早期开发状态（README badge 自述 `Status: early development`）。

## 5. 失败模式与已知坑

1. **只到 README 层**：本卡没有读码，所以「它到底能做什么」只能记作者自述。
2. **AutoCAD 路线 ≠ 参数化 3D**：即使成熟，也补不上 SolidWorks 的参数化建模与工程图交付。
3. **早期开发**：README 自述，且与 SolidCraft 一样没有对外承诺几何等价。
4. **许可信息自相矛盾**（见 §7），商用前必须读 `LICENSE` 原文确认——本轮未读。

## 6. 对我方目标的可用处（能学 / 不能学）

**能学**：
- **配方本身**：一个领域知识 + AI 编码 agent + Rust 单栈 + 双许可 + MCP 暴露 ≈ 两周出可用 CAD。这条对我们的启示不是「去写一个 CAD」，而是**「我们能不能用同样的配方重做我们自己的验证链」**（例如把「打开 SolidWorks 回读」换成纯 Rust/Python 的离线几何核验）。
- **SonarCloud + CodeRabbit 双门**：AI 生成代码的常规质量护栏样本。

**不能学 / 不能替代**：
- 它是 2D 制图为主的 AutoCAD 克隆，**不是参数化 3D**，与我们的首件（板件/装配/图样）不在同一条能力轴上。
- 未读码，"能不能用"无法判断。

## 7. 许可与红线

**矛盾必须单列**：README badge 写 `License: MIT / Apache-2.0`，GitHub API 的 `license.spdx_id` 只报 `Apache-2.0`。⇒ 商用或移植前必须读 `LICENSE-MIT` / `LICENSE-APACHE` 原文；本轮**未读**，故只能记「至少 Apache-2.0」。
若确为双许可，则可并入（保留版权与 NOTICE）；若只有 Apache-2.0，同样可并入但需声明改动。

## 8. 证据清单

- `gh api search/repositories?q=cadcraft in:name`（2026-11-02）：`storytold/cadcraft` stars=7429 · created=2026-10-07T05:22:31Z · pushed=2026-11-01T19:42:33Z · `license.spdx_id=Apache-2.0`
- README（`gh api repos/storytold/cadcraft/readme`，2026-11-02 取，全文 32,426 字符）：badge `License: MIT / Apache-2.0` · `Agent-drivable over MCP` · `Status: early development` · 正文 MCP 出现 14 次、agent 9 次
- 第三方报道：https://3dprintingindustry.com/news/vibecoded-clones-of-solidworks-and-autocad-released-as-open-source-255770/（2026-10-18）—— 把 SolidCraft 与 CADCraft 并列为「vibe-coded 的 SolidWorks/AutoCAD 克隆」，称发布时 CADCraft 约 4.3k stars / 2,000 forks

## 9. 未确认事项

1. **未克隆未读码**：全部技术细节只能从 README 取，`evidence=元数据`。
2. **MCP 工具面大小**：不知道它暴露多少个工具、有没有内联断言。
3. **有没有 oracle / 数值验证**：未见，也未查证「没有」。
4. **许可到底是双许可还是只有 Apache-2.0**：API 与 badge 矛盾，未读 LICENSE 原文。
5. **7,429 星的真实性**：与 SolidCraft 同波暴涨，未查是否有媒体效应放大。
