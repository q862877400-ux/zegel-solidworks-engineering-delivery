# Spec — **二级文档对齐**：`phase2-obsolete-status.md` 的旧措辞必须与 `sw_part.py` 的订正一致

**Feature**: `specs/298-phase2-doc-alignment/`
**日期**: 2026-10-10
**上游**: `specs/293-route-change-viability/`（★ 订正了一级真源 `scripts/sw_part.py` 的 3 处错记档）
**触发**: ★ 收 `AUTO_HANDOFF.md` ④ 段登记项 **⑥** 逐字：
「★ `docs/phase2-obsolete-status.md:36` 的旧措辞（「`5` 就是现行那代」）⇒ ★ 与 `sw_part.py` 的订正对齐」。

---

## 一、★★★★ 先量：同一事实写在**两处**，只改了一处

★★ **一级真源**（★ spec 293 已订正 · `scripts/sw_part.py:1457-1466`）逐字：

```
★★★★ **⚠ 订正（★ spec 293 · 2026-10-10）**：★ 此处原写「★ 5 也废弃、★ **后继为空**」——
  ★★★ **那句话是错的** ✗。★ **官方逐字**（C:\swapi\types\IFeatureManager\FeatureLinearPattern5.md:12）：
    「Obsolete. See `IFeatureManager::CreateFeature` and the Remarks in
      `ILinearPatternFeatureData` and `ILocalLinearPatternFeatureData`.」
  ⇒ ★★ **后继不是 `FeatureLinearPattern6`，★ 是 `CreateFeature` + `I*FeatureData`** ✓
★★ **⇒ ∴ `5` 是**本族最高代**、★ 而**不是"没有后继"****
```

★★ **二级文档**（★ 本轮**改前** · `docs/phase2-obsolete-status.md:36`）逐字：

```
| ★ `sw_part.py:1261` | ★ `FeatureLinearPattern5` | ★★ **记档保留** | ★ `output/linear-pattern-baseline-evidence.json`（★ `5` **就是现行那代**）|
```

★★★ **⇒ 问题**：★ 「**`5` 就是现行那代**」这句话**会被读成「没有后继」**（★ 而官方**给了**跨族后继）。
★★ **而这正是** `MEMORY.md` 规则 30 逐字点名的形态：

> 「**「同一事实被写在 N 处」⇒ 必须有一条判据把 N 处串起来** —— ★ 291 实测：`AddMate5` 的**分流语义**
> 被写在 **5 处** ⇒ ★ **前 3 处改了、后 2 处漏了** ⇒ ★★ 「改了 A 没改 B」**永远发现不了**
> （★ 且 docstring 是**施工指令**，会骗下一轮）。」

---

## 二、★★★★ 为什么这是「文档不一致」而不是无害笔误

| ★ 优先级 | ★ 依据 |
|---|---|
| ★ `GOAL.md` §五 第 3 步逐字 | 「★★ **挑最红的那项先做** —— 判据红 > 门禁红 > 真机未验 > **文档不一致**」 |

★★★ **而且它不是无害的**：★ `docs/phase2-obsolete-status.md` 是**处置阶段 2 的状态表**
—— ★ 下一轮读它的人会**据此判断「`FeatureLinearPattern5` 没有后继、不用换」**
⇒ ★★ **而官方给了后继** ⇒ ★ 照它做就会**漏掉一次该换的路由**。

---

## 三、需求

### FR-001 ★★★ 旧措辞「`5` 就是现行那代」不得**作为主张**存在
- **验收场景**：`test_doc_no_longer_says_five_is_the_current_generation` 通过
  （★ **撤回式引述除外** —— ★ 订正**要引旧话**，否则读者不知道改了什么）。

### FR-002 ★★★ 订正处必须写出**官方后继**与「跨族」口径
- **验收场景**：`test_doc_carries_the_official_successor` 通过。

### FR-003 ★★★ **两处必须一致**（★ 规则 30 的形态）
- **验收场景**：`test_the_two_places_agree_on_the_verdict` 通过。

### FR-004 ★★ 二级文档必须**指回一级真源**
- **验收场景**：`test_doc_points_back_to_the_primary_source` 通过。

### FR-005 ★★★ **全篇**不得再有「`5` 没有后继」类的**主张**（★ 不是只看那一行）
- **验收场景**：`test_no_stale_no_successor_claim_anywhere_in_the_doc` 通过。

### FR-006 ★★ **边界冻结**：★ 只改**二级文档**，★ 不动一级真源
- **验收场景**：★ `scripts/sw_part.py` 的订正块**一字未动**（★ 由 `git diff` 可核）。
