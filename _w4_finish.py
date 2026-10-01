"""W4 收工的机械步骤（★ 每步只做加法、且只改该改的那一处）。

1. test_server_wiring 67 → 72
2. test_mcp_protocol_layer 112 → 117
3. 无人值守基线：★ **只加** `sketch_build` 一条（不重生成）
4. capabilities.yaml：加 `sketch_build`

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（收工脚本，工作区仓库）
# 文件:   D:\\AI\\SW\\_w4_finish.py
# 定位:   砌墙 W4 的机械收尾；每处断言锚点，防误改；幂等。
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
if "assert len(all_specs()) == 72" in t:
    print("  test_server_wiring: 已是 72，跳过")
else:
    assert "assert len(all_specs()) == 67" in t, "锚点不符"
    t = t.replace("assert len(all_specs()) == 67", "assert len(all_specs()) == 72", 1)
    t = t.replace('"""**十四批**合计 **67** 条', '"""**十五批**合计 **72** 条', 1)
    t = t.replace(
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**',
        "    ★ **轮 229（Spec Kit `135`，砌墙 W4）新增 `tool_specs_batch21.py`（5 条）⇒ 72** ——\n"
        "    **建草图 + 画几何**。★ 这批补的是**最底层的短板**：此前 MCP 里连草图都建不了，\n"
        "    以致**已挂的** `revolve_boss` / `create_hole_feature` / 钣金 `base_flange` **全都用不了**\n"
        "    （它们都要一个已存在的草图）。★ 参数用**语义名 + _mm**（规则 2 合规 + 规则 3 的豁免路径）。\n"
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**', 1)
    p.write_text(t, encoding="utf-8")
    print("  ✓ test_server_wiring: 67 → 72")

q = REPO / "tests" / "test_mcp_protocol_layer.py"
u = q.read_text(encoding="utf-8")
if "assert n == 117" in u:
    print("  test_mcp_protocol_layer: 已是 117，跳过")
else:
    assert "assert n == 112" in u, "锚点不符"
    u = u.replace("assert n == 112", "assert n == 117", 1)
    u = u.replace("**112** 条", "**117** 条", 1)
    u = u.replace(
        "轮 227（砌墙 W3）新增 `tool_specs_batch20.py` 的 2 个自定义属性读取 ⇒ **110 → 112**。",
        "轮 227（砌墙 W3）新增 `tool_specs_batch20.py` 的 2 个自定义属性读取 ⇒ **110 → 112**；\n"
        "      轮 229（砌墙 W4）新增 `tool_specs_batch21.py` 的 5 个建草图/画几何 ⇒ **112 → 117**。", 1)
    q.write_text(u, encoding="utf-8")
    print("  ✓ test_mcp_protocol_layer: 112 → 117")

bp = REPO / "tests" / "unattended_baseline.json"
d = json.loads(bp.read_text(encoding="utf-8"))
if "sketch_build" in d["allowed"]:
    print("  基线: 已在，跳过")
else:
    d["allowed"].append("sketch_build")
    d["allowed"] = sorted(set(d["allowed"]))
    bp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 基线只加 sketch_build（schema 与 denied_count 一字未动）")

cP = REPO / "capabilities.yaml"
cap = json.loads(cP.read_text(encoding="utf-8"))
if any(c.get("id") == "sketch_build" for c in cap["capabilities"]):
    print("  能力清单: 已在，跳过")
else:
    cap["capabilities"].append({
        "id": "sketch_build",
        "label": "建草图与画基本几何（线 / 圆 / 矩形）",
        "level": "verified",
        "backends": ["solidworks-com-pywin32"],
        "verified_versions": ["2026"],
        "dependencies": ["solidworks"],
        "limitations": [
            "★ 本批只覆盖 5 个：进入/退出草图 + 线/圆/矩形（对角两点）。"
            "多边形 / 槽 / 弧 / 椭圆 / 样条 / 自动尺寸**未挂**（能力层已有，留后续批次）",
            "★★ **已知静默行为**：不先调用 `solidworks_sketch_start` 就画几何 ⇒ **不抛错（静默）** ——"
            "真机实测（output/sketch-build-evidence.json 的 `record_draw_without_start`）。"
            "⇒ 调用方必须先 start；★ 目前**没有机器守卫**，靠工具说明约束",
            "★ 画几何**必须给草图平面内的坐标**（规则 3 的豁免路径）⇒ 参数用语义名 + `_mm`",
            "★ 只在**前视基准面**上真机验证过；上视/右视基准面与中文面名**未逐项验证**",
        ],
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "evidence": [
            "python tools/capture_sketch_build_evidence.py（真机，2026-10-01 轮 229 / 砌墙 W4："
            "新建零件 → start（前视）→ 画线 → 画圆 → 画矩形 → end，"
            "★ **并用 W1 的只读工具回读断言**：线后 count_lines=1 · 圆后 count_arcs=1 · "
            "矩形后 count_lines=5（1 线 + 4 边）· **关掉草图后仍读到 5**；"
            "另记两条：不 start 就画线 = 静默 · 坏基准面名 = ValueError。"
            "verdict: pass，证据落 output/sketch-build-evidence.json）",
            "python tools/capture_sketch_evidence.py（W1，只读批；与本批构成**读写配对**）",
            "pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 72 / 协议层 117）",
        ],
        "source": "original",
        "source_evidence": "scripts/sw_part.py 的 start_sketch / end_sketch / sketch_line / "
                           "sketch_circle / sketch_corner_rectangle（照官方 ISketchManager.Create* 一族）",
    })
    cP.write_text(json.dumps(cap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 能力清单已加 sketch_build")

d2 = json.loads(cP.read_text(encoding="utf-8"))
print("  能力条目: %d" % len(d2["capabilities"]))
print("  level 分布:", dict(Counter(c.get("level") for c in d2["capabilities"])))
