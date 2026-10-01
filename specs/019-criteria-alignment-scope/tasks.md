# 019 · Tasks（全部完成，轮 100）

- [x] T-1501 查审计产物 ⇒ 发现 `final-audit.md` 编号不合
- [x] T-1502 推广门禁的作用范围（全篇找表格块）
  `→ 验收:` `python scripts/check_report_criteria_alignment.py`（**抓到 final-audit**）
- [x] T-1503 修假阳性（表头 `#` 被当成混入行）
- [x] T-1504 重写 `final-audit.md` 逐条表为 A1–A10 + 刷新时间/规模
  `→ 验收:` 门禁 **2/2 张表 PASS**
- [x] T-1505 补负例测试 `tests/test_report_criteria_alignment_gate.py`（**7 passed**）
- [x] T-1506 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
