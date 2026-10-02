# 调研报告 · 社区 SolidWorks MCP / Python 库（2026-10-02）

> 这份是**对照报告**，不是进度。★ 结论先行，附**许可判定**（铁律 6：能否抄）。
> ★ **v2：已按铁律"逐份读真实 LICENSE"补做克隆与读码**（三个仓库已在 `C:\swprojects\`）。

## 〇、v2 的更正与新增（★ 先看这里，因为**推翻了 v1 的两条许可判断**）

### ★★★ 更正一：三个项目**全部是 MIT**（v1 写"许可未明/待核"是错的）
```
★ 已克隆到 `C:\swprojects\`，**逐份读了 LICENSE 文件**（不采信 README 徽章）：

| 项目 | 目录 | LICENSE 实读 | 规模 |
|---|---|---|---|
| `just1step/solidworks-mcp` | `just1step__solidworks-mcp` | ★ **MIT**（1087 B）| 69 个 .cs · 3.5 MB |
| `Cai-aa/CAD-Agent-Hub` | `Cai-aa__CAD-Agent-Hub` | ★ **MIT**（1084 B）| 120 个源文件（117 py + 3 cs）· 1.4 MB |
| `deloarts/pyswx` | `deloarts__pyswx` | ★ **MIT**（1094 B）| 107 个 .py · 2.8 MB |
⇒ ★★ **三个都可抄代码**（保留版权声明）⇒ ★ 与 SolidPilot/q3ds 的 AGPL **完全不同**
```

### ★★★ 更正二：CAD-Agent-Hub 的 SolidWorks 部分**有 Feature Graph IR**（v1 漏了）
```
MCP/Solidworks/ 下（★ 最大的三个文件）：
  src/solidworks_mcp/executor.py         42,197 字节
  src/solidworks_mcp/native_features.py  34,675
  src/solidworks_mcp/interactive.py      23,309
  src/solidworks_mcp/server.py           22,746
  src/solidworks_mcp/feature_graph.py    13,473
  schemas/feature-graph.schema.json       5,001
  docs/compatibility-and-lessons.md       2,593   ★★ 见下
  tests/（14 个测试文件，含 test_save_routing.py / test_single_document_mode.py）
⇒ ★ 与 SolidPilot 的 IR 路线是**同类**，但**独立实现** ⇒ ★ 可对照两家的 schema
```

---

## 〇之二、★★★ **读码后的五条新发现**（★ 比 v1 的四条更具体、更能直接用）

### ① ★★★ CAD-Agent-Hub 的容差判据是「**按尺度算 + 逐轴判**」（可直接抄）
```
native_features.py:238  tolerance_mm = 1e-5                       ← 回读校验
native_features.py:642  tolerance       = selector["tolerance_mm"]  默认 **0.05 mm**
native_features.py:647  radius_tolerance =                          默认 **0.1 mm**
native_features.py:655  断言 |dx| ≤ tol 且 |dy| ≤ tol 且 |dz| > tol   ★★ **三根轴分别判**
involute_gear.py:327    radius_tolerance = max(0.08, 模数 × **0.08**)  ★★ **容差随模数缩放**
⇒ ★★ 比我们现在用的「相对容差 1e-6」更工程化：**绝对 mm 容差 + 逐轴判 + 随特征尺度缩放**
⇒ ★ 我今天做质量属性（`specs/138`）用的就是相对容差 ⇒ ★ **可换成它这套**
```

### ② ★★★ 它的 `test_save_routing.py` 是「**负例证明门禁**」的教科书写法（★ 对应我们事实 62）
```
用两个假对象**互相禁止对方那条路**：
  class _NativeModel :  SaveAs3() 写盘 ; SaveAs()  → raise AssertionError("native saves must not use export SaveAs")
  class _ExportModel :  SaveAs3()  → raise AssertionError("foreign exports must not use native SaveAs3")
★ ⇒ 原生保存走 SaveAs3、导出走 Extension.SaveAs，**两条路被测试双向锁死**
⇒ ★ 抄这个形状：★ 我们的门禁如果只是"查有没有调"，不如这样"**让错误的那条直接抛**"
```

### ③ ★★ 它的保存路由（★ 与我们的红线直接相关）
```
原生 .sldprt/.sldasm/.slddrw  ⇒ `IModelDoc2.SaveAs3`（三参数兼容路径）
STEP/IGES/STL/PDF/DXF/DWG   ⇒ `IModelDocExtension.SaveAs`，**绝不走 SaveAs3**
★ 两条路都**验证目标存在且非空**才报成功
⇒ ★★ 「导出后验证产物非空」= **我们缺的收尾检查**（我们只验了"调用没抛"）
```

