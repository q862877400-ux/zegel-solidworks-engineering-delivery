# capabilities.yaml schema 提案

**本文件定四件事**：`level` 与 `provenance` 的形状、枚举、必填性，以及把这些约束变成门禁的机判规则。

**业务取值归执行方**：这条能力到底跑没跑过、来自哪个来源、某操作是否真的不做，都不由本提案决定，末节单列。

**输入**：`C:\swprojects\sw-skill-fork\capabilities.yaml`；迁移前数据里出现过的 `level` 只有三个值（按文本计数 `verified` 8 / `pilot` 19 / `not_implemented` 1），`provenance` / `evidence` / `commit` 三个字段 0 处。

## 一 迁移形态：原地改值 + bump `schema_version`

**裁断**：`level` 原地改值，`capabilities.yaml` 的 `schema_version` 由 `"1.0"` 升到 `"2.0"`，不做双写、不加 `level_legacy`。

**理由一（一个事实两个家就是腐坏的起点）**：留一份旧值就是给同一事实安第二个家，两份值必然分叉；旧值一旦不再被任何门禁读取就腐坏，这与官方 slop 那条同源。

**理由二（历史的家在提交里）**：迁移过程由 `git log -p capabilities.yaml` 回溯，数据里不必再存第二份历史。

**理由三（默认方向必须保守）**：旧 `pilot` 无运行证据时一律迁 `stitched`（代码已并入、从未运行）；把 `stitched` 误标 `verified` 直接违反 A7 与 `docs/union-conventions.md` 规则 4，低报只是保守。升级到 `verified` / `source_verified` 必须由执行方补证据。

| 迁移前取值 | 迁移后默认取值 | 说明 |
|---|---|---|
| `verified` | `verified` | 我们自己真机跑过；仍要满足第四节的硬约束 |
| `pilot` | `stitched` | 口径不清的旧值（「跑过」还是「写了」），无运行证据即按「已并入、从未运行」落地 |
| `not_implemented` | `not_implemented` | 明确不做，原因写在 `limitations` |
| `reference_only` | `indexed` | 旧枚举里的残留值（不在当前数据里）；迁移后同样不得再作为合法值 |

**枚举恰好五个**：`verified` / `source_verified` / `stitched` / `indexed` / `not_implemented`；含义沿用 `docs/union-conventions.md` 规则 4 与 `docs/AGENTS-tasks-for-writer.md` 的 2.3 节，本提案不改含义，只钉形状。

| level | 含义 | 证据要求 |
|---|---|---|
| `verified` | 我们自己真机跑过 | 非空 `evidence`；`backends` 含 CAD 后端时另要非空 `verified_versions` |
| `source_verified` | 来源声明跑过，我们未复现 | 带 `upstream_verified` 的 `provenance` |
| `stitched` | 代码已并入，从未运行 | 外部来源并入的写 `provenance.files`；自研未运行的不强制任何字段 |
| `indexed` | 只有官方成员索引，无实现 | 记官方接口族，写在 `evidence` |
| `not_implemented` | 明确不做 | `limitations` 里写原因 |

**载体必须留在 JSON 语法内**：这个文件的读取方都用 `json.loads` 解析（`scripts/capabilities.py` 的 `load_capabilities`、`scripts/check_union_conventions.py` 的 `check_capabilities_levels`、`scripts/release_check.py` 的 `run_release_check`、`scripts/validate_skill.py` 的清单校验），扩展名是 `.yaml` 但内容不得引入锚点、多行标量或注释。

**`schema_version` 是另一个文件的另一个事实**：`tools/union-sources.json` 有它自己的 `schema_version`，由 `check_union_conventions.py` 的 `check_sources` 钉在 `"1.0"`；本次只动 `capabilities.yaml` 的那一个。

### 1.1 同批必须一起改的地方

