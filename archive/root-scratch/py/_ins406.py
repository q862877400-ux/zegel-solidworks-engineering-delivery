import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           406 🎯 **Spec Kit `066`：收掉上轮标的边界 —— `SaveAs3` 出 PNG / JPG**（轮 147）——
               `065` 把「png/jpg 要走 `SaveAs` 的图片过滤器」写进限度（**未做**）⇒ 本轮**收掉**。
               ★ 官方是**三级废弃链**：`SaveAs` ⇒（Superseded）⇒ `SaveAs2` ⇒（Superseded）⇒ **`SaveAs3`**。
            407 ★★★ **真机上踩了两个坑**：
               ```
               ① 反射里**两个重载**：
                    Int32   SaveAs3(String, Int32, Int32)
                    Boolean SaveAs3(String, Int32, Int32, Object, Object, Int32&, Int32&)
                  ★ 按 **3 参**调 ⇒ 报 `0x8002000F`（`DISP_E_PARAMNOTOPTIONAL`）
                    ⇒ **实际解析到的是 7 参那个** ⇒ 必须 7 参 + `out_i4()` 给出参占位
                    ⇒ ★ 返回也随之从 `Int32` 变成 **`Boolean`**
               ② `ExportData` / `AdvancedSaveAsOptions` 传 `None` ⇒ 报 **`类型不匹配`**（位置 4）
                  ⇒ 必须 `create_empty_dispatch_variant()`（事实 12 / 33 那一族）
               ⇒ ★ **静态反射把两个重载都列出来了 —— 但"pywin32 挑哪个"只有真机才知道。**
                 与事实 84（"取"成员会"调"它）**同族**：都是「**调用形态的坑**」。
               ```
            408 ★ **真机冒烟 9/9**：PNG **129437 字节**（魔数 `89 50 4E 47…` + `IHDR` 尺寸
               **1232x1049**）· JPG **54431 字节**（魔数 `FF D8 FF`）· 扩展名守卫 ⇒ ValueError。
            409 ★★ **一处我自己的判据错，处理方式本轮做对了**：
               ```
               交叉核对写「PNG 尺寸 ≈ 窗口尺寸」⇒ **红了**（BMP(0,0)=(1460,1049) vs PNG=(1232,1049)，
                 高度一致、宽度差 228）
               ⇒ ★ 两条路：① 改预期去迁就  ② **先查清是不是我假设错**
               ⇒ 选 ② ⇒ 最可能是「窗口 vs 绘图区」⇒ ⚠ **但我没验证**
               ⇒ **如实写「未查明」**（事实 82/142 的教训：不把没验证的假设写成判据）
               ```
               ★ 这是**主动放弃一个"看起来能过"的判据** —— 与 `064` 撤掉那条零参判据**同一路数**。
            410 ★ **与 `065` 的衔接**：`065` 把 png/jpg 写进**限度**（未做）⇒ `066` 照着它做 ⇒
               ★ **限度不是终点，它是一份待办清单**；下一轮照着做，就成了闭环。
               ⚑ **未查证**：⚠ **未查明** `SaveBMP(0,0)` 与 `SaveAs3` 的宽度差（1460 vs 1232）；
                 只证格式与尺寸，**不证画面内容**；⚠ **图片尺寸不可指定**（`SaveAs3` 无尺寸入参）。
               已知事实 **87** 入库 · 回归 **1220 passed** · `release_check` exit 0。
               下轮候选：① 查 `SaveBMP` 与 `SaveAs3` 的宽度差（窗口 vs 绘图区）到底是不是那个原因；
               ② 回到「真缺」继续补；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+406 ", before, re.M):
    print("  游标 406 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+410 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 410 行已存在 ✓")
