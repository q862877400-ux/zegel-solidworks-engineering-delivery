# 049 · Tasks（全部完成，轮 130）

- [x] T-4501 ★ 量 A 系列现状 ⇒ 只有 **A5** 是缺口
- [x] T-4502 定位那 2 条存疑 ⇒ 都标「**需真机确认**」
- [x] T-4503 ★ 读出真因：**comtypes 早绑定** vs 工具的 **pywin32** 前提
- [x] T-4504 加 `COMTYPES_CALL_SITES`（带理由）+ `audit()` 分流 + CLI 单列
  `→ 验收:` `python scripts/audit_call_arity.py scripts\sw_delivery.py @refs`（**存疑 0**）
- [x] T-4505 负例测试 `tests/test_arity_comtypes_classification.py`（**4 passed**）
- [x] T-4506 `final-audit.md`：**A5 部分达成 → 达成**（写清理由）
- [x] T-4507 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
