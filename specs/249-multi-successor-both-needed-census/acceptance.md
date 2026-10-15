# Acceptance — 「两个后继都要」的宿主级先量

**Feature**: `specs/249-multi-successor-both-needed-census/`
**日期**: 2026-10-09
**结论**: ✅ **四件齐 · 判据 6/6 绿 · 红基线成立 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: **真树上 0 靶子** ⇒ 247 的「未过门 1」**关闭**（★ 不升级靶子表形态）。

---

## 一、逐条验收（对应 `spec.md` 的 FR）

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | 条目数与写站点数下界 | `test_census_sizes_are_frozen` | ✅ 条目 **15** · 写站点 **7** |
| FR-002 | 每个写站点都表态（双向） | `test_every_write_site_is_adjudicated` | ✅ **7/7**，无缺失、无空口表态 |
| FR-003 | ★★ 无写站点落在「两个后继」的废弃接口上 | `test_no_write_site_targets_a_multi_successor_interface` | ✅ **问题数 0** |
| FR-004 | 判据**能红**（正反两向合成负例） | `test_criterion_is_red_able` | ✅ `IView` 写 `Name` **判出**；`IFeature` 写 `Name` **不判出** |
| FR-005 | 把「裸名归集会给出假靶子」冻成判据 | `test_bare_name_aggregation_would_give_false_targets` | ✅ 假靶子 **4** ≥ 下界 4；宿主级仍为空 |
| FR-006 | 与 248 的宿主表跨规格一致 | `test_hosts_agree_with_spec_248` | ✅ `feature`/`study` 两表同接口 |
| FR-007 | 不许改生成器 / 靶子表 / `sw_*.py` | mtime 核（§三） | ✅ 全部早于开工时刻 |

---

## 二、★ 红基线（★ 本仓纪律：不能红的判据 = 空判据）

| 变异 | 期望 | 实测 |
|---|---|---|
| 把 `sw_sheet_metal.py:257` 的宿主接口由 `ICustomBendAllowance` 改成 `IBendsFeatureData` | 判出 **1 条**靶子 | ✅ **`["sw_sheet_metal.py:257 宿主 'bend_allowance'=IBendsFeatureData 写 KFactor ⇒ 该条目**两个后继都要**"]`** |
| 合成：`IView` 写 `Name` | 判出 | ✅ |
| 合成：`IFeature` 写 `Name` | **不**判出（★ 防判据过宽） | ✅ |

★ 命令（★ 可复制）：
```bash
cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
import sys, importlib.util
sys.path.insert(0,'D:/AI/SW'); sys.path.insert(0,'D:/AI/SW/scripts'); sys.path.insert(0,'D:/AI/SW/tests')
s=importlib.util.spec_from_file_location('t','D:/AI/SW/tests/test_multi_successor_both_needed_census.py')
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
e=m._multi_pair_entries()
print('条目', len(e), '| 写站点', len(m._write_sites({x['member'] for x in e})))
print('正常:', m._both_needed_failures(e, m._WRITE_SITE_REVIEW))
mut=dict(m._WRITE_SITE_REVIEW); mut[('sw_sheet_metal.py',257,'bend_allowance','KFactor')]=('IBendsFeatureData','变异')
print('变异:', m._both_needed_failures(e, mut))
"
```

---

## 三、★ 未改动证明（★ 用 mtime，**不用 `git status`**）

★ 理由同 248：本仓工作树是「已 staged 的整树基线」⇒ `git status` 的 `M` 标记**不代表本轮改过**。

| 文件 | mtime | 早于 22:38？ |
|---|---|---|
| `tools/build_obsolete_index.py` | `10-03 23:28` | ✅ |
| `scripts/release_check.py` | `10-09 14:41` | ✅ |
| `docs/gate-classification.json` | `10-09 14:41` | ✅ |
| `scripts/sw_com_traps.py` | `10-09 19:46` | ✅ |

