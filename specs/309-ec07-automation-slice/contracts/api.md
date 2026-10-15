# Contract — 309-ec07-automation-slice 的公开接口

**Feature**: `specs/309-ec07-automation-slice/`

**来源**: ★ **AST 提取**（★ 真签名）

---

| ★ 函数 | ★ 说明 |
|---|---|
| `check_reachability` | ★ 对外入口（★ 与 `StateMachine` 的几个方法**合起来** —— ★ 便于判据调用）。 |
| `select_drive` | ★★★ **选型**（★ EC07-T02 逐字：★「★ 选择**电机/减速/丝杠或气动**方案」）。 |
| `assert_no_com_imports` | ★★★ **纯离线自证**（★ 本模块不 import COM —— ★ 与 EC03/EC04 同族）。 |
