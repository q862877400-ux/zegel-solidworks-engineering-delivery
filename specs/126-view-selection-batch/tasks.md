# Tasks: 视图读取 + 体上实体枚举

- [x] T-12601 ★ 核"哪些真能挂"（首参是否约定注入点）
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\scripts'];import inspect,sw_view as v;print(inspect.signature(v.get_active_view), inspect.signature(v.activate_view))"`
  （期望 `(model)` 与 `(view) -> bool` ⇒ **后者不挂**）
- [x] T-12602 ★ 核"有没有 view 包装的先例"（**期望空**）
  `→ 验收:` `Select-String -Path C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch*.py -Pattern 'ActiveView|sw_view' | Where-Object { $_.Filename -ne 'tool_specs_batch14.py' }`（**空**；⚠ 必须排除本批产物，见 known-facts 147）
- [x] T-12603 写 `tool_specs_batch14.py` + 注册
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\mcp-server',r'C:\swprojects\sw-skill-fork'];import register_capabilities as rc;print(len(rc.all_specs()))"`（**53**）
- [x] T-12604 两处计数同步（51→53 · 96→98）
  `→ 验收:` `python -m pytest tests/test_server_wiring.py tests/test_mcp_protocol_layer.py -q`（0 failed）
- [x] T-12605 五处口径一致动 2
  `→ 验收:` `python tools/probe_unexposed_functions.py` + `python tools/build_union_map.py`
- [x] T-12606 全链 + 回归
  `→ 验收:` `python scripts/release_check.py`（exit 0）· `python -m pytest tests -q`（0 failed）
