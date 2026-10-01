# Tasks: 圆形阵列 + 旋转凸台（角度换算边界）

- [x] T-13001 ★ 核规则 2 的原文与"边界"指哪一层
  `→ 验收:` `Select-String D:\AI\SW\AGENTS.md -Pattern '换算只在边界'` ⇒ 期望命中「换算只在边界做一次（`sw_connect.mm()`）」
- [x] T-13002 ★★ 核"换算助手已经存在、不需要新建"
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\scripts'];from sw_connect import deg;print(deg(90))"` ⇒ 期望 **1.5707963267948966**（π/2）
- [x] T-13003 ★★ 核"改名 ≠ 换算"（**本批存在的理由**）
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\scripts'];from sw_connect import deg;print(deg(90), 90)"` ⇒ 期望两个数**不同**（相差 180/π ≈ 57.3 倍）
- [x] T-13004 ★ 核"换算该用哪个机制"（找先例）
  `→ 验收:` `Select-String C:\swprojects\sw-skill-fork\mcp-server\tool_specs_batch3.py -Pattern '_consumed|derived_args'` ⇒ 期望命中 `_consumed(...)` + `derived_args=lambda p: ...`
- [x] T-13005 写 `tool_specs_batch17.py` + 注册
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\mcp-server',r'C:\swprojects\sw-skill-fork'];import register_capabilities as rc;print(len(rc.all_specs()))"` ⇒ 期望 **58**
- [x] T-13006 ★★★ 写守卫测试（**含负例**）并跑绿
  `→ 验收:` `python -m pytest tests/test_tool_specs_batch17.py -q` ⇒ 期望 **5 passed**
- [x] T-13007 ★★★ **证明那条负例测试真的能抓 bug**（事实 62：负例是唯一的证明）
  `→ 验收:` 把 `_radians_of_deg` 改成 `float(p.angle_deg)`（只改名不换算）后重跑 ⇒ **必须 2 failed**；还原后 **5 passed**
  （本轮实测：`FAILED test_deg_is_converted_to_radians` + `FAILED test_negative_naive_alias_...`）
- [x] T-13008 两处计数同步（56→58 · 101→103）
  `→ 验收:` `python -m pytest tests/test_server_wiring.py tests/test_mcp_protocol_layer.py -q` ⇒ 0 failed
- [x] T-13009 五处口径一致动 2（★ 缺口第二次动 337→**336**）
  `→ 验收:` `python tools/probe_unexposed_functions.py` + `python tools/build_union_map.py`
- [x] T-13010 全链 + 回归
  `→ 验收:` `python scripts/release_check.py`（exit 0）· `python -m pytest tests -q`（0 failed）
