# tasks 235 —— 分发口**调用点**的非字面量实参门禁

> 每条都带**可复制执行**的验收命令；★ 顺序即施工顺序（**先量 → 先证能红 → 再改实现**）。

## T1 量测（先量后改）

- [x] **T1.1** 列 `partial` / `unresolved` / `no-callers` 入口的**非字面量**调用点与形态。

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_probe235_gap.py
#   ⇒ 解析面 resolved 18 · partial 3 · unresolved 4 · no-callers 12 · 可解析调用点 327
#   ⇒ 缺口调用点 8 个；形态分布 Name 5 · Subscript 2 · IfExp 1
```

- [x] **T1.2** 逐点定**包围 `def`** + 实参是否形参 + 候选值官方存在性。

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_probe235_gap2.py
#   ⇒ 8 处：可枚举 4（IfExp ×1 · for 字面量容器 ×1 · 模块级 dict 下标 ×2）
#            二级转发 3（实参是包围 def 的形参）· 枚举不出 1（for 目标 over 形参 dict）
#   ⇒ ★ 候选值**全部**在两源并集里查得到（12 个 distinct）
```

- [x] **T1.3** 与 234 的 `local` 桶**去重核对**（防重复判罪）。

```bash
# ⇒ 重叠：[]（8 处与 234 的 46 处**零重叠**）
```

## T2 先写判据并确认能红

- [x] **T2.1** 门禁本体写完后**先跑真树**，确认判据能红：

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B \
  scripts/check_dispatch_forward_arg_guard.py
#   ⇒ [FAIL] 违规 4 处：[undeclared] ×4 · exit 1   ← ★ 红基线（改实现前）
```

- [x] **T2.2** 写 `tests/test_dispatch_forward_arg_guard.py`（19 例），跑绿。

- [x] **T2.3** **变异检验**：把 `judge()` 短路成 `return None` ⇒ 判据必须转红。

```bash
# ⇒ Ran 19 tests · FAILED (failures=6)   ← ★ 判据不是空判据
```

## T3 实现

- [x] **T3.1** `scripts/check_dispatch_forward_arg_guard.py`（封闭形态读取器 + 三 code 自证 +
  下界冻结 + 零检查即红 + 口径不变量）。
- [x] **T3.2** 4 行声明（**纯插入零删除**）：
  `sw_drawing_create_missing.py`（`upstream`）· `sw_drawing_view.py`（`upstream`）·
  `sw_simulation_study_options.py`（`dynamic` ×1 + `upstream` ×1）。
- [x] **T3.3** 真树复跑 ⇒ `非字面量 8 · 可枚举 4 · 候选值 12 · 表态 upstream 3 / dynamic 1 · 违规 0 · exit 0`。

## T4 接线

- [x] **T4.1** `scripts/release_check.py`：`_run_dispatch_forward_arg_gate` + fail 判据 +
  **`_gate_results`** 登记（★ 元门禁 `check_gate_wiring.py` 会抓「没进返回体」）。
  ★ 插完**立刻 `sed` 复核相邻 `# ── 来源 ──` 头**（231/233/234 三次被 `Edit` 吞过）。
- [x] **T4.2** `docs/gate-classification.json`：`classification` 44 → **45**。
- [x] **T4.3** 两套口径**都 +1**：`gates` 43 → **44** · `classification` 44 → **45**。

## T5 收尾

- [x] **T5.1** 收尾链：

```bash
pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests/test_dispatch_forward_arg_guard.py
#   ⇒ release_check: 第 1 轮 OK · 19 passed in 23.81s
```

- [x] **T5.2** 门禁全套（★ **必须 3.14.7**）：

```bash
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py
#   ⇒ EXIT 0 · status pass · missing [] · gates 44 · dispatch_forward_arg_guard pass
```

- [x] **T5.3** 229–235 合并回归。
- [x] **T5.4** 更新 `docs/ROADMAP.md` §一 游标 · `.specify/feature.json` ·
  `.workbuddy-ai/memory/2026-10-09.md` · `output/AUTO_HANDOFF.md` · `output/AUTO_RUN_*.md`。

## T6 明确不做（登记，不在本切片）

- [ ] 递归解析二级转发（`upstream` 只要求声明 + 自证）。
- [ ] 候选值的**接口归属**（属 `check_interface_member_ownership.py`，映射表有洞）。
- [ ] 真机复核（`HEM_POSITIONS` / 16 条 arity 定罪）—— **需业主另行授权 COM**。
- [ ] 扩 `_entry_sites()` 认别名 —— 触发条件 = spec 232 门禁变红（真树 0 处）。
- [ ] 223 登记的 8 条 `HEAD` 即红既有失败 —— **先确认权属**。
- [ ] 发版前同步打包副本 —— 不需要每轮跑（收尾链已含）。
