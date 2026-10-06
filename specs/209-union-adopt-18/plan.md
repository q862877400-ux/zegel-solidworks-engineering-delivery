# 规格 209 · 施工计划（plan）

> ★ 判据与需求见 [spec.md](spec.md)；进度（唯一进度字段）见 [tasks.md](tasks.md)。

---

## 一 · 工法（★ 每件活照这个来，不另创）

```
① 官方页三样：签名 + `## Remarks` + `## Examples`（★ 例子给的是**调用序**，签名与 Remarks 都给不出）
   ★ 顺序：官方页 → `docs/dead-ends.md` → 该能力的 `limitations` → `docs/known-facts.md` → 动手
② 查 `docs/recon-206/pre-code-conflict-lookup.md`（★ 该成员是否在「Remarks 与示例不能同时成立」表里）
③ 写能力函数：落**已有模块**；一行 docstring 不适用（追加段），来源块紧随
   ★ 判据 MUST 写成**回读**（规则 6），★ **不许拿被调成员的返回值当唯一判据**
④ 真机探针：`python tools/sw_guard.py --timeout 900 -- python tools/probe_union_adopt_*.py`
   ★ 一件活**一格**，判据按能力分；★ 负例 MUST 有（非法参数 / 越界 / 不存在的名字）
⑤ 登记 `capabilities.yaml`：`level` + `evidence`（可复跑命令 + 产物路径）+ `limitations`（★ 含"未验"）
⑥ 工具层：`mcp-server/tool_specs_batchNN.py` + 登记进 `register_capabilities.BATCH_MODULES`
⑦ 测试：契约（注册得到 / 目标函数解析得到 / 必填形参全声明）+ ★ **裁决书点名的那条硬约束要有回归测试**
⑧ 收尾链：`pwsh -File tools/round_chain.ps1 -Tests tests/<本批>.py`
⑨ 提交：`git reset -q` → 只 add 自己的路径 → `python tools/commit_mine.py -m <信息文件> <路径…>`
```

---

## 二 · 分批与顺序（★ 顺序不是偏好，是依赖）

| 批 | 为什么这个顺序 | 判据形态 |
|---|---|---|
| **B1** | 零参或普通 COM、无指针/无 `AccessSelections`（事实 47 无关）；落点都是**已有模块**；判据可写成回读 | 回读状态 / 回读属性 / 回读清单 |
| **B2** | 官方**没给 mark** 或**两家结论矛盾** ⇒ **必须先真机定出可建形态**才能写 `verified` | ★ 先"定前置"再"判建成" |
| **B3** | 「**读属性读不到**」是**独立风险**（事实 3x：`ActiveView.Name/Type` 报 `unknown.X`）⇒ 先小验证再落 | 欧拉公式 `V−E+F=2`（★ 不需新 API） |
| **B4** | 余下 5 条：★ 211 要**先解决弹窗**（`swCommands_StopMacro` 官方逐字会弹 Save As）；173/181/155/205 是普通 COM 但各有各的**前置表** | 各自定 |

---

## 三 · 三条**横向纪律**（★ 裁决书 §九 采纳为纪律，本规格照办）

1. ★★ **绝不能跨条复制映射表** —— 本批三条 mark 表**互不相同**：`155 Fold=0/1/4` ·
   `175 BlankSketch 只有 0` · `173 Hem 官方示例压根无选区` ⇒ **复制即错** ✓
2. ★★ **别家"写成员名"的幻觉是跨条高频的**（dp8 片 3/8）⇒ 沿铁律 4：
   **别家的名只当"该做哪个操作"的路标**，实现必须从官方重推 ✓
3. ★★ **「别家的实现本身与官方文档冲突，抄进来即负债」** —— 实例：`146` 给 `FeatureExtrusion3`
   传 **22 实参 vs 官方 23** · `160` 用已 **Obsolete 两代**的 `IModelDoc2.SaveAs2` ·
   `175` 零选区 + 返回常量 ✓

---

## 四 · 风险登记（★ 动手前先读这一节）

| 风险 | 处置 |
|---|---|
| ★★ **单实例 COM**（事实 24）：多个进程抢同一 COM 连接会死锁 | ★ 真机探针**串行**跑；★ 批量静态活（读官方页）**不并发抢 COM** ⇒ 这正是裁决书 D-3 的由来 |
| ★★ **弹窗冻住 COM**（本仓头号死因） | ★ 真机一律走 `tools/sw_guard.py`；★ B4 的 211 另需 `CommandInProgress` + 显式要求调用方给路径（不许它弹 Save As） |
| ★ **`AccessSelections` 那一族到不了**（事实 47，20+ 形态已穷尽） | ★ 涉及者（155 fold 等）先查 `I...` 指针变体；★ **不要再用"换个参数试试"的方式继续试** |
| ★ **官方例子与 Remarks 冲突**（`pre-code-conflict-lookup.md` 424 条） | ★ 动手前查该表；★ 冲突时**以真机读数为准并逐条记账**（spec.md §五） |
| ★ **`verified` 标签覆盖不到的分支** | ★ MUST 写进 `limitations`（★ 例：只有零件验过 ⇒ 明写"装配未验"） |

---

## 五 · 产物落点

```
specs/209-union-adopt-18/{spec,plan,tasks}.md      ★ 本规格
scripts/sw_*.py                                     ★ 能力层（★ 优先追加到已有模块）
mcp-server/tool_specs_batch92+.py                   ★ 工具层（每批一个批次文件）
tests/test_tool_specs_batch92+.py                   ★ 契约 + 负例 + 硬约束回归
tools/probe_union_adopt_*.py                         ★ 真机探针（每批一个）
output/union-adopt-*.json                            ★ 真机证据（★ output/ 被 gitignore ⇒ 可复跑）
capabilities.yaml                                    ★ 能力条目（level + evidence + limitations）
```
