# 021 · Tasks（全部完成，轮 102）

- [x] T-1701 抽出两档别名 63 条
  `→ 验收:` `Select-String docs\union-gap-triage-sample.md -Pattern 'aliases'`
- [x] T-1702 ★ **全核** 63 条（真 7+6 / 部分 0+14 / 假 19+17）
- [x] T-1703 定位最强反例：8 个曲面操作配到同两个函数
- [x] T-1704 合并四档 ⇒ 真实缺口 ≈ **289**（写明限度）
- [x] T-1705 追加进 sample 文档 + 更新 triage 顶部提示
  `→ 验收:` `Select-String docs\union-gap-triage.md -Pattern '轮 102 追加'`
- [x] T-1706 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
