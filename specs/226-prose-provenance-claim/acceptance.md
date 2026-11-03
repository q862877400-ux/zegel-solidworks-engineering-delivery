# Acceptance — 散文式出处自称的收口（spec 226）

**Feature**: `specs/226-prose-provenance-claim/`
**日期**: 2026-10-09
**结论**: ✅ **离线切片完成**。四件齐 · 判据 **9/9 绿**（改动前 **5 例红**）· 门禁 **exit 0** ·
`release_check`（3.14.7）**exit 0**。★ 未提交、未部署、未打 tag、未调 COM/真机、未删任何文件。

---

## 一、判据读数（★ 先红后绿）

```
判据：tests/test_gate_prose_provenance_claim.py
改动前：Ran 9 tests · FAILED (failures=5)      ← ★ 判据真的能红
改动后：Ran 9 tests · OK
```

| 例 | 改动前 | 改动后 |
|---|---|---|
| `test_claim_matches_prose_provenance_words`（FR-001） | **红** | 绿 |
| `test_claim_does_not_match_ambiguous_prose`（FR-001 边界冻结） | 绿 | 绿 |
| `test_claim_still_matches_legacy_probes`（FR-005） | 绿 | 绿 |
| `test_prose_claim_table_is_now_visible_in_the_blind_inventory`（FR-002） | **红** | 绿 |
| `test_prose_claim_table_declares_the_matching_official_enum`（FR-002） | **红** | 绿 |
| `test_every_blind_table_is_dispositioned`（FR-002，下界 55） | **红**（54 < 55） | 绿 |
| `test_undeclared_prose_claim_makes_the_gate_red`（FR-003 端到端负例） | **红** | 绿 |
| `test_declared_prose_claim_keeps_the_gate_green`（FR-003 正例） | 绿 | 绿 |
| `test_wrong_value_in_a_prose_claim_table_is_caught`（FR-003 反向） | 绿 | 绿 |

★ **红/绿同时存在**（5 红 / 4 绿）⇒ 判据既非恒红也非恒绿，是真判据。

---

## 二、门禁读数

```
覆盖清单 · 扫描 **189** 个文件 · 模块级整数表 **101** 张 · 已覆盖 **33** · 未覆盖 **68**
其中**自称官方却无 `# swXxx` 标注**（★ 门禁盲区）：**0** 张      ← ★ 未表态
[PASS] **175** 条有据可查的值**全部与出厂反射一致**
[PASS] 表级出处声明 **55** 张**全部可核**，盲区**未表态 = 0**
exit 0
```

| 读数 | 226 前 | 226 后 | 判 |
|---|---|---|---|
| 扫描文件 | 189 | **189** | 不变 ✓ |
| 模块级整数表 | 101 | **101** | 不变 ✓ |
| 已覆盖 | 33 | **33** | 不变 ✓ |
| 未覆盖 | 68 | **68** | 不变 ✓ |
| 盲区（自称有出处） | 54 | **55** | +1（本轮目标）✓ |
| **未表态** | 0 | **0** | 不变 ✓ |
| `ok` | 175 | **175** | 不变 ✓ |
| 查不到 | 2 | **2** | 不变 ✓ |
| 两源冲突 | 3 | **3** | 不变 ✓ |

⇒ ★ **只动了「盲区张数」这一个目标读数**，其余全不变 ⇒ **不制造任何新红**。

---

## 三、表态明细（本轮新增的 1 条）

| 文件:行 | 表 | 项 | 声明 | 核法 |
|---|---|---|---|---|
| `sw_import_mesh_reference.py:74` | `SW_LENGTH_UNITS` | 8 | `enum swLengthUnit_e`（声明在第 73 行） | 值集 `{0,1,2,3,4}` ⊆ 官方取值集 |

★ **散文 → 可核**：改动前该表的出处只是注释里一句
`# 本机 SolidWorks 2024 swconst.dll 验证值`（**人看得懂、机器看不见**）；
改动后是 `#: enum-gate: enum swLengthUnit_e` ⇒ 门禁**每次都会**拿出厂反射转储去核它的值集。

---

## 四、三源核对（铁律 0 / 铁律 4）

