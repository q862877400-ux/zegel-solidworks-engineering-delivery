# Robusr/Vulcan

<!-- survey: class=D; repr=dsl; orchestration=single; verify=none; deliver=none; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `Robusr/Vulcan` · https://github.com/Robusr/Vulcan |
| 许可 | **GPL-3.0**（`LICENSE` 35823 字节 = GPLv3 全文）⇒ **只读思想，不抄代码、不抄文本**（与本仓 `AGENTS.md` 铁律 6 一致）|
| 元数据 | stars 24 · forks 2 · 语言 C#（24 个 `.cs`）+ Python（31 个 `.py`）· 仓库 13704 KB · 建档 2026-03-02 · 最近推送 2026-10-20（来源：`gh api repos/Robusr/Vulcan`，2026-11-02 取）|
| 克隆 | `D:\swagent-2026Q4\repos\Robusr__Vulcan`（`--depth 1`）|
| 证据等级 | **读码**（仓内仅 1 个测试文件 `beta/client-python-beta/test_server.py`，`release/` 侧零测试；C# 需 SolidWorks 互操作 DLL 才能编译，**未跑**；建模能力结论止步 `source`）|

## 1. 一句话定位

**唯一把「LLM 只输出受控 JSON 特征树、执行器完全确定性」这条契约讲清楚并写成版本化领域提示词的一家**，但覆盖面极窄（只有 `extrude` 与 `cut`、5 种草图轮廓），且**没有任何回读验证**，还留了一处 `SendKeys` 敲键盘的兜底。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：SolidWorks add-in 面板里的自然语言请求（中/英/法皆可，系统提示词本身是中文）。

**中间表示**：**一份带版本号的 JSON 契约**，这是它全部价值所在（见 §3.1）。`release/` 用「LLM 产 JSON → C# 确定性地执行」；`beta/` 是前身，用「LLM 产 Python 代码 → 客户端 `exec()`」——README 明说两代并存，`release/` 是维护中的架构（`README.md`「Why Vulcan」段：「beta/ — the original proof of concept. The LLM generated Python code and the client executed it with `exec()`.」「release/ — the maintained architecture. The LLM returns a typed JSON feature tree and a C# add-in executes it deterministically.」）。

**生成**：Flask 服务端拼「版本化领域提示词 + 用户请求」，调任意 OpenAI 兼容端点，要求**只回纯 JSON**（`release/server/prompts/system_prompt.py:4` `PROMPT_VERSION = "2.0.0"`；同文件开头的「输出铁则」明写「仅输出纯JSON，无任何额外文本、解释、markdown、代码块、注释」「禁止输出 ```json」）。

**编排**：**无编排**——一次请求一份 JSON，一次执行到底；没有多步回环，也没有纠错重试。

**执行**：C# add-in 反序列化特征树，逐个特征建草图、调 COM（`release/client/Vulcan.SolidWorksClient/Services/SwModeler.cs` 25982 字节；`ExecuteModeling` → `ExecuteSingleFeature` → `CreateExtrusionFeature`/`CreateCutFeature`）。特征内的 `FeatureCut4` 参数被逐个对齐并写死注释（`SwModeler.cs:248-269` 逐行标注 `Sd`/`Flip`/`Dir`/`D1`/`NormalCut`/`UseAutoSelect`）。

**验证**：**无**。全仓没有质量属性回读、没有重建错误读取、没有前后对比（`Select-String -Path 'release\client\**\*.cs' -Pattern 'MassProperty|GetWhatsWrong'` ⇒ 0 命中）。成功的判据就是「调用没抛异常」。

**交付**：每个请求处理完做一次视图适配（`SwModeler.cs:89`），不导出任何格式、不出工程图。

## 3. 技术方案要点（可迁移的机制）

### 3.1 JSON 契约的形状（唯一值得搬的东西，且只能搬「设计」）

信封两种（`README.md`「The JSON contract」段）：单特征 `{feature_type, name, params}`，或多特征 `{model_name, features:[…]}`（**有序**，基体在前、后续特征在后）。字段表（README 同段）：

| 字段 | 类型 | 说明 |
|---|---|---|
| `feature_type` | string | `extrude` 或 `cut` |
| `params.plane` | string | 基准面名，**中文**（`前视基准面` 等）|
| `params.shape` | string | `circle` / `rectangle` / `polygon` / `ellipse` / `slot` |
| `params.depth` | number | 盲孔深度（mm）；`through_all` 为真时忽略 |
| `params.through_all` | boolean | 仅 cut，双向贯穿 |
| `params.center_x` / `center_y` | number | 草图中心（mm）|

⇒ 契约小到可以被模型稳定填对，这是它的**优点**；代价是能力上限被锁死在「拉伸 + 切除 + 5 种轮廓」。

### 3.2 版本化领域提示词：把「坐标约定」写成可迭代资产

`system_prompt.py` 不止规定输出格式，还把**平面与轴的映射**写死并给了算例（同文件「核心坐标规则」段）：前视基准面草图是 X-Y（`center_x`→X、`center_y`→Y）；上视基准面是 X-Z（`center_y`→**Z**，且「必须在基体厚度范围内」）；右视是 Y-Z；并要求「多特征建模时，必须先读取前面基体特征的 length/width/depth，再计算后续特征的坐标」，还附了一个 200×100×20 底座打 4 个孔的具体算例（`center_x=±90`、`center_y=10`）。

⇒ **可迁移的是这条资产形态**：把「哪个平面的哪个参数对应哪个轴」这种最容易错、最没人写下来的约定，连同算例一起放进版本化提示词（`PROMPT_VERSION = "2.0.0"`），而不是散在代码里。这与我方「单位必须出现在名字里」是同一类治理手段——**把易错约定提到最上层、可版本化、可被 diff 审阅**。

### 3.3 两个「补丁式兜底」是反面教材

1. **`SendKeys.SendWait("{DOWN 4}")`**（`SwModeler.cs:460-485` 的 `ExecuteExtrusionFallback`）：当 `through_all` 没生效时，靠**发方向键**在下拉框里选「完全贯穿」再 `SendKeys` 填充深度。⇒ 这条路依赖窗口焦点与 UI 布局，任何语言/主题/版本变化都可能让它选错菜单项；而且**它无法被单元测试覆盖**。
2. **四角孔位启发式**（`SwModeler.cs:290-313`）：用户没给孔位时按「基体半长减 10 mm」摆四个角，注释写明「仅用户明确要求时触发」。⇒ 硬编码 10 mm 的边距是**把工程判断写死成常数**，既不是规范也不可配。

两条都指向同一个病：**执行器在缺信息时自己编几何**，而不是拒绝或提问。

### 3.4 三个「我们最贵的四件事」它一件都没解

- **持久引用**：无选择器抽象；`GetSketchCoordinate` 只处理草图内中心点，面/边的选择在 `CreateCutFeature` 里靠「选中零件所有实体」（`SwModeler.cs:233-238`）。
- **回读验证**：无（§2「验证」）。
- **事务式建模**：无回滚；失败即留下半成品。
- **单源 COM 互斥**：add-in 单进程，天然一档；无反多开的显式处理。

### 3.5 仓库卫生问题（影响可信度）

- **提交了 2.9 MB 的 `Vulcan.exe`** 与整包 `ReferenceDLL/`（含 `SolidWorks.Interop.sldworks.dll`、`sldworks.tlb`、`swconst.tlb`），以及 `packages/`、`obj/`、`bin/` 产物（`release/client/Vulcan.SolidWorksClient/…`）。
- **`beta/` 整代**（含 23 KB 的 `VulcanApp.cs`）与 `release/` 并存 ⇒ 读代码要先判断哪一代是活的（README 已说明，但混淆成本仍在）。
- 单文件最大 420 KB 级别的同类问题它没有（对比 `sw-kumar1441-forge-ai.md`），但**执行器 26 KB 单文件**已经很难审。

## 4. 运行条件与依赖

- Windows + SolidWorks（README 徽章标 SW 2025）+ .NET Framework 4.8（C# add-in）+ Python 3.9 + Flask 3.0（`README.md` 徽章段）。
- `release/server/` 是 Flask 应用（`app.py` 2266 字节 + `services/llm_client.py`），可本地/容器/隧道跑；**只有客户端需要 Windows**（README「Portable server」）。
- 需配一个 OpenAI 兼容端点（OpenAI / DeepSeek / Qwen / vLLM / Ollama）。
- 无测试工程；`beta/client-python-beta/test_server.py` 是唯一测试文件。

## 5. 失败模式与已知坑

1. **模型不按 JSON 输出就全盘失败**：没有 JSON 容错、没有重试、没有修复轮；提示词只能靠「铁则」施压。
2. **坐标规则错一处，孔就打到实体外**：`center_y` 在上视基准面代表 Z，提示词用大段规则+算例来防，但**执行器不校验**（打进实体外会得到空切除，且无回读发现）。
3. **`SendKeys` 兜底**（§3.3）：焦点一偏就选错菜单。
4. **`through_all` 靠「强制双向」实现**（`SwModeler.cs:222-233` 注释「完全贯穿时，强制双向切除，确保100%切穿」）⇒ 对单侧有料的零件可能多切。
5. **无验证 = 假成功不可发现**：`FeatureCut4` 完全可能出现「接受了参数但没切」的情形（本轮另两家都记录了这类静默失败，见 `sw-kumar1441-forge-ai.md` §5、`sw-raylanlin-millwright.md` §5 #12/#13）。
6. **能力面锁死**：只有两种特征、五种轮廓、三张标准基准面（`plane` 只接受三张命名平面）。
7. **两代并存**：`beta/` 的 `exec()` 路线虽已废弃，代码仍在仓里，容易被误当现役实现读。

## 6. 对我方目标的可用处（能学 / 不能学）

**Q2 逐条答**：
| 问题 | 它解到什么程度 | 依据 |
|---|---|---|
| 持久引用 | **没解**：无选择器抽象，切除靠「选中所有实体」 | `release/client/Vulcan.SolidWorksClient/Services/SwModeler.cs:233-238` |
| 回读验证 | **没解**：无质量属性/重建错误读取 | 同文件全篇；全仓 `MassProperty|GetWhatsWrong` 命中 0 |
| 事务式建模 | **没解**：无回滚 | 同文件 `ExecuteModeling` |
| 单源 COM 互斥 | **天然一档**（单 add-in 进程），无显式保护 | `Core/SwAddIn.cs` |

**Q3 答**：**不是 MCP 服务端、不是 CLI、也不是库——是「Flask 服务 + SolidWorks add-in」的应用**；工具面 **0 个工具**（没有工具调用面，只有一份 JSON 契约）；粒度 = **一个契约两种特征**，属「少 DSL + 无万能口」的极端。（`release/server/prompts/system_prompt.py` 的 JSON 契约）

**能学**：
1. **版本化领域提示词**（`PROMPT_VERSION`），把平面↔轴映射与算例写进去：可直接用于我方任何「模型必须产出结构化计划」的场景。
2. **「LLM 只产 JSON、执行器确定性」的分层**，以及它**从 `exec()` 迁移到 JSON 的这段历史**（README 明确记下两代）：这是我方「不要 `exec` 模型给的代码」的现成旁证。
3. **有序特征树 + 基体在前的信封**：最朴素的「先基体后特征」约束，简单有效。
4. **`FeatureCut4` 逐参数注释**（`SwModeler.cs:248-269`）：可作参数语义对照，但我方仍须以出厂类型库反射为准（铁律 4）。

**不能学**：
- **缺信息时自己编几何**（四角孔位启发式、`SendKeys` 兜底）——正确做法是拒绝或提问。
- **零验证**：它连「切没切掉」都不查。
- **无 IR 之外的校验**：JSON 契约不做 schema 级语义校验（比如 `center_y` 是否落在基体厚度内）。
- **仓内提交二进制与依赖包**。
- **能力面只有 extrude/cut**：这是「契约简单」的代价，不是优点。

## 7. 许可与红线

**GPL-3.0**（`LICENSE` = GPLv3 全文 35823 字节）。★ **只读思想**：不复制任何代码、不复制提示词文本、不复制 README 文本。§3.1 的契约**字段设计**（`feature_type`/`params.shape`/`through_all` 这类通用概念）本身不受版权保护，但**不得**照搬其提示词措辞、不得照搬 `SwModeler.cs` 的参数注释。若我方要复现「版本化领域提示词」这一形态，须自行撰写并用我方单位命名规约（`_mm` 后缀）重写。

## 8. 证据清单

- `LICENSE`（GPLv3 全文，35823 字节）· `README.md`「Why Vulcan」（`beta/` = LLM 产 Python + `exec()`；`release/` = 类型化 JSON + C# 确定性执行）·「The JSON contract」（信封两种 + 字段表）·「Capabilities」·「System architecture」·「Requirements」
- `release/server/prompts/system_prompt.py:4`（`PROMPT_VERSION = "2.0.0"`）· 同文件「输出铁则」段（只许纯 JSON、禁代码块、只写数字不写单位、三张平面名固定）·「核心坐标规则」段（平面↔轴映射 + 200×100×20 打四孔算例）
- `release/client/Vulcan.SolidWorksClient/Services/SwModeler.cs:50`（`ExecuteModeling`）· `:103`（`ExecuteSingleFeature`）· `:132-203`（拉伸）· `:203-269`（切除；`:222-233` 强制双向贯穿；`:248-269` `FeatureCut4` 逐参数注释）· `:290-313`（四角孔位启发式，半长减 10 mm）· `:460-485`（`ExecuteExtrusionFallback` 用 `SendKeys.SendWait("{DOWN 4}")`）
- `release/client/Vulcan.SolidWorksClient/Core/SwAddIn.cs`（12106 字节，add-in 生命周期）· `Services/ApiClient.cs`（3501 字节，调 Flask）· `Models/ModelData.cs`（`ModelData` 反序列化）
- `release/server/app.py`（2266 字节）· `services/llm_client.py`（3586 字节）· `services/param_parser.py`（1518 字节）· `config.py`（511 字节）
- `beta/client-python-beta/test_server.py`（**全仓唯一测试文件**，3 个 `def test_` 量级）
- 仓内二进制：`release/client/Vulcan.SolidWorksClient/Vulcan Setup/Output/Vulcan.exe`（2940453 字节）、`ReferenceDLL/SolidWorks.Interop.sldworks.dll`、`ReferenceDLL/sldworks.tlb`、`ReferenceDLL/swconst.tlb`
- 元数据：`gh api repos/Robusr/Vulcan`（2026-11-02 取：stars 24 / GPL-3.0 / pushed 2026-10-20）

## 9. 未确认事项

1. **`release/` 是否真能跑通**：未编译（缺本机互操作程序集配置）、未跑；README 的 demo 是「Illustrative response」（**它自己标注为示意**）⇒ 端到端能力**未证实**。
2. **三张标准平面之外的自定义基准面**：提示词只允许三张中文名，`GetRealPlaneName`/`FindPlaneFeature` 是否支持其它平面**未逐行确认**。
3. **`SendKeys` 兜底的触发频率**：无日志/测试，**未确认**它在真机上多久走一次。
4. **`beta/` 的 `exec()` 路线是否仍有维护价值**：README 说是「kept for reference」，**是否还能跑未确认**。
5. **多特征时的坐标耦合**：提示词要求「先读基体尺寸再算后续坐标」，但执行器**是否把基体尺寸回填给下一次请求**（单轮内是否有多轮对话）**未确认**。
6. **`Vulcan.exe` 提交进仓是否与源码一致**：未比对（无法验证二进制来源）。
