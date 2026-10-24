# 孤立函数里混着「从没跑通过」的代码

> **什么时候会发现**：把「孤立能力」暴露成工具时。
> **本轮样本**：`scripts/sw_export.py::get_mass_property_override_options`。

## 事实（2026-10-01 轮 93 真机实测）

```
IModelDocExtension.GetMassProperties(1.0)   ⇒ (-2147352561, '非选择性的参数。')
IModelDocExtension.GetMassProperties(0)     ⇒ 同上
IModelDocExtension.GetMassProperties()      ⇒ 同上
IModelDocExtension.GetMassProperties2(1.0, outStatus, False) ⇒ **能跑，但返回扁平浮点数组（13+ 个 float）**
```

`get_mass_property_override_options` 的实现里，拿到返回值后要调
`IMassProperty2.GetOverrideOptions()` —— 而**两条路都拿不到 `IMassProperty2` 对象**：

* `GetMassProperties` 任何参数数都失败；
* `GetMassProperties2` 返回的是**数值数组**，不是接口对象。

⇒ **该函数的前提不成立** ⇒ **不是「参数没调对」，是「从没跑通过」**。

## 为什么一直没人发现

**因为它是个孤立函数** —— 没有调用者、没有测试、没人跑。
⇒ ★ **孤立同时是两个东西**：
* 对「暴露」而言，它意味着**便宜的机会**（接出去就行）；
* 对「正确性」而言，它意味着**从未被验证**。

**两者必须分开处理**：`012`/`013` 的暴露筛选中，只有**真机冒烟过**的才算数。

## 本轮的处置

* **不修**（换路子要查官方 API，超出「暴露」范围）；
* **不暴露**（已从 `tool_specs_batch6.py` 移除，并在文件里写明原因）；
* **记在这里**，作为对剩余 303 个孤立能力的**警示**：
  **暴露前必须真机冒烟，不能只看签名兼容。**

## 可复用的判据

> **签名兼容 ≠ 能用。**
> 一个从没被调用过的函数，**必须先真机跑一次**，再决定要不要暴露。

---

## 追加样本 ②：`scripts/sw_weldment.py::create_cut_list`（轮 94）

```
create_cut_list(零件)  ⇒ TypeError: 'NoneType' object is not callable
  最后两帧：scripts/sw_weldment.py: feature = get_com_member(manager, "InsertWeldmentCutList2", sort…)
            scripts/sw_connect.py:  return member(*args)
```
⇒ `InsertWeldmentCutList2` 在 pywin32 迟到绑定下**解析为 `None`** ⇒ 调用即崩。
⚠ 在**装配体**与**新建零件**上**都崩**（不是输入不合适）⇒ **真缺陷**。

★ 与样本 ① 同一个模式：**孤立函数 = 从没跑过 = 缺陷可以长期潜伏**。

---

## 轮 94 普查结果（17 个暴露候选，真机各调一次）

```
ok 14 · raised 3 ⇒ 其中
   ✓ 真缺陷 2：get_mass_property_override_options · create_cut_list
   ✗ 普查假阳性 1：get_extension（**单独调用是好的**，连调 17 个时才报错）
```

**⇒ 真缺陷率 ≈ 2/17 ≈ 12%**（⚠ **更正轮 93 的「25%」估计** —— 那次样本只有 4 个，且含 1 个假阳性）。

⚠⚠ **普查本身有假阳性**（状态/顺序相关）⇒ **普查只能用来"缩小范围"，
每个 raised 必须单独复验才能定性** —— 否则会把好的函数冤枉成坏的。
