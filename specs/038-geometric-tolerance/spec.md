# 038 · 从「真缺」再补一条：形位公差 —— 但**换了入口**

**Status**: Implemented（轮 119）

## 一、背景
接着从「真缺」档补。本轮挑 **`gdt`**（形位公差）。

## 二、★★ 关键查证：**官方推荐的那条路在新版上无效**
```
官方 IModelDoc2.InsertGtol()          ⇒ **0 参**，返回空 GTol        ✓ 可用
官方 IGtol.SetFrameSymbols2(…9 参)    ⇒ ⚠ Remarks **原文**：
   「This method is valid only if this Gtol was created in a version of
     SOLIDWORKS **earlier than 2022**.」
   ⇒ 本机是 **SW 2026** ⇒ **那条路不可用**
   ⚠ 而且它的符号参数是 `LibraryName-SymbolName` 形态的**字形串**
     （官方文档里那些符号**显示为空**，是特殊字体的字形）⇒ **文本协议传不了**
```
★ 查到这里，最容易的收场是「**做不了，记为不做 + 原因**」（A1 允许）。
⚠ 但**再查一层**才发现有 2022 格式的路：
```
IGtolFrame.SetSymbolXml(String)          ⇒ 走 **XML**（官方有独立 Schema 文档）
IGtolFrame.AddIndicator(Int32, Int32, String)  ⇒ ★ **收枚举 + 字符串**
IGtolFrame.SetIndicator(Int32, Int32, Int32, String)
```
⇒ **本模块采用 `AddIndicator`** —— 两样参数都是**文本协议能传的**。

## 三、做法
1. `insert_gtol(model)` → `model.InsertGtol()`（**0 参**）
2. `add_gtol_indicator(gtol, *, tol_type, datum, border_type, frame)` →
   `IGtol.GetFrame(frame)`（**1 基**）→ `IGtolFrame.AddIndicator(border, tol, datum)`
3. **两条枚举**都取出厂反射并**逐值核对**：
   `swGtolIndicatorBorderType_e` = 0..3 · `swGtolGeomCharSymbol_e` = **19 项 / 12..30**

## 四、判据
| ID | 判据 |
|---|---|
| SC-3401 | ★★ **不走**那条「只对 2022 之前有效」的旧路径（测试断言**实现段**里不出现该**调用形态**）|
| SC-3402 | ★ 两条枚举逐值与出厂反射一致（**独立抄一份**在测试里）|
| SC-3403 | `swGtolGeomCharSymbol_e` **恰好 19 项**（多一个少一个都要查）|
| SC-3404 | `GetFrame` 的 `FrameIndex` 按官方 **1 基** |
| SC-3405 | `AddIndicator` 三参按官方顺序 `(BorderType, TolType, Datum)` |
| SC-3406 | 返回 `False` / 取不到帧 ⇒ **都抛带原因的错** |
| SC-3407 | 来源块写明 `stitched` 且**无本机运行证据** |
| SC-3408 | 门禁 + 回归不退化（回归 **1101 passed**）|

## 五、**本轮测试自己踩了两次**（都当场修）
```
① 用 t.split("# ── 来源")[0] 取"实现段" ⇒ **切在模块 docstring 里那一段**上
   ⇒ 取到的"实现"其实是文件头 ⇒ 断言必然失败（改用 rsplit）
② 断言"实现里不许出现 SetFrameSymbols2" ⇒ **被自己的说明文字误伤**
   （文档串里**必须**提到它来解释为什么不走它）
   ⇒ 改成查**调用形态**（带引号的成员名），而不是裸名字
```
★ 两条都是**判据写得太糙**，不是代码有问题。

## ⚠ 明确记下的限度
* **等级 `stitched`** —— 只有静态证据，**本机从未建过形位公差**；
* `AddIndicator` 的**失败原因**是**推断**的（官方只说 True/False）；
* 只覆盖**新建 + 加指示符**；`SetSymbolXml`（XML 路径）/ `SetIndicator` / `AddFrame` /
  `DeleteFrame` / 取回族**都未实现**；
* `InsertGtol` 的引线来自**调用前的选中**（官方 Remarks）—— 本模块**不代选**。
