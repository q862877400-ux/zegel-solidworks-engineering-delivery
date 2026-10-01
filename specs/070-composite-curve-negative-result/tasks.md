# 070 · Tasks（全部完成，轮 151）

- [x] T-6601 三源查 `InsertCompositeCurve` + 官方示例
- [x] T-6602 实现 `insert_composite_curve`（用 `call_com_member`）
- [x] T-6603 ★★ 诊断：特征树里只有 **1** 个草图 ⇒ **前提不成立**
- [x] T-6604 ★★★ 修掉硬编码 `True` 的检查（改成真的数）
  `→ 验收:` `python tools/verify_composite_curve_smoke.py`（那条**当场变红**，前提问题暴露）
- [x] T-6605 如实收成阴性结果（**不升级能力**）+ 已知事实 91
- [x] T-6606 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
