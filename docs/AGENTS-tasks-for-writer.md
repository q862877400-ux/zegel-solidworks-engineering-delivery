# 要你做的三件事（执行方 → 改 AGENTS.md 的对话）

> 分工判据一句话：**凡需要知道 SolidWorks 或我们仓库里有什么的判断归我；
> 凡需要知道「怎么写才不腐坏、才合规」的判断归你。**
>
> 下面三件都落在你的判据范围内。**第 2 件是主要的。**

---

## 任务 1 · 改 §一 末尾那两行指针（立刻可做）

**现状**（你上一轮定的落点）：

```
进度与下一步的真相在 `docs/union-coverage-matrix.md` 第五节的「并入清单」（生成物，
随并入更新）；未完成的条目按 `level` 标 `stitched`。
```

**问题**：我实测了那一节 —— 它是**按域的缺口清单**，回答「每个域缺什么、从哪抄、
该来源声明跑过没有」。关键词扫描：**已完成 / 未开始 / 下一步 / 阶段 / A 级 / B 级 六项全无**。
**指过去之后我仍然读不出该从哪继续。**

**建议改成**：

```
进度与下一步看 `capabilities.yaml`（manifest：每条带 `level` 与 `provenance`）——
状态由清单承载，不写进本文件。
`docs/union-coverage-matrix.md` 第五节的「并入清单」是**缺口地图**（每域缺什么、从哪抄、
该来源验证过没有），不是进度。
```

**依据是你自己引的那句的后半句**：

> Status rots; **the repo layout and package manifests carry it**.

manifest 就是 `capabilities.yaml`。现在它只有 28 条、还是旧三级 `level`
（`{verified: 8, pilot: 19, not_implemented: 1}`）⇒ **状态无处可放，这才是根因。**

---

## 任务 2 · 给 `capabilities.yaml` 出 **schema 提案**（主要）

**这一件的边界**：你设计**怎么表达**；我填**每条是什么**。
你不需要知道任何 SolidWorks 术语 —— 下面把数据形状给你了。

### 2.1 这个文件是什么

上游自带的「**能力真源**」（manifest）：`原子操作 → 后端映射`。
它**本来就是清单性质的**，所以状态放这里**不违反 slop 那条**（那条针对的是散文里的状态注解）。

### 2.2 现在它长什么样（你要**兼容**它）

```
顶层键: schema_version · verified_versions · backend_schema_version
        · backend_catalog · operation_routes · capabilities
条目数: 28
每条字段: id · label · level · backends · verified_versions
          · dependencies · limitations · allowed_modes
```

一条完整样例（最短的那条）：

```json
{
  "id": "requirements_planning",
  "label": "需求分析与工程规划",
  "level": "verified",
  "backends": ["local-agent"],
  "verified_versions": [],
  "dependencies": ["python"],
  "limitations": ["关键尺寸、公差、载荷和安全参数仍需人工确认"],
  "allowed_modes": ["interactive", "reviewed"]
}
```

### 2.3 schema 要新增/改动的两处

**(a) `level` 从旧三级迁到新五级**

```
旧（现在）:  verified | pilot | not_implemented        ← pilot 口径不清（「跑过」还是「写了」？）
新（要求）:  verified | source_verified | stitched | indexed | not_implemented
```

含义（`docs/union-conventions.md` 规则 4 定的）：

| level | 含义 | 证据要求 |
|---|---|---|
| `verified` | **我们自己真机跑过** | 非空 `evidence` + `verified_versions` |
| `source_verified` | 来源声明跑过，我们**未复现** | 引用其声明 |
| `stitched` | 代码已并入，**从未运行** | 记来源文件 |
| `indexed` | 只有官方成员索引，**无实现** | 记官方接口族 |
| `not_implemented` | 明确不做 | **必须写原因** |

**兼容问题（要你决定）**：现有 19 条 `pilot` 怎么迁？我倾向「按实际证据判」——
但**哪些算有证据是业务判断，归我**；你要定的是**迁移形态**（原地改值？加 `level_legacy` 保留？双写？）。

**(b) 新增 `provenance` 字段**（规则 5 的载体）

```yaml
provenance:
  - repo: Slacker-LLC/solidworks-mcp      # owner/repo 全名，不只写目录名
    license: Apache-2.0
    files: ["sw_feature.py"]
    upstream_verified: "SW 2026 SP3.2"    # 来源自己声明的验证环境，没有就留空
```

### 2.4 数据形状（你不懂业务，所以照抄这个设计）

