"""W3 收工的机械步骤（★ 每步都只做加法，且**只改该改的那一处**）。

1. `test_server_wiring`  65 → 67（计数守卫）
2. `test_mcp_protocol_layer` 110 → 112
3. 无人值守基线：★ **只加** `file_custom_property_read` 一条（**不重生成** —— 重生成会吸收别的漂移）
4. `capabilities.yaml`：加 `file_custom_property_read`（level=verified + evidence）

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（收工脚本，工作区仓库）
# 文件:   D:\\AI\\SW\\_w3_finish.py
# 定位:   砌墙 W3 的机械收尾；★ 每处改动都断言锚点，防误改。
# 官方依据: 不适用
# 许可:   本仓库 MIT。
# ⚠ 幂等（重复跑不重复加）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")

#: ── 1/2 计数守卫 ────────────────────────────────────────────────────
p = REPO / "tests" / "test_server_wiring.py"
t = p.read_text(encoding="utf-8")
if "assert len(all_specs()) == 67" in t:
    print("  test_server_wiring: 已是 67，跳过")
else:
    assert "assert len(all_specs()) == 65" in t, "锚点不符（test_server_wiring）"
    t = t.replace("assert len(all_specs()) == 65", "assert len(all_specs()) == 67", 1)
    t = t.replace('"""**十三批**合计 **65** 条', '"""**十四批**合计 **67** 条', 1)
    t = t.replace(
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**',
        "    ★ **轮 227（Spec Kit `133`，砌墙 W3）新增 `tool_specs_batch20.py`（2 条）⇒ 67** ——\n"
        "    **读文件自定义属性**。★ 这批补的是一个**真空白**：本仓库早就能**写**自定义属性\n"
        "    （上游工具），却**读不回来验**。★ 而且只有 2 个工具 —— `count`/`names` 的结果\n"
        "    已被「读全部」包含，**不重复挂**。\n"
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**', 1)
    p.write_text(t, encoding="utf-8")
    print("  ✓ test_server_wiring: 65 → 67")

q = REPO / "tests" / "test_mcp_protocol_layer.py"
u = q.read_text(encoding="utf-8")
if "assert n == 112" in u:
    print("  test_mcp_protocol_layer: 已是 112，跳过")
else:
    assert "assert n == 110" in u, "锚点不符（test_mcp_protocol_layer）"
    u = u.replace("assert n == 110", "assert n == 112", 1)
    u = u.replace("**110** 条", "**112** 条", 1)
    u = u.replace(
        "轮 224（砌墙 W2）新增 `tool_specs_batch19.py` 的 3 个工程图轻量读数 ⇒ **107 → 110**。",
        "轮 224（砌墙 W2）新增 `tool_specs_batch19.py` 的 3 个工程图轻量读数 ⇒ **107 → 110**；\n"
        "      轮 227（砌墙 W3）新增 `tool_specs_batch20.py` 的 2 个自定义属性读取 ⇒ **110 → 112**。", 1)
    q.write_text(u, encoding="utf-8")
    print("  ✓ test_mcp_protocol_layer: 110 → 112")

#: ── 3 无人值守基线：只加一条 ─────────────────────────────────────────
bp = REPO / "tests" / "unattended_baseline.json"
d = json.loads(bp.read_text(encoding="utf-8"))
if "file_custom_property_read" in d["allowed"]:
    print("  基线: 已在，跳过")
else:
    d["allowed"].append("file_custom_property_read")
    d["allowed"] = sorted(set(d["allowed"]))
    bp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 基线只加 file_custom_property_read（schema 与 denied_count 一字未动）")

#: ── 4 capabilities.yaml ─────────────────────────────────────────────
cP = REPO / "capabilities.yaml"
cap = json.loads(cP.read_text(encoding="utf-8"))
if any(c.get("id") == "file_custom_property_read" for c in cap["capabilities"]):
    print("  能力清单: 已在，跳过")
else:
    cap["capabilities"].append({
        "id": "file_custom_property_read",
        "label": "文件自定义属性读取（值 / 类型 / 全部清单）",
        "level": "verified",
        "backends": ["solidworks-com-pywin32"],
        "verified_versions": ["2026"],
        "dependencies": ["solidworks"],
        "limitations": [
            "★ 读的是**文件级**自定义属性（默认配置）。★ 按配置读的路径**未真机验证**（需多配置文档）",
            "★ editable（IsCustomPropertyEditable）**实测没读到** ⇒ 结果里如实留 null，不假称可读",
            "不写属性 —— 写由上游 solidworks_set_custom_properties 承担",
            "★ **不用 Get2..Get6**：它们带 by-ref out，pywin32 下报类型不匹配"
            "（-2147352571）；只用单返回值的 Get(name) ⇒ 见 known-facts 161",
            "PDM 那一族（引用文档等）不在本能力内 —— sw_pdm 需 PDM 许可证",
        ],
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "evidence": [
            "python tools/capture_custom_property_evidence.py（真机，2026-10-01 轮 227 / 砌墙 W3："
            "新建零件 ⇒ Add3 写一个属性（count 28→29）⇒ **读回写入值** ⇒ 读全部（count_read 29 "
            "== count_reported 29）⇒ 2 个负例，verdict: pass，证据落 "
            "output/custom-property-evidence.json）",
            "python tools/probe_custom_property_reads.py（真机探针：定下「管理器必须当方法调用」与"
            "「by-ref out 不通、只能用单返回值的 Get」；证据 output/custom-property-reads.json）",
            "pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 67 / 协议层 112）",
        ],
        "source": "original",
        "source_evidence": "scripts/sw_custom_property.py（照官方 ICustomPropertyManager.Get/GetNames/"
                           "Count/GetType2 与 IModelDocExtension.CustomPropertyManager 新写）",
    })
    cP.write_text(json.dumps(cap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 能力清单已加 file_custom_property_read")

d2 = json.loads(cP.read_text(encoding="utf-8"))
print("  能力条目: %d" % len(d2["capabilities"]))
print("  level 分布:", dict(Counter(c.get("level") for c in d2["capabilities"])))
