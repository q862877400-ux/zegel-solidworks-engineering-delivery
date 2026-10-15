import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           451 🎯 **Spec Kit `076`：导出格式矩阵 —— 逐格式****读文件头******（轮 157）——
               `075` 用读魔数证明 `.dwg` 是真 DWG ⇒ ★ 那个手法**可以一次覆盖全部格式**。
            452 ★★ **结果：9/10 名实相符**（读头取证，不是抄规范）：
               ```
               step      'ISO-10303-21;\\r\\nHEADER;\\r'   ⇒ STEP ✓
               stl       'stlbn probe             '        ⇒ **二进制 STL** ✓
               iges      'SolidWorks IGES file usi'        ⇒ IGES ✓
               parasolid '**ABCDEFGHIJKLMNOPQRSTUV'        ⇒ Parasolid 文本 ✓
               dxf       '  0\\r\\nSECTION\\r\\n  2\\r'       ⇒ DXF ✓
               dwg       'AC1015\\x00…'                     ⇒ DWG ✓
               png / jpg / bmp                             ⇒ PNG / JPEG / BMP ✓
               pdf       ✗ AttributeError: <unknown>.GetSldWorksObject
               ```
            453 ⚠ **`pdf` 在零件上失败 —— 但措辞要准**：`export_to_pdf(model, path, sheet_names=None)`
               的签名里有 `sheet_names` ⇒ 语义上**是工程图的入口** ⇒ ⚠ **本轮没做工程图 ⇒ 未查明**。
               ★ **不是「功能不行」，是「我用的对象不对」**（与事实 95 同一纪律）。
            454 ★★★ **本轮的第二个收获：我的分类器判反了两处**：
               ```
               第一版 `classify()` 里「IGES 只认首字节 S/s」**排在**「ASCII STL 以 solid 开头」**之前**
               ⇒ **顺序 bug** ⇒ 把 .iges（`SolidWorks IGES file…`，恰以大写 S 开头）判成 STL(ascii)
               ⇒ ★ 改成**把文件头原文打出来**、用证据判之后，真相自明
               ```
               ⇒ ★★ **「我的观测本身要先被验」—— 这是第 4 次**（152 数法 / 153+154 判法 / 157 **分类器**）；
                 ★ 而这次错在**我为了验证而写的那个工具**里 ⇒
                 **「验证工具自身也需要被验证」。**
               ⚑ **未查证**：⚠ **`pdf` 在工程图上能不能出，未查明**；⚠ 只在**钣金件**上测；
                 ⚠ 只验**文件头**（证"是那个格式"），**不证"内容完好"**。
               已知事实 **97** 入库 · 回归 **1232 passed** · `release_check` exit 0。
               下轮候选：① **做一个工程图**，把 `pdf` 那条补上（这是本轮唯一没验的格式）；
               ② 回到「真缺」继续补；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+451 ", before, re.M):
    print("  游标 451 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+454 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 454 行已存在 ✓")