**要登记的操作：并集去重后 349 个，按 16 个域分布**

| 域 | 操作数 | 域 | 操作数 |
|---|---|---|---|
| `sketch` 草图 | 77 | `appearance` 外观/材质 | 16 |
| `drawing` 工程图 | 68 | `param` 尺寸/约束/参数 | 16 |
| `other` 未归类 | 61 | `surface` 曲面 | 12 |
| `session` 会话/文档 | 53 | `sheetmetal` 钣金 | 11 |
| `feature` 零件特征 | 50 | `refgeom` 参考几何 | 9 |
| `macro` 宏/自动化 | 47 | `weldment` 焊件 | 5 |
| `assembly` 装配 | 27 | `simulation` 仿真/Motion | 4 |
| `inspect` 检查/测量 | 27 | `mold` 模具 | 3 |

**四家来源已有的字段**（`tools/union-sources.json`，**这决定了 level 能自动判到哪一级**）：

| 来源 | 许可 | 工具数 | 操作数 | `declared_verified` |
|---|---|---|---|---|
| `Eduardof0nt/Solidworks-MCP-Server` | MIT | 187 | 178 | `""`（**未声明**） |
| `andrewbartels1/SolidworksMCP-python` | MIT | 128 | 121 | `""`（未声明） |
| `vespo92/SolidworksMCP-TS` | MIT | 103 | 98 | `""`（未声明） |
| `Slacker-LLC/solidworks-mcp` | Apache-2.0 | 92 | 89 | `"SW 2026 SP3.2 简体中文"` |

### 2.5 ⚑ 一个对 schema 设计有影响的发现

**五级里有四级可以由数据/规则自动判定，只有 `verified` 必须人工标：**

| 条件 | level | 谁能判 |
|---|---|---|
| 我们有实现 **且我们真跑过** | `verified` | **只有我**（要运行证据） |
| 来源 `declared_verified` 非空 + 我们抄了 | `source_verified` | 可自动 |
| 我们抄了但没跑 | `stitched` | 可自动 |
| 只有官方成员索引 | `indexed` | 可自动 |
| 明确不做 | `not_implemented` | 业务判断（我） |

**⇒ 这意味着 `capabilities.yaml` 应该是「生成物 + 人工标注」混合，不是纯手写。**
**schema 设计要考虑这一点** —— 比如加一个 `generated: true/false` 或
`level_source: "auto" | "manual"` 之类，让「哪几条是人标的」一眼可辨。
**这是我提请你注意的，具体怎么表达归你。**

### 2.6 schema 要满足的约束（都是你判得了的）

1. **兼容现有 28 条** —— 别破坏 `release_check.py` 里对 `capabilities.yaml` 的校验
   （它检查：ID 无重复、条数 ≥10）
2. **可生成** —— 状态要能由 `tools/build_union_map.py` 一类生成器刷新，不是手抄
3. **不腐坏** —— 状态只进这个清单，不进任何散文
4. **可校验** —— `scripts/check_union_conventions.py` 要能查它
   （现在规则 4/5 的校验已经指向 `level` 与 `provenance`）

---

## 任务 3 · 复审我填的内容（等我的，后续）

我填完 349 条之后，请你复审：

- 有没有违反 `docs/union-conventions.md` 规则 4/5 的形态
- **有没有把 `stitched` / `source_verified` 写成 `verified`**（A7 禁词，实测 0 命中是判据）
- `provenance` 的 `repo` 是否都是 `owner/repo` 全名、`license` 是否在白名单

**形态与合规归你；「这条到底跑没跑过」归我。**

---

## ❌ 明确不要你做的

| 别做 | 为什么 |
|---|---|
| **不要填 349 条各自的 `level`** | 你判不了「我们仓库里有没有这个实现」「我们跑没跑过」。**填错会导致把 `stitched` 标成 `verified`，直接违反 A7。** |
| **不要动 `C:\swprojects\sw-skill-fork\`** | 那是代码副本，归我。你的产出以**提案/文本**形式给我，我落地 |
| **不要把「当前进度」写进 AGENTS.md 散文** | 你已经判对了这件事，我认。状态去 manifest |

---

## 附 · 我这边同时在做

我先把 349 个操作按域 + **可自动判定的四级 level** 生成出来（第 2.5 节那张表），
**给你当 schema 的输入** —— 这样你的 schema 是照着真实数据形状设计的，不是凭空想的。

**你出了 schema 提案我就照它填。**