### ④ ★★ 旋转轴的两套 mark —— ★ 我们**没核过**
```
草图构造线做轴 ⇒ 选 `EXTSKETCHSEGMENT` + **mark 4**
参考轴          ⇒ **mark 16** + `FeatureRevolve2`；老兼容调用 `FeatureRevolve` 用 **mark 4**
★「Axis strategy never changes during a retry」——重试时轴策略不变，只允许 API 版本回退
⇒ ★ 我们的 `solidworks_revolve_boss` **没验过轴的选择** ⇒ ★ 可抄这条判据
```

### ⑤ ★★★ just1step 的工具是「**工作流动词**」，不是「API 方法名」（★ 路线对照）
```
它只有 **7 个 Tools.cs**（Assembly / Connection / Document / Feature / Selection / Sketch / Workflow）
最大那个 WorkflowTools（11.7 KB）里 5 个工具全是**多步带验收**的高层动作：
  DiagnoseActiveDocumentHealth              诊断当前文档健康度
  ReviewModelStructureHygiene               模型结构卫生检查
  CutFaceByProjectedEdges                   按投影边切面（faceIndex + 深度 + innerLoops）
  ReplaceNestedComponentAndVerifyPersistence ★★ 替换嵌套件**并验证持久化**
  ReviewTargetedStaticInterference          定向静态干涉复核（两条 hierarchy path + 相邻面算不算）
⇒ ★★ 这与我们**路线相反**：我们 150 个工具大多是「一个 API 调用 = 一个工具」，它是「少而深」
⇒ ★★ **不冲突，是互补**：★ 我们的"广"可以再叠一层它的"深"（包装成工作流工具）
```

### ⑥ ★★ 文档生命周期当**事务**（★ 我们"关件不保存"的更严版本）
```
建模运行是事务：先枚举 → **拒绝关闭用户未管理或脏的文档** → 只关自己认得的干净 MCP 文档
→ 建一个测试文档 → 失败时自动关掉它
★ 它还设了「ownership marker」，让重载后不会把自己生成的模型当成野文档
⇒ ★★ 我们只做到"关件不保存"⇒ ★ 它这条**多一层"不许碰脏文档"** ⇒ 值得抄
```

---

## 一、结论先行：**五个项目里三个已在台账，其中两个是同一条链**

| 项目 | 真实身份 | 许可（★ 实读 LICENSE） | 台账状态 |
|---|---|---|---|
| **SolidPilot** | ★ **`eyfel/mcp-server-solidworks`**（355 星）的**公开名** | **AGPL-3.0** | ✅ 已登记 |
| **q3ds-solidworks-mcp** | ★ **SolidPilot 的 fork**（Benny Cohen 自 2026-07-11 维护）| **AGPL-3.0** | ✅ 已登记 |
| **just1step/solidworks-mcp** | 单 exe + 托盘 Hub/Proxy | ★ **MIT**（已克隆）| ★ 本次补登 |
| **CAD-Agent-Hub**（Cai-aa）| 含 `MCP/Solidworks`（**自带 Feature Graph IR**）| ★ **MIT**（已克隆）| ★ 本次补登 |
| **pyswx**（deloarts）| SolidWorks API 的 Python 封装 | ★ **MIT**（已克隆）| ★ 本次补登 |

⇒ ★★ **AGPL 两个 ⇒ 铁律 6：只读思想，不抄代码。三个 MIT ⇒ 可抄（保留版权声明）。**

★ **一处身份澄清**（台账里原来只写目录名 `mcp-server-solidworks`）：
```
`eyfel/mcp-server-solidworks` 的**公开产品名是 SolidPilot**；
`Bennyco86/q3ds-solidworks-mcp` 是它的 AGPL-3.0 独立分支（基于上游 commit a7348f0）。
★ ⇒ 以后引用写 **`eyfel/mcp-server-solidworks`（产品名 SolidPilot）**，避免有人当成两个项目。
```

---

## 二、四个值得拿的东西（按对本项目的价值排序）

### ① `compare_parts` 的**验证判据** —— ★★★ 最值钱

**它怎么验**（README 原文要点）：
```
compare_parts — 对两个零件做客观 diff（拓扑 / 体积 / 表面积 / 重心），
   判定为 `verified` 的条件是：**拓扑完全相同 且 |ΔV| ≤ 1% 且 |ΔA| ≤ 1%**。
★ 而且：每个零件都在**全新文档**里重建，再与原件比。
```

