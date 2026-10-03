# 候选裁决 · 工程图 8 项挂 MCP 工具

> 裁判轮次：2026-10-03 · 逐份读完 cand-A/B/C，全部结论回源码核过。
> ★ 本文件**只评分**，不重写方案。核验用的具体判据见每节「核验」。

---

## 0. ★★ 先说一件推翻三份前提的事（必须先讲）

**这个任务已经在树里了 —— 三份候选都没发现。**

| 事实 | 出处 |
|---|---|
| `mcp-server/tool_specs_batch75.py` **已存在**，就是本题的落地件（8 条 ToolSpec，标题逐字「把工程图**已实现却没挂**的 8 项接成工具」） | `mcp-server/tool_specs_batch75.py:1` |
| 它**已在注册表里** | `mcp-server/register_capabilities.py:369` `"tool_specs_batch75",` |
| 它的注册注释**逐字写着这就是 R1 本题**：「规格 `specs/202-user-coverage-gaps` 的 **R1**：**工程图「已实现却没挂」的 8 项** —— 投影视图 · 剖面视图 · 局部视图 · 图纸格式/模板 · 注释/文字 · 孔表 · 修订表 · 中心符号线」 | `register_capabilities.py:360-361` |
| 转接层 `scripts/sw_drawing_expose.py` **已存在**，8 个包装函数首参全是 `drawing_model`，`_mm()` 在 `:39-41` 做 `/1000.0` | `scripts/sw_drawing_expose.py:39,64,76,87,103,113,119,133,149` |

⇒ **三份候选全部把落点写成 `mcp-server/tool_specs_batch73.py`。而那个文件也已经存在、也已注册**
（`register_capabilities.py:359`），装的是**另一件事**（R2「工程图真缺口」：断裂视图 / 辅助视图 / 表面粗糙度符号 / 基准符号，248 行）。
⇒ **按三份里任何一份粘贴，都会覆盖一个已注册、含 4 条可用工具的活文件。**

| 候选 | 关于批次号的说法 | 实况 |
|---|---|---|
| A | 「落点文件名 `mcp-server/tool_specs_batch73.py`（候选，未落地）」 | 该文件已存在且已注册 |
| B | 「落地点：`mcp-server/tool_specs_batch73.py`」 | 同上 |
| C | 「`tool_specs_batch72.py` 是现存最大编号」「在 `register_capabilities.py:140` 的 `BATCH_MODULES` 末尾加一行 `"tool_specs_batch73"`」 | 错两次：最大编号是 **75**（batch73/batch75 都已注册，74 跳过）；且按 C 的指示做会把 batch73 **再注册一遍** ⇒ 4 个工具名重复 ⇒ `check_specs` 抛「工具名重复」⇒ `register()` 在 `:554-555` **整批不注册** |

★ **三份都没有打开 `mcp-server/` 看一眼。** 这是全场最大的共错，且直接抽掉了「可落地性」这一列的地基。

---

## 1. ★ 真正的 8 项清单 —— 三份全数搞错

`specs/202-user-coverage-gaps/recon/drawing-existing-coverage.md:32` 逐字：
「**「已实现」= 8**：第 1、2、3、6、9、13 项（6 项）+ 第 11、12 项（2 项）」

⇒ 8 项 = **投影视图 · 剖面视图 · 局部视图 · 注释/文字 · 图纸格式/模板 · 中心符号线 · 孔表 · 修订表**
（与 `tool_specs_batch75.py:20-27` 的工具名表逐条对上）

| 候选 | 它认的 8 项 | 错在哪 |
|---|---|---|
| A | 剖面/局部/中心/**孔表**/**修订表**/**表面粗糙度**/注释/图纸格式 | ★ 用**表面粗糙度**顶掉了**投影视图**。而 `drawing-existing-coverage.md:18` 逐字写表面粗糙度「**无（创建）**」—— 它是被**判为未实现**的那 5 项之一 |
| B | 同 A 的错，另加 A3 页 | 同上 |
| C | 同 A 的错 | 同上；且 C 在 `:459-461` 自己承认「8 条 ≠ 8 项能力」，却仍按错的清单判分 |

★ 三份**全都没提「投影视图」**（`drawing_workflow.py` 的 `create_adaptive_standard_views` / `add_view` 那一族），
而它是这 8 项里的第 1 项 —— 也正是已落地的 `sw_drawing_expose.create_projected_view` 干的那件事。

---

## 2. 逐维评分

### 2.1 事实正确性（`module` / `inject` / 形参 与源码一致？）

#### 先记对的部分（三份都对，不构成区分）

