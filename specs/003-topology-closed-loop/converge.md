# Converge: 拓扑优化闭环（真机跑通并取得 Material Mass）

**Feature**: `003-topology-closed-loop` · **Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md) · **Tasks**: [tasks.md](tasks.md)

**Converged**: 2026-10-01（轮 48）· **环境**: SW 2026 SP4.1 / `revision 34.4.1`

> **这一步做什么**：把 `spec.md` 的每条验收判据**与交付物的实测证据逐条对齐**，
> 并**明确记下不符合项**。**不是复述 spec** —— 复述没有价值，找出「声称」与「实际」的差才有。

---

## 一、结论摘要

| 判据 | 结论 | 依据（可复跑的枚举命令） |
|---|---|---|
| SC-001 退出码 0 / `verdict == pass` | ⚠ **成立但本轮未重跑** | 见 §二.1 |
| SC-002 `material_mass_plot.ok` + 图名 | ✅ **成立** | 见 §二.2 |
| SC-003 `level == verified` + evidence 指向命令行 | ✅ **成立** | 见 §二.3 |
| SC-004 门禁 + 回归与基线逐条相同 | ✅ **成立（本轮实测）** | 见 §二.4 |
| SC-005 无许可 ⇒ 非零退出 + 证据写明是**许可**问题 | 🔴 **未验**（设计有、从未实跑） | 见 §三.1 |
| FR-001 可复跑命令 + 机器可读证据 | ✅ 成立 | `tools/capture_topology_evidence.py` + `output/topology-evidence.json` |
| FR-002 判据是回读值、不用返回码 | ✅ 成立 | 证据 8 步各带回读值（见 §二.2） |
| FR-003 `Results` 非空 + 图数 > 0 + **专门断言 Material Mass** | ✅ 成立 | 见 §二.2 |
| FR-004 任一步不达标 ⇒ 非零退出 + 写明哪一步 | ⚠ **代码有、未实测失败路径** | 同 SC-005 |
| FR-005 覆盖「无许可」失败形态 | 🔴 **未验** | 同 SC-005 |
| FR-006 不用真假值判成功码 | ✅ 成立 | 证据里 `goal_endedit_code_means` 字段**自己写明**「0 = EndEdit 提交成功（**不是真假值**）」 |
| FR-007 采集脚本不得在 pytest 里自动运行 | ✅ 成立 | `grep -c capture_topology_evidence tests/*.py` = **0** |
| FR-008 不留未关闭文档 / 未结束进程 | ✅ 成立 | `tools/capture_topology_evidence.py` 的 `finally:` ⇒ `sw.CloseDoc(title)` + `sw.CommandInProgress = False` |

**⇒ 净结果：8 条 FR 里 **7 条成立**、1 条未验；5 条 SC 里 **3 条成立**、1 条未重跑、1 条未验。**
**⇒ 另有 **1 处清单陈旧**（§三.2）—— 它不是 spec 的不符合项，而是**清单与事实不符**，一并记下。**

---

## 二、成立项的取证（**每条都给命令，不给结论式的「已验证」**）

### 1. SC-001 —— ⚠ 本轮**没有重跑**

**⚠ 诚实说明**：本轮**没有**执行 `python tools/capture_topology_evidence.py`
（单次求解约 187 秒且需许可），因此**不能声称「本轮验过」**。
成立性来自**已落盘的记录**：

```powershell
python -c "import json;d=json.load(open('output/topology-evidence.json',encoding='utf-8'));print(d['verdict'],d['captured_at'],d['revision'])"
# ⇒ pass 2026-09-30T23:38:09+00:00 34.4.1
```

⇒ **判据**：`verdict == 'pass'` ✓、`revision` 与本机一致（`34.4.1`）✓。
⚠ **遗留**：记录时间（2026-09-30）早于本轮 ⇒ 若要「本轮验过」，得真跑一次。

### 2. SC-002 / FR-002 / FR-003 —— 回读值与 Material Mass 断言

```powershell
python -c "import json;d=json.load(open('output/topology-evidence.json',encoding='utf-8'));\
s=d['steps'];print('solve.results_present',s['solve']['results_present']);\
print('solve.plot_count',s['solve']['plot_count']);\
print('material_mass_plot',s['material_mass_plot'])"
# ⇒ solve.results_present True
#   solve.plot_count 2
#   material_mass_plot {'ok': True, 'matched_plots': ['材料质量1'], ...}
```

**关键点**：`solve` 这一步**自己声明** `run_analysis_return_is_trustworthy: False`，
并改用 `results_present` + `plot_count` 作判据 —— **正是 FR-002 要求的形态**（本项目累计五处「返回码撒谎」）。
`matched_plots = ['材料质量1']` 命中判据正则 `(材料质量|Material\s*Mass)` ⇒ **中文界面也成立**（spec §Assumptions 的要求）。

### 3. SC-003 —— 清单里的 level 与 evidence

