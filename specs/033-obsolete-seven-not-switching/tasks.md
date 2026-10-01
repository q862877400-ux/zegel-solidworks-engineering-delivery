# 033 · Tasks（全部完成，轮 114）

- [x] T-2901 取 7 条的旧/新签名（反射）并排比
- [x] T-2902 ★ 判定：**7 条全部不换**（形状全对不上）
- [x] T-2903 两条后继查不到 ⇒ 按铁律 5 记「查不到」
- [x] T-2904 写进台账 §四之二
  `→ 验收:` `Select-String docs\obsolete-member-candidates.md -Pattern '全部不换'`
- [x] T-2905 ★ 台账重排 + 去重 + 重编号（**断言不丢内容**）
  `→ 验收:` `Select-String docs\obsolete-member-candidates.md -Pattern '^## '`
- [x] T-2906 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
