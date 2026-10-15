import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\076-export-magic-matrix")
S.mkdir(parents=True, exist_ok=True)

spec = """# 076 · 导出格式矩阵 —— 逐格式**读文件头**

**Status**: Implemented（轮 157）

## 一、动机
`075`（轮 156）用**读魔数**证明了 `.dwg` 是真 DWG。
⇒ ★ 那个手法**可以一次覆盖全部格式** ⇒ 本轮做成一张**矩阵**。

## 二、★★ 结果：**9/10 名实相符**
```
step      'ISO-10303-21;\\r\\nHEADER;\\r'      ⇒ STEP ✓
stl       'stlbn probe             '           ⇒ **二进制 STL**（80 字节 header）✓
iges      'SolidWorks IGES file usi'           ⇒ IGES ✓
parasolid '**ABCDEFGHIJKLMNOPQRSTUV'           ⇒ Parasolid 文本 ✓
dxf       '  0\\r\\nSECTION\\r\\n  2\\r'          ⇒ DXF ✓
dwg       'AC1015\\x00…'                        ⇒ DWG ✓
png       '\\x89PNG\\r\\n\\x1a\\n'                ⇒ PNG ✓
jpg       '\\xff\\xd8\\xff\\xe0\\x00\\x10JFIF'      ⇒ JPEG ✓
bmp       'BM6\\x10\\x0e…'                      ⇒ BMP ✓
pdf       ✗ AttributeError: <unknown>.GetSldWorksObject
```

## 三、⚠ **`pdf` 在零件上失败** —— 但措辞要准
```
`export_to_pdf(model, output_path, sheet_names=None)` —— 签名里有 `sheet_names`
⇒ 语义上**是工程图的入口** ⇒ ⚠ **本轮没做工程图 ⇒ 未查明**
★ 注意措辞：**不是「功能不行」，是「我用的对象不对」**（与事实 95 同一纪律）
```

## 四、★★★ 本轮的**第二个收获**：我的分类器判反了两处
```
第一版 `classify()` 里「IGES 只认首字节 `S`/`s`」**排在**「ASCII STL 以 `solid` 开头」**之前**
⇒ **顺序 bug** ⇒ 把 `.iges`（`SolidWorks IGES file…`，恰以大写 `S` 开头）判成 `STL(ascii)`
⇒ ★ 改成**把文件头原文打出来**、用证据判之后，真相自明
```
⇒ ★ 与事实 91/93/94 与轮 152/153/154 **同一纪律** —— **这是第 4 次**
「**我的观测**本身要先被验」。

## 五、判据
| ID | 判据 |
|---|---|
| SC-7201 | ★★ 逐格式**读文件头**（不是"文件存在"/"没抛异常"）|
| SC-7202 | ★★ 矩阵 **9/10 名实相符** |
| SC-7203 | ★★ 查出 **`pdf` 在零件上失败**，并**准确措辞**（对象不对，不是功能不行）|
| SC-7204 | ★★★ **查出我自己的分类器判反了两处**（顺序 bug）|
| SC-7205 | ★ 改成**读头原文**，不让易错的分类器挡住真相 |
| SC-7206 | 事实 97 入库；门禁 + 回归不退化（回归 **1232 passed**）|

## ⚠ 明确记下的限度
* ⚠ **`pdf` 在工程图上能不能出，未查明**（本轮没做工程图）；
* ⚠ 只在一个**钣金件**上测（别种文档没测）；
* ⚠ 只验**文件头**（证"是那个格式"），**不证"内容完好"**；
* ⚠ 分类器仍在文件里（已改为**只做参考**，真相以 `head_ascii` 为准）。
"""

plan = """# 076 · Plan

## 步骤
1. `075` 的读魔数手法 ⇒ 做成**全格式矩阵**
2. 造一个钣金 scratch 件（DXF/DWG 需要「钣金件 + 已保存」）⇒ 逐个格式导出
3. ★ 第一版只打 `classify()` 的判定 ⇒ **STL/IGES 两处被判反**
4. ★★ 改成**把文件头原文打出来** ⇒ 真相自明（`SolidWorks IGES file…` / `stlbn`）
5. ⇒ **9/10 名实相符**；**`pdf` 在零件上失败**（`AttributeError`）
6. ⇒ `pdf` **准确措辞**（对象不对，不是功能不行）
7. 事实 97 + 能力证据 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 靠一个易错的分类器下结论 | ★ **打出文件头原文**，用证据判 |
| 把 `pdf` 失败说成「功能不行」 | ★ **准确措辞**（对象不对）；限度里写「未查明」 |
| 只测一种格式就 generalization | ★ 一次覆盖 **10 个**格式 |
| 只验文件头就说过关 | ★ 限度里写明**不证内容完好** |
"""

tasks = """# 076 · Tasks（全部完成，轮 157）

- [x] T-7201 钣金 scratch 件 + 逐格式导出
  `→ 验收:` `python tools/probe_export_magic_matrix.py`（末行打印"扫了 N 个窗口 · 无模态框"）
- [x] T-7202 ★★ 读文件头 ⇒ **9/10 名实相符**
- [x] T-7203 ★★ 查出 `pdf` 在零件上失败（**准确措辞**）
- [x] T-7204 ★★★ 查出我的分类器顺序 bug ⇒ 改成读头原文
- [x] T-7205 事实 97 + 能力证据
- [x] T-7206 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 076 · Converge

**Converged**: 2026-10-01（轮 157）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-7201 逐格式读文件头 | ✅ |
| SC-7202 9/10 名实相符 | ✅ |
| SC-7203 `pdf` 失败 + 准确措辞 | ✅ |
| SC-7204 查出我的分类器错 | ✅ 顺序 bug |
| SC-7205 改成读头原文 | ✅ |
| SC-7206 事实 97 + 门禁 + 回归 | ✅ `release_check` exit 0 · **1232 passed** |

## 二、★★★ 「我的观测本身要先被验」—— 这是**第 4 次**
```
轮 152：FeatureByPositionReverse **滞后一格**       ⇒ 我的数法错
轮 153/154：SelectByID2 的 bool 不可信              ⇒ 我的判法错
轮 157：classify() 的**顺序 bug**                   ⇒ 我的**分类器**错
⇒ ★★ 有趣的是：**这次错在"我为了验证而写的那个工具"里** ——
  「**验证工具自身也需要被验证**」。
```

## 三、★ 一个正面的、可复用的产物
```
一张**导出格式矩阵**（10 个格式 × 文件头签名）⇒ 以后任何"导出对不对"的问题
都能拿它**一句话对照**，不必再逐个查规范。
★ 而且它是**读头取证**得来的，不是抄规范得来的。
```

## 四、未查证
* ⚠ **`pdf` 在工程图上能不能出，未查明**（本轮没做工程图）；
* ⚠ 只在一个**钣金件**上测；
* ⚠ 只验**文件头**，不证**内容完好**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
