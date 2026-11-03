# Acceptance — 门禁盲区探测器的漏网（spec 225）

**Feature**: `specs/225-blind-spot-claim-detector/`
**验收日期**: 2026-10-09
**结论**: ✅ **离线切片完成** —— 探测器修好、10 张表逐张表态、判据全绿、门禁 exit 0。
**未验收**: COM/真机（离线切片）· 发行收口 · 提交/部署。

---

## 一、判据读数（★ 先红后绿）

| 项 | 改动前 | 改动后 |
|---|---|---|
| `tests/test_gate_blind_spot_claim.py`（**新增，11 例**） | **FAILED (failures=8)** | **Ran 11 tests · OK** |
| ├ `test_undeclared_sws_claim_makes_the_gate_red`（端到端负例） | **红**（门禁 exit 0） | 绿（exit 1 + 点名） |
| ├ `test_claim_matches_sws_name_family` | 红 | 绿 |
| ├ `test_claim_matches_reflection_provenance_words` | 红 | 绿 |
| ├ `test_sws_tables_are_now_visible_in_the_blind_inventory` | 红 | 绿 |
| ├ `test_reflection_derived_tables_are_now_visible...` | 红 | 绿 |
| ├ `test_every_blind_table_is_dispositioned` | 红（盲区 44 < 54） | 绿（盲区 54，未表态 0） |
| ├ `test_the_three_sws_enums_declare_the_matching_official_enum` | 红 | 绿 |
| └ `test_reflection_derived_tables_declare_the_expected_subclass` | 红 | 绿 |
| ├ `test_claim_still_matches_legacy_official_probes` | 绿（★ 放宽不许丢旧探针） | 绿 |
| ├ `test_declared_sws_claim_keeps_the_gate_green` | 绿 | 绿 |
| └ `test_wrong_value_in_a_sws_enum_table_is_caught` | 绿 | 绿 |

★ **8 例红 → 11 例绿**：判据真的能红（不是空判据）。

## 二、门禁读数

```
$ <3.13.12> -B scripts/check_enum_values_vs_reflection.py
  覆盖清单 · 扫描 189 个文件 · 模块级整数表 101 张 · 已覆盖 33 · 未覆盖 68
  其中**自称官方却无 `# swXxx` 标注**（★ 门禁盲区）：**0** 张      ← = 未表态数
  表级出处声明（`#: enum-gate: …`）· 已表态 **54** 张