| 位置 | 现在写的 | 为什么必须同批 |
|---|---|---|
| `scripts/capabilities.py` 的 `VALID_LEVELS = {"verified", "pilot", "reference_only", "not_implemented"}` | 运行时逐条校验 `level`，不在集合即 `raise ValueError("能力清单条目无效")` | 新五级一落盘，`load_capabilities()` 立刻抛错；`backend_router.py`、`sw_capability_probe.py` 与桌面应用全部读不到清单 |
| `scripts/check_union_conventions.py` 的 `if lv not in LEVELS and lv != "pilot"` | 迁移期的 `pilot` 豁免 | 迁完不删豁免，`pilot` 仍是合法值，枚举实际是六个 —— 双写换一种形式回来 |
| `tests/test_cad_reliability.py` 的 `test_capability_manifest_marks_unverified_workflows` | 逐条断言 7 个 id 的 `level == "pilot"`（`external_spur_gear_geometry`、`parameter_updates`、`custom_properties_and_bom`、`pack_and_go`、`configurations_and_design_tables`、`sheet_metal`、`weldments`） | 这 7 条迁 `stitched` 后测试立刻红 |
| `tests/test_sw_capability_probe.py` 的 `test_advanced_interfaces_do_not_inherit_unrelated_verified_levels` | 断言 `surface_modeling` / `mold_tools` / `routing` 的 `implementation_status == "pilot"` | 同上 |
| `docs/union-conventions.md` 规则 4 的等级表 | 写的就是新五级 | 枚举的散落副本，迁完要与数据一致（现在一致） |
| 使用旧枚举值的实现与测试（执行方实测 2026-10-01：22 个文件 / 49 处 ＝ 9 个实现 + 13 个测试）| 大量断言直接比旧字符串（例：`test_cad_reliability.py` 断言 7 个 id 的 `level == "pilot"`；`test_sw_capability_probe.py` 断言 `implementation_status == "pilot"`）| 本表上两行只点到其中 2 个测试文件；实际有 13 个测试文件会红，逐条按业务判该断言什么（归执行方）。口径：在代码副本全仓按五个旧枚举值 grep 命中的文件数，复跑命令由执行方补录 |

### 1.2 `pilot` 的迁移：把「证据强度」与「授权」拆开

`pilot` 不是口径不清：它同时编码了两个事实 —— 「跑了，但证据不足以无人值守」与「不许无人值守」。新五级只拆开了前者。裁断走选项 A。

1. 19 条 `pilot` 中有 `verified_versions` 的 13 条迁 `verified`（它们跑过，这是事实）；同批必须为这 13 条补 `evidence` —— 可以是「跑过它的命令或脚本名 + 结果摘要」，不要求重新跑一遍，缺则 B4 立刻红。
2. 另 6 条（`verified_versions` 为空）迁 `stitched`。
3. `allowed_modes` 的定值域扩为 `interactive` / `reviewed` / `unattended`；原 8 条 `verified` 补 `unattended`，原 19 条 `pilot` 不补。
4. `unattended_allowed()` 从「看 `level`」改为「看 `allowed_modes` 含不含 `unattended`」，并同批改它的全部调用点与相关测试文件。
5. **迁移必须附一条等价性验收测试**：`unattended_allowed()` 为真的 capability_id 集合，迁移前后逐条相同。这是本次改动的验收判据，不是可选项。
6. 新不变量见 §五 的 R11。

不采纳另两个选项：保留第六级 `pilot` 会把两个事实继续焊在一个字段里（那正是它腐坏的根源）；把 13 条一律迁 `stitched` 会让同一份数据里同时出现「跑过 2024/2026」与「从未运行」—— 那不是保守，是错报。

## 二 `provenance` 的形状与必填性

**必填规则**：`level == source_verified` ⇒ `provenance` 必须非空；自研但未运行的 `stitched` 允许为空（它没有来源仓）；`indexed` 的出处写在 `evidence` 里（官方接口族），不是 `provenance`。

| 字段 | 必填性 | 形状 |
|---|---|---|
| `repo` | 必填 | `owner/repo` 全名，不写克隆目录名 |
| `license` | 必填 | 归一化后落在白名单内 |
| `files` | 必填 | 非空字符串数组，路径相对该来源仓根 |
| `upstream_verified` | 必填（可为空串） | 来源自己声明的验证环境原文；它没声明就是空串 |
| `commit` | 可选 | 字符串，该来源仓的提交哈希 |
| `tag` | 可选 | 字符串，该来源仓的标签 |

