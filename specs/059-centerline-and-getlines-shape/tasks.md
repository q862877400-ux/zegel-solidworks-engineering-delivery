# 059 · Tasks（全部完成，轮 140）

- [x] T-5501 查 `centerline` 入口 ⇒ **两级废弃链** ⇒ 走 `ISketchManager.CreateCenterLine`
- [x] T-5502 实现 `sketch_centerline`
- [x] T-5503 真机冒烟（建成 + 往返 + 再测单位）
  `→ 验收:` `python tools/verify_centerline_smoke.py`（**8/8**）
- [x] T-5504 ★★ 探针查清 `get_lines` 的返回形状
  `→ 验收:` `python tools/probe_getlines_count.py`（**12/24/36**）
- [x] T-5505 改写 docstring + 冒烟加定量判据
  `→ 验收:` `python tools/verify_sketch_getters_smoke.py`（**18/18**）
- [x] T-5506 契约测试加 3 条
  `→ 验收:` `python -m pytest tests/test_sw_sketch_contract.py -q`（**15 passed**）
- [x] T-5507 能力条目 + 已知事实 81 + **地图重跑**（门禁尽职抓到）
- [x] T-5508 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
