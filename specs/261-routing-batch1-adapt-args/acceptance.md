# Acceptance — 换路由第 1 批（KFactor / MaterialIdName）

**Feature**: `specs/261-routing-batch1-adapt-args/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立 · 生成器链 7 步 OK · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ **2 处已换路由**；★★★ **真机证明两代**不等价**（语义变了）** —— ★ 已如实记录。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 2 处废弃调用已清 | `test_batch1_deprecated_calls_are_gone` | ✅ **0**（★ 按名字 + 宿主判） |
| FR-002 | ★★★ 记录语义变化 | `test_machine_readings_record_the_semantic_change` | ✅ 新 `'AISI 1020'` ≠ 旧 `'solidworks materials\|AISI 1020\|2'` |
| FR-003 | ★★★ 调用方不许依赖旧格式 | `test_no_caller_depends_on_the_old_format` | ✅ 16 处调用，**无一处**做格式操作 |
| FR-004 | ★★★ `DeleteRenderMaterial` 重分类 | `test_delete_render_material_is_reclassified` | ✅ 推翻 260 的 `adapt-args` |
| FR-005 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 三组负例全红 |

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 空表 | `[]` | ✅ |
| 合成残留 | 报错 + 带位置 | ✅ `['sw_simulation.py:803 仍在调废弃的 MaterialIdName']` |
| ★★ 真扫 `KFactor`/`definition`（废弃宿主） | `[]` | ✅ **`[]`** |
| ★★ 真扫 `KFactor`/`cba`（**非废弃**宿主） | ★ **找得到，但不算违规** | ✅ `[(211, 'KFactor')]` —— ★ **按宿主判生效** |

## 三、★★★ 真机复验

★ 零件 `output/fixtures/刀柄_Holder.sldprt` · **可写**打开 · 赋 `AISI 1020` · **`QuitDoc` 不保存**。

| 写法 | 读数 |
|---|---|
| ★ 新 `GetMaterialPropertyName2("", byref)` | **`'AISI 1020'`** |
| 旧 `MaterialIdName`（废弃） | **`'solidworks materials\|AISI 1020\|2'`** |
| ★★ 一致？ | ★ **否** —— **语义不同** |

★ **夹具零件未被改**：mtime 仍 `09-27 11:37` ✓。

★ **`_read_k_factor` 未被走到**（★ 该零件没有 `BaseFlange`）⇒ ★ **如实登记为「未验」**。

## 四、★★★ 三条教训（★ 都由判据抓出）

1. ★★★ **判「是不是废弃调用」必须看宿主接口** —— ★ 第一版**只按成员名** ⇒ ★ 把**我自己新写的**
   `get_com_member(cba, "KFactor")` 判成违规（★ `cba` 是 `ICustomBendAllowance`、★ **不废弃**）。
2. ★★★ **行为变化的**安全性**取决于「调用方怎么用它」，不是「有没有人用」** ——
   ★ 我写「全仓没有调用方」⇒ ★ **当场红**：实测 **16 处**；★ 逐个核过都只用 `bool()` 与直接存值 ⇒ 安全。
3. ★★ **函数名要核准** —— ★ 是 `set_material`，★ 我第一版写成了 `assign_material`。

## 五、生成器链（★ 改了 `scripts/` ⇒ 必跑）

★ `sync_bundled_skill` → `gen_level_audit` → `gen_metrics` → `gen_harvest_digest` → `build_union_map` →
`gen_dead_ends` → `sync_bundled_skill` ⇒ ✅ **7/7 OK**。

## 六、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47** |

## 七、未过门（如实登记）

1. **`_read_k_factor` 未被真机走到** —— ★ 该零件没有钣金基体法兰。★ **触发条件** = 拿一个有 `BaseFlange` 的零件。
2. **`DeleteRenderMaterial` 未改**（★ 已重分类 ⇒ 要先用 `IRenderMaterial::GetMaterialIds` 拿外观 ID）。
3. **4 处 `needs-feature-data`** 未改（★ 大改：要先造 `ILinearPatternFeatureData` / `ILocalCurvePatternFeatureData` / `IFormToolFeatureData`）。
4. 高危写盘 · `create_hem` 行为证据 · 223 的 8 条既有红 · 未提交未部署。
