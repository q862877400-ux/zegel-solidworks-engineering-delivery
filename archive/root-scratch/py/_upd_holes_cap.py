import json
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(P.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") != "holes_and_finishing":
        continue
    c["evidence"] = list(c.get("evidence") or []) + [
        "python tools/verify_hole_standards_smoke.py"
        "（**真机**，SW 2026 SP4.1 / 34.4.1：`list_hole_standards(sw, 0)` ⇒ "
        "**15 条真实孔标准**，**6/6 通过**，证据落 output/hole-standards-smoke-evidence.json）"
    ]
    c["limitations"].insert(0, "⚑ 2026-10-01（轮 124）**把 4 个「孤儿包装」接成了能用的 API** —— "
                              "`get_hole_standards` 等 4 个此前**在仓库里没有调用方**"
                              "（它们把**出参甩给调用方**，而调用方得自己造 by-ref VARIANT ⇒ 没人用）。"
                              "本轮补了高层入口 `list_hole_standards(sw, hole_type_id)`："
                              "**自己造容器、自己读回来、按位配对**。")
    c["limitations"].insert(1, "★ **真机证据**：`list_hole_standards(sw, 0)`（沉头孔）⇒ **15 条**，"
                              "如 `{'id': 0, 'name': 'ANSI Inch'}` · `{'id': 4, 'name': 'DIN'}` · "
                              "`{'id': 7, 'name': 'ISO'}`；**15 个名字互不相同**（⇒ 两组出参真的按位配对上了）；"
                              "**命中 ISO / DIN**（⇒ **空操作给不出这个**）。")
    c["limitations"].insert(2, "★★ **出参的正确传法**（真机裁断，已知事实 68）：必须是 "
                              "`VARIANT(VT_BYREF|VT_VARIANT, None)` —— 裸 `None` 与 "
                              "`VT_BYREF|VT_DISPATCH` **都报「类型不匹配」**。"
                              "⚠ 另：`VARIANT` 在 **`win32com.client`** 里，**`pythoncom.VARIANT` 不存在**。")
    c["limitations"].insert(3, "⚠ **未查证**：只证了 `hole_type_id=0`（沉头孔）一档，其余 8 档未测；"
                              "**不证「15 条是全集」**；`id` 的语义未核（只知它与名称一一对应）；"
                              "`get_fastener_types` / `get_fastener_table_types` / `get_fastener_table` "
                              "**仍是孤儿**（本轮只接了 `get_hole_standards` 这一条）；"
                              "★ 也**没有**把它注册成 MCP 工具（需要 `ISldWorks` 而非 `model`，"
                              "注册方式另议）。")
    print("  ok holes_and_finishing 已更新")
    break
else:
    raise SystemExit("  找不到 holes_and_finishing")
P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  能力数 %d" % len(d["capabilities"]))
