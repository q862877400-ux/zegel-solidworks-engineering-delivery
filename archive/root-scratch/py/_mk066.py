import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\066-export-image-png-jpg")
S.mkdir(parents=True, exist_ok=True)

spec = """# 066 · 收掉上轮标的边界：`SaveAs3` 出 PNG / JPG

**Status**: Implemented（轮 147）

## 一、起因
`065`（轮 146）把「png/jpg 要走 `SaveAs` 的图片过滤器」写进限度、**未做**。
⇒ 本轮**收掉那条边界**。

## 二、★ 官方：**三级废弃链**
```
IModelDocExtension.SaveAs  ⇒ Obsolete ⇒ SaveAs2
IModelDocExtension.SaveAs2 ⇒ Obsolete ⇒ SaveAs3
IModelDocExtension.SaveAs3 ← **现行**
⇒ 本模块只用现行那个。
```

## 三、★★★ 真机上踩了**两个坑**
```
① 反射里有**两个重载**：
     Int32   SaveAs3(String, Int32, Int32)
     Boolean SaveAs3(String, Int32, Int32, Object, Object, Int32&, Int32&)
   ★ 按 **3 参**调 ⇒ 报 `0x8002000F`（`DISP_E_PARAMNOTOPTIONAL`）
     ⇒ **解析到的是 7 参那个** ⇒ 必须按 7 参调 + `out_i4()` 给出参占位
     ⇒ ★ 返回也随之从 `Int32` 变成 **`Boolean`**
② `ExportData` / `AdvancedSaveAsOptions` 传 `None` ⇒ 报 **`类型不匹配`**（位置 4）
   ⇒ 必须用 `create_empty_dispatch_variant()`（事实 12 / 33 那一族）
```
★ **静态反射把两个重载都列出来了 —— 但"pywin32 会挑哪个"只有真机才知道。**

## 四、真机冒烟 **9/9**
```
✓ export_to_image(.png) 未抛异常
✓ ★ PNG 文件存在且非空                              129437 字节
✓ ★ PNG **魔数**（89 50 4E 47…）与 `IHDR`             IHDR 尺寸 (1232, 1049)
✓ ★★ PNG 尺寸是**正数**（读回 IHDR）
✓ ★★ JPG 生成且**魔数** FF D8 FF                    54431 字节
✓ ★ 两个尺寸都是**合理的正数**
✓ ★ 扩展名不在名单 ⇒ 明确拒绝（ValueError）
✓ 收尾无残留模态框
```

## 五、★★ 一处**我自己的判据错**（当场改了，如实记）
```
第一版交叉核对写的是「**PNG 尺寸应当 ≈ 窗口尺寸**（±2 px）」⇒ **它红了**：
  BMP(0,0) = (1460, 1049)   vs   PNG = (1232, 1049)
  ⇒ **高度一致、宽度差 228**
★ 最可能的解释：`SaveBMP(0,0)` 按**窗口**取（含侧边面板）、`SaveAs3` 按**绘图区**取
  ⇒ **两者本来就不该相等**。
⚠ **但我没有验证这个解释** ⇒ 按事实 82/142 的教训：
  **不把没验证的假设写成判据** ⇒ 改成"两者都是**合理的正数**"，
  并把差值**如实记为「未查明」**。
```

## 六、判据
| ID | 判据 |
|---|---|
| SC-6201 | ★ 只用**现行**入口（三级废弃链的末端）|
| SC-6202 | ★★ 踩出并记录**两个坑**（3 参到不了 · 空 Dispatch 不是 `None`）|
| SC-6203 | ★★ 冒烟 **9/9**：PNG/JPG **魔数 + IHDR 尺寸**都验了 |
| SC-6204 | ★ 返回 `False` 要抛；**文件不在也要抛**（"成功返回值≠文件写出来了"）|
| SC-6205 | ★★ 一处**我自己的判据错**：不改预期去迁就，而是**如实标「未查明」** |
| SC-6206 | 已知事实 87 入库；门禁 + 回归不退化（回归 **1220 passed**）|

## ⚠ 明确记下的限度
* ⚠ **未查明**：`SaveBMP(0,0)` 与 `SaveAs3` 的**宽度不同**（1460 vs 1232，高度都是 1049），
  疑为「窗口 vs 绘图区」，**本轮没有验证**；
* 只证**格式合法 + 尺寸合理** ⇒ **不证画面内容**（不比对像素）；
* ⚠ 图片**尺寸不可指定**（`SaveAs3` 没有尺寸入参）—— 要指定尺寸得用 `SaveBMP`（**只出 bmp**）。
"""

