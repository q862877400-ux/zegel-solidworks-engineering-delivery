# Spec — `IView::Name` **换路由**（4 处真命中改掉）

**Feature**: `specs/256-iview-name-routing-done/`
**日期**: 2026-10-10
**上游**: `specs/254-iview-name-routing/`（先量）· `specs/255-multi-view-drawing-evidence/`（造图取证）
**本轮只做一件事**：把 **248 判出的 4 处 `IView::Name` 真命中**改掉。

---

## 一、★★★ 拍板依据（★ 授权 E：业主不在时由主代理拍板并如实记录）

| 依据 | 内容 |
|---|---|
| 官方 | `C:/swapi/types/IView/Name.md` 首行「**Obsolete. Superseded by [[IView::GetName2]] and [[IView::SetName2]]**」 |
| 真机 254 | `output/pdf-probe.SLDDRW` **1** 个视图（伪视图）：`Name` == `GetName2` |
| 真机 255 | `output/fixtures/刀柄_Holder.sldprt` 造图 **4** 个视图（**3 个真实模型视图**）：`Name` == `GetName2` **全部相同** |
| ★ 合计 | ★ **5 个视图 · 异 0** ⇒ ★ **等价成立** ⇒ **可换路由** |

★ **拍板**：★ 达「两轮合计 ≥5 个视图、且异 0」即换路由（★ 256 探针想补第 5 个视图返回 `None`，
★ 故**不纠缠** —— 两轮合计已 **5**，★ 依据充分）。
★ **如实记录**：★ 这是**主代理拍的板**，★ 不是业主逐条确认的。

---

## 二、4 处改动（★ 逐处）

| # | 站点 | 原写法 | 改法 | 为什么 |
|---|---|---|---|---|
| 1 | `sw_drawing_query.py:194` | `GetName2` 失败 ⇒ `get_com_member(view, "Name")` | ★ **`name = ""`** | ★ 失败就是**取不到名字**，★ **不换个废弃成员再试** |
| 2 | `sw_drawing_query.py:264` | 同上 | ★ **`name = ""`** | 同上 |
| 3 | `sw_drawing_view.py:436` | `GetName2` 为假 ⇒ `get_com_member(view, "Name")` | ★ **`return ""`** | 同上 |
| 4 | `sw_review.py:637` | ★ **直接**调 `get_com_member(av, "Name")` | ★ **换成 `GetName2`**（官方后继） | ★ 这才是真正的**换路由** |

★ 1/2/3 三处**本来就先调 `GetName2`** ⇒ ★ 去掉兜底**不影响正常路径**，★ 只在**异常路径**上不再碰废弃成员。

---

## 三、需求

### FR-001 ★★★ `scripts/` 里**不许**再有对 `view`/`av` 调 `Name`

- **来源**：248 的 4 处真命中。
- **规则**：AST 找 `get_com_member(<宿主>, "Name")` 且宿主 ∈ {`view`, `av`} ⇒ 必须为 **0**。
- **验收场景**：`test_no_deprecated_name_call_on_view_hosts` 通过；★ **能红的判据**：改回任一处即红。

### FR-002 ★★ 换路由的**依据**必须留在判据里

- **规则**：`diff == 0` · 真实模型视图 ≥3 · ★ 两轮样本合计 ≥5。
- **验收场景**：`test_routing_evidence_is_recorded` 通过。

### FR-003 ★ 替换点是**官方后继**

- **规则**：`sw_review.py` 那处必须是 `get_com_member(av, "GetName2")`。
- **验收场景**：`test_replacement_uses_the_official_successor` 通过。

### FR-004 ★★ 判据必须能红

- **验收场景**：`test_pure_function_is_red_able` 通过。

### FR-005 ★ **按名字定位，不按行号**

- **来源**：本仓铁律（「判据按名字定位，不按行号」）。
- **规则**：AST + 宿主名字，★ 不用行号。

### FR-006 ★★ 改了 `scripts/` ⇒ **必须跑生成器链**

- **验收场景**：7 步全 OK（★ 已跑）。

---

## 四、非目标

- **不**动其它 `Name` 调用（★ 248 判过：**47 处是假命中**，★ 属别的接口）。
- **不**改 `GetName2` 的调用形态（★ 它是**属性**，★ 不加括号）。

## 五、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 合成残留 ⇒ 报出；空表 ⇒ 通过 |
| SC-2 | 判据**是绿的** | `tests/test_iview_name_routing_done.py` **4/4 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 生成器链 | 7 步全 OK |
| SC-5 | 换路由后**真机复验** | ★ 见未过门 |

## 六、未过门（本轮不做，如实登记）

- **换路由后未做真机复验** —— ★ 改的是**异常路径**（1/2/3）与一处直读（4）；
  ★ 复验需要**打开一张图纸并调这两个函数**（★ 独立一件工作）。★ 但 254/255 已证两个成员**等价**。
- **250 的 7 处真命中**（`FeatureLinearPattern5` 等）仍未换路由。
- **251 的 `SketchTrim` 4 处**仍未换路由。
- 高危写盘（`SaveAs3` 等）· 10 条 `byref-tail` 真机验证 · 门禁 R8 跨天假红 · 223 的 8 条既有红 · 未提交未部署。