**为什么加 `commit` / `tag`**：不带可复现锚点的 provenance 事后核不了 —— 来源仓会前进、改名、删除，`files` 里的路径只在某个提交上才成立；有就写，没有留空。

**白名单与归一化**：白名单就是 `MIT` 与 `Apache-2.0` 两个值，比对前先去掉全角括号里的附注（`scripts/check_union_conventions.py` 的 `COPYABLE_LICENSES` 与 `check_sources` 用的是同一手法）；本项目自身是 MIT，不作为 provenance 来源。

**唯一的例外**：`angelsix/solidworks-api` 的 `References/` 是 MIT 仓里被点名的那一个例外（文件属达索，只许原样用于 SolidDNA），这类文件不得进 `files`，依据是 `docs/sources.md` 的许可判定表与其后的例外段。

## 三 生成器是校验者，不是写者

**裁断**：`tools/build_union_map.py` 不回写 `capabilities.yaml`；它额外产出审计报告 `docs/union-level-audit.md`，由 `scripts/check_union_conventions.py` 当门禁读。

**理由**：手写清单与生成物互相覆盖时，谁也说不清当前真相在哪；官方对生成物的一贯口径是「生成物只由生成器写、人不手改」——`docs/union-coverage-matrix.md` 顶部就这么写，门禁用「重跑一遍、与提交内容逐字比对」强制它。反过来让生成器改写手写清单，等于把人工标注静默覆盖掉。

**审计报告的形态**：生成物，顶部写明「本文件是生成物」，与地图同一新鲜度口径。

| 列 | 内容 |
|---|---|
| `id` | 能力 id |
| `人标 level` | `capabilities.yaml` 里的值 |
| `自动 level` | 生成器按 `tools/union-sources.json` 与覆盖数据算出的值 |
| `判定` | `ok` / `高报` / `缺证据` / `自动不可判` |
| `依据` | 判这一行用了哪些字段（`declared_verified`、来源是否覆盖、实现文件是否存在） |

**核心不变量是不得高报**：五级按证据强度排序 `verified` > `source_verified` > `stitched` > `indexed`，`not_implemented` 单列；审计只允许人标不高于自动，人标高于自动即红。

**为什么高报比低报严重**：`level` 不只是文档，它是操作开关 —— `scripts/capabilities.py` 的 `unattended_allowed()` 与 `scripts/sw_capability_probe.py` 的 `ready_for_unattended_use` 都只认 `verified`；高报一条等于解锁一条无人值守执行路径，这正是 A7 要禁的事。

**`not_implemented` 不参与高低比较**：它表示「明确不做」，是业务判断而非证据强度；任一侧是 `not_implemented` 的行只登记、不判高低，它的原因约束由第四节管。

**自动不可判也留痕**：生成器算不出自动 level 的行写成 `自动不可判`，只登记、不算红 —— 机器给不出结论的地方不冒充结论，但这一行必须在报告里搜得到。

**不设 `level_source: auto|manual`、也不设 `generated: true|false`**：哪几条是人标的可由「`verified` 必带非空 `evidence`」一眼看出（有 `evidence` 就是我们自己跑的）；再加一个来源字段就是给同一事实安第二个家。

**新鲜度照地图的既有做法**：`check_union_conventions.py` 的 `check_map_fresh` 已经用「重跑生成器、逐字比对产物」防止手改或忘记重生成；审计报告加同一条，报告与数据不同步即红。

## 四 两条硬约束

**`verified` ⇒ `evidence` 非空；且 `backends` 含 CAD 后端时 `verified_versions` 非空**。

**`evidence` 的形状**：非空字符串数组，一条一行「命令 + 结果摘要」，与 `limitations` 同型，不新造类型。

**与现有门禁的差别**：`scripts/check_union_conventions.py` 的 `check_capabilities_levels` 现在只在 `backends` 含 CAD 后端时才要求 `verified_versions`（`is_cad` 判断），理由是 `requirements_planning`（`local-agent`）与 `geometry_and_delivery_review`（`local-python`）本来没有 SolidWorks 版本可说。

