# 122 · Tasks（全部完成，轮 203）

- [x] T-12201 ★★★ 证伪"许可"归因（查枚举：3=文件没找到 · 7=许可错）
  `→ 验收:` `Get-Content C:\swapi\enums\swLoadAddinError_e.md`
- [x] T-12202 ★★ 只读注册表拿真路径 ⇒ `LoadAddIn(<完整路径>)` ⇒ **0 = swSuccess**
  `→ 验收:` `python tools\probe_simulation_loadaddin_by_path.py`
- [x] T-12203 ★★ 持久修复 + 实测取件
  `→ 验收:` `get_cosmosworks(sw)` ⇒ **CDispatch**
- [x] T-12204 ★★★ 整链真机复验 ⇒ **`verdict: pass`**
  `→ 验收:` `python tools\capture_topology_evidence.py`（exit 0 · 85,748 单元 · 图数 2 · `材料质量1` · 228.9 s）
- [x] T-12205 ★★ 修下游三处（签名审计 45→47 · 重生成地图 · 报告数字）⇒ 全绿
- [x] T-12206 门禁 + 回归 `→ 验收:` `python scripts\release_check.py`（exit 0）· 全量 **1260 passed / 17 skipped**
