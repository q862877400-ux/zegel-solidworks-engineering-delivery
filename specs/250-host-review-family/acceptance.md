# Acceptance — 245 其余 13 条命中名的宿主表达式级表态

**Feature**: `specs/250-host-review-family/`
**日期**: 2026-10-09
**结论**: ✅ **四件齐 · 判据 6/6 绿 · 红基线三组全红 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 复核结论**: **245 的 13 条名级结论全部通过，无一处翻案。**

---

## 一、逐条验收（对应 `spec.md` 的 FR）

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | 每个命中名都要有宿主表达式级表态（含接口） | `test_every_remaining_name_is_adjudicated` | ✅ **13 名 / 14 站点**全部进表 |
| FR-002 | ★★ 表态与**该名全部条目接口**自洽 | 同上（纯函数第 ③ 查项） | ✅ `real-hit` ⟺ 接口 ∈ 条目接口**集合**，**0 矛盾** |
| FR-003 | 判据**能红**（三组合成负例） | `test_criterion_is_red_able` | ✅ 冒出新名 / 翻码矛盾 / 删条目 **全部判出** |
| FR-004 | 证据站点与重算**逐字相等**（不是子集） | `test_every_remaining_name_is_adjudicated` | ✅ 13 名的站点集合**逐一相等** |
| FR-005 | 下界 | `test_lower_bounds` | ✅ 名 **13** · 站点 **14** · 真 **7** · 假 **7** |
| FR-006 | ★★ 与 245 的**名级**表态跨规格一致 | `test_consistent_with_245_name_level_verdict` | ✅ 13 名逐条一致 |
| FR-007 | 调用口径与互锁**逐条一致** | `test_scan_parity_with_interlock` | ✅ 全部 `scripts/sw_*.py` 逐条相等 |
| FR-008 | 不许改生成器 / 靶子表 / `sw_*.py` / 245 的登记表 | mtime 核（§三） | ✅ 全部早于开工时刻 |

---

## 二、★★ 红基线（★ 本仓纪律：不能红的判据 = 空判据；★ 且「首跑全绿 = 可疑信号」）

★ 本切片判据**首跑 6/6 全绿** ⇒ ★ 按纪律 16 **必须补红基线**。三组实测：

| 变异 | 期望 | 实测 |
|---|---|---|
| **清空表态表** | 13 个名全部报「未表态」 | ✅ **`清空表 => 13`** |
| **把 `SketchTrim` 翻成 `real-hit`** | 报「表态与接口矛盾」 | ✅ **`名 'SketchTrim' 表态 'real-hit' 但宿主接口 ISketchManager ∉ 该名的条目接口 ['IModelDoc2']`** |
| **把 `GetArcs2` 翻成 `real-hit`** | 报矛盾 | ✅ **`名 'GetArcs2' 表态 'real-hit' 但宿主接口 ISketch ∉ 该名的条目接口 ['IView']`** |
| 合成：冒出新名 | 判出 | ✅ |
| 合成：删掉 `KFactor` 条目 | 判出 | ✅ |

★ 命令（★ 可复制）：
```bash
cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
import sys, importlib.util
sys.path[:0]=['D:/AI/SW','D:/AI/SW/scripts','D:/AI/SW/tests']
s=importlib.util.spec_from_file_location('t','D:/AI/SW/tests/test_obsolete_host_review_family.py')
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
h=m._host_sites(); i=m._entry_ifaces()
print('名', len(h), '| 站点', sum(len(v) for v in h.values()))
print('正常:', len(m._adjudication_failures(h, m._HOST_EXPR_REVIEW, i)))
print('清空表 =>', len(m._adjudication_failures(h, {}, i)))
mut=dict(m._HOST_EXPR_REVIEW); c,f_,w,st=mut['SketchTrim']; mut['SketchTrim']=('real-hit',f_,w,st)
print('翻 SketchTrim:', m._adjudication_failures(h, mut, i)[:1])
"
```

---

## 三、★ 未改动证明（★ 用 mtime，**不用 `git status`**）

| 文件 | mtime | 早于本会话开工（22:38）？ |
|---|---|---|
| `tools/build_obsolete_index.py` | `10-03 23:28` | ✅ |
| `scripts/release_check.py` | `10-09 14:41` | ✅ |
| `docs/gate-classification.json` | `10-09 14:41` | ✅ |
| `scripts/sw_com_traps.py` | `10-09 19:46` | ✅ |
| ★ `tests/test_obsolete_multi_successor_impact.py` | `10-09 22:41` | ★ **本轮未动**（那是 **248** 改的）—— ✅ |

