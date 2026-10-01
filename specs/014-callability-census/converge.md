# 014 · Converge

**Converged**: 2026-10-01（轮 94）

## 一、普查结果
```
17 个暴露候选（签名兼容现有注入的那批），真机各调一次：
   ok        14
   raised     3  ⇒ 逐个复验后：
        ✓ 真缺陷 2：get_mass_property_override_options · create_cut_list
        ✗ 假阳性 1：get_extension（**单独调用是好的**，连调 17 个时才报错）
```
**⇒ 真缺陷率 ≈ 2/17 ≈ 12%**。

## 二、★ 更正轮 93 的估计
轮 93 说「抽 4 个撞上 1 个坏的 ⇒ **约 25%**」。本轮证明：
* 那次样本只有 **4** 个；
* 而且那 1 个「坏的」里**不含**假阳性（那次确实是真缺陷）；
* 扩大到 17 个后，比率降到 **12%**。
⇒ **4 个样本估不出比例** —— 这正是本轮做普查的理由。

## 三、⚠⚠ 普查**自己**有假阳性（这是本轮最该记住的）
`get_extension(model)` 在普查里报 `TypeError: This dispatch object does not define a Count method`，
**单独调用却完全正常** ⇒ 失败与**前面那 16 次调用造成的状态**有关。

★ **⇒ 普查只能用来「缩小范围」；每个 raised 必须单独复验才能定性。**
否则会把**好的函数冤枉成坏的** —— 那和"坏函数被放过去"一样有害。

## 四、两个真缺陷的共性与处置
| 函数 | 症状 | 处置 |
|---|---|---|
| `sw_export.get_mass_property_override_options` | `GetMassProperties` 任何参数数都失败；`GetMassProperties2` 返回数组而非接口 | **不暴露**（轮 93 已剔除）|
| `sw_weldment.create_cut_list` | `InsertWeldmentCutList2` 在迟到绑定下解析为 `None` ⇒ 调用即崩 | **不暴露**；记档 |

★ 共性：**都是孤立函数** ⇒ **孤立 = 从没跑过 = 缺陷可以长期潜伏**。

## 五、未查证
* **剩下 283 个孤立能力**（300 − 17）**没查** —— 本轮只查了"暴露候选"那批。
  若要普查全部，需为每个备前置条件，**成本需要单独立项**；
* `create_cut_list` 的**正确调用方式**未查（不知道 `InsertWeldmentCutList2` 该用什么替代）。
