# 085 · 「帧取不到」是**顺序问题** —— `ConvertFormat()` 必须先于 `AddFrame()`

**Status**: Implemented（轮 165）· ⚠ `geometric_tolerance` 仍为 `stitched`（3/5）

## 一、线索来源（顺 `0x80010105` 回查）
轮 164 更正了 `CreateChamfer` 的误判后，我顺那条线索回查「**还有哪些能力是被『只看异常』误判的**」。
★ 我写了一个扫描（按「附近有没有回读字样」判）⇒ **73 处命中，大多假阳性**
（门禁自己的措辞 / 参数校验 / 官方 Remarks 引文）⇒ ★ **判据又是"邻近文本"式，弃用**。

⇒ 但里面有一条值得动手：`sw_gtol.py` 的「**我们在 SW 2026，那条路不可用**」——
★ 而 `geometric_tolerance` 正是 5 条 `stitched` 之一（3/5）。

## 二、★ 先核实：那条断言**不是**「只看异常」
```
它的依据是**官方 Remarks 原文**：
  IGtol.SetFrameSymbols2 > "valid only if this Gtol was created in a version of
                            SOLIDWORKS earlier than 2022."
⇒ 这是**读文档**读出来的 ✓；而「到不了」那半也**回读了状态**：
  GetFrameCount 1 →（ConvertFormat 成功后）0 · GetFrame(0/1/2) 全 None
⇒ ★ **所以这条本来就不是误判** —— 我的扫描判据误报了它（已如实记）。
```

## 三、★★★ 但**它自己列的「未查证」里藏着真因**
```
轮 120 写的顺序是：AddFrame()（False）→ ConvertFormat()（成功）→ GetFrame(1)/(2)（None）
★ 读官方 `IGtol.AddFrame` 的 Remarks（`C:/swapi/types/IGtol/AddFrame.md`）**原文**：
  > This method is valid only if this Gtol was created in SOLIDWORKS **2022 or later**.
⇒ 新建的 Gtol **默认是旧格式** ⇒ `AddFrame()` 在**转换前**调用**必然 False**
⇒ ★★★ **正确顺序**：**先 `ConvertFormat()` → 再 `AddFrame()` → 再 `GetFrame(n)`**
```

## 四、★★ 实测（`tools/probe_gtol_frame_order.py`）
```
新建后 AddFrame()【旧顺序】   ⇒ **False**
ConvertFormat()              ⇒ 0（成功）
★★ AddFrame()【转换之后】     ⇒ **True**        ← ★★★ 旧顺序下是 False
   加帧后 GetFrameCount      ⇒ **2**
★★ GetFrame(0..3)            ⇒ ['None', '有', '有', 'None']  ← ★★ **拿到对象了**
★★★ AddIndicator(0,0,'A')    ⇒ **False**        ← ⚠ 这一层仍未通
```

## 五、★ 修法与更正
```
修：`ensure_gtol_frame` 改为**先 ConvertFormat() 再 AddFrame()**
正：改掉两句**已过时**的报错
    · `GetFrame` 那句不再说「该 Gtol 可能不是 2022 格式」（⚠ 走了那个分支就已转换过）
    · `AddIndicator` 那句不再说「不是 2022 格式」⇒ 改成「**帧已拿到 ⇒ 参数/前置未查明**」
```

## 六、判据
| ID | 判据 |
|---|---|
| SC-8501 | ★ 核实原断言**不是**「只看异常」（有官方 Remarks + 回读状态）⇒ 我的扫描**误报**了它 |
| SC-8502 | ★★★ **从它自己写的「未查证」里读出真因**（`AddFrame` 的 Remarks）|
| SC-8503 | ★★★ **顺序更正**：`ConvertFormat()` → `AddFrame()` ⇒ **`AddFrame()` True**、`GetFrame` **拿到对象** |
| SC-8504 | ★ 修 `ensure_gtol_frame` + 改两句已过时的报错 |
| SC-8505 | ★ 事实 105；条目更正（「帧取不到」→「**帧路径已通**，指示符未查明」）|
| SC-8506 | 门禁 + 回归不退化（回归 **1246 passed**）|

## ⚠ 明确记下的限度
* ⚠ **`IGtolFrame.AddIndicator(Int32, Int32, String)` 仍返回 `False`** ⇒ **参数/前置未查明**
  （★ 但**不再**是「帧取不到」）；
* ⚠ `geometric_tolerance` **仍为 `stitched`**（3/5）—— **没有**升 `verified`；
* ⚠ 本轮**没有**试 `SetSymbolXml`（XML 路径）；
* ⚠ 我那个「按邻近文本扫误判」的判据**已弃用**，**没有**接进任何门禁。
