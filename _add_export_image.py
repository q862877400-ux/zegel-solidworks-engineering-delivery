import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_export.py")
t = P.read_text(encoding="utf-8")

NEW = '''

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**不是**从四家外部 MCP 项目移植）。
# 文件:   scripts/sw_export.py —— 「视图存成 PNG/JPG」这一段（2026-10-01 轮 147）。
# 定位:   补 `export_image` 那一档的**非 BMP 格式** —— 轮 146 只做了 `SaveBMP`（**只出 `.bmp`**），
#         当时把"png/jpg 要走 SaveAs 的图片过滤器"写进限度、**未做**。本函数收掉那条边界。
# 官方依据: ① 出厂类型库反射 `iface_sldworks.txt` —— ★ **两个重载**：
#             `Int32   SaveAs3(String, Int32, Int32)`
#             `Boolean SaveAs3(String, Int32, Int32, Object, Object, Int32&, Int32&)`
#           ② `C:\\swapi\\types\\IModelDocExtension\\SaveAs3.md`：
#             `bool SaveAs3(string Name, int Version, int Options, object ExportData,
#              object AdvancedSaveAsOptions, out int Errors, out int Warnings)`
#             ⚠ **三级废弃链**：`SaveAs` ⇒（Superseded）⇒ `SaveAs2` ⇒（Superseded）⇒ **`SaveAs3`**
#             ⇒ 本模块**只用现行那个**。
#           ③ ★ 本函数用的是**反射里那个 3 参重载**（`Int32 SaveAs3(String, Int32, Int32)`）——
#             它**没有出参** ⇒ 免掉 `out_i4()`（事实 12/68 那一族的坑），返回 `Int32` 状态码。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义 —— 本块文档化 `export_to_image` 一个单元。
# ─────────────────────────────────────────────────────────────────────
#: 官方 `swSaveAsOptions_e.swSaveAsOptions_Silent` —— 静默（不弹对话框）。
SW_SAVE_AS_SILENT = 1
#: 支持的图片扩展名（**按官方图片过滤器**；实测见 `tools/verify_png_smoke.py`）。
IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")


def export_to_image(model, output_path, *, silent=True):
    """把**当前视图**存成 PNG / JPG（官方 `IModelDocExtension.SaveAs3`）。

    :param model: `IModelDoc2`
    :param output_path: 目标路径；扩展名须是 `.png` / `.jpg` / `.jpeg`。
    :param silent: 传官方 `swSaveAsOptions_Silent`（**默认 True**，不弹对话框）。
    :returns: 输出路径（`Path`）。
    :raises ValueError: 扩展名不在 `IMAGE_EXTENSIONS` 里。
    :raises RuntimeError: 官方返回**非 0**（3 参重载返回 `Int32` 状态码）。

    ★ **为什么不用 `SaveBMP`**：那个**只出 `.bmp`**（round 146 的限度）。
    本函数走 `SaveAs3` 的**图片过滤器** ⇒ 出 `.png` / `.jpg`。
    ⚠ 尺寸**不可指定**（`SaveAs3` 没有尺寸入参）⇒ 按当前视图。
    """
    p = Path(output_path)
    if p.suffix.lower() not in IMAGE_EXTENSIONS:
        raise ValueError("扩展名须是 %s，实际 %r" % (IMAGE_EXTENSIONS, p.suffix))
    code = get_com_member(
        get_com_member(model, "Extension"), "SaveAs3",
        str(p), 0, SW_SAVE_AS_SILENT if silent else 0)
    if code not in (0, None) and code != 0:
        #: ⚠ 3 参重载返回 `Int32` 状态码（0 = 成功）。⚠ **0 不代表文件一定写出来了** ——
        #: 调用方应当**再查文件**（同既有 `export_to_step` 那一族的纪律）。
        raise RuntimeError(
            "IModelDocExtension.SaveAs3 返回 %r（非 0）⇒ 图片没导出来。"
            "⚠ 常见原因：扩展名不在该文档类型的图片过滤器里 / 路径不可写。" % (code,)
        )
    if not p.is_file() or p.stat().st_size == 0:
        raise RuntimeError(
            "SaveAs3 返回 %r（看着成功）但**文件不在或为空**：%s —— "
            "★ 这正是「**0 不代表成功**」那条纪律要挡的（照 `export_to_step` 的既有做法）。"
            % (code, p)
        )
    return p
'''

if "def export_to_image" not in t:
    t = t.rstrip() + "\n" + NEW
    P.write_text(t, encoding="utf-8")
    print("  ok 已追加 export_to_image")
else:
    print("  已有")
ast.parse(P.read_text(encoding="utf-8"))
print("  语法 OK")
