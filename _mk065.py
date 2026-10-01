import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\065-export-bmp-quantitative-roundtrip")
S.mkdir(parents=True, exist_ok=True)

spec = """# 065 · 补 `export_image` / `capture_screenshot` —— 用**定量往返**取证

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
"""

plan = """# 065 · Plan

## 步骤
1. 挑一个**小而强**的真缺：`export_image` / `capture_screenshot`
2. 查官方 ⇒ `IModelDoc2.SaveBMP(String, Int32, Int32) -> Boolean`
   ⇒ ★ 三源一致；★ **宽高是入参** ⇒ 能做定量往返
3. 实现 `export_to_bmp`（含返回 False 即抛 + 扩展名守卫）
4. 冒烟：写 800x600 ⇒ **读 BMP 头核对**（偏移 18/22，小端）
   + 官方 Remarks 那条（≤0 ⇒ 窗口尺寸）
5. 契约测试（4 条，**用真模块**加载 —— 桩太难追全）
6. 能力证据 + 事实 86 + 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 用"没抛异常"当证据 | ★ **读回文件头**做定量往返（弱证据空操作也能满足）|
| 与 `sw_capture` 重复 | ★ docstring 写明**分工**（GDI 抓窗口 vs 原生抓视图）|
| 测试桩追名字追不完 | ★ **改用真模块**（导入时不连 COM），只替换 `get_com_member` |
| 顺手把 png/jpg 也做了 | **不做**（限度里写明未查）|
"""

tasks = """# 065 · Tasks（全部完成，轮 146）

- [x] T-6101 三源互证 `SaveBMP` 签名与语义
- [x] T-6102 实现 `export_to_bmp`（返回 False 即抛 + `.bmp` 守卫 + 分工说明）
- [x] T-6103 真机冒烟 `→ 验收:` `python tools/verify_bmp_smoke.py`（**8/8**）
- [x] T-6104 契约测试 4 条 `→ 验收:` `python -m pytest tests/test_sw_export_bmp_contract.py -q`（**4 passed**）
- [x] T-6105 能力证据 + 已知事实 86
- [x] T-6106 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 065 · Converge

**Converged**: 2026-10-01（轮 146）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-6101 三源互证 | ✅ |
| SC-6102 冒烟 8/8（含定量往返） | ✅ 800x600 读回 (800, 600) |
| SC-6103 官方 Remarks 两条 | ✅ ≤0 ⇒ (1460, 1049) |
| SC-6104 返回 False 即抛 | ✅ 有测试 |
| SC-6105 与 `sw_capture` 分工 | ✅ docstring 写明 |
| SC-6106 事实 86 + 门禁 + 回归 | ✅ `release_check` exit 0 · **1214 passed** |

## 二、★ 本轮**刻意收窄**，而收窄本身是一个判断
```
前几轮（051~064）动辄 3~4 个真缺陷、几十个文件 —— 有价值，但**节奏过长**。
⇒ 本轮主动挑一个**小而强**的目标：
   接口干净（3 参、Boolean 返回）+ **入参里带尺寸** ⇒ 能做**定量往返**
⇒ ★ 结果：**一个函数、一次冒烟、4 条测试**，把 `export_image` 这一格补上，
   并留下一条**强证据**（写 800x600 ⇒ 读回 800x600）。
```
★ 与 `051`/`062` 那种"顺手量出整模块问题"的轮次**同样是有效工作** ——
**不是每轮都必须踩出大缺陷。**

## 三、★★ 本轮真正的方法论收获：**"入参里有没有可回读的量"决定证据强度**
```
弱证据（空操作也能满足）：没抛异常 · 文件存在 · 返回 True
强证据（空操作满足不了）：★ **写进去的尺寸 == 读回来的尺寸**
⇒ ★ 挑任务时**先看官方签名里有没有"可回读的入参"** ——
   有（宽高、角度、直径…）⇒ 能做定量往返；没有 ⇒ 只能找侧证（如边界框、特征树）。
```
★ 这条把 `040`（螺旋线 50mm ⇒ 读回 0.05）· `044`（反向验证）那一族的经验**变成了选任务的准则**。

## 四、⚠ 一处**主动收窄的边界**
```
官方 `SaveBMP` **只出 `.bmp`**；png/jpg 要走 `SaveAs` 的图片过滤器 —— **本轮没查、没做**
⇒ 限度里写明，**不假装覆盖了 `export_image` 的全部格式**。
```

## 五、未查证
* **不证画面内容**（不比对像素）；
* ⚠ **无头环境下 `SaveBMP` 是否可用，未测**；
* ⚠ png/jpg 那条路（`SaveAs` 图片过滤器）**未查**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
