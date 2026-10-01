# Converge: B 级缺口分诊

**Feature**: `010-gap-triage` · **Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md) · **Tasks**: [tasks.md](tasks.md)

**Converged**: 2026-10-01（轮 86）· **环境**: Python 3.14.7

> **这一步做什么**：把 `spec.md` 的每条验收判据**与实测证据逐条对齐**，并**明确记下不符合项**。
> **不是复述 spec** —— 复述没有价值，找出「声称」与「实际」的差才有。

---

## 一、结论摘要

| 判据 | 结论 | 依据（可复跑的枚举命令） |
|---|---|---|
| SC-601 `_our_tools()` 读两个来源（45 + 20 = 65）| ✅ 成立 | `python tools/probe_exposure_surface.py` |
| SC-602 分诊表可重生成、四类计数稳定 | ✅ 成立 | `python tools/triage_union_gaps.py` |
| SC-603 输出含**抽验警告** | ✅ 成立 | 同上（末段打印「假阳性率约一半」）|
| SC-604 **主匹配器未被改动** | ✅ 成立 | `git diff --stat tools/build_union_sources.py` ⇒ **空** |
| SC-605 门禁 + 回归不退化 | ✅ 成立 | `release_check` exit 0 · **970 passed / 17 skipped / 0 failed** |

---

## 二、**实测记录**（本节才是价值所在）

### 2.1 ★ 真缺陷（**已修**）：暴露面被低估 20 个
```
`server.py` 的 `@mcp.tool(name=…)` 装饰器 : 45 个
`tool_specs_batch*.py` 的注册表            : 20 个（**与装饰器交集 = 0**）
合并                                        : **65** 个   ← 修前只数到 45
```
**后果**：暴露面低估 20 ⇒ 「缺口」被灌水。
**复算**：并集 **384 → 404** · 本仓库独家 **35 → 55**。
★ 这个数**不降反升** —— 因为它量的是**我们带进并集的独家操作**，属于**修正记账**，不是我们的进度。

### 2.2 ★ 根因：归一**不剥域词** ⇒ 同一条操作是**两个键**
```
solidworks_mold_parting_line  →  mold_parting_line   ≠   parting_line（外部）
```
⚠ **但本轮不给主匹配器加模糊启发式**（已知事实 53）。
⇒ `tools/build_union_sources.py` **一个字没动**（SC-604 已验证），
339 仍是**严格名口径**的诚实数字；另出分诊表。

### 2.3 ★★ 抽验揭穿了我自己的分类规则（**本轮最有价值的一步**）
「后缀候选」抽 10 条 ⇒ **约一半假阳性**（规则只比**最后一个词**）：
```
✅ parting_line→insert_parting_line · export_drawing_pdf→export_to_pdf
   · add_dimension→add_dimension · create_mate→add_mate
❌ shut_off_surface→create_bspline_surface（都是 surface，但不是 shut-off）
   · set_material→add_render_material · create_section_view→activate_view
   · get_mass_properties→apply_visual_properties
⛔ 正确拒绝: run_simulation · unfold_sheet_metal（确实没有）
```
⇒ **处置（不调规则）**：改名「后缀候选（需人工核）」+ 抽验率写进输出 + 报告写明只用于定范围。
★ **这就是「一个门禁/规则写了不等于有效」的同族**，只是这次发生在**我自己的分诊规则**上。

### 2.4 ⚠ 我最初的怀疑**只对了一小半**（如实纠正）
开头怀疑「339 被命名差异灌水」—— 实测：
* **强别名只有 26 个（8%）** ⇒ 命名差异**远没有我想的多**；
* 真正的大头是「**能力在 `scripts/` 里、只是没暴露成 MCP 工具**」（**144，42%**），
  而那一类**又有一半是后缀假阳性**（§2.3）。
⇒ **诚实结论**：**339 这个数不能简单说"灌水"**；
它混了**三个口径**（暴露面 / 能力面 / 严格名），**必须先分清口径再谈进度**。

---

## 三、与 `tasks.md` 的对账

**T-601..T-612 全部完成**。关键：T-602 是**先找到一个具体反例**才往下查；
T-608 是**抽验自己的规则**（否则会把「144 个只要接出去」当成结论报出去）。

---

## 四、本轮**没有**做的事

* **没有**改 `build_union_sources._normalize`（§2.2，纪律）；
* **没有**调「后缀候选」的规则（§2.3，纪律）；
* **没有**把 144 个后缀候选**逐个人工核**（那是**下一步的工作量**，本轮只定范围）；
* **没有**动那 132 个「真缺」（那是并入的**真正待办**，留给后续特性）。

---

## 五、⚠ 本轮**未查证**（如实记录）

1. **「真缺 132」也可能被低估**：本轮的判定是"`scripts/` 里没有以它结尾的函数"，
   而**语义相同、用词完全不同**的操作（如 `run_simulation` vs 我们的 `run_analysis` 系）
   会被判成"真缺" ⇒ **132 是上限估计，不是下限**；
2. **`scripts/` 779 个公开函数里，有多少根本没暴露成 MCP 工具** ——
   本轮只从"缺口这一侧"看了 144 个，**没从"我们这一侧"看**（那会是另一个方向的全景）。

---

## 六、复跑全部命令

```powershell
cd C:\swprojects\sw-skill-fork
python tools/probe_exposure_surface.py      # 45 + 20 = 65（两个口径）
python tools/triage_union_gaps.py           # 四类计数 + 抽验警告 → docs/union-gap-triage.md
python tools/build_union_map.py             # 并集 404 / 缺 339 / 独家 55
python -m pytest tests -q                   # 970 passed / 17 skipped / 0 failed
python scripts/release_check.py             # exit 0（14 道硬门禁）
```
