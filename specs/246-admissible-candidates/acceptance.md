# 246 · 验收记录

日期：2026-10-09。结论：**离线判据全绿（8/8）**，且**红基线成立（8 组变异全红）**。
runtime / product = **not_run**（本特性**不涉** COM，纯静态）。

---

## 一、实际命令与读数

受管解释器：`C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`（★ 路径写 3.13.12，二进制实报 **3.13.14**）。
★ **pytest 风格判据与 `release_check` 用 3.14.7**：`C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`。

### 1. 先量（Phase 1）

| 命令 | 读数 |
|---|---|
| `output/_probe246_candidates.py` | 分桶 `successor-same-name 34 · terminal-never-called 23 · **admissible 15** · ambiguous-terminal 9 · chain-broken-all 1`；六关失败 `{multiple-official-successors: 4, successor-page-missing: 1}` |
| `output/_probe246_signatures.py` | 8 组**两边签名**逐条导出（被废弃页 vs 后继页） |

### 2. 处置读数（15 条）

| code | 条数 | 成员名 |
|---|---|---|
| `collected` | **5** | `ActivateDoc2` · `AutoDimension2` · `FeatureCircularPattern4` · `GetExplodedViewCount` · `ResumeSelectionList` |
| `already-in-table` | 2 | `AddMate5` · `SaveAs` |
| `reject-multi-successor` | 4 | `FeatureLinearPattern5`(3 链接) · `FeatureLocalCurveDrivenPattern`(2) · `InsertFormToolFeature`(2) · `SketchTrim`(2) |
| `reject-successor-page-missing` | 1 | `GetActiveSketch2`（终点页 `SketchManager::ActiveSketch` **不存在**） |
| `reject-host-interface-mismatch` | **3** | `Add2`（宿主 IEquationMgr）· `GetModelDoc`（宿主 IView）· `GetUserPreferenceIntegerValue`（宿主 ISldWorks） |

### 3. ★★ 红基线（T004/T005）

`output/_probe246_redbaseline.py` —— 8 组变异：**21 处 `✓` · 0 处 `✗`**。

```
A. 基线（未变异）—— 8 条判据全 GREEN
B. 变异 1：Add2 判成 collected          ⇒ ⑤ RED ✓  ③ RED ✓
C. 变异 2：Add2 真收进靶子表            ⇒ ⑥ RED ✓
D. 变异 3：FeatureCircularPattern4 用**字面后继** ⇒ ③ RED ✓（关 2 链终点）
E. 变异 4：从靶子表删掉 ActivateDoc2     ⇒ ④ RED ✓
F. 变异 5：清空处置表                    ⇒ ① RED ✓  ⑦ RED ✓
G. 变异 6：删 sw_part.py 的 AutoDimension2 登记 ⇒ ⑧ RED ✓
H. 变异 7：证据行号改 999                ⇒ ⑦ RED ✓
I. 变异 8：code 写成 'unknown'           ⇒ ② RED ✓
J. 恢复后复跑核心判据                    ⇒ ③④⑧ GREEN ✓
```

★★ **变异 1 当场抓出一处「不可读的失败」**（见 §三）。

### 4. 绿读数（T003/T010）

```
49 passed in 12.60s
  tests/test_deprecated_admissible_disposition.py  8   ← 本特性
  tests/test_deprecated_table_admission.py        12
  tests/test_deprecated_entry_interlock.py         6
  tests/test_save_routing_interlock.py             3
  tests/test_obsolete_multi_successor.py           4
  tests/test_obsolete_multi_successor_impact.py    7
  tests/test_tool_specs_batch80.py                 9
★ 新鲜度族另跑：tests/test_{bundled_skill_enum_freshness,sync_bundled_skill,report_freshness_gate,signature_audit_freshness_gate}.py
  ⇒ 20 passed, 2 skipped
```

### 5. ★ 生成器链（T009 —— 改了 `scripts/`）

```
scripts/release_check.py   ⇒ files 471 · pruned []
scripts/gen_level_audit.py      ⇒ 140 条能力 · level {verified 117, stitched 20, not_implemented 3}
tools/gen_metrics.py            ⇒ docs/metrics.md
tools/gen_harvest_digest.py     ⇒ docs/harvest-digest.md（344 行）· 门禁 44 道
tools/build_union_map.py        ⇒ 并集 808 操作 / 本仓缺 310
tools/gen_dead_ends.py          ⇒ 「死路」75 条 / 46 能力
scripts/release_check.py   ⇒ files 471 · pruned []
```

### 6. 门禁全套（T011）@3.14.7

```
"$PY314" -B scripts/release_check.py   ⇒   EXIT=0 · "status": "pass" · "missing": []
★ 门禁计数：len(gates) = 47 · gate_wiring（scripts/check_*.py）= 44 · gate-classification = 48
   ⇒ ★ 三者**都不变**（★ 未新增门禁文件）
★ 实测耗时：首跑 **4 s（红）** · 修完复跑 **2m33s（绿）**
```

### 7. 生成器未改（T013 / FR-009）

`git status --short tools/build_obsolete_index.py` ⇒ **无输出** ✓

---

## 二、核心事实（本轮量出来的）

