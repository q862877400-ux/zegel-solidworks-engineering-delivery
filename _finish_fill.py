import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

# ── ① MCP 工具声明 ────────────────────────────────────────────────────
p = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch45.py")
t = p.read_text(encoding="utf-8")
NEW_SPEC = '''

# ── 24h 计划 段 6 续（objective② 的第二个真缺）：**填充曲面** ──────────────────────────
# ★★★★★ 2026-10-02（轮 388）真机（`output/fill-surface-evidence.json`）**PASS**：
#   · ★ 前置 `曲面-拉伸1`（树 6→7）；★ 负例 `resolutions = 9` ⇒ **显式拒绝**
#   · ★★ `insert_fill_surface_report(doc, 2)` ⇒ **新特征 `曲面填充1`** · 选 4 条边 · 树 **7→8** ✓
# ★★ **两个关键细节**（★ 真机撞出来的）：★ 边界边必须用 `SelectByID2` 带 **mark = 1**
#   （★ `Select4` **没有 mark 参数** —— 事实 32；★ 传 mark = 4 会**静默失败**：回 true 而计数 0 —— 事实 8）·
#   ★ `Options = 1`（`swOptimizeSurface`，★ 与官方示例一致）。
# ★★ **对应四家缺口名 `filled_surface`**（★ objective② 重核后确认的真缺 —— 事实 302/304）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch45.py —— 追加本声明
# 定位:   把 `sw_surface_features.insert_fill_surface_report` 挂成 MCP 工具。
# 官方签名依据: `C:\\swapi\\types\\IFeatureManager\\InsertFillSurface2.md`（**6 参** · mark 表 ·
#   `Resolutions` = 1/2/3）· `C:\\swapi\\enums\\swFeatureFillSurfaceOptions_e.md`（★ Bitmask，
#   `swOptimizeSurface = 1`，★ md 表与反射两源一致）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────

_SPEC_FILL = ToolSpec(
    name="solidworks_surface_fill",
    title="Fill Surface Feature",
    module="sw_surface_features",
    function="insert_fill_surface_report",
    inject="model",
    params=[
        Param("resolutions", int, default=2,
              description="分辨率 **1 / 2 / 3**（★ 越大质量越好，官方 Remarks）"),
        Param("options", int, default=1,
              description="`swFeatureFillSurfaceOptions_e` 的 Bitmask；★ 默认 1（`swOptimizeSurface`）"),
        Param("boundary_z", float, default=None,
              description="要填的那一圈边所在的 z（★ **单位是米**）；留空 = 自动取最高那一圈"),
    ],
    doc="★ **填充曲面** —— 走 `IFeatureManager.InsertFillSurface2`（官方 **6 参**）。"
        "★★ 判据（规则 6）：**回 `Feature` 非 None** **且** **特征树增量非空**。"
        "★ 真机证据：建 `曲面填充1`（树 7→8）· 负例 `resolutions = 9` ⇒ 显式拒绝。"
        "★★ **边界边按中点 + `mark = 1` 选**（★ 官方 Remarks；`Select4` 没有 mark 参数 —— 事实 32；"
        "传 mark = 4 会静默失败：回 true 而计数 0 —— 事实 8）。"
        "⚠ 坐标单位是**米**（★ `boundary_z` 照此）。",
)

SPECS_BATCH45 = SPECS_BATCH45 + [_SPEC_FILL]
'''
if "solidworks_surface_fill" not in t:
    p.write_text(t.rstrip() + NEW_SPEC, encoding="utf-8")
    print("  (1) 已加 solidworks_surface_fill")
try:
    compile(p.read_text(encoding="utf-8"), str(p), "exec")
    print("      ok-compile")
except SyntaxError as e:
    print("      **错 L%s**: %s" % (e.lineno, str(e.msg)[:70]))

# ── ② 判定表：filled_surface 真缺 ⇒ 已补 ──────────────────────────────
g = Path(r"C:\swprojects\sw-skill-fork\docs\union-gap-evidence-based.md")
gt = g.read_text(encoding="utf-8")
new_row = ("| `filled_surface` | Fill a closed boundary of edges with a new surface. | "
           "**已补**（★ 2026-10-02 轮 388 真机 **PASS**：`曲面填充1` · 树 7→8 · 选 4 边 —— "
           "边界按**中点 + mark=1** 选；★ 详见 known-facts 事实 305）|")
gt2 = re.sub(r"\|\s*`filled_surface`\s*\|[^|]*\|[^|]*\|", new_row, gt, count=1)
if gt2 != gt:
    g.write_text(gt2, encoding="utf-8")
    print("  (2) 已更新 filled_surface 行")

# ── ③ capabilities：工具 + evidence + limitations ──────────────────────
c = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(c.read_text(encoding="utf-8"))
x = next(y for y in d["capabilities"] if y["id"] == "surface_features")
tools = list(x.get("mcp_tools") or [])
if "solidworks_surface_fill" not in tools:
    tools.append("solidworks_surface_fill")
x["mcp_tools"] = tools
EV = ("python 真机（轮 388）★ **PASS** —— objective② 补的第二个真缺 `filled_surface`："
      "`scripts/sw_surface_features.py` 新增 `insert_fill_surface_report`（官方 "
      "`IFeatureManager.InsertFillSurface2`，**6 参**）。真机（走 `sw_guard`，6.47 s 无弹窗）："
      "前置 `曲面-拉伸1`（树 6→7）· 负例 `resolutions = 9` 被拒 · "
      "**`insert_fill_surface_report(doc, 2)` ⇒ 新特征 `曲面填充1` · 选 4 条边 · 树 7→8** ⇒ `verdict: pass`。"
      "★★ **真机打通的关键**：边界边必须用 `SelectByID2` 带 **mark = 1**（官方 Remarks 的 Boundary curves）；"
      "★ `IEntity.Select4` **没有 mark 参数**（事实 32），而传 **mark = 4** 会**静默失败**"
      "（回 true 而 `GetSelectedObjectCount2(-1)` = 0 —— 事实 8）。证据 output/fill-surface-evidence.json。")
ev = list(x.get("evidence") or [])
if not any("filled_surface" in s for s in ev):
    ev.insert(0, EV)
x["evidence"] = ev
LIM = ("⚠ 本入口只验了 `resolutions = 2` · `options = 1`（`swOptimizeSurface`）；"
       "★ `resolutions` 的另两档（1/3）与别的 Bitmask 位**未真机验**。"
       "⚠ ★ **坐标单位是米**（`boundary_z` 照此）—— 真机实测 `GetPoint` 的 z 是 `0.03` 而拉伸是 30 mm。"
       "⚠ 边界取法是「**同一 z 上的那一圈边**」这一种；★ 更复杂的缺口（示例用**偏移双圆**）未验。")
lim = list(x.get("limitations") or [])
if not any("swOptimizeSurface" in s for s in lim):
    lim.insert(0, LIM)
x["limitations"] = lim
c.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  (3) surface_features mcp_tools = %s · ev=%d lim=%d" % (tools, len(ev), len(lim)))
