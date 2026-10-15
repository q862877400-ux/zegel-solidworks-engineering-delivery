import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
EV = ("python tools/verify_bmp_smoke.py（**真机**，SW 2026 SP4.1 / 34.4.1："
      "`export_to_bmp(model, path, 800, 600)` 建成 ⇒ **读回 BMP 头（偏移 18/22，小端 int32）"
      "尺寸 == 800x600**（**定量往返**，空操作满足不了）；官方 Remarks 那条也验了 —— "
      "宽高 ≤ 0 ⇒ 读回 (1460, 1049) 即**窗口尺寸**；扩展名不是 `.bmp` ⇒ ValueError；"
      "**8/8 通过**，证据落 output/bmp-smoke-evidence.json）")
L = ("⚑ 2026-10-01（轮 146）**补 `export_image` / `capture_screenshot`**（真缺档）："
     "`sw_export.export_to_bmp` 走官方 `IModelDoc2.SaveBMP(String, Int32, Int32)` "
     "（**三源一致**：反射 / swapi / 官方示例；`Boolean` 返回 ⇒ 可查成败）。"
     "★ 与既有 `scripts/sw_capture.py` **分工**：那个走 Windows GDI `PrintWindow`（抓**窗口**、"
     "不受遮挡），本函数走 SolidWorks 自己的 SaveBMP（抓**当前视图**、无需窗口在前台）。"
     "⚠ **未查证**：只证「尺寸按请求走 + 文件合法」，**不证画面内容**（不比对像素）；"
     "无头（headless）环境下 SaveBMP 是否可用**未测**。")

for c in d["capabilities"]:
    if c.get("id") == "export_delivery":
        c["evidence"] = list(c.get("evidence") or []) + [EV]
        c["limitations"].insert(0, L)
        print("  ok export_delivery 已更新")
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

FACT = "| 86 | " + "".join([
    "**`IModelDoc2.SaveBMP(String, Int32, Int32)` 可用，且**宽高入参**可以做「定量往返」验证** —— ",
    "2026-10-01（轮 146）真机实测（`tools/verify_bmp_smoke.py`，SW 2026 SP4.1 / 34.4.1）：",
    "`export_to_bmp(model, path, 800, 600)` ⇒ **读回 BMP 头（偏移 18/22，小端 int32）尺寸 == 800x600**；",
    "官方 Remarks 那条也成立 —— **宽高 ≤ 0 ⇒ 按当前窗口尺寸**（实测读回 `(1460, 1049)`）。",
    "★ 三源一致（出厂反射 `Boolean SaveBMP(String, Int32, Int32)` · swapi md · 官方示例链接）⇒ 铁律 4 满足。",
    "★★ 这条的价值在**证据强度**：入参里有宽高 ⇒ 可以**读回文件头**做**定量往返**，",
    "而「没抛异常」那种弱证据是**空操作也能满足**的（事实 40 那一族）。",
    "★ 与 `scripts/sw_capture.py`（GDI `PrintWindow`，抓**窗口**、不受遮挡）**分工不同**：",
    "本函数抓**当前视图**、无需窗口在前台。⚠ 只证尺寸与文件合法，**不证画面内容**；",
    "**无头环境下是否可用未测**。 | `tools/verify_bmp_smoke.py`（**8/8**）；",
    "`scripts/sw_export.py` 的 `export_to_bmp`；`C:\\swapi\\types\\IModelDoc2\\SaveBMP.md`；",
    "`tests/test_sw_export_bmp_contract.py`（4 条）|",
])
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
if "SaveBMP(String, Int32, Int32)" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 86")
else:
    print("  已有 86")
