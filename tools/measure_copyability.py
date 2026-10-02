"""量一件事：我们**已经挂出去**的工具，四家外部项目**有没有对应物**（能抄的话在哪儿）。

★ 判据（避免"名字不同就以为没有"）：
  对每个我们挂的工具，取其**动作词**，去四家的工具名里找是否有**同名或近名**的。
命中 ⇒ 抄是**可能的**（但≠划算）；未命中 ⇒ ★ **根本抄不到**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（分析工具，工作区仓库）
# 文件:   D:\\AI\\SW\\tools\\measure_copyability.py
# 定位:   回答「四家已有的工具能不能直接抄」。
# 官方依据: `tools/union-sources.json`（四家工具名的权威来源）
# 许可:   本仓库 MIT。
# ⚠ 只读；名字级匹配，**不判语义等价**。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"" + _ROOT_S + r"")
sys.path[:0] = [str(REPO / "mcp-server"), str(REPO)]
import register_capabilities as rc

u = json.loads((REPO / "tools" / "union-sources.json").read_text(encoding="utf-8"))
four = {}
for s in u["sources"]:
    owner = s.get("repo") or s.get("owner") or "?"
    four[owner] = [str(t) for t in (s.get("tools") or [])]
all_four = {t.lower() for lst in four.values() for t in lst}

#: 我们**本会话新挂**的批次（W1–W6 的产物）
OUR_BATCHES = {
    "batch18 草图只读": ["count_lines", "count_arcs", "count_segments", "is_3d"],
    "batch19 工程图轻量": ["list_sheets", "get_current_sheet", "list_views"],
    "batch20 自定义属性": ["custom_property_get", "custom_property_list"],
    "batch21 建草图": ["sketch_start", "sketch_end", "sketch_add_line",
                     "sketch_add_circle", "sketch_add_rectangle"],
    "batch22 拉伸": ["extrude_boss", "extrude_cut", "extrude_midplane"],
    "batch23 倒角圆角": ["chamfer", "fillet"],
    "batch24 质量属性": ["part_mass_properties"],
    "batch25 装配只读": ["assembly_list_components", "assembly_list_mates",
                       "assembly_check_interference"],
}

print("  四家工具名总数（去重）: %d" % len(all_four))
print()
tot = hit = 0
for batch, ops in OUR_BATCHES.items():
    rows = []
    for op in ops:
        tot += 1
        words = [w for w in re.split(r"[_\W]+", op.lower()) if len(w) > 2]
        found = [t for t in all_four if all(w in t for w in words)] if words else []
        if found:
            hit += 1
            rows.append("    ✓ %-28s ← 四家有: %s" % (op, sorted(found)[:2]))
        else:
            rows.append("    ✗ %-28s ← ★ **四家都没有**" % op)
    print("  ══ %s ══" % batch)
    for r in rows:
        print(r)
print()
print("  ★ 能「抄到名字」的: **%d / %d**" % (hit, tot))
print("  ★ **四家根本没有的**: **%d / %d**（%.0f%%）" % (tot - hit, tot, 100.0 * (tot - hit) / tot))
