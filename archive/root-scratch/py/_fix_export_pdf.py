import ast
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_export.py")
t = P.read_text(encoding="utf-8")

OLD = '''def export_to_pdf(model, output_path, sheet_names=None):
    """
    导出工程图为 PDF

    参数:
        model: IModelDoc2（必须是工程图文档）
        output_path: PDF 文件路径
        sheet_names: 图纸名称列表，None=所有图纸
    """
    sw = model.GetSldWorksObject()'''

NEW = '''# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（**缺陷修复**，2026-10-01 轮 158）。
# 文件:   scripts/sw_export.py —— `export_to_pdf` 的**第一行**。
# 定位:   ⚠⚠⚠ **两套官方源都查不到 `IModelDoc2.GetSldWorksObject`**
#         （`D:\\AI\\SW\\_raw\\**\\iface_*.txt` 与 `C:\\swapi\\types\\` 均无此名）
#         ⇒ 按**铁律 5**：名字缺席 = 官方 API 里没有这个成员。
#         ★★ 真机实测（`tools/probe_pdf_on_drawing.py`）：无论是**零件**还是**工程图**，
#         都在这一行抛 `AttributeError: <unknown>.GetSldWorksObject`
#         ⇒ **`export_to_pdf` 此前从未能运行过**（4 个调用点全都会炸）。
# 官方签名依据: `ISldWorks.GetExportFileData(System.int FileType)`（下表那一行已在用）；
#         拿 `ISldWorks` 的**正确**路径是**从连接处持有** —— 本函数的调用方
#         （`server.py` / `sw_session.py`）本来就有 `sw`，故**加可选入参 `sw=None`**
#         （向后兼容：缺省时走既有 `sw_connect.connect_solidworks()`，
#          COM 是**单实例**，拿到的是**同一个** SolidWorks —— 与事实 24 的单源约束一致）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   本函数的签名与第一行（至 `pdf_data` 那行之前）
# ─────────────────────────────────────────────────────────────────────
def export_to_pdf(model, output_path, sheet_names=None, *, sw=None):
    """
    导出工程图为 PDF

    参数:
        model: IModelDoc2（必须是工程图文档）
        output_path: PDF 文件路径
        sheet_names: 图纸名称列表，None=所有图纸
        sw: 可选的 `ISldWorks`。⚠⚠ **2026-10-01（轮 158）新增** ——
            此前本函数第一行写的是 `model.GetSldWorksObject()`，而该成员
            **两套官方源都查不到**（铁律 5）⇒ 无论零件还是工程图都会抛
            `AttributeError: <unknown>.GetSldWorksObject` ⇒ **此前从未能运行过**。
            缺省 `None` 时走 `sw_connect.connect_solidworks()` 取**同一实例**。
    """
    if sw is None:
        import sw_connect
        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]'''

assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
ast.parse(P.read_text(encoding="utf-8"))
print("  ok export_to_pdf 已修（第一行 + 可选 sw 入参 + 来源块）")
