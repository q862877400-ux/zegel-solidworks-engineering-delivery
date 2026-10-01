# 091 · 形位公差 XML 路径：官方 schema 拿到了（**片段式**），但 `SetSymbolXml` 未打通

**Status**: Implemented（轮 171）· ⚠ **未打通**，只留下素材与解释 · `geometric_tolerance` 仍 `stitched`

## 一、动机
轮 166 判 `IGtolFrame.AddIndicator` **20 组全 False**（border×tol 穷尽）⇒ 本轮试**另一条**：
`IGtolFrame.SetSymbolXml(String)` —— 其 Remarks 只要求「**2022 格式创建或转换过**」，
而我们**确实 `ConvertFormat()` 过了**（轮 165）。

## 二、实测三件事
```
① `IGtolFrame.GetSymbolXml()`（新建+转换+加帧后的帧上）⇒ **空串**（长度 0）
   ⇒ 「**先读出合法样本再改**」这条路**断了**
② ★★ `ISldWorks.GetGtolFrameXMLSchema()` ⇒ **有**，返回 **14319 字节 / 342 行 / 61 个 `xs:element`**
   （已存 `D:/AI/SW/output/gtol-frame-xml-schema.txt`）—— **官方产物**（缝合素材，不是发明）
③ `SetSymbolXml('<AnyCrossSection/>')` / `('<GtolFrame/>')` ⇒ **False**（最小 XML 不成）
```

## 三、★★★ schema 的形状**解释了**为什么最小 XML 不成
```
`xmlns:swGtolFrame="urn:swGtolFrame"` · `elementFormDefault="qualified"`
★ 且 61 个 element 里**没有任何「根元素」**（被引用最多的为空）
⇒ ★ 它是**片段（fragment）式** schema —— `SetSymbolXml` 收的是**帧内容的 XML 片段**，
  **不是完整文档** ⇒ `<X/>` 这种**没有内容**的最小串**必然** False。
★ 另注：`PrimaryRangeSymbol` 有 `xs:pattern value="phi|sPhi|sqr"` ⇒ 值是**受控词表**。
```

## 四、★ 停手依据（事实 53）
```
这是这一处的**第 4 次**尝试：
  轮 120 顺序（AddFrame 先于 ConvertFormat）· 轮 165 帧路径 · 轮 166 AddIndicator 20 组 · 轮 171 XML
⇒ ★ 按事实 53（≥3 次即停）**在此停手**，只留下**素材与解释**：
  · schema 文件（**将来构造 XML 的唯一正确起点**）
  · 「片段式 + 受控词表」这条**结构性事实**
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-9101 | ★ 试**另一条**官方路径（`SetSymbolXml`），不是重复 `AddIndicator` |
| SC-9102 | ★★ 证伪：`GetSymbolXml()` 返回**空串** ⇒ 「先读再改」不可行（**如实报**）|
| SC-9103 | ★★★ 拿到**官方 schema**（14319 字节 / 61 元素）并**存盘** |
| SC-9104 | ★★★ **解释**了最小 XML 为何 False（**片段式**、无根元素）|
| SC-9105 | ★★ 按**事实 53 停手**，不继续穷举 XML 组合 |
| SC-9106 | 门禁 + 回归不退化 |

## ⚠ 明确记下的限度
* ⚠ **XML 路径未打通** —— 需按 schema 构造**完整片段**（61 元素、必需项与顺序），**本轮没做**；
* ⚠ `geometric_tolerance` **仍为 `stitched`**（`AddIndicator` 那半仍不通）；
* ⚠ schema 是**片段的**这个判断来自**读**（无根元素 + `urn:` 命名空间 + `elementFormDefault`），
  **不是**由一次成功的调用证明的；
* ⚠ 没试「给 `SetSymbolXml` 一份**有内容**的片段」（如 `<PrimaryToleranceValue>0.05</PrimaryToleranceValue>`
  加命名空间）—— 那是第 5 次尝试，按 53 停手。
