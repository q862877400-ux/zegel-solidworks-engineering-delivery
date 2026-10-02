"""W7（仿真载荷包装层 · 护城河）收工的机械步骤（★ 只做加法；幂等）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（收工脚本，工作区仓库）
# 文件:   D:\\AI\\SW\\_w7_finish.py
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
if "assert len(all_specs()) == 83" in t:
    print("  test_server_wiring: 已是 83，跳过")
else:
    assert "assert len(all_specs()) == 81" in t, "锚点不符"
    t = t.replace("assert len(all_specs()) == 81", "assert len(all_specs()) == 83", 1)
    t = t.replace('"""**十九批**合计 **81** 条', '"""**二十批**合计 **83** 条', 1)
    t = t.replace(
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**',
        "    ★ **轮 238（Spec Kit `140`，砌墙 W7）新增 `tool_specs_batch26.py`（2 条）⇒ 83** ——\n"
        "    ★★ **仿真载荷包装层（护城河）**：夹具 / 法向力。\n"
        "    ★ 核实过：四家合计只有 **4 个**仿真工具，且**全是\"建研究/跑\"**，**没有一个挂载荷/约束**。\n"
        "    ★ 而能力层**早已包装好** ⇒ 本批即目标里那句「**有就直接挂**」。\n"
        "    ★ 包装形状是**三种机制的组合**：`inject=\"study\"` + `pre_call`（先选面）+\n"
        "    `derived_args`（补 `model`）—— ★ 既有 8 个先例已用同种组合。\n"
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**', 1)
    p.write_text(t, encoding="utf-8")
    print("  ✓ test_server_wiring: 81 → 83")

q = REPO / "tests" / "test_mcp_protocol_layer.py"
u = q.read_text(encoding="utf-8")
if "assert n == 128" in u:
    print("  test_mcp_protocol_layer: 已是 128，跳过")
else:
    assert "assert n == 126" in u, "锚点不符"
    u = u.replace("assert n == 126", "assert n == 128", 1)
    u = u.replace("**126** 条", "**128** 条", 1)
    u = u.replace(
        "轮 237（砌墙 W6）新增 `tool_specs_batch25.py` 的 3 个装配只读 ⇒ **123 → 126**。",
        "轮 237（砌墙 W6）新增 `tool_specs_batch25.py` 的 3 个装配只读 ⇒ **123 → 126**；\n"
        "      轮 238（砌墙 W7）新增 `tool_specs_batch26.py` 的 2 个仿真载荷 ⇒ **126 → 128**。", 1)
    q.write_text(u, encoding="utf-8")
    print("  ✓ test_mcp_protocol_layer: 126 → 128")

bp = REPO / "tests" / "unattended_baseline.json"
d = json.loads(bp.read_text(encoding="utf-8"))
if "simulation_loads_wiring" in d["allowed"]:
    print("  基线: 已在，跳过")
else:
    d["allowed"].append("simulation_loads_wiring")
    d["allowed"] = sorted(set(d["allowed"]))
    bp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 基线只加 simulation_loads_wiring（schema 与 denied_count 一字未动）")

cP = REPO / "capabilities.yaml"
cap = json.loads(cP.read_text(encoding="utf-8"))
if any(c.get("id") == "simulation_loads_wiring" for c in cap["capabilities"]):
    print("  能力清单: 已在，跳过")
else:
    cap["capabilities"].append({
        "id": "simulation_loads_wiring",
        "label": "★ 仿真载荷包装层（夹具 / 法向力）—— 护城河域",
        "level": "verified",
        "backends": ["solidworks-com-pywin32"],
        "verified_versions": ["2026"],
        "dependencies": ["solidworks", "simulation-addin"],
        "limitations": [
            "★★ **护城河（核实过）**：四家外部项目合计只有 **4 个**仿真工具，且**全是「建研究 / 跑」**，"
            "**没有一个挂载荷 / 约束**（`Eduardof0nt` 3 · `vespo92` 1 · `Slacker-LLC` **0** · "
            "`andrewbartels1` 2 个是**误命中**，它的 \"load\" 指 `load_part`）。"
            "★ 四家的**测试**里也**没有**仿真载荷判据。",
            "★★ **依赖 Simulation 加载项**：首次调用会自动 `LoadAddIn`（走注册表里的**真路径** "
            "`…\\SOLIDWORKS\\Simulation\\cosworks.dll`）。⚠ 「插件不在」是**假象** —— "
            "`Dispatch(\"SldWorks.Simulation\")` 报「找不到指定的模块」，而 `LoadAddIn` 传 ProgID "
            "返回 **3 = swFileNotFound**（★ 官方要求**完整路径**；**许可错才是 7**）⇒ 实测 "
            "`ensure_simulation_addin` 返回 **CDispatch**（事实 141/142）。",
            "★ 目标函数**已是包装层**（首参是 `study`，不是 raw COM 对象）；"
            "★ 本能力只补「**把选区装成官方 `DispArray`**」那一环（靠 `model=`）。",
            "⚠ **调用前必须先选好面**（`pre_call` 用声明式 `selection` 选）—— "
            "★ 且**每次施加载荷/夹具之间要清空选区**（`ClearSelection2(True)`），"
            "否则第二次回读的计数会把上一次的算进来（**本批实测踩到，判据假红**）。",
            "⚠ 只暴露了**夹具**与**法向力**两种；`sw_simulation_loads` 里另有 "
            "**28 个**载荷/连接器函数（压力 / 扭矩 / 重力 / 离心 / 轴承 / 远程载荷 / 12 种连接器等）**未挂**。",
            "⚠ 只跑通了 100×60×20 mm 单实体板 + AISI 1020 这个工况；**复杂几何与装配体未验**。",
            "⚠ **没有**「建研究」的工具 ⇒ `study_name` 只能引用**已存在**的研究"
            "（空名取第一个）—— 建研究要用能力层 `create_static_study`（未挂）。",
        ],
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "evidence": [
            "python tools/capture_simulation_loads_evidence.py（真机，2026-10-01 轮 238 / 砌墙 W7："
            "★ **走工具真实路径**（`inject`(resolve_study) + `pre_call`(选面) + `derived_args`(补 model)）"
            "⇒ 夹具「**固定-1**」· 载荷「**力-1**」· 选区计数 **1/1** · `LoadsAndRestraintsManager.Count == 2`。"
            "verdict: pass，证据落 output/simulation-loads-evidence.json）",
            "python tools/capture_simulation_evidence.py（真机，既有脚本，**能力层直调**："
            "赋材料 → 夹具 → 载荷（Count == 2）→ CreateMesh（**7,310 单元**）→ RunAnalysis（1 秒）→ "
            "**study.Results 非空、GetPlotCount == 4**（品质/应力/位移/应变）。verdict: pass）",
            "pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 83 / 协议层 128）",
        ],
        "source": "original",
        "source_evidence": "scripts/sw_simulation.py 的 apply_fixed_restraint / apply_normal_force"
                           "（照官方 ICWLoadsAndRestraintsManager.AddRestraint / AddForce）",
    })
    cP.write_text(json.dumps(cap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 能力清单已加 simulation_loads_wiring")

d2 = json.loads(cP.read_text(encoding="utf-8"))
print("  能力条目: %d" % len(d2["capabilities"]))
print("  level 分布:", dict(Counter(c.get("level") for c in d2["capabilities"])))
