# Acceptance — 两条独立的路都建不出基体法兰

**Feature**: `specs/264-base-flange-two-paths/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 4/4 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ **现代路与老路都回 `None`** ⇒ ★★ **失败在环境/前置，不是「我们怎么用现代路」**。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 两条都失败 ⇒ 环境/前置 | `test_both_paths_fail_so_it_is_environmental` | ✅ `environment-or-precondition` |
| FR-002 | ★★ 老路按官方 19 参签名 | `test_legacy_path_was_called_with_the_full_signature` | ✅ 19 参 |
| FR-003 | ★★ 坑留档 | `test_pitfall_is_recorded` | ✅ `PCBA` / 类型不匹配 |
| FR-004 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 三组负例全红 |

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ |
| ★ **一条成功** | 判别翻成 `our-usage` + 报错 | ✅ `our-usage` · `["'老路 InsertSheetMetalBaseFlange2' 竟然成功了 ⇒ ★ 结论要改（★ 判别逻辑会翻）"]` |
| 只给一条读数 | 报错 | ✅ |
| 签名参数量错 | 报错 | ✅ |

## 三、★★★ 真机读数

| 路 | 结果 |
|---|---|
| ★ **现代路** `CreateDefinition` + `CreateFeature` | ★ **回 `None`** |
| ★★ **老路** `InsertSheetMetalBaseFlange2`（★ 19 参全给 · `cba` 是真对象） | ★★ **也回 `None`** |

⇒ ★★★ **两条独立的路都失败** ⇒ ★★ **失败不在「我们怎么用现代路」**，★ **在环境/前置**。

## 四、★★ 官方事实（★ 纠正一个可能的误解）

★ `InsertSheetMetalBaseFlange2` **本身也是废弃的**：
「Obsolete. Superseded by [[IFeatureManager::CreateDefinition]] and [[IFeatureManager::CreateFeature]]。」
⇒ ★★ **官方指认「现代路」才是正确入口** ⇒ ★ **老路不是更正确的替代**（★ 本探针只用它做判别）。

## 五、★★ 探针踩的坑

★ 老路第 **10 参** `PCBA` 要 `CustomBendAllowance` **对象** ⇒ ★ 传 `None` 抛
`com_error(-2147352571, '类型不匹配')`（★ **不报是哪个参数**）。

## 六、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47** |

★ **生成器链未跑**（★ 没改 `scripts/`）。

## 七、未过门（如实登记）

1. ★★ **根因仍未定到可改的点** —— ★ 已排除：顺序 · 常量 · 选前 · **现代路的用法**。
   ★ **下一步线索**：① **查钣金选项卡/插件是否激活** · ② 换 `Top` 平面 · ③ 查 SW 版本/许可是否限制钣金。
2. `_read_k_factor` 仍未被真机走到（★ 阻塞 = 造不出件）。
3. 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · `create_hem` · 223 的 8 条既有红 · 未提交未部署。
