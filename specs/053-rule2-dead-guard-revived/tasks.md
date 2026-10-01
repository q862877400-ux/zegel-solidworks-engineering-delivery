# 053 · Tasks（全部完成，轮 134）

- [x] T-4901 发现 `_LEN_SUFFIX` 是死常量（只在定义处出现）
- [x] T-4902 ★ 写负例**证明它死**（`tests/test_rule2_length_suffix_is_enforced.py`）
  `→ 验收:` `python -m pytest tests/test_rule2_length_suffix_is_enforced.py -q`（接上前 **3 passed**）
- [x] T-4903 接上判据 + `bool` 排除 + 3 个真例外显式豁免
- [x] T-4904 ★★ 把负例**翻方向** ⇒ 接上后 **5 passed**
- [x] T-4905 ★ 面积核对：`check_specs(all_specs())` = **0 问题**
- [x] T-4906 写 `docs/rule-2-dead-guard.md` + 已知事实 75
- [x] T-4907 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
