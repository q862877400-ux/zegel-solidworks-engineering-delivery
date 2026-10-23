# Autodesk Fusion 的 Autodesk Assistant

<!-- survey: class=H; repr=feature-tree; orchestration=human-approve; verify=visual; deliver=none; evidence=元数据 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | 闭源，无源码（Fusion 内的内置面板）。产品帮助 https://help.autodesk.com/view/fusion360/ENU/?guid=LEARNINGPANEL ；官方 FAQ https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Autodesk-Assistant-in-Fusion-FAQ.html |
| 许可 | 商业闭源 · **订阅内置**，另按「代理动作」计量。官方 FAQ：「starting October 13th 2026, every Fusion subscription includes a per-seat monthly quota of Monthly Flex Tokens (Beta)」，用尽后需购 Flex tokens（来源：https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Autodesk-Assistant-in-Fusion-FAQ.html ） |
| 元数据 | Autodesk（Fusion，原 Fusion 360）· https://www.autodesk.com/products/fusion-360 · 取数 2026-10-24（来源：https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Autodesk-Assistant-in-Fusion-FAQ.html ） |
| 克隆 | 未克隆（闭源，无仓库） |
| 证据等级 | **元数据**（官方 FAQ 正文 + 官方帮助页；无源码、无本地实测——需 Fusion 订阅与 Autodesk 账号） |

## 1. 一句话定位

**把「一个会点界面、会按按钮的实习生」装进 Fusion 右侧面板**：它能把自然语言翻成 Fusion 自己的命令（草图、拉伸、圆角、倒角、孔、基本体，以及 CAM 的 setup/toolpath），但**每次动作前先把计划摊给你看、你批准了才执行**，且执行完必须你自己在视口里看一眼（来源：https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Autodesk-Assistant-in-Fusion-FAQ.html ）。

- **AI 落在哪一段工序**：**草图（只建轮廓）+ 特征 + CAM 的 setup/toolpath + 渲染与项目协作**。官方原文明列它能做：「Creating sketches (but not sketch dimensions or constraints) / Extruding profiles / Adding features (fillets, chamfers, holes) / Creating primitives (boxes, cylinders, etc.) / Performing basic modeling operations」（同上）。
- **装配是残的**：「AA has limited capabilities in Assembly mode. Modeling create/update/delete operations may not work reliably.」（同上）
- **仿真/工程图**：官方 FAQ 的 Design & Modeling、Manufacturing、Rendering 三节里**没有**仿真求解、没有工程图出图；只有「Manufacturing guidance」与生成 toolpath（同上）。仿真与图纸**查不到**任何能力声明。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

1. **输入**：面板里的自然语言 + 当前打开的「design, workspace, setup, study, or project」上下文；官方给的最佳实践要求点名 Browser 里的**精确名字**（组件、草图、实体、setup、study、参数）（来源：https://help.autodesk.com/view/fusion360/ENU/?guid=LEARNINGPANEL ）。
2. **中间表示**：**Fusion 自己的特征/命令序列**（不是外来 DSL，也不是网格）。官方原话：「Autodesk Assistant can generate native, editable 3D CAD geometry inside Fusion, not static meshes. The generated geometry behaves like standard Fusion design data and can be edited using normal modeling tools.」（来源：FAQ 同上）
3. **生成**：底层是 LLM，官方明说「uses large language models」且「The underlying model and configuration may change over time」（同上）。
4. **编排**：官方把代理能力分成一条**四级光谱**——`Show me`（只读检视）/`With me`（带你做，你握着控制权）/`For me`（先准备动作、亮出计划、**你批准后**才跑）；另有制造问题路由到专门的 agent（同上）。
5. **执行**：在 Fusion 内执行原生命令。「AA requires a saved design with proper document context.」（同上）
6. **验证**：**只有人眼**。官方两条硬话：「AA may report success if the tool executed without error — even if the geometry is not what you intended.」与「Always visually inspect the result in the viewport.」（同上）
7. **交付**：无独立文件交付——结果就是 Fusion 文档本身（原生特征）。导出格式不在本功能的范围内（同上，FAQ 未提导出）。

## 3. 技术方案要点（可迁移的机制）

- **四级授权光谱（Show / With / For me）**：把「只读」「共做」「代做」拆成三个显式档位，且每档给一句行为承诺——这比笼统的「AI 帮你建模」可验收得多（来源：https://help.autodesk.com/view/fusion360/ENU/?guid=LEARNINGPANEL ）。
- **「亮计划 → 批准 → 执行」是产品级硬约束**：官方 FAQ 单列一问一答「Does Autodesk Assistant apply changes automatically in Fusion? No. Autodesk Assistant confirms changes before applying them.」（来源：FAQ 同上）
- **上下文靠「名字」而不是「坐标」**：官方最佳实践要求用 Browser 里的精确名字（组件/草图/实体/参数），并警告单位（cm vs inch）（同上）。这是「选择器必须稳定」的产品级承认。
- **错误分级与「成功」的定义分离**：它把「命令跑通」和「几何对不对」明确分开（§2.6 那两句）。这是本卡最该抄的一句话。
- **计量与成本可见**：按「AI assists」计量，且官方承认「Clicking Cancel stops the task, but any AI assists already used up to that point still count toward your usage.」（来源：FAQ 同上）

