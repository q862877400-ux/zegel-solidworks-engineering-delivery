# 规格 216 · 任务（tasks）

> ★ 每条 `→ 验收:` **只点仓库里存在的 `.py`**（由 `scripts/check_spec_acceptance_paths.py` 守着）✓

## 阶段 A · ③ 台账订正（★ 本轮已完成）

### T-216-01 · 读第一现场：`costing` 条目的 `limitations`
→ 验收: ★ 已读（19 条），★ 结论写进 goal-bar

### T-216-02 · 用台账自己的验收命令真机复跑
★ `python tools/sw_guard.py --timeout 600 -- python tools/verify_costing_e2e.py`（★ 走护栏，不裸跑）
→ 验收: `output/costing-evidence.json` 的 `verdict` = `pass` 且 `assertions` 3/3

### T-216-03 · 修 `revision` 真缺陷（源头 + 调用方）
★ `scripts/sw_connect.py` 补 `revision`（复用 `get_sw_version()`）· `tools/verify_costing_e2e.py` 加 `or ""`
→ 验收: 真机复跑后 `solidworks_revision` = `34.4.1`（★ 修前为空串）

### T-216-04 · 订正台账两处（追加 + 标注旧条作废）
★ `capabilities.yaml`：`costing`（limitations +4 条、evidence 改判据）· `costing_readback`（limitations +1 条）
→ 验收: `python scripts/check_union_conventions.py` ⇒ 退出 0

## 阶段 B · ① 预选族 9 条加 `pre_call`（★ 主要工作量）

### T-216-05 · 取「官方前置」那 9 条并逐条读目标函数
→ 验收: `python -c "import json;d=json.load(open(r'D:/AI/SW/docs/preselect-family-baseline.json',encoding='utf-8'));print(len(d['entries']) if isinstance(d,dict) else len(d))"` ⇒ 记录条数

### T-216-06 · 照 `tool_specs_batch74.py::_select_faces_for` 的形状写 `pre_call`
→ 验收: `python scripts/check_preselect_family.py` ⇒ 退出 0

### T-216-07 · 逐条真机验证（选区 >0 且特征真建成）
→ 验收: ★ 每条留一份真机证据（`output/*-evidence.json`）

### T-216-08 · 复核「显式拒」3 条与「诊断型」2 条的结论仍成立
→ 验收: `python scripts/check_preselect_family.py --report` ⇒ 分类与 baseline 一致

## 阶段 C · ② AVI 取舍

### T-216-09 · 判 (a) 能否拿到 `CosmosMotion` 类算例
★ 不许拿 `ensure_motion_type_library` 的 ok 当"能导"的证据（★ 台账 L3189 的警告）
→ 验收: ★ 结论落 `specs/216-real-machine-closeout/recon/avi-boundary.md`

### T-216-10 · 把结论写进台账
→ 验收: `capabilities.yaml` 的 `animation_export` 含结论 + 三条实测事实；`check_union_conventions` 退出 0

## 阶段 D · 收口

### T-216-11 · 全量回归（★ 改过 `sw_connect.py` ⇒ 按纪律必须跑全量）
→ 验收: `python -m pytest tests -q` ⇒ 尾行 **0 failed**

### T-216-12 · 收尾链 + 回写游标 + 按路径提交
→ 验收: `pwsh tools/round_chain.ps1` ⇒ 首轮 OK；★ `git status` 索引 0

---

```
T-01..T-04（③，本轮完成）─┐
T-05..T-08（①，主要工作量）┼─> T-11（全量）─> T-12（收尾 + 提交）
T-09..T-10（②）─────────┘
★ T-03 改了 scripts/sw_connect.py ⇒ T-11 的**全量**不可省（★ 该文件被大量测试共用）
```