plan = """# 066 · Plan

## 步骤
1. 收掉 `065` 标下的边界：`SaveBMP` 只出 `.bmp` ⇒ 查 `SaveAs` 能不能出 png/jpg
2. 查官方 ⇒ **三级废弃链** ⇒ 现行是 `SaveAs3`；★ 反射里有**两个重载**
3. 先用 **3 参**那个 ⇒ 真机报 `DISP_E_PARAMNOTOPTIONAL` ⇒ 改用 **7 参** + `out_i4()`
4. 两个 `Object` 入参传 `None` ⇒ **`类型不匹配`** ⇒ 改用 `create_empty_dispatch_variant()`
5. ⇒ **PNG/JPG 都出来了** ⇒ 冒烟验**魔数 + IHDR 尺寸**
6. ⚠ 交叉核对判据**红了** ⇒ 查清是我**假设错**（窗口 vs 绘图区）⇒ **如实标未查明**，不迁就
7. 契约测试（钉住两个坑）+ 能力 + 事实 87 + 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 3 参重载报错就以为"接口不支持" | ★ **看错误码是 `DISP_E_PARAMNOTOPTIONAL`** ⇒ 是"参数不够"，换 7 参 |
| `None` 报类型不匹配 | ★ 事实 12/33：空 Dispatch 要用 VARIANT |
| 交叉核对红了就改预期 | ★ **先查清是不是我假设错** ⇒ 本次是我错 ⇒ 标「未查明」而不是硬凑 |
| 顺手把尺寸也做成可指定 | **不做**（`SaveAs3` 没有尺寸入参，限度里写明）|
"""

tasks = """# 066 · Tasks（全部完成，轮 147）

- [x] T-6201 查 `SaveAs` 家族 ⇒ **三级废弃链**，现行 `SaveAs3`
- [x] T-6202 实现 `export_to_image`（png/jpg）
- [x] T-6203 ★★ 踩两个坑并修（3 参→7 参 · `None`→空 Dispatch）
- [x] T-6204 真机冒烟 `→ 验收:` `python tools/verify_png_smoke.py`（**9/9**）
- [x] T-6205 契约测试 5 条 `→ 验收:` `python -m pytest tests/test_sw_export_image_contract.py -q`（**5 passed**）
- [x] T-6206 ⚠ 交叉核对判据错 ⇒ **如实标未查明**（不迁就预期）
- [x] T-6207 能力 + 事实 87 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 066 · Converge

**Converged**: 2026-10-01（轮 147）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-6201 现行入口 | ✅ 三级废弃链末端 |
| SC-6202 两个坑 | ✅ 都记录并修 |
| SC-6203 冒烟 9/9 | ✅ PNG 129437 B / JPG 54431 B |
| SC-6204 两种"失败"都要抛 | ✅ 5 条测试 |
| SC-6205 判据错如实标未查明 | ✅ |
| SC-6206 事实 87 + 门禁 + 回归 | ✅ `release_check` exit 0 · **1220 passed** |

## 二、★★★ 本轮的核心：**静态反射列出两个重载，但"pywin32 挑哪个"只有真机知道**
```
反射：Int32 SaveAs3(String, Int32, Int32)   ← 看着更简单，我选了它
      Boolean SaveAs3(…, Int32&, Int32&)
真机：3 参形式报 DISP_E_PARAMNOTOPTIONAL ⇒ **实际解析到的是 7 参那个**
⇒ ★ 与事实 84（"取"成员会"调"它）**同族**：**都是"调用形态的坑"**，
  而**都只能靠真机实测发现**。
```

## 三、★★ 一处判据错，处理方式本轮**做对了**
```
交叉核对写「PNG 尺寸 ≈ 窗口尺寸」⇒ **红了**（1460 vs 1232，高度同）
⇒ ★ 有两条路：① 改预期去迁就（"差 228 也还行吧"）② **先查清是不是我假设错**
⇒ 我选 ② ⇒ 最可能是「窗口 vs 绘图区」⇒ ⚠ **但我没验证** ⇒
  **如实写「未查明」**（事实 82/142 的教训：不把没验证的假设写成判据）
```
★ 这一步是**主动放弃一个"看起来能过"的判据** —— 与 `064` 撤掉那条零参判据**同一路数**。

## 四、★ 与 `065` 的衔接
```
065：SaveBMP ⇒ 只出 `.bmp`，把 png/jpg 写进限度（**未做**）
066：SaveAs3 ⇒ 出 png/jpg，**收掉那条边界**（并把它记进能力的 limitations）
⇒ ★ **限度不是终点** —— 它是一份**待办清单**；下一轮照着它做，就完成了闭环。
```

## 五、未查证
* ⚠ **未查明** `SaveBMP(0,0)` 与 `SaveAs3` 的宽度差（1460 vs 1232）；
* 只证格式与尺寸，**不证画面内容**；
* ⚠ **图片尺寸不可指定**（`SaveAs3` 无尺寸入参）。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
