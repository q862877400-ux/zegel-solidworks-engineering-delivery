# spec 236 · 分发口 `upstream` 声明的**上游覆盖**门禁

> ★ 本规格收 spec 235 交接单的**待办 1**（「二级转发的上游」）。
> ★ **先量后做** —— 量完发现 3 条 `upstream` 声明**各落一个不同的桶**（`sites` 1 · `tool-only` 1 · `orphan` 1），
> 一轮做完。

## 一、问题（为什么需要）

spec 235 给分发口**调用点**的非字面量实参开了三条逃生门，其中 `upstream` 的语义是：

```
#: dispatch-fwd: upstream <caller-def 名> <理由>
```

它自证到的东西**只有两件**：

1. 实参**是**包围 `def` 的形参；
2. 包围 `def` 的名字**等于**声明的 `<caller-def 名>`。

★ **它从不检查那个 `<caller-def 名>` 的调用方到底传了什么** ⇒
`upstream` 是一个**半开的逃生门**：写 `upstream X` 只要 X 恰好是包围 `def`、恰好收一个成员名形参，
就永远绿 —— **哪怕 X 的每一个调用方都在用运行期变量传成员名**。

这正是本仓反复踩到的形态：**「一句话不是守卫」**（spec 229）与
**「`dynamic`/`upstream` 只做形态自证」**（spec 235 acceptance §六）。

## 二、需求

| # | 需求 | 来源 | license |
|---|---|---|---|
| FR-001 | `upstream` 声明的**第三个 token** 必须是封闭词表里的**上游桶**：`sites` / `tool-only` / `orphan`。缺失或不在词表 ⇒ **红（未表态）**。 | spec 235 交接单待办 1；本仓纪律「未表态即红」（229） | 本项目 MIT |
| FR-002 | **桶必须与事实相符**（自证条件，写错即红）：`sites` ⇒ `def <caller>` 在本仓**有** AST 调用点；`tool-only` ⇒ **0** 个 AST 调用点 **且** 名字出现在某 `mcp-server/tool_specs_*.py` 的 `function="<caller>"`；`orphan` ⇒ **0** 个 AST 调用点 **且 0** 个 ToolSpec 引用。 | 本仓纪律「逃生门必须自带自证条件」（235） | 本项目 MIT |
| FR-003 | `sites` 桶：**每个**上游调用点的成员名实参**必须**是字面量字符串；**非字面量 ⇒ 红**（该点须另行表态）。字面量值**必须**能在官方两源（`_raw/**/iface_*.txt` + `C:\swapi\types`）里查到；查不到 ⇒ 红。 | 同 FR-002；官方依据见 plan.md §二 | 本项目 MIT；官方源见 plan.md |
| FR-004 | `def <caller>` 在本文件找不到 ⇒ 红（**声明指向一个不存在的 def**）。 | 本仓纪律「解析不出必须显式判出来」（230/231/233/234/235） | 本项目 MIT |
| FR-005 | **只增不减**：`upstream 声明数` / `上游调用点总数` / `字面量候选值 distinct` 三个读数各有一个**下界常量**，任一减少 ⇒ 红（减少 = 取点或读取器漏了，**不是**「问题解决了」）。 | 本仓纪律「可见性边界必须被量出来并冻结下界」（225–235） | 本项目 MIT |
| FR-006 | **零检查即红**：`upstream 声明数 == 0` ⇒ 红（事实 46）。 | 本仓纪律「检查量为 0 判失败」 | 本项目 MIT |
| FR-007 | 两源**都**读不到 ⇒ `[SKIP]` + `exit 0`（缺数据源 ≠ 检查失败）。 | 本仓纪律「便携性」（234/235） | 本项目 MIT |
| FR-008 | 3 条既有 `upstream` 声明按 FR-001 补上游桶（**纯插入/行内改写，不新增行、不删除**）。 | 本规格 §三的实测表 | 本项目 MIT |

