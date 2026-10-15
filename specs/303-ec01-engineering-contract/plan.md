# Plan — 303-ec01-engineering-contract

**Feature**: `specs/303-ec01-engineering-contract/`

**实现**: `scripts/engineering_contract.py`（★ 488 行）

**判据**: `tests/test_ec01_*.py`

---

## 一、施工步骤（★ 本会话真走的那条）

1. ★ **G0 基线**：核编号/权属/写入面/复用目标（★ 见 `baseline.md`）
2. ★ **先写判据，再看它红**：★ 每个 V 都要有**红基线证明**（★ 事实 62：门禁写了 ≠ 有效）
3. ★ **离线实现**：★ 纯逻辑层（★ 不 import COM）
4. ★ **真机（如需）**：★ 一律 `python tools/sw_guard.py --timeout N -- python <script>.py`
5. ★ **跑生成器链 7 步** → ★ `release_check.py` 至 EXIT 0 → ★ `goal_gate.py` EXIT 0

## 二、职责

★ 工程设计契约（四类信息 / 状态机 / 内容哈希 / 旧计划适配）

## 三、模块规模

| ★ 项 | ★ 数 |
|---|---|
| ★ 源码行 | **488** |
| ★ 类 | **15** |
| ★ 公开函数 | **2** |
