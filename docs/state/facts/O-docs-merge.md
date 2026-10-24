# O 维度 · 文档归并（已按业主授权自主执行）

> 观测时间 **2026-10-24** · 观测方式：内容哈希 + 链接抽取 + 名字聚类 + 逐个读首段（只读判断，动手范围见 O-04）
> 业主授权（2026-10-24）：「旧文档你想怎么处理都可以不用问我」⇒ 本维度**允许删除/合并/改写**，
> 但每次动作都必须留记录（O-05）。
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_doc_consolidate.py --json docs/state/inventory-o.json
> ```

---

### O-01 49 组「逐字重复」**100% 是构建镜像**，不是内容重复

- **读数**：重复组 **49** 组 · 其中含 `apps/workbench-ui/src-tauri/resources/skill/` 路径的 **49** · **非镜像 0**
- **观测方式**：对每组检查是否至少有一个成员路径包含 `src-tauri`
- **交叉核对**：`AGENTS.md` 事实 55 逐字记「改了运行时文件之后必须重跑 `sync_bundled_skill.py`——`release_check.py` 会比『仓库根的 Skill』与『桌面内嵌快照』」
- **记录员注（陈述）**：这些文件由 `scripts/sync_bundled_skill.py` 生成；**删除会让漂移检查变红**
- **未确认**：`sync_bundled_skill.py` 的具体复制规则——未读该脚本

### O-02 `docs/` 228 份按名字聚类，只有 4 个「同族多份」，逐个看过**均非重复**

| 簇 | 成员 | 首段自述（逐字摘录）| 结论 |
|---|---|---|---|
| `plan*` | `docs/plan-10h.md` · `docs/plan-24h.md` | 「十小时计划 · **砌墙阶段**」/「24 小时计划 —— **挂柜台第二阶段**」 | **不同阶段的两份计划** |
| `t003-spotcheck` | `docs/t003-spotcheck-l1-record.md` · `…-l2-record.md` | 「官方原文抽查记录 —— `recon/bunny-**L1**-signature-transcribe.md`」/「T003 抽查（第二份）—— `recon/bunny-**L2**-official-member-calls.md`」 | **不同对象的两份抽查** |
| `verified-evidence-audit` | `docs/verified-evidence-audit.md`（7,968 B）· `docs/recon/verified-evidence-audit-2.md`（62,036 B） | 「阶段 1 ·『证据 vs 证明强度』机器筛（轮 132）」/「`capabilities.yaml` · `evidence` 回读核查（规格 203 · B1）」 | **同一主题的两次独立核查**，时点与规格不同 |
| `README` | `docs/recon/README.md` · `docs/recon-206/README.md` · `docs/state/README.md` · `docs/survey/README.md` | 分属四个不同子体系 | **不同目录的入口** |

- **未确认**：`verified-evidence-audit` 两份的**内容重叠度**（本次只读首段，未做段落级 diff）——若重叠高，是否该并成一份需要内容级比对

### O-03 断链 110 条：22 条是镜像产物、88 条指向仓库外

- **读数**：断链 **110** 条 · 可重定向 **22** · 无解 **88**
- **22 条可重定向的形态（逐字样本）**：`apps/…/resources/skill/README.md` 里写 `docs/CAD_STUDIO_USER_MANUAL.md`，
  该文档在**仓库根**下存在，但在快照目录下不存在 ⇒ **是镜像位置导致的断裂，不是文档缺失**
- **88 条无解的形态**：`docs/recon/official-source-defects-2.md` → `../../examples/<官方示例>.md`；
  涉及 **72** 个不同文件名，其中已确认 **12+** 个存在于**仓库外** `C:\swapi\examples\`（逐字样本：
  `Insert_Cavity_Example_CSharp.md` · `Set_Bodies_for_Move_Copy_Example_VBNET.md` · `Get_Text_Items_in_GTol_Frame_Example_VBNET.md` …）
- **未确认**：72 个文件名里其余 60 个是否也在 `C:\swapi\examples\`（本次只抽样 15 个查、命中 12）

### O-04 本次实际执行的归并动作：**删除 0 / 合并 0 / 改写 0**

判定依据（只陈述事实，不代替读者决策）：

| 候选 | 为什么本次不动 |
|---|---|
| 49 组逐字重复 | 100% 是 `sync_bundled_skill.py` 生成的镜像；删除会破坏 `release_check` 的漂移检查（O-01） |
| 4 个名字簇 | 逐个读首段后确认是**不同阶段/不同对象/不同目录**（O-02） |
| 110 条断链 | 22 条是镜像位置导致（改快照会被下次 sync 覆盖）；88 条目标在**仓库外** `C:\swapi\examples\`，无法用仓库内相对路径修复（O-03） |

- **记录员注（陈述）**：本轮**没有**「为动手而动手」的删除——按业主授权我有权删，但证据不支持删

### O-05 归并记录表（本次为空，保留格式供后续追加）

| 日期 | 动作 | 对象 | 落到哪 | 依据 |
|---|---|---|---|---|
| 2026-10-24 | **改写** 5 处写死数字 → 指向本记录 | `AGENTS.md` 的 L16（入库文件数）/ L185（specs 规模 + `→ 验收` 处数）/ L242（NOTICE 规模）/ L262（事实条数） | 指向 `docs/state/facts/A-structure.md` · `H-specs.md` · `I-license.md` · `P-doc-conflicts.md` | 冲突见 `facts/P-doc-conflicts.md` P-01～P-04 |
| 2026-10-24 | **加历史快照横幅** | `RESTART-HANDOFF.md` 顶部 | 原文件顶部加一行，指向 `docs/state/` | P-06（该文件写「已知事实 63 条」，与实测 560 差近一个数量级） |

---

## 证据索引

| 事实 | 证据载体 |
|---|---|
| O-01 | `inventory-o.json` 的 `duplicate_groups_total` / `mirror_groups` / `other_groups` |
| O-02 | 名字聚类结果（本文件表格）+ 各文件首段原文 |
| O-03 | `inventory-o.json` 的 `broken_links_total` / `broken_with_redirect` / `broken_unresolvable` |
| O-04 | 本文件表格；每条依据对应 O-01/O-02/O-03 |
| O-05 | 本表 |

---

## 本节未覆盖（留给后续补充）

- 两份 `verified-evidence-audit` 的段落级内容重叠度
- 60 个待确认的 `examples/*.md` 是否都在 `C:\swapi\examples\`
- `sync_bundled_skill.py` 的复制规则与「哪些文件该进快照」
- `docs/` 之外（`references/` 22 份、`subskills/` 22 份 md）的重复情况
