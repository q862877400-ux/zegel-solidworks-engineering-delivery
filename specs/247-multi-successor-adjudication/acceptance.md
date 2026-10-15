# 247 · 验收记录

日期：2026-10-09。结论：**离线判据全绿（11/11）**，且**红基线成立（7 组变异：24 处 `✓` · 0 处 `✗`）**。
runtime / product = **not_run**（本特性**不涉** COM，纯静态）。

---

## 一、实际命令与读数

受管解释器：`C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`（★ 路径写 3.13.12，二进制实报 **3.13.14**）。
★ **pytest 风格判据与 `release_check` 用 3.14.7**：`C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`。

### 1. 先量：254 条多链接条目的**措辞分布**

| 措辞 | 条数 | 真后继 |
|---|---|---|
| `Superseded by A and B` | **235** | ★ **A 与 B 都是** |
| `See X and the Remarks in/of Y` | **14** | ★ **只有 X**（Y 是数据接口） |
| 其它 `See …` | **5** | ★ **判不出**（★ 顺序不可靠） |

### 2. 先量：**真树在调的多链接条目 = 18**

`SUPERSEDED-BY 16` · `SEE+REMARKS 2` · `SEE(other) 0`
⇒ ★ **只有 2 条机械可判为「真后继 = 1」** ⇒ 本轮**收这 2 条**；★ 16 条「两个都是后继」**表表达不了** ⇒ 拒。

### 3. ★★ 红基线（T007）

`output/_probe247_redbaseline.py` —— 7 组变异：**24 处 `✓` · 0 处 `✗`**。

```
A. 基线（未变异）—— 11 条判据全 GREEN
B. 变异 1：`_official_successor_links` 退回 243 的旧语义（返回**全部**链接）
   ⇒ ② see_remarks_counts_only_prefix RED ✓ · ⑦ collected_pass_admission RED ✓
C. 变异 2：把 `Superseded by A and B` 塞进**表态表**
   ⇒ ⑨ adjudication_never_whitelists_pair RED ✓
D. 变异 3：从靶子表删掉 FeatureLinearPattern5          ⇒ ⑧ RED ✓
E. 变异 4：把 FeatureLinearPattern5 的后继改成**同名**   ⇒ ⑦ RED ✓（关 4）
F. 变异 5：删 sw_pattern.py 的登记                       ⇒ ⑪ RED ✓
G. 变异 6：表态表塞一条依据不合格的条目                  ⇒ ⑩ RED ✓
H. 变异 7：把 `_COLLECTED` 的目标改成表里没有的后继      ⇒ ⑦ RED ✓ · ⑧ RED ✓
I. 恢复后复跑核心判据                                    ⇒ ⑤⑦⑧ GREEN ✓
```

### 4. 绿读数（T006/T012）

```
65 passed in 18.41s
  tests/test_deprecated_multi_successor_adjudication.py  11   ← 本特性
  tests/test_deprecated_table_admission.py               12
  tests/test_deprecated_entry_interlock.py                6
  tests/test_save_routing_interlock.py                    3
  tests/test_deprecated_admissible_disposition.py         8
  tests/test_obsolete_multi_successor.py                  4
  tests/test_obsolete_multi_successor_impact.py           7
  tests/test_tool_specs_batch80.py                        9
  tests/test_bundled_skill_enum_freshness.py + test_sync_bundled_skill.py  5
```

### 5. ★ 生成器链（T011 —— 改了 `scripts/`）

7 步全 `ok`（`sync_bundled_skill` → `gen_level_audit` → `gen_metrics` → `gen_harvest_digest` →
`build_union_map` → `gen_dead_ends` → `sync_bundled_skill`）。

### 6. 门禁全套（T013）@3.14.7

```
"$PY314" -B scripts/release_check.py   ⇒   EXIT=0 · "status": "pass" · "missing": []
★ 门禁计数：len(gates) = 47 · gate_wiring = 44 · gate-classification = 48 —— ★ 三者都不变
★ 实测耗时 2m51s
```

### 7. 生成器未改（T015 / FR-008）

`git status --short tools/build_obsolete_index.py` ⇒ **无输出** ✓

