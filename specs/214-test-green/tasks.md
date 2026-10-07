# 规格 214 · 任务（tasks）

> ★ 宪法 §V：**每个任务都要有「怎么验」，且是一条能跑出绿的命令**；「我检查过了」不算 ✓
> ★★ 每条都带 `→ 验收:`，★ 且**只点仓库里存在的 `.py`**（★ 由 `scripts/check_spec_acceptance_paths.py` 守着）✓
> ★ 排序 = 执行顺序（★ 先低垂果实，★ 再动核心连接层，★ 最后二分污染源 —— 因为二分要 ~8 次全量）✓

## 阶段 A · A1 九条稳定红（★ 逐条定位真因，★ 不许先改测试）

### T-214-01 · A1-1 钉死数 339 → 504
★ 先**复算真值**，再改那一个数字；★ 改的时候**把依据写进注释**（★ 两条通路）。
→ 验收: `python tools/probe_mcp_stdio_handshake.py` 且 `python -m pytest tests/test_mcp_protocol_layer.py -q` ⇒ 0 failed

### T-214-02 · A1-2 效应表过期
★ **跑生成器**（★ 生成物不许手改）。
→ 验收: `python tools/gen_effect_declarations.py` 且 `python -m pytest tests/test_effect_declarations.py -q` ⇒ 0 failed

### T-214-03 · A1-4 `RESOLVERS['sketch']` 未用键
★ 先查全仓有没有 spec 用 `inject="sketch"`；★ 没有 ⇒ 删键**并写明为什么**（★ 该表有"未用键"判据守着）。
→ 验收: `python -m pytest tests/test_registry_wiring.py -q` ⇒ 0 failed

### T-214-04 · A1-7 `CreateSketchSlot` 判据
★ 先读断言在判什么（★ 注释/类型 vs 实例）。
→ 验收: `python -m pytest tests/test_sketch_slot_params.py -q` ⇒ 0 failed

### T-214-05 · A1-8 triage 档位与真源不一致
★ 以真源 `tools/spec211_manual_verdicts.py` 为准，让台账与它一致。
→ 验收: `python -m pytest tests/test_real_gap_triage_contract.py -q` ⇒ 0 failed

### T-214-06 · A1-6 裸 byref 一处
→ 验收: `python -m pytest tests/test_no_bare_byref_args.py -q` ⇒ 0 failed

### T-214-07 · A1-5 注入与导入不一致
→ 验收: `python -m pytest tests/test_com_member_helpers.py -q` ⇒ 0 failed

### T-214-08 · A1-9 batch79「十七条工具」
★ 先算差集；★ **是新增的合法工具 ⇒ 更新清单**；★ **是漏挂 ⇒ 走挂载三件套挂上**（★ 二选一，★ 不猜）。
→ 验收: `python -m pytest tests/test_tool_specs_batch79.py -q` ⇒ 0 failed

### T-214-09 · A1-3 `sw_connect.py` 真 bug（★ 本阶段唯一动核心连接层的一件）
★ 现象：`AttributeError: 'bool' object has no attribute 'get'`。
★ 改完**必须跑全量**（★ 该文件被大量测试共用 —— 见 plan §五）。
→ 验收: `python -m pytest tests/test_sw_connect_open_document.py -q` ⇒ 0 failed

### T-214-10 · A 阶段收口
★ 九条**逐个单跑**绿 ⇒ ★ 跑一次全量看还剩几条。
→ 验收: `python -m pytest tests/test_mcp_protocol_layer.py tests/test_effect_declarations.py tests/test_registry_wiring.py tests/test_com_member_helpers.py tests/test_no_bare_byref_args.py tests/test_sketch_slot_params.py tests/test_real_gap_triage_contract.py tests/test_tool_specs_batch79.py tests/test_sw_connect_open_document.py -q` ⇒ **0 failed**

## 阶段 B · A2 第二个污染源（★ 二分，★ 不盲试）

### T-214-11 · 建**复现装置**
★ 已知受害者 + 候选污染源**同一次运行** ⇒ ★ 先用它**复现**全量里那 9 条红（★ 复现不了就说明二分口径不对，★ 先修口径）。
→ 验收: `python -m pytest tests/test_rule3_declarative_selection_is_enforced.py tests/test_spec212_rule2b_gate.py tests/test_sw_part_sketch_selection.py tests/test_tool_specs_batch92.py -q` ⇒ 记录基线读数（★ 当前 **全绿** —— 说明污染源不在这一小撮里）

### T-214-12 · 二分定位第二个污染源
★ 按收集顺序取前缀 ⇒ 与受害者拼一次 ⇒ 区间减半；★ 收敛到 1 个文件（★ 方法见 plan §2.2）。
→ 验收: ★ 给出「污染源文件 + 一次能复现红的命令」并落盘到 `specs/214-test-green/recon/order-pollution.md`

### T-214-13 · 修掉它（★ 优先 PEP 562 转发那一类）
→ 验收: ★ 复现装置 **0 failed** 且 `python -m pytest tests -q` 的失败数**比 T-214-10 的读数少**（★ 逐数对账）

## 阶段 C · 收口

### T-214-14 · 全量归零
→ 验收: `python -m pytest tests -q --no-header -p no:cacheprovider` ⇒ 尾行 **`0 failed`**（★ C1）

### T-214-15 · 收尾链 + 按路径提交
→ 验收: `pwsh tools/round_chain.ps1` ⇒ 首轮 OK 且 `git status` 索引复位为 0（★ 提交走 `python tools/commit_mine.py`）

### T-214-16 · 回写游标 + 目标栏
★ 更新 `docs/ROADMAP.md` §一 与 `specs/214-test-green/goal-bar.md`（★ 进度**只**写这两处）。
→ 验收: ★ `python scripts/check_report_freshness.py` 退出码 0（★ 生成物与真源不分叉）

---

## 依赖与并行

```
T-01..T-09（A1，可任意序、各自独立）
   └─> T-10（A 阶段收口：一次单跑九文件）
T-11（建复现装置）─> T-12（二分）─> T-13（修污染源）
   └─> T-14（全量归零）─> T-15（收尾链 + 提交）─> T-16（回写游标）
★ T-09（改 sw_connect）与 T-12（二分）**都要求"改完跑全量"** ⇒ ★ 二者**串行**，不并行（★ 否则读数互相污染）
```
