# 并入规范 —— 把五家统一成一支「正规军」

> 本文件定义**并入外部项目时必须遵守的统一规则**。
> 目的：避免并入后变成大杂烩 —— 五套命名、五套单位、五套验证口径混在一起。
>
> 配套：`capabilities.yaml`（能力真源）· `docs/union-coverage-matrix.md`（广度地图）
> · `scripts/check_union_conventions.py`（机器校验）

## 〇 为什么需要这份文件

2026-09-30 调研发现，与本项目重叠的 MCP 项目有四家，各有各的规矩：

| 项目 | 工具命名 | 单位 | 选择方式 | 验证口径 |
|---|---|---|---|---|
| **Eduardof0nt** (187) | `sw_<op>` | `_mm` 后缀 | 未声明 | README 称已验，**仓库 0 个测试** |
| **andrewbartels1** (128) | `<op>`（无前缀） | 未声明 | 未声明 | 「under active construction」 |
| **vespo92** (103) | `<op>` + 27 个 `vba_*` | 未声明 | 未声明 | 7 个测试，0 live |
| **Slacker-LLC** (92) | `<op>` | **`_mm`/`_deg` 显式** | **声明式 selection** | 全工具真机跑过 |
| **本仓库** (45) | `solidworks_<op>` / `cadstudio_<op>` | `_mm` 后缀 + `mm()` 转换 | 各自实现 | 见 capabilities.yaml |

**五套规矩 ⇒ 必须先统一，才能并入。**

---

## 一 统一的六条（每条都可机器校验）

### 规则 1 · 命名：**工具名统一 `solidworks_<域>_<动作>`**

```
✅ solidworks_sketch_create          域在前，动在后，蛇形
✅ solidworks_weldment_structural_member_add
❌ sw_create_sketch                   Eduardof0nt 风格：前缀混用
❌ createSketch                       camelCase
❌ vba_sheet_metal                    vespo92 风格：那是「生成宏」，不是「做操作」
```

**为什么统一到 `solidworks_`**：本仓库上游已有 45 个工具用这个前缀（`solidworks_connect`、
`solidworks_create_basic_part`）；`cadstudio_*` 保留给**无 SolidWorks 的 headless 路线**，
两者语义不同，不混用。

**校验**：`^solidworks_[a-z0-9_]+$` 或 `^cadstudio_[a-z0-9_]+$`。

### 规则 2 · 单位：**长度参数必须 `_mm` 结尾，角度必须 `_deg` 结尾**

```python
depth_mm: float = Field(..., description="Extrusion depth in mm.")
angle_deg: float = Field(default=90.0, description="Bend angle in degrees.")
```

**转换只在边界做一次**（`scripts/sw_connect.py` 的 `mm()`），下层一律用米/弧度。
**来源**：本仓库上游已有此约定（`width_mm` 等 102 处）；Slacker-LLC 独立采用同一约定。

**为什么必须有后缀**：COM 底层是米，模型极易把 `50`（想写 50mm）当成 50 米。
Slacker-LLC 的原话：「No tool has ever silently taken metres.」

**校验**：长度/角度类参数的 `Field(...)` 描述含 `mm` / `degrees`，且变量名带 `_mm`/`_deg`。

### 规则 2b · 单位：**读数（返回侧）也必须能机器判，且"未确证"必须说出来**

★★ **为什么补这一条**：规则 2 只管**输入侧**（形参名后缀）。★ 而实测过一次真机读数与官方文档
**对不上**（`IFace2.GetArea` 官方说平方米、真机读数是平方毫米）⇒ ★ **输出侧原先没有任何门禁** ✗

```python
# ★ 对：返回的数值字段**名字自带单位**
{"volume_mm3": 120000.0, "area_mm2": 6000.0, "centroid_mm": [50, 30, 0]}
# ★ 对：无量纲的字段**在显式白名单里**（ok / count / ratio / status / index / error / notes …）
{"ok": True, "count": 6, "status": 0}
# ★ 错：数值字段既没单位后缀、也不在白名单
{"volume": 120000.0}
```