**CAD 后端的判据（机判照此实现）**：`backends` 里任一项以 `solidworks` 或 `autocad` 开头 —— 与 `check_capabilities_levels` 现行的 `is_cad` 同一口径。`requirements_planning`（`local-agent`）与 `geometry_and_delivery_review`（`local-python`）不满足它 ⇒ 这两条只要求 `evidence`，不要求 `verified_versions`。给代理层与本地 Python 层填「SolidWorks 版本」是给字段安它没有的含义，与本提案反对的「一个事实两个家」同源。

**`not_implemented` ⇒ 必须写原因**：原因写在已有字段 `limitations` 里，不新起字段 —— 它本来就是记「这条为什么不能用」的地方，`check_capabilities_levels` 也已经在查它。

## 五 机判规则表

**前置**：文件必须能被 `json.loads` 解析，否则下面每条都无从落地。

| 规则号 | 机判内容 | 失败信息 |
|---|---|---|
| R1 | `schema_version` 等于本提案定的新值 `"2.0"` | `capabilities.yaml 的 schema_version 不是 "2.0"（读到 <值>）—— 五级枚举与 provenance 必填性挂在 2.0 上` |
| R2 | 每条 `level` ∈ 五值枚举；且 `scripts/capabilities.py` 的 `VALID_LEVELS` 与 `scripts/check_union_conventions.py` 的 `LEVELS` 两个副本与枚举同集合（`pilot` / `reference_only` 不得再合法） | `能力 <id> 的 level=<值> 不在五级枚举内` / `枚举副本不一致：capabilities.py=<集合>，check_union_conventions.py=<集合>` |
| R3 | `id` 全局唯一，且是稳定 slug（`^[a-z][a-z0-9_]*$`）；改 id 会断掉 `operation_routes[].capability_ids` 的引用与既有 provenance 指向 | `能力 id 重复：<id>` / `能力 id 不是稳定 slug：<id>` |
| R4 | 条数 ≥ 10 | `能力清单 ID 重复或数量不足`（沿用 `scripts/release_check.py` 的现有断言与文案） |
| R5 | `verified` ⇒ `evidence` 非空 且 `verified_versions` 非空（第四节） | `能力 <id> 标 verified 但 evidence 为空` / `能力 <id> 标 verified 但 verified_versions 为空 —— 「跑过」必须有版本证据` |
| R6 | `level == source_verified` ⇒ `provenance` 非空；任何带 `provenance` 的条目，其 `repo` 必须是 `owner/repo`、`license` 在白名单、`files` 非空、`upstream_verified` 字段必须存在（可为空串） | 外部来源派生的能力没有出处，或出处形状不合法 |
| R7 | `not_implemented` ⇒ `limitations` 非空 | `能力 <id> 标 not_implemented 但没写原因` |
| R8 | 审计（第三节）：`docs/union-level-audit.md` 出现一行 `高报` 即红；报告重生成后与提交内容不一致也红 | `能力 <id> 的人标 level=<人标> 高于自动算出的 <自动>（依据 <字段>）—— 不得高报` / `union-level-audit.md 与数据不同步 —— 重跑 tools/build_union_map.py 并提交` |
| R9 | `provenance.files` 为非空数组；`commit` / `tag` 可省略或为空串，若出现必须是字符串 | `能力 <id> 的 provenance.files 是空数组` / `provenance.commit 不是字符串：<值>` |
| R10 | `provenance.files` 不得落在 `angelsix/solidworks-api` 的 `References/` 下（第二节的例外） | `能力 <id> 的 provenance 引用了 angelsix 的 References/ —— 那是达索财产，只能原样配 SolidDNA 用` |
| R11 | `allowed_modes` ⊆ {`interactive`, `reviewed`, `unattended`}；`level != verified` ⇒ 不含 `unattended`；授权真源是 `allowed_modes` —— 任何按 `level` 推断无人值守授权的写法都违规（实测该判据在代码里有 4 条路径，只改 `unattended_allowed()` 抓不全） | 非 `verified` 的能力带了无人值守授权，或出现第二个授权真源 |

**规则落点**：R1–R3、R5–R7、R9、R10 进 `scripts/check_union_conventions.py`（已经在 `release_check.py` 里硬失败的那道门）；R4 留在 `scripts/release_check.py` 的现有断言；R8 读生成物。

