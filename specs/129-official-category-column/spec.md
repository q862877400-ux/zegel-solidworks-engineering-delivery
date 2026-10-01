# Feature Specification: 接入官方接口分类（`category`），并量清「未认领」族

**Feature Branch**: `129-official-category-column` · **Created**: 2026-10-01 · **Status**: Implemented

**Input**: 外部只读审计 `D:\AI\SW-transfer\official-category-unused.md` + 用户指示「把这个分类的问题先解决掉」。

## 来源（§I / §IV）
| 需求 | 来源 | license |
|---|---|---|
| `family-coverage` 加「官方 category」一列 | **本项目自身**（扩既有的 `tools/gen_family_coverage.py`）| 本仓库 **MIT** |
| `category` 字段本身 | ⚠ **`C:\swapi\types\<接口>\*.md`** ＝ **help 站点的文档镜像**（来源仓 `offline-solidworks-api-docs`，**无许可**）⇒ ★ **只读思想、不入闭源分发**（既有口径见 `docs/sources.md`）| **无许可** |
| 「未认领族」的算法 | **本项目自身**（`_dedupe_domains()` 的「一族只算一次」口径）| 本仓库 **MIT** |
| 外部审计的四条建议 | `D:\AI\SW-transfer\official-category-unused.md`（**两仓库之外的只读报告**）| 不适用（分析，未抄文本）|

## 来源裁定（§II / §III：这一列**只有一个源**，先说清）
```
★ `category` 只存在于 `C:\swapi`（help 站点镜像）。
  实测：**两份出厂反射转储都没有该字段**
    · iface_sldworks.txt  —— 只有接口名（`## AdvancedHoleDesignData`）
    · iface_cosworks.txt  —— `<接口> :: <返回类型> <方法名>(<参数类型>, ...)`
  ⇒ ★ **无法按铁律 4 做三源互证**（裁决者给不出这个字段）
  ⇒ 本列**只能标成"单一来源的分类"**，用在「分类 / 校验 / 发现空白」，
    **不能**用它推「该不该做成工具」（标签说的是接口**是什么**，不是我们**需不需要**）。
```

## User Scenarios & Testing

### User Story 1 - 让「未认领」的族有第二个归属可查（Priority: P1）
现状：881 个接口族里**近六成**的 `domain` 是 `全量索引/<程序集>`（即没被 14 个业务域的正则认领）。
希望：能一眼看到这些族**官方是怎么分类的**，从而判断哪些其实有归属、哪些真的该留在原处。

**Independent Test**: 跑生成器后，`family-coverage.md` 的 §四 里能看到「未认领族按官方一级分类」的清单。

**Acceptance Scenarios**:
1. **Given** 生成器跑完，**When** 读 `family-coverage.json` 的任一行，**Then** 有 `official_category` 字段（读不到是**空串**，不是缺字段）
2. **Given** 生成器跑完，**When** 读 md 的 §四，**Then** 有「未认领族合计 **507/881 = 57.5%**」与「其中能归位 **340/507 = 67.1%**」
3. **Given** §四，**When** 读它的来源声明，**Then** 明写「只有一个来源、无法三源互证」

### User Story 2 - 纠正外部审计的两处读法（Priority: P2）
审计报告的两处需要更正，而更正本身要落进产物（否则下一个人会照着错的读）。

**Independent Test**: 读 §四 的 `4.2`，能看到「审计只数了 `全量索引/sldworks` 一个桶（385 / 43.7%）⇒ **低估**」。

**Acceptance Scenarios**:
1. **Given** 审计说「385 / 881 = 43.7% 未分类」，**When** 把九个 `全量索引/*` 桶加总，**Then** 得 **507 / 881 = 57.5%**
2. **Given** 审计说那是「兜底桶」，**When** 读 `_dedupe_domains()` 的 docstring，**Then** 看到那是「**一族只算一次**」的产物（1,090 → 774 的去重纪律）

## 明确不做
| 不做 | 理由 |
|---|---|
| **替换**业务域 | ★ 两者维度不同（厂商视角 vs 业务视角）；审计自己也这么说（`ISelectionMgr` 官方归 Utility，本项目归「应用与会话」是**业务判断，不是错**）|
| 用一级分类判「该不该做工具」 | ★ 那是**把标签当判据** —— 本项目禁止「看着像就当成」 |
| 声称该列「经官方核过」 | ★ 出厂反射没有该字段 ⇒ **无法互证**（如实标"单一来源"）|
| 全量对照「手写域 vs 官方类」的错位 | ★ 那是**下一件**（本特性只把列接进来，对照留待用它去做）|