[PASS] **175** 条有据可查的值**全部与出厂反射一致**（另有 2 条查不到、3 处两源冲突，均已列出）
[PASS] 表级出处声明 **54** 张**全部可核**，盲区**未表态 = 0**
exit 0
```

| 读数 | 改动前 | 改动后 | 说明 |
|---|---|---|---|
| 盲区张数 | 44 | **54** | +3（`sws*`）+7（反射/转储/CHM/_raw） |
| **未表态** | 0 | **0** | ★ 新暴露的 10 张**全部当场表态** ⇒ 仍为 0 |
| 表态分类 | enum 23 · member 11 · not-enum 10 | **enum 26 · member 11 · not-enum 17** | +3 enum / +7 not-enum |
| `[PASS] 175` 条值 | 175 | **175** | ★ **不变** |
| 查不到 / 两源冲突 | 2 / 3 | **2 / 3** | ★ **不变** |
| 覆盖清单（文件/表/已覆盖/未覆盖） | 189/101/33/68 | **189/101/33/68** | ★ **不变** |

★ **本切片不制造任何新红**：`ok` / 查不到 / 两源冲突 / 覆盖清单**四读数全不变**，
变的只有「盲区张数」（这正是修复目标）。

## 三、表态明细（本轮新增的 10 条）

| 文件 | 表（改动后起始行） | 声明 | 声明行 |
|---|---|---|---|
| `scripts/sw_simulation.py` | `SWS_SOLVER_TYPES`（1566） | `enum swsSolverType_e` | 1565 |
| `scripts/sw_topology.py` | `SWS_TOPOLOGY_DEMOLD_DIRECTIONS`（186） | `enum swsTopologyDemoldDirectionOption_e` | 185 |
| `scripts/sw_topology.py` | `SWS_TOPOLOGY_ACTIVATION`（195） | `enum swsTopologyActivationOption_e` | 194 |
| `scripts/sw_costing.py` | `COSTING_ARITY`（76） | `not-enum arity` | 75 |
| `scripts/sw_featureworks.py` | `FEATUREWORKS_ARITY`（76） | `not-enum arity` | 75 |
| `scripts/sw_pdm.py` | `DOCUMENT_ARITY`（95） | `not-enum arity` | 94 |
| `scripts/sw_pdm.py` | `TABLE_ARITY`（110） | `not-enum arity` | 109 |
| `scripts/sw_routing.py` | `ROUTING_ARITY`（85） | `not-enum arity` | 84 |
| `scripts/sw_selection.py` | `SELECTION_ARITY`（100） | `not-enum arity` | 99 |
| `scripts/sw_simulation_loads.py` | `_REFGEOM_POSITIONS`（305） | `not-enum index` | 304 |

★ 全部**纯插入**（含 `sw_pdm.py` 给 `TABLE_ARITY` 补的一行出处注释），**零删除**。

## 四、三源核对（铁律 0 / 铁律 4）

| 表 | 声明的枚举 | 转储（③）节头 | 转储值集 | 表内值集 | ⊆ ? |
|---|---|---|---|---|---|
| `SWS_SOLVER_TYPES` | `swsSolverType_e` | `_raw/reflect/enum_cosworks.txt` | `{0,1,2,5,6,7,8}` | `{0,1,2,5,6,7,8}` | ✓ |
| `SWS_TOPOLOGY_DEMOLD_DIRECTIONS` | `swsTopologyDemoldDirectionOption_e` | 同上 | `{0,1,2}` | `{0,1,2}` | ✓ |
| `SWS_TOPOLOGY_ACTIVATION` | `swsTopologyActivationOption_e` | 同上 | `{0,1}` | `{0,1}` | ✓ |

- **①swapi**：`C:\swapi\enums\` **没有**这三个页（142 个 `sws*` 页全是 `swS*`/`swSF*`/`swSM*`/`swSTL*` 等，
  非 Simulation/Cosworks 程序集）⇒ 本轮 Simulation 枚举**只能靠 ②③**。
- **②CHM 解包**：`_raw/chm_cosworks/` · `_raw/cosworks_pages/` 存在，作交叉核对。
- **③出厂反射转储**：★ **本轮判据的值来源**（`enum_value_sets()` 读的就是它）。
- **冲突裁决顺序**：③ > ② > ①（**铁律 4**：冲突以**出厂类型库**为准）。
- ★★ **本轮三源不冲突** ⇒ 裁决顺序**未被动用**。这点必须写清楚：
  是「**查了、不冲突**」，**不是**「没查」。

## 五、回归

| 判据 | 读数 |
|---|---|
| 224 `tests/test_enum_table_disposition.py` | **8/8 OK** |
| 223 `tests/test_gate_boundary_transparency.py` | **7/7 passed** |
| 222 `tests/test_relation_enum_alignment.py` | **18/18 OK** |
| 222 `tests/test_pattern_enum_alignment.py` | **12/12 passed** |
| 打包新鲜度 `tests/test_rule2_length_suffix_is_enforced.py` | **3/3 passed** |
| `scripts/release_check.py` | `{"status":"pass","files":461,"pruned":[]}` |
| **门禁全套** `scripts/release_check.py`（@**3.14.7**） | **exit 0**（`missing: []`） |

★ 两处**本来可能假红**、实测**没红**的地方（先读判据确认，再实测）：
1. 223 的 `test_enum_gate_reports_coverage_inventory` 断言
   `len(未覆盖：明细行) == min(未表态数, 20)` —— 它算的是**未表态数**（改后仍 **0**），
   ★ 不是「盲区张数」（44→54）⇒ 明细仍 0 行 ✓ 不假红。
2. 224 的 `BASELINE_BLIND = 44` —— 断言是 `assertGreaterEqual(blind, 44)`（**下界**）⇒ 54 ≥ 44 ✓ 不假红。

## 六、未过门（★ 明确登记，不冒充通过）

1. **散文式出处自称仍看不见**：`CLAIM` 是**启发式** —— 窗口里出现「官方/swapi/`sws?[A-Z]`/反射/转储/CHM/`_raw`」
   才算「自称」。用**不含这些词**的散文声称出处的表**仍落在盲区外**。
   ★ 这是**已知缺口**，不是「已解决」。要根治需把「出处」变成**结构化字段**（表级 YAML/装饰器），
   属更大的改动，本轮**不做**。
2. **窗口是 15 行**：★ 本轮**当场踩到** —— 给 `TABLE_ARITY` 上方插声明行后，它原本的「自称」来自
   **上一张表的注释**、被挤出 15 行窗口 ⇒ 它**掉出盲区**（盲区 54→53）。
   处置：给 `TABLE_ARITY` 补了**它自己**的出处注释（★ 该说法经核为真：`sw_pdm.py:228-233` 的
   签名块写明「对 `SolidWorks.Interop.swdocumentmgr.dll` 的**纯元数据反射**」）⇒ 盲区回到 54。
   ⇒ ★ **可复用教训**：**窗口启发式会让「插入注释」改变分类结果**；给表补注释时要**自带出处行**，
   别依赖邻表的注释。
3. **`enum` 声明只做值集包含**，**不校验键与官方成员名的对应**（`SWS_SOLVER_TYPES` 的键是本地语义键
   `"intel_cluster"`，官方成员名不在键里）—— 与 224 同一条限制。
4. **`not-enum` 声明不校验值**：只校验子类在封闭词表内。⇒ `*_ARITY` 的 25/5/10/7/31/40 个**实参个数**
   **一个都没被机器验过**（它们只在运行期 `_checked()` 里被使用）。
5. **真机未验**：本切片 100% 离线，**无任何 COM/真机读数**。
6. **223 的 8 条 `HEAD` 即红既有失败未修**（权属不明）。
7. **`HEM_POSITIONS` 真机复核未做**（需业主另行授权 COM）。

## 七、可复用纪律（本轮新增）

1. ★★ **探测器自己也要有判据** —— 「修宽正则」这件事，若只跑门禁本体，**改前改后都 exit 0**
   ⇒ 必须有**合成树上的端到端负例**才能红（本轮 `test_undeclared_sws_claim_makes_the_gate_red`）。
   与 223 判过的「空判据」同族。
2. ★ **判据按表名定位，不按行号** —— 本轮要往表上方插行，行号必然移位；
   行号写死 = 一插就假红（与「把偶然当判据」同族）。
3. ★ **15 行窗口启发式对「插入注释」敏感** —— 补注释要**自带出处行**（见 §六.2）。
4. ★ 沿用：`release_check` 必须 **3.14.7**；`--basetemp` 不许指向仓库内；判据用 3.13.12（桩掉 COM）。
