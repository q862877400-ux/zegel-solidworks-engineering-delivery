# Acceptance — `IView::Name` 换路由（4 处真命中改掉）

**Feature**: `specs/256-iview-name-routing-done/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 4/4 绿 · 红基线成立 · 生成器链 7 步 OK · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★ **4 处 `IView::Name` 真命中全部改掉** —— 3 处去掉废弃兜底、1 处换成官方后继 `GetName2`。

---

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ `scripts/` 里无对 `view`/`av` 调 `Name` | `test_no_deprecated_name_call_on_view_hosts` | ✅ **0 处**（grep 亦为空） |
| FR-002 | ★★ 换路由依据留在判据里 | `test_routing_evidence_is_recorded` | ✅ `diff=0` · 真实视图 **3** · 合计 **5** |
| FR-003 | ★ 替换点是官方后继 | `test_replacement_uses_the_official_successor` | ✅ `get_com_member(av, "GetName2")` |
| FR-004 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 合成残留 ⇒ 报出；空表 ⇒ 通过 |
| FR-005 | 按名字定位不按行号 | AST + 宿主名 | ✅ |
| FR-006 | ★★ 生成器链 | 7 步 | ✅ **全 OK** |

---

## 二、★★ 红基线

| 变异 | 期望 | 实测 |
|---|---|---|
| 空表 | 通过 | ✅ `[]` |
| 合成残留（`sw_drawing_view.py:436` 宿主 `view`） | 报出 + 带位置 | ✅ **`["sw_drawing_view.py:436 仍在调废弃的 \`IView::Name\`（宿主 'view'）"]`** |
| ★ 把任一处**真的**改回 `get_com_member(view, "Name")` | 判据红 | ✅（★ 由 AST 判据覆盖） |

---

## 三、★★★ 拍板记录（★ 授权 E）

★ **主代理拍板**：达「**两轮合计 ≥5 个视图、且异 0**」即换路由。

| 依据 | 读数 |
|---|---|
| 官方 | `IView/Name.md` 首行「Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]]」 |
| 真机 254 | `pdf-probe.SLDDRW` **1** 视图（伪）· `Name` == `GetName2` |
| 真机 255 | 造图 **4** 视图（**3 真实模型视图**）· `Name` == `GetName2` **全部相同** |
| ★ 合计 | ★ **5 视图 · 异 0** |

★ **如实记录**：★ 这是**主代理拍的板**，★ 不是业主逐条确认的。
★ 256 的探针想再补一个 `*Isometric` 视图，`CreateDrawViewFromModelView3` 回 **`None`** ⇒ ★ **未纠缠**（★ 依据已足）。

---

## 四、★★ 改动面（★ 4 处）

| # | 文件 | 改法 |
|---|---|---|
| 1 | `sw_drawing_query.py:194` | `get_com_member(view, "Name")` ⇒ ★ **`name = ""`** |
| 2 | `sw_drawing_query.py:264` | 同上 |
| 3 | `sw_drawing_view.py:436` | `get_com_member(view, "Name")` ⇒ ★ **`return ""`** |
| 4 | `sw_review.py:637` | `get_com_member(av, "Name")` ⇒ ★ **`get_com_member(av, "GetName2")`** |

★ **未改**：其它 `Name` 调用（★ 248 判过 **47 处是假命中**，★ 属别的接口）。

---

## 五、生成器链（★ 改了 `scripts/` ⇒ 必跑）

| 步骤 | 结果 |
|---|---|
| `scripts/release_check.py` | ✅ OK |
| `scripts/gen_level_audit.py` | ✅ OK |
| `tools/gen_metrics.py` | ✅ OK |
| `tools/gen_harvest_digest.py` | ✅ OK |
| `tools/build_union_map.py` | ✅ OK |
| `tools/gen_dead_ends.py` | ✅ OK |
| `scripts/release_check.py`（★ 头尾各一次） | ✅ OK |

---

## 六、门禁全套 @3.14.7

### ★★ 首跑**红**（★ 已修）—— `[baseline-shrunk] 可见调用点 1180 < 下界 1183`

| 项 | 内容 |
|---|---|
| **根因** | ★ 我删了 **3 处字面量调用点**（`sw_drawing_query.py:194`/`:264` + `sw_drawing_view.py:436` 的兜底）⇒ 可见调用点 **1183 → 1180** ⇒ **棘轮红**；★ `sw_review.py:637` 是**同位置换名**（净 0） |
| **正当性** | ★★ 那 3 处是**调废弃成员**，★ **删它们是本切片的目的、不是副作用** |
| **处置 ①** | `scripts/check_dispatch_entry_guard.py` 的 `BASELINE_VISIBLE` **1183 → 1180**，★ 注释写明理由 |
| **处置 ②（内容断言）** | ★ `tests/test_iview_name_routing_done.py` —— ★ AST 按名字断言「对 `view`/`av` 调 `Name` 的处数 == 0」+ 「`sw_review.py` 用的是官方后继 `GetName2`」 |
| **复跑** | ★ 改了 `scripts/` ⇒ **生成器链 7 步重跑**（全 OK）；★ 单跑该门禁 ⇒ `[PASS] · exit 0` |

### 复跑后的全套读数

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47** |

★★ **教训（★ 已写进 memory）**：★ **「换路由」这种「删废弃调用」的切片，必然压低棘轮下界**
⇒ ★ **立项时就该把「下界同步 + 内容断言」写进 `tasks.md`**。

---

## 七、未过门（如实登记）

1. **换路由后未做真机复验** —— ★ 改的是**异常路径**（1/2/3）与一处直读（4）；
   ★ 254/255 已证两个成员**等价**，★ 但**没在真机上跑过改后的函数**。★ **触发条件** = 打开一张图纸调这两个函数。
2. **250 的 7 处真命中**仍未换路由。
3. **251 的 `SketchTrim` 4 处**仍未换路由。
4. **高危写盘**（`SaveAs3` · `create_draft` · `create_profile_center_mate`）。
5. **10 条 `byref-tail` 真机验证** · **门禁 R8 每日跨天假红** · **223 的 8 条既有红**。
6. **未提交 / 未部署**；**未删任何文件**。
