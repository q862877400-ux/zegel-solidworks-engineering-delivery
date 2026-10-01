# 085 · Tasks（全部完成，轮 165）

- [x] T-8501 顺线索回查 ⇒ 第一版扫描判据**弃用**（73 处大多假阳性）
- [x] T-8502 ★ 核实 `geometric_tolerance` 的原断言 ⇒ **不是**误判（我的扫描误报）
- [x] T-8503 ★★★ 读 `AddFrame` 的 Remarks 找出**顺序**这个真因
- [x] T-8504 ★★ 实测 `→ 验收:` `python tools/probe_gtol_frame_order.py`
  （`ConvertFormat` → `AddFrame()` **True** → `GetFrameCount` **2** → `GetFrame` **有对象**）
- [x] T-8505 修 `ensure_gtol_frame` + 改两句过时报错
- [x] T-8506 事实 105 + 条目更正
- [x] T-8507 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
