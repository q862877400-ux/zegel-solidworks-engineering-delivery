# 058 · Tasks（全部完成，轮 139）

- [x] T-5401 量 `subskills/` 的 manifest / name / 快照接线
- [x] T-5402 ★★ 把"看起来像发现"的 **23 个差异逐条查明** ⇒ 全是 `__pycache__/*.pyc`
- [x] T-5403 ★ 确认铁律 3：13 个 `__pycache__` 全 gitignore · 0 个跟踪的 `.pyc`
- [x] T-5404 5 条结构判据做成回归 `tests/test_subskills_wiring.py`
  `→ 验收:` `python -m pytest tests/test_subskills_wiring.py -q`（**5 passed**）
- [x] T-5405 ★★ **三条故障注入**全部会红、复原精确
- [x] T-5406 ★★ 宣告**扫荡结束** + 文档（并入 `docs/dead-guards.md`）+ 已知事实 80
- [x] T-5407 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
