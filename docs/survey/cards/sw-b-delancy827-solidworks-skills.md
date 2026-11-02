# delancy827/solidworks-skills

<!-- survey: class=B; repr=feature-tree; orchestration=loop; verify=numeric; deliver=STEP; evidence=读码 -->

| 字段 | 值 |
|---|---|
| 仓库 / 主页 | `delancy827/solidworks-skills` · https://github.com/delancy827/solidworks-skills |
| 许可 | **MIT**（`LICENSE` 首行 `MIT License`，版权行 `Copyright (c) 2026 delancy827`；`solidworks-mcp/pyproject.toml` 亦写 `license = "MIT"`）⇒ 可借鉴，保留版权声明即可 |
| 元数据 | stars **152** · 创建 2026-05-30T10:53:46Z · 最近推送 2026-10-07T03:58:32Z · 语言 Python · 仓库 1544 KB（来源：`gh api repos/delancy827/solidworks-skills`，2026-11-02 取） |
| 克隆 | `D:\swagent-2026Q4\repos\delancy827__solidworks-skills`（`--depth 1`，HEAD `33bc2c04`，2026-10-07 11:57:34 +0800；另有远端分支 `codex/debug-clevis-support`，本次未读） |
| 证据等级 | **读码**（未跑：全部脚本要真机 COM；`examples/verified/assemble_two_link_arm.py:21` 硬编码作者本机目录 `C:\Users\22374\Desktop\湛江北海\学习课程\sw`，三个零件文件不在仓内 ⇒ 不可复现） |

## 1. 一句话定位

**本线星数最高的一份「双形态」包：既是两份 Codex/Claude skill（短入口 + 按需 references），又自带一个 27 工具的 MCP 服务端**；主体价值不是建模能力，而是一份把 SW 2024 COM 双接口（makepy 早绑定 + 动态 IDispatch）怪癖逐条实证下来的中文手册，以及一套「先算 bbox 期望值再硬断言」的位姿校验写法。

## 2. 技术路径（输入 → 中间表示 → 生成 → 编排 → 执行 → 验证 → 交付）

**输入**：两条互不相同的入口。
- **Skill 入口**：`solidworks-automation/SKILL.md`（49 行，`cl100k_base` 计 1238 tokens）与 `sw-designer/SKILL.md`（33 行，609 tokens）——前者给「怎么写可执行 COM 代码」，后者给「设计决策与检查清单」。
- **MCP 入口**：`solidworks-mcp/server.py`（49 行）用 `FastMCP` 注册 **27 个** `@mcp.tool()`：`connection_tools.py` 7 个、`modeling_tools.py` 12 个、`screenshot_tools.py` 2 个、`verification_tools.py` 6 个（来源：`solidworks-mcp/tools/*.py` 逐文件 `@mcp.tool` 计数，2026-11-02 实测）。

**中间表示**：**没有 IR**。中间物是「特征树 + 选择集」，另加两个文字型中间物：**尺寸账本**（`SKILL.md:29` 要求把 exact / inferred / designer-choice / unsupported 四类尺寸分开）与 **几何指纹**（`SKILL.md:20` 要求每次改动前抓特征数、实体数、bbox、体积、关键尺寸）。

**生成**：生成 Python COM 脚本 / C# 控制台程序 / VBA 宏三选一（`SKILL.md:30-33`：Python COM 优先；>12 参的复杂切除改 C# 或 VBA）。仓内两种语言都真写了：**40 个 .py 共 5702 行、30 个 .cs 共 3818 行**（来源：`git ls-files` + 逐文件 `Get-Content | Measure-Object -Line`，2026-11-02 实测）。

**编排**：`loop`。`README.md` v4.8.0 节自述「双重嵌套纠错环（编译纠错 + 几何校验 + 视觉 QA）」；`SKILL.md:21-22` 把闭环写成硬规则：改动→rebuild→重读指纹→断言，断言失败就停当前策略、打 traceback 与特征树、给具体 fallback。

**执行**：**双通道并存**，这是它最可迁移的一处。`examples/verified/sw_common.py:39-59` 同时拿两个对象：`sldworks_gen.py`（由 `makepy` 从 `sldworks.tlb` 生成）的早绑定接口，和动态 `CDispatch`；`com-dualinterface-quirks.md:10-14` 给出分工判据——动态层大量 `找不到成员 (-2147352573)`，早绑定层遇 byref 出参（`OpenDoc6`/`Extension.SaveAs`/`ToolsCheckInterference2`）会炸，所以按方法选用。`sw_common.py:30-36` 的 `pm()` 再兜住「同一成员在两层一个是属性一个是方法」。

