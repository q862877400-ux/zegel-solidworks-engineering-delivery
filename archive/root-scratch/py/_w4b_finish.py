"""W4 续（拉伸族）收工的机械步骤（★ 只做加法、只改该改的那一处；幂等）。

1. test_server_wiring 72 → 75
2. test_mcp_protocol_layer 117 → 120
3. 无人值守基线：★ **只加** `feature_build_extrude` 一条（不重生成）
4. capabilities.yaml：加 `feature_build_extrude`

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（收工脚本，工作区仓库）
# 文件:   D:\\AI\\SW\\_w4b_finish.py
# 定位:   砌墙 W4 续的机械收尾；每处断言锚点，防误改。
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
if "assert len(all_specs()) == 75" in t:
    print("  test_server_wiring: 已是 75，跳过")
else:
    assert "assert len(all_specs()) == 72" in t, "锚点不符"
    t = t.replace("assert len(all_specs()) == 72", "assert len(all_specs()) == 75", 1)
    t = t.replace('"""**十五批**合计 **72** 条', '"""**十六批**合计 **75** 条', 1)
    t = t.replace(
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**',
        "    ★ **轮 230（Spec Kit `136`，砌墙 W4 续）新增 `tool_specs_batch22.py`（3 条）⇒ 75** ——\n"
        "    **拉伸族**（凸台 / 切除 / 中面）。★ 这是**第一批能建出实体**的工具：\n"
        "    与 W4 的 `batch21`（建草图 + 画几何）合起来，本仓库第一次具备**完整建模最小闭环**。\n"
        "    ★ 验证是**数字断言**：矩形 40×20 拉伸 10 ⇒ 包围盒 size **40×20×10**；\n"
        "    中面拉伸总深 10 ⇒ min/max **±5**（两侧对称被数值证实）。\n"
        '    **本测试是"钉死数量"的守卫，加批次必须同时改这里**', 1)
    p.write_text(t, encoding="utf-8")
    print("  ✓ test_server_wiring: 72 → 75")

q = REPO / "tests" / "test_mcp_protocol_layer.py"
u = q.read_text(encoding="utf-8")
if "assert n == 120" in u:
    print("  test_mcp_protocol_layer: 已是 120，跳过")
else:
    assert "assert n == 117" in u, "锚点不符"
    u = u.replace("assert n == 117", "assert n == 120", 1)
    u = u.replace("**117** 条", "**120** 条", 1)
    u = u.replace(
        "轮 229（砌墙 W4）新增 `tool_specs_batch21.py` 的 5 个建草图/画几何 ⇒ **112 → 117**。",
        "轮 229（砌墙 W4）新增 `tool_specs_batch21.py` 的 5 个建草图/画几何 ⇒ **112 → 117**；\n"
        "      轮 230（砌墙 W4 续）新增 `tool_specs_batch22.py` 的 3 个拉伸 ⇒ **117 → 120**。", 1)
    q.write_text(u, encoding="utf-8")
    print("  ✓ test_mcp_protocol_layer: 117 → 120")

bp = REPO / "tests" / "unattended_baseline.json"
d = json.loads(bp.read_text(encoding="utf-8"))
if "feature_build_extrude" in d["allowed"]:
    print("  基线: 已在，跳过")
else:
    d["allowed"].append("feature_build_extrude")
    d["allowed"] = sorted(set(d["allowed"]))
    bp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 基线只加 feature_build_extrude（schema 与 denied_count 一字未动）")

cP = REPO / "capabilities.yaml"
cap = json.loads(cP.read_text(encoding="utf-8"))
if any(c.get("id") == "feature_build_extrude" for c in cap["capabilities"]):
    print("  能力清单: 已在，跳过")
else:
    cap["capabilities"].append({
        "id": "feature_build_extrude",
        "label": "拉伸族（凸台 / 切除 / 中面）—— 把草图变成实体",
        "level": "verified",
        "backends": ["solidworks-com-pywin32"],
        "verified_versions": ["2026"],
        "dependencies": ["solidworks"],
        "limitations": [
            "★ 本批只有 3 个（拉伸族）⇒ **倒角 / 圆角不在内**：它们需要**选择边**"
            "（规则 3 的声明式 selection 包装层），**单独一批做**",
            "★ 三个都**需要一个已存在的草图** ⇒ 先用 `solidworks_sketch_*`（batch21）建草图；"
            "找不到草图会抛 ValueError（错误信息会列出它试过的四条路）",
            "★ `depth_mm = 0` 表示**完全贯穿**（切除）；`extrude_midplane` 的参数是**总深**，"
            "每侧为一半",
            "★ 未覆盖：拔模角 / 薄壁 / 双向 / 到面等 `FeatureExtrusion3` 的其余参数"
            "（能力层只暴露了 depth 一族）",
            "★ 只在**前视基准面**上真机验证过",
        ],
        "allowed_modes": ["interactive", "reviewed", "unattended"],
        "evidence": [
            "python tools/capture_feature_build_evidence.py（真机，2026-10-01 轮 230 / 砌墙 W4 续："
            "新建零件 → batch21 建草图（矩形 40×20）→ extrude_boss(10) ⇒ ★ **包围盒 size "
            "[40,20,10]**；再建圆草图 → extrude_cut(0=完全贯穿) ⇒ 特征树 19→21；"
            "另一新零件 → extrude_midplane(总深 10) ⇒ size [40,20,10] 且 min/max **±5**（两侧对称）；"
            "负例：不存在的草图名 ⇒ ValueError。verdict: pass，证据落 output/feature-build-evidence.json）",
            "python tools/capture_sketch_build_evidence.py（batch21；与本批合起来构成**建模最小闭环**）",
            "pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 75 / 协议层 120）",
        ],
        "source": "original",
        "source_evidence": "scripts/sw_part.py 的 extrude_boss / extrude_cut / extrude_midplane"
                           "（照官方 IFeatureManager.FeatureExtrusion3 的 23 参数与 FeatureCut4）",
    })
    cP.write_text(json.dumps(cap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ 能力清单已加 feature_build_extrude")

d2 = json.loads(cP.read_text(encoding="utf-8"))
print("  能力条目: %d" % len(d2["capabilities"]))
print("  level 分布:", dict(Counter(c.get("level") for c in d2["capabilities"])))
