# acceptance 236 · 验收记录

> 施工日期：2026-10-09（主任务 `ff6c7344` 第 10 轮 · 全新会话）
> 解释器：判据 **3.13.12**（受管）· 门禁全套 **3.14.7**（`pythoncore-3.14-64`）

## 一、交付物

| 件 | 路径 | 动作 |
|---|---|---|
| 门禁本体 | `scripts/check_dispatch_upstream_guard.py` | **新增** |
| 判据 | `tests/test_dispatch_upstream_guard.py` | **新增 18 例** |
| 声明 | `scripts/sw_drawing_create_missing.py` / `sw_drawing_view.py` / `sw_simulation_study_options.py` | **行内改写 3 行**（补上游桶 token，零新增行、零删除） |
| 接线 | `scripts/release_check.py` | 改：`_run_dispatch_upstream_gate` + fail 判据 + `_gate_results` |
| 登记 | `docs/gate-classification.json` | 改：`classification` **45 → 46**（`+6 / -0` 行） |
| 探针 | `output/_probe236_upstream.py` · `output/_probe236_facts.py` | 一次性（**不进仓库代码**） |
| 规格 | `specs/236-dispatch-upstream-guard/{spec,plan,tasks,acceptance}.md` | **新增** |

## 二、★ 先量（本规格的起点，探针输出）

| # | `upstream` 声明位置 | 上游 `def` | AST 调用点 | ToolSpec 引用 | **桶** |
|---|---|---|---|---|---|
| 1 | `sw_drawing_create_missing.py:286` | `_sum_over_views` | **10**（全字面量 · 5 distinct） | 0 | **`sites`** |
| 2 | `sw_drawing_view.py:391` | `call_view_no_args` | **0** | 0 | **`orphan`** |
| 3 | `sw_simulation_study_options.py:905` | `set_study_option_report` | **0** | **1** | **`tool-only`** |

5 个候选值 `GetSFSymbolCount` / `GetDatumTagCount` / `GetNoteCount` / `GetAnnotationCount` /
`GetCenterLineCount` —— **全部**在官方两源（转储 18411 名 ∪ swapi）里查到 ✓。

## 三、判据读数

| 判据 | 命令 | 读数 |
|---|---|---|
| 门禁本体（真树） | `python -B scripts/check_dispatch_upstream_guard.py` | `upstream 声明 3 · 上游调用点 10 · 字面量候选值 distinct 5 · 桶 sites 1 / tool-only 1 / orphan 1 · 违规 0 · [PASS] · exit 0` |
| ★ **红基线（证明能红）** | 同上，**补桶之前** | `[FAIL] 违规 3 处`（三条声明**都未表态上游桶**，`[invalid-claim]`）· **exit 1** |
| ★ **变异检验** | 把 `judge()` 首行改成 `return []` 后跑判据 | `Ran 18 tests · FAILED (failures=8)` ⇒ 判据**不是空判据**；已 `md5sum` 复核还原 |
| 本规格判据 | `python -B tests/test_dispatch_upstream_guard.py` | **Ran 18 tests · OK**（17.5 s） |
| 235 回归（★ 声明语法向后兼容） | `python -B tests/test_dispatch_forward_arg_guard.py` | **Ran 19 tests · OK**（22.4 s） |

## 四、判据清单（18 例）

- **真树 1 例**：`(3, 10, 5, 0)` + `桶 sites 1 / tool-only 1 / orphan 1`。
- **合成树端到端负例 13 例**：`sites` 正样本 · `orphan` 正样本 · `tool-only` 正样本 ·
  未表态桶 · 桶不在词表 · 缺理由 · `sites` 却无调用点（事实 `orphan`） ·
  `sites` 的调用点非字面量 · 候选值官方查不到 · `orphan` 却有 ToolSpec 引用（事实 `tool-only`） ·
  `tool-only` 却有调用点（事实 `sites`） · 零检查 · 下界收缩。
