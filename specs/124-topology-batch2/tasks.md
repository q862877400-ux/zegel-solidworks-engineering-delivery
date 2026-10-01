# Tasks: 拓扑族第二批

- [x] T-12401 写 `mcp-server/tool_specs_batch12.py`（3 条 `ToolSpec`，照 `batch1` 的 `study` 模板）
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\mcp-server',r'C:\swprojects\sw-skill-fork'];import register_capabilities as rc;print(len(rc.all_specs()))"`（**48**）
- [x] T-12402 ★ 三个枚举的**取值**逐个核到（可重跑的命令）
  `→ 验收:` `python -c "import re,sys;from pathlib import Path;t=Path(r'D:/AI/SW/_raw/reflect/enum_cosworks.txt').read_text(encoding='utf-8',errors='replace');[print(n, n in t) for n in ('swsTopologyDemoldDirectionOption_e','swsTopologyStudyConstraintComparator_e','swsTopologyPreservedRegionOption_e','swsTopologySymmetryType_e')]"`
  （期望 **True/True/True/False** —— ★ 最后一个 False **就是"查不到"的证据**）
- [x] T-12403 注册（`BATCH_MODULES` 加一行）并过规则 1/2/3 门禁
  `→ 验收:` `python -m pytest tests/test_server_wiring.py -q`（0 failed）
- [x] T-12404 两处计数测试同步更新（45→48 · 90→93）
  `→ 验收:` `python -m pytest tests/test_server_wiring.py tests/test_mcp_protocol_layer.py -q`（0 failed）
- [x] T-12405 五处口径一致地动 3
  `→ 验收:` `python tools/probe_unexposed_functions.py` + `python tools/build_union_map.py`
- [x] T-12406 全链 + 回归
  `→ 验收:` `python scripts/release_check.py`（exit 0）· `python -m pytest tests -q`（0 failed）
