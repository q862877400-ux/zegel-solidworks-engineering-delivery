# Tasks: 结构化审查报告

- [x] T-12701 ★ 核"哪些真能挂"（首参是否约定注入点）
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\scripts'];import inspect,sw_simulation_results as m;print(inspect.signature(m.activate_plot))"`
  （期望 `(results, plot_name: 'str') -> 'bool'` ⇒ **首参 `results` 不是注入点 ⇒ 不挂**）
- [x] T-12702 ★ 核"有没有 list 型 Param 先例"（**排除本批产物**，事实 147）
  `→ 验收:` `Select-String -Path C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch*.py -Pattern 'Param\([^)]*,\s*list' | Where-Object { $_.Filename -ne 'tool_specs_batch15.py' }`（**空**）
- [x] T-12703 写 `tool_specs_batch15.py` + 注册
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\mcp-server',r'C:\swprojects\sw-skill-fork'];import register_capabilities as rc;print(len(rc.all_specs()))"`（**54**）
- [x] T-12704 两处计数同步（53→54 · 98→99）
  `→ 验收:` `python -m pytest tests/test_server_wiring.py tests/test_mcp_protocol_layer.py -q`（0 failed）
- [x] T-12705 五处口径一致动 1
  `→ 验收:` `python tools/probe_unexposed_functions.py` + `python tools/build_union_map.py`
- [x] T-12706 全链 + 回归
  `→ 验收:` `python scripts/release_check.py`（exit 0）· `python -m pytest tests -q`（0 failed）
