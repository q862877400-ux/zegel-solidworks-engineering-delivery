"""★ 一次性：把 B5-5 的进展写进 goal-bar 与 tasks。"""
from pathlib import Path

ROOT = Path(r"D:\AI\SW")

t = ROOT / "specs/210-declarative-effects/tasks.md"
lines = t.read_text(encoding="utf-8").splitlines()
out, done, i = [], False, 0
while i < len(lines):
    if lines[i].startswith("- [ ] **B5-5**"):
        out += [
            "- [x] **B5-5** 夹具**一次性快照 + 哈希清单**（**已交付** `tools/fixtures.py` + "
            "`tools/make_fixture_library.py`）",
            "      ★★ **真机已建**：模型目录里 **9 个 CAD 件**（8 零件 + 1 装配体）一次性复制进夹具库，",
            "      **校验一致**（9 个 · 0 缺失 · 0 哈希不符 · 0 清单外多余）· 库落在**不入库**的 `output/` 下 ✓",
            "      ★ 只按扩展名收 CAD 件 ⇒ ★ **分析产物与 `.step` 被正确排除** ✓",
            "      ★★★ **最关键负例**：`fixture_path` **只在夹具库内解析、绝不去原目录取** ——",
            "      ★ 若它回退到原目录，★ 那「此后**没人再碰原目录**」（评审**收回 ACL 方案的前提**）就不成立 ✗",
            "      ★ 另三条：**哈希一变就报污染** · **同名不同哈希换名不覆盖** · **纯加法（不删清单外的文件）** ✓",
        ]
        done = True
        i += 1
        while i < len(lines) and not lines[i].startswith("- [ ] "):
            i += 1
        continue
    out.append(lines[i]); i += 1
assert done, "没找到 B5-5 那一格"
t.write_text("\n".join(out) + "\n", encoding="utf-8")
print("tasks B5-5 已勾:", done)

g = ROOT / "specs/210-declarative-effects/goal-bar.md"
s = g.read_text(encoding="utf-8")
s = s.replace("阶段：**B5 进行中** —— B5-1 · B5-2 · B5-2b · B5-3 · **B5-4 全部已交付**；"
              "下一步 = **B5-5 夹具一次性快照 + 哈希清单**",
              "阶段：★★ **B5 全部收口**（B5-1..B5-5）· **B1 收口**；下一步 = **B2 指纹与灵敏度校准**")

NEW = [
    "## 下一个动作（只写一条，免得没人知道该恢复哪个）",
    "",
    "★ **B5-5 已交付**（夹具一次性快照 + 哈希清单）：",
    "- `tools/fixtures.py`（`library_root` / `sha256_of` / `load_manifest` / `fixture_path` /",
    "  `verify` / `collect_sources` / `build`）+ `tools/make_fixture_library.py`（`--verify` / `--dry-run`）✓",
    "- ★★ **真机已建**：模型目录里 **9 个 CAD 件**一次性复制进夹具库并冻结哈希 ⇒",
    "  ★ **校验一致**（9 · 0 缺失 · 0 哈希不符 · 0 清单外多余）✓",
    "  ★ 库落在**不入库**的 `output/fixtures/`（已核 `.gitignore:120` 命中）⇒ 用户的设计件**不会进仓库** ✓",
    "- ★ 只按扩展名收 CAD 件 ⇒ ★ **分析产物（`.CWR` 等）与 `.step` 被正确排除** ✓",
    "- ★★★ **最关键负例**：★ `fixture_path` **只在夹具库内解析、绝不回退到原目录** ——",
    "  ★ 若它会回退，★ 那「此后**没人再碰原目录**」这个**评审收回 ACL 方案的前提**就不成立了 ✗",
    "- ★ 另三条负例：**哈希一变就报污染**（评审的判据：哈希一变就不算留出集）·",
    "  **同名不同哈希 ⇒ 换名不覆盖** · **纯加法（清单外文件不删）** ✓",
    "",
    "★★ **B5 到此全部收口**（B5-1 预检门禁 · B5-2 提共用助手 · B5-2b 接进护栏 · B5-3 copy-in/out ·",
    "  B5-4 输出落点 · B5-5 夹具库）✓",
    "",
    "**B2 · 指纹与灵敏度校准**（★ 下一批，★ 它是 B3 的量具）：",
    "  定义**状态指纹**（选区数 · 编辑态 · 文档修改标志 · 特征数 · 体数 · 面数 · 显示状态 ·",
    "  活动配置 · 重建状态）；★ 然后为**每一类状态**挑一个**已知会改它**的写工具做**灵敏度测试**，",
    "  ★★ **检测不到的类别** ⇒ ★ **补进指纹**，**或明写「这类写入当前不可见」**（★ 不许默认它没问题）✓",
    "  ★ 判据：★ 每一类状态都有**灵敏度证据**或**明确的「不可见」记录** ⇒ 指纹这个「量具」被校准过 ✓",
    "  ⚠ 风险：★ 指纹的每个读数都要先在**合成件**上确认它**只读**（★ 读数本身不许有副作用）✓",
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
s2 = s2.replace("- **B5 隔离与预检**：进行中（B5-1 · B5-2 · B5-2b · B5-3 · **B5-4 完成**；B5-5 未开始）",
                "- **B5 隔离与预检**：**完成**（B5-1 · B5-2 · B5-2b · B5-3 · B5-4 · B5-5）")
s2 = s2.replace("- **B2 指纹与灵敏度**：未开始", "- **B2 指纹与灵敏度**：⚪ 未开始（★ 下一步）")
g.write_text(s2, encoding="utf-8")
print("goal-bar 已更新:", "B5-5 已交付" in s2)