## 三、先量（2026-10-09 · 本规格开工前，探针 `output/_probe236_upstream.py` / `_probe236_facts.py`）

对 3 条 `upstream` 声明所指的上游 `def`：

| # | `upstream` 声明位置 | 上游 `def` | `scripts/**`+`mcp-server/**` 的 AST 调用点 | ToolSpec `function=` 引用 | **桶** |
|---|---|---|---|---|---|
| 1 | `sw_drawing_create_missing.py:286` | `_sum_over_views` | **10**（全字面量 · 5 distinct） | 0 | **`sites`** |
| 2 | `sw_drawing_view.py:391` | `call_view_no_args` | **0** | 0 | **`orphan`** |
| 3 | `sw_simulation_study_options.py:904` | `set_study_option_report` | **0** | **1**（`tool_specs_batch37.py:96`） | **`tool-only`** |

★ 5 个字面量候选值 `GetSFSymbolCount` / `GetDatumTagCount` / `GetNoteCount` /
`GetAnnotationCount` / `GetCenterLineCount` —— **全部**在官方两源里查到 ✓。

★★ **量出的两条纠正**（交接单的前提又错了一半）：
1. 「3 个上游」里**只有 1 个**有调用点 ⇒ 「扩 `entries` 会动 229 的下界常量」这条**不成立**
   （`_sum_over_views` 不是分发口，它的字面量在**调用方**那一层）⇒ **不需要**动 229 的任何常量。
2. `call_view_no_args` 是**真 orphan**（全仓零引用，`output/orphan-capabilities.json` 已登记）；
   `set_study_option_report` **不是** orphan —— 它由**工具层按名**注册（ToolSpec `function=`）
   ⇒ ★ 「AST 调用点为 0」**不等于**「没人用」（与 234「窄读取器读出 0 也会骗人」同族）。
   ⇒ 这就是为什么桶**必须有 `tool-only` 这一档**。

## 四、验收判据（可复制执行）

```bash
# ① 门禁本体（真树）—— 期望 exit 0
"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B \
  D:/AI/SW/scripts/check_dispatch_upstream_guard.py

# ② 本规格判据
"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B \
  D:/AI/SW/tests/test_dispatch_upstream_guard.py

# ③ 235 回归（★ 声明语法向后兼容，必须仍绿）
"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B \
  D:/AI/SW/tests/test_dispatch_forward_arg_guard.py

# ④ 门禁全套（★ 必须 3.14.7）
"C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" \
  D:/AI/SW/scripts/release_check.py
```

## 五、不做什么（边界）

- **不做递归解析**：上游桶只**核一层**（上游 `def` 的调用点）；再往上追会变成「会移动的靶子」
  （spec 235 §三.1 的设计决定，本规格沿用）。
- **不判接口归属**：字面量只判「名字在两源里存在」，不判属于哪个接口
  （那是 `check_interface_member_ownership.py` 的职责，映射表另有洞）。
- **不动 229 的下界常量**（`BASELINE_ENTRIES 37` / `BASELINE_RESOLVED 18` / `BASELINE_RESOLVED_SITES 327`）——
  §三 已证 `_sum_over_views` 不是分发口，无需扩 `entries`。
- **不修 `call_view_no_args` 的 orphan 状态** —— 它是否该保留是**能力层**的决定，本规格只**登记**。
- **不动 `apps/workbench-ui/src-tauri/resources/skill/`** 的打包副本（那是 `sync_bundled_skill` 的产物，
  发版前同步；本门禁只扫真树 `scripts/**` + `mcp-server/**`）。

## 六、未过门（如实登记）

- 桶的判定是**静态**的：`tool-only` 只证明「名字出现在 ToolSpec 的 `function=`」，
  **不证明**该 ToolSpec 真的会被调用、也不证明其成员名实参真的来自运行期。
- `sites` 桶的调用点只核**成员名实参**，不核 `arity` / by-ref 占位（那是 228/231 的职责）。
- 真机未验（本切片全程离线）。