| 判据 | 核验 | 出处 |
|---|---|---|
| 导入契约 `__import__("scripts.%s" % spec.module, …)` ⇒ `module` 只能指 `scripts/` 下模块 | ✓ 三份全对 | `tool_registry.py:524` |
| `RESOLVERS` 已有 `"drawing_model": resolve_model` | ✓ 三份全对 | `register_capabilities.py:136` |
| 注入键**字面等于 `inject`**（`register()` 不传 `inject_as`）⇒ 首参必须叫 `drawing_model` | ✓ 三份全对（A/B/C 各引 `:507`+`:559`，逐字相符） | `tool_registry.py:507` · `:559` |
| `x_mm`/`y_mm` **不触规则 3**（`_mm` 后缀放行） | ✓ 三份全对 | `tool_registry.py:128` |
| 逐字形参（section/detail/note/sheet_format/add_sheet/center_marks/table） | ✓ 三份全对，**没有一个形参抄错** | 见下表 |

核验用的真值（**三份引的行号全错，实测行号如下**）：

| 函数 | 三份都写的行号 | **实测** | 形参是否相符 |
|---|---|---|---|
| `add_section_view(drawing_model, x, y)` | 998 | **1045** | ✓ |
| `add_detail_view(...)` | 1022-1035 | **1069-1082** | ✓ 含 `*` 后 7 个 keyword-only |
| `add_note(drawing_model, x, y, text)` | 1238 | **1285** | ✓ docstring 逐字「（米）」 |
| `set_sheet_format(drawing_model, format_path)` | 1400 | **1447** | ✓ |
| `add_sheet(..., paper_size=7, template_path="", first_angle=True)` | 1411 | **1458** | ✓ 图幅表逐字相符 |
| `auto_insert_center_marks(drawing_model, requirements)` | 1883 | **1930** | ✓ 键 `id`/`view`/`count`/`targets` 相符 |
| `insert_table_annotation(...)` | 2306-2316 | **2353-2363** | ✓ |
| `add_a3_sheet(...)`（仅 B） | 1426 | **1473** | ✓ |
| `setup_current_sheet(...)`（仅 C） | 2042 | **2089** | ✓ |

★ **行号系统性偏 +47** ⇒ 三份都没有按当前文件核行，是「读了旧快照或凭记忆」。**签名本身没抄错**，这是三者唯一没塌的地方。

#### 判别项一：`table_type` 到底是什么（**决定性**）

实测官方签名 `C:\swapi\types\IDrawingDoc\InsertTableAnnotation.md:14` 逐字：

```
TableAnnotation InsertTableAnnotation( System.double X, System.double Y,
                                       System.int AnchorType, System.int Rows, System.int Columns )
```

且 `InsertTableAnnotation2.md:20` 逐字：`AnchorType: Type of anchor as defined in [[swBOMConfigurationAnchorType_e]]`。

实现 `drawing_workflow.py:2373-2376` 把 `table_type` 塞进**第 3 个 int 槽** ⇒ **那是锚点类型，不是表种类**。

| 候选 | 它说 `table_type` 是什么 | 判定 |
|---|---|---|
| **A** | 「实现叫 `table_type` 的那个 int **落在官方 AnchorType 槽**里，**建不出孔表，也建不出修订表**」；并指出真入口是 `IView.InsertHoleTable3`（**9 参**，实测签名逐字含第 9 参 `ManualTags` 为 `System.object`）与 `ISheet.InsertRevisionTable2`（**7 参**），宿主是 IView/ISheet | ★★ **完全正确**，三处官方页逐条复核通过 |
| B | 「官方 `InsertTableAnnotation` 的 Int32 `Type`」「表种类（孔表 / 修订表 / BOM 共用这一个官方入口，种类由 `table_type` 决定）」 | ✗ **错**，官方是 `AnchorType` |
| C | 「★ **官方 `Int32 Type`，决定表的种类**（孔表 / 修订表 / 通用表 / BOM）」「孔表/修订表/通用表/BOM **共用这一个官方入口**」 | ✗ **错**，同上 |

⇒ B 与 C 各自在 §二 的代码块里写了一条**建立在误读上的工具**（`Param("table_type", int, description=…Type…)`），并把它当成「8 项里覆盖了孔表+修订表」来计分。
⇒ **已落地的 batch75 走的正是 A 指出的那条路**：`create_hole_table` / `create_revision_table` **分成两条**，分别打 `InsertHoleTable3` / `InsertRevisionTable2`（`tool_specs_batch75.py:126,146`）。

#### 判别项二：`list` 型入参本仓有没有先例

