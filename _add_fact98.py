import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

EV = ("python tools/probe_pdf_on_drawing.py（**真机**，轮 158，工程图 1 张图纸已保存）："
      "★★ 修好后 `export_to_pdf` 成功 ⇒ **39830 字节 · 头部 `%PDF-1.4` · 页数 = 1**（数 `/Type /Page`）"
      "⇒ 定量证据；★ 同时 `export_to_dxf(.dwg)` 在**工程图**上 ⇒ **279450 字节 · 头部 `AC1015`**"
      "（真 DWG）⇒ 轮 156 那条「只测钣金件」的限度补上了。")
L = ("★★★ **2026-10-01（轮 158）修好了一个**此前从未能运行过**的公开函数** "
     "`sw_export.export_to_pdf` —— 它有**两处**缺陷：① 第一行 `model.GetSldWorksObject()`，"
     "而该成员**两套官方源都查不到**（铁律 5）⇒ 零件与工程图**都**抛 "
     "`AttributeError: <unknown>.GetSldWorksObject`；② `SaveAs(output_path, …)` 收 `Path` ⇒ "
     "`TypeError: must be real number, not WindowsPath`。"
     "⇒ 修法：**(a)** 加可选入参 `sw=None`，缺省走 `sw_connect.connect_solidworks()` 取**同一实例**"
     "（COM 单实例，符合事实 24）；**(b)** `str(output_path)`。"
     "★ 修后真机验证：**39830 字节 · `%PDF-1.4` · 页数 = 1**（定量）。"
     "⚠⚠ 影响面：`mcp-server/server.py` 的 `solidworks_export_active` **pdf 格式**、"
     "`sw_session.py` 的 `.pdf` 路由 —— **此前都是坏的**（用户可见）。"
     "⚠ 仍未查证：只验了**工程图**那条路（**零件**上仍会失败 ⇒ 那是**应然的**，"
     "因为 PDF 是工程图语义）。")

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") == "export_delivery":
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        c["limitations"].insert(0, L)
        print("  ok export_delivery 已更新")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

FACT = "| 98 | " + "".join([
    "**`sw_export.export_to_pdf` 此前**从未能运行过** —— 两处缺陷，2026-10-01（轮 158）修好** —— ",
    "① 第一行 `model.GetSldWorksObject()`，而该成员**两套官方源都查不到**",
    "（`D:\\AI\\SW\\_raw\\**\\iface_*.txt` 与 `C:\\swapi\\types\\` 均无）⇒ **铁律 5**：名字缺席 = 没有这个成员；",
    "⇒ 零件与工程图**都**抛 `AttributeError: <unknown>.GetSldWorksObject`；",
    "② `model.Extension.SaveAs(output_path, …)` 收 `Path` ⇒ `TypeError: must be real number, not WindowsPath`",
    "（★ 报错**完全看不出**是路径类型问题 —— 与事实 59 同族：**路径类型要在边界上 settle 一次**）。",
    "⇒ 修法：**(a)** 加可选入参 `sw=None`，缺省走 `sw_connect.connect_solidworks()` 取**同一实例**",
    "（COM 单实例 ⇒ 符合事实 24 的单源约束）；**(b)** `str(output_path)`。",
    "★★ 修后真机验证（`tools/probe_pdf_on_drawing.py`，工程图 1 张）：",
    "**39830 字节 · 头部 `%PDF-1.4` · 页数 = 1**（数 `/Type /Page`）⇒ **定量证据**。",
    "★★★ **影响面（用户可见）**：`mcp-server/server.py` 的 `solidworks_export_active` 的 **pdf 格式**、",
    "`sw_session.py` 的 `.pdf` 路由 —— **此前都会炸**。",
    "★ 为什么之前没被发现：**没有任何测试/冒烟跑过它** —— ",
    "与事实 60（存在但没人用的守卫）**同族**：**存在但没人跑的函数**也一样。",
    "★ 回归判据：`tests/test_sw_export_pdf_contract.py`（4 条）—— 其中「不许再出现该成员」那条",
    "**用 `ast` 只查代码**（docstring 里**要**写明它；第一版搜整段源码 ⇒ **假阳性**，已修）。",
    " | `tools/probe_pdf_on_drawing.py`；`tests/test_sw_export_pdf_contract.py`；事实 59 / 60 / 97 |",
])
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
if "| 98 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 98")
else:
    print("  已有 98")