### 事实 A：★★★ 245 的教训对 `admissible` 同样成立

242/243 的 `admissible` 分桶**也按裸成员名**算 ⇒ ★ 15 个里 **3** 个是**假命中**：

| 候选（条目接口） | 真树宿主表达式 | 宿主接口 | 结论 |
|---|---|---|---|
| `ICustomPropertyManager::Add2` | `mgr` = `_manager(model)` | **IEquationMgr** | ❌ 假命中 |
| `IComponent2::GetModelDoc` | `view` | **IView** | ❌ 假命中 |
| `IModelDoc2::GetUserPreferenceIntegerValue` | `app` = `IModelDoc2.GetSldWorks` | **ISldWorks** | ❌ 假命中 |

★ 其中 `GetUserPreferenceIntegerValue` 更微妙：★ 官方后继 `IModelDocExtension::GetUserPreferenceInteger`
是**2 参的另一个方法**（★ `sw_units.py:134` 的注释**早已逐字写明**这一点）。

### 事实 B：★★★ `FeatureCircularPattern4` 的**字面后继自己也废弃**

官方 `FeatureCircularPattern4.md` 说 `Superseded by [[IFeatureManager::FeatureCircularPattern5]]`，
★ 而 `FeatureCircularPattern5` **本身也 Obsolete** ⇒ ★ **链终点是 `CreateFeature`**
⇒ ★ 242 的「按链终点、不按字面后继」定则**又一次**在真表上生效。

### 事实 C：★ 靶子表 **4 → 9 条**，且**五条都不是 drop-in**

| 新收条目 | 后继 | 两边签名的差异 |
|---|---|---|
| `ISldWorks::ActivateDoc2` | `ActivateDoc3` | `(Name, Silent, out Errors)` → `(Name, UseUserPreferences, Option, out Errors)` |
| `ISketch::AutoDimension2` | `ISketchManager::FullyDefineSketch` | ★ **跨接口**，且语义 auto-dimension → fully-define |
| `IFeatureManager::FeatureCircularPattern4` | `CreateFeature` | ★ **换整族**（要造 `ICircularPatternFeatureData`） |
| `IAssemblyDoc::GetExplodedViewCount` | `GetExplodedViewCount2` | `()` → `(ConfigurationName)` |
| `ISelectionMgr::ResumeSelectionList` | `ResumeSelectionList2` | `()` → `(Append)` |

⇒ ★ **本表只登记"它已废弃、后继是谁"**；★ **换路由必须真机验**（★ 与 `_REGISTERED` 同规）。

---

## 三、★★ 本轮踩的两处坑（都由机器抓出，不是"我小心了"）

### 坑 1：★ **行首 `+` 的字符串拼接 ⇒ `check_diff_markers` 当场红**

新测试里写了：

```python
assert not bad, "…：\n" \
    + "\n".join("  " + b for b in bad)
```

★ 门禁把**行首的 `+`** 当成 **patch 记号**：

```
[FAIL] 1 行混入了 diff 记号（`*` / `+` 前缀）。
       tests\test_deprecated_admissible_disposition.py  282: + "\n".join(...)
```

★ **修法**：用 `%` 格式化**放同一行**（`"...：\n%s" % ("\n".join(...),)`），**别用行首 `+` 续行**。
★ 这与事实 271（来源块别带 patch 记号）**同族**。

### 坑 2：★★ **变异检验抓出「不可读的失败」**（判据③ 抛 `KeyError` 而不是断言）

把 `Add2` 判成 `collected` 时，判据③ 直接 `KeyError`（因为 `_COLLECTED_SUCCESSOR` 里没有 `Add2`）
⇒ ★ **`KeyError` 与"判据红"在测试里同形**，但**它不告诉你该改成什么**。
★ **修法**：① 判据③ 补「`collected` 必须在 `_COLLECTED_SUCCESSOR` 里」的**显式断言**（带修法提示）；
② 判据④ 补**反向一致性**（判成 `collected` 却没写期望后继 ⇒ 红）。

★★ **定则**：★ **判据的失败必须是"可读的"** —— ★ 凡「表 A 的取值去索引表 B」，
先断言**两表的键集合一致**，否则读到的是 `KeyError`，不是「哪一条错了」。

---

## 四、未过门（不得当通过）

1. **被拒的 10 个候选只登记理由、不收** —— ★ 其中 `FeatureLinearPattern5` / `FeatureLocalCurveDrivenPattern` /
   `InsertFormToolFeature` **是真命中**（我们确实在调），★ 但**官方那句点名多个后继** ⇒ 按 243 关 5 **必须人工表态**，本轮不做。
2. **5 条新收条目的调用点一律不换路由** —— ★ 五条**都不是 drop-in**（参数都变了），换它们**必须真机验**。
3. **宿主接口判定靠人工**（★ 无静态类型推断）⇒ ★ 判错的兜底是判据⑤（宿主≠条目）与判据⑥（假命中不许进表）。
4. **改了公开 MCP 工具的输出**：`deprecated_successor()` 现在能回答这 5 个名 ⇒ ★ 只**增**不改，且新条目**全部过六关**。
5. 真机未验（离线切片）；223 的 8 条既有红未修；未提交未部署、未派成员。
