# 123 · Tasks（全部完成，轮 204）

- [x] T-12301 ★★★ **先修判据**：探针加结构化全量输出（含签名）
  `→ 验收:` `python tools\probe_unexposed_functions.py`（落 `D:/AI/SW/output/orphan-capabilities.json` · 302 个）
- [x] T-12302 ★★ 从数据选批（51 可注入 / 4 含裸坐标）⇒ 取拓扑族 4 个
- [x] T-12303 ★★ 写 `mcp-server/tool_specs_batch11.py`（4 条 · 照既有 `study` 模板 · 签名照实取）
- [x] T-12304 ★★ 注册 + 门禁
  `→ 验收:` `python -c "import register_capabilities as rc; print(len(rc.all_specs()))"`（**45**）
- [x] T-12305 ★★ 五处口径一致动 4（探针 3 处 + 地图 2 处）
  `→ 验收:` `python tools\probe_unexposed_functions.py` + `python tools\build_union_map.py`
- [x] T-12306 ★ 两处硬编码计数同步更新
  `→ 验收:` `python -m pytest tests/test_server_wiring.py tests/test_mcp_protocol_layer.py -q`（**16 passed**）
- [x] T-12307 门禁 + 回归 `→ 验收:` `python scripts\release_check.py`（exit 0）· 全量回归
