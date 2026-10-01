# 038 · Tasks（全部完成，轮 119）

- [x] T-3401 查 `gdt` 入口 ⇒ `InsertGtol()`（0 参）
- [x] T-3402 ★ 查 `SetFrameSymbols2` ⇒ **只对 2022 之前的 Gtol 有效**
- [x] T-3403 ★ **再查一层** ⇒ 2022 格式走 `IGtolFrame.AddIndicator`
- [x] T-3404 取两条枚举 + `GetFrame` 的 1 基约定（出厂反射）
- [x] T-3405 写 `scripts/sw_gtol.py`
- [x] T-3406 契约测试（**10 passed**）
  `→ 验收:` `python -m pytest tests/test_sw_gtol_contract.py -q`
- [x] T-3407 加能力条目（35 → **36**）
- [x] T-3408 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
