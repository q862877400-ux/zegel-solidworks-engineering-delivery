# Spec — **两种改法对比 + 拍板**：★ 改表（5 类同步）↔ ★ `_checked` 自动补出参（1 处）

**Feature**: `specs/289-arity-change-route-decision/`
**日期**: 2026-10-10
**上游**: `specs/288-study-arity-change-surface/`（★ 量出 **4 类同步点**）
**本轮只做一件事**：★ 288 量出 4 类 ⇒ ★ 本轮**又发现第 5 类** ⇒ ★ 于是**先比方案、再拍板**（★ 授权 **E**）。

---

## 一、★★★ **第 5 类同步点**（★ 本轮量出）

★ `scripts/sw_api_cosworks.py:149` 的 **`ARITY`** —— ★ **逐接口逐成员的反射镜像**：

```python
'ICWStudyManager': {
    'CreateNewStudy': 3, 'CreateNewStudy2': 2, 'CreateNewStudy3': 3,
    'DuplicateStudy': 4, 'DuplicateStudy2': 6, 'ConvertStudy': 6, 'ConvertStudy2': 8,
    'RunAllStudies': 0, 'RunSpecifiedStudyByName': 0, …
}
```

★★★ **⇒ 它与 `STUDY_MANAGER_ARITY` 同一口径** ⇒ ★★ **改表要同步它** —— ★ **288 只量出 4 类** ✓

---

## 二、★★★ 5 类同步点（★ 甲方案要动的**全部**地方）

| # | ★ 同步点 | ★ 内容 |
|---|---|---|
| ① | 表值 | ★ `STUDY_MANAGER_ARITY`（★ 9 处） |
| ② | 调用点 | ★ 5 个被调用的封装要传 `out_i4()` |
| ③ | 标注 | ★ `#: arity-reflect:` 的 `excluded` → `included` |
| ④ | 测试对照表 | ★ `REFLECTED_MANAGER_ARITY`（★ 9 处） |
| ★ ⑤ | ★ **反射镜像表** | ★ `sw_api_cosworks.py` 的 `ARITY['ICWStudyManager']`（★ 9 处） |

---

## 三、★★★ **两条路的对比**

| 项 | ★ **甲 · 改表 + 改调用点** | ★★ **乙 · `_checked` 按表补出参** |
|---|---|---|
| ★ **改动面** | ★ **5 类 × 3 模块** | ★★ **2 处 × 3 模块**（★ `_checked` + 一张「出参类型」小表） |
| ★ 静态 `arity` 桶 | ★ 清空 | ★ **不清空**（★ 它本来就**只计数、不判罪**） |
| ★ **运行期** | ★ 正确 | ★ **正确**（★ 补上占位 ⇒ 与官方形参数一致） |
| ★ 风险 | ★ 高（★ 5 处要同步，★ **漏一处就红**） | ★ **低**（★ 集中在 `_checked` 一处） |
| ★ 表 / 调用点 / 标注 / 镜像表 | ★ **全要动** | ★★ **全不动** ✓ |

---

## 四、★★★ **拍板**（★ 授权 **E**）

★★★ **选乙** —— ★ 理由两条：
1. ★★ **`arity` 桶**只计数、不判罪****（★ 266 判「**改口径不值**」）⇒ ★ **清空它没有硬价值**；
2. ★★★ **真正的目标**是「**运行期能调通**」（★ 补上 by-ref 占位）⇒ ★ **乙用最小改动达成** ✓

★★ 乙方案的实现要点：★ `_checked` 按「**成员 → 出参类型**」的小表**补占位**
⇒ ★ 出参**只有 3 种**（★ 273 量出）：★ `Int32&` ⇒ `out_i4()` · ★ `Double&` ⇒ `VT_BYREF | VT_R8` · ★ `SwDmTableError&`（枚举）⇒ `out_i4()`。

---

## 五、需求

### FR-001 ★★★ **第 5 类同步点**已量出
- **验收场景**：`test_the_fifth_sync_point_is_found` 通过。

### FR-002 ★★★ 两条路**已对比**
- **验收场景**：`test_two_routes_are_compared` 通过。

### FR-003 ★★★ **拍板是乙**（★ 理由写死）
- **验收场景**：`test_the_verdict_is_b_with_the_reason` 通过。

### FR-004 ★★ 乙要用的 **3 种出参**已备齐
- **验收场景**：`test_the_three_out_kinds_are_ready` 通过。

### FR-005 ★★ 三个模块**都有 `_checked`**
- **验收场景**：`test_three_modules_are_in_scope` 通过。

### FR-006 ★★ 判据必须能红
- **验收场景**：`test_pure_function_is_red_able` 通过（★ 五组负例）。

---

## 六、非目标

- ★★★ **本轮不改任何实现** —— ★ 只**比方案 + 拍板**（★ 动手**另开切片**）。
- ★ **不改** `scripts/` ⇒ ★ **不跑生成器链**。

## 七、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 同步点少一类 / 第 5 类没登记 / 拍板不是乙 / 出参不是 3 种 / 模块不是 3 个 ⇒ 全红 |
| SC-2 | 判据**是绿的** | `tests/test_arity_change_route_decision.py` **6/6 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |

## 八、未过门（本轮不做，如实登记）

- ★★★ **乙方案的实现未做** —— ★ 改动面：★ **3 个 `_checked`**（★ 各 1 处）+ ★ **3 张「出参类型」小表** ⇒ ★ **下一轮动手**。
- ★★ **同族的另两张表**（`RESULTS_ARITY` / `MESH_ARITY` / `sw_pdm.py`）**未逐条量** ⇒ ★ 下一轮**同样先量**。
- ★ ② 段第 2 条（250 的 7 处换路由）· `create_draft` 的 `pre_call` · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 未提交未部署。
