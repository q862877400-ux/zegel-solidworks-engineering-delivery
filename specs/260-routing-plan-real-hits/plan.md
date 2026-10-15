# Plan — 250 的 6 名 7 处真命中的换路由先量

**Feature**: `specs/260-routing-plan-real-hits/`
**日期**: 2026-10-10

## 一、三源与冲突裁决顺序

| 序 | 源 | 用途 | 权威度 |
|---|---|---|---|
| 1 | ★★ **官方索引** `official-obsolete-index.json` | **后继**真源 | ★★★ |
| 2 | **官方页** `C:/swapi/types/**` | 废弃句原文 | ★★ |
| 3 | **250 的表态表** `_HOST_EXPR_REVIEW` | 真命中站点 | ★★ |
| 4 | **真树源码** | 现调写法 | ★ 事实 |

**冲突裁决顺序**：1 > 2 > 3 > 4。★ **后继一律以索引为准**（★ 不手抄）。

## 二、口径

| 口径 | 真源 | 怎么用 |
|---|---|---|
| 真命中站点 | `tests/test_obsolete_host_review_family._HOST_EXPR_REVIEW` | ★ **import** |
| 后继 | `official-obsolete-index.json` 的 `entries`（★ **list of dicts**） | ★ 运行时查 |
| 索引键 | ★ **`(源接口, 成员名)`** | ★★ 不是 `(后继接口, 成员名)` |

## 三、实现步骤

1. **先量**：列 6 名 7 处（★ 文件 · 行号 · 宿主表达式）。
2. **查后继**：★ 逐名查索引（★ 用**源接口**）。
3. **定改法**：★ 按后继形态分 `rename` / `adapt-args` / `needs-feature-data`。
4. **写判据** → 证明能红（★ 判据第一次跑就红了两条 ⇒ ★ 修的是**判据**，不是数据）。
5. 门禁 + 回写四处。

## 四、改动面

`tests/test_routing_plan_real_hits.py`（新）· `specs/260-*/`（新）· 四处状态。
★ **未改** `scripts/` ⇒ ★ **不跑生成器链**。

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| ★★ 手抄后继 ⇒ 双盲 | ★ 判据**运行时查索引**逐字比对（★ FR-002） |
| ★★ 把「造 `*FeatureData`」当成「改名」 | ★ 判据钉住 `needs-feature-data ≥ 4`（★ FR-003） |
| ★ 用 `grep obsolete` 判废弃 ⇒ 假阴性 | ★★ 定则写进 spec §二（★ `DeleteRenderMaterial` 就是反例） |
| ★ 查索引用了后继的接口 | ★★ 计划表**存源接口**，判据核对它等于 250 记的那个 |
