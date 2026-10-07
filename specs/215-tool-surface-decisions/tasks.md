# 规格 215 · 任务（tasks）

> ★ 宪法 §V：每个任务都有「怎么验」、且是**一条能跑出绿的命令** ✓
> ★ 每条 `→ 验收:` **只点仓库里存在的 `.py`**（★ 由 `scripts/check_spec_acceptance_paths.py` 守着）✓

## 阶段 A · 呈现（★ 只做加法）

### T-215-01 · a：5 个 `macro_*` 首句前置"内部件"一句
★ 在 `mcp-server/tool_specs_batch79.py` 里，为 5 个 spec 的 `doc=` **前置一个字符串字面量**：
★ 「★ **内部件（★ 模型不必直接调用）**：本工具是 `sw_macro_guard.generate_macro_with_guard` 管线的**一步**。」
→ 验收: `python scripts/check_lean_first_line_caveat.py` ⇒ 退出 0

### T-215-02 · b：3 个钣金工具首句前置结论
★ `tool_specs_batch3.py`（`one_bend` 视读数）· `tool_specs_batch4.py`（`edge_flange` / `gusset` / `draft`）·
`tool_specs_batch93.py`（`hem`）—— ★ **只改实测不在窗口内的那 3 个**：
★ 前置「★ **本机（SW 2026 SP4.1 + pywin32）仍不可用**：<一句原因>。」✓
→ 验收: `python scripts/check_lean_first_line_caveat.py` ⇒ 退出 0；★ 且 `hem`/`one_bend` 的 lean 首句**与改前逐字相同**

### T-215-03 · 复核：lean 首句实读存证
★ 逐个打印 10 个工具的 lean 首句（★ 改前/改后对照），★ 存 `output/lean-first-line-215.json`
→ 验收: `python -c "import json;print(len(json.load(open(r'D:/AI/SW/output/lean-first-line-215.json'))))"` ⇒ 10

## 阶段 B · 门禁化（★ 数据先行的判据）

### T-215-04 · 建门禁本体
★ `scripts/check_lean_first_line_caveat.py`：★ 两条判据（★ `仍不可用`/`NOT USABLE` ⇒ 首句必须含其一；
★ 提到 `generate_macro_with_guard` ⇒ 首句必须含 `内部件`）+ `--report` 模式
→ 验收: `python scripts/check_lean_first_line_caveat.py --report` ⇒ ★ 命中集**恰好 8 条**（5 + 3），★ 无第 9 条

### T-215-05 · 双侧负例
★ `tests/test_lean_first_line_caveat_gate.py`：★ 正例（该报的两类样本）· ★ 负例（不该报的三类：
★ `不可用` 但指别的路 · ★ `建不出` 的历史叙述 · ★ 提到管线但首句已自证）
→ 验收: `python -m pytest tests/test_lean_first_line_caveat_gate.py -q` ⇒ **0 failed**

### T-215-06 · 接线（硬门禁 + 分类登记）
→ 验收: `python scripts/check_gate_wiring.py` ⇒ PASS（★ 已接线 + hard + 已汇总）

## 阶段 C · 提案（★ 只出文档，★ 不改规范）

### T-215-07 · c：`docs/proposal-r1-naming-redundancy.md`
★ 五要素齐（★ 前提 / 现状依据 / 三个选项 / 改名打断什么 / 建议）
→ 验收: `python -c "import pathlib;s=pathlib.Path(r'D:/AI/SW/docs/proposal-r1-naming-redundancy.md').read_text(encoding='utf-8');print(all(k in s for k in ('保留现状','去前缀','别名层')))"` ⇒ True

## 阶段 D · 收口

### T-215-08 · 收尾链 + 全量
→ 验收: `pwsh tools/round_chain.ps1` ⇒ 首轮 OK；★ 且 `python -m pytest tests -q` 尾行 **0 failed**（★ 规格 214 建立的不变量不许破）

### T-215-09 · 回写游标 + 目标栏 + 按路径提交
→ 验收: ★ `git status` 索引复位为 0；★ `docs/ROADMAP.md` §一 的 ⓪-214 段"下一步"改为"规格 215 已完成"

---

## 依赖

```
T-01 / T-02（改 doc，只做加法）─┬─> T-03（实读存证）
                              └─> T-04（建门禁）─> T-05（负例）─> T-06（接线）
T-07（提案文档，独立）
   └─> T-08（收尾链 + 全量）─> T-09（回写 + 提交）
```