| 源 | 内容 | 结论 |
|---|---|---|
| ① `C:\swapi\enums\swLengthUnit_e.md` | `swMM=0 · swCM=1 · swMETER=2 · swINCHES=3 · swFEET=4 · swFEETINCHES=5 · swANGSTROM=6 · swNANOMETER=7 · swMICRON=8 · swMIL=9 · swUIN=10`（11 项） | 逐条 |
| ③ `_raw/enum_values_sldworks.txt` 第 959–970 行 | **同上，逐条一致** | 逐条 |

★ ② CHM 解包**不适用**（`swLengthUnit_e` 属 `swconst` 程序集，不在 cosworks CHM 里）——
**不是「没查」，是「该源不覆盖此枚举」**。
★ **两源无冲突** ⇒ 未动用裁决顺序（铁律 4：冲突时以出厂反射为准）。

---

## 五、回归

| 判据 | 读数 |
|---|---|
| `tests/test_enum_table_disposition.py`（224） | **8/8 OK** |
| `tests/test_gate_blind_spot_claim.py`（225） | **11/11 OK** |
| `tests/test_gate_boundary_transparency.py`（223） | **7/7 passed** |
| `tests/test_relation_enum_alignment.py`（222） | **18/18 OK** |
| `tests/test_pattern_enum_alignment.py`（222） | **12/12 passed** |
| `tests/test_rule2_length_suffix_is_enforced.py` | **3/3 passed**（`sync_bundled_skill` 461 文件 · `pruned=[]`） |
| `scripts/release_check.py`（★ **@3.14.7**） | **exit 0** · `"missing": []` |

★ 224 的 `BASELINE_BLIND=44` 与 225 的 `BASELINE_BLIND=54` 都是**下界断言** ⇒ 55 ≥ 54 ≥ 44 不假红。

---

## 六、未过门（★ 明确登记，不冒充通过）

1. **散文的「残余」不是 0 的证明，只是本树上的实测 0** ——
   本轮把定稿词集当作「散文自称」的**可操作定义**，逐张核过 14 张非盲区表 ⇒ **没有第 2 张**。
   但**完全不含这 12 个词的散文**（若有）仍看不见。★ 判据用**下界**（`BASELINE_BLIND=55`）而非等号，
   正是为了不把当前读数当永久真理。
2. **`enum` 声明只做「值集包含」，不验「键 ↔ 官方成员名」的对应** ——
   `SW_LENGTH_UNITS` 的键是本地语义键（`"mm"`/`"meter"`/`"in"`），且**有意允许同义键**（`m`/`meter`/`meters` → 2）
   ⇒ 机器**无法**从表本身推出「哪个键对哪个官方成员」。沿用 224/225 的既有边界。
3. **真机未验** —— 本轮是离线切片，未调 COM、未在 SolidWorks 里跑 `configure_mesh_import_preferences`。
4. **`not-enum` 声明不验值** —— 224/225 登记的老问题（`*_ARITY` 的实参个数没被机器验过），本轮**未动**。
5. **223 登记的 8 条 `HEAD` 即红既有失败** —— 权属落在他人未提交改动内，**未修**（先确认权属）。
6. **`HEM_POSITIONS` 真机复核** —— 需业主另行授权 COM，**未做**。

---

## 七、可复用纪律（本轮新增）

1. ★★ **「先量」要量两样：① 目标张数 ② 加词的爆炸半径** ——
   只量①（=1）会以为「很小，随手改」；量了②（=1）才敢改。
   ★ 225 的教训正是②：放宽后**新暴露 10 张**、要逐张表态。
2. ★★ **放宽正则必须有「边界冻结」判据** ——
   本轮加了 `test_claim_does_not_match_ambiguous_prose`：`参考`/`据`/`按` **必须不命中**。
   否则「加宽」会以「顺手」的方式**无限蔓延**（每轮加几个词，没人挡得住）。
   ⇒ ★ 可复用语式：**加词的同时，写一条断言把「不加什么」也钉住**。
3. ★ **端到端负例的合成夹具必须「只含新词」** ——
   夹具注释里只放 `本机` + `.dll`，**不放** `官方`/`反射`/`CHM`/`sws*`。
   否则旧 `CLAIM` 也命中 ⇒ 测不出新词那一条（判据会「因错误的原因」通过）。
4. ★ **量测探针放 `output/`、不进仓库代码** —— 一次性量测的产物不该成为维护负担；
   它的**结论**（量 = 1）写进 spec §1.2，**代码**（`output/_probe_prose_claim.py`）留在 output。
5. ★ **判据按表名定位、不按行号**（225 已记，本轮再次适用：往表上方插了 4 行）。
