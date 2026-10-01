# 032 · Tasks（全部完成，轮 113）

- [x] T-2801 写脚本打出「官方接口 vs 我方调用点目标」
  `→ 验收:` `python _triage20.py`（工作区脚本）
- [x] T-2802 逐条核 20 条 ⇒ **真 8 / 假阳性 10 / 未定性 1**
- [x] T-2803 ★ 查出 `MoldUndercutDetect` 是**活的**（轮 98 的 batch9 工具包着它）
- [x] T-2804 ★ 在该工具 `doc` 里加警示（**不擅自改实现**）
  `→ 验收:` `Select-String mcp-server\tool_specs_batch9.py -Pattern 'marked Obsolete'`
- [x] T-2805 台账补总账 + 标为全部处置完毕
  `→ 验收:` `Select-String docs\obsolete-member-candidates.md -Pattern '台账总账'`
- [x] T-2806 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