**`provenance` 的触发条件（修正）**：只有「实现源自外部来源仓」的条目才要求 `provenance`；自研但未运行的 `stitched`（`dfm_checks`、`surface_modeling`、`mold_tools`、`autocad_headless_preview`、`dxf_preview_scene`、`routing`）允许为空 —— 它们没有来源仓，填一个指向本仓库的值属于给字段安它没有的含义。`indexed` 的出处是官方接口族，记在 `evidence` 里，不是来源仓的 `provenance`。将来 B 级并入产生的 `stitched` 条目由并入生成器写入 `provenance`，由审计规则把关，不靠 `level` 推断。

## 六 最小样例

**顶层键不变**：`schema_version` · `verified_versions` · `backend_schema_version` · `backend_catalog` · `operation_routes` · `capabilities`，只动 `capabilities[]` 里的条目形状。

**before**：`docs/AGENTS-tasks-for-writer.md` 的 2.2 节那条 `requirements_planning`，原样照录。

```
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

**after**：`level` 不动（它本来就是新枚举里的值，且这条是我们自研、我们跑过）；补上 `evidence` 与一个非空的 `verified_versions`；它不是来源派生，因此不给 `provenance`。

```
{
  "id": "requirements_planning",
  "label": "需求分析与工程规划",
  "level": "verified",
  "evidence": ["<我们自己的运行证据：命令 + 结果摘要>"],
  "backends": ["local-agent"],
  "verified_versions": ["<我们实际跑过的运行时版本>"],
  "dependencies": ["python"],
  "limitations": ["关键尺寸、公差、载荷和安全参数仍需人工确认"],
  "allowed_modes": ["interactive", "reviewed"]
}
```

**下面两条示范来源派生与明确不做的写法**：形状可照抄，id、来源文件与取值归执行方；第二条的来源用 `Slacker-LLC/solidworks-mcp`，因为它的 `declared_verified` 非空（`"SW 2026 SP3.2 简体中文"`），够判 `source_verified`。

```
{
  "id": "<来源派生的能力 id>",
  "label": "<中文标签>",
  "level": "source_verified",
  "backends": ["solidworks-com"],
  "verified_versions": ["2026"],
  "dependencies": ["SolidWorks", "pywin32"],
  "limitations": ["<抄进来之后仍需人工确认的点>"],
  "allowed_modes": ["interactive", "reviewed"],
  "provenance": [
    {
      "repo": "Slacker-LLC/solidworks-mcp",
      "license": "Apache-2.0",
      "files": ["sw_feature.py"],
      "upstream_verified": "SW 2026 SP3.2 简体中文",
      "commit": "<并入时该来源仓的提交哈希>"
    }
  ]
}
```

```
{
  "id": "<明确不做的能力 id>",
  "label": "<中文标签>",
  "level": "not_implemented",
  "backends": ["solidworks-com"],
  "verified_versions": [],
  "dependencies": ["SolidWorks", "对应加载项许可证"],
  "limitations": ["<为什么不做：缺许可证 / 官方 API 未暴露该数据 / 与单源运行冲突 —— 写成可核的一句话>"],
  "allowed_modes": ["interactive"]
}
```

**`provenance` 是数组**：一条能力可以由多个来源并入，每条来源一个对象；`license` 取该来源仓的真实许可（`Slacker-LLC` 是 Apache-2.0，另三家是 MIT），与 `tools/union-sources.json` 的记录一致。

## 七 不归本提案判的

**业务取值全部归执行方**：哪条能力实际跑没跑过、`evidence` 写什么、某条来自哪个来源、`provenance.files` 列哪些文件、`upstream_verified` 的原文、某操作是否真的不做（`not_implemented` 的原因）、`allowed_modes` 给哪几个模式，都由执行方定。

**本提案只定四件事**：形状（字段与类型）、枚举（五个 `level` 值）、必填性（哪些字段在哪些 `level` 下不能缺）、机判规则（第五节那张表）。

**分工判据**：凡需要知道 SolidWorks 或仓库里有什么的判断归执行方；凡需要知道「怎么写才不腐坏、才合规」的判断归本提案，由第五节的规则兜底。
