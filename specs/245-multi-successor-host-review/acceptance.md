# 245 · 验收记录

日期：2026-10-09。结论：**离线判据全绿（7/7）**，且**红基线成立（5 组变异全红）**。
runtime / product = **not_run**（本特性**不涉** COM，纯静态）。

---

## 一、实际命令与读数

受管解释器：`C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`（★ 路径写 3.13.12，二进制实报 **3.13.14**）。
★ **pytest 风格判据与 `release_check` 用 3.14.7**：`C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`。

### 1. 先量（Phase 1）

| 命令 | 读数 |
|---|---|
| `output/_probe245_hosts.py` | **命中名 14 · 调用点 65** · 逐条导出「宿主表达式源码」 |
| `output/_probe245_pages.py` | **11** 个名在 `C:/swapi/types/*/` 下有**非废弃的同名页**（3 个没有：`FeatureLinearPattern5` / `FeatureLocalCurveDrivenPattern` / `InsertFormToolFeature`） |
| 人工逐条判宿主接口（T003） | **real-hit 6 · mixed 1 · false-hit 7** |

### 2. ★★ 红基线（T005/T006，本特性的核心证据）

`output/_probe245_redbaseline.py` —— 对登记表做 5 组变异，逐条看判据**是否当场红**：

```
A. 基线（未变异）—— 全部应 GREEN
  ① every_hit_name_is_reviewed        ✓  ② live_same_name_pages…  ✓  ③ codes_are_closed…  ✓
  ④ evidence_sites_match_recomputed   ✓  ⑤ real_and_false_hit…    ✓  ⑥ no_real_hit_in_known_wrong ✓
  ⑦ scan_parity_with_interlock        ✓

B. 变异 1：把 SketchTrim 改成 real-hit（★ 244 当初就是这么判的）
  ⑥ no_real_hit_in_known_wrong        期望 RED  实得 RED  ✓

C. 变异 2：清空登记表
  ① 期望 RED 实得 RED ✓   ② 期望 RED 实得 RED ✓   ④ 期望 RED 实得 RED ✓

D. 变异 3：把 KFactor 的证据行号改成 999（调用点漂移）   ④ RED ✓
E. 变异 4：把 Name 的 code 写成 'unknown'（★ 不许糊过去） ③ RED ✓
F. 变异 5：把全部 false-hit 改成 real-hit（下界被击穿）  ⑤ RED ✓  ⑥ RED ✓
G. 恢复后复跑核心判据                                  ⑥ GREEN ✓
```

★★ **变异 2 当场抓出一处空判据**（见 §三）：判据 ④ 补「检查量下界」后才转红。

### 3. 绿读数（T004）

```
29 passed in 10.71s
  tests/test_obsolete_multi_successor_impact.py  7   ← 本特性
  tests/test_obsolete_multi_successor.py         4   ← 244 回归
  tests/test_deprecated_table_admission.py      12   ← 243 回归
  tests/test_deprecated_entry_interlock.py       6   ← 互锁族
```

### 4. 门禁全套（T009）@3.14.7

```
"$PY314" -B scripts/release_check.py   ⇒   EXIT=0 · "status": "pass" · "missing": []
★ 实测耗时：首跑 2m40s · 改完 `docs/` 后复跑 3m11s（★ 比历史记录里的 ~31 s 长 —— 它现在扫 1043 / 1384 / 199 个文件）
★ 门禁计数：len(gates) = 47 · gate_wiring（scripts/check_*.py）= 44 · gate-classification = 48
   ⇒ ★ 三者**本轮都不变**（★ 未新增门禁文件；★ 只改了 tests/ 与 docs/）
```

### 5. 受保护文件未改（T008 / FR-007）

```
git status --short tools/build_obsolete_index.py   ⇒ 无输出 ✓（mtime 2026-10-03）
★ scripts/sw_com_traps.py 的 ` M` 是**本轮之前**的改动（mtime 16:33，★ 早于本会话 19:04）
  ⇒ ★ 本轮**没有碰它**（`DEPRECATED_ENTRIES` 仍 **4 条**）。
```

★ **未跑生成器链** —— 改动面只有 `tests/*.py` 与 `docs/*.md`（生成物只依赖 `scripts/` 与 `mcp-server/`）。

---

## 二、核心事实（本轮量出来的）

### 事实 A：★★★ 244 的「14」是**裸成员名**口径 ⇒ 一半是**假命中**

