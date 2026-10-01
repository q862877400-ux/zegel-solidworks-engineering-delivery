# 015 · 把两个「跑不通的函数」改成**失败可见**

**Status**: Implemented（轮 95）

## 背景
`014` 的普查定性出 **2 个真缺陷**（孤立函数，从没跑通过）：
* `sw_export.get_mass_property_override_options`
* `sw_weldment.create_cut_list`

**修之前它们抛的是**：
```
create_cut_list              ⇒ TypeError: 'NoneType' object is not callable      ← 看不出是「成员取不到」
get_mass_property_override…  ⇒ com_error (-2147352561, '非选择性的参数。')        ← 看不出是「后端不可用」
```

## 为什么不"修好"，而是"让失败可见"
查证表明**两条路都走不通**：
* `IFeatureManager.InsertWeldmentCutList` / `InsertWeldmentCutList2`
  **权威类型库里有**，但 pywin32 迟到绑定**取到 `None`**；
* `IModelDocExtension.GetMassProperties` **任何参数数都失败**；
  `GetMassProperties2` 能跑但**返回数值数组**，拿不到 `IMassProperty2`。

⇒ **不是参数问题，是后端能力问题** ⇒ 与仓库对 `IModeler.Create*Surface` 的先例一致
（已知事实 40）：**不可靠时唯一能修的是「让失败可见」**。

## 判据
| ID | 判据 |
|---|---|
| SC-1101 | `create_cut_list` 在成员取不到时抛 **`RuntimeError`**，消息含**成员名 + 「后端」** |
| SC-1102 | `get_mass_property_override_options` 把 COM 失败**包成 `RuntimeError`**，消息含成员名 + 「不可用」 |
| SC-1103 | 两处 docstring 写明「**跑不通 / 不可用**」与「**后端**」（文档串与代码同步）|
| SC-1104 | 上述三条由**桩测**钉住（不连 COM）⇒ `tests/test_dead_capability_diagnostics.py` **3 passed** |
| SC-1105 | 门禁 + 回归不退化（本次因改了运行时文件，需同步签名审计表与报告数字）|

## 明确不做
不换 COM 后端（`comtypes` / 进程内 C++）—— 那是**另一个量级**的工程，超范围。
