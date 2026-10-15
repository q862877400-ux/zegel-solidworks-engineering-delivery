import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\038-geometric-tolerance")
S.mkdir(parents=True, exist_ok=True)

spec = """# 038 · 从「真缺」再补一条：形位公差 —— 但**换了入口**

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
"""

plan = """# 038 · Plan

## 步骤
1. 查 `gdt` 的入口 ⇒ `IModelDoc2.InsertGtol()`（0 参）
2. ★ 查填充方法 ⇒ `SetFrameSymbols2` 的 Remarks 明写**只对 2022 之前的 Gtol 有效**
3. ★ **再查一层**（不急着收场）⇒ 找到 2022 格式的 `IGtolFrame.AddIndicator`
4. 取两条枚举（出厂反射）+ `GetFrame` 的 1 基约定
5. 写 `scripts/sw_gtol.py` + 契约测试（10 条）
6. ★ 测试自己踩两次（切分点 / 裸名字误伤）⇒ 当场修
7. 加能力条目（35 → **36**）+ 重生成 + 门禁 + 回归

## 风险与对策
| 风险 | 对策 |
|---|---|
| 查到旧路无效就收场 | ★ **再查一层**（2022 格式有 XML 与 indicator 两条路）|
| 用字形串参数 | ★ 选**收枚举**的那条（`AddIndicator`）|
| 枚举凭记忆写 | ★ 逐值查**出厂反射**，测试里**独立抄一份** |
| 判据切分点/误伤 | ★ 测试当场踩到并修（切分用 rsplit；查**调用形态**不查裸名字）|
"""

tasks = """# 038 · Tasks（全部完成，轮 119）

- [x] T-3401 查 `gdt` 入口 ⇒ `InsertGtol()`（0 参）
- [x] T-3402 ★ 查 `SetFrameSymbols2` ⇒ **只对 2022 之前的 Gtol 有效**
- [x] T-3403 ★ **再查一层** ⇒ 2022 格式走 `IGtolFrame.AddIndicator`
- [x] T-3404 取两条枚举 + `GetFrame` 的 1 基约定（出厂反射）
- [x] T-3405 写 `scripts/sw_gtol.py`
- [x] T-3406 契约测试（**10 passed**）
  `→ 验收:` `python -m pytest tests/test_sw_gtol_contract.py -q`
- [x] T-3407 加能力条目（35 → **36**）
- [x] T-3408 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 038 · Converge

**Converged**: 2026-10-01（轮 119）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-3401 不走旧路径 | ✅ 断言**实现段**里不出现该**调用形态** |
| SC-3402 两条枚举逐值一致 | ✅ 测试独立抄一份 |
| SC-3403 几何符号恰好 19 项 | ✅ |
| SC-3404 `FrameIndex` 1 基 | ✅ |
| SC-3405 三参按官方顺序 | ✅ `(BorderType, TolType, Datum)` |
| SC-3406 失败要抛 | ✅ 两种情况都测 |
| SC-3407 来源块写明 `stitched` | ✅ |
| SC-3408 门禁 + 回归 | ✅ `release_check` exit 0 · **1101 passed** |

**能力分布**：**36 条**（新增 1）· `verified 29` · `stitched 6`

## 二、★ 本轮最要紧的一步是「**查到旧路无效之后，再查一层**」
```
第一层：SetFrameSymbols2  ⇒ 官方明写**只对 2022 之前的 Gtol 有效** ⇒ 此路不通
        ⇒ **最容易的收场是记「不做 + 原因」**（A1 允许，也不算错）
第二层：**再查一层** ⇒ 2022 格式有两条路：
        · SetSymbolXml（XML，有独立 Schema 文档）
        · **AddIndicator（收枚举 + 字符串）** ← ★ 采用
```
★ **"官方推荐的那条路不通" ≠ "这件事做不了"** ——
但**也不能反过来假设总有路**：如果再查一层还是不通，正确收场就是**记为不做 + 原因**。

## 三、★ 两条判据的糙法（本轮当场踩到并修）
```
① 取"实现段"用 split("# ── 来源")[0]  ⇒ 切在 **docstring 里那一段**上（文件里该标记出现两次）
   修：改用 rsplit（取最后一段）
② 断言"实现里不许出现 SetFrameSymbols2" ⇒ **被自己的说明文字误伤**
   （文档串里**必须**提到它，才能解释为什么不走它）
   修：查**调用形态**（带引号的成员名），不查裸名字
```
★ 两条都是**判据写得太糙**，**不是代码有问题** ——
而**如果不修就"改代码去迎合判据"，那才是真的坏**。

## 四、「真缺」档补录进度
```
023 螺旋线 · 024 草图倒角/镜像 · 028 方程式 · 034 转换实体引用 · 038 形位公差
⇒ 共补 **5 条**（其中 `034` 并入已有模块，不新开文件）
⚠ 该档约 **132 条**（`022` 抽样估），**剩余仍很多**
```

## 五、未查证
* **本机从未建过形位公差**（等级 `stitched`）；
* `AddIndicator` 的**失败原因是推断的**（官方只说 True/False）；
* `SetSymbolXml` 的 **XML Schema 未读**（本模块选了另一条路）；
* `SetIndicator` / `AddFrame` / `DeleteFrame` / 取回族**都未实现**；
* `InsertGtol` 的引线来自调用前的选中 —— **未处理**（不代选）。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
