# Spec — **`create_draft` 首次真机验证**：★★ **建出来了**（★ 需 方向项 mark1 + 待拔模面 mark2）

**Feature**: `specs/283-create-draft-machine-verified/`
**日期**: 2026-10-10
**上游**: `specs/239-*`（★ 把路径从 `CreateDefinition(3)` 改到 `IFeatureManager::InsertMultiFaceDraft` —— ★ **离线切片**）
**授权**: ★ 业主**已授权**（`GOAL.md` §三 **C · 高危/写盘**：★「`create_draft` / `create_profile_center_mate` **真机验证**」）
**本轮只做一件事**：★ **首次真机跑** `create_draft`。

---

## 一、★★★ 真机读数 1：★ **只给面** ⇒ **18 臂全失败**（★ 报文恒定）

| 臂 | 选择 | 结果 | ★ 消息栈 |
|---|---|---|---|
| 6 面 × 3 标记（`mark2` / `mark2+1` / 不设） | 面 | ✗ **全失败** | ★ **「此拔模方向尚未定义。」** |

⇒ ★★★ **排除「选错了面 / 选错了标记」** —— ★ 因为**六种面 × 三种标记**都报**同一条**。

---

## 二、★★★ 真机读数 2（决定性）：★ 加**方向项** ⇒ **成功**

```
★ Front Plane + 面#0 ⇒ 选中 2 · **成功** ✓（'拔模1'）
```

★★★ **`create_draft` 真机建出来了**：★ 新特征 **`拔模1`**，★ 选中 **2** 个（平面 + 面）。
⇒ ★★★ **规格 239 的路径改动（`InsertMultiFaceDraft`）**是对的****，★ 缺的只是**方向项**这一选择。

★ 而 `create_draft` 的 docstring **本来就写着**：「方向项 **mark 1**、待拔模面 **mark 2**、拔模边 **mark 4**」
⇒ ★★ **文档是对的，是**调用方**没照它选**（★ 与事实 503 同族：★ 选区必须由 `pre_call` 重建）。

---

## 三、★★★ 顺带：★ 这是 282 那条假说的**反例**

★ 282 提过一条假说：★「本机的特征创建 API **似乎吃不到「边 / 面」类选择**」（★ 只有 2 个样本）。
★★ 本轮证明：★ `InsertMultiFaceDraft` **吃得到面选择**（★ 只要**同时**给方向项）
⇒ ★★★ **假说被削弱** —— ★ 「吃不到」**不是普遍现象**，★ 而是**按 API 逐个**看的。

---

## 四、需求

### FR-001 ★★★ 只给面 ⇒ 18 臂全失败
- **验收场景**：`test_face_only_always_fails` 通过。

### FR-002 ★★★ 加方向项 ⇒ 成功
- **验收场景**：`test_adding_a_direction_reference_succeeds` 通过。

### FR-003 ★★★ 这是 282 假说的反例
- **验收场景**：`test_it_is_a_counterexample_to_the_282_hypothesis` 通过。

### FR-004 ★★★ 状态表**升为 `True`**（★ 回源码核）
- **验收场景**：`test_status_entry_is_promoted_to_true` 通过。

### FR-005 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 六组负例）。

---

## 五、非目标

- ★★ **不改** `create_draft` 的实现（★ 239 的路径是**对的**）。
- ★ **不改** `face_ref` 那个未用形参（★ 已由 `tool_specs_batch4.py` 登记为真实缺陷）。
- ★ **不碰** `SaveAs3` / `create_profile_center_mate`（★ 同属 §三 C，★ 但**另开切片**）。

## 六、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 臂数不对 / 报文不对 / 没记特征名 / 需求不是两条 / 路径不对 / 表仍写「未测」 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_create_draft_machine_verified.py` **5/5 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 生成器链已跑 | 7 步全 `exit 0`（★ 改了 `scripts/`） |
| SC-5 | ★ 真机无残留 | 护栏预检「读到文档 0 个」 |

## 七、未过门（本轮不做，如实登记）

- ★★★ **`SaveAs3` 未真机验证**（★ `sw_connect.py:1167` · ★ §三 C **已授权**）⇒ ★ 下一轮。
- ★★★ **`create_profile_center_mate` 未真机验证**（★ §三 C **已授权**）⇒ ★ 下一轮。
- ★★ **`create_draft` 的 `pre_call` 未接**（★ 要照 `tool_specs_batch74.py::_select_faces_for` 的形状）
  ⇒ ★ 否则 MCP 表面**仍然**建不出来（★ 事实 503：★ `RESOLVERS` 会清空选区）。
- ★ 12 条 `arity` 接线 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。
