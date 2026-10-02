# 调研报告 · 社区 SolidWorks MCP / Python 库（2026-10-02）

> 这份是**对照报告**，不是进度。★ 结论先行，附**许可判定**（铁律 6：能否抄）。
> 调研方式：★ 先核本机台账（`docs/sources.md`）与 `C:\swprojects\` 克隆，
> ★ 再去项目主页核 README / LICENSE；★ **没有下载、没有运行任何外部项目**。

## 一、结论先行：**五个项目里三个已在台账，其中两个是同一条链**

| 项目 | 真实身份 | 许可 | 台账状态 |
|---|---|---|---|
| **SolidPilot** | ★ **`eyfel/mcp-server-solidworks`**（355 星）的**公开名** | **AGPL-3.0** | ✅ 已登记（目录 `mcp-server-solidworks`）|
| **q3ds-solidworks-mcp** | ★ **SolidPilot 的 fork**（Benny Cohen 自 2026-07-11 维护）| **AGPL-3.0** | ✅ 已登记 |
| **just1step/solidworks-mcp** | 单 exe + 托盘 Hub/Proxy 架构 | ★ **MIT** | ❌ 未登记 → **本次补登** |
| **CAD-Agent-Hub**（Cai-aa）| 含 `MCP/Solidworks`（有状态建模）、CATIA、NX、Fusion | ⚠ **README 未写许可** | ❌ 未登记 → **补登但按未明许可处理** |
| **pyswx**（deloarts）| SolidWorks API 的 Python 封装 | ⚠ **未核** | ❌ 未登记 → **补登，待核** |

⇒ ★★ **AGPL 两个（SolidPilot / q3ds）⇒ 铁律 6：只读思想，不抄代码、不抄文本。**

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
③ ⚠ **未核项**：`CAD-Agent-Hub` 与 `pyswx` 的**许可**未核
   ⇒ ★ 按最保守处理（未明许可 ⇒ 不抄）；★ `pyswx`（deloarts）**疑似**与台账里
     GPL-2.0 的 `pySW`（kalyanpi4）**不是同一个**，待核
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

| 来源 | 用途 |
|---|---|
| [raw.githubusercontent.com/Bennyco86/q3ds-solidworks-mcp/main/README.md](https://raw.githubusercontent.com/Bennyco86/q3ds-solidworks-mcp/main/README.md) | SolidPilot / q3ds 的身份、许可、工具数、`compare_parts` 判据、`execute_batch`、引用解析器自述 |
| [raw.githubusercontent.com/just1step/solidworks-mcp/main/README.md](https://raw.githubusercontent.com/just1step/solidworks-mcp/main/README.md) | MIT 许可、单 exe 入口、Hub/Proxy 架构、版本能力表 |
| [raw.githubusercontent.com/Cai-aa/CAD-Agent-Hub/main/README.md](https://raw.githubusercontent.com/Cai-aa/CAD-Agent-Hub/main/README.md) | 含 `MCP/Solidworks` 有状态建模；仓库根那句「COM 成功 ≠ 结果正确」|
| 本机 `D:\AI\SW\docs\sources.md` | 现有台账（21 个外部项目 + 许可判定表）|
| 本机 `C:\swprojects\`（23 个目录）| 核「哪些已在克隆」|

★ **未访问**：`pyswx` 的 README/LICENSE、`solidworks-mcp-server`（NPM）的任何页面。