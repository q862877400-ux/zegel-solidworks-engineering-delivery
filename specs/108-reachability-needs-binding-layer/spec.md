# 108 · 可达性结论必须带**绑定层次**限定 —— 更正轮 186 过强的「到不了」

**Status**: Implemented（轮 188）· ★ **本轮是对**上一轮自己的更正****

## 一、起因：上轮的记录**过强**
```
轮 186：pywin32 **迟到绑定**下测得 `ISafeArrayUtility` 21/21 不可达 + 无 dispinterface
        ⇒ 记成「**到不了**」（**未限定层次**）。
⚠ 同一轮我在括号里也写了限度「未试 comtypes / C# PIA」—— 本轮就去闭它。
```

## 二、★★★ 实测（`tools/probe_safearray_comtypes.py`）
```
① comtypes.client.GetActiveObject('SldWorks.Application') ⇒ **附着同一实例**
   （comtypes PID=20456 ⇒ 与运行中的那个**同一个**；**没起第二个实例** —— 事实 24 红线）
② cc.GetModule('…/sldworks.tlb') ⇒ 模块 comtypes.gen.SldWorks，**里面有 ISafeArrayUtility**
③ ★★★ **QueryInterface(ISafeArrayUtility) 成功** ⇒ 对象**真的实现**那个 vtable 接口
⇒ ★★ 正确的是「**pywin32 迟到绑定看不到它**」，**不是**「接口不存在 / 到不了」
```

## 三、⚠ 但**往返没走通**（如实记）
```
PutDouble(arr, 0, 1.5) ⇒ 不报错（类型库说它确实要 **3** 参、VariantArray 是 **in,out**）
但 arr.value=None、GetDouble 读回 **0.0** ⇒ **in,out 的 VARIANT 数组没回写**（事实 68 同族）
⇒ 按事实 53 **不继续凑形态**；「能否正确构造 SAFEARRAY」**本轮未走通**。
```

## 四、★★ 而它对我们**没有净收益**（这条才决定结论）
```
对照（同一探针 ⑥）：pywin32 的 `VARIANT(VT_ARRAY|VT_R8, [...])` 与
                   `VARIANT(VT_ARRAY|VT_DISPATCH, [...])` **本来就能构造数组**
                   （事实 123 / 167 就是这么修的）
⇒ ★ 它是**给 C++ 弥补「没有原生数组」**的；脚本语言的绑定层**已经替我们做了**
⇒ ★ 本后端仍然「**不做**」，但**理由从「够不到」改成「够得到但没有净收益」**。
```

## 五、★★★ 立下的新定则
> **可达性结论必须带「绑定层次」限定**：`pywin32 迟到绑定` / `comtypes 早绑定` /
> `C# PIA` / `进程内 C++` —— **四层结论不能互相顶替**。
> ⚠ 不带层次的「到不了」会被后来人读成「**官方没这个能力**」。

## 六、★★★ 副产：**类型库的方法表是第 4 套官方签名源**
```
comtypes.client.GetModule('<xxx.tlb>').<IIface>._methods_
  每条 = (HRESULT, 名字, argtypes, flags(名 + 方向), id, 描述)
★ 它**直接给出 [in] / [out] / [in,out]** ——
  反射文本只给 `&`、swapi md 只给措辞（`out` / `ref`），**两套源都没这么直白的方号**。
实例：PutDouble(VariantArray=**in,out** · Index=in · Value=in) ⇒ **3 参**
     GetDouble(VariantArray=in · Index=in · Value=**out**) ⇒ 2 参，出参作返回值
⇒ ⚠ 我第一版**按 md 的措辞**传 2 个实参 ⇒ `TypeError: required argument 'Value' missing`
```

## 七、判据
| ID | 判据 |
|---|---|
| SC-10801 | ★★ 附着同一实例（**不起第二个** —— 事实 24 红线）|
| SC-10802 | ★★★ **`QueryInterface` 成功** ⇒ 更正轮 186 的「到不了」|
| SC-10803 | ⚠ **如实记**：`in,out` 数组**没回写**、往返**未走通**（不吹）|
| SC-10804 | ★★ 用**对照**得出「**没有净收益**」（pywin32 原生就能构造数组）|
| SC-10805 | ★★★ 立定则：**可达性结论必须带绑定层次** |
| SC-10806 | ★★★ 副产：**类型库方法表**（带 `[in]/[out]`）是第 4 套官方签名源 |
| SC-10807 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ **往返没走通** ⇒ 「comtypes 早绑定**能正确驱动** `ISafeArrayUtility`」**仍未证明**
  （已证的是：**接口可 QI 到、方法可调用、实参形态已对**）；
* ⚠ 只试了 `PutDouble` + `GetDouble` 一对，**其余 19 个成员未逐个试**；
* ⚠ C# PIA / 进程内 C++ 两层**未试**（定则说要分层说，但本轮只覆盖前两层）；
* ⚠ 本轮**没改**任何生产代码（结论仍是「不做」）。
