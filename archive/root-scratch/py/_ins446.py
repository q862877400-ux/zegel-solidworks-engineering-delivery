import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           446 🎯 **Spec Kit `075`：`.dwg` 到底是不是 DWG —— ****读魔数****取证（一个****正面****结论）**（轮 156）——
               `074` 已按事实 53 强停止 ⇒ 本轮**换题**：挑一个**不依赖 `mark`**、**可读魔数**的。
               动机：`scripts/sw_export.py` 的 `export_to_dxf` docstring 写着「导出为 **DXF/DWG** 格式」，
               而 `_export_for_format` 把 **`.dwg` 与 `.dxf` 路由到同一个函数** ⇒ 那 `.dwg` 真出 DWG 吗？
            447 ★★ **结果：名实相符（正面）** —— 读魔数：
               ```
               `.dxf` ⇒ 20208 字节 · 头部 `  0\\r\\nSECTI` ⇒ **DXF 文本** ✓
               `.dwg` ⇒ 272032 字节 · 头部 **`AC1015`**    ⇒ **真 DWG** ✓
               ```
            448 ★ **一个可复用的观察**：**`AC1015` = AutoCAD 2000 / R2000** —— **不是最新版**；
               ⚠ 若下游要求更新的 DWG，**本轮没查到通过 API 指定版本的入口**
               （`SaveAs3` 无此参数，疑为用户首选项级别 ⇒ **未验证**）。
            449 ★ **前置条件（实测，且**错误信息清晰**）**：零件路径要求
               **「钣金件 + 必须先保存」** —— 普通拉伸件报
               `ValueError: 导出展开 DXF 前必须先保存钣金零件` ⇒ ★ 这个错误**指向明确、可操作**，
               与事实 55 那种「报错看不出该怎么办」相反，**记为一个正例**。
            450 ★★ **与本会话前几轮的对照**：
               ```
               事实 91/93（轮 151/153）：**说了没做** / **前提没验** ⇒ 假绿
               事实 96（本轮）          ：**docstring 说的就是真的** ⇒ 真货
               ⇒ ★★ 两者用的是**同一种手法**（魔数 / 回读计数 / 多法对照）——
                 **手法一样，结论可以相反** ⇒ 这正是「取证」与「背书」的区别。
               ```
               ⚑ **未查证**：⚠ **DWG 版本不可选**（没查到入口）；⚠ 只测**钣金件**那条路
                 （**工程图** `doc_type == 3` 那条**没测**）；⚠ **没测 `.dwg` 能不能被 AutoCAD 打开**
                 ⇒ 只证「文件头是 DWG」，**不证「内容完好」**。
               已知事实 **96** 入库 · 回归 **1232 passed** · `release_check` exit 0。
               下轮候选：① 测**工程图**那条路（`doc_type == 3`）的 `.dwg`；② 回到「真缺」继续补；
               ③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+446 ", before, re.M):
    print("  游标 446 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+450 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 450 行已存在 ✓")
