# 交接包 v2：再次修改 `D:\AI\SW\AGENTS.md`

> **给执行者**：这是**内容变更单**，不是草稿。原作者（另一个 AI 会话）被要求不改这个文件，
> 只提供「要写进去的**事实与结构建议**」。具体措辞、排版、章节层级由你按 AGENTS.md 规范决定。
>
> **v1 已生效**：你上一轮已把 AGENTS.md 从 34 KB / 551 行压到 **21 KB / 200 行**，
> 拆出 `docs/{upstream-layout,sources,provenance-format,team-roles,local-resources,kickoff-template}.md`。
> **本 v2 只讲 v1 之后发生的事。** v1 的改动本身都成立，不用回退。

---

## 第 0 部分 · 一句话：任务定义变了

**AGENTS.md 现在第〇章还写着：**

> 把 `wzyn20051216/solidworks-automation-skill`（1010 星, MIT）补强成「…」，**最后推一个 fork**。

**2026-10-01 用户指示，这句话不再适用，原话：**

> 「我们现在这么多各家所长和自己的护城河，我们完全可以自己建立一个仓库，引用别人就行了」

### 为什么这个判断成立（三条理由，都有硬证据）

**① 我们已经在违反 fork 的规矩了**

铁律 3 说「参照上游结构，**不新增顶层目录**」。实测：

```
上游顶层目录:  .github agents ai_team apps assets docs dotnet examples
               mcp-server references scripts subskills tests

我们多了 4 个:  .api-signatures   ← 签名索引
               tools             ← 并集工具
               output            ← 构建产物
               .pytest_cache     ← 测试缓存
```

不是「将要违反」，是**已经违反了** —— 这条约束早就不合身。

**② 我们的资产已经比上游的基底大**

```
上游原有文件:  389 个 / 10.1 MB
我们新增:      100 个 / 18.6 MB      ← 我们的大
我们改过的:     13 个
scripts 模块:  上游 49 个  vs  我们新增 58 个
```

**③ 「fork」这个身份给错了信号**

我们是「集大成 + 建护城河」，不是「上游的补丁集」。

### 用户选定的搬迁方式：**B · 按需搬取**

用户原话与理由：

> 「B · 按需搬取，搬全一点就好了，**你整体继承到时候有什么部分和我们要借鉴的别的项目冲突了怎么办**」

**这个理由是对的**：整体继承会把上游的一整套结构、命名、验证口径带进来，
而我们同时要并入四家外部项目 —— **两套约定会在同一批文件里打架**。
按需搬取时，每一件搬进来的东西都过一遍「并入六条规则」，冲突在搬的时候解决，不留在后面。

**⚠ 一处必须写清**：「引用别人就行」**不等于「不用上游的代码」**。
上游的 `mcp-server/server.py`（104 KB，45 个工具的现成实现，**我们一行没改**）
和 49 个 `scripts/` 模块是**要用的**；只是它们从「本仓库的历史基底」降为**来源之一**，
与四家外部项目同等，须带 MIT 版权声明。**许可义务不变。**

---

## 第 1 部分 · v1 之后的新事实

### 事实 A · DSH 的 SolidWorks MCP 已换源

```
原: C:/Users/Zegel/solidpilot-mcp/adapters/claude/server.py
    eyfel/mcp-server-solidworks (SolidPilot) · AGPL-3.0 · C# 706 个 .cs · 46 工具
新: C:/swprojects/sw-skill-fork/mcp-server/server.py
    上游自带 · MIT · 纯 Python · 45 工具
备份: ~/.dsh/profiles/web/cordis.patch.yml.bak-20261001-solidworks
```

**换的三条理由**（这三条值得写进 AGENTS.md，因为它们是**硬约束**）：

1. **运行时只能有一个 SolidWorks MCP** —— 多个进程抢同一 COM 连接会**死锁**。
   实证：`Eduardof0nt/server.py` 实现了 Windows 命名互斥锁
   （`Local\SolidWorksMCPServer_SingleInstance_v1`）；`Slacker-LLC` 写进已知限制
   （"Two clients driving the same session at once will deadlock it."）。
2. **选上游那个而非任一家外部项目**：它**同源**（直接 `import scripts/*`），
   带着本仓库的官方 API 索引与标准件数据；四家这些都没有。
3. **SolidPilot 是 AGPL-3.0** ⇒ 按铁律 6 只读思想，不作为运行时依赖。

