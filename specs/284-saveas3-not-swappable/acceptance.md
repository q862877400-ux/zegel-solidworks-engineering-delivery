# Acceptance — `SaveAs3` 真机静默失败 ⇒ 不换

**Feature**: `specs/284-saveas3-not-swappable/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立 · 生成器链 7/7 · 真机无残留 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★★★ **不换** —— ★ `SaveAs3` 在本机**静默失败**（★ 返回 `True` 却不落盘）
⇒ ★★ **照官方链硬换会**静默坏掉写盘**** ⇒ ★ **保持 `SaveAs`**（★ 「先量」救了一次）。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 四个 Options 全静默失败 | `test_saveas3_silently_fails_for_every_option` | ✅ 都不落盘 |
| FR-002 | ★★ 对照 `SaveAs` 真的落盘 | `test_the_current_saveas_actually_writes` | ✅ 48696 B |
| FR-003 | ★★★ 官方说要换、本机不能换 | `test_official_chain_says_switch_but_machine_says_no` | ✅ |
| FR-004 | ★★★ `save_document` 仍走 `SaveAs` | `test_save_document_still_uses_saveas` | ✅ 回源码核 |
| FR-005 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 六组负例全红 |

## 二、★★★ 真机读数（SW **34.4.1** · ★ 走 `sw_guard` · ★ 看**文件是否真的落盘**）

| 入口 | 返回 | `errors` | ★ **文件存在？** |
|---|---|---|---|
| `SaveAs3(path, 0, 1, empty, adv, e, w)`（★ `GetAdvancedSaveAsOptions(0)`） | ★ **`True`** | **0** | ★★ **`False`** |
| `SaveAs3` × `Options=1` | **`True`** | 0 | **`False`** |
| `SaveAs3` × `Options=2` | **`True`** | 0 | **`False`** |
| `SaveAs3` × `Options=3` | **`True`** | 0 | **`False`** |
| ★ **对照**：`SaveAs(path, 0, 1, empty, e, w)`（★ 现状） | **`True`** | 0 | ★ **`True`**（**48696 B**） |

★★★ **⇒ `SaveAs3` 在本机**静默失败**** —— ★ **四个 `Options` 全返回 `True`、`errors=0`，★ 而文件一个都没写出来**。
★★★ **⇒ 绝不能换** —— ★★ 换了就是「存成功了」的假象 + 实际没落盘（★ 比「报错」**更危险**）。
★ 读数原文 `output/_probe284_saveas3.txt` · `output/_probe284_saveas3_opt.txt`。

## 三、★★★ 官方链说要换、本机不能换

| 成员 | ★ 官方页逐字 |
|---|---|
| `SaveAs` | ★ **`Obsolete. Superseded by [[IModelDocExtension::SaveAs2]]`** |
| `SaveAs2` | ★ **`Obsolete. Superseded by [[IModelDocExtension::SaveAs3]]`** |
| ★ `SaveAs3` | ★ **无 `Obsolete`** ⇒ ★ **链终点** |

★ `SaveAs3` 的 Remarks 逐字：「To specify the AdvancedSaveAsOptions parameter of this method,
call **`IModelDocExtension::GetAdvancedSaveAsOptions`**」⇒ ★ 本轮**照它做了**（★ 三源一致：
★ 官方页 / 取代链 / 反射 `GetAdvancedSaveAsOptions(Int32)`）。
★★★ **而真机证明：★ 照官方链换会**静默坏掉写盘**** ⇒ ★★ **处置：★ 保持 `SaveAs` + 把实测登记下来**。

## 四、★★★ 登记（★ `scripts/sw_connect.py`）

| 位置 | 内容 |
|---|---|
| ★ `save_document` 的**来源块**（★ **注释**） | ★ 完整实测（★ 四个 `Options` · ★ 对照 48696 B · ★ 官方链 · ★ 处置） |
| ★ `save_document` 的**文档串** | ★ **一行**警示：「⚠★ **不要换成 `SaveAs3`** —— ★ 真机实测它**静默失败**」 |

★ **行为未改**（★ 仍走 `SaveAs`）· ★ 长文本写**注释**（★ 吸取 **282** 的教训）。

## 五、★★ 红基线（★ 六组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| Options 数不对 | 报错 | ✅ `['★ 应测 4 个 Options，实测 1']` |
| 某个回 False | 报错 | ✅ `['★ 四个 Options 都应**返回 True**']` |
| 某个落了盘 | 报错 | ✅ `['★ 四个 Options 都应**不落盘**（★ 那才是「静默失败」）']` |
| 对照没落盘 | 报错 | ✅ `['★ 对照 `SaveAs` 应**真的落盘**']` |
| 结论不是「不换」 | 报错 | ✅ `['★ 结论必须是**不换**']` |
| 源码出现 `SaveAs3(` | 报错 | ✅ `['★★★ `save_document` **不该**出现 `SaveAs3(` 调用（★ 那会静默坏掉写盘）']` |

## 六、生成器链（★ 改了 `scripts/`）

| 步骤 | 结果 |
|---|---|
| `release_check.py` → `gen_level_audit.py` → `gen_metrics.py` → `gen_harvest_digest.py` → `build_union_map.py` → `gen_dead_ends.py` → `release_check.py` | **7/7 `exit 0`** |

★ 改完**先 `ast.parse`**（★ 282 的教训）。

## 七、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate284.log` |

★ 真机预检前后均「**读到文档 0 个**」⇒ **无残留**。

## 八、未过门（如实登记）

1. ★★★ **`create_profile_center_mate` 未真机验证**（★ §三 C **已授权**）⇒ ★ 下一轮。
2. ★★ **`SaveAs3` 为什么静默失败**未查（★ 本轮只测了「**换不换**」）⇒ ★ 只登记。
3. ★★ **`create_draft` 的 `pre_call` 未接**（★ 否则 MCP 表面**仍然**建不出来）。
4. 12 条 `arity` 接线 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。
