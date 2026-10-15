# Contract — 306-ec04-safe-jobs-and-evidence 的公开接口

**Feature**: `specs/306-ec04-safe-jobs-and-evidence/`

**来源**: ★ **AST 提取**（★ 真签名）

---

| ★ 函数 | ★ 说明 |
|---|---|
| `filter_sensitive` | ★★ **敏感信息过滤**（★ EC04-T07 逐字 —— ★ 与 EC00 的脱敏**同一口径**）。 |
| `assert_no_com_imports` | ★★★ **纯离线自证**（★ 本模块**不 import** 任何 COM 模块）。 |
| `inject_worker_exit` | ★★★ **注入 ①：worker 退出**（★ 判据：★ 它**不能再改**，★ 但**别人可以接手**）。 |
| `inject_approval_expired` | ★★★ **注入 ②：审批过期**（★ 判据：★ **旧批准不能放行新版本**）。 |
| `inject_model_externally_modified` | ★★★ **注入 ③：模型被外部修改**（★ 判据：★ **旧证据立即失效**）。 |
| `injection_coverage` | ★★ **故障注入覆盖表**（★ 如实 —— ★ 哪些能离线注、哪些要 COM）。 |