```powershell
python -c "import json;d=json.load(open('capabilities.yaml',encoding='utf-8'));\
c=[x for x in d['capabilities'] if x.get('id')=='topology_optimization'][0];\
print(c['level']);[print(' -',e) for e in c['evidence']]"
# ⇒ verified
#   - python tools/capture_topology_evidence.py（真机闭环，落 output/topology-evidence.json）
#   - pytest tests/test_sw_topology_contract.py（8 条契约测试，无 COM）
```

⇒ `level == 'verified'` ✓ 且 evidence **指向该命令行**（不是纯文字）✓。

### 4. SC-004 —— 门禁与回归（**本轮实测**）

```
python scripts/check_provenance.py        exit=0
python scripts/check_member_names.py      exit=0
python scripts/check_diff_markers.py      exit=0
python scripts/check_union_conventions.py exit=0
python scripts/check_env_pitfalls.py      exit=0
python scripts/release_check.py           exit=0
python -m pytest tests -q                 ⇒ 868 passed / 17 skipped / 0 failed
```

⇒ 与基线**逐条相同**（基线 = 868 passed / 17 skipped / 0 failed，轮 46 收工值）✓。

---

## 三、不符合项（**本步的主要产出**）

### 🔴 1. SC-005 / FR-004 / FR-005 —— 「无许可」失败路径**设计有、从未实跑**

**spec 要求**：无许可时脚本**非零退出**，且证据里能看出是**许可**问题（不是笼统「失败」）。

**实际**：
- **代码层有**：`tools/capture_topology_evidence.py` 的模块文档串 L39 写明
  「无许可时求解会弹『拓扑算例未获许可』且 `Results` 为空 ⇒ 本脚本会以非零退出并写明原因」；
  L223 的 `note` 也写着同一件事。
- **清单层有**：`capabilities.yaml` 的 `limitations[3]` 记了当初的**真实现象**
  （本机原先只有 `SimulationXpress`，弹「未获许可」、`Results` 为空，**而 `RunAnalysis` 仍返回 0**）。
- 🔴 **但没有任何一次「在无许可状态下运行本脚本并观察其退出码与证据」的记录。**

**⇒ 处置（不猜、不补写）**：按**铁律 5** 与**停止条件 6**，
**不把它标成「已验证」**；在下面 §四 追加一条 `limitations` 明确写「未验」。
**⚠ 能否补验**：需要把 SolidWorks 的 Simulation 许可**撤掉再重启**——
那是**系统层的许可设置改动**（`~/.dsh/AGENTS.md` 的「不碰系统层」+ 本项目铁律 2），
**我不自行做**。⇒ 记为**需用户配合或接受缺口**。

### 🔴 2. 清单陈旧：`limitations[15]` / `limitations[16]` 与 `level: verified` **自相矛盾**

**现象**：
- `limitations[15]` 结尾写：**「⇒ 维持 `stitched`：**不得升 verified**（A7 + 停止条件 6）。」**
- `limitations[16]` 结尾写：**「**本条目因此维持 `stitched`，不得升 `verified`。**」**
- **而同一份条目里 `level` 已经是 `verified`**，且 `limitations[1]` / `[2]` 记录了闭环跑通与验收命令。

**为什么这是问题**：一个读者只看 15/16 会得出「这能力还是 `stitched`」的**相反结论**。
本项目的原话：**「文档串与代码不符比没有文档更糟」**。

**成因（可复查）**：15/16 是**升 verified 之前**写的（那时确实卡着），
升 verified 时**补了新条目 1/2，但没回头标注旧的**。⇒ **典型的「追加式记录不留过期标记」。**

**⇒ 处置**：给 15/16 **加过期标记**（不删 —— 它们记录了**当时的真实状态**，有历史价值），
并在标记里指向 `[1]`/`[2]` 说明为何已过期。

---

## 四、对 `capabilities.yaml` 的收敛改动（本步产出）

1. **追加** `limitations` 一条：**「无许可失败路径未验」**（§三.1）
2. **标注** `limitations[15]` / `[16]` **已过期**（§三.2），保留原文
3. **不动** `level`（`verified` 是**对的**：它说的是「有我们自己的运行证据」，
   而 happy path 的证据齐全；§三.1 的缺口是**失败路径**，用 `limitations` 承载，不是降级理由）

---

## 五、这一步**没有**覆盖的（明确写出，避免「converge 过了就万事大吉」的错觉）

- **没有重跑**真机闭环（§二.1）⇒ 「本轮未验」而非「已验」
- **没有验**多实体零件 / 装配体（spec §Edge Cases 已排除，`limitations[6]` 有记）
- **没有验**导出类结果（`Export Smoothed Mesh` / 收敛曲线）—— 四源查不到，按铁律 5 记「查不到」
- **没有验** `ICWTopologyStudyManager` 的事务纪律（`limitations[14]` 已记「未在真机验证过」）
