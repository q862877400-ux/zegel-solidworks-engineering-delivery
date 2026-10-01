# 055 · Tasks（全部完成，轮 136）

- [x] T-5101 写 `tools/probe_uncalled_helpers.py`
  `→ 验收:` `python tools/probe_uncalled_helpers.py`（164 扫过 / **0 可疑**，删完后）
- [x] T-5102 ★★ 判定唯一可疑是**真的死代码**（与 `stems_only` 的 docstring 对照）
- [x] T-5103 删除 + 墓碑注释
- [x] T-5104 ★★ 判定**不升硬门禁**（n=1）⇒ 做回归测试 + 豁免表
- [x] T-5105 ★ 纠正负例写法（抽 `find_uncalled(root)`，测试调真函数）
  `→ 验收:` `python -m pytest tests/test_no_uncalled_helpers.py -q`（**3 passed**）
- [x] T-5106 写 `docs/dead-guards.md` + 已知事实 77
- [x] T-5107 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
