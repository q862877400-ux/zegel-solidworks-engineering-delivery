# 012 · Plan

**不重造**：形式与 `tool_specs_batch1..4` 完全一致，只加一个模块 + 一行注册。

## 步骤
1. 筛「签名兼容」的孤立能力（22 个）
2. 挑 5 个只读/低风险
3. 写 `tool_specs_batch5.py`（`SPECS_BATCH5`）
4. 在 `register_capabilities.py` 的 `BATCH_MODULES` 加一行
5. 写契约测试（对着真实签名核）
6. 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 声明手抄漂移 | 契约测试用 `inspect.signature` 核（沿用 batch1 的做法）|
| 钉死数量的测试红 | `test_expected_batch_size` 20→25，**并写明这是它的设计意图** |
| 「声明了但没注册」 | 加 SC-804：断言 `all_specs()` 里真的包含这 5 条 |
