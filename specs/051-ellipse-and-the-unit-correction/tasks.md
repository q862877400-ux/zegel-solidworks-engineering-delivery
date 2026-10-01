# 051 · Tasks（全部完成，轮 132）

- [x] T-4701 查 `ellipse` 入口 ⇒ **两级废弃链** ⇒ 走 `ISketchManager.CreateEllipse`
- [x] T-4702 实现 `sketch_ellipse`
- [x] T-4703 真机冒烟（量单位 + 验椭圆往返）
  `→ 验收:` `python tools/verify_ellipse_smoke.py`（**11/11**）
- [x] T-4704 ★ 逐条校正 14 处单位 docstring + 模块头说明
- [x] T-4705 补来源块（**两次**：第二次是因为中间还有两块）
  `→ 验收:` `python scripts/check_provenance.py`（exit 0）
- [x] T-4706 契约测试（**8 passed**）+ 能力条目 + 已知事实 73
- [x] T-4707 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
