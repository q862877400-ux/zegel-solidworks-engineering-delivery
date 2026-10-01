# 086 · `AddIndicator` 穷尽 20 组后判定「这条后端到不了」—— 并拆出可用那一半

**Status**: Implemented（轮 166）· ✅ `gtol_insert` 升 `verified`

## 一、动机（顺 `085` 的尾巴）
`085` 把帧路径打通了，但 `AddIndicator` 仍 `False` ⇒ 本轮**先读官方 Remarks**（上轮刚学到的）。

## 二、★★★ Remarks 里藏着**取值限制**
```
C:/swapi/types/IGtolFrame/AddIndicator.md 的 Remarks **原文**列出：
  TolType may be one of only swGtolGeomCharSymbol_e.:
    swGcsANG(20) · swGcsPARALLEL(22) · swGcsPERP(21) · swGcsCIRCRUNOUT(25) · swGcsSYMMETRY(13)
⇒ ★★ 而 GTOL_GEOM_SYMBOL 里另外 **14** 个（flatness / position / straightness …）**都不在清单里**
⇒ 传它们**必然 False** —— 而★**契约测试当时正用 `position`(23) 断言它会成功**
  （又一次「假对象看不见官方取值限制」）
```

## 三、★★★ 穷尽式结论（`tools/probe_gtol_indicator_matrix.py`）
```
BorderType(0..3) × TolType(5 个合法值) = **20 组全试**
★ 每一组的帧**都拿到了**（GetFrame(1) 非 NULL）
⇒ **20 组全返回 False**
⇒ 不是「取值不对」⇒ **这条后端（pywin32 迟到绑定）到不了这一个成员**
  （与事实 47 那族同类：多出参 / 需指针的接口）
```

## 四、★ 处置（三条）
```
① 给 add_gtol_indicator 加**清单校验** ⇒ 错值当场 ValueError
   （过去它表现为模糊的 False，会被读成"到不了"）
② **拆出 `gtol_insert`（verified）** 覆盖「新建 GTol + 帧路径」那一半
③ `geometric_tolerance` **仍 `stitched`**（含「加指示符」那半）
   ★ 与轮 164 倒角那次**同一决策**：**冒烟只覆盖哪一半，就只升哪一半**
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-8601 | ★★ 读 Remarks 找出**取值限制**（只允许 5 个）|
| SC-8602 | ★★ 给函数加**清单校验**（错值当场报）|
| SC-8603 | ★★★ **20 组穷尽矩阵** ⇒ 断定「这条后端到不了」 |
| SC-8604 | ★ 拆出 `gtol_insert`（verified）；`geometric_tolerance` 留 `stitched` |
| SC-8605 | ★★ 改契约测试（它**用了非法值**）+ 写明理由 |
| SC-8606 | 能力 **38 → 39**（verified **32 → 33**）；门禁 + 回归不退化（回归 **1246 passed**）|
| SC-8607 | ⚠ **如实记下本轮又两次切坏文件**（事实 61）|

## ⚠ 明确记下的限度
* ⚠ `AddIndicator` 只是「**这 20 组在这条后端上不成**」⇒ **不排除**换后端（`comtypes`）能成；
* ⚠ 未试 `SetSymbolXml`（XML 路径）—— ⚠ 但它也**需要先拿到 frame**，而 frame 已拿到 ⇒ 值得下次试；
* ⚠ `gtol_insert` 只证「拿到对象」，**不证公差标得对**；
* ⚠ 本轮**两次**切坏文件（`sw_gtol.py` / `test_sw_gtol_contract.py`）⇒ 都用 `git checkout` 恢复 +
  改用 `edit`；★ **「改完先看 `git diff --stat`」这条我仍未养成动作习惯**。