**三条同时生效**：
1. ★★ **每个工具返回的顶层数值字段**，键名**要么带单位后缀**（`_mm` · `_mm2` · `_mm3` · `_deg` ·
   `_px` · `_s` · `_kg` · `_m2` …），**要么在无量纲键白名单里**（★ 白名单**显式列出、每条带理由**）✓
   ★ 落点是**返回出口的守卫** —— ★ 加一次即覆盖全部工具 ✓
2. ★★ **输入侧的逆向一半**：**`Param.description` 里明确出现单位词**（`mm`/`millimetre`/`inch`/
   `meter`/`degree`）⇒ ★ **名字必须带对应的 `_mm`/`_deg`** ✓
   ★（★ 原有那条只从"名字含长度词"出发，**词表有界** ⇒ ★ 不在词表里的长度词从不被查 ✗）
3. ★★ **"未确证"必须说出来**：凡返回值带 `units_verified: false` ⇒ ★ **必须同时带 `unit_caveat`** ✓
   ★ 依据**铁律 5「查不到就说查不到」** —— ★ **不许为了让返回值好看而编一个单位** ✗

**为什么不做"值里带单位字符串"**（如 `depth="20mm"`）：★ MCP **只传 JSON 值** ⇒ 值带单位就是字符串
⇒ ★ **失去类型检查**，★ 且单位**只在下游可见** ✗ ★★ 而后缀在**形参名/键名**上 ⇒ ★ **能被静态门禁强制** ✓

**官方声明与真机读数冲突时**：★ **登记进 [`docs/unit-conflicts.md`](unit-conflicts.md)**（五要素：
官方页 / 官方原话 / 真机读数 / 证据文件 / 处置）⇒ ★ 处置只许"**让失败可见**"或"**如实标注未确证**" ✓

**校验**：门禁在 `mcp-server/tool_registry.py`（输入侧）；★ 判据**一律是确定性的**（后缀名 / 白名单 /
显式表）—— ★★ **不许靠 LLM 判单位** ✓

### 规则 3 · 选择：**必须用声明式 `selection`，禁止裸坐标**

**实际形态**（★ 照代码写，见下「与文档的差异」）：

```python
#: `selection` 是**字符串选择器**（或一个 COM 对象），另配 `kind` 说明选什么
"selection": "__current_selection__"   #: 用当前选区里的第一个（**不重选**）
"selection": "index:<n>"               #: 该体上第 n 个实体（0 基；**会重选**，带越界检查）
"selection": <COM 对象>                 #: 直接 Select4 它
"kind": "EDGE" | "FACE"                #: 合法值来自 `sw_selection_spec.ENTITY_KINDS`
```

实现与入口（可 grep 核对）：

| 函数 | 作用 |
|---|---|
| `sw_selection_spec.resolve_entity(model, selector, kind, *, body_index=0)` | 解析选择器 → **已选中的实体对象** |
| `sw_selection_spec.resolve_selection(model, selector, kind, *, body_index=0)` | 同上，但**只回读选区计数**（0 表示没选中 ⇒ 调用方**不得继续**）|
| `sw_selection_spec.select_entity_by_index` / `select_object` | 按序号 / 按对象选 |
| `sw_selection_spec.entities_on_body(model, kind, *, body_index=0)` | 列出体上的实体（序号来源）|

底层把选择解析为**实体上的一点**再按 3D 坐标选（绕开 pywin32 无法 QueryInterface
`Face2`→`IEntity` 的限制），并**按 mark 分配**（多引用特征读 mark 0/1/2，不读选择顺序）。

**为什么禁止裸坐标**：侧边栏一拉、DPI 一变、几何一重建，坐标就错。
本仓库已在嘉立创 GUI 上为此吃过 12 轮返工。

**来源**：Slacker-LLC（Apache-2.0）· 其 README 明写「Exposing that to an agent is hopeless」。

#### ⚠⚠ 与文档的差异（2026-10-01 轮 218 实测核对，**本节是更正**）

本规则此前还写了下面这两条 —— ★ **代码里没有**（按铁律 5，**写明"未实现"**，不再当作既有能力）：

