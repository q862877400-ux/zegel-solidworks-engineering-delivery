"""Spec Kit `141`（仿真研究族）收工的机械步骤（★ 只做加法；幂等）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（收工脚本，工作区仓库）
# 文件:   D:\\AI\\SW\\_s141_finish.py
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
if "assert len(all_specs()) == 86" in t:
    print("  test_server_wiring: 已是 86，跳过")
else:
    assert "assert len(all_specs()) == 83" in t, "锚点不符"
    t = t.replace("assert len(all_specs()) == 83", "assert len(all_specs()) == 86", 1)
    t = t.replace('"""**二十批**合计 **83** 条', '"""**二十一批**合计 **86** 条', 1)
    t = t.replace(
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**',
        "    ★ **轮 239（24h 计划 段 1.1 / Spec Kit `141`）新增 `tool_specs_batch27.py`（3 条）⇒ 86** ——\n"
        "    **仿真研究族**（建 / 取 / 列）。★★ **补 W7 的硬前置**：此前 `study_name` 只能引用\n"
        "    **已存在**的研究（用户得先手动在 SolidWorks 里建一个）。\n"
        "    ★ 3 个薄函数包既有四个（都回 COM 对象 ⇒ MCP 回不了）⇒ 只回**可 JSON 化**的东西。\n"
        "    ★★ 本批还加了**参数绑定门禁**（`scripts/check_param_binding.py`）—— 因为本批与 W7\n"
        "    **两次**都漏写 `param_alias` 导致真机 `TypeError`：★「记下来」不等于「下次不犯」。\n"
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**', 1)
    p.write_text(t, encoding="utf-8")
    print("  ✓ test_server_wiring: 83 → 86")

q = REPO / "tests" / "test_mcp_protocol_layer.py"
u = q.read_text(encoding="utf-8")
if "assert n == 131" in u:
    print("  test_mcp_protocol_layer: 已是 131，跳过")
else:
    assert "assert n == 128" in u, "锚点不符"
    u = u.replace("assert n == 128", "assert n == 131", 1)
    u = u.replace("**128** 条", "**131** 条", 1)
    u = u.replace(
        "轮 238（砌墙 W7）新增 `tool_specs_batch26.py` 的 2 个仿真载荷 ⇒ **126 → 128**。",
        "轮 238（砌墙 W7）新增 `tool_specs_batch26.py` 的 2 个仿真载荷 ⇒ **126 → 128**；\n"
        "      轮 239（24h 段 1.1）新增 `tool_specs_batch27.py` 的 3 个仿真研究 ⇒ **128 → 131**。", 1)
    q.write_text(u, encoding="utf-8")
    print("  ✓ test_mcp_protocol_layer: 128 → 131")

bp = REPO / "tests" / "unattended_baseline.json"
d = json.loads(bp.read_text(encoding="utf-8"))
if "simulation_study_create" in d["allowed"]:
    print("  基线: 已在，跳过")
else:
    d["allowed"].append("simulation_study_create")
    d["allowed"] = sorted(set(d["allowed"]))
    bp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 基线只加 simulation_study_create（schema 与 denied_count 一字未动）")

cP = REPO / "capabilities.yaml"
cap = json.loads(cP.read_text(encoding="utf-8"))
if any(c.get("id") == "simulation_study_create" for c in cap["capabilities"]):
    print("  能力清单: 已在，跳过")
else:
    cap["capabilities"].append({
        "id": "simulation_study_create",
        "label": "仿真研究族（新建 / 按名取 / 列出）—— 补 W7 的硬前置",
        "level": "verified",
        "backends": ["solidworks-com-pywin32"],
        "verified_versions": ["2026"],
        "dependencies": ["solidworks", "simulation-addin"],
        "limitations": [
            "★ **只支持静力学研究**（`study_type = static`）—— ★ 其它研究类型**未真机验证**"
            "⇒ 本批**不暴露** `study_type` / `mesh_type` 开关（★ 比「暴露一个没验过的开关」诚实）",
            "★★ **`entry_name` 是「是否走了降级入口」的唯一证据**：实测值 = `CreateNewStudy3`"
            "（★ 最高版本入口，**非降级**）；★ **空字符串 ⇒ 三个入口都没命中 ⇒ 没建成**",
            "★ 能力层既有四个函数**都回 COM 对象**（`create_static_study` 回三元组含对象、"
            "`iter_studies` yield `(index, study)` 元组、`get_study_by_name` 回对象或 `None`）"
            "⇒ MCP 回不了对象 ⇒ ★ 本批**加了三个薄函数**把它们翻成**可 JSON 化**的字典"
            "（既有四个**一行未改**）",
            "★ 已实测：`get_study_by_name` 在**找不到时返回 `None`**（**不抛错**）"
            "⇒ 对外用**显式的 `found` 字段**，避免把「没有」当成「有」",
            "⚠ **重名研究的行为未验**：能力层**不检查重名** —— 若同名研究已存在，由 SolidWorks 决定，"
            "★ 用 `solidworks_simulation_list_studies` 回读确认",
            "★ 依赖 Simulation 加载项（首次调用自动 `LoadAddIn`，走注册表里的真路径）",
        ],
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "evidence": [
            "python tools/capture_simulation_study_evidence.py（真机，2026-10-01 轮 239 / 24h 段 1.1："
            "★ **走工具真实路径** ⇒ 建研究 `DSH-141` 成功，★ `entry_name` = **CreateNewStudy3**、"
            "`error_code` = 0；★ **建完回读**名字逐字相等；★ **列出** count 1 且含该名字；"
            "★ **负例**：取不存在的名字 ⇒ `found` 为 **False**。verdict: pass，"
            "证据落 output/simulation-study-evidence.json）",
            "python tools/probe_simulation_study_shapes.py（真机探针：定死三个真形状 —— "
            "`create_static_study` 回 **tuple(3)**、`iter_studies` yield **`(index, study)`**、"
            "`get_study_by_name` 找不到**回 None 不抛错**）",
            "python scripts/check_param_binding.py（★ 本批新增的门禁：声明参数必须『有归属』；"
            "★ **已用负例证明它抓得住** —— 临时摘掉 `param_alias` ⇒ exit 1 并精确指出是哪个参数）",
            "pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 86 / 协议层 131）",
        ],
        "source": "original",
        "source_evidence": "scripts/sw_simulation.py 的 create_study_report / list_studies / find_study"
                           "（照官方 ICWStudyManager.CreateNewStudy3/2/1 与 ICWModelDoc.StudyManager）",
    })
    cP.write_text(json.dumps(cap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 能力清单已加 simulation_study_create")

d2 = json.loads(cP.read_text(encoding="utf-8"))
print("  能力条目: %d" % len(d2["capabilities"]))
print("  level 分布:", dict(Counter(c.get("level") for c in d2["capabilities"])))
