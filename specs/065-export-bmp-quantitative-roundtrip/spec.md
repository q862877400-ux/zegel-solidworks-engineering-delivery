# 065 · 补 `export_image` / `capture_screenshot` —— 用**定量往返**取证

**Status**: Implemented（轮 146）

## 一、挑它的理由（本轮**刻意收窄**）
```
本模块原有 step / stl / iges / parasolid / pdf / dxf，**没有图片** ⇒ 真缺口。
官方入口 `IModelDoc2.SaveBMP(String, Int32, Int32) -> Boolean`：
  · 签名**干净**（3 参、返回 `Boolean` ⇒ 成败可查）
  · ★★ **宽高是入参** ⇒ 可以**读回文件头**做**定量往返** —— 而"没抛异常"那种弱证据
    **空操作也能满足**（事实 40 那一族）。
⇒ 一个**小而强**的目标：正适合把前几轮过长的节奏收回来。
```

## 二、三源互证（铁律 4）
```
出厂反射 iface_sldworks.txt : Boolean SaveBMP(String, Int32, Int32)
swapi md                    : bool SaveBMP(string FileNameIn, int WidthIn, int HeightIn)
                              Returns: True if file is created successfully, false if not
                              Remarks: 必须**完整路径**且扩展名 `.bmp`；
                                       WidthIn/HeightIn ≤ 0 ⇒ 按**当前窗口尺寸**
官方示例链接                 : Save_Model_as_Bitmap_Example_CSharp / VBNET / VB
⇒ **一致，无冲突。**
```

## 三、★ 真机冒烟 **8/8**
```
✓ 造出 100x60x20 的板（有东西可拍）
✓ export_to_bmp(800x600) 未抛异常
✓ ★ 文件存在且非空                          1440054 字节
✓ ★★ **定量往返**：BMP 头里的尺寸 == 800x600   读回 (800, 600)（偏移 18/22，小端 int32）
✓ ★ 官方 Remarks：宽高 ≤ 0 ⇒ 按窗口尺寸       读回 (1460, 1049)
✓ ★ 扩展名不是 .bmp ⇒ 明确拒绝（ValueError）
✓ 收尾无残留模态框
```

## 四、★ 与既有 `sw_capture.py` 的**分工**（不是重造）
```
`scripts/sw_capture.py` : Windows GDI `PrintWindow` ⇒ 抓**窗口**、**不受遮挡**
                           （其来源块写明：`ImageGrab.grab(bbox)` 抓到的是遮挡物）
本轮的 `export_to_bmp`   : SolidWorks 自己的 `SaveBMP` ⇒ 抓**当前视图**、无需窗口在前台
⇒ ★ **两个都在，用途不同** ⇒ 符合"不重造已存在的基础设施"。
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-6101 | ★ 官方三源互证（反射 / swapi / 官方示例）|
| SC-6102 | ★★ 真机冒烟 **8/8**，含**定量往返**（写 800x600 ⇒ 读回头 == 800x600）|
| SC-6103 | ★ 官方 Remarks 两条都验了（完整路径 `.bmp` · ≤0 ⇒ 窗口尺寸）|
| SC-6104 | ★ 返回 `False` 要**抛**（官方：True 才是成功）|
| SC-6105 | ★ 与 `sw_capture` **分工**写进 docstring（不重造）|
| SC-6106 | 已知事实 86 入库；门禁 + 回归不退化（回归 **1214 passed**）|

## ⚠ 明确记下的限度
* 只证**尺寸按请求走 + 文件合法** ⇒ **不证画面内容**（不比对像素）；
* ⚠ **无头（headless）环境下 `SaveBMP` 是否可用，未测**；
* ⚠ 本轮**只加了一个图片函数**，`export_image` 那一档的**其它格式**（png/jpg）未做
  （官方 `SaveBMP` 只出 `.bmp`；别的格式要走 `SaveAs` 的图片过滤器，**未查**）。