## 4. 运行条件与依赖

- **宿主**：Fusion 桌面客户端。官方明确排除两处：「Autodesk Assistant is not currently available in the Fusion web client, Fusion Manage, or mobile app.」（来源：https://help.autodesk.com/view/fusion360/ENU/?guid=LEARNINGPANEL ）
- **账号与订阅**：Commercial/Startup、Trial、Educational、Personal 均可问答与动设计；但「Generate AI visualizations」只有 Commercial/Startup 有，且每月含一定额度（同页权限表）；官方另注「Create 20 included AI visualizations per month from your design」（同页脚注，来源同上 URL）。
- **动作能力要开 Tech Preview**：不开启时只能「answers questions, based on information in Autodesk product documentation」；开启后才能查模型/带做/代做（同上）。
- **文档必须先存盘**：未命名/未保存的设计不能动（来源：FAQ 同上）。
- **协作类能力另有前置**：「Requires a collaborative editing (CE) hub」，且建项目要 hub Admin 授权（来源：https://help.autodesk.com/view/fusion360/ENU/?guid=LEARNINGPANEL ）。
- **联网**：FAQ 有「AA keeps switching between offline and online」的排障条目（来源：FAQ 同上）——即在线依赖。
- **数据**：提示与对话历史「may be stored in Autodesk systems for up to 45 days」，模型托管在 Autodesk 云、不拿客户提示训练第三方模型（来源：https://www.autodesk.com.cn/support/technical/article/caas/sfdcarticles/sfdcarticles/CHS/Autodesk-Assistant-Supported-Products-and-How-to-Use-It.html ）。

## 5. 失败模式与已知限制

### 5.1 ★ 官方逐条否认过什么（原文 + 链接）

以下每条都出自 https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Autodesk-Assistant-in-Fusion-FAQ.html （另有出处的另注）：

- **不自动改**：「No. Autodesk Assistant confirms changes before applying them. Autodesk explicitly states that the assistant reviews and confirms actions with the user rather than making silent or automatic changes.」
- **不做端到端全自动**：「No. Autodesk Assistant is not a fully autonomous system that replaces user‑driven design workflows. ... does not automate entire end‑to‑end design processes without user involvement.」
- **不做草图尺寸与约束**：「Creating sketches (but not sketch dimensions or constraints)」——括注就是否认。
- **不做文件级操作**：「No. AA cannot currently perform file‑level operations such as: Open / Close / Save / Rename / Delete.」
- **不做材质与外观**：「Not at this time. Applying physical materials or appearances is currently unsupported.」
- **装配模式不给保证**：「AA has limited capabilities in Assembly mode. Modeling create/update/delete operations may not work reliably.」
- **不能中途打断**：「Not currently. Once AA begins responding, it cannot be interrupted.」（注：同页另一条说 agentic 任务可以 Cancel，两者指的不是同一件事——前者指「生成回复」。）
- **不支持 Web/Manage/移动端**：见 §4（来源：https://help.autodesk.com/view/fusion360/ENU/?guid=LEARNINGPANEL ）。

### 5.2 官方承认的错误形态

- 单提示描述复杂物体「often leads to inaccurate results」，并列出四类：「Incorrect proportions / Misplaced features / Overlapping geometry / Missing clarifying questions」。
- 出错三大类原因：「Spatial reasoning errors (wrong face or orientation) / Incorrect scale or proportions / Choosing the wrong modeling operation」。
- **选择感知有限**：「Selection awareness is limited (AA may not know what face or body you selected)」。
- **不追踪手工改动**：「It may not detect manual changes made between prompts」。
- **单位**：「AA's internal modeling tools currently operate in centimeters」——英寸设计可能被当厘米（原文举例：要求 [2,0,0] 英寸会被放到 2 cm）。
- **文档类回答也会错**：快捷键、版本相关细节、复杂工作流的「accuracy may vary」；并承认会把 Fusion 叫成「Fusion 360」。

### 5.3 【宣称】vs【事实】

