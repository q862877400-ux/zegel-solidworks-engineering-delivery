# Spec — **`DeleteRenderMaterial` 后继可调性真机复核**：证据与记档一致 ⇒ 保留旧入口是有据的

**Feature**: `specs/299-delete-render-material-recheck/`
**日期**: 2026-10-10
**上游**: `specs/260-*`（★ 7 处换路由先量）· `specs/261-*`（★ 第 1 批 `adapt-args`）
**触发**: ★ 收 `AUTO_HANDOFF.md` ④ 段登记项 **③** 逐字：
「`DeleteRenderMaterial` —— ★ 先**真机复核**后继是否可调 · ★ 既有证据说**不可调**（`3/4`）」。

---

## 一、★★★★ 先量：既有证据说「后继不可调」，而本轮要**独立复验**

★ 既有证据（`output/render-material-family-evidence.json`）的**逐条读数**：

| ★ 入口 | ★ `ok` | ★ 读数 |
|---|---|---|
| ★ 旧 `DeleteRenderMaterial` | ★★ **true** | ★ `ret: True` |
| ★★ 新 `DeleteDisplayStateSpecificRenderMaterial` | ★★★ **false** | ★ **`TypeError: …不可调用（`getattr` 回了 `bool`）`** |

★★ **而那份证据里的 `verdict` 逐字是**「★ 新旧都能调 ⇒ **可以换**」**** ⇒ ★★ **与逐条读数打架**
（★ 它把 `3/4` 读成了"都能调"）。

★★★ **⇒ 本轮的判据**（★ 记档里已写明的可复用定则）：
> ★★★ **证据文件里的 `verdict` 是**结论**、★ 而逐条 `ok` 才是**事实** ——
> 两者打架时**以逐条为准**（★ 与事实 519 同族：★ "表里有"≠"它做到了"）。

---

## 二、★★★★★ 本轮真机复验（★ SW rev **34.4.1** · ★ 走 `sw_guard`）

★ 探针 `output/_probe299_render_material.py`（★ **按 §十七 的契约**：★ 开临时零件 ⇒ 试调 ⇒ `finally` 关闭且不保存）。

```
=== ① 两个入口的**可调用性**（★ 逐条读数，★ 不合并成 verdict）===
  ★ DeleteRenderMaterial(0, False)                        ok=True  True
  ★ DeleteDisplayStateSpecificRenderMaterial(0, False, 0)  ok=False TypeError: …
       取回来的成员**不可调用**（`getattr` 回了 `bool`，★ 而它通常是 `(None, None, None)`）
       —— ★ 这**多半是 pywin32 迟到绑定造不出该方法的调用包装**

=== ② **取成员**这一步成不成（★ 区分「取不到」与「调了报错」）===
  ★ DeleteRenderMaterial                          getattr ⇒ method
  ★ DeleteDisplayStateSpecificRenderMaterial      getattr ⇒ bool
```

★★★ **⇒ 本轮复验结论：与既有证据**逐条一致**** ✓
★ 旧入口**能调**（`True`）· ★★ 后继**不可调**（`getattr` 回 `bool`）。

★★ **而且②把「不可调」的**性质**说清了**：★ **两个名字都取得到**（★ 一个 `method`、★ 一个 `bool`）
⇒ ★★ **区别不在"取不到"、★ 而在"取回来的不可调用"** ——
★ 那是 **pywin32 迟到绑定造不出调用包装**（★ **架构性**限制，★ 不是 API 语义）。

---

## 三、★★★★ 官方口径（★ 比 `Obsolete` 更强）

★ `IModelDocExtension/DeleteRenderMaterial.md` **没有** `Obsolete` 行 ——
★★ 而是 `official-members-index.json` 记的 `obsolete_line` 逐字：

> 「**Not supported in SOLIDWORKS 2011 and later. Superseded by …**」

★★★ **⇒ 那比 `Obsolete` **更强**（★ "不支持"）** ⇒ ★ 所以**该换**；
★★ 而**换不过去**（★ 后继在本机不可调）⇒ ★★ **⇒ 保留旧入口是有据的** ✓

---

## 四、需求

### FR-001 ★★★ 后继**仍不可调**必须由**本轮真机证据**撑着
- **验收场景**：`test_the_successor_is_still_not_callable_on_this_machine` 通过。

### FR-002 ★★★ 「取不到成员」与「调了报错」必须**分开**
- **验收场景**：`test_take_member_and_call_are_distinguished` 通过。

### FR-003 ★★ 保留旧入口的决定必须**记档带理由**（★ 不是"漏改"）
- **验收场景**：`test_the_decision_is_recorded_with_its_reason` 通过。

### FR-004 ★★★ `verdict` **不当作事实**用（★ 可复用判据）
- **验收场景**：`test_the_evidence_file_is_not_trusted_by_its_verdict` 通过。

### FR-005 ★★ 证据必须**能复跑**（★ 探针自带清理）
- **验收场景**：`test_probe_is_reusable_and_self_contained` 通过。

### FR-006 ★★ **边界冻结**：★ 本轮**只复核**，★ **不改路由**
- **验收场景**：★ `scripts/sw_render_material.py` 的调用**一字未动**（★ 由 `git diff` 可核）。
