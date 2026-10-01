
---

## 二十八、**决定性结论**：那三条不是「参数没找对」，是**后端到不了**（2026-10-01）

### 28.1 两轮 20+ 种形态，全部失败
```
SetFixedFace(X,Y,Z,EdgeArray):
  · **七种数组包装**（None / [] / VT_ARRAY|VT_DISPATCH / VT_ARRAY|VT_VARIANT /
    裸边列表 / 逐元素 VARIANT / VT_DISPATCH(边)）× **两个重载**（4 参 / 1 参）
    ⇒ 全部 `类型不匹配`（位置 1 或 4）
  · 先**预选边**再传空数组 ⇒ 同样失败
AccessSelections(model, None)                        ⇒ `类型不匹配`（位置 2）
AccessSelections(model, VARIANT(VT_DISPATCH,None))   ⇒ **`服务器出现意外情况`（0x80010105）**
```

### 28.2 ⇒ 这是**已记录的架构性限制**
`0x80010105`（`RPC_E_SERVERFAULT`）**与已知事实 28 的 `CreateBsplineSurface` 同一个错误码**。
而 `capabilities.yaml` 的 `backend_catalog` 里**早就写着**：

> 「**不能调用官方标记为仅进程内非托管 C++ 的指针接口**」

反射里那对 **`IAccessSelections` / `IAccessSelections2`** 正是那种 **`I` 前缀的指针变体**。

### 28.3 结论（写死，避免后人重走）
**`create_one_bend` / `create_edge_flange` / `create_gusset` 三条，在 pywin32 迟到绑定这条后端上
到不了「建成」** —— 除非换后端（`comtypes`，或进程内 C++）。
**⚠ 「换个参数试试」这条路已穷尽（20+ 种），不要再试。**

### 28.4 本会话在这个模块上**确证并修掉**的（另一个方向的进展）
* `create_one_bend` 的常量错：`swFmOneBend(33)` → `swFmSketchBend(35)`（事实 43）
* `create_gusset` 整步缺失的官方步骤 3（事实 44）
* `create_edge_flange` 的属性跨接口泄漏（`ReverseDirection`）
* 报告错层次**前推**（`CreateDefinition` → `CreateFeature`）

**⇒ 「到不了」与「一直没往前走」是两件事 —— 这几轮确实往前走了。**
