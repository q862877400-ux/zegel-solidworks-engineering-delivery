# Spec — **两条独立的路都建不出基体法兰** ⇒ 失败在**环境/前置**

**Feature**: `specs/264-base-flange-two-paths/`
**日期**: 2026-10-10
**上游**: `specs/263-base-flange-failure-layers/`（★ 把失败点定位到 `CreateFeature`）
**本轮只做一件事**：★ 用**另一条独立的路**做**判别** —— ★ 失败在「我们怎么用现代路」，还是**环境**？

---

## 一、★★★ 判别设计

★ 263 只证明了「**现代路**（`CreateDefinition` + `CreateFeature`）在 `CreateFeature` 回 `None`」。
★★ 但那**不足以**区分两件事：
1. ★ **我们没把现代路用对**（★ 该调参数、该补前置）
2. ★ **环境/前置**（★ 与用哪条路无关）

⇒ ★★ **判别办法**：★ 用**另一条完全独立的路**试一遍。
★ 选 **`IFeatureManager::InsertSheetMetalBaseFlange2`**（★ 19 参、★ **一次调用就建**，★ 不经过 `CreateDefinition`）。

---

## 二、★★★ 真机读数（`output/_probe264_legacy.py` · SW rev **34.4.1**）

| 路 | 结果 |
|---|---|
| ★ **现代路** `CreateDefinition` + `CreateFeature` | ★ **回 `None`** |
| ★★ **老路** `InsertSheetMetalBaseFlange2`（★ 19 参全给） | ★★ **也回 `None`** |

⇒ ★★★ **两条独立的路都失败** ⇒ ★★ **失败不在「我们怎么用现代路」**，★ **在环境/前置**。

★★ **为什么这条值钱**：★ 没有它 ⇒ ★ 下一轮还会去「调现代路的参数」；
★ 有了它 ⇒ ★ **方向转到环境/前置**。

---

## 三、★★ 一条官方事实（★ 顺带纠正一个可能的误解）

★ `InsertSheetMetalBaseFlange2` **本身也是废弃的**，★ 逐字：

> **Obsolete. Superseded by [[IFeatureManager::CreateDefinition]] and [[IFeatureManager::CreateFeature]].**

⇒ ★★ **官方明确指认「现代路」才是正确入口** ⇒ ★ **老路不是「更正确的替代」**，
★ 本探针用它**只为判别**（★ 不是要换路由）。

---

## 四、★★ 探针踩的坑（★ 留档）

★ 老路第 **10 参** `PCBA` 要的是 **`CustomBendAllowance` 对象** —— ★ 传 `None` 抛
`com_error(-2147352571, '类型不匹配')`（★ 而且**不报是哪个参数**）。
⇒ ★ 要传真的对象（★ `manager.CreateCustomBendAllowance()`）。

---

## 五、需求

### FR-001 ★★★ 两条独立路都失败 ⇒ 判「环境/前置」
- **规则**：两条都回 `None` ⇒ `environment-or-precondition`；★ **任一条成功 ⇒ 判别翻成 `our-usage`**。
- **验收场景**：`test_both_paths_fail_so_it_is_environmental` 通过；
  ★★ **能红的判据**：★ 一条成功 ⇒ 当场红（★ 结论要改）。

### FR-002 ★★ 老路按**官方 19 参签名**调（★ 排除「少给参数」）
- **验收场景**：`test_legacy_path_was_called_with_the_full_signature` 通过。

### FR-003 ★★ 探针踩的坑留档
- **验收场景**：`test_pitfall_is_recorded` 通过。

### FR-004 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过。

---

## 六、非目标

- **不**改 `scripts/`（★ 根因仍未定到可改的点）⇒ ★ **不跑生成器链**。
- **不**换路由到老路（★ 它**也是废弃的**）。

## 七、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 一条成功 ⇒ 判别翻 + 报错；只给一条读数 ⇒ 报错；签名参数量错 ⇒ 报错 |
| SC-2 | 判据**是绿的** | `tests/test_base_flange_two_paths.py` **4/4 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 真机 | 护栏预检「读到文档 0 个」· ★ 临时零件**已关闭** |

## 八、未过门（本轮不做，如实登记）

- ★★ **根因仍未定到可改的点** —— ★ 已排除：顺序 · 常量 · 选前 · **现代路的用法**（★ 两条路都失败）。
  ★ **下一步线索**：① **查钣金选项卡/插件是否激活**（★ `CreateFeature` 的 Remarks 提过「Sheet Metal tab 要可见」）；
  ② 换官方示例用的 **`Top` 平面**；③ 查 SW 版本/许可是否限制了钣金。
- `_read_k_factor` 仍未被真机走到（★ 阻塞 = 造不出件）。
- 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · `create_hem` · 223 的 8 条既有红 · 未提交未部署。
