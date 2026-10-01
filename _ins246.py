import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           246 🎯 **Spec Kit `034`：真缺档再补一条 —— 转换实体引用**（轮 115）——
               ⚠ **并进已有的 `sw_sketch_edit.py`**（与草图倒角/镜像同类）—— **不新开文件**（不重造）。
            247 ★ **选哪个入口：先查废弃，再选**：
               ```
               IModelDoc2.SketchUseEdge2(Boolean)       ⇒ **Obsolete**（md 明写）        ✗
               ISketchManager.ConvertEntities()          ⇒ 未废弃，**零参**              ~ 可用但语义含糊
               ISketchManager.SketchUseEdge3(Bool, Bool) ⇒ 未废弃，**两参都有官方说明**  ✓ **采用**
               ```
               ★ **没有"哪个都行"就随便选一个** —— 选了之后把**为什么**写进来源块与能力条目。
            248 ★ **"失败信号长得像正常值"这一类错，本轮被专门挡了一次**：
               ```
               官方 SketchUseEdge3 失败时返回 **False** ⇒ `if not got: pass` 会**静默吞掉**
               ⇒ 本函数对 False **抛带原因的错**，并**单列一条测试**钉住
               ```
               ★ 与 `028`（方程式的 **`-1` 双重语义**）同一族。
            249 ⚑ **「真缺」档补录进度**：`023` 螺旋线 · `024` 草图倒角/镜像 · `028` 方程式 ·
               `034` 转换实体引用 ⇒ 共 **4 条**（其中本轮这条**并入已有模块**，不新开文件）。
               ⚠ 该档共约 **132 条**（`022` 抽样估），**剩余仍很多**。
            250 ⚑ **未查证**：本机**从未做过**转换实体引用（等级仍 `stitched`）；
               前置条件（先选中 + 在草图态）**未实测**；
               零参的 `ConvertEntities()` 与 `SketchUseEdge3` 的**行为差异未查**。
               回归 **1091 passed**。
               下轮候选：① 继续补「真缺」（`gdt` / `jog` / `activate_sheet` / 图纸类）；
               ② A5 的 2 条存疑；③ 给已补的 4 条做真机冒烟（需先备前置条件）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+246 ", before, re.M):
    print("  游标 246 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+250 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 250 行已存在 ✓")
