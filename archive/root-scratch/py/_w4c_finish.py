"""W4 续（倒角/圆角）收工的机械步骤（★ 只做加法、只改该改的那一处；幂等）。

1. test_server_wiring 75 → 77
2. test_mcp_protocol_layer 120 → 122
3. 无人值守基线：★ **只加** `chamfer_fillet_on_selection` 一条（不重生成）
4. capabilities.yaml：加 `chamfer_fillet_on_selection`

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（收工脚本，工作区仓库）
# 文件:   D:\\AI\\SW\\_w4c_finish.py
# 定位:   砌墙 W4 续（倒角/圆角）的机械收尾；每处断言锚点，防误改。
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
if "assert len(all_specs()) == 77" in t:
    print("  test_server_wiring: 已是 77，跳过")
else:
    assert "assert len(all_specs()) == 75" in t, "锚点不符"
    t = t.replace("assert len(all_specs()) == 75", "assert len(all_specs()) == 77", 1)
    t = t.replace('"""**十六批**合计 **75** 条', '"""**十七批**合计 **77** 条', 1)
    t = t.replace(
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**',
        "    ★ **轮 231（Spec Kit `137`，砌墙 W4 续）新增 `tool_specs_batch23.py`（2 条）⇒ 77** ——\n"
        "    **倒角 / 圆角**。★ 这是**第一次用规则 3 的声明式 `selection` 驱动「建特征」工具**：\n"
        "    能力层两个函数**都没有 `edges` 参数** ⇒ 作用在**当前选择**上 ⇒ 对外的 `selection`\n"
        "    由 `pre_call` 解析成真实选区（复用 `batch4` 的既有机制）。\n"
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**', 1)
    p.write_text(t, encoding="utf-8")
    print("  ✓ test_server_wiring: 75 → 77")

q = REPO / "tests" / "test_mcp_protocol_layer.py"
u = q.read_text(encoding="utf-8")
if "assert n == 122" in u:
    print("  test_mcp_protocol_layer: 已是 122，跳过")
else:
    assert "assert n == 120" in u, "锚点不符"
    u = u.replace("assert n == 120", "assert n == 122", 1)
    u = u.replace("**120** 条", "**122** 条", 1)
    u = u.replace(
        "轮 230（砌墙 W4 续）新增 `tool_specs_batch22.py` 的 3 个拉伸 ⇒ **117 → 120**。",
        "轮 230（砌墙 W4 续）新增 `tool_specs_batch22.py` 的 3 个拉伸 ⇒ **117 → 120**；\n"
        "      轮 231（砌墙 W4 续）新增 `tool_specs_batch23.py` 的 2 个倒角/圆角 ⇒ **120 → 122**。", 1)
    q.write_text(u, encoding="utf-8")
    print("  ✓ test_mcp_protocol_layer: 120 → 122")

bp = REPO / "tests" / "unattended_baseline.json"
d = json.loads(bp.read_text(encoding="utf-8"))
if "chamfer_fillet_on_selection" in d["allowed"]:
    print("  基线: 已在，跳过")
else:
    d["allowed"].append("chamfer_fillet_on_selection")
    d["allowed"] = sorted(set(d["allowed"]))
    bp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 基线只加 chamfer_fillet_on_selection（schema 与 denied_count 一字未动）")

cP = REPO / "capabilities.yaml"
cap = json.loads(cP.read_text(encoding="utf-8"))
if any(c.get("id") == "chamfer_fillet_on_selection" for c in cap["capabilities"]):
    print("  能力清单: 已在，跳过")
else:
    cap["capabilities"].append({
        "id": "chamfer_fillet_on_selection",
        "label": "倒角 / 圆角（作用于声明式选择选中的边）",
        "level": "verified",
        "backends": ["solidworks-com-pywin32"],
        "verified_versions": ["2026"],
        "dependencies": ["solidworks"],
        "limitations": [
            "★★ **两个函数都没有 `edges` 参数** ⇒ 它们作用在**当前选择**上 ⇒"
            "对外的 `selection`（规则 3 的声明式形态）由 `pre_call` 解析成真实选区。"
            "★ 真机对照实验证实了这一点：清空选区后调用 ⇒ **特征数不变**（21 → 21）",
            "★★ **但「清空选区」时它**不抛错**（返回一个无名对象、特征数不变）⇒"
            "★ 这是本族的**静默失败点**（与 batch21「不 start 就画线」同型）；"
            "★ 目前**没有机器守卫**，靠工具说明与 `selection` 的解析约束",
            "★ 越界 `selection` ⇒ `EntitySelectionError`，且错误信息**给出上界**（如「体 0 上共 18 个」）",
            "★ 断言的读数只能用**特征树计数 + 返回对象的名字**（如「倒角1」/「圆角1」）——"
            "项目里**没有**体积/质量属性工具；★ 包围盒**通常不变**（切掉角不改变最大坐标）",
            "★ 只在**前视基准面**上、对**一个盒体**验证过",
        ],
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "evidence": [
            "python tools/capture_chamfer_fillet_evidence.py（真机，2026-10-01 轮 231 / 砌墙 W4 续："
            "建草图→拉伸成盒 → 选 `index:0` → `chamfer(2mm)` ⇒ 特征「**倒角1**」（19→20）；"
            "再选 `index:1` → `fillet(3mm)` ⇒ 特征「**圆角1**」（→21）；"
            "★ **对照实验**：清空选区后调用 ⇒ **特征数不变**（21→21，且返回对象无名）"
            "⇒ 证实「它作用在当前选择上」；负例：`index:9999` ⇒ EntitySelectionError（给出上界 18）。"
            "verdict: pass，证据落 output/chamfer-fillet-evidence.json）",
            "pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 77 / 协议层 122）",
        ],
        "source": "original",
        "source_evidence": "scripts/sw_part.py 的 chamfer / fillet（照官方 "
                           "IFeatureManager.InsertFeatureChamfer —— 形态已按铁律 4 核过："
                           "swChamferType_e.swChamferAngleDistance = 1，两源一致）",
    })
    cP.write_text(json.dumps(cap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 能力清单已加 chamfer_fillet_on_selection")

d2 = json.loads(cP.read_text(encoding="utf-8"))
print("  能力条目: %d" % len(d2["capabilities"]))
print("  level 分布:", dict(Counter(c.get("level") for c in d2["capabilities"])))