| 此前文档所述 | 实测 | 处置 |
|---|---|---|
| dict 形态：`{ "selection": { "edges": [4, 6, 9] } }` · `{ "face_edges": [2] }` · `{ "planes": ["front"] }` | `resolve_entity` / `resolve_selection` 接受的是**字符串选择器或 COM 对象**，**没有 dict 分支** | ★ **未实现** —— 保留为**目标形态**，不当作现状 |
| 「索引来自 `list_faces` / `list_edges` / `list_vertices` / `list_sketch_segments`」 | 这四个函数 **grep 0 命中（不存在）** | ★ **未实现** —— 现存序号来源是 `entities_on_body` |

**核查命令**（可重跑，两条都应给出"不存在"）：
```
grep -rn "def list_faces\|def list_edges\|def list_vertices\|def list_sketch_segments" scripts/
python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\scripts'];import inspect,sw_selection_spec as m;print(inspect.signature(m.resolve_entity))"
```

#### 校验（★ 只覆盖本规则三句里的**第一句**）

**已实现**：新增工具的参数 schema 里不出现裸 `x`/`y`/`z` 浮点
（`mcp-server/tool_registry.py` 的 `_BARE_COORD_NAMES`；除非该工具本身是
`*_at_point` 类且注明用途）。

**★ 第二句已补上门禁（2026-10-01 轮 218）**：
**「选择必须是声明式的」** ⇒ 判据 = **`selection` 参数的 `kind` 必须是 `str`**
（声明式选择器就是字符串；传 `float`/`int` 不是声明式选择）。
负例见 `tests/test_rule3_declarative_selection_is_enforced.py`（★ 事实 62：负例是唯一的证明）。

**★★ 第三句「按 mark 分配」静态判不了（如实记，不假称有判据）**：
那是**运行行为** —— 多引用特征读 mark 0/1/2、不读选择顺序。静态检查做不到；
它的证据**只能来自真机**。另注：`select_object` / `Select4` **不取 mark**，
多引用特征所需的 mark 目前只能由**各调用点自己传**。

> ★ 一条规则若含多个子句，要**逐子句问"机器验了哪几个"**；没验的子句不是不存在，
> 而是**在无人看守地漂移**（事实 153）。

### 规则 4 · 验证等级：**五级，写在 `capabilities.yaml` 的 `level`**

| level | 含义 | 证据要求 |
|---|---|---|
| `verified` | **我们自己真机跑过** | 有运行日志/截图，记 `verified_versions` |
| `source_verified` | **来源项目声明真机跑过**，我们未复现 | 引用其 README 原文 + 版本 |
| `stitched` | 代码已并入，**从未运行** | 记来源文件 |
| `indexed` | 只有官方成员索引，**无实现** | 记官方接口族 |
| `not_implemented` | 明确不做 | **必须写原因** |

**⚠ 这条最要紧。** 上游原有 `verified` / `pilot` / `not_implemented` 三级口径不清
（`pilot` 到底是「跑过」还是「写了」？）。新五级把「谁跑的」和「跑没跑」分开。

**禁止**：把 `source_verified` 写成 `verified`。那是**转述别人的话**，不是我们的证据。

**校验**：`level` 必须在枚举内；`level == verified` 的条目必须有非空 `evidence` 字段。

### 规则 5 · 出处：**每条并入的条目必须带 `provenance`**

```yaml
provenance:
  - repo: Slacker-LLC/solidworks-mcp      # owner/repo 全名，不只写目录名
    license: Apache-2.0
    files: ["sw_feature.py"]
    upstream_verified: "SW 2026 SP3.2"    # 来源自己声明的验证环境，没有就留空
```

**许可义务**（已核实真实 LICENSE 文件，非 README 徽章）：

| 许可 | 能做什么 | 义务 |
|---|---|---|
| **MIT** | 抄、改、商用 | 保留版权声明 |
| **Apache-2.0** | 抄、改、商用 | **保留 `NOTICE` + 声明改动过的文件** |
| AGPL / GPL | **只读思想** | 不抄代码、不抄文本 |
| 无许可 | 只读思想 | 同上 |