**验证**：**数值断言**，三种。
1. **位姿**：`assemble_two_link_arm.py:140-143` 手算期望装配 bbox `(-0.13814, 0.0, -0.075, 0.075, 0.25314, 0.13081)`，逐项 `abs(g-w) < 0.002`（米，即 2 mm）硬断言。
2. **体积/包围盒/特征树三重**：`com-dualinterface-quirks.md:156` 写明「体积查材质多少、bbox 查在哪、特征树查留了什么垃圾」。
3. **防假跑**：`README.md` v4.1.0 节记「`GetFeatureCount()` 会被空草图/错误特征绕过 ⇒ 改用 `GetBodies2` 实体计数」。

**交付**：`.SLDPRT` / `.SLDASM` / PNG 截图 / STEP（`SKILL.md` 未把 STEP 写成必交付；MCP 侧 `sw_save_document` 走 `SaveAs`）。

## 3. 技术方案要点（可迁移的机制）

### 3.1 「双接口」分工判据（本卡第一价值）

`com-dualinterface-quirks.md:10-14` 的原话是判据，不是猜测：动态 IDispatch 报 `找不到成员 (-2147352573)` → 换 makepy 早绑定；早绑定遇 byref 出参炸 `int() argument must be ...` → 回退动态。`sw_common.py:84-89` 的 `open_doc` 就是这条判据的落地：`OpenDoc6` 走动态 + `VT_BYREF|VT_I4` 的 errs/warns，拿回对象再 `typed()` 成早绑定。

★ 这条与我们已知事实 32、与 `Slacker-LLC` 卡的 `flag_methods` 路线**是两条不同解法**：Slacker 用「运行时 `_FlagAsMethod` + `value()` 兜可调用对象」在纯动态层解决；本仓直接生成类型库包装绕开动态层。两法各有代价（前者不依赖 tlb，后者要求本机有 `sldworks.tlb` 且版本对得上）。

### 3.2 接口归属表（7 行，可当核对清单用；来源：`com-dualinterface-quirks.md:24-34`）

`com-dualinterface-quirks.md:24-34` 给了一张「API → 真实宿主」表，与我们的 `docs/existing-assets.md` 口径直接对口：

| API | 真实宿主 |
|---|---|
| `GetPartBox` | `IPartDoc`（不是 IModelDoc2） |
| `GetBodies2` | `IPartDoc` / `IComponent2` |
| `GetBox` | `IAssemblyDoc` / `IBody2` |
| `AddComponent5` / `AddMate3` / `GetComponentCount` | `IAssemblyDoc` |
| `CreateArc2` / `InsertAxis2` | `IModelDoc2`（SketchManager 上没有） |
| `GetMathUtility` | `ISldWorks` |
| `Volume` | `IMassProperty` propget（经 `Extension.CreateMassProperty()`） |

### 3.3 六条会直接改我们代码的实测结论

1. **`Create3PointArc` 的弧不并入轮廓** → 轮廓不闭合 → `FeatureExtrusion2` **静默返回 `None`**，且 `SketchAddConstraints("sgMERGEPOINTS")` 救不回来；改用 `IModelDoc2.CreateArc2(圆心, 起点, 终点, 方向)`，**且弧必须先画**（`com-dualinterface-quirks.md:35-45`）。
2. **`FeatureExtrusion2` 第 21 参是 T0 枚举不是偏移距离**：0=草图面、3=`swStartOffset`；把距离误传进 T0 会被**静默截断为 0**，特征照建（`com-dualinterface-quirks.md:47-58`）。
3. **偏移模式下 `Flip` 无效**，反方向偏移要用负 `StartOffset`（同上 `:57-58`）。
4. **`AddComponent5` 前零件必须已 `OpenDoc6` 进内存**，否则静默返回 None、组件数 0（`com-dualinterface-quirks.md:70-78`）。
5. **`ComposeTransform` 的 X/Y/Z 是旋转矩阵的三列，且必须传 `IMathVector` 对象**；裸数组会被静默错拆（`com-dualinterface-quirks.md:80-93`）。读回 `Transform2.ArrayData` 布局是 `[R(9), T(3), 1,0,0,0]`，与输入布局不同。
6. **装配里 `SelectByID2("前视基准面@支座-1", "PLANE", ...)` 返回 False 且选不中**，可靠姿势是 `IComponent2.FeatureByName` + `IFeature.Select2`；命中选面 `SelectByID2("", "FACE", x,y,z,...)` 可用但**返回值不可信**，要读 `SelectionManager.GetSelectedObjectCount2(-1)` 并用 `GetSelectedObject6(cnt,-1).GetComponent().Name2` 验归属（`com-dualinterface-quirks.md:99-115`）。

### 3.4 「先建命名基准轴」= 一种廉价的持久引用

`com-dualinterface-quirks.md:119-123`：建模时选中孔圆柱面 → `IModelDoc2.InsertAxis2(True)`（**返回 bool 不是特征**）→ 靠动态遍历特征树找 `GetTypeName2 == "RefAxis"` 的最后一个拿名字。这些轴就是装配同心配合的稳定命名实体。`sw_common.py:276-301` 是它的实现。
⇒ 对我们 Q2 的「持久引用」：这是**用「主动补一个命名实体」换「选面不失效」**的思路，比解析器便宜，但要求建模阶段就规划好。

### 3.5 成本结构：短入口 + 按需 references

`README.md` v5.4.0 节把这件事写成了版本主题：「技能主文档改为低上下文短入口，完整手册与实战经验按需加载」。

实测口径（`cl100k_base`，`D:\swagent-2026Q4\token-cost.md` 与同目录逐目录复算，2026-11-02）：

| 层 | 内容 | tokens |
|---|---|---:|
| 入口 | `solidworks-automation/SKILL.md` | 1238 |
| 入口 | `sw-designer/SKILL.md` | 609 |
| 按需 | `solidworks-automation/references/` 5 份（`automation-manual.md` 独占 38794） | 49398 |
| 按需 | `sw-designer/references/design-manual.md` | 12809 |
| **应删未删** | `skills/` 3 份旧文档 | **59741** |

⇒ 入口只占整包的 **2.0%**（1238 / 62207），设计意图成立。★ 但 `skills/` 那 59741 tokens 的旧文档仍在树里，一旦被模型搜到，等于成本翻倍（来源：同上 `token-cost.py` 复算）。

`SKILL.md:52` 还给了检索用法：`rg -n "keyword" references/automation-manual.md` 再读窄行区间，明确禁止默认整文件加载。

### 3.6 覆盖域

两份 skill + 27 个 MCP 工具（来源：`solidworks-mcp/tools/*.py` 的 `@mcp.tool` 计数），覆盖：连接/文档、草图（线/圆/矩形/弧）、拉伸/切除、多角度截图、验证（含 `sw_get_status` 一类）。C# 侧另有一批具体零件：叉形接头（`src/clevis-joint/`）、U 形凸模（`src/punch-die/`）、分阶段试验（`src/stages/`）、10 个反射探针（`src/probes/`）、3 个几何校验测试（`src/tests/`）。

## 4. 运行条件与依赖

- 真机 SolidWorks **2024**（README 徽章写 `2024+`，手册多处写 SW 2024 SP5 / 32.5.0）+ Windows。
- Python 依赖只有一条：`pywin32>=311`（`requirements.txt`）。MCP 侧 `solidworks-mcp/pyproject.toml` 另加 `mcp[cli]>=1.27.0`、`psutil>=5.9.0`。
- 早绑定通道需**额外一步**：`examples/verified/make_typelib_wrapper.py` 用 `win32com.client.makepy` 从 `sldworks.tlb` 生成 `sldworks_gen.py`（37 行，含注册表找 tlb 的回退）。
- 无自动化测试入口：`solidworks-automation/test-prompts.json` 是 **4 条提示词 + 期望行为**，不含任何执行结果；`src/tests/*.cs` 是 3 个零件级几何校验程序（101/98/149 行），要真机跑。

## 5. 失败模式与已知坑

**自述坑**（都在 §3.3，另有两条）：`GetPartBox(NoConversion)` 传 `True` 才恒为米、`False` 跟文档单位走；`ShowNamedView2` 第二参传 `-1` 视图根本不切，正确 ID 是等轴测=7/前视=1/上视=5/右视=4；截图前必须 `ActivateDoc3`，因为 `Extension.SaveAs(png)` 导的是**活动窗口**文档（`com-dualinterface-quirks.md:125-132`）。

**本卡实读发现的缺陷**（这是本卡必须打折扣的地方）：

