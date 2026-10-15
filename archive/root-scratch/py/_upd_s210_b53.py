"""★ 一次性：把 B5-3 的进展写进 goal-bar 与 tasks。"""
from pathlib import Path

ROOT = Path(r"D:\AI\SW")

# ── tasks ────────────────────────────────────────────────────────────────
t = ROOT / "specs/210-declarative-effects/tasks.md"
lines = t.read_text(encoding="utf-8").splitlines()
out, done, i = [], False, 0
while i < len(lines):
    if lines[i].startswith("- [ ] **B5-3**"):
        out += [
            "- [x] **B5-3** `copy-in / run / copy-out`（**已交付** `scripts/sw_sandbox.py` + "
            "`open_document` 咽喉点 + 护栏 `_child_env`/`collect_sandbox_outputs`）",
            "      ★★ **判据（可跑的命令，已真机验）**：护栏里 `MODE=enforce` ⇒ 沙盒外的件 "
            "`materialized=True`、**打开的路径在沙盒内**、**原件仍在**、沙盒里确有副本、copy-out 进 `runs/<id>/results` ✓",
            "      ★★★ 并**当场抓到一个会重演原事故的设计错**：我第一版把**模型素材库**列进只读豁免 ⇒ "
            "不复制 ⇒ ★ 那正是当初「产物写进用户目录」的成因 ✗ ⇒ 已收窄为**只豁免纯文档源**，并加回归钉 ✓",
        ]
        done = True
        i += 1
        while i < len(lines) and not lines[i].startswith("- [ ] "):
            i += 1
        continue
    out.append(lines[i]); i += 1
assert done, "没找到 B5-3 那一格"
t.write_text("\n".join(out) + "\n", encoding="utf-8")
print("tasks B5-3 已勾:", done)

# ── goal-bar ─────────────────────────────────────────────────────────────
g = ROOT / "specs/210-declarative-effects/goal-bar.md"
s = g.read_text(encoding="utf-8")
s = s.replace("阶段：**B5 进行中** —— B5-1 · B5-2 · **B5-2b 全部已交付**；下一步 = **B5-3 `copy-in / run / copy-out`**",
              "阶段：**B5 进行中** —— B5-1 · B5-2 · B5-2b · **B5-3 全部已交付**；"
              "下一步 = **B5-4 输出根独立配置 + 产品模式子目录**（★ B5-3 已把它做了一半）")

NEW = [
    "## 下一个动作（只写一条，免得没人知道该恢复哪个）",
    "",
    "★ **B5-3 已交付**（`copy-in / run / copy-out`）：",
    "- 新 `scripts/sw_sandbox.py`：`resolve_input`（**copy-in**）· `collect_outputs`（**copy-out**）·",
    "  `sandbox_root` / `output_root`（**带 run id**）· `sweep` ✓",
    "- 接在**咽喉点** `scripts/sw_connect.py` 的 `open_document` 上（★ 会打开文档的调用几乎都经过它）✓",
    "- ★★ 开关放在**护栏**：`_child_env()` 给**探针子进程**设 `SW_SANDBOX_MODE=enforce`，",
    "  跑完 `collect_sandbox_outputs()` 把产物拷到输出根 ✓",
    "  ★ 于是**真机跑被保护**，★ 而离线调用与单测**不受影响**（它们默认 `passthrough`）✓",
    "",
    "★★ **判据（可跑的命令，真机已验）**：护栏里跑一次 ⇒ `MODE=enforce` · 沙盒外的件",
    "  **`materialized=True`** · **打开的路径在沙盒内** · **原件仍在** · 沙盒里确有副本 ·",
    "  copy-out 收进 `output/runs/<run-id>/results` ✓",
    "",
    "★★★ **本轮当场抓到一个会重演原事故的设计错**（★ 只有真的跑一遍才会暴露）：",
    "  我第一版把**模型素材库**列进「只读豁免」⇒ 不复制 ⇒ ★★ 而当初出的事故**正是**",
    "  「对素材库里的件直接开分析 ⇒ 分析产物**落在那个目录里**」✗",
    "  ⇒ ★ 已收窄为**只豁免 `C:\\swapi` 那种纯文档源**（SolidWorks 永远不开它、更不会往旁边写结果）✓",
    "  ⇒ ★ 并加**回归钉**：模型素材库**不许**进豁免名单 ✓",
    "",
    "**B5-4 · 输出根独立配置 + 产品模式的落点**：★ B5-3 已把 `output_root()`（**带 run id**、",
    "  可用 `SW_OUTPUT_ROOT` 覆盖）做出来了 ⇒ 本格剩下的是**产品模式**那一半：",
    "  产品模式（用户让智能体改他的模型）下，★ **分析类产物进一个明确命名的子目录**，",
    "  并在**工具返回值里报出实际路径**（★ 业主已拍板）—— ★ 不再静默落在零件旁边 ✓",
    "  判据：★ 一条测试证明「返回值里有产物路径」；★ 一条证明「产品模式也走子目录」 ✓",
    "",
]
lines_g, i2, hit = s.splitlines(), 0, False
out2 = []
while i2 < len(lines_g):
    if lines_g[i2].startswith("## 下一个动作"):
        hit = True
        out2 += NEW
        i2 += 1
        while i2 < len(lines_g) and not lines_g[i2].startswith("## "):
            i2 += 1
        continue
    out2.append(lines_g[i2]); i2 += 1
assert hit, "没找到「下一个动作」段"
s2 = "\n".join(out2) + "\n"
s2 = s2.replace("- **B5 隔离与预检**：进行中（B5-1 · B5-2 · **B5-2b 完成**；B5-3 / B5-4 / B5-5 未开始）",
                "- **B5 隔离与预检**：进行中（B5-1 · B5-2 · B5-2b · **B5-3 完成**；B5-4 / B5-5 未开始）")
g.write_text(s2, encoding="utf-8")
print("goal-bar 已更新:", "B5-3 已交付" in s2)
