# 022 · Tasks（全部完成，轮 103）

- [x] T-1801 抽真缺 132 的**无偏样本**（每 6 取 1 ⇒ 22 条）
- [x] T-1802 ★ 自动检查**错 3 次**（登记表 / 陷阱表 / 参数名与知识表）——
      每次都在**写进结论之前**拦下
- [x] T-1803 ★ **弃用自动检查，逐条人工判** 22 条
  `→ 验收:` `Select-String docs\union-gap-triage-sample.md -Pattern '确实有'`
- [x] T-1804 合并四轮 ⇒ 真匹配 ≈ **73** ⇒ 真实缺口 ≈ **265**
- [x] T-1805 追加进 sample 文档 + 更新 triage 顶部（轮 103）
- [x] T-1806 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
