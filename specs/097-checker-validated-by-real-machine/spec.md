# 097 · 修好断链，并**第一次用真机验证了检查器的命中**（13 处全部有真机支持）

**Status**: Implemented（轮 177）

## 一、★★★ 链断点定位
```
`mold_evidence` 的 `_count` 里 `get_com_member(fm, name)` 推不出 `fm` —— 因为**建表**那处只查**裸名**：
  反射里是 `FeatureManager get_FeatureManager()`      ← **属性带 `get_` 前缀**
  而代码写 `get_com_member(model, "FeatureManager")`  ← **裸名**
  ⇒ 建表时 `mem in d["returns"]` **一律查不到** ⇒ `ret=None` ⇒ 变量**进不了表**
⇒ ★★ 我在**查询**处做了 `canon_member` 规范化，**却忘了建表处** ——
  **同一个坑踩两次**（事实 113/115/116 同族：都是"规范化只做了一半"）。
```

## 二、修法与效果
```
修：建表时**三种写法都试**（`mem` / `canon_member(mem)` / `"get_" + mem`）
效果：检查点 **33 → 45** · 命中 **6 → 13**（`_count` 的 `fm` 那条链**也**命中了）
```

## 三、★★★ 真机核对了新命中（`tools/verify_mold_draft_analysis_owner.py`，**3/3 pass**）
```
反射 (官方源):  MoldDraftAnalysis 出现在 **['IModelDoc2']**
✓ 真机**否定**：IFeatureManager.MoldDraftAnalysis ⇒ **AttributeError: <unknown>.MoldDraftAnalysis**
✓ 真机**肯定**：IModelDoc2.MoldDraftAnalysis      ⇒ **能取到**（method）
⇒ ★★★ **三条独立证据指向同一结论**（反射 / 真机否定 / 真机肯定）
```

## 四、★★★ 为什么这一步重要
```
★ 这是检查器**第一次**在一个**新**位置（不是我先前查过的）抓出真问题，
  并被真机证实是**真阳性** ⇒ **它不再只是「看起来在查」**（事实 62 那种假绿）。
★ 而且这是**轮 176 那 6 处之外的**第 7 处**：
  `mold_draft_analysis` 也把成员取在了 `IFeatureManager` 上（`MoldDraftAnalysis` 属 `IModelDoc2`）
  ⇒ **一处真 bug**（⚠ **尚未修** —— 本轮只做了核对）。
★ 现状：**13 处命中** = 那 6 个成员 × 2 条链（`fm` / `model`，轮 172 核过）+ 1 处 `MoldDraftAnalysis`（本轮核过）
  ⇒ ★ **13 处全部有真机支持**。
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-9701 | ★★★ **定位链断点**（建表处漏规范化 ⇒ 变量进不了表）|
| SC-9702 | ★ 修（三种写法都试）⇒ 检查点 33 → 45 · 命中 6 → 13 |
| SC-9703 | ★★★ **真机核对新命中**（反射 + 真机否定 + 真机肯定，三条独立证据）|
| SC-9704 | ★★ 结论：检查器**第一次被真机证实能抓真阳性** |
| SC-9705 | ★ 发现第 7 处真 bug（`mold_draft_analysis`）—— ⚠ **未修** |
| SC-9706 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ **未修 `mold_draft_analysis`**（本轮只核对；它是**真 bug**：成员取在了 `IFeatureManager` 上）；
* ⚠ 13 处里那 6 个成员的**两条链**算 12 处（同一批成员的两种取法）⇒ **独立问题实际是 7 个**；
* ⚠ 47 处未检查项**仍在**；
* ⚠ 检查器的**判据仍可能在其未覆盖处出错**（本轮只验证了命中的那 13 处）。