实测（`grep 'Param\(".*", list' mcp-server/`）：

```
tool_specs_batch33.py:132   Param("configuration_names", list, default=None,
tool_specs_batch36.py:124   Param("bom_rows", list, …)
tool_specs_batch57.py:28    Param("positions", list,
tool_specs_batch61.py:59    Param("source_indices", list,
tool_specs_batch71.py:62    Param("points_mm", list, …)
```

| 候选 | 它怎么说 | 判定 |
|---|---|---|
| A | R8：「本仓见过的复杂参数**只有 `dict`**…`list` **未实测**」 | ✗ 错（是少报，方向保守） |
| **B** | 「★ `list` 作为 `Param.kind` 是**已验证可用**的形态（`tool_specs_batch57.py:28`、`tool_specs_batch36.py:124`）」 | ✓ **正确，且行号逐条命中** |
| C | §3.2：「★ 本仓 72 个批次文件里**没有一条 `list` 型入参**」 | ✗✗ **平白造事实**。更糟：它把 `register_capabilities.py:167` 里 batch14 那句**只针对 batch14 自身**的注记（「本批也**不暴露** views/expected_outputs（**list 型无先例**）」）**当成全仓禁令**引用 —— 作用域被它自己放大了一格 |

#### 判别项三：`first_angle` 会不会被规则 2 拦

实测 `tool_registry.py:423`：`if p.kind is not bool and any(w in low for w in _ANGLE_WORDS) and not low.endswith(_ANGLE_SUFFIX)`

⇒ **`bool` 被显式豁免**，声明 `Param("first_angle", bool, …)` 合法。

| 候选 | 它怎么说 | 判定 |
|---|---|---|
| A | 「刻意用 `bool` 而不是 `projection: str`：注册器 `check_spec` 对 `kind is bool` **豁免**规则 2 的长度/角度后缀检查（`tool_registry.py:412` / `:423`）⇒ 这个名字不会被门禁拦」 | ✓ **正确，行号逐条命中** |
| B | 「`first_angle` 命中 `_ANGLE_WORDS` 的 `angle`，但 `kind is bool` 被 `tool_registry.py:412` 显式豁免」 | ✓ **正确** |
| C | 「规则 2：`add_sheet` 的形参 `first_angle` 含 `angle` 而不以 `_deg` 结尾 ⇒ **会被拦** ⇒ 对外改叫 `projection`」 | ✗ **错**（`:423` 就是 bool 豁免）⇒ 代价是多一层 `_first_angle` 间接 + 一个凭空的改名理由 |

#### 判别项四：只有 B 说、且说对了的两条桥内风险

| B 的说法 | 核验 |
|---|---|
| §1.2(a)：`drawing_workflow.py` **无 `__all__`** ⇒ 走 `scripts/sw_drawing.py:26-27` 的兜底分支，`math`/`re`/`Path`/`VARIANT` 等一并 re-export；将来谁补一个不完整 `__all__`，这批工具会**整批消失** | ✓ `grep '__all__' drawing_workflow.py` = **0 命中**；`sw_drawing.py:25-27` 兜底逻辑逐字相符 |
| §1.2(c)：该文件用了 `Any` 却**从未 import**，且**无 `from __future__ import annotations`** ⇒ 只因本机 Python 3.14 的 PEP 649 惰性注解才不炸，**≤3.13 上 import 会 NameError** | ✓ `grep 'Any'` = 仅 `:2405` `get_table_shape(table) -> dict[str, Any]` 与 `:2703` `get_annotation_view_evidence(...) -> dict[str, Any]`；`grep '^from typing\|from __future__'` = **0 命中** ⇒ **成立**。B 且诚实标注「这一步属于推出来、不是量出来的」 |

⇒ ★ A 走的是**同一座桥的再导出层**，把 B 这两条账**全部继承却一个字没提** —— 这是 A 最该补的洞。

### 2.2 完整性（8 项挂几条）

| | A | B | C |
|---|---|---|---|
| 工具条数 | 6 | 8 | 8 |
| 覆盖到**真 8 项**里的 | 剖面·局部·中心·注释·图纸格式（拆 2）= **6 条** | 剖面·局部·中心·注释·图纸格式 = **6 条** | 剖面·局部·中心·注释·图纸格式 = **6 条** |
| 投影视图 | ✗ | ✗ | ✗ |
| 孔表 | ✗ 判「本仓无实现」 | △ 错塞进 `insert_table_annotation` | △ 同 B，且明说「合并成 1 条」 |
| 修订表 | ✗ | △ 同上 | △ 同上 |
| 凑数用的**非 8 项** | — | `add_a3_sheet` | `add_sheet` + `setup_current_sheet` |
| 自评是否诚实 | ✓ §二 明说「实际只有 5 项能接成工具」 | △ 说 8 条但其中 2 条建的是错的表 | ✓ §3.3-7 主动说「8 条 ≠ 8 项能力」 |