| 命中名 | 废弃条目接口 | 真树调用的宿主 | 判定 |
|---|---|---|---|
| `DeleteRenderMaterial` | IModelDocExtension | `extension`（IModelDocExtension） | **real-hit** |
| `FeatureLinearPattern5` | IFeatureManager | `FeatureManager` | **real-hit** |
| `FeatureLocalCurveDrivenPattern` | IFeatureManager | `fm` = `FeatureManager` | **real-hit** |
| `InsertFormToolFeature` | IFeatureManager | `_mgr` = `FeatureManager` | **real-hit** |
| `KFactor` | IBendsFeatureData | `definition` = `GetDefinition`（BaseFlange） | **real-hit** |
| `MaterialIdName` | IModelDoc2 | `model` | **real-hit** |
| `Name` | IView / IComponent2 | `view`（3 处，真）+ `feature`/`feat`/`x`/`active`（48 处，假） | **mixed** |
| `GetArcs2` / `GetLines2` / `GetPolylines` / `GetSplines` / `GetEllipses3` | `IView::*` | ★ `sketch` = **ISketch** | **false-hit** ×5 |
| `GetMassProperties` | `IModelDoc2::*` | ★ `extension` = **IModelDocExtension**（= **后继本身**） | **false-hit** |
| **`SketchTrim`** | `IModelDoc2::SketchTrim` | ★ `get_com_member(model, "SketchManager")` = **ISketchManager** | **false-hit** |

⇒ **real-hit 6 · mixed 1 · false-hit 7**。

### 事实 B：★★★ 244 的「1 个真靶子（`SketchTrim`）」**是错的**

`scripts/sw_sketch_edit_ops.py:148` 逐字：

```
get_com_member(_sketch(model) and get_com_member(model, "SketchManager"), "SketchTrim", …)
```

★ 宿主是 **ISketchManager** ⇒ 调的是 **`ISketchManager::SketchTrim`**（★ **非废弃**，正是索引该给的那一个）
⇒ ★★ 索引把 `IModelDoc2::SketchTrim` 的后继取成 `SketchExtend`（**确实错**），
但**真树上没有任何站点调 `IModelDoc2::SketchTrim`** ⇒ **零影响**。

### 事实 C：★★★ 真命中里**没有一条**落在「索引取错」的后继上 ⇒ 待办 1 **关闭**

244 的 6 条错后继（`GetBody` / `IGetBody` / `SketchTrim` / `IGetTextFormat` / `ISetTextFormat` / `ICreateOLEObject`）
里，真树命中的只有 `SketchTrim`，★ 而它是**假命中** ⇒ **真靶子 = 0**
⇒ ★ 交接单**待办 1（「逐条复核 254 条多后继条目」）关闭**（★ 关闭依据 = 判据 ⑥，且它**能红**）。

### 事实 D：★ 机械信号 —— 11 个名有**非废弃的同名页**

`C:/swapi/types/*/<名>.md` 里存在首行非 `Obsolete.` 的页 ⇒ 该名**必须**人工表态。
★ `Name` 一个名就有 **22** 个非废弃同名页（`IFeature` / `IBody2` / `IBomFeature` / …）。
⇒ ★ 这条信号**独立于**人工判断，是「**有盲区即红**」的形态（FR-002）。

---

## 三、★★★ 变异检验当场抓出的一处空判据（本轮最值钱的一条）

**变异 2（清空登记表）** 下，判据 ④（证据与重算站点比对）**仍然是绿的**：

```
④ evidence_sites_match_recomputed   期望 RED   实得 GREEN   ✗ ★不是能红的判据
```

**根因**：判据体是 `for name, (…) in _HOST_REVIEW.items(): …` —— ★ 表为空 ⇒ **一次循环都不进** ⇒
「逐条比对」退化成「**一条都不比**」⇒ **空判据**（★ 事实 46「检查量为 0 判失败」的又一实例）。

**修法**：加**检查量下界**（表 ≥14 条 · 证据站点 ≥14 个），放在循环之前。
修后同一变异 ⇒ **RED** ✓。

★ **定则**：★ **凡「遍历一张表做比对」的判据，必须先钉住表的规模** ——
否则「表被清空/被读空」与「全部通过」**同形**。

---

## 四、未过门（不得当通过）

1. **7 个真命中 = 我们确实在调废弃成员** —— ★ 但换路由**必须真机验**（与 `_REGISTERED` 同规）
   ⇒ ★ 本轮**只定性、不换路由**。★ 其中索引后继 **7/7 正确**（索引这一侧没问题）。
2. **`Name` 的 51 处站点只逐站点看了 2 处**（1 真 + 1 假）—— ★ 其余按宿主变量名归类，**未逐条读上下文**。
3. **244 的 6 条索引错后继仍未修**（★ 改生成器 = 独立工作）；本轮只证明它们**在真树上零影响**。
4. **宿主接口判定靠人工**（★ 无静态类型推断）⇒ ★ 判错的兜底是判据 ④（证据对不上）与判据 ⑥（落在错后继）。
5. 真机未验（离线切片）；223 的 8 条既有红未修；未提交未部署、未派成员。
