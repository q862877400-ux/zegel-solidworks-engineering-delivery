# Tasks: 仿真研究族

- [x] T-12501 ★ 先核"归属"（队列说 `_study`，实测在 `sw_simulation`）
  `→ 验收:` `python -c "import sys;sys.path[:0]=['scripts'];import inspect,sw_simulation as si;print(inspect.signature(si.default_element_size_and_tolerance))"`
- [x] T-12502 ★ 核 `template` 的合法取值（**期望"查不到"**）
  `→ 验收:` `python -c "from pathlib import Path;print([p.name for p in Path(r'C:/swapi/enums').glob('*eport*')])"`（**空**）
- [x] T-12503 写 `tool_specs_batch13.py` + 注册
  `→ 验收:` `python -c "import sys;sys.path[:0]=['mcp-server','.'];import register_capabilities as rc;print(len(rc.all_specs()))"`（**51**）
- [x] T-12504 两处计数同步（48→51 · 93→96）
  `→ 验收:` `python -m pytest tests/test_server_wiring.py tests/test_mcp_protocol_layer.py -q`（0 failed）
- [x] T-12505 五处口径一致动 3
  `→ 验收:` `python tools/probe_unexposed_functions.py` + `python tools/build_union_map.py`
- [x] T-12506 全链 + 回归
  `→ 验收:` `python scripts/release_check.py`（exit 0）· `python -m pytest tests -q`（0 failed）