★ **本会话（22:38 之后）改过**：`tests/test_obsolete_name_host_adjudication.py`（248 新）·
`tests/test_obsolete_multi_successor_impact.py`（★ 248 **只改** `Name` 一条）·
`tests/test_multi_successor_both_needed_census.py`（249 新）· `tests/test_obsolete_host_review_family.py`（250 新）·
`specs/248-*` · `specs/249-*` · `specs/250-*` · `docs/ROADMAP.md` · `.workbuddy-ai/memory/2026-10-09.md` ·
`output/AUTO_HANDOFF.md` · `output/AUTO_RUN_*.md` · `.specify/feature.json` · `output/_probe*` / `_gate*` / `_mem*` / `_handoff*` / `_assemble*`。
⇒ ★ **`scripts/` 与 `tools/` 一个文件都没动**。

---

## 四、门禁全套 @3.14.7

```bash
cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/release_check.py > output/_gate250.log 2>&1
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
cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_obsolete_host_review_family.py tests/test_obsolete_name_host_adjudication.py tests/test_multi_successor_both_needed_census.py -q
```
**读数：`18 passed`**（250 的 6 + 248 的 6 + 249 的 6）。
★ **生成器链未跑**（★ 没改 `scripts/`）。

---

## 六、★★★ 核心发现（本轮的价值）

### 发现一：**245 的登记有三处不够**

| # | 问题 | 后果 |
|---|---|---|
| 1 | **散文依据不被机检** | ★ 写错了也没人报（★「一句话不是守卫」） |
| 2 | **证据只登记 1 处/名** | ★ `FeatureLinearPattern5` 有 **2 处**站点 ⇒ 表里没有「相等」判据时，漏站点与全登记**同形** |
| 3 | **没有「接口」字段** | ★ 无法机检「`real-hit` ⟺ 宿主接口 == 条目接口」这条**定义** |

### 发现二：★★★ **一个命中名可跨多个条目接口**

| 名 | 条目接口 |
|---|---|
| `GetMassProperties` | `IModelDoc2` · `ISldWorks` |
| `GetSplines` | `ISketchBlockDefinition` · `IView` |
| `KFactor` | `IBendsFeatureData` · `IOneBendFeatureData` · `ISheetMetalFeatureData` |

⇒ ★ **名级表态答不了「我们调的是哪一个接口的成员」** ⇒ ★ 表态表**必须带接口字段**。

### 发现三：13 条名级结论**全部通过**

**真命中 7 处** = `extension`(`IModelDocExtension`) · `FeatureManager` 的两种写法(`IFeatureManager` ×2) ·
`fm`(`IFeatureManager`) · `_mgr`(`IFeatureManager`) · `definition`(`IBendsFeatureData`) · `model`(`IModelDoc2`)；
**假命中 7 处** = `sketch`(`ISketch` ×5) · `extension`(`IModelDocExtension`，★ 条目是 `IModelDoc2`/`ISldWorks`
⇒ **我们调的正是后继**) · `get_com_member(model,"SketchManager")`(`ISketchManager`，★ **非废弃**)。
⇒ ★ **无一处翻案。**

---

## 七、未过门（如实登记）

1. **7 处真命中未换路由** —— ★ 需 COM 授权；★ `FeatureLinearPattern5` / `FeatureLocalCurveDrivenPattern` /
   `InsertFormToolFeature`（⇒ `CreateFeature` / `CreateDefinition`）**都不是 drop-in**（★ 要先造 `I*FeatureData`）。
2. **245 的名级表态未被改动** —— ★ 本轮是**独立复核**（★ 结论 = 13 条全部通过）。
3. **`sketch` 的接口**沿用 245 的判读（★ 未逐字核官方页，★ 但已进**机检自洽**）。
4. **6 条索引错后继仍未修**（★ 改生成器 = 独立工作）。
5. **真机未验**；**223 的 8 条 `HEAD` 即红既有失败未修**；**未提交 / 未部署**。
6. **未调 COM / 真机**；**未删任何文件**；**未派任何成员**；**未 create 或 update 任何自动任务**。
