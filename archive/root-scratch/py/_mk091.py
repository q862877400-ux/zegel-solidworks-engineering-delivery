import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 111 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 111 | " + "".join([
    "**形位公差的 XML 路径：官方 schema 拿到了（**片段式**，无根元素），但 `SetSymbolXml` 未打通** —— ",
    "2026-10-01（轮 171）。轮 166 判 `IGtolFrame.AddIndicator` **20 组全 False**（border×tol 穷尽）⇒ ",
    "本轮试**另一条**：`IGtolFrame.SetSymbolXml(String)`（其 Remarks 只要求「2022 格式创建或转换过」，",
    "而我们**确实 `ConvertFormat()` 过了**）。",
    "★ 实测三件事：",
    "```",
    "① `IGtolFrame.GetSymbolXml()`（在**新建+转换过+加帧后**的帧上）⇒ 返回**空串**（长度 0）",
    "   ⇒ 「**先读出合法样本再改**」这条路**断了**",
    "② ★★ `ISldWorks.GetGtolFrameXMLSchema()` ⇒ **有**，返回 **14319 字节 / 342 行 / 61 个 `xs:element`**",
    "   （已存 `D:/AI/SW/output/gtol-frame-xml-schema.txt`）—— 这是**官方产物**（缝合素材，不是发明）",
    "③ `SetSymbolXml('<AnyCrossSection/>')` / `('<GtolFrame/>')` ⇒ **False**（最小 XML 不成）",
    "```",
    "★★★ **schema 的形状解释了③**：它声明 `xmlns:swGtolFrame=\"urn:swGtolFrame\"`、",
    "`elementFormDefault=\"qualified\"`，**且**61 个 element 里**没有任何「根元素」**",
    "⇒ ★ 它是**片段（fragment）式** schema —— `SetSymbolXml` 收的是**帧内容的 XML 片段**，**不是完整文档**",
    "⇒ 所以 `<X/>` 这种**没有内容**的最小串**必然** False。",
    "★ 另注：`PrimaryRangeSymbol` 有 `xs:pattern value=\"phi|sPhi|sqr\"` ⇒ 值是**受控词表**（不是自由文本）。",
    "⚠⚠ **仍未打通**：XML 路径需要**按 schema 构造出完整片段**（61 个元素、必需项与顺序），",
    "**本轮没做**；`geometric_tolerance` **仍为 `stitched`**。",
    "★ **本轮是这一处的第 4 次尝试**（轮 120 顺序 · 轮 165 帧路径 · 轮 166 AddIndicator 20 组 · 轮 171 XML）",
    "⇒ ★ 按**事实 53**（≥3 次即停）**在此停手**，只留下**素材与解释**（schema 文件 + 「片段式」这条）。",
    " | `tools/probe_gtol_symbol_xml.py` / `probe_gtol_xml_schema.py`；",
    "`D:/AI/SW/output/gtol-frame-xml-schema.txt`；`C:/swapi/types/IGtolFrame/SetSymbolXml.md`；事实 53 / 106 |",
])
if "| 111 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 111")
else:
    print("  已有 111")

# ── Spec Kit 091 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\091-gtol-xml-path")
S.mkdir(parents=True, exist_ok=True)
spec = """# 091 · 形位公差 XML 路径：官方 schema 拿到了（**片段式**），但 `SetSymbolXml` 未打通

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
"""
plan = """# 091 · Plan

## 步骤
1. 轮 166 判 `AddIndicator` 20 组全不成 ⇒ 试**另一条**：`SetSymbolXml`（Remarks 只要求 2022 格式）
2. ★ 先试「**读出**当前 XML 再改」⇒ `GetSymbolXml()` **空串** ⇒ 断开
3. ★★ 转向官方 schema：`ISldWorks.GetGtolFrameXMLSchema()` ⇒ **14319 字节** ⇒ 存盘
4. ★ 最小 XML 两个试探 ⇒ **False**
5. ★★★ **读 schema 的形状**解释原因：**片段式**（`urn:swGtolFrame`、无根元素、61 元素）
6. ★ 按**事实 53**（第 4 次）**停手** ⇒ 只留素材与解释
7. 事实 111 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 重复试同一条路 | ★ 本轮换的是**另一条**官方路径 |
| 最小试探失败就说"不通" | ★ **读 schema 找解释**（本轮找着了：片段式）|
| 一直穷举 XML 组合 | ★ **事实 53**：第 4 次即停 |
| 把"拿到 schema"说成"打通了" | ★ 结论里明写**未打通**，并列出**没做**的事 |
"""
tasks = """# 091 · Tasks（全部完成，轮 171）

- [x] T-9101 换另一条路径 `→ 验收:` `python tools/probe_gtol_symbol_xml.py`（`GetSymbolXml` **空串**，如实报）
- [x] T-9102 取官方 schema `→ 验收:` `python tools/probe_gtol_xml_schema.py`（**14319 字节 / 61 元素**）
- [x] T-9103 ★★★ 读 schema 形状 ⇒ 解释最小 XML 为何 False（**片段式**）
- [x] T-9104 事实 111
- [x] T-9105 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""
converge = """# 091 · Converge

**Converged**: 2026-10-01（轮 171）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-9101 换另一条路径 | ✅ |
| SC-9102 证伪 `GetSymbolXml` | ✅ 空串 |
| SC-9103 拿到官方 schema | ✅ 14319 字节 |
| SC-9104 解释最小 XML 为何 False | ✅ **片段式** |
| SC-9105 按 53 停手 | ✅ 第 4 次 |
| SC-9106 门禁 + 回归 | ✅ |

## 二、★★★ 本轮的形状：**收获是「素材 + 一个解释」，不是「打通」**
```
没打通：SetSymbolXml 仍 False（完整片段未构造）
但拿到：① 官方 schema 文件（将来构造 XML 的**唯一正确起点**）
        ② 「它是**片段式**、值域是**受控词表**」这条结构性事实
⇒ ★ 这解释了为什么最小 XML 必然 False —— **不是"接口不行"，是我给的东西形状不对**。
```

## 三、★ 与事实 104/105/106 **同一族，但结论相反**
```
104 CreateChamfer：把「返回值拿不到」读成「接口到不了」 ⇒ **修正了**
105 AddFrame     ：把「顺序不对」读成「帧取不到」       ⇒ **修正了**
106 AddIndicator ：把「取值不在清单里」读成「到不了」   ⇒ **部分修正**（清单校验 + 20 组穷尽）
111 本轮 XML     ：★ **这次没有草率下结论** —— 读了 schema，找到了**形状**上的解释，
                    并明确记「**未打通**」，而不是说「XML 路径到不了」。
⇒ ★★ 这是那条纪律**正面生效**的一次：**先解释，再决定要不要说"做不到"**。
```

## 四、未查证
* ⚠ XML 路径**未打通**（完整片段未构造）；
* ⚠ 「片段式」这个判断来自**读 schema**，**不是**一次成功调用证明的；
* ⚠ 没试「**有内容**的片段 + 命名空间」（第 5 次，按事实 53 停）；
* ⚠ `geometric_tolerance` 仍 `stitched`。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