- **取实参形态 3 例**：按**形参名下标**取（`name` 不是最后一个）· 关键字优先 · 取不到返回 `None` 不降级。
- **源隔离 1 例**：合成树只看到合成转储/swapi（`官方成员名 3 个`，**不含** `18460`）。

## 五、★ 本规格的实质结论

### 5.1 `upstream` 是**半开的逃生门**（本规格封上）

spec 235 的 `upstream` 只自证：① 实参是包围 `def` 的形参；② 包围 `def` 名 == 声明的 caller 名。
★ **它从不检查那个 caller 的调用方到底传了什么** ⇒ 写 `upstream X` 只要 X 恰好合格就**永远绿**。
本规格要求声明**带上游桶且桶与事实相符**，把「写了」变成「写了且对得上」。

### 5.2 ★★ 「AST 调用点为 0」**不等于**「没人用」——所以 `tool-only` 这一档是必需的

`set_study_option_report` 的 AST 调用点是 **0**，但它是**工具层按名注册**的
（`mcp-server/tool_specs_batch37.py:96` 的 `function="set_study_option_report"`）
⇒ 若只有 `orphan` 一档，它会被**误判成死代码**。这是 spec 234「窄读取器读出 0 也会骗人」的同族形态。

### 5.3 ★★ 交接单的前提**又错了一半**（连续第 6 轮）

待办 1 写「3 个 `upstream` 的上游仍未被守卫；若大多是字面量 ⇒ 该升级成 `entries`，
**但这会动 229 的下界常量**（37 / 18 / 327）」。**先量**后：

- 「3 个上游」里**只有 1 个**（`_sum_over_views`）**有**调用点 ⇒ **无需**扩 `entries`，
  ★ **229 的任何常量一个都没动**（`_sum_over_views` **不是**分发口，它的字面量在**调用方**那一层）；
- 另两个的上游 `def` 的 AST 调用点**都是 0** ⇒ 「递归解析」对它们**没有靶子**。

## 六、未过门（如实登记）

1. **桶的判定是静态的**：`tool-only` 只证明「名字出现在 ToolSpec 的 `function=`」，
   **不证明**该 ToolSpec 真会被调用、也不证明其成员名实参真来自运行期（**需真机**）。
2. `sites` 桶只核**成员名实参**，不核 `arity` / by-ref 占位（那是 228 / 231 的职责）。
3. **不判接口归属**：候选值只判「名字在两源里存在」（属 `check_interface_member_ownership.py`）。
4. **只核一层**：`sites` 桶的上游调用点若又用变量传名 ⇒ 本门禁只**红**，不继续追。
5. `call_view_no_args` 的 **orphan 状态未处理**（是否该保留是**能力层**的决定，本规格只登记）。
6. 真机未验（本切片全程离线）；223 的 8 条 `HEAD` 即红既有失败未修；未提交未部署。

## 七、本轮自己踩到的坑（供下一轮）

1. ★ **首版留了一个不可达分支**：`find_def()` 按名找上游 `def` —— 但上游 `def` **就是包围 `def`**
   （声明的 caller 名必须等于它），所以那个「找不到 `def`」的分支**永远跑不到**。
   ⇒ 已**删除** `find_def()`，直接用 `encl`。★ 教训：**先想清两个取点是不是同一个东西**，
   否则会写出一条「没有靶子的守卫」（spec 232 同族）。
2. ★ `Edit` 往 `release_check.py` 插函数后**立刻复核相邻 `# ── 来源 ──` 头** ⇒ 本轮**没有**吞头
   （231/233/234 三次都吞了，235/236 按规矩做都没吞）。
3. ★ 判据**首跑就 18/18 绿** —— 这本身是可疑信号 ⇒ 立刻做**变异检验**（短路 `judge`）
   拿到 `failures=8` 才算证完「判据不是空判据」。
