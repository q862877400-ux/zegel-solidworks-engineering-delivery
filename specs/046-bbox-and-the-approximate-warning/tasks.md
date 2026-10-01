# 046 · Tasks（全部完成，轮 127）

- [x] T-4201 挑 `bbox`（可用精确数字验证）
- [x] T-4202 ★ 先读官方 IMPORTANT 段 ⇒ 判据改成"容差内"+ **专门量偏差**
- [x] T-4203 实现 `sw_part.get_bounding_box`
- [x] T-4204 数值冒烟 ⇒ **先 7/8**
  `→ 验收:` `python tools/verify_bbox_smoke.py`
- [x] T-4205 ★★ 抓到并修两处错（`mm` 未导入 + 输入方向的 `mm()` 用在输出上）
- [x] T-4206 ★ 直读 COM 确认单位是**毫米** ⇒ **8/8，偏差 0.00e+00**
- [x] T-4207 测试（**4 passed**）+ 能力条目 + 已知事实 71
- [x] T-4208 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
