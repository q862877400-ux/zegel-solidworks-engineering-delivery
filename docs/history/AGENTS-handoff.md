# 交接包：修改 `D:\AI\SW\AGENTS.md`

> **给执行者**：你拿到的是**内容变更单**，不是草稿。原作者（另一个 AI 会话）被要求**不要动这个文件**，
> 所以本文只提供「要写进 AGENTS.md 的**事实与结构建议**」，具体措辞、排版、章节层级由你按
> AGENTS.md 的写作规范决定。
>
> **文件现状**：`D:\AI\SW\AGENTS.md`，551 行 / 34,050 字节，11 个 `##` 章节。

---

## 第 0 部分 · 你是谁、这是什么项目（必读，否则改不对）

### 0.1 项目一句话

把开源项目 [`wzyn20051216/solidworks-automation-skill`](https://github.com/wzyn20051216/solidworks-automation-skill)
（1010★，MIT）补强到「官方 SolidWorks API 全覆盖 + 集众家之所长」，最后推一个 fork。

**注意：这是「缝合」项目，不是「从零写」项目。** 铁律 1 规定：每加一个能力必须能指认出处。

### 0.2 三处路径（**这是最容易被改错的地方**）

| 路径 | 是什么 | 能改吗 |
|---|---|---|
| `D:\AI\SW\` | **AGENTS.md 所在** · DSH 工作区根 · 任务产物（草稿/日志/报告/证据） | ✅ 放产物 |
| `C:\swprojects\sw-skill-fork\` | ★ **代码工作副本**（独立 git 仓库，唯一改代码的地方） | ✅ 唯一改代码处 |
| `D:\AI\SW\AI Solidworks\官方文档\` | 官方 API 文档（CHM 解包，285 MB） | ⛔ 只读 |

**本会话新增事实**：`D:\AI\SW\` **现在也是 git 仓库了**（提交 `1f86c5d`），
`.gitignore` 排除了 398 MB（官方文档 / 反射转储 / 探索截图）。AGENTS.md 的工作区章节应反映这一点。

### 0.3 任务方向的演进（**这是本次修改的根本原因**）

```
原任务（AGENTS.md 当前写的）
  └─ 官方 API 全覆盖缝合：把 12 个程序集的官方成员全部索引
     ✅ 已达成：881 族 / 12,859 成员索引完整（防御得住的表述是
        「选定程序集官方成员清单完整 + 调用元数据与高价值能力已整合；
          可调用/运行时覆盖不完整」）

新任务（2026-09-30 用户指示，**AGENTS.md 必须改以反映**）
  ├─ 集大成：把 4 个 MIT/Apache 外部 MCP 项目的**能力广度**并入本仓库，
  │           使其**单一项目即可替代四家之和**
  ├─ 建护城河：做业界空白域（**拓扑优化**，经核实全网无工程实现）
  └─ 统一成「正规军」：不搞大杂烩 —— 命名/单位/选择/验证等级/出处**五统一**
```

---

## 第 1 部分 · 必须写进 AGENTS.md 的**新事实**（对方不可能知道）

### 事实 A · 四家外部 MCP 项目（**§4.2 项目表必须加**）

本会话克隆到 `C:\swprojects\` 并逐项核实（**读真实 LICENSE 文件，不采信 README 徽章**）：

| 仓库 | 工具 | 许可 | 测试文件 | 它自己声明跑过的环境 |
|---|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | **187** | **MIT** | **0 个** | **未声明** |
| `andrewbartels1/SolidworksMCP-python` | 128 | **MIT** | 147（7 live） | 未声明（README 自述 under active construction） |
| `vespo92/SolidworksMCP-TS` | 103 | **MIT** | 7（0 live） | 未声明 |
| `Slacker-LLC/solidworks-mcp` | 92 | **Apache-2.0** | 2（1 live） | **SW 2026 SP3.2 简体中文** |

**⚠ 三条必须写进去的警示：**

1. **工具最多的那个（187）测试文件数为 0** —— 它的 README 写「✅ Verified on SolidWorks 2024」，
   但仓库里没有任何测试文件。**「README 说验过」≠「验过」。**
2. **四家里只有 `Slacker-LLC` 声明全工具真机跑过**，且它是最少的（92）。
3. **`Slacker-LLC` 是 Apache-2.0** ⇒ 可抄，但**必须保留 `NOTICE`（`Copyright 2026 JIALE LIU`）
   并声明改动了哪些文件**。**这会在推送 fork 时产生硬性义务 —— `THIRD-PARTY-NOTICES.md` 目前尚未创建。**

### 事实 B · 五家的域覆盖矩阵（本会话实测）

```
              会话  参考  草图  尺寸  零件  曲面  钣金  焊件  模具  装配  工程图  检查  仿真  外观  宏  高级
Eduardof0nt    14    3    26    6    23   11   10    5     3    13    18    11    3    10    4    0
andrewbartels1 22    3    15    2    11    0    0    0     0     7    18     3    0     1   22    0
vespo92        10    0    16    6     3    1    1    0     0     4    15     7    1     3   21    1
Slacker-LLC     7    3    20    2    13    0    0    0     0     3    17     6    0     2    0    0
本仓库           7    0     0    1     1    2    0    0     0     6     3     2    2     4    1    3 ★
                                                                                              ↑ 唯一独有
```

**域定义**（去重归一后 384 个操作）：
`会话/文档` `参考几何` `草图` `尺寸/约束/参数` `零件特征` `曲面` `钣金` `焊件` `模具`
`装配` `工程图` `检查/测量` `仿真/Motion` `外观/材质` `宏/自动化` `高级/专项`

**★ 关键观察**：`高级/专项`（拓扑优化 / DFM / Costing / PDM / 路由 / DimXpert / GD&T）
**是唯一「四家全空、只有本仓库有」的域**。其余 15 个域本仓库都落后。

### 事实 C · 我先前说错、已被推翻的两个结论（**别把它们写进 AGENTS.md**）

1. ❌ 「Slacker-LLC 的 92 个工具就够用」 —— **错**。那是它作者对「零件建模」的口径；
   它的 92 个里**仿真/动画/拓扑/钣金/焊件/公差全是空的**。
2. ❌ 「焊件/模具/曲面/钣金/公差/仿真 全网没人做」 —— **错**（我第一次只扫了本地 5 个项目）。
   上网核实后发现 `Eduardof0nt` 187 个工具覆盖了其中大部分。

**✅ 经核实**真正**全网空白**的只有三个：
- **拓扑优化** —— `andrewbartels1` 明确列在 "Not Yet / Simulated"（"Simple Topology Optimization via SimulationXpress etc."）
- **动画导出（AVI）** —— Motion Study *创建*有人做，*出片*没搜到
- **Costing** —— 全网没搜到自动化实现（PDM 被 `Eduardof0nt` 的 Contributing 明确列为 missing）

### 事实 D · 「草图必须完全定义」这条纪律**别人有实现**

我先前说「全仓 0 命中」（那是**我们仓库**，正确），但据此推断「全网没人做」是错的。
`andrewbartels1`（MIT）有真正实现且带测试：

```
src/solidworks_mcp/adapters/solidworks/sketch.py:2135
    _check_sketch_fully_defined_impl(adapter, sketch_name)
    多探针：ISketch.IsFullyConstrained (SW 2018+) / ISketch.GetStatus / ISketch.FullyDefined
    经 _probe_to_flag 归一 bool/int/float/string
    返回 {sketch_name, fully_defined, state, source_api}
tests: test_check_sketch_fully_defined_variants
       test_check_sketch_fully_defined_feature_fallback_and_over_defined_count
       test_check_sketch_fully_defined_handles_textual_probe_values
```

**本仓库目前没有这条纪律**（全仓 grep `完全定义|fully defined|欠定义` = 0 命中）。
它被 `andrewbartels1` 接进了 `checkpoint_service` 和 `parameter_repair_service` —— 值得借鉴。

### 事实 E · 本会话新产出的文件（**AGENTS.md 应指向它们**）

在代码副本 `C:\swprojects\sw-skill-fork\`：

| 文件 | 是什么 |
|---|---|
| `docs/union-conventions.md` | ★ **并入规范**：六条可机器校验的规则（见下） |
| `docs/union-coverage-matrix.md` | ★ **A 级广度地图**（生成物）：域 × 来源矩阵 |
| `tools/build_union_sources.py` | 扫描外部项目产出去重来源清单 |
| `tools/build_union_map.py` | 生成上面的地图 |
| `tools/union-sources.json` | 来源数据（含每家的许可与验证口径） |
| `scripts/check_union_conventions.py` | ★ **规范门禁**，已接进 `release_check.py` |

**六条规则**（`docs/union-conventions.md` 全文，AGENTS.md 只需指针 + 摘要）：
```
1 命名   统一 solidworks_<域>_<动作>
2 单位   长度 _mm 结尾、角度 _deg；转换只在边界做一次（脚本 sw_connect.mm()）
3 选择   必须声明式 selection，禁止裸坐标（含自动设 mark）
4 等级   五级 verified / source_verified / stitched / indexed / not_implemented
         ★ 禁止把 source_verified 写成 verified —— 那是转述别人的话
5 出处   每条并入条目带 provenance{repo(owner/repo), license, files, upstream_verified}
6 失败要响 建特征必须 EditRebuild3 + GetWhatsWrong2；禁止静默成功
```

---

## 第 2 部分 · 逐章节改动建议

> **这不是必须照做**，是「哪些地方会与事实冲突」的清单。请按 AGENTS.md 规范决定怎么写。

| 章节（当前行号） | 建议 | 原因 |
|---|---|---|
| `## ★ 工作区`（L13） | **补**：`D:\AI\SW` 现已是 git 仓库（`1f86c5d`），`.gitignore` 排除 398 MB | 新事实 |
| `## 〇、一句话任务`（L39） | ★ **必须重写** | 任务从「全覆盖」升级为「集大成 + 护城河」 |
| `## 一、验收标准`（L49） | ★ **必须重写** | A1–A8 是旧任务的判据；新任务需要新判据（建议含：五统一门禁通过、地图可生成且与来源同步、每个并入条目带 provenance） |
| `## 二、六条铁律`（L64） | **补**：铁律 1 的「合法来源」加四家外部 MCP；铁律 6 的许可表加 Apache-2.0 行及其 NOTICE 义务 | 新素材 |
| `## 三、上游仓库结构`（L131） | **补**：新增 `tools/` 目录与 `docs/union-*.md` | 新增文件须落在上游结构里（铁律 3） |
| `### 4.2 其它项目`（L252） | ★ **必须改**：现写「19 个目录 = 18 个项目」，实际已克隆 4 家新项目 | 事实 B 表 |
| `### 4.3 来源标注制`（L309） | **考虑补**：`provenance` 字段格式（规则 5） | 与新的机器校验对齐 |
| `## 五、工作方法（四步法）`（L326） | ★ **必须改** | 原四步是「建全景 → 对差 → 缝合 → 报告」；新任务多了「并入外部项目 → 归一 → 标验证等级 → 实测」 |
| `## 六、已知事实`（L401） | ★ **必须补**：事实 A/B/C/D/E | 这是防止后来者重蹈我覆辙的关键 |
| `## 七、Git / Fork 规则`（L427） | **补**：Apache-2.0 的 NOTICE 义务；`D:\AI\SW` 也是仓库 | 推送前置条件 |
| `## 八、智能体团队分工`（L460） | 可能需调整 | 集大成工作量大，分工维度可能从「按域」变成「按来源 + 按域」 |
| `## 九、停止条件`（L491） | 考虑补一条 | 「需要并入 AGPL/GPL 代码才能补齐 → 停」已有；可加「来源无测试且我们无法实测 → 标 stitched，不得标 verified」 |
| `## 十、本地资源速查`（L502） | ★ **必须改**：加四家新克隆路径、两个新工具脚本 | 路径表 |
| `## 十一、开工第一句话模板`（L541） | ★ **必须改** | 任务变了 |

---

## 第 3 部分 · **必须保留**的（不要顺手删掉）

| 内容 | 为什么不能删 |
|---|---|
| **铁律 1「只做缝合不做发明」** | 这是整个项目的立身之本 |
| **铁律 2 的三条实测安全约束** | 先置 `CommandInProgress`、每个 COM 调用设超时、收尾必做。**未抑制的模态框会永久挂起会话** —— 这是外部实证 |
| **铁律 4「签名以官方文档为准，两套源都要用」** | `C:\swapi` 与 CHM 各管一头；且**官方文档与出厂类型库不一致**（见下） |
| **铁律 5「查不到就说查不到」** | — |
| **铁律 6 许可红线** | AGPL/GPL/无许可**只读思想** |
| **§六 已知事实的 #1–#17** | 全部本机核实过，删了就有人重踩 |
| **§九 停止条件** | 4 条红线（含推送需批准） |

**⚠ 一条与官方文档有关的新证据**（本会话从 `Slacker-LLC` 的 README 读到，
它为此专门写了 `tools/tlb_probe.py` 直读类型库）：

> **`FeatureFillet3` 在这台机器的类型库里吃 14 个参数，官方文档写 7 个。**

这**强化**了铁律 4 —— 但方向要写对：不是「文档不可信」，而是
**「文档 + 反射 + CHM」三者互证，冲突时以出厂类型库的反射为准**（这一口径与
项目记忆里「2026-09-29 起反射是权威成员清单来源」一致）。

---

## 第 4 部分 · 一句话交接

> 把 `D:\AI\SW\AGENTS.md` 从「官方 API 全覆盖缝合」的任务书，
> 改写为「集四家 MIT/Apache MCP 项目之广度 + 建护城河」的任务书；
> 补进事实 A–E；把五统一规范与规范门禁写成可执行的验收判据；
> **别删铁律与 §六 已知事实**。

---

## 附录 · 想核实时去哪查

| 问题 | 去哪看 |
|---|---|
| 任务方向的原话 | Hindsight 知识页 `集大成：把 4 个 MIT/Apache 项目的广度并入本仓库 + 拓扑优化护城河` |
| 原任务的完整状态 | Hindsight 知识页 `SolidWorks skill 官方 API 全覆盖缝合` |
| 五统一规范全文 | `C:\swprojects\sw-skill-fork\docs\union-conventions.md` |
| 广度地图 | `C:\swprojects\sw-skill-fork\docs\union-coverage-matrix.md` |
| 四家的许可与验证口径 | `C:\swprojects\sw-skill-fork\tools\union-sources.json` |
| 四家源码 | `C:\swprojects\{Eduardof0nt,andrewbartels1,SolidworksMCP-TS,Slacker-LLC}\` |
| 本会话的工作日志 | `D:\AI\SW\` 的 git 历史（`1f86c5d` → `fdf4b27`） |
| 代码副本的提交 | `C:\swprojects\sw-skill-fork\` 的 git 历史（最新 `93826ae`） |