⇒ **在「表」这一格上，只有 A 的判断（孔表/修订表要补实现）与已落地的 batch75 一致**；B/C 的「一条工具覆盖三项」被官方签名否掉了。

### 2.3 可落地性（能否直接粘贴）

| | A | B | C |
|---|---|---|
| 落点文件名 | `tool_specs_batch73.py` ✗ **已被占用并已注册** | 同 ✗ | 同 ✗ **且它明确教你去改 `BATCH_MODULES` 加这一行 ⇒ 会造成重复注册 ⇒ 整批不注册** |
| 过 `check_spec` | ✓（`x_mm` 合法、`bool` 豁免、`derived_args` 不撞名 `:517-522`） | ✓ | ✓（多一层无必要的 `projection`） |
| 过 `check_param_binding` | ✓（`:20-21` 的判据：声明名 ∈ 形参 或 ∈ `param_alias`；只用 `None` ⇒ 自动满足） | ✓ | ✓ |
| 代码本身 | 干净 | 干净 | 干净 |

### 2.4 诚实度（有无编造 / 漏标）

| | A | B | C |
|---|---|---|---|
| 明写「未落地 / 未注册 / 未跑真机」 | ✓ R10 | ✓ 抬头 | ✓ 抬头 |
| 自曝风险条数 | 10 条（R1-R10） | 6 条（§3.3） | 8 条（§3.2/3.3） |
| 主动**认错自己** | ✓ R1 里推翻实现来源块那句「枚举查不到」 | ✓ §3.3-1 标「推出来的，不是量出来的」 | ✓ §3.2 标 `idempotent` 「首次使用、现有测试没覆盖」（实测 0 命中 ⇒ **这句是对的**） |
| 编造 / 假事实 | R8「`list` 无先例」（少报）· R7 把 `tool_registry.py:125-127` 的**已解决叙事**读成「注释与代码矛盾」 | 无 | ✗✗ §3.2 平白断言「72 个批次里没有一条 `list` 型入参」并**引用 batch14 的局部注记冒充全仓事实** · ✗「`first_angle` 会被拦」 |

---

## 3. 总分与胜者

| 候选 | 事实正确性 | 完整性 | 可落地性 | 诚实度 | **总分** |
|---|---|---|---|---|---|
| **A** | **9/10** — 唯一在 `table_type` 锚点槽、`swTableAnnotationType_e` 存在、`InsertHoleTable3`/`InsertRevisionTable2` arity、`bool` 豁免、`list` 门外这几处全对；失分在 R8 与 R7 两处少读 | **6/10** — 6 条对 6 项；投影视图缺、孔表/修订表判 0，但**判断方向与已落地件一致** | **5/10** — 代码干净可过门禁，但落点文件名被占 | **9/10** | **29** |
| B | **6/10** — 桥的 4 条账（`__all__` 兜底 / `__module__` 漂移 / PEP 649 / 导入时机）与 `list` 先例全对且独有；但 `table_type` 说成官方 `Type` 是硬错，另「2746 行」实为 **2793** | **6/10** | **5/10** | **9/10** | **26** |
| C | **4/10** — 两处硬错（`first_angle` 会被拦 / `table_type` 是 `Type`）+ 一处平白造事实（`list` 无先例）+ 批次号判错两次 | **5/10** | **3/10** — 唯一会**照做把人搞坏**的：按它改 `BATCH_MODULES` ⇒ 重复注册 ⇒ `register()` 整批不注册 | **6/10** | **18** |

# ★ 胜者：A

**一句话理由**：A 是三份里**唯一**在决定性的 `table_type` 事实上核对了官方签名（`InsertTableAnnotation` 第 3 个 int 是 `AnchorType` 而非 `Type`，`InsertHoleTable3` 9 参 / `InsertRevisionTable2` 7 参都对），而 B 与 C 各自把一条工具建在这个误读上；A 的形参抄写零错误、诚实度最高，且它「孔表/修订表得补专用入口」的判断与**树里已落地的 `tool_specs_batch75.py`（分成 `create_hole_table` / `create_revision_table` 两条）完全一致**。

## 该把落选者的哪些片段并进 A

