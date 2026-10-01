# 084 · Tasks（全部完成，轮 164）

- [x] T-8401 逐类型判别 `→ 验收:` `python tools/probe_chamfer_forms.py`（type2 段数 2→3）
- [x] T-8402 ★★★ 更正「架构性限制」的定性并修 `create_sketch_chamfer`
- [x] T-8403 真机冒烟 `→ 验收:` `python tools/verify_sketch_edit_smoke.py`（**10/10**）
- [x] T-8404 拆出 `sketch_chamfer`（verified）+ 更正 `sketch_edit_ops`
- [x] T-8405 契约测试 `→ 验收:` `python -m pytest tests/test_sw_sketch_edit_contract.py -q`（**16 passed**）
- [x] T-8406 事实 104 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
