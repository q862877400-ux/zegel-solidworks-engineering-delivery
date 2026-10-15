# 204 · Plan（六件的顺序、波次与算量）

**WIP = 1**：同时只允许一件是 🟡。件内可多波。

## 一、总表

| 件 | 波数 | 每波路数 | 合计 agent 调用 | 预计产出 |
|---|---|---|---|---|
| **C1** 多路一致率 | **3**（同一批 60 箱 × 3 路）＋补跑 | 60 | ~185 | `multiway-agreement.md` |
| **C2** 四家签名对账 | **6**（Eduardof0nt 1 · andrewbartels1 3 · SolidworksMCP-TS 1 · Slacker-LLC 1）＋补跑 | 60 | ~360 | `competitor-signature-crosscheck.md` |
| **C3** 前置 × evidence | **2**（110 条目分箱）＋补跑 | 55 | ~115 | `precondition-vs-evidence.md` |
| **C4** 示例 ↔ 成员页 | **10**（按成员 3887 个分箱）＋补跑 | 60 | ~600 | `official-internal-conflicts.md` |
| **C5** 缺口三态 | **1–2**（754 个缺口操作）＋补跑 | 60 | ~70 | `union-gap-tristate.md` |
| **C6** 事实去重 | **1**（6390 条 claim 分箱）＋补跑 | 60 | ~60 | `fact-single-home.md` |
| | | | **≈ 1390** | |

> **补跑**：按 203 实测的 ~21% 失败率预留；**只补缺失的，不重派整波**。
> ⚠ 算量目的是让用户知道**要花多少轮**，不是精确预算。

## 二、每件的动工顺序（**不许跳步**）

```
① 备料    按「页数/文件数/条目数」均衡装箱 → manifest JSON（每路一个明确输出路径）
② 探针    5 路；验 returned 与 schema；**returned: 0 当失败查**
③ 铺量    按 60 路/波；provider + model 成对写；一份文档一路
④ 核验    引文逐字回查 + schema 检查 + 计数可重数
⑤ 补跑    只补失败/缺失
⑥ 归并    按 manifest 映回原对象；**跨件不合并**
⑦ 抽查    Lead 独立复核 5–12 条，**并复验复核器自身**
⑦bis 三裁判门禁 ★ **每件必过**（设计见 [`verifiers.md`](verifiers.md)）：
         V1 审计者 = `deepseek-official` / `deepseek-flash`（官方 V4.1 flash）· 抽检 + 审判据
         V2 对抗者 = `opencode-zen` / `space-bunny-free` · 专门证伪
         V3 复算者 = `opencode-zen` / `space-bunny-free` · 独立重做一遍再比对
         ⇒ 产出里必须写 `artifact_verdict`（pass / conditional_pass）与**三方各自的问题**（不许只报多数票）
⑧ 出产物  docs/recon/<件>.md（统计 → 主表 → 异常单列 → **三裁判结论** → 限度）
⑨ 记账    更新本文件勾选 + `docs/ROADMAP.md` §一·C 支线段
```

★ **第 0 件事（比 C1 还早）**：**探针验 V1 的路由** ——
用 `provider="deepseek-official"` / `model="deepseek-flash"` 派一路只读任务。
**不通就停下问用户**，不许静默换成 bunny（那就变成三个同源，门禁失效）。

## 三、各件的**前置条件**（不满足就不许开工）

| 件 | 前置 | 现在满足吗 |
|---|---|---|
| C1 | `docs/recon/{iview,drawingdoc,isheet}-read-members.md` 在盘（788 页的标准答案） | ✅ 已交付 |
| C2 | 四家克隆可读 + `docs/recon/interface-ledger.md` 在盘 | ✅ 克隆在（2/259/59/15 代码文件）；台账已交付 |
| C3 | `capabilities.yaml` 可解析 + B3/B4 的前置 JSON 已落 `specs/203-*/recon/` | ✅ 两者都在 |
| C4 | `member-to-example-index.md` 的成员→示例索引 + 成员页 `Remarks` | ✅ 索引已交付（3887 个成员） |
| C5 | `tools/union-sources.json` 在盘 | ✅ **已查**：在盘，45253 B |
| C6 | `claims_norm.json` 已在 `specs/203-*/recon/` | ✅ **已补拷**（`claims-norm.json`，6390 条 / 6385 过闸） |

## 四、验收（每件收工时必须能跑出数字）

| 件 | 验收 |
|---|---|
| C1 | 报出**两个**一致率（集群自洽 / 与标准答案），且**三路一致率的分母 = 788** 可重数 |
| C2 | 按项目分列；每条的引文都能在该项目文件里逐字搜到；`unknown_overload` 单列 |
| C3 | 三态计数之和 = 条文数；「有前置未覆盖」清单每条带两段原文 |
| C4 | 分歧按「争的是哪个量」分组；「示例更具体」单列 |
| C5 | 三态之和 = 缺口总数；给「矩阵错判了几个」 |
| C6 | 每个量有唯一家；矛盾 vs 时序更新分开计数 |

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| **C2 误判别人**（他们有我们不认识的封装/重载） | 单列 `unknown_overload`；**只说"与官方签名不一致"，不说"他们错了"** |
| **C1 测出 Lead 自己的错误率高** | 如实报（这本来就是它的一半价值）；不许只报集群那一半 |
| **C5 依赖主线文件** | 开工前查；不在就延后并记明 |
| **单件过长**（C4 需 ~10 波） | 分次交；每波收工就把中间结果落 `specs/204-*/recon/`，不攒到最后 |
| 产出与主线文件冲突 | 只写 `docs/recon/` 与 `specs/204-*/` + ROADMAP 支线段 |
