"""W5（质量属性读数）收工的机械步骤（★ 只做加法、只改该改的那一处；幂等）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（收工脚本，工作区仓库）
# 文件:   D:\\AI\\SW\\_w5_finish.py
# 定位:   砌墙 W5 的机械收尾；每处断言锚点，防误改。
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
if "assert len(all_specs()) == 78" in t:
    print("  test_server_wiring: 已是 78，跳过")
else:
    assert "assert len(all_specs()) == 77" in t, "锚点不符"
    t = t.replace("assert len(all_specs()) == 77", "assert len(all_specs()) == 78", 1)
    t = t.replace('"""**十七批**合计 **77** 条', '"""**十八批**合计 **78** 条', 1)
    t = t.replace(
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**',
        "    ★ **轮 234（Spec Kit `138`，砌墙 W5）新增 `tool_specs_batch24.py`（1 条）⇒ 78** ——\n"
        "    **读质量属性**。★ 又一个「**能写不能读**」的真空白（有 `set_mass_property_override`\n"
        "    却读不出实际值，与 `specs/133` 同型）。★ 只有 1 个工具：五个读数**总是一起被问**。\n"
        "    ★ 验证用**数字断言**：盒 40×20×10 ⇒ volume **8000** · surface_area **2800** ·\n"
        "    center_of_mass **[0,0,−5]**。\n"
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**', 1)
    p.write_text(t, encoding="utf-8")
    print("  ✓ test_server_wiring: 77 → 78")

q = REPO / "tests" / "test_mcp_protocol_layer.py"
u = q.read_text(encoding="utf-8")
if "assert n == 123" in u:
    print("  test_mcp_protocol_layer: 已是 123，跳过")
else:
    assert "assert n == 122" in u, "锚点不符"
    u = u.replace("assert n == 122", "assert n == 123", 1)
    u = u.replace("**122** 条", "**123** 条", 1)
    u = u.replace(
        "轮 231（砌墙 W4 续）新增 `tool_specs_batch23.py` 的 2 个倒角/圆角 ⇒ **120 → 122**。",
        "轮 231（砌墙 W4 续）新增 `tool_specs_batch23.py` 的 2 个倒角/圆角 ⇒ **120 → 122**；\n"
        "      轮 234（砌墙 W5）新增 `tool_specs_batch24.py` 的 1 个质量属性读数 ⇒ **122 → 123**。", 1)
    q.write_text(u, encoding="utf-8")
    print("  ✓ test_mcp_protocol_layer: 122 → 123")

bp = REPO / "tests" / "unattended_baseline.json"
d = json.loads(bp.read_text(encoding="utf-8"))
if "mass_property_read" in d["allowed"]:
    print("  基线: 已在，跳过")
else:
    d["allowed"].append("mass_property_read")
    d["allowed"] = sorted(set(d["allowed"]))
    bp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 基线只加 mass_property_read（schema 与 denied_count 一字未动）")

cP = REPO / "capabilities.yaml"
cap = json.loads(cP.read_text(encoding="utf-8"))
if any(c.get("id") == "mass_property_read" for c in cap["capabilities"]):
    print("  能力清单: 已在，跳过")
else:
    cap["capabilities"].append({
        "id": "mass_property_read",
        "label": "读零件/装配的质量属性（体积 / 表面积 / 重心 / 密度 / 质量）",
        "level": "verified",
        "backends": ["solidworks-com-pywin32"],
        "verified_versions": ["2026"],
        "dependencies": ["solidworks"],
        "limitations": [
            "★★ **单位是「毫米系」**（实测：盒 40×20×10 mm ⇒ volume **8000**、surface_area **2800**、"
            "center_of_mass z = **−5**）—— **不是 SI 米**，与 `IBody2.GetBodyBox` 一致、"
            "与官方其余几何接口惯用的「米」**不同** ⇒ ★ 本能力**不做任何换算**",
            "★★★ **`mass` 的物理单位未确证**：实测盒上 `mass` 恰好等于 `volume(mm³) × density`，"
            "⇒ **量纲不成立**（若 volume 是 mm³、density 是 kg/m³，质量应是 8 g 而非 8e6）"
            "⇒ ★ 照实透传，**不猜、不给它安一个单位**（见 known-facts 167）",
            "★ `density` 官方惯用 kg/m³，但**本机未实测确认**",
            "⚠ `IMassProperty2.AccuracyLevel` 实测**读不到**（`AttributeError`）⇒ **不暴露**",
            "★ 只读；**改**质量属性覆盖值是另一件事（`sw_export.set_mass_property_override`）",
            "★ 惯性矩 / 主惯性轴**未暴露**（能力层只读了 5 个成员）",
            "★★ 在**工程图**上调用会报错（`GetType()==3` ⇒ 无质量属性）——"
            "★ **这条守卫是真机负例逼出来的**：实测在工程图上 `CreateMassProperty` 也会返回一个"
            "带 `Mass`/`Volume` 的对象 ⇒ 只靠「行为判据」会**静默通过**并返回无意义读数"
            "⇒ 行为判据必须**配合文档类型判据**",
        ],
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "evidence": [
            "python tools/capture_mass_property_evidence.py（真机，2026-10-01 轮 234 / 砌墙 W5："
            "建草图（矩形 40×20）→ 拉伸 10mm → 读质量属性 ⇒ ★ **数字断言**：volume **8000** · "
            "surface_area **2800** · center_of_mass **[0,0,−5]**；另如实记录 `mass` 的量纲疑点与 "
            "`AccuracyLevel` 读不到；负例：在**工程图**上调用 ⇒ RuntimeError。"
            "verdict: pass，证据落 output/mass-property-evidence.json）",
            "python tools/probe_mass_property_reads.py（真机探针：定下「`CreateMassProperty` **当属性取**"
            "即可」——★ 与其兄弟 `CustomPropertyManager`（**必须当方法调**）**相反**；"
            "并实测出**单位是毫米系**；证据 output/mass-property-reads.json）",
            "pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 78 / 协议层 123）",
        ],
        "source": "original",
        "source_evidence": "scripts/sw_mass_property.py（照官方 IModelDocExtension.CreateMassProperty 与 "
                           "IMassProperty2 的 Mass/Volume/SurfaceArea/CenterOfMass/Density 新写）",
    })
    cP.write_text(json.dumps(cap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 能力清单已加 mass_property_read")

d2 = json.loads(cP.read_text(encoding="utf-8"))
print("  能力条目: %d" % len(d2["capabilities"]))
print("  level 分布:", dict(Counter(c.get("level") for c in d2["capabilities"])))
