# 078 · Tasks（全部完成，轮 159）

- [x] T-7401 第一版判据跑出 323 处、**假阳性 ≈100%** ⇒ **弃用**
- [x] T-7402 ★★ 第二版判据（对象名有依据）⇒ **12 处** `→ 验收:` `python tools/probe_direct_member_access.py`
- [x] T-7403 ★★★ 查出 `get_interference_detection` **3 处**成员名错并修
- [x] T-7404 真机冒烟 `→ 验收:` `python tools/verify_interference_smoke.py`（**6/6**，体积 16000 mm³）
- [x] T-7405 ★★★ 假对象测试改成官方真名 + 留档
- [x] T-7406 回归测试 4 条 `→ 验收:` `python -m pytest tests/test_interference_member_names.py -q`（**4 passed**）
- [x] T-7407 事实 99 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
