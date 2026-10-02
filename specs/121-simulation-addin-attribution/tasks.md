# 121 · Tasks（全部完成，轮 202）

- [x] T-12101 ★★★ 量环境 + **不采信**现成探针的结论
- [x] T-12102 ★★★ 查官方参数（要完整路径）+ 枚举含义（3≠7）
  `→ 验收:` `Get-Content C:\swapi\enums\swLoadAddinError_e.md`（**swFileNotFound=3 · swLicenseError=7**）
- [x] T-12103 ★★ 只读注册表拿真路径 ⇒ `LoadAddIn(<路径>)` ⇒ **0 = swSuccess**
  `→ 验收:` `python tools\probe_simulation_loadaddin_by_path.py`
- [x] T-12104 ★★ 持久修复 + 实测 `get_cosmosworks` 非 None
  `→ 验收:` `python -c "import sys;sys.path[:0]=['scripts'];import sw_connect,sw_simulation;print(type(sw_simulation.get_cosmosworks(sw_connect.connect_solidworks(10)[0])).__name__)"`（**CDispatch**）
- [x] T-12105 ★ 账本更正归因（`topology_optimization` / `simulation_and_fea`）
- [x] T-12106 ★★ 修下游（signature-audit 45→47 · 重生成地图）⇒ 三处全绿
- [x] T-12107 ★★ 查清回归 skipped 15→17 ⇒ **事实 57 的守卫，不是回归**
- [x] T-12108 事实 141 + 门禁 + 回归
  `→ 验收:` `python scripts\release_check.py`（exit 0）· 全量 **1260 passed / 17 skipped**