**我们现在的判据有多弱**：
```
★ 我们（本会话做的 `specs/136` 拉伸族）：断言 **包围盒 == [40, 20, 10]**
⇒ ★★ **包围盒相同 ≠ 形状相同**（倒角/挖槽都可能在包围盒不变的情况下做错）
⇒ ★★ 抄它 ⇒ 真机证据能证明「造对了」，不只是「外框对了」
⇒ ★ **成本低**：这是**判据**不是实现，可直接进我们的证据脚本（`scripts/` 不动）
★ 许可：AGPL ⇒ ★ **抄判据的思路与阈值（1% 这个量级）**，不抄它的代码
```

### ② `execute_batch` —— 一次调用跑 100 步 + 可引用上一步结果

**它怎么做的**：
```
execute_batch — 一次 MCP 调用最多 100 个有序低层操作；
   精确引用（如 `$last.features.0`）可复用前面操作的结果。
inspect_model — 一次返回紧凑拓扑 + 质量属性 + 可选多视图拼图。
★ 它的设计前提写在 README：把几千个 API 方法逐个暴露给 AI 会「炸掉上下文与 token 成本」。
```

**为什么这条对我们直接有用**：
```
★ 我们现在是「一个工具一次调用」⇒ 每批真机验证要十几次 pwsh，**每次都有工具输出进上下文**
⇒ ★★ 这正是今天算出来的成本大头（工具输出 + 每轮重读）
⇒ ★ **可借鉴**：批量操作 + 结果引用 + 一次调用回读多类读数
⚠ 代价：引入「批量」会**放大**我们已有的两个风险（模态框静默挂起、参数用错）
  ⇒ ★ 若采纳，必须配「每步可回读 + 单步失败即停」，不能盲批
```

### ③ 持久引用解析器 —— ★ 它**自己承认这是成败关键**

**它的原话**（README Project Status 段）：
```
★ 「The open problem — and the project's real research risk — is a **durable reference
   resolver**: the v0 geometric anchors reproduce a part exactly in a fresh document but
   do **not** survive upstream edits (a changed dimension moves the anchors).」
★ 并且它把「让语义引用（top_face、某条边）在尺寸与拓扑变化后依然成立」
   称为 **「the make-or-break module still ahead」**。
```

**为什么这条对我们最有用**：
```
★★ 我们的**规则 3（声明式 `selection`）正是在解决同一个问题**
   —— 我今天做的 `index:<n>` / `__current_selection__` 就是这个方向
⇒ ★★ **它的失败模式比它的成功经验更值钱**：
   「几何锚点在全新文档里能精确复现，但一改上游尺寸就失效」
⇒ ★ 这直接对应我们的已知事实 **32**（实体没有可用名字，`SelectByID2("Edge1")` 计数为 0）
  与 **43**（`CreateDefinition` 只收 35 个常量）
⇒ ★ 结论：**我们与它在同一条路上，且它承认还没做完** ⇒ ★ 值得把它的失败模式写进我们的路线图
```

### ④ 按版本标能力等级 + 主动禁高风险（`just1step` 的做法）

**它的版本表**（README 原文）：
| SolidWorks 版本 | 支持状态 | 高风险改动工作流 |
|---|---|---|
| 2024 | **Certified** | Enabled |
| 2025 | Targeted | Enabled |
| **2026** | **Experimental** | **Blocked** |
| <2024 / >2026 | Unsupported | **Blocked** |

⇒ ★ 与我们「不碰高风险写操作（保存/另存/删除）」方向一致
⇒ ★★ **值得学的是「写成了公开的能力表」** —— 让使用者知道「在 2026 上它主动禁了什么」

★ 它的另一处设计约束也很硬（对我们有参考价值）：
```
★ 「`SolidWorksMcpApp.exe` 是唯一支持的入口」「For local use and testing,
   **do not start `SolidWorksBridge` directly**」⇒ ★ 入口唯一化、禁止绕过后台直接起
★ 架构：`client → proxy → hub → MCP tools → SolidWorks`
   ⇒ ★★ **一个 COM 拥有者（hub）+ 多个代理** ⇒ 这是我们事实 24（多客户端抢同一 COM 会死锁）
     的**另一种解法**（我们是命名互斥锁；主任务今天又做了 `sw_isolate` 进程隔离）
   ⇒ ★ 三种解法都摆在面前，值得对照
```

