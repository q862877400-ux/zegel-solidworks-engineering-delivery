# 076 · 导出格式矩阵 —— 逐格式**读文件头**

**Status**: Implemented（轮 157）

## 一、动机
`075`（轮 156）用**读魔数**证明了 `.dwg` 是真 DWG。
⇒ ★ 那个手法**可以一次覆盖全部格式** ⇒ 本轮做成一张**矩阵**。

## 二、★★ 结果：**9/10 名实相符**
```
step      'ISO-10303-21;\r\nHEADER;\r'      ⇒ STEP ✓
stl       'stlbn probe             '           ⇒ **二进制 STL**（80 字节 header）✓
iges      'SolidWorks IGES file usi'           ⇒ IGES ✓
parasolid '**ABCDEFGHIJKLMNOPQRSTUV'           ⇒ Parasolid 文本 ✓
dxf       '  0\r\nSECTION\r\n  2\r'          ⇒ DXF ✓
dwg       'AC1015\x00…'                        ⇒ DWG ✓
png       '\x89PNG\r\n\x1a\n'                ⇒ PNG ✓
jpg       '\xff\xd8\xff\xe0\x00\x10JFIF'      ⇒ JPEG ✓
bmp       'BM6\x10\x0e…'                      ⇒ BMP ✓
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