**⚠ Apache-2.0 的 NOTICE 义务会跟着分发走** —— 一旦入库，将来推送 fork 时必须带
`THIRD-PARTY-NOTICES.md`。

**校验**：`provenance[].repo` 必须匹配 `owner/repo`；`license` 必须在白名单内。

**⚠ 适用范围（2026-10-01 加，免得 A2 被误读成「没过」）**：
本规则约束的是**并入**的条目 —— 即「这一件能力是从别处搬来的」。
**本仓库自研的条目不需要 `provenance`**（它们没有外部出处；出处是本项目自己的官方签名依据，
写在源码的 `# ── 来源 ──` 块里）。

实测口径：`capabilities.yaml` 当前 29 条里**只有并入的那 1 条**带 `provenance`
（`mold_tools` ← `Eduardof0nt/Solidworks-MCP-Server`，MIT）。
**⇒ 判据 A2「每个并入条目带 provenance」按此读：对**并入**的条目 100% 命中即可，
不是要求 29 条全都带。** 要复核「哪些是并入的」，看源码里有没有 `# 仓库: <owner>/<repo>`
形式的来源块（`scripts/check_provenance.py` 核的就是这件事）。

**⚠ 另一个真实缺口（登记在此，不在 A2 名下）**：**「已有能力 → MCP 工具」的暴露**
（`AGENTS.md` 已知事实 25：`mcp-server/server.py` 只引用 25 个 `scripts` 模块，
本仓库后补的 61 个模块一个都没进）。评估见
[T-011](T-011-expose-capabilities-assessment.md)（真实工作量 **~120 个函数**，不是 814）。

### 规则 6 · 失败要响：**禁止静默成功**

```python
# ✅ 特征建完必查
doc.EditRebuild3()
wrong = doc.Extension.GetWhatsWrong2(...)
if wrong: raise ToolError(f"特征失败: {wrong}")

# ❌ 调用返回就当作成功
doc.FeatureManager.FeatureExtrusion3(...)
return "done"
```

**为什么**：Slacker-LLC 的实现笔记记了两条硬事实 ——
「**Most failures are silent.** SolidWorks returns null far more often than it raises.」
「**Return values lie.** `SketchTrim` returns `False` on success.」

本仓库也踩过：`AddSelectionListObject` 12 次全返回 false 但实际选中了 12 个。

**校验**：新增的「建特征」类工具必须调用 `EditRebuild3()` + `GetWhatsWrong2`。

---

## 二 地图的形态

`docs/union-coverage-matrix.md` 是**生成物**，由 `tools/build_union_map.py` 从：

1. `capabilities.yaml`（本仓库已有能力）
2. 四家项目的工具清单（`tools/union-sources.json`，含来源+许可+各自验证状态）

生成一张 **域 × 项目** 的矩阵，每个格子标：

```
✓N   该域该来源有 N 个工具
·    没有
```

**并集目标**：让本仓库在**每一个域**都至少有一个来源覆盖，且每个格子可追溯到具体文件。

### R14 · 「不做 + 原因」（**A1 的另一半**，2026-10-01 轮 67 加）

`AGENTS.md §一 A1` 的判据是「域覆盖矩阵里本仓库每一格**都有来源，或写明「不做 + 原因」」。
⇒ 这是**两个半边**：

| 半边 | 机制 | 门禁 |
|---|---|---|
| **有来源** | `capabilities.yaml` 的 `source` + `source_evidence` | **R12**（枚举 + 依据非空）· **R13**（`source` 与 `provenance` 自洽） |
| **不做 + 原因** | `docs/union-not-doing.json` | **R14**（本规则） |

⚠ **为什么要有 R14**：轮 67 实测发现，此前**只有「有来源」那一半有机制** ——
矩阵里只有「**缺 N**」，读者**无从分辨**「我们不做这个域」与「这个域还没做」。
两者对决策的含义完全相反：前者是**结论**，后者是**待办**。

**数据形状**（`docs/union-not-doing.json`）：

