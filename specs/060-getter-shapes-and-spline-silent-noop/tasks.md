# 060 · Tasks（全部完成，轮 141）

- [x] T-5601 写通用探针 `tools/probe_sketch_getter_shapes.py`
  `→ 验收:` `python tools/probe_sketch_getter_shapes.py`（**12/16/22**）
- [x] T-5602 ★★ 追 `get_splines` = 0 的根因
  `→ 验收:` `python tools/probe_spline_creation.py`（返回 **None**）
- [x] T-5603 ★★ 排除官方"必须重绘"的解释
  `→ 验收:` `python tools/probe_spline_redraw.py`（**重绘后仍 0**）
- [x] T-5604 ★ 处置：`sketch_spline` 返回 `None` 即抛 + docstring 写明四条实测
- [x] T-5605 ★ 三个取法的 docstring 写明形状 + 契约测试 3 条
  `→ 验收:` `python -m pytest tests/test_sw_sketch_contract.py -q`（**18 passed**）
- [x] T-5606 能力条目（两条）+ 已知事实 82 + 地图重跑
- [x] T-5607 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
