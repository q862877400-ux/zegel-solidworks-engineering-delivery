# 081 · `AddRelation` 的调用形态 —— 它此前**从没在真机上跑通过**

**Status**: Implemented（轮 161）· ✅ **修好了一个「真机从没跑通」的函数**

## 一、起因（顺 `080` 的在上下文链）
`080`（轮 161 前半）里 `add_relation` 报 `TypeError: 'NoneType' object is not callable`
⇒ ★ 而它在**契约测试里是绿的** ⇒ **说明它从没在真机上跑通过**（假对象看不见实参形态）。

## 二、★★★ 真机判别实验（`tools/probe_add_relation_forms.py`）
```
① 「实参形态」逐个试，**每次都回读 `GetRelationsCount`**（事实 94：别信返回值）
    list[0:2]                       ⇒ com_error 0x80010105 · 计数 3 → 3（**没加上**）
    tuple(0,1)                      ⇒ 同上
    VARIANT(VT_ARRAY|VT_DISPATCH)   ⇒ **无错** · 计数 **3 → 4** ⇒ ★★ **加上了**
```
⇒ ★★★ **`AddRelation(Object, Int32)` 的 `Object` 是 SAFEARRAY** ⇒
**必须包 `VARIANT(VT_ARRAY | VT_DISPATCH, [实体…])`**，裸 `list`/`tuple` 都不行。

## 三、★ 一个**同码不同因**的坑
```
那个错误码 `0x80010105`（「服务器出现意外情况」）与事实 28/47 **同一个码** ——
  事实 28：`CreateBsplineSurface`
  事实 47：`AccessSelections` 传 VARIANT 时
  本轮  ：**数组实参没包 VARIANT**
⇒ ★ 报错本身**看不出是哪一种** ⇒ 只能靠「逐个形态试 + 回读计数」分开。
```

## 四、★ 修法与连带发现
```
修：`sketch_relations._dispatch_array()` 把实体序列包成 SAFEARRAY。
⚠ 连带：**既有契约测试红了** —— 它用假对象把 `'ENTS'` 当实体传、断言**原样透传** ⇒
  改成断言「**包过**」，并**把理由写进测试的 docstring**。
★ 这是本会话**第三次**「假对象测试看不见真契约」（事实 99 / 101 / 本轮）。
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-8101 | ★★ 三种实参形态逐个试，**每次回读计数** |
| SC-8102 | ★★★ 找到**唯一可行**的形态（`VARIANT(VT_ARRAY|VT_DISPATCH)`）|
| SC-8103 | ★ 记录**同码不同因**（`0x80010105` 现在有三种成因）|
| SC-8104 | ★ 修 `add_relation` + 改契约测试（并把理由写进 docstring）|
| SC-8105 | 门禁 + 回归不退化（回归 **1246 passed**）|

## ⚠ 明确记下的限度
* ⚠ **在上下文链仍未打通** —— 卡在「拿到 `IComponent2` 并选中它的边」：
  `asm.GetComponents(True)` 给回来的对象上**没有 `GetBody2`**（接口族可能不是 `IComponent2`）；
  按**事实 53**（≥3 次就停）**已停下**，不再换写法；
* ⚠ 所以**提案 §六 的判据①②仍没绿**，**外部参考仍未建立**；
* ⚠ `AddRelation` 的形态只在**零件草图**上验过（装配上下文没验）。