★ **本轮（22:38 之后）改过**：`tests/test_obsolete_name_host_adjudication.py`（新）·
`tests/test_obsolete_multi_successor_impact.py`（只改 `Name` 一条）· `tests/test_multi_successor_both_needed_census.py`（新）·
`specs/248-*/` · `specs/249-*/` · `docs/ROADMAP.md` · `.workbuddy-ai/memory/2026-10-09.md` ·
`output/AUTO_HANDOFF.md` · `output/AUTO_RUN_*.md` · `.specify/feature.json` · `output/_probe248_*` · `output/_probe249_*` ·
`output/_gate248.log` · `output/_gate249.log` · `output/_mem248.md` · `output/_mem249.md` · `output/_handoff248_*.md` ·
`output/_assemble248.py`。
⇒ ★ **`scripts/` 与 `tools/` 一个文件都没动**。

---

## 四、门禁全套 @3.14.7

```bash
cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/release_check.py > output/_gate249.log 2>&1
```
| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47**（★ 未新增门禁） |
| 耗时 | 约 **2m40s**（★ 后台跑，落盘日志） |

---

## 五、相关族回归

```bash
cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_obsolete_name_host_adjudication.py tests/test_multi_successor_both_needed_census.py -q
```
**读数：`12 passed`**（248 的 6 + 249 的 6）。
★ **生成器链未跑**（★ 没改 `scripts/`）。

---

## 六、★★★ 核心发现（本轮的价值）

### 发现一：**裸名归集又骗了一次**（245 → 248 → **249** 第三次）

第一版探针按**裸成员名**归集 ⇒ 报 **4 条**「两个后继都要」。★ 真象：

| 裸名 | 条数 | 写站点宿主**真**接口 | 15 条里那个接口 |
|---|---|---|---|
| `KFactor` | 3 | **`ICustomBendAllowance`** | `IBendsFeatureData` / `IOneBendFeatureData` / `ISheetMetalFeatureData` |
| `Name` | 1 | **`IMate2`** / **`IFeature`** / **`CWStudy`** | `IView` |

⇒ ★★ **一条都不成立。**

### 发现二：真树上对这批成员名的**写**站点只有 **7 处**

| 站点 | 宿主表达式 | 接口 | 成员 |
|---|---|---|---|
| `sw_sheet_metal.py:257` | `bend_allowance` | `ICustomBendAllowance` | `KFactor` |
| `sw_sheet_metal.py:1288` | `cba` | `ICustomBendAllowance` | `KFactor` |
| `sw_assembly.py:442` | `mate` | `IMate2` | `Name` |
| `sw_gear.py:288` | `feature` | `IFeature` | `Name` |
| `sw_hole_features.py:80` | `feature` | `IFeature` | `Name` |
| `sw_motion.py:137` | `study` | `CWStudy` | `Name` |
| `sw_motion.py:238` | `motor_feature` | 马达特征对象 | `Name` |

⇒ ★★ **没有一处的接口落在 15 条条目的接口集里** ⇒ **0 靶子**。

### 发现三：待办关闭，但**留下触发条件**

★ 靶子表**暂不升级**为可表达多后继 —— ★ 因为**没有靶子**。
★ **触发条件**：`test_no_write_site_targets_a_multi_successor_interface` **变红** ⇒ 那时才立项改表形态。

---

## 七、未过门（如实登记）

1. **靶子表仍表达不了「两个后继」** —— ★ 但**本轮证明无靶子** ⇒ 暂不升级（★ 触发条件见 §六·发现三）。
2. **4 处 `IView::Name` 真命中未换路由**（★ 248 的未过门；★ 非 drop-in，必须真机验）。
3. **`sw_motion.py:238` 的 `motor_feature` 未逐字核官方页** —— ★ 按「马达特征对象」登记；
   ★ 但它**显然不是** 15 条里任何一个接口 ⇒ **不影响结论**。
4. **245 的其余 13 条命中名**仍只登记**名**级结论（★ 未按宿主表达式展开）。
5. **6 条索引错后继仍未修**（改生成器 = 独立工作）。
6. **真机未验**；**223 的 8 条 `HEAD` 即红既有失败未修**；**未提交 / 未部署**。
7. **未调 COM / 真机**；**未删任何文件**；**未派任何成员**；**未 create 或 update 任何自动任务**。
