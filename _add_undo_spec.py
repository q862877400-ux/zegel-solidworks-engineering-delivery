import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch52.py")
t = p.read_text(encoding="utf-8")

NEW = '''

# ── objective② / 四家缺口 `undo`：**撤销（`IModelDoc2.EditUndo2`）** ─────────────────────
# ★★★★ 2026-10-03（轮 395）真机（`output/undo-evidence.json`）**PASS**：
#   · ★ 前置 `凸台-拉伸1` ⇒ 特征树 **7**；★ 负例 `steps = 0` ⇒ **显式拒绝**
#   · ★★ `undo_report(doc, 1)` ⇒ **特征树 7 → 6** · `undone: true` ·
#     **`removed_features: ["凸台-拉伸1"]`**（★ 指名撤掉了哪个）✓
# ★★ **对应四家缺口名 `undo`**（★ objective② 三层证据判定的真缺 —— 事实 311）。
# ★★ **为什么它对自动化 agent 有用**：★ 我们的工具会**改模型**；★ 改错时**没有撤销就只能重来**。
# ⚠ **调用纪律**：★ `EditUndo2` 撤的是**会话里的动作**、**不区分是不是我们做的** ⇒
#   ★ **只在我们自己的改动之后调用**。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   mcp-server/tool_specs_batch52.py —— 追加本声明
# 定位:   把 `sw_session.undo_report` 挂成 MCP 工具。
# 官方签名依据: `C:\\swapi\\types\\IModelDoc2\\EditUndo2.md`（★ `void EditUndo2(int Steps)` ·
#   反射 arity **1**）· `EditUndo`（★ **Obsolete**）· `SketchUndo()`（★ 零参）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────

_SPEC_UNDO = ToolSpec(
    name="solidworks_undo",
    title="Undo Actions",
    module="sw_session",
    function="undo_report",
    inject="model",
    params=[
        Param("steps", int, default=1,
              description="要撤的动作数（★ 必须 ≥ 1；★ 它**不通**单位，只是个数）"),
    ],
    doc="★ **撤销** —— 走 `IModelDoc2.EditUndo2`（官方 **1 参** · ★★ **返回 `void`**）。"
        "★★ 判据（规则 6）：**特征树真的退回了**（真机：7 → 6 · 撤掉 `凸台-拉伸1`）。"
        "★ 负例 `steps = 0` ⇒ 显式拒绝。"
        "⚠ **调用纪律**：★ 它撤的是**会话里的动作**、**不区分是不是我们做的** ⇒ "
        "★ **只在我们自己的改动之后调用**（★ 例如"建完发现参数错 ⇒ 撤掉重来"）。",
)

SPECS_BATCH52 = SPECS_BATCH52 + [_SPEC_UNDO]
'''

if "solidworks_undo" not in t:
    p.write_text(t.rstrip() + NEW, encoding="utf-8")
    print("  已加 solidworks_undo")
try:
    compile(p.read_text(encoding="utf-8"), str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **错 L%s**: %s" % (e.lineno, str(e.msg)[:80]))
