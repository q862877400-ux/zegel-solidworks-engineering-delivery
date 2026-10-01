import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

EV = ("python tools/probe_export_magic_matrix.py（**真机**，轮 157，钣金件 60x40x1 mm 已保存）："
      "**逐格式读文件头** ⇒ **9/10 名实相符** —— STEP `ISO-10303-21` · STL `stlbn`（二进制）· "
      "IGES `SolidWorks IGES file` · Parasolid `**ABCDEFGH…` · DXF `  0\\r\\nSECTION` · "
      "DWG `AC1015` · PNG `\\x89PNG` · JPEG `\\xff\\xd8\\xff\\xe0…JFIF` · BMP `BM`；"
      "★ **`pdf` 在零件上失败**：`AttributeError: <unknown>.GetSldWorksObject`")
L = ("★★ **2026-10-01（轮 157）逐格式读文件头，得到一张矩阵**："
     "**9/10 名实相符**（STEP / STL / IGES / Parasolid / DXF / DWG / PNG / JPEG / BMP）。"
     "⚠⚠ **`export_to_pdf` 在「零件」上失败 —— `AttributeError: <unknown>.GetSldWorksObject`**；"
     "它的签名里有 `sheet_names` ⇒ 语义上**是工程图**的入口 ⇒ ⚠ **本轮没做工程图，故未查明**"
     "（不是「功能不行」，是「**我用的对象不对**」）。")

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") == "export_delivery":
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        c["limitations"].insert(0, L)
        print("  ok export_delivery 已更新")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

FACT = "| 97 | " + "".join([
    "**导出格式矩阵（读文件头）：9/10 名实相符；`pdf` 在零件上失败** —— ",
    "2026-10-01（轮 157）`tools/probe_export_magic_matrix.py` 逐格式读头：",
    "STEP `ISO-10303-21` · STL `stlbn`（**二进制**，80 字节 header）· IGES `SolidWorks IGES file` · ",
    "Parasolid `**ABCDEFGH…` · DXF `  0\\r\\nSECTION` · DWG `AC1015` · PNG `\\x89PNG` · ",
    "JPEG `\\xff\\xd8\\xff\\xe0…JFIF` · BMP `BM` ⇒ **全部名实相符**。",
    "★★⚠ **`export_to_pdf` 在\ue000**零件**上失败**：`AttributeError: <unknown>.GetSldWorksObject`；",
    "它的签名带 `sheet_names` ⇒ 语义上**是工程图的入口** ⇒ ⚠ **本轮没做工程图 ⇒ 未查明**",
    "（★ 注意措辞：不是「功能不行」，是「**我用的对象不对**」——与事实 95 同一纪律）。",
    "★★★ **本轮的第二个收获：我的分类器判反了两处** —— 第一版 `classify()` 里 ",
    "「IGES 只认首字节 `S`/`s`」**排在**「ASCII STL 以 `solid` 开头」**之前** ⇒ **顺序 bug**，",
    "把 `.iges`（`SolidWorks IGES file…`，恰以大写 `S` 开头）判成 `STL(ascii)`。",
    "⇒ ★ 改成**把文件头原文打出来**、用证据判之后，真相自明 ⇒ **别让一个容易写错的分类器挡住真相**",
    "（与事实 91/93/94、轮 152/153/154 **同一纪律**，这是**第 4 次**）。 | ",
    "`tools/probe_export_magic_matrix.py`；`D:\\AI\\SW\\output\\export-magic-matrix.json`；事实 96 |",
])
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
if "| 97 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 97")
else:
    print("  已有 97")