```json
{
  "not_doing": [
    {
      "subject":   "不做什么（域 / 能力 / 动作）",
      "reason":    "为什么不 —— 一条没有原因的「不做」等于用一个词掩盖一个缺口",
      "evidence":  ["凭什么这么判定（可核的命令 / 文件 / 实测输出）"]
    }
  ]
}
```

**判据**（三条，每条都必须**非空**）：`subject` · `reason` · `evidence`。
**校验**：`scripts/check_union_conventions.py` 的 `check_not_doing()`（R14）。
**渲染**：`tools/build_union_map.py` 把它渲染进矩阵 **§二 之后**的
「不做 + 原因（A1 的另一半）」小节 —— **一个没渲染进矩阵的清单，读者看不到，
而 A1 的判据正是「矩阵里…或写明」**。

⚠ **两条刻意的设计**：

1. **空清单合法**（文件不存在也不报错）—— 要求「必须有一条不做」会**逼人编**条目来过关，
   那正是本项目反复记录的「为了迁就实现而改判据」的反面。空清单时生成器会在矩阵里
   打一行「**本清单为空** —— 一个「不做」都没登记（那通常意味着**还没逐域确证**）」。
2. **不臆断** —— 只登记**有硬依据**的条目；没有依据的域**留空**，不为填满而编。

## 二之补 R 编号登记表（**R1–R14 的唯一登记处**，2026-10-01 轮 193 加）

> ⚑ **为什么补这一节**（轮 193 实测）：
> ```
> · 门禁 `scripts/check_union_conventions.py` 引用 **R1–R14**（14 个编号）
> · 而**代码仓库里此前没有任何一处**说明 R1–R11 是什么 ——
>   它们的权威定义在**另一个仓库**的 `capabilities-schema-proposal.md`（起草时的方案文件）
> · 反过来，**R12 / R13 / R14** 是后来（轮 58 / 59 / 67）加的，**那份提案里没有它们**
> ⇒ ★★ 两个方向都缺：读代码的人**无法核验这些编号代表什么**。
> ⇒ ★ 本节把它们**一次登记齐**，并写明**每条由哪段门禁守**、**权威出处在哪**。
> ```
> ⚠ **本表是**手写**的（因为它含判断与出处），但**编号集合**由一条门禁守**：
> `check_rule_registry()` 保证「门禁段名里引用的每个编号都在本表内」且「本表无缺号」。

| 编号 | 含义（一句话） | 由哪段门禁守 | 权威出处 |
|---|---|---|---|
| **R1** | `capabilities.yaml` 的 `schema_version` 等于约定值 | 「清单形状」段 | 提案 §五（**工作区仓库** `D:/AI/SW/docs/capabilities-schema-proposal.md`） |
| **R2** | 每条 `level` ∈ 五值枚举；且 `scripts/capabilities.py` 的 `VALID_LEVELS` 与本门禁的集合一致 | 「清单形状」段 | 同上 |
| **R3** | `id` 全局唯一且是稳定 slug（`^[a-z][a-z0-9_]*$`） | 「清单形状」段 | 同上 |
| **R4** | 能力条数 ≥ 10 | ★ **`scripts/release_check.py` 的现有断言**（本门禁不重复守） | 同上 |
| **R5** | `verified` ⇒ `evidence` 非空；`backends` 含 CAD 后端时另要 `verified_versions` 非空 | 「验证等级与授权」段 | 同上 |
| **R6** | `level == source_verified` ⇒ `provenance` 非空；带 `provenance` 的条目 `repo` 必须是 `owner/repo`、`license` 在白名单 | 「清单形状」段 | 同上 |
| **R7** | `not_implemented` ⇒ `limitations` 非空 | 「验证等级与授权」段 | 同上 |
| **R8** | 等级审计 `docs/union-level-audit.md` **不得出现「高报」**；且它是**生成物**（重跑必须逐字一致） | 「规范与地图存在性」段（读生成物 + 新鲜度） | 同上 + 本文件 §三 的生成物口径 |
| **R9** | `provenance.files` 为非空数组；`commit`/`tag` 可省或为空串，若出现必须是字符串 | 「清单形状」段 | 同上 |
| **R10** | `provenance.files` 不得落在 `angelsix/solidworks-api` 的 `References/` 下（那是 MIT 仓里被点名的例外） | 「清单形状」段 | 同上 + `docs/sources.md` 的许可例外段 |
| **R11** | `allowed_modes` ⊆ {`interactive`,`reviewed`,`unattended`}；且 `level != verified` ⇒ 不得含 `unattended` | 「验证等级与授权」段 + 「授权真源」段 | 同上 |
| **R12** | `source` 标记的**枚举**（回答「这条是**并入来的**还是**本项目自研的**」）+ 依据非空 | 「清单形状」段 | 代码注释（轮 58 加）—— ⚠ 提案未收录 |
| **R13** | `source` 与 `provenance` 必须**自洽**（`original` 却有 `provenance` ⇒ 报自相矛盾） | 「清单形状」段 | 代码注释（轮 59 加）—— ⚠ 提案未收录 |
| **R14** | 「**不做 + 原因**」：`docs/union-not-doing.json` 的每条都要有 `subject`/`reason`/`evidence` | 「A1 的另一半」段 | 本文件 §二 的 R14 小节（轮 67 加）—— ⚠ 提案未收录 |

