# 064 · Tasks（全部完成，轮 145）

- [x] T-6001 ★★ 24/24 读完 ⇒ 全部是故意调用
- [x] T-6002 加 `call_com_member` + 迁移 24 处
- [x] T-6003 ★★ 补 11 个模块的导入 + 三类测试桩
- [x] T-6004 ★★★ 新判据（`hasattr`）抓出 `sw_assembly.py` 12 处 NameError
  `→ 验收:` `python -m pytest tests/test_com_member_helpers.py -q`（**3 passed**）
- [x] T-6005 ★★ 修两个漏计（`check_member_names` WRAPPER · `audit_call_arity` WRAPPERS）
- [x] T-6006 ⚠ 撤掉做不成的判据 + 留档
- [x] T-6007 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
