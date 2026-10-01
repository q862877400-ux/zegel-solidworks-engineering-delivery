# 106 · `ISafeArrayUtility` 是**给 C++ 的**，pywin32 到不了 —— 一条外部「高杠杆」建议被实测否定

**Status**: Implemented（轮 186）· ⚠ **负结果**（含一个**被证伪的静态信号**）

## 一、起因（外部评审 §七）
```
一条外部评审把 `ISafeArrayUtility`（台账 used=0、21 成员）列为本项目**唯一高杠杆**缺口：
「官方给了数组工具集，而本项目到处手搓 VARIANT(...)」——
  事实 12 / 33 / 68 / 123 / 167 都是这类坑
★ 但评审**没验证可达性**（它自己 §十三 写了「未连 SolidWorks」）。
```

## 二、★★★ 实测否定
```
tools/probe_safearray_utility.py（真机 · CommandInProgress 置位 · 不开文档 · 收尾轮询点掉）
① ISldWorks.GetSafeArrayUtility()  ⇒ **返回 CDispatch（对象拿得到）**
② 官方登记的全部 **21 个成员**逐个试 ⇒ **可达 0/21**（每个都 `AttributeError: <unknown>.X`）
③ 类型信息内省 ⇒ `com_error(-2147352565, '无效索引。')` ⇒ **没有可用的 dispinterface**
```

## 三、★★ 官方自己写明了原因
> "The ISafeArrayUtility interface replaces the SOLIDWORKS **SafeArray template class**, which you might
>  have used in earlier versions of SOLIDWORKS to instantiate SafeArrays for methods requiring Variant
>  arrays in **your C++ projects**." —— `C:/swapi/types/ISafeArrayUtility/_overview.md`

⇒ ★★★ 它是**取代 C++ 的 SafeArray 模板类**的便利件；在脚本语言里**本就有原生数组**
⇒ **它不是我们手搓 `VARIANT(...)` 的替身**。
★ 与**事实 47**（`IAccessSelections` / `SetFixedFace`「仅进程内非托管 C++」）**同一族**。

## 四、⚠⚠⚠ 一个被我**证伪**的静态信号（差点做成门禁）
```
猜想：`IX` 有成员、而它的无 I 孪生段存在且为空 ⇒ 只有 vtable ⇒ 迟到绑定到不了
实测：1032 个接口段里 **504 对有孪生、502 对的孪生是空的**
★★ 而其中包含 ISldWorks / IModelDoc2 / IFeatureManager / ISketchManager / ISelectionMgr / IFace2
   —— **这些全都能用** ⇒ 该信号**完全不能预测可达性**
⇒ ☆ 若做成门禁，会**同时**给出 **502 个假阳性**
```

## 五、★ 立下的可复用判据
> 判「一个官方接口在本后端可达吗」**只能真机逐接口穷尽枚举**（全部成员名 + 类型信息），
> **没有静态捷径** —— 与事实 47 的结论一致。

## 六、判据
| ID | 判据 |
|---|---|
| SC-10601 | ★★ 从反射拿到官方 21 个成员名单（**穷尽**，不只试几个）|
| SC-10602 | ★★★ 真机逐成员试 ⇒ **0/21** + 无 dispinterface |
| SC-10603 | ★★ 找到官方的**原因**（Remarks：取代 C++ 的 SafeArray 模板类）|
| SC-10604 | ★ 记进 `backend_catalog`（A1 的「不做 + 原因」正主）|
| SC-10605 | ★★★ **证伪**那个诱人的静态信号（并写出若做成门禁的后果：502 假阳性）|
| SC-10606 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ 未试 `comtypes` / C# PIA 后端（它们**可能**能驱动 `out` 形参）—— 本轮只判 **pywin32**；
* ⚠ 「0/21 可达」是**迟到绑定**口径；若有现成 makepy 生成的早绑定模块，结论**未验**；
* ⚠ `PackVariant` 的 `ref Int32 Data` 形态**始终没查明**（因为压根够不到）；
* ⚠ 本轮**没有**因此改动任何生产代码（结论是「不做」，不是「实现」）。