**⚠ 另一个可写进 AGENTS.md 的实测事实**：
上游那个 MCP **只包了 25 个 `scripts` 模块**，本 fork 后补的 56 个**一个都没进去**
（实测：`server.py` 引用的模块与我们新增模块的交集 = **0**）。
**「我们补的能力没被 MCP 暴露」是当前最大的结构性缺口。**

### 事实 B · `D:\AI\SW\solidpilot-salvage\` 已存在（241 文件 / 11 MB）

从 `C:\Users\Zegel\solidpilot-mcp\` 抢救出的**自有成果**（原目录保留当备份、注册已停用）。
里面有几件**直接关系当前任务**：

| 文件 | 为什么重要 |
|---|---|
| `官方文档/拓扑优化_官方做法.md` | **拓扑优化是三个护城河域之一（A9）** —— 做到时先读它 |
| `loose/问题交接2_DISPPARAMS已通卡E_INVALIDARG.md` | COM byref 的实操记录 |
| `loose/问题交接_Simulation夹具API调不通.md` | Simulation 域的坑 |
| `loose/swdoc.ps1` / `swdoc2.ps1` | 官方文档检索工具（AGENTS.md §4.1 引用的那个） |
| `cs-patches/` + `_MANIFEST.tsv` | C# 执行层 14 个文件（6 改上游 + 8 新增） |

**刻意没搬**：`知识库/`（与 `~/.agents/skills/mech-design/知识库/` 是同一份，实测独有 0 个）、
`调研/GitHub项目/`（140 MB，10 个 git 克隆可重取，**且含 `SolidWorks-CAD` 破解投递页 —— 铁律 2 红线零接触**）。

### 事实 C · A 级已完成的部分（v1 时还没有）

| 产出 | 位置 | 状态 |
|---|---|---|
| 并入六条规则全文 | `sw-skill-fork/docs/union-conventions.md` | 已写 |
| 广度地图（含**可执行的并入清单**） | `sw-skill-fork/docs/union-coverage-matrix.md` | 299 行，生成物 |
| 规范门禁 | `sw-skill-fork/scripts/check_union_conventions.py` | 已接进 `release_check.py` |
| 来源与地图构建器 | `sw-skill-fork/tools/build_union_{sources,map}.py` | 已跑通 |

**地图第五节的「来源验证」列值得在 AGENTS.md 里提一句**：
它把「工具最多的 Eduardof0nt 测试文件为 0」这件事，从一条口头警示变成**每张表上都看得见的字段**，
直接决定抄进来先标 `stitched` 还是 `source_verified`（规则 4）。

### 事实 D · 一处 v1 遗留的结构问题（建议顺手解决）

v1 把 AGENTS.md 拆出的 6 个 `docs/*.md` **放在工作区** `D:\AI\SW\docs\`，
而任务产出（`union-conventions.md` 等）在**代码副本** `C:\swprojects\sw-skill-fork\docs\`。

**这个分工是对的**（工作区放指令、代码副本放产出），但 **AGENTS.md 里没有明说**。
建议在「工作区」章节加一句：`docs/` 相对 AGENTS.md 解析 = `D:\AI\SW\docs\`。

---

## 第 2 部分 · 逐处改动建议

| 位置 | 建议 | 依据 |
|---|---|---|
| **第〇章「一句话任务」** | ★ **必须重写** | 事实：fork 不再适用；改「自建仓库 + 按需搬取 + 引用各家」 |
| **铁律 3** | ★ **必须重写** | 「不新增顶层目录」**已被违反 4 次**；换成**我们自己的结构规范**（建议：顶层目录白名单 + 新增需说明） |
| **第〇章「三条主线」** | **补**一条 | 「单源交付：运行时只有一个 MCP」—— COM 死锁是硬约束 |
| **§七 Git / Fork 规则** | ★ **必须改** | origin 语义变了（不再是「fork 前的只读锚点」）；去掉「fork 目标」；推送义务（`THIRD-PARTY-NOTICES.md`）保留并升级为**对上游 + 四家都适用** |
| **§一 验收标准** | 建议**补 A10** | 「搬进来的每一件都过一遍并入六条规则」—— 这是「按需搬取」的核心动作 |
| **§六 已知事实** | **补 4 条** | 见下 |
| **工作区章节** | **补一句** | `docs/` 相对 AGENTS.md 解析 = `D:\AI\SW\docs\`（事实 D） |
| **§十 资源速查** | **补** | `D:\AI\SW\solidpilot-salvage\`（事实 B） |
| **铁律 6** | **补一句** | 「运行时只能有一个 SolidWorks MCP」（事实 A 的理由 1） |

### 建议补进 §六「已知事实」的 4 条

| # | 事实 | 依据 |
|---|---|---|
| 24 | **运行时只能有一个 SolidWorks MCP**：多个进程抢同一 COM 连接会死锁。`Eduardof0nt` 为此实现命名互斥锁 `Local\SolidWorksMCPServer_SingleInstance_v1`；`Slacker-LLC` 写进已知限制「Two clients driving the same session at once will deadlock it.」 | 两家源码 + README |
| 25 | **上游 MCP 只包了 25 个 `scripts` 模块，本 fork 后补的 56 个一个都没进**（实测交集 = 0）⇒「我们补的能力没被 MCP 暴露」是当前最大的结构性缺口 | `mcp-server/server.py` 静态抽取 + `git diff` 对比 |
| 26 | **仓库构成**：上游原有 389 文件 / 10.1 MB；我们新增 100 文件 / 18.6 MB；改过 13 个。`mcp-server/server.py`（104 KB，45 工具的实现）是上游的、**我们一行没改** | `git diff origin/main --stat` |
| 27 | **铁律 3 已被违反 4 次**：`.api-signatures` / `tools` / `output` / `.pytest_cache` 四个顶层目录上游没有 | `git ls-tree -d origin/main` vs 实际目录 |

---

## 第 3 部分 · **必须保留**的（v1 保留的继续保留）

| 内容 | 为什么 |
|---|---|
| **铁律 1「只做缝合不做发明」** | 立身之本 |
| **铁律 2 三条实测安全约束** | `CommandInProgress` / 超时 / 收尾 —— 未抑制的模态框会永久挂起会话 |
| **铁律 4 三源互证** | 文档 + CHM + 反射；冲突时以出厂类型库为准（`FeatureFillet3` 实际 14 参 vs 文档 7 参） |
| **铁律 5「查不到就说查不到」** | — |
| **铁律 6 许可红线** | 四类许可 + Apache-2.0 的 NOTICE 义务 |
| **§一 A1–A9** | 都还成立；A9（护城河可跑实现）现在有 `拓扑优化_官方做法.md` 可依据 |
| **§六 已知事实 #1–#23** | 全部本机核实过 |
| **§九 停止条件 6 条** | 含「来源没测试又无法实测 ⇒ 标 `stitched` 不得标 `verified`」 |
| **并入六条规则** | 五统一的具体内容 |

**⚠ 特别注意**：v1 把 AGENTS.md 压到 21 KB 是好事，但**不要为了压缩而删掉 §六 已知事实**。
那 23 条是踩出来的，删了必有人重踩。**要压就压散文，别压事实表。**

---

## 第 4 部分 · 一句话交接

> 把 `D:\AI\SW\AGENTS.md` 从「补强上游 fork」改为「**自建仓库 + 按需搬取 + 引用各家**」；
> 重写第〇章与铁律 3；补事实 #24–#27；在铁律 6 与第〇章补「运行时只能有一个 SolidWorks MCP」；
> **别删铁律与 §六 已知事实**。

---

## 附录 · 想核实时去哪查

| 问题 | 去哪看 |
|---|---|
| 任务方向的原话与理由 | Hindsight 知识页 `从「补强上游 fork」转为「自建仓库 + 引用各家」` |
| 上一轮（v1）的交接 | `D:\AI\SW\docs\AGENTS-handoff.md` 的 git 历史（提交 `c7b69b5`） |
| 并入六条规则全文 | `C:\swprojects\sw-skill-fork\docs\union-conventions.md` |
| 广度地图 + 并入清单 | `C:\swprojects\sw-skill-fork\docs\union-coverage-matrix.md` |
| 四家的许可与验证口径 | `C:\swprojects\sw-skill-fork\tools\union-sources.json` |
| 抢救出的自有成果 | `D:\AI\SW\solidpilot-salvage\README.md` |
| MCP 换源的完整记录 | 工作区 git 提交 `3eba685` |
| 仓库构成数据 | `git -C C:\swprojects\sw-skill-fork diff origin/main --stat` |