1. **「0.000% 体积偏差 / 9-9 配合」不可复现**。`README.md:523`、`examples/verified/README.md:4-6`、`com-dualinterface-quirks.md:3-5` 三处都写了「三零件体积与理论值偏差 0.000%、9/9 配合自动添加」，但仓内**没有**那三个零件（`assemble_two_link_arm.py:111-115` 依赖 `支座.SLDPRT` / `连杆.SLDPRT` / `销轴.SLDPRT`），也**没有**任何体积/配合的运行日志或报告 ⇒ 按【宣称】处理，不能并入事实。
2. **同一文件的注释自相矛盾**：`assemble_two_link_arm.py:8` 的模块 docstring 写「X/Y/Z 为旋转矩阵的**行向量**（不是列！）」，而 `:27` 的正文注释与 `com-dualinterface-quirks.md:82` 都写「**列**」。代码按列写的（`R_Z135 = ((C,S,0),(-S,C,0),(0,0,1))`），所以是 docstring 陈旧未改。
3. **README 的「>12 参即失败」过度概括**：`README.md:169` 写「Python COM 调用 >12 个参数的方法会失败（COM 限制）」，而 `requirements.txt` 的注释限定为「v306 has known issues with >12 param APIs」，即**pywin32 版本问题、311 已修**。同一仓两份文件给出强度不同的结论，采信后者。
4. **v5.1.2 声称「替换源码中硬编码路径为通用占位符」，实际没换干净**：`assemble_two_link_arm.py:21` 仍是 `C:\Users\22374\Desktop\湛江北海\学习课程\sw`；`sw_common.py:24-25` 硬编码 `C:\ProgramData\SolidWorks\SOLIDWORKS 2024\templates\...`。
5. **仓内同时有 `skills/`（旧）与 `solidworks-automation/`（新）两套**：`skills/DEPRECATED.md` 自认作废，但 `skills/solidworks-automation.md`（3275 行 / 142,983 字节）与 `skills/sw-designer.md`（558 行）仍留在树里，与 `references/automation-manual.md`（2756 行）内容重叠、版本不同步 ⇒ 读者容易读错那一份。
6. **`solidworks-mcp/` 的验证工具未与 skill 侧打通**：MCP 侧 6 个 verification 工具（来源：`solidworks-mcp/tools/verification_tools.py`）与 skill 侧的 W-A-R 铁律是同一思想的两套实现，没有共享代码。
7. **深度 1 克隆看不到历史**：README 的版本叙事（v3.2.0 → v5.5.0）无法在本地核对，只能当作者自述。

## 6. 对我方目标的可用处（机制层面）

**能学（机制）**：

- **双接口分工判据 + `pm()` 属性/方法自适应**：这是本线里唯一给出「什么时候必须早绑定」判据的一份，且与 `Slacker-LLC` 的运行时 flag 路线互补。我们若继续纯动态，至少应把「byref 出参走动态、其余走早绑定」写成选择规则。
- **接口归属表**：7 行，可直接进 `docs/existing-assets.md` 的对照名单（`GetPartBox`→`IPartDoc` 这类错误我们踩过）。
- **`CreateArc2` + 弧先画**：一条能省掉「拉伸静默返回 None」整轮排查的事实，值得写成一个负例测试。
- **T0 枚举 vs 偏移距离（第 21/22 参）**：与已知事实 32 的 mark 语义同类——「参数位错一位，静默错」。
- **手算期望 bbox 再逐项断言**：把「摆位对不对」变成可判定的数，是我们 `verify` 从 `run-only` 升 `numeric` 的最短路径之一；容差写法（2 mm）也可直接抄。
- **「用 `GetBodies2` 实体计数防假跑」**：比 `GetFeatureCount` 可靠，是一条便宜的高杀伤检查。
- **主动补命名基准轴换稳定选择**：Q2 持久引用的低成本变体。
- **短入口 + 按需 references + 给出检索命令**：把指令成本压到 1238 tokens 的做法，可作为我们 skill 化的成本模板。

**不能学**：

- **不可复现的数值宣称**（`README.md:523` 的 0.000% 体积偏差与 9/9 配合）：无零件、无日志，只能记【宣称】。
- **两套并存未清理的旧文档**：`skills/` 与 `references/` 内容重叠不同步，会误导读者。
- **把 MCP 服务端塞进 skill 仓**：`solidworks-mcp/` 与 skill 侧不共享代码，等于维护两份同思想实现。
- **硬编码本机路径**：与本仓纪律直接冲突。
- **单点真机证据**：仓内没有任何可重放的测试结果，3 个 `.cs` 校验程序也只能真机跑。

## 7. 许可与红线

