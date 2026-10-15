import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

EV = ("python tools/probe_dwg_magic.py（**真机**，轮 156，钣金件 60x40x1 mm 已保存到 output/）："
      "**读魔数**取证 —— `.dxf` ⇒ **20208 字节**，头部 `  0\\r\\nSECTI` ⇒ **DXF** ✓；"
      "`.dwg` ⇒ **272032 字节**，头部 `AC1015` ⇒ **真 DWG（AC1015 = AutoCAD 2000 / R2000）** ✓。"
      "★ 结论：`export_to_dxf` 的「DXF/DWG」是**名实相符**的（正面结论）。"
      "★ 另记前置条件：**零件路径要求「钣金件 + 必须先保存」** —— 普通拉伸件会报"
      "`ValueError: 导出展开 DXF 前必须先保存钣金零件`（**错误清晰、是对的**）。")
L = ("★★ **2026-10-01（轮 156）验证了 `.dwg` 是真 DWG**：`export_to_dxf` 的 docstring 写"
     "「DXF/DWG」，而 `_export_for_format` 把两个扩展名路由到同一个函数 —— "
     "本轮**读魔数**取证：`.dxf` 头部 `  0\\r\\nSECTI`（DXF 文本）· `.dwg` 头部 **`AC1015`**"
     "（**真 DWG**）⇒ **名实相符**。⚠ **`AC1015` = AutoCAD 2000 / R2000** —— "
     "**不是最新版**；若下游要求更新的 DWG 版本，**本轮没查到通过 API 指定版本的入口**"
     "（`SaveAs3` 无此参数，疑为用户首选项级别 ⇒ **未验证**）。"
     "★ 前置条件：**零件路径要求「钣金件 + 必须先保存」**（错误信息清晰）。")

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") == "export_delivery":
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        c["limitations"].insert(0, L)
        print("  ok export_delivery 已更新")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

FACT = "| 96 | " + "".join([
    "**`.dwg` 导出的**是真 DWG**（头部 `AC1015` = AutoCAD 2000 / R2000），`.dxf` 是真 DXF** —— ",
    "2026-10-01（轮 156）**读魔数**取证（`tools/probe_dwg_magic.py`，钣金件 60×40×1 mm 已保存）：",
    "`.dxf` ⇒ 20208 字节，头部 `  0\\r\\nSECTI` ⇒ **DXF 文本** ✓；",
    "`.dwg` ⇒ 272032 字节，头部 **`AC1015`** ⇒ **真 DWG** ✓。",
    "★ 结论：`scripts/sw_export.py` 的 `export_to_dxf` 文档串写「DXF/DWG」**名实相符**",
    "（与事实 91/93 那种「说了没做」相反，这是一个**正面的**验证）。",
    "⚠ **`AC1015` 是 AutoCAD 2000 / R2000**，**不是最新版** ⇒ 若下游要求更新的 DWG，",
    "**本轮没查到通过 API 指定版本的入口**（`SaveAs3` 无此参数，疑为用户首选项级别 ⇒ **未验证**）。",
    "★ **前置条件**（实测）：零件路径要求 **「钣金件 + 必须先保存」** —— ",
    "普通拉伸件会报 `ValueError: 导出展开 DXF 前必须先保存钣金零件`（**错误清晰、指向明确**）。",
    "★ 可复用的手法：判「导出格式对不对」**用魔数**（DXF 文本 vs DWG 二进制 `AC10xx`），",
    "比「文件存在」「没抛异常」强得多（与事实 86/87 那一族同）。 | ",
    "`tools/probe_dwg_magic.py`；`D:\\AI\\SW\\output\\dwg-magic.json`；`scripts/sw_export.py` 的 `export_to_dxf` |",
])
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
if "| 96 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 96")
else:
    print("  已有 96")