---

## 三、一句话纪律（★ 值得抄进我们的规范，但本次**未改** `AGENTS.md`）

> CAD-Agent-Hub 在**仓库根 README** 写着：
> 「**A successful COM/API call is not by itself proof that a model, mesh, drawing, or
> simulation result is correct; inspect the native application state and generated artifacts.**」

⇒ ★★ 这正是本项目**反复吃到**的教训：
```
· 「能力层能跑」≠「工具能跑」（本会话抓到 `magnitude_n` 漏改名，只走能力层永远看不到）
· 干涉检查曾**静默降级**（不炸、永远拿不到数据）
· `mass` 的物理单位**未确证**（三个读数各自对、乘起来量纲不成立）
· 四家里「README 说验过不等于验过」（187 个工具、0 个测试文件）
⇒ ★ **把这句话写在仓库根，比放在某份 spec 里更有约束力** —— ★ 但本次按用户要求**未改** `AGENTS.md`
```

---

## 四、⚠ 三处如实标注（不替别人认领、不掩饰没核的）

```
① ★ **用户原帖把两个项目的特点混了**：「参数过多时自动生成 VBA 宏绕过 COM 限制」
   —— ★ `just1step/solidworks-mcp` 的 README **里没有这个特性**；
     那个描述属于 NPM 上的 `solidworks-mcp-server`（★ **该项目本次未核**，不敢替它认领）
② ★ **工具数对比**（只按数，不按深度）：
     SolidPilot 上游 **43** · q3ds fork **58** · ★ **我们的 MCP 暴露面 150**
   ⇒ ★ 我们是它们的 **2.6–3.5 倍**；但**工具数不等于功能深度**，不宜据此宣称更强
③ ⚠ **v1 的未核项（v2 已补核）**：`CAD-Agent-Hub` 与 `pyswx` 的许可 ★ **v2 已读真实 LICENSE ⇒ 两者都是 MIT** ⇒ ★ 可抄（保留版权声明）
```

★ 另：★ SolidPilot 与 q3ds 都**自述**「working prototype / early alpha」，
  且「Behavioral verification against live SolidWorks remains **manual by design**」
  ⇒ ★ 与我们的门禁纪律相比**更松** ⇒ ★ **不可作为"验证标准"的参照**。

---

## 五、建议的三件事（按性价比；★ **本次都还没做**）

| # | 做什么 | 成本 | 收益 |
|---|---|---|---|
| 1 | ★ 抄 `compare_parts` 的判据思路（拓扑全等 + ΔV/ΔA ≤1%）进我们的真机证据脚本 | 低 | ★★★ 证据强度上一个量级 |
| 2 | ★ 把「COM 成功 ≠ 结果正确，要看原生状态与产物」写进 `AGENTS.md` | 极低 | ★ 防"看起来能用"的守卫反复失效（**待你批准**）|
| 3 | ★ 台账补三条：`just1step`（MIT，hub/proxy + 版本能力表）· `CAD-Agent-Hub`（许可未明）· `pyswx`（待核）；并给 `mcp-server-solidworks` 补注「产品名 SolidPilot，q3ds 是其 fork」 | 低 | 台账消歧 + 可对照项 +1 |

---

## 六、来源

★ **v2 已克隆并读码的三份（本地只读，未运行）**：

| 项目 | 本地目录 | 我读了什么 |
|---|---|---|
| `just1step/solidworks-mcp` | `C:\swprojects\just1step__solidworks-mcp` | `LICENSE` · 7 个 `Tools.cs`（重点 `WorkflowTools.cs`）|
| `Cai-aa/CAD-Agent-Hub` | `C:\swprojects\Cai-aa__CAD-Agent-Hub` | `LICENSE` · `MCP/Solidworks/README.md` · `docs/compatibility-and-lessons.md` · `native_features.py` 的容差段 · `tests/test_save_routing.py` 全文 |
| `deloarts/pyswx` | `C:\swprojects\deloarts__pyswx` | `LICENSE` · 文件构成 |

★ **只读 README（未克隆）**：`Bennyco86/q3ds-solidworks-mcp`（= SolidPilot 的 AGPL 分支，已在台账）· NPM 上的 `solidworks-mcp-server`。

★ **本机台账**：`D:\AI\SW\docs\sources.md`（21 个外部项目 + 许可判定表，本次更新）
★ **本机克隆盘**：`C:\swprojects\`（23 → 26 个目录）