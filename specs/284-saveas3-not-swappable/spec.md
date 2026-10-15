# Spec — `SaveAs3` **真机静默失败** ⇒ ★★ **不换**（★ 换了会静默坏掉写盘）

**Feature**: `specs/284-saveas3-not-swappable/`
**日期**: 2026-10-10
**上游**: ★ ② 段第 3 条（★ 原话：「`sw_connect.py:1167` 的 `Extension.SaveAs` → `SaveAs3`（★ **改错会直接坏掉写盘**）」）
**授权**: ★ 业主**已授权**（`GOAL.md` §三 **C · 高危/写盘**）
**本轮只做一件事**：★ **先量** —— ★ 换之前**真机试一次** `SaveAs3`。

---

## 一、★★★ 真机读数（SW **34.4.1** · ★ 走 `sw_guard`）

★ 夹具：★ 一个新零件 · ★ 存到**临时目录** · ★ 每次都**检查文件是否真的存在**。

| 入口 | 返回 | `errors` | ★ **文件存在？** |
|---|---|---|---|
| ★ `SaveAs3(path, 0, 1, empty, adv, e, w)`（★ `GetAdvancedSaveAsOptions(0)`） | ★ **`True`** | **0** | ★★ **`False`** |
| `SaveAs3` × `Options=1` | **`True`** | 0 | **`False`** |
| `SaveAs3` × `Options=2` | **`True`** | 0 | **`False`** |
| `SaveAs3` × `Options=3` | **`True`** | 0 | **`False`** |
| ★ **对照**：`SaveAs(path, 0, 1, empty, e, w)`（★ 现状） | **`True`** | 0 | ★ **`True`**（**48696 B**） |

★★★ **⇒ `SaveAs3` 在本机**静默失败**** —— ★ **四个 `Options` 全返回 `True`、`errors=0`，★ 而文件一个都没写出来**。
★★★ **⇒ 绝不能换** —— ★★ **换了就是「存成功了」的假象 + 实际没落盘**（★ 比「报错」**更危险**）。

---

## 二、★★★ 官方链**说要换**，★ 而本机**不能换**

| 成员 | ★ 官方页逐字 |
|---|---|
| `SaveAs` | ★ **`Obsolete. Superseded by [[IModelDocExtension::SaveAs2]]`** |
| `SaveAs2` | ★ **`Obsolete. Superseded by [[IModelDocExtension::SaveAs3]]`** |
| ★ `SaveAs3` | ★ **无 `Obsolete`** ⇒ ★ **链终点** |

★★ `SaveAs3` 的 Remarks 逐字：「To specify the AdvancedSaveAsOptions parameter of this method,
call **`IModelDocExtension::GetAdvancedSaveAsOptions`**」⇒ ★ 本轮**照它做了**（★ 三源一致：
★ 官方页 / 取代链 / 反射 `GetAdvancedSaveAsOptions(Int32)`）。
★★★ **而真机证明：★ 照官方链换会**静默坏掉写盘**** ⇒ ★★ **处置：★ 保持 `SaveAs` + 把实测登记下来**。

---

## 三、需求

### FR-001 ★★★ `SaveAs3` 四个 Options 全静默失败
- **验收场景**：`test_saveas3_silently_fails_for_every_option` 通过。

### FR-002 ★★ 对照：`SaveAs` 真的落盘
- **验收场景**：`test_the_current_saveas_actually_writes` 通过。

### FR-003 ★★★ 官方说要换、本机不能换
- **验收场景**：`test_official_chain_says_switch_but_machine_says_no` 通过。

### FR-004 ★★★ `save_document` **仍走 `SaveAs`**（★ 回源码核）
- **验收场景**：`test_save_document_still_uses_saveas` 通过。

### FR-005 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 六组负例）。

---

## 四、非目标

- ★★ **不换 `SaveAs3`**（★ 真机证明会坏）。
- ★ **不改** `save_document` 的行为（★ 只加**注释 + 一行文档串警示**）。
- ★ **不碰** `create_profile_center_mate`（★ 另开切片）。

## 五、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | Options 数不对 / 某个回 False / 某个落了盘 / 对照没落盘 / 结论不是「不换」/ 源码出现 `SaveAs3(` ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_saveas3_not_swappable.py` **5/5 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 生成器链已跑 | 7 步全 `exit 0`（★ 改了 `scripts/`） |
| SC-5 | ★ 真机无残留 | 护栏预检「读到文档 0 个」 |

## 六、未过门（本轮不做，如实登记）

- ★★★ **`create_profile_center_mate` 未真机验证**（★ §三 C **已授权**）⇒ ★ 下一轮。
- ★★ **`SaveAs3` 为什么静默失败**未查（★ 只测了「**换不换**」；★ 若要**查明**，★ 那是**另一件**工作）⇒ ★ 只登记。
- ★ 12 条 `arity` 接线 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。
