"""W6（装配只读）收工的机械步骤（★ 只做加法、只改该改的那一处；幂等）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（收工脚本，工作区仓库）
# 文件:   D:\\AI\\SW\\_w6_finish.py
# 定位:   砌墙 W6 的机械收尾；每处断言锚点，防误改。
# 官方依据: 不适用
# 许可:   本仓库 MIT。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")

p = REPO / "tests" / "test_server_wiring.py"
t = p.read_text(encoding="utf-8")
if "assert len(all_specs()) == 81" in t:
    print("  test_server_wiring: 已是 81，跳过")
else:
    assert "assert len(all_specs()) == 78" in t, "锚点不符"
    t = t.replace("assert len(all_specs()) == 78", "assert len(all_specs()) == 81", 1)
    t = t.replace('"""**十八批**合计 **78** 条', '"""**十九批**合计 **81** 条', 1)
    t = t.replace(
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**',
        "    ★ **轮 237（Spec Kit `139`，砌墙 W6）新增 `tool_specs_batch25.py`（3 条）⇒ 81** ——\n"
        "    **装配只读**（零部件清单 / 配合清单 / ★★ **干涉检查**）。\n"
        "    ★ 本批第一次用 `inject=\"asm_model\"` ⇒ 为此给 `RESOLVERS` **加了一行**\n"
        "    （注入名只能是那张表的键；那个模块有一批函数首参叫 `asm_model`）。\n"
        "    ★★ 干涉检查那个函数**修过三处成员名却从没验过**（注释自述「此前静默降级」）\n"
        "    ⇒ 本批是它的**第一次真机验证**，设计成**一正一反**：重叠 ⇒ count 1 · 分开 ⇒ count 0。\n"
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**', 1)
    p.write_text(t, encoding="utf-8")
    print("  ✓ test_server_wiring: 78 → 81")

q = REPO / "tests" / "test_mcp_protocol_layer.py"
u = q.read_text(encoding="utf-8")
if "assert n == 126" in u:
    print("  test_mcp_protocol_layer: 已是 126，跳过")
else:
    assert "assert n == 123" in u, "锚点不符"
    u = u.replace("assert n == 123", "assert n == 126", 1)
    u = u.replace("**123** 条", "**126** 条", 1)
    u = u.replace(
        "轮 234（砌墙 W5）新增 `tool_specs_batch24.py` 的 1 个质量属性读数 ⇒ **122 → 123**。",
        "轮 234（砌墙 W5）新增 `tool_specs_batch24.py` 的 1 个质量属性读数 ⇒ **122 → 123**；\n"
        "      轮 237（砌墙 W6）新增 `tool_specs_batch25.py` 的 3 个装配只读 ⇒ **123 → 126**。", 1)
    q.write_text(u, encoding="utf-8")
    print("  ✓ test_mcp_protocol_layer: 123 → 126")

bp = REPO / "tests" / "unattended_baseline.json"
d = json.loads(bp.read_text(encoding="utf-8"))
if "assembly_read" in d["allowed"]:
    print("  基线: 已在，跳过")
else:
    d["allowed"].append("assembly_read")
    d["allowed"] = sorted(set(d["allowed"]))
    bp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 基线只加 assembly_read（schema 与 denied_count 一字未动）")

cP = REPO / "capabilities.yaml"
cap = json.loads(cP.read_text(encoding="utf-8"))
if any(c.get("id") == "assembly_read" for c in cap["capabilities"]):
    print("  能力清单: 已在，跳过")
else:
    cap["capabilities"].append({
        "id": "assembly_read",
        "label": "装配只读（零部件清单 / 配合清单 / 干涉检查）",
        "level": "verified",
        "backends": ["solidworks-com-pywin32"],
        "verified_versions": ["2026"],
        "dependencies": ["solidworks"],
        "limitations": [
            "★★ **干涉检查的真机验证是本轮第一次做的**：那个函数此前**修过三处成员名却从没验过**"
            "（其源码注释自述「两处都在 try: 里 ⇒ 此前静默降级（不炸，但永远拿不到数据）」）"
            "⇒ ★ 现在有正反两个场景的读数（重叠 ⇒ 1 · 分开 ⇒ 0）",
            "★ 干涉检查的 `status` 语义：`pass` = 无干涉 · `warn` = 有干涉 · "
            "**`blocked` = 检查本身失败** ⇒ ★ **不要把 blocked 读成「无干涉」**",
            "★ 每项干涉只报 `volume` 与 `component_count` —— 官方 `IInterference` 上**没有 `Name`**",
            "★ `collect_mate_feature_summary` 报的是**特征树里写了哪些配合**，"
            "**不等于**自由度分析（不判「装对了没有」）",
            "⚠ 真机验证用了**两个零件、同一文件**（在 `output/_fixtures/` 里造的临时夹具、"
            "插入坐标相同/相隔 60mm 造出重叠/分开两场景）⇒ ★ 复杂装配与子装配**未验证**",
            "★ 本能力**只读**；加组件/加配合是别的能力",
        ],
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "evidence": [
            "python tools/capture_assembly_evidence.py（真机，2026-10-01 轮 237 / 砌墙 W6："
            "造临时零件（40×20×10 盒）存到 output/_fixtures/ → 建装配 → 同一零件加两次；"
            "★ **一正一反**：重叠（都在 z=0）⇒ interference_count **1** · "
            "分开（z=0 与 z=60）⇒ **0**（status pass）；另回读 2 个组件与配合清单。"
            "verdict: pass，证据落 output/assembly-evidence.json）",
            "pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 81 / 协议层 126）",
        ],
        "source": "original",
        "source_evidence": "scripts/sw_assembly.py 的 get_components / collect_mate_feature_summary / "
                           "get_interference_detection（照官方 IAssemblyDoc.GetComponents · "
                           "IInterferenceDetectionMgr · IInterference）",
    })
    cP.write_text(json.dumps(cap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 能力清单已加 assembly_read")

d2 = json.loads(cP.read_text(encoding="utf-8"))
print("  能力条目: %d" % len(d2["capabilities"]))
print("  level 分布:", dict(Counter(c.get("level") for c in d2["capabilities"])))
