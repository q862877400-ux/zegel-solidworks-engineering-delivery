# 036 · Tasks（全部完成，轮 117）

- [x] T-3201 挑 `sw_sketch`（轮 111 换的 6 个取法只有静态证据）
- [x] T-3202 查现成的造草图件 ⇒ `start_sketch` / `sketch_line` / `sketch_arc` / `end_sketch`
- [x] T-3203 写 `tools/verify_sketch_getters_smoke.py`
  `→ 验收:` `python tools/verify_sketch_getters_smoke.py`（**17/17**）
- [x] T-3204 ★ 交叉验证 `get_sketch_segments == 2`（画了线+弧）
- [x] T-3205 ★ 查归属 ⇒ **发现 `sw_sketch` 没有能力条目** ⇒ 新建 `sketch_query`（`verified`）
- [x] T-3206 同步源码与测试里的过时注释（"未在本机实测"）
- [x] T-3207 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
