"""把 `converge.md` 的两条结论落到 `capabilities.yaml`（**先验证往返逐字节相同**）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（清单收敛）
# 文件:   C:\\swprojects\\sw-skill-fork\\capabilities.yaml（内容是 JSON、扩展名是 yaml）
#         D:\\AI\\SW\\specs\\003-topology-closed-loop\\converge.md（本改动的依据）
# 定位:   轮 48 跑 Spec Kit 的 **converge** 步，抓到两条：
#         ① SC-005/FR-005「无许可失败路径」**设计有、从未实跑** ⇒ 追加一条 limitation 写明「未验」
#         ② `limitations[15]`/`[16]` 写「维持 stitched，不得升 verified」，
#            而 `level` 已是 `verified` ⇒ **自相矛盾，会误导读者**
#            ⇒ **加过期标记（不删，保留当时的真实状态）**
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ **先证明 JSON 往返逐字节相同**再改（否则格式会被整体重排，`git diff` 一片红）。
# ⚠ 按**事实 61**：跑完先看 `git diff --stat`，确认只有预期的行变化。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
CAP = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")

RAW = CAP.read_text(encoding="utf-8")
d = json.loads(RAW)

# ── ① **先验证往返逐字节相同**（不改任何东西）──────────────────────
roundtrip = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
assert roundtrip == RAW, (
    "⚠ **JSON 往返不是逐字节相同** ⇒ 停下：改了会让 git diff 整体重排。"
    "（长度 %d vs %d）" % (len(roundtrip), len(RAW))
)
print("  ✓ ① 往返逐字节相同（%d 字节）⇒ JSON 往返编辑是安全的" % len(RAW))

caps = d["capabilities"] if isinstance(d.get("capabilities"), list) else list(d["capabilities"].values())
topo = next(c for c in caps if c.get("id") == "topology_optimization")
lim = topo["limitations"]

# ── ② 给旧条目加**过期标记**（保留原文，事实 61 式：只加不删）────────
MARK15 = ("🕓 **本条已过期（2026-10-01，轮 48 标注）**：写下时的状态是「整链未跑通 ⇒ 维持 stitched」，"
          "**而该状态已改变** —— 见上方 `limitations[1]`/`[2]`：闭环真机跑通、`level` 已升 `verified`。"
          "**保留原文是因为它记录了当时的真实状态**，不是当前结论。｜ 原文：")
MARK16 = ("🕓 **本条已过期（2026-10-01，轮 48 标注）**：同上 —— 「维持 `stitched`，不得升 `verified`」"
          "是**升级之前**的结论；`level` 现为 `verified`，依据见 `limitations[1]`/`[2]`。"
          "⚠ **本条的「静态三源一致指向无公开方法」那一半仍然有效**（拓扑导出类结果至今查不到）。｜ 原文：")

n_mark = 0
for i, s in enumerate(lim):
    if s.startswith("⚠ 2026-10-01 真机首验") and not s.startswith("🕓"):
        lim[i] = MARK15 + s; n_mark += 1
    elif s.startswith("⚠ **运行期未验**") and not s.startswith("🕓"):
        lim[i] = MARK16 + s; n_mark += 1
print("  ✓ ② 已给 %d 条旧记录加过期标记（原文保留）" % n_mark)

# ── ③ 追加「无许可路径未验」（converge §三.1）────────────────────────
NEW = ("🔴 **「无许可」失败路径**设计有、从未实跑**（2026-10-01 轮 48 的 Spec Kit `converge` 步查出）**："
       "`specs/003-topology-closed-loop/spec.md` 的 **SC-005/FR-004/FR-005** 要求"
       "「无许可时脚本**非零退出**，且证据里能看出是**许可**问题」。"
       "**代码层的设计在**（`tools/capture_topology_evidence.py` 模块文档串写明「无许可 ⇒ 非零退出并写明原因」，"
       "`note` 字段同）；**清单层也记了当时的真实现象**（见本表另一条：弹「拓扑算例未获许可」、`Results` 为空、"
       "**而 `RunAnalysis` 仍返回 0**）。"
       "⚠ **但没有任何一次「在无许可状态下运行本脚本并观察其退出码与证据」的记录。**"
       "**⇒ 按铁律 5 / 停止条件 6，不把它标成「已验证」（本能力 `level: verified` 说的是**happy path** 有运行证据，"
       "失败路径是另一件事，用本条承载）。** "
       "★ **补验的前置是系统层改动**（撤掉 Simulation 许可并重启 SolidWorks）⇒ "
       "**我不自行做**（铁律 2「不动系统层」）⇒ **记为需用户配合或接受缺口**。"
       "▶ 详见 `specs/003-topology-closed-loop/converge.md` §三.1。")
if not any("「无许可」失败路径" in s for s in lim):
    lim.append(NEW)
    print("  ✓ ③ 已追加「无许可路径未验」一条")
else:
    print("  ⚠ ③ 该条已存在")

# ── ④ 写回（同样逐字节可控）──────────────────────────────────────
CAP.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
after = json.loads(CAP.read_text(encoding="utf-8"))
t2 = next(c for c in (after["capabilities"] if isinstance(after.get("capabilities"), list)
                      else after["capabilities"].values()) if c.get("id") == "topology_optimization")
print()
print("  ── 落盘核对 ──")
print("    limitations 条数: %d → %d" % (len(lim) - 1, len(t2["limitations"])))
print("    level 仍为: %r（**不动**）" % t2["level"])
print("    过期标记条数: %d（应 2）" % sum(1 for s in t2["limitations"] if s.startswith("🕓")))
print("    含「无许可」失败路径: %s" % any("「无许可」失败路径" in s for s in t2["limitations"]))