---

## 二、核心事实（本轮量出来的）

### 事实 A：★★★ 243 的关 5 **把数据接口也算成了后继**

官方常写「`See [[X]] and the Remarks in [[Y]]`」⇒ ★ **`Y` 不是后继**。
★ 实证：`ILinearPatternFeatureData` / `ILocalCurvePatternFeatureData` 在 `C:/swapi/types/` 里**页根本不存在**
（它们只出现在 `Remarks` 引用里）。
⇒ ★ 243 只数「全部 `[[…]]` 链接」⇒ 这两条**会被假拒**。

### 事实 B：★★★ 三态是可机械判定的（且第三态必须回 `None`）

| 形态 | 例（逐字取自 `C:/swapi/types/`） | 判据 |
|---|---|---|
| `Superseded by A and B` | `Obsolete. Superseded by [[ISketchManager::SketchExtend]] and [[ISketchManager::SketchTrim]].` | **2** |
| `See X and the Remarks in/of Y` | `Obsolete. See [[IFeatureManager::CreateFeature]] and the Remarks in [[ILinearPatternFeatureData]] …` | **1** |
| 其它 `See …` | `Obsolete. See [[IProjectionCurveFeatureData]] and [[IFeatureManager::CreateDefinition]].` | ★ **`None`** |

★ **第三态为什么必须 `None`**：★ 上例里**数据接口在前、真后继在后** ⇒ ★ 按位置取**必错**。
⇒ ★ **判不出就不许猜**（★ 与 237 的 `[reader-too-narrow]` 同族）。

### 事实 C：★ 靶子表 **9 → 11 条**

| 新收条目 | 后继 | 两边签名 |
|---|---|---|
| `IFeatureManager::FeatureLinearPattern5` | `CreateFeature` | `FeatureLinearPattern5(22 参)` → `CreateFeature(System.object FeatureData)` |
| `IFeatureManager::FeatureLocalCurveDrivenPattern` | `CreateFeature` | `FeatureLocalCurveDrivenPattern(13 参)` → 同上 |

★ 两条**都不是 drop-in**（都要**先造 `I*PatternFeatureData`**）⇒ ★ **只登记，不换路由**。

---

## 三、本轮踩的坑（★ 都由机器抓出）

1. ★★ **`_chain_terminal` 对「起点不在索引里」回 `None`** —— 我第一版的「官方那个链接必须在链上」检查
   写成 `o_term is None ⇒ 红`，⇒ ★ **把「链接自己就不废弃」这种**正常情形**误判成红**
   （`CreateFeature` 不在索引里 ⇒ `_chain_terminal` 回 `None`）。
   ★ **修法**：先判 `(o_iface, o_member) not in imap ⇒ 它就是终点`，**再**走链。
   ★★ **定则：`None` 有两种含义（"断链"与"起点不在索引里"）** —— ★ 与 243 的关 6 教训**同族**。
2. ★ **合成夹具的 `successor` 必须写**全限定名** —— 索引里存的是 `Iface::Member`；
   写裸名会让 `_split` 切出 `("裸名", "")` ⇒ ★ 关 2 报 `!=`（空）⇒ **夹具自己错了**。
3. ★ **变异检验里我的期望写错了一条**（把「表态表加 `SketchTrim`」误当成会影响「2 条新收过六关」）——
   ★ 那是**两条不同判据的靶子**。★ 已订正为 `GREEN`，并在探针里写明理由。

---

## 四、未过门（不得当通过）

1. **16 条 `Superseded by A and B`** 只登记理由、**不收**（★ 表的值是裸成员名，表达不了「两个都要」）。
2. **5 条 `See(other)`** 机械判不出 ⇒ ★ 但**真树在调的是 0 条** ⇒ **没有靶子**
   ⇒ ★ 表态表**现在为空**（★ 空满足；★ 机制由**合成表态表**用例保证可跑）。
3. **新收 2 条的调用点一律不换路由**（★ 都要先造 `I*PatternFeatureData`，换它是重写，须真机验）。
4. 真机未验（离线切片）；223 的 8 条既有红未修；未提交未部署、未派成员。
