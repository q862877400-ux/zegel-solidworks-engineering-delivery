# Spec — **换路由第 1 批**：`KFactor` / `MaterialIdName` 两处已改 + 真机复验

**Feature**: `specs/261-routing-batch1-adapt-args/`
**日期**: 2026-10-10
**上游**: `specs/260-routing-plan-real-hits/`（★ 7 处计划；★ 本文件做 `adapt-args` 那批）
**本轮只做一件事**：把 7 处里**便宜的 2 处**真正改掉，并**真机复验**。

---

## 一、★★★ 改了什么

| # | 文件 | 改法 |
|---|---|---|
| 1 | `scripts/sw_sheet_metal.py` | 新增 `_read_k_factor(definition)`：`GetCustomBendAllowance()` ⇒ 再取 `ICustomBendAllowance.KFactor`；★ 原 `get_com_member(definition, "KFactor")` 已删 |
| 2 | `scripts/sw_simulation.py` | 新增 `_read_material_id_name(model)`：`GetMaterialPropertyName2("", byref)`；★ 原 `get_com_member(model, "MaterialIdName")` 已删 |

---

## 二、★★★ 真机复验（`output/_probe261_verify.py` · SW rev **34.4.1**）

★ 零件 `output/fixtures/刀柄_Holder.sldprt`，★ **可写**打开（★ 为了赋材料拿非空读数）、**结束 `QuitDoc` 不保存**
⇒ ★ 事后核 **mtime 未变**（`09-27 11:37`）✓。

| 写法 | 读数 |
|---|---|
| ★ 新 `GetMaterialPropertyName2("", byref)` | **`'AISI 1020'`** ← ★ **纯材料名** |
| 旧 `MaterialIdName`（废弃） | **`'solidworks materials\|AISI 1020\|2'`** ← ★ **库名\|材料名\|编号** |
| ★★ 两代一致？ | ★ **否** —— ★ **语义不同**（★ 不是同值） |

★★★ **这是本轮最重要的发现**：★ **换路由不是「同值改名」** —— ★ 返回值**语义变了**。
★ 换后**语义更好**（现在可直接与 `material_name` 比），★ 但**必须如实记录**。

### ★★ `_read_k_factor` **未被走到**（★ 如实登记）

★ 该零件**没有钣金基体法兰**（22 个特征里没有 `BaseFlange`）⇒ ★ `_read_k_factor` **在真机上没被执行**。
★★ **缺数据源 ≠ 检查失败**，★ 但**不能据此宣称它验过**。

---

## 三、★★★ 三条教训（★ 都由判据抓出来）

### 1. **判「是不是废弃调用」必须看宿主接口**（★ 不是只看成员名）
★ 本判据第一版**只按成员名** ⇒ ★ 把**我自己新写的** `get_com_member(cba, "KFactor")` 判成了违规 ——
★ 而 `cba` 是 **`ICustomBendAllowance`**、★ 它上面的 `KFactor` **不废弃**。
⇒ ★★ **定则：同一个成员名在不同接口上废弃状态不同**（★ 与 245/248/250 同一条）。

### 2. **行为变化的**安全性**取决于「调用方怎么用它」，不是「有没有人用」**
★ 我写「全仓没有 `set_material` 的调用方」⇒ ★ **当场红**：实测 **16 处**（★ 都在 `tools/` 的证据采集脚本里）。
★ 逐个核过：★ 它们只用 `bool(返回值)` 与**直接存值** ⇒ ★ **不依赖旧格式** ⇒ 变化安全。
★★ **判据要核的是「怎么用」，不是「有没有用」**。

### 3. **函数名要核准** —— ★ 是 `set_material`，★ 不是 `assign_material`
★ 我第一版 docstring 写的是 `assign_material` ⇒ ★ 判据扫出来才发现真名是 **`set_material`**。

---

## 四、需求

### FR-001 ★★★ 2 处的废弃调用**已清**（★ 按**名字 + 宿主**判）
- **验收场景**：`test_batch1_deprecated_calls_are_gone` 通过；
  ★★ **能红的判据**：★ 改回任一处即红。

### FR-002 ★★★ 真机读数必须记录**语义变化**（★ 两代不等价）
- **规则**：新 `'AISI 1020'` · 旧 `'solidworks materials|AISI 1020|2'` · `equivalent = False`；
  ★ 且 `set_material` 的 docstring 必须**写着**这个变化。
- **验收场景**：`test_machine_readings_record_the_semantic_change` 通过。

### FR-003 ★★★ 调用方**不许**依赖旧格式
- **规则**：全仓扫 `set_material(` 的调用行，★ **不许**出现 `.split(` / `.startswith(` / `.replace(` / `|` 等格式相关操作。
- **验收场景**：`test_no_caller_depends_on_the_old_format` 通过。

### FR-004 ★★★ `DeleteRenderMaterial` **重分类**（★ 推翻 260 的 `adapt-args`）
- **规则**：★ 后继 `DeleteDisplayStateSpecificRenderMaterial(PWMaterialId1, PWMaterialId2)` **按外观 ID 删**
  ⇒ ★ 要先调 `IRenderMaterial::GetMaterialIds` ⇒ ★ **不是 `adapt-args`**。
- **验收场景**：`test_delete_render_material_is_reclassified` 通过。

### FR-005 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过。

---

## 五、非目标

- **不**动 `DeleteRenderMaterial`（★ 已重分类 ⇒ ★ 要另开切片）。
- **不**动 4 处 `needs-feature-data`（★ 大改）。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 合成残留 ⇒ 报错；★ `KFactor`/`cba` **不**判违规（★ 按宿主判） |
| SC-2 | 判据**是绿的** | `tests/test_routing_batch1_adapt_args.py` **5/5 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 生成器链 | 7 步全 OK（★ 改了 `scripts/`） |
| SC-5 | ★ 真机只读/不落地 | 零件 **mtime 未变**（`09-27 11:37`） |

## 七、未过门（本轮不做，如实登记）

- **`_read_k_factor` 未被真机走到** —— ★ 该零件没有钣金基体法兰。★ **触发条件** = 拿一个有 `BaseFlange` 的零件。
- **`DeleteRenderMaterial` 未改**（★ 已重分类 ⇒ 要拿外观 ID）。
- **4 处 `needs-feature-data`** 未改（★ 大改）。
- 高危写盘 · `create_hem` 行为证据 · 223 的 8 条既有红 · 未提交未部署。
