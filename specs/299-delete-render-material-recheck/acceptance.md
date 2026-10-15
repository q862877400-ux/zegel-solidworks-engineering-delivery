# Acceptance — **`DeleteRenderMaterial` 后继可调性真机复核**

**Feature**: `specs/299-delete-render-material-recheck/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立（`2 failed, 3 passed`）· 真机复验一致 · 无残留 · 生成器链 7/7 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★★ 业务结论**: ★★★ **「保留旧入口」这个决定**经本轮独立真机复验仍然成立** ——
★ 旧入口**能调**（`True`）· ★★ 后继**不可调**（`getattr` 回 `bool`）
⇒ ★ **换过去 = 从「废弃但能调」变成「新但调不了」** ⇒ ★★ **保留是有据的** ✓

## 一、逐条验收

| # | 需求 | 判据 | ★ 读数 |
|---|---|---|---|
| FR-001 | ★★ 后继仍不可调 | `test_the_successor_is_still_not_callable_on_this_machine` | ✅ pass |
| FR-002 | ★★ 区分「取不到」与「调了报错」 | `test_take_member_and_call_are_distinguished` | ✅ pass |
| FR-003 | ★ 决定记档带理由 | `test_the_decision_is_recorded_with_its_reason` | ✅ pass |
| FR-004 | ★★ `verdict` 不当事实用 | `test_the_evidence_file_is_not_trusted_by_its_verdict` | ✅ pass |
| FR-005 | ★ 证据能复跑 | `test_probe_is_reusable_and_self_contained` | ✅ pass |
| — | **合计** | — | **5 passed** |

## 二、★★★★★ 本轮真机读数（★ SW rev **34.4.1** · ★ 走 `sw_guard --timeout 600`）

```
=== ① 两个入口的**可调用性**（★ 逐条读数，★ 不合并成 verdict）===
  ★ DeleteRenderMaterial(0, False)                        ok=True  True
  ★ DeleteDisplayStateSpecificRenderMaterial(0, False, 0)  ok=False TypeError: …
  ★★ DeleteRenderMaterial                          getattr ⇒ method
  ★★ DeleteDisplayStateSpecificRenderMaterial      getattr ⇒ bool
```

★ 证据 `output/_probe299_render_material.txt` · 探针 `output/_probe299_render_material.py`。

### 2.1 ★★★ 与既有证据**逐条一致**

| ★ 入口 | ★ 既有证据（`render-material-family-evidence.json`） | ★ 本轮复验 | ★ 一致？ |
|---|---|---|---|
| ★ 旧 `DeleteRenderMaterial` | ★★ `ok=true` · `ret: True` | ★★ **`ok=True` · `True`** | ✅ |
| ★★ 新 `DeleteDisplayStateSpecificRenderMaterial` | ★★★ `ok=false` · `TypeError` | ★★★ **`ok=False` · `TypeError`** | ✅ |

### 2.2 ★★★ ② 把「不可调」的**性质**说清了

★ **两个名字都 `getattr` 取得到**（★ 一个回 `method`、★ 一个回 `bool`）
⇒ ★★ **区别不在「取不到」、★ 而在「取回来的不可调用」** ——
★ 那是 **pywin32 迟到绑定造不出调用包装**（★ **架构性**限制，★ 与事实 47 同族）。

### 2.3 ★ 无残留

| 项 | 读数 |
|---|---|
| `sw_guard --scan` | ★ 弹窗 **0** 个 |
| 打开的文档 | ★ **0** 个（临时零件**关闭且未保存**） |

## 三、★★★★ 为什么保留旧入口是**有据的**

| ★ 面 | ★ 事实 |
|---|---|
| ★ 官方口径 | ★ **不是** `Obsolete`，而是「**Not supported in SOLIDWORKS 2011 and later. Superseded by …**」⇒ ★★ **比 `Obsolete` 更强**（★ "不支持"）⇒ ★ **该换** |
| ★★ 本机现实 | ★★ 后继**不可调**（★ `getattr` 回 `bool` ⇒ pywin32 迟到绑定造不出包装） |
| ★★★ 结论 | ★ **换过去 = 从「废弃但能调」变成「新但调不了」** ⇒ ★★ **保留旧入口** ✓ |

★★★ **可复用定则**（★ 本轮再次印证 · 已写进记档）：
> ★★★ **证据文件里的 `verdict` 是**结论**、★ 而逐条 `ok` 才是**事实** ——
> 两者打架时**以逐条为准**（★ 与事实 519 同族：★ "表里有"≠"它做到了"）。

## 四、★★ 改动面

| # | ★ 文件 | ★ 性质 |
|---|---|---|
| 1 | `tests/test_render_material_successor_299.py` | ★ **新建判据**（5 例） |
| 2 | `output/_probe299_render_material.py` / `.txt` | ★ 真机探针与读数（★ 一次性，★ 留 `output/`） |
| 3 | `specs/299-delete-render-material-recheck/*` | ★ 本规格四件套 |

★★ **未改**：`scripts/sw_render_material.py`（★ 边界冻结 —— **FR-006** 要求本轮**只复核、不改路由**）。

## 五、★★★ 红基线（★ 改前实测）

```
$ mv output/_probe299_render_material.txt /tmp/          # 拿走证据
$ python -m pytest tests/test_render_material_successor_299.py -q
FAILED tests/test_render_material_successor_299.py::test_the_successor_is_still_not_callable_on_this_machine
FAILED tests/test_render_material_successor_299.py::test_take_member_and_call_are_distinguished
2 failed, 3 passed
```

## 六、★ 生成器链

| 步骤 | 结果 |
|---|---|
| `sync_bundled_skill` → `gen_level_audit` → `gen_metrics` → `gen_harvest_digest` → `build_union_map` → `gen_dead_ends` → `sync_bundled_skill` | **7/7 `rc=0`** |

## 七、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate299.log` |

## 八、未过门（如实登记）

| # | ★ 项 | ★ 说明 |
|---|---|---|
| ① | ★ 4 处 `needs-feature-data` 换路由 | ★ 属**另一件**已登记项；★ 其中 `sw_pattern.py` 的 `FeatureLocalCurveDrivenPattern` **已由 298 判「本机不建」**（★ 换路由**也救不了** —— ★ 同一个后端）。 |
| ② | ★ `DeleteRenderMaterial` **仍然不换** | ★ **本轮的结论就是"不该换"** ⇒ ★ 不是未过门，★ 是**已判定** ✓ |
