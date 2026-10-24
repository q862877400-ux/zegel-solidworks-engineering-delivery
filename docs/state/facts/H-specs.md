# H 维度 · `specs/` 规格层现状

> 观测时间 **2026-10-24** · 观测方式：目录扫描 + 正则抽取 `Status` / `→ 验收` + 语料计数（只读）
> 复现总命令：
> ```powershell
> python docs\state\probes\probe_specs.py --json docs/state/inventory-h.json
> ```

---

### H-01 规格目录 **281** 个；有 `spec.md` **277**，无 **4**

- **读数**：目录 **281** · 含 `spec.md` **277** · 不含 **4**
- **无 `spec.md` 的 4 个（逐字）**：`218-docs-consolidation` · `332-known-facts-triage` · `345-video-lectures` · `346-modeling-playbook`
- **记录员注（陈述）**：`346-modeling-playbook` 内含 8 个分册 md（`01-first-step.md` … `07-pitfall-index.md` + `README.md`），无 `spec.md`
- **未确认**：另外 3 个的目录内构成——未逐个列

### H-02 编号 1 ~ 346，区间内缺号 **30 个**（本次只显示前 30）

- **读数**：有数字前缀的目录 **count_numeric** 见 `inventory-h.json`；编号范围 **1~346**
- **缺号前 30（逐字）**：`80, 146, 147, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177`
- **记录员注（陈述）**：缺号里 `151~177` 是**连续段**
- **未确认**：这些编号是被占用后删除、还是从未使用——未查 `git log --diff-filter=D -- specs/`

### H-03 `→ 验收` 标记：`specs/` 下共 **935** 处，其中 `spec.md` 内仅 **20** 处

- **读数**：`specs/**/*.md` 全部文件 **935** 处；只管 `spec.md` 则 **20** 处
- **交叉核对**：`AGENTS.md` 记「门禁 `check_spec_acceptance_paths` 读它们的 `→ 验收:` 行（**866 处**）」⇒ 与本次 935 不同
- **门禁判据原文**：`scripts/check_spec_acceptance_paths.py:1` 逐字「验收命令的可跑性门禁：`→ 验收:` 行点到的脚本必须**在仓库里**」；`:15` 逐字「对每个 `→ 验收:` 行里出现的脚本记号」
- **未确认**：866 那个数字的取样范围（是否也含 `docs/`）——未复现该口径

### H-04 `Status` 字段：**140 份无 Status 行**，其余为自由文本

| Status 取值 | 份数 |
|---|---|
| `<无 Status 行>` | **140** |
| `Draft` | 19 |
| `Implemented（真机已验证）` | 1 |
| `Implemented（本机可跑，无外部依赖）` | 1 |
| `Implemented（轮 87）` … `（轮 98–99）` 等 | 各 1 |

- **读数**：取值**无固定枚举**；`Implemented（…）` 后括注内容各不相同（含轮次号）
- **未确认**：是否有读取方（门禁/生成器）解析 `Status`——未查引用

### H-05 **168/281** 份规格在 `docs/` + `AGENTS.md` 的语料里未被提及

- **观测方式**：把 `docs/` 下 md（取前 4000 份）与 `AGENTS.md` 全文拼成语料，检查规格目录名是否作为子串出现
- **读数**：未被提及 **168/281**；样本前 12 见 `inventory-h.json` 的 `specs_not_mentioned_sample`
- **未确认**：这 168 份是否被 `specs/` 内部互引（本次语料**不含 `specs/` 自身**）

### H-06 规格内 md 的构成（与 G 维度交叉）

- **读数**：`specs/` 下 md **1,452** 份（占全仓 md 78%，见 `facts/G-docs.md` G-02）
- **读数**：281 个目录平均 **5.2 份 md**（1,452 / 281）
- **未确认**：规格内常见文件名（`spec.md` / `tasks.md` / `plan.md` / `recon/*`）的分布——未统计

---

## 本节未覆盖（留给后续补充）

- 每条 `→ 验收:` 指向的脚本是否真存在（门禁 `check_spec_acceptance_paths` 的对象）——本次未跑该门禁
- 规格的**实际完成度**与 `Status` 的自述是否一致
- 规格与 `capabilities.yaml` 的对应关系
- 连续缺号段 `151~177` 的历史成因

---

## 证据索引（每个事实号 → `inventory-h.json` 的键）

| 事实 | 证据载体 |
|---|---|
| H-01 | `inventory-h.json` 的 `spec_dirs` / `with_spec_md` / `without_spec_md` |
| H-02 | `inventory-h.json` 的 `numbering.min/max/missing_in_range` |
| H-03 | `inventory-h.json` 的 `acceptance_lines_total`（20，仅 spec.md）；935 由仓库级 `Select-String` 得 |
| H-04 | `inventory-h.json` 的 `status_histogram` |
| H-05 | `inventory-h.json` 的 `specs_not_mentioned_in_docs` / `specs_not_mentioned_sample` |
| H-06 | `facts/G-docs.md` G-02（specs 1,452 份）÷ `spec_dirs`（281） |