**MIT**（`LICENSE` 全文 + `Copyright (c) 2026 delancy827`）。义务只有一条：保留版权声明与许可全文。⇒ 上面 §3 的机制与事实可自由移植，但按本仓铁律 1 仍要留来源头注释。

**来源披露**（作者自己写的，对我们判断「重复度」有用）：`README.md:559` 记 v5.3.0「经验来源：SolidPractices/CADSharp、wzyn20051216 (MIT)、vespo92/SolidworksMCP-TS (MIT)、andrewbartels1/eyfel 等社区开源项目」；`:620` 记 v5.0.0「经验来源：wzyn20051216/solidworks-automation-skill（MIT，283 stars）」；`:550` 记 Sec 42-46 来自 CSDN/抖音/B站/知乎等社区公开实践。⇒ **它明确承认自己是「多来源缝合」**，不是原创知识。

## 8. 证据清单

- 结构：`git ls-files` 94 个文件；`.py` 40 个 5702 行 / `.cs` 30 个 3818 行 / `.md` 19 个 9258 行（逐文件 `Get-Content | Measure-Object -Line` 汇总，2026-11-02）
- `solidworks-automation/SKILL.md:14-24`（Operating rules，含几何指纹与「不许凭返回值判成功」）· `:29`（四类尺寸账本）· `:30-33`（Python/C#/VBA 三通道选择）· `:52`（`rg -n` 检索用法）
- `solidworks-automation/references/automation-manual.md`（2756 行；`^## ` 计 50 个标题 = 3 条铁律 + 1 条 SW 2024 踩坑 + 46 章，与 README 的「46 章」一致）
- `solidworks-automation/references/com-dualinterface-quirks.md:10-14`（双接口分工）· `:24-34`（接口归属表）· `:35-45`（CreateArc2 + 弧先画）· `:47-58`（T0 枚举）· `:70-78`（AddComponent5 前置）· `:80-93`（ComposeTransform 列向量）· `:99-115`（装配选择绕开 SelectByID2）· `:119-123`（InsertAxis2 命名轴）· `:125-132`（视图与截图）· `:156`（三重断言）
- `solidworks-automation/examples/verified/sw_common.py:30-36`（`pm()`）· `:39-59`（双通道 connect）· `:84-89`（OpenDoc6 byref）· `:162-172`（bbox）· `:276-301`（InsertAxis2 + 动态特征树）
- `solidworks-automation/examples/verified/assemble_two_link_arm.py:8` vs `:27`（行/列向量矛盾）· `:21`（硬编码本机路径）· `:111-115`（依赖仓外零件）· `:140-143`（bbox 硬断言）
- `solidworks-automation/examples/verified/make_typelib_wrapper.py`（37 行，`makepy` 生成 `sldworks_gen.py`）
- `solidworks-mcp/server.py`（49 行，`FastMCP` stdio）· `solidworks-mcp/tools/*.py` 逐文件 `@mcp.tool` 计数 7+12+2+6 = 27 · `solidworks-mcp/pyproject.toml`（`mcp[cli]>=1.27.0` / `pywin32>=311` / `psutil>=5.9.0`）
- `README.md:169`（>12 参失败）vs `requirements.txt`（限定 v306、推荐 v311）· `README.md:523`（0.000% / 9-9 宣称）· `:559` / `:620`（来源披露）· `:525-539`（v5.4.0 短入口）
- `solidworks-automation/test-prompts.json`（4 条提示词 + `expected`，无结果）
- 成本读数：`D:\swagent-2026Q4\token-cost.md`（`python token_cost.py`，`cl100k_base`，2026-11-02）
- 元数据：`gh api repos/delancy827/solidworks-skills`（2026-11-02）

## 9. 未确认事项

1. **`README.md:523` 所称「三零件体积偏差 0.000%」「装配 9/9 配合」**是否有仓外记录（issue / 博客 / 视频）——**查不到**，本卡按【宣称】处理。
2. `automation-manual.md` 46 章里哪些结论是作者本机实证、哪些是从 wzyn20051216 / vespo92 / andrewbartels1 转述——**未标注逐条来源**，无法区分。
3. `codex/debug-clevis-support` 分支与 main 的差异（可能是未合并的调试成果）——**未读**。
4. `solidworks-mcp/tools/*.py` 里的 27 个工具是否真机跑过——仓内无测试结果，**未确认**。
5. 早绑定通道在 SW 2025/2026 上是否仍成立（手册全部基于 SW 2024 SP5）——**未确认**。
6. `sw-designer/references/design-manual.md` 的 18 个标题与 README 所称「17 章」是否只差一个总标题——**未逐节核对**。
