# 050 · Tasks（全部完成，轮 131）

- [x] T-4601 ★ 复核 NOTICE 三条可核断言 ⇒ **三条都成立**
  `→ 验收:` `Select-String THIRD-PARTY-NOTICES.md -Pattern 'source_verified'`
- [x] T-4602 找出真过时的 3 处（登记历史 / 提交数 / 能力数）
- [x] T-4603 ★★ 新增机器检查 `tests/test_notice_consistency.py`（**5 passed**）
  `→ 验收:` `python -m pytest tests/test_notice_consistency.py -q`
- [x] T-4604 补登记历史（轮 131 条目）⇒ 第 ⑤ 条转绿
- [x] T-4605 更正 `final-audit.md` 的两处数字（并写明重新数的命令）
- [x] T-4606 许可门禁 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
