import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
EV = ("python tools/verify_png_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1："
      "`export_to_image` 出 **PNG 129437 字节**（魔数 `89 50 4E 47…` + `IHDR` 尺寸 **1232x1049**）与 "
      "**JPG 54431 字节**（魔数 `FF D8 FF`）；**9/9 通过**，证据落 output/png-smoke-evidence.json）")
L = ("★★ **2026-10-01（轮 147）收掉轮 146 标下的那条边界**：`SaveBMP` **只出 `.bmp`** ⇒ "
     "本轮用 `IModelDocExtension.SaveAs3` 出 `.png` / `.jpg`。"
     "★ 官方是**三级废弃链**（`SaveAs` ⇒ Superseded ⇒ `SaveAs2` ⇒ Superseded ⇒ **`SaveAs3`**）。"
     "⚠⚠ **真机上踩了两个坑**：① 反射里那个 **3 参**重载 `Int32 SaveAs3(String, Int32, Int32)` "
     "在 pywin32 下报 `0x8002000F`（`DISP_E_PARAMNOTOPTIONAL`）⇒ **解析到的是 7 参那个**"
     "（末两个 `out Int32` ⇒ 要用 `out_i4()`）；② `ExportData` / `AdvancedSaveAsOptions` "
     "传 `None` 报 **`类型不匹配`**（位置 4）⇒ 必须用 `create_empty_dispatch_variant()`"
     "（事实 12 / 33 那一族）。⚠ **未查明**：`SaveBMP(0,0)` 与 `SaveAs3` 的**宽度不同**"
     "（1460 vs 1232，高度都是 1049）—— 最可能是「窗口 vs 绘图区」，**但本轮没有验证**"
     "（事实 82/142 的教训：不把没验证的假设写成判据）。⚠ 只证「格式合法 + 尺寸合理」，"
     "**不证画面内容**。")
for c in d["capabilities"]:
    if c.get("id") == "export_delivery":
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        c["limitations"].insert(0, L)
        print("  ok export_delivery 已更新")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

FACT = "| 87 | " + "".join([
    "**`IModelDocExtension.SaveAs3` 有**两个重载**，而 pywin32 解析到的是**7 参**那个** —— ",
    "2026-10-01（轮 147）真机实测（`tools/verify_png_smoke.py`）：反射里 ",
    "`Int32 SaveAs3(String, Int32, Int32)` 与 `Boolean SaveAs3(String, Int32, Int32, Object, Object, ",
    "Int32&, Int32&)` 并存 ⇒ ★ **按 3 参调报 `0x8002000F`（`DISP_E_PARAMNOTOPTIONAL`）**",
    "⇒ 必须按 **7 参**调 + 用 `out_i4()` 给出参占位；★ 返回也随之从 `Int32` 变成 `Boolean`。",
    "⚠ 另一坑：`ExportData` / `AdvancedSaveAsOptions` 传 `None` 报 **`类型不匹配`**",
    " ⇒ 必须 `create_empty_dispatch_variant()`（事实 12 / 33 那一族）。",
    "★★ 与事实 84 的联系：那次是「**取**成员会**调**它」，这次是「**同名重载挑错了那个**」——",
    " 都属「**调用形态的坑**」，而**都只能靠真机实测发现**（静态反射把两个重载都列出来了）。",
    "★ 官方三级废弃链：`SaveAs` ⇒ `SaveAs2` ⇒ **`SaveAs3`**（只用现行）。",
    "⚠ 未查明：`SaveBMP(0,0)` 与 `SaveAs3` 的**宽度不同**（1460 vs 1232，高度都 1049），",
    "  疑为「窗口 vs 绘图区」但**未验证**。 | `tools/verify_png_smoke.py`（**9/9**）；",
    "`scripts/sw_export.py` 的 `export_to_image`；`tests/test_sw_export_image_contract.py`（5 条）；",
    "事实 12 / 33 / 84 / 86 |",
])
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
if "SaveAs3` 有" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 87")
else:
    print("  已有 87")
