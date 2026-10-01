import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           521 🎯 **Spec Kit `091`：形位公差的 XML 路径 —— 官方 schema 拿到了（****片段式****），但 `SetSymbolXml` ****未打通******（轮 171）——
               动机：轮 166 判 `IGtolFrame.AddIndicator` **20 组全 False** ⇒ 本轮试**另一条**：
               `IGtolFrame.SetSymbolXml(String)`（其 Remarks 只要求「**2022 格式创建或转换过**」，
               而我们**确实 `ConvertFormat()` 过了**）。
            522 ★ **实测三件事**：
               ```
               ① `IGtolFrame.GetSymbolXml()`（新建+转换+加帧后的帧上）⇒ **空串**（长度 0）
                  ⇒ 「**先读出合法样本再改**」这条路**断了**
               ② ★★ `ISldWorks.GetGtolFrameXMLSchema()` ⇒ **有**，
                  返回 **14319 字节 / 342 行 / 61 个 `xs:element`**
                  （已存 `D:/AI/SW/output/gtol-frame-xml-schema.txt`）—— **官方产物**（缝合素材，不是发明）
               ③ `SetSymbolXml('<AnyCrossSection/>')` / `('<GtolFrame/>')` ⇒ **False**（最小 XML 不成）
               ```
            523 ★★★ **schema 的形状**解释了③**：声明 `xmlns:swGtolFrame="urn:swGtolFrame"`、
               `elementFormDefault="qualified"`，**且**61 个 element 里**没有任何「根元素」**
               ⇒ ★ 它是**片段（fragment）式** schema —— `SetSymbolXml` 收的是**帧内容的 XML 片段**，
                 **不是完整文档** ⇒ `<X/>` 这种**没有内容**的最小串**必然** False。
               ★ 另注：`PrimaryRangeSymbol` 有 `xs:pattern value="phi|sPhi|sqr"` ⇒ 值是**受控词表**。
            524 ★★ **按事实 53 停手** —— 这是这一处的**第 4 次**尝试：
               轮 120（AddFrame 顺序）· 轮 165（帧路径）· 轮 166（AddIndicator 20 组）· **轮 171（XML）**
               ⇒ ★ 只留下**素材与解释**：schema 文件（**将来构造 XML 的唯一正确起点**）+
                 「**片段式 + 受控词表**」这条结构性事实。
            525 ★★ **本轮的形状：收获是「素材 + 一个解释」，不是「打通」** ——
               ⚠ **XML 路径未打通**（完整片段未构造）· `geometric_tolerance` **仍为 `stitched`**。
               ★★★ 与事实 104/105/106 **同一族，但结论相反**：
               ```
               104 CreateChamfer：把「返回值拿不到」读成「接口到不了」 ⇒ **修正了**
               105 AddFrame     ：把「顺序不对」读成「帧取不到」       ⇒ **修正了**
               106 AddIndicator ：把「取值不在清单里」读成「到不了」   ⇒ **部分修正**
               111 本轮 XML     ：★ **这次没有草率下结论** —— 读了 schema，找到了**形状**上的解释，
                                  并明确记「**未打通**」，而**不是**说「XML 路径到不了」
               ⇒ ★★ 这是那条纪律**正面生效**的一次：**先解释，再决定要不要说「做不到」**。
               ```
               门禁 + `release_check` exit 0 · 回归 **1247 passed**。
               ⚑ **未查证**：⚠ XML 路径**未打通**（61 元素的完整片段未构造）；
                 ⚠ 「片段式」这个判断来自**读 schema**（无根元素 + `urn:` 命名空间 + `elementFormDefault`），
                 **不是**由一次成功调用证明的；⚠ 没试「**有内容**的片段 + 命名空间」
                 （`<PrimaryToleranceValue>0.05</PrimaryToleranceValue>`）—— 那是**第 5 次**，按事实 53 停手。
               下轮候选：① 回到在上下文链（轮 162 的 `SketchUseEdge3` 静默无效）；
               ② 换个域推进（`surface_modeling` / `mold_tools` 的 COM 侧可拆条目）；
               ③ 构造那份 61 元素的完整 XML 片段（**若愿意破例第 5 次**）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+521 ", before, re.M):
    print("  游标 521 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+525 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 525 行已存在 ✓")
