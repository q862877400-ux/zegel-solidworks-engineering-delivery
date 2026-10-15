import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_export.py")
t = P.read_text(encoding="utf-8")

NEW = '''

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_export.py —— 「视图存图」这一段（2026-10-01 轮 146）。
# 定位:   补 `docs/union-gap-triage.md`「真缺」档里的 `export_image` / `capture_screenshot`。
#         ⚑ 本模块原有 step/stl/iges/parasolid/pdf/dxf，**没有图片** ⇒ 这是真缺口。
# 官方依据: ① 出厂类型库反射 `iface_sldworks.txt`：`Boolean SaveBMP(String, Int32, Int32)`
#           ② `C:\\swapi\\types\\IModelDoc2\\SaveBMP.md`：
#             `bool SaveBMP(string FileNameIn, int WidthIn, int HeightIn)`
#             · Returns: **True if file is created successfully, false if not**
#             · Remarks: **必须带完整路径且扩展名是 `.bmp`**；
#               **WidthIn/HeightIn ≤ 0 ⇒ 按当前窗口尺寸**
#           ③ ★ 三源一致（反射 / swapi / 官方示例链接），无冲突（铁律 4）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化 `export_to_bmp` 一个单元。
# ─────────────────────────────────────────────────────────────────────
def export_to_bmp(model, output_path, width=0, height=0):
    """把**当前视图**存成 BMP（官方 `IModelDoc2.SaveBMP`）。

    :param model: `IModelDoc2`
    :param output_path: 目标路径。⚠ 官方 Remarks 要求**完整路径**且扩展名 `.bmp`。
    :param width, height: 像素尺寸。★ **≤ 0 ⇒ 按当前窗口尺寸**（官方 Remarks）。
    :returns: 输出路径（`Path`）。
    :raises RuntimeError: 官方**返回 `False`**（没建出来）。

    ⚠ 与 `scripts/sw_capture.py` 的分工：那个走 **Windows GDI `PrintWindow`**
    （抓**窗口**、不受遮挡），本函数走 **SolidWorks 自己的 SaveBMP**
    （抓**当前视图**、无需窗口在前台）。**两者都在，用途不同。**
    """
    p = Path(output_path)
    if p.suffix.lower() != ".bmp":
        raise ValueError("官方要求扩展名是 `.bmp`，实际 %r" % p.suffix)
    ok = get_com_member(model, "SaveBMP", str(p), int(width), int(height))
    if not ok:
        raise RuntimeError(
            "IModelDoc2.SaveBMP 返回 False ⇒ 没写出图（官方说 True 才是成功）。"
            "⚠ 常见原因：路径不是完整路径 / 目录不存在 / 扩展名不是 .bmp"
        )
    return p
'''

if "def export_to_bmp" not in t:
    t = t.rstrip() + "\n" + NEW
    P.write_text(t, encoding="utf-8")
    print("  ok 已追加 export_to_bmp")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
