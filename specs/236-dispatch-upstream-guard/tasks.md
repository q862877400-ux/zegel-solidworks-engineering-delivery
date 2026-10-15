# tasks 236 · 任务清单（每条带**可复制执行**的验收命令）

> 解释器：判据用 **3.13.12**（`C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`）；
> ★★ 门禁全套 `release_check.py` **必须用 3.14.7**（`C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`）。

- [x] **T1 先量**（已完成，见 spec §三）：探针 `output/_probe236_upstream.py` + `_probe236_facts.py`
  ⇒ 3 条 `upstream` 各落一个桶（`sites` / `orphan` / `tool-only`），5 个候选值全在官方两源。
  验收：`python -B output/_probe236_facts.py`（输出含「官方成员名 18460 个」与三行桶事实）。

- [x] **T2 写门禁本体** `scripts/check_dispatch_upstream_guard.py`。
  验收：`python -B scripts/check_dispatch_upstream_guard.py`（★ 此时应为 **exit 1 · 未表态 3 处**）。

- [x] **T3 写判据** `tests/test_dispatch_upstream_guard.py`（合成树端到端负例 + 读取器 + 源隔离 + 真树读数）。
  验收：`python -B tests/test_dispatch_upstream_guard.py`

- [x] **T4 记录红基线**：T2 之后、T5 之前跑真树 ⇒ `[FAIL] 违规 3 处 = [undeclared] ×3 · exit 1`。
  验收：`python -B scripts/check_dispatch_upstream_guard.py; echo "exit=$?"`

- [x] **T5 补 3 条声明的上游桶**（行内改写，零新增行 / 零删除）。
  验收：`grep -n "dispatch-fwd: upstream" scripts/*.py`（3 行，各含 `sites` / `orphan` / `tool-only`）。

- [x] **T6 真树转绿**。
  验收：`python -B scripts/check_dispatch_upstream_guard.py; echo "exit=$?"`（期望 `exit=0`）。

- [x] **T7 接线 `release_check.py`**：`_run_dispatch_upstream_gate` + fail 判据 + `_gate_results`。
  验收：`grep -n "dispatch_upstream" scripts/release_check.py`（≥3 处：函数、调用、返回体）。

- [x] **T8 登记 `docs/gate-classification.json`**：`classification` +1。
  验收：`python -c "import json;d=json.load(open('docs/gate-classification.json',encoding='utf-8'));print(len(d['classification']))"`

- [x] **T9 235 回归**（★ 声明语法向后兼容）。
  验收：`python -B tests/test_dispatch_forward_arg_guard.py`

- [x] **T10 收尾链 + 门禁全套**。
  验收：`pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests/test_dispatch_upstream_guard.py`
  验收：`"C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" D:/AI/SW/scripts/release_check.py`

- [x] **T11 更新 ROADMAP §一 游标 + `memory/2026-10-09.md`（append）+ 交接单 + `output/AUTO_RUN_*.md`**。

## 收口定义

- [x] 四件齐（`spec.md` / `plan.md` / `tasks.md` / `acceptance.md`）。
- [x] 门禁本体真树 **exit 0**；判据全绿；235 回归全绿；门禁全套 **status pass**。
- [x] 两个口径都 +1（`release_check.gates` 与 `gate-classification.classification`）。
- [x] 红基线已记录（能红）。
