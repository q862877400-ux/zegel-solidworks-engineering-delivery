import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 已知事实 69
P = Path(r"D:\AI\SW\docs\known-facts.md")
t = P.read_text(encoding="utf-8")
ADD = """

| # | 事实 | 依据 |
|---|---|---|
| 69 | **`IHoleStandardsData` 拿到后必须先"热身"：不先调一次 `GetHoleStandards`，直接调 `GetFastenerTypes` 会返回 `False`** —— 2026-10-01（轮 125）真机四组对照：**A 拿到 data 直接调 ⇒ `False`**；**B 先调 `GetHoleStandards` 再调 ⇒ `True`**；C 在 A 那个（未热身的）对象上**再调一次** ⇒ 仍 `False`（⇒ 不是"调一次就好"）；D 换标准名 `'ISO'` ⇒ 仍 `False`（⇒ 不是名字问题）。⇒ ★ 官方文档**没写**这条约束。修法：`scripts/sw_hole_features._hole_standards_data()` **默认顺手调一次 `GetHoleStandards` 当初始化**（`initialize=False` 可跳过）。★ 反向验证已固化进冒烟：**去掉热身 ⇒ `GetFastenerTypes` 返回 `False`**（不是"加了也没坏处"） | `tools/verify_hole_standards_smoke.py`（11/11，含该反向验证）；`_probe_fastener_ordering.py` 的 A/B/C/D 四组；`tests/test_sw_hole_features.py` 的 `test_hole_standards_data_warms_up_by_default` |
"""
if "必须先「热身」" not in t:
    P.write_text(t.rstrip() + ADD, encoding="utf-8")
    print("  ok known-facts 已加 69")
else:
    print("  已有 69")

# ② 能力条目
import json
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
for c in d["capabilities"]:
    if c.get("id") != "holes_and_finishing":
        continue
    c["evidence"] = [
        e for e in (c.get("evidence") or []) if "verify_hole_standards_smoke" not in e
    ] + [
        "python tools/verify_hole_standards_smoke.py"
        "（**真机**，SW 2026 SP4.1 / 34.4.1：`list_hole_standards` → 15 条 · "
        "`list_fastener_types('ANSI Inch')` → 14 条 · `list_fastener_table_types` → [0,1,2]，"
        "**11/11 通过**，含「**去掉热身就会失败**」的反向验证，"
        "证据落 output/hole-standards-smoke-evidence.json）"
    ]
    c["limitations"].insert(0, "⚑ 2026-10-01（轮 125）**再把 3 个孤儿接上**（上轮接了 1 个）—— "
                              "`list_fastener_types` / `list_fastener_table_types` 已可用；"
                              "`get_fastener_table` **到不了**（见下）。"
                              "★ 链路：标准（15）→ 紧固件类型（14）→ 表类型（`[0,1,2]`）。")
    c["limitations"].insert(1, "★★ **查出一条官方没写的行为约束**：`IHoleStandardsData` 拿到后"
                              "**必须先调一次 `GetHoleStandards` 热身** —— 否则 `GetFastenerTypes` "
                              "**返回 `False`**。真机四组对照排除了两种替代解释（同一未热身对象"
                              "**再调也不变**；换标准名**也一样**）。⇒ 已在 `_hole_standards_data()` "
                              "里默认热身；★ 冒烟里加了**反向验证**（去掉热身 ⇒ 返回 `False`）—— "
                              "**证明它真的必要**，不是「加了也没坏处」。")
    c["limitations"].insert(2, "❌ **`get_fastener_table` 到不了**：官方 `Boolean GetFastenerTable("
                              "String, Int32, Int32, out Object)`，第 4 参是 `out IHoleDataTable`；"
                              "用**同族另外三个已验过**的容器形态 `VARIANT(VT_BYREF|VT_VARIANT, None)` 传，"
                              "三个 `TableID` 全报 `com_error -2147352571`「类型不匹配」**位置 4**。"
                              "⚠ **按事实 53 停手**；保留该函数作**可复算的证据**。")
    c["limitations"].insert(3, "⚠ **名称随 UI 语言变**：本机中文 UI ⇒ `list_fastener_types` 返回的是"
                              "`'六角精致螺栓'` 这类**中文名**（**不是**英文）。"
                              "⇒ 调用方**不要假定是英文**；标准名那一层（`'ANSI Inch'`）倒是英文。")
    print("  ok holes_and_finishing 已更新")
    break
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  能力数 %d" % len(d["capabilities"]))
