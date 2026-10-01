# 098 · `mold_draft_analysis` 两处错（对象 + 返回类型）修好并**真机闭合**（4/4）

**Status**: Implemented（轮 178）

## 一、两处错（都由轮 177 的静态检查器抓出）
```
① **对象错**：原实现 `fm = get_com_member(model, "FeatureManager")` 再取 `MoldDraftAnalysis`
   ⇒ 真机 `IFeatureManager.MoldDraftAnalysis` = **AttributeError: <unknown>.MoldDraftAnalysis**
   ★ 官方两源一致：它在 **`IModelDoc2`** 上
     · 反射 `Void MoldDraftAnalysis(Double, Int32, Object, Int32)`（IModelDoc2 段）
     · `C:/swapi/types/IModelDoc2/MoldDraftAnalysis.md`
② **返回类型写反**：原 docstring 说「返回码为 `Int32`，非 0 不一定是失败」
   ★ 官方是 **`Void`** ⇒ **没有返回码** ⇒ 整句都错
```

## 二、真机复验 **4/4 pass**
```
✓ ① IFeatureManager.MoldDraftAnalysis ⇒ **AttributeError**（否定）
✓ ② IModelDoc2.MoldDraftAnalysis     ⇒ **能取到**（method，肯定）
✓ ③ 改后 `mold_draft_analysis` 可调用（**不再 AttributeError**）⇒ 返回 **bool**
✓ 收尾无残留
⇒ ★★★ **改前 AttributeError · 改后能调** ⇒ **真机闭合**
```

## 三、⚠⚠⚠ 本轮我下过一个**错的结论**并当场纠正
```
看到真机回 `bool` 而我 docstring 写 `None`，我一度推断「**这个函数从来没真正调用过**」
★ 依据是我**自己写的测试桩**：`_Model(..., MoldDraftAnalysis=md)` 把 `_Recorder` 的**实例**
  设成属性（**不可调用**）⇒ `get_com_member` 调用失败、静默返回成员本身 ⇒ **看起来「没调用」**
★★ **真相**：`get_com_member` 的语义是「**取或调**」，**有实参 ⇒ 一定调用**（它自己的 docstring 明写）
⇒ ★ **是我的测试桩错了，不是实现错了。**
```

> ★ **教训（可复用）**：**用桩下结论之前，先确认桩自己是对的** ——
> 否则会把自己的**脚手架缺陷**当成**被测代码的缺陷**。
> ⚠ 这与事实 113~117 的「**用猜填不知道**」**形状不同**：这次是「**用错误的观测下结论**」。

## 四、★ 顺带更正一处细节
```
pywin32 对 **`Void`** 调用**往往回 `True`** ⇒ `:returns:` 写成 `None` **不精确**
⇒ 已改成「官方是 `Void`；pywin32 可能回 `True`/`None`；**不得当作成败**」
★ 并让契约测试断言「**不是**被当成成败的整数返回码」（`True`/`None` 都可，数字不行）
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-9801 | ★★ 修**对象错**（从 `IModelDoc2` 取）|
| SC-9802 | ★★ 修**返回类型写反**（`Void` ⇒ 没有返回码）|
| SC-9803 | ★★★ **真机复验 4/4**（否定 + 肯定 + 改后能调 + 收尾）|
| SC-9804 | ★ 改契约测试（它钉着**两条错的**语义）⇒ **11 passed** |
| SC-9805 | ★★★ **如实记下我那个错的结论**（桩错 ≠ 实现错）|
| SC-9806 | 静态命中 13 → 12（那处真问题被修掉）· 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ `MoldDraftAnalysis` 的**实际效果未验**（只证「调得到」+「不抛 AttributeError」）；
* ⚠ `swDraftAnalysisOptions_e` / `swDraftAnalysisShow_e` 的**枚举值未逐条查证**；
* ⚠ 它**仍可能弹模态框**（未定义拔模方向时）⇒ 调用方需配兜底（⚠ 本轮真机上**没弹**，但那不构成保证）；
* ⚠ 那 12 处命中里，**只有 1 处**（`MoldDraftAnalysis`）本轮被真机核过；其余 11 处（那 6 个成员的
  两条链）**在轮 172/177 核过** ⇒ ★ **独立问题实际是 6 个**。