| 并入 | 出处 | 为什么值 |
|---|---|---|
| ★ **桥的四笔账**：`__all__` 兜底耦合 · `__module__` 漂移 · **PEP 649 `Any` 前提（≤3.13 会 NameError）** · 首次 import 会跑 `import_com_dependencies()` 但不连 SW | B §1.2(a)-(d) | A 的薄再导出层**逐字继承**这四条，却一条没写；其中 PEP 649 那条是**真会炸**的 |
| ★ **`list` 型入参有 5 处先例**（`batch33:132`/`batch36:124`/`batch57:28`/`batch61:59`/`batch71:62`） | B §1.4(iii) | **直接更正 A 的 R8**（A 误判为无先例） |
| **`insert_dimensions(drawing_model, view=None)`**（`:1126`）在 A 的「挂不了」表里 | B §3.2 | 它是**唯一半可挂**的：A/B/C 都没提；`view=None` 时能标全部视图 |
| **`set_section_style` 的 `None = 「不设」` 语义 `Param` 表达不了** | B §3.2 末 | 比 A 的「首参是 COM 对象」更进一步的**第二条**不可挂理由 |
| `idempotent=False` 挂到 6 条会改模型的工具上（字段实测存在：`tool_registry.py:311`），**并保留 C 自己那条免责**（全仓首次使用、无测试覆盖，实测 0 命中） | C §3.2 第 2 行 | 6 条里 6 条每调一次多一个视图/页/标记，缺这行 `idempotentHint` 会说反 |
| `SetupSheet6` 官方页**没读到**（`recon/api/` 下只有 `SetupSheet5.md`）⇒ 那条若要挂，官方依据不完整 | C §3.3-2 | 诚实度补丁 |

## ★ 明确**不要**并进 A 的东西

- ✗ **C 的 `projection` 改名 + `_first_angle`** —— 建立在一个**错的门禁读法**上（`tool_registry.py:423` 的 bool 豁免）。A 现有写法（`Param("first_angle", bool, …)`）既正确又少一层间接。
- ✗ **B / C 关于 `table_type` 的任何一句**（「官方 Int32 Type」「孔表/修订表/BOM 共用一个入口」）—— 与官方签名相反。
- ✗ **C §3.2 的 `list` 无先例论断**，以及任何以它为前提的处置。

---

## 4. ★ 三份共有的错（⇒ 说明都没查源码现状）

**共错 1 · 最重：落点 `mcp-server/tool_specs_batch73.py` 已被占用且已注册。**
`tool_specs_batch73.py` 已存在（248 行，装的是 R2 工程图真缺口），已注册于 `register_capabilities.py:359`；
本题的正解早已落在 **`tool_specs_batch75.py`**（已注册于 `:369`，转接层 `scripts/sw_drawing_expose.py`）。
⇒ 三份**没有一份打开过 `mcp-server/`**。这一条直接抽掉了三份「可落地性」的地基：
按任一份粘贴 = 覆盖一个含 4 条可用工具的活文件；按 C 的指示改注册表还会造成重复注册 ⇒ `register()` 在 `:554-555` **整批不注册**。

**共错 2 · 每个 `drawing_workflow.py` 行号系统性偏 +47**（998→1045、1238→1285、1400→1447、1411→1458、1883→1930、2306→2353；B 的「2746 行」实为 **2793**）。
⇒ 三份都没按当前文件核行。签名没抄错，是侥幸不是本事。

**共错 3 · 「8 项」清单全错**：三份都用**表面粗糙度**顶掉了**投影视图**，
而 `drawing-existing-coverage.md:18` 逐字写表面粗糙度「**无（创建）**」（它是被判为**未实现**的那 5 项之一），
`:32` 的权威口径是「第 1、2、3、6、9、13 项 + 第 11、12 项」。三份**全都没提投影视图**。

**共错 4（仅 B 与 C）· `table_type` 认成官方 `Type`** —— 官方逐字是 `AnchorType`（`InsertTableAnnotation.md:14`）。

---

## 5. 给 Lead 的一句实操建议

★ 本题的**正确解已经在树里**（`tool_specs_batch75.py` + `scripts/sw_drawing_expose.py`，带真机证据
`output/drawing-batch-evidence.json`，见 `tool_specs_batch75.py:64,96,108,123,141,161`）。
⇒ **三份候选不该被实现为新批次。** 若一定要用，选 A 当**复核清单**，但把它降级成一份**对照审计**，
用来核 `tool_specs_batch75.py` 现状 —— 特别是 B 那条 PEP 649 的 `Any` 隐患，以及 C 那条 `list` 型入参的先例归属。