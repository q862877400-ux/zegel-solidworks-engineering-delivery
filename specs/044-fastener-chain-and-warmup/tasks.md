# 044 · Tasks（全部完成，轮 125）

- [x] T-4001 走链路量清楚每步的参数与返回（`_probe_fastener_chain.py`）
- [x] T-4002 ★ 发现第 2 参是 Int32（紧固件 ID）而非尺寸名
- [x] T-4003 ★ `GetFastenerTable` 报「类型不匹配 位置 4」⇒ 按事实 53 停手
- [x] T-4004 ★★ 四组对照查出**必须热身**（`_probe_fastener_ordering.py`）
- [x] T-4005 写 `list_fastener_types` / `list_fastener_table_types` / `get_fastener_table`
- [x] T-4006 把热身做进 `_hole_standards_data()` 默认路径
- [x] T-4007 冒烟加**反向验证**（11/11）
  `→ 验收:` `python tools/verify_hole_standards_smoke.py`（**11/11**）
- [x] T-4008 契约测试（**19 passed**）+ 已知事实 69 + 能力条目
- [x] T-4009 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