- 【宣称】「an AI‑powered assistant ... Create and modify designs using natural language」（FAQ 首节）。
- 【事实】能动的只有「basic to moderately complex geometry」，且草图不含尺寸与约束（同页 Design & Modeling 节）。
- 【宣称】「can generate native, editable 3D CAD geometry inside Fusion」。
- 【事实】同页紧接着写「AA may report success if the tool executed without error — even if the geometry is not what you intended」——**「可编辑」成立，「正确」不成立**。
- 【宣称】开启 Tech Preview 后可「Query your model / Help you work through a task / Perform a task for you」（帮助页）。
- 【事实】「For me」的定义即为「Prepare an action, show what it plans to do, and run it after you approve」（同一 URL）——「代做」被产品定义成「经批准的代做」。

## 6. 对我方目标的可用处（机制层面，含**不能**学什么）

**能学的**

- **「亮计划 → 批准 → 执行」的产品契约**：这正是我们要的「human-approve 编排」的现成范式，且它有官方原文可引（§5.1 第一条）。
- **「命令跑通 ≠ 几何正确」写成显式警告**：这句话可以直接搬到我们每一条 SolidWorks 能力的返回值里——`FeatureCut4` 返回非 NULL 不等于切对了。
- **四级授权光谱**：我们可以在工具层做同样的分级：`query`（只读）/`guide`（给步骤）/`prepare`（出方案不执行）/`apply`（执行），每级独立开关。
- **用「宿主里的名字」当选择器**：官方要求用 Browser 里的精确名字——与我们「按名字选特征、按对象选实体（已知事实 32）」完全同向。
- **计量单位陷阱写进产品文档**：cm/inch 这条错误模式，对应我们必须显式声明 `swUnit` 与文档单位。

**不能学的**

- **「让模型直接点界面」**：Fusion 的助手是调自家命令；我们的宿主是 SolidWorks COM，几十个入口有 20+ 参数与 mark 选择语义（见本仓已知事实 1/33/36）。把「模型自由点」搬过来必然踩参数顺序与选择集的坑——我们只能走**声明式工具 + 契约校验**。
- **「一次长提示生成中等复杂零件」**：官方自己承认这条路「often leads to inaccurate results」。我们的目标（规范参数化）恰恰要求逐步、可回归。
- **它的验收方式**：「Always visually inspect」对人可行，对无人值守不行。我们要的是数值/几何门，不是人眼。
- **它的上下文获取方式**：它靠人把 Browser 名字念对。我们不能靠「模型猜名字」——需要程序化读取特征树与选择集。

## 7. 许可与红线

- **商业闭源订阅**：不可抄其提示词、工具名、UI 文案；可引其**行为契约**作设计依据（且必须带 URL，本卡即按此写）。
- **模型第三方**：官方称使用「various一流的 third-party models」，托管在 Autodesk 云，且「模型提供商不使用客户数据训练」（来源：https://www.autodesk.com.cn/support/technical/article/caas/sfdcarticles/sfdcarticles/Autodesk-Assistant-Supported-Products-and-How-to-Use-It.html ）。
- **不要照抄它的「能力清单」当我们的验收标准**：它的清单是产品承诺，不是工程判据。

## 8. 证据清单

- https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/Autodesk-Assistant-in-Fusion-FAQ.html —— 权威一手 FAQ（2026-10-14 版）：全部「能做/不能做」逐条问答、四级能力、Flex tokens 计量、单位与装配限制、「report success 但几何可能错」。
- https://help.autodesk.com/view/fusion360/ENU/?guid=LEARNINGPANEL —— 帮助页「About Autodesk Assistant in Fusion」：四种模式（Tell/Show/With/For me）各自的示例提示、Tech Preview 开关、订阅权限矩阵、Web/Manage/移动端不可用。
- https://www.autodesk.com.cn/support/technical/article/caas/sfdcarticles/sfdcarticles/Autodesk-Assistant-Supported-Products-and-How-to-Use-It.html —— 总览 FAQ（中文机翻）：第三方模型、托管边界、提示与历史留存期限、内容安全与租户隔离。

## 9. 未确认事项

- **帮助页正文未能直读**：`help.autodesk.com` 是 JS 应用，直接抓取只返回「Fusion Help | Autodesk Help Home」。本卡引用的帮助页内容取自该 URL 的检索索引正文；**逐字引用前建议在浏览器里复核一次**。
- **Flex tokens 的具体额度与单价**：FAQ 只说「per-seat monthly quota」与「可另购」，**没有数字**（查不到）。
- **仿真与工程图**：FAQ 与帮助页均未提及，故本卡只写「查不到能力声明」，**不等于**官方声明「不做」。
- **「AI visualizations 每月 20 张」**：该数字出自帮助页脚注，本卡按原文引；未见其他页面复核。
- **AutoCAD/Vault 等其他产品里的 Assistant**：官方另有总览页列出多产品，本卡只覆盖 Fusion，跨产品差异未核。
- **它是否真的调 Fusion 的公开 API 还是内部接口**：官方未披露；FAQ 里出现过「Tool names (e.g., fusion_mcp_create)」这类内部字串被误显示（来源：FAQ 同上），但**不能据此断定**其架构。