> ⚑ **本登记的守卫范围**（轮 194 扩，**如实声明覆盖面**）：
> ```
> 守：`scripts/*.py`（**执行侧**）里出现的每个 R 编号，都必须在**上表**里登记；
>     且上表本身**无缺号**（R1..Rmax 连续）；**读不出上表 ⇒ 报**（不是静默通过）。
> 不守：`tests/`（**负例测试必须能写出未登记的编号**来证明判据有牙）
>      · `docs/`（ROADMAP / known-facts / specs 是**历史记录**，记的是"当时引用过什么"）
>      · **函数体里的字符串拼接**（若编号是拼出来的，静态看不见）
> ⚠ 实测（轮 194）：执行侧引用 R 编号的共 **7 个文件**，**全部已在册**。
> ★ 且这条检查**加完立刻抓到一处**：本门禁自己的注释里写了举例「如 R99」
>   ⇒ ★ **定则**：在本文件里举例请用 `` R<n> `` 占位，**不要写具体编号**
>     （判据分不出"举例"与"引用"，所以让**举例本身不构成引用**，比去剥注释更稳）。
> ```

**⚠ 两条如实记的限度**：
1. **R4 不在本门禁里守**（它由 `release_check.py` 的既有断言守）⇒ 本门禁的段名里**不出现 R4**，
   所以 `check_rule_registry()` 的「引用 ⊆ 登记」这一半**覆盖不到 R4** —— 它靠**本表**登记，
   靠**另一道断言**执行。★ 这是**分工**，不是遗漏（`check_rule_registry` 的文档串里写明了）。
2. **提案与代码已分叉**（提案 R1–R11 · 代码 R1–R14）⇒ ★ 本节是**代码仓库内的权威**；
   提案在**另一个仓库**，本仓库**不该**依赖它（别的机器上没有）。

## 三 与 DSH 官方约定的对应

| DSH 原则 | 本规范对应 |
|---|---|
| Explicit > implicit at package boundaries | 规则 4：验证等级显式，禁止「大概跑过」 |
| No hardcoded tunables | 规则 2：单位在边界显式转换，不靠猜 |
| Misconfiguration fails loud | 规则 6：禁止静默成功 |
| Prefer maintained dependencies over hand-rolling | 并入而非重写（本文件存在的理由） |
| Ban ambiguous origin labels | 规则 5：出处必须 `owner/repo` 全名 + 许可 + 来源验证状态 |
| Prefer symmetry for parallel values | 规则 1/2：命名与单位对称，不留特例 |
| Wire checkable invariants into an executed gate | `scripts/check_union_conventions.py` |

## 四 违规怎么办

`scripts/check_union_conventions.py` 在 `release_check.py` 里执行，违规**硬失败**。
新增条目不合规 ⇒ 门禁红 ⇒ 不许提交。

**这不是建议，是门禁。**
