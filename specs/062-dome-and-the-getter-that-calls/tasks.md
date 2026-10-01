# 062 · Tasks（全部完成，轮 143）

- [x] T-5801 核实 `swFmDome` **不存在**（枚举 + 35 常量表）
- [x] T-5802 实现 `insert_dome`（走 `IModelDoc2.InsertDome`）
- [x] T-5803 ★★ 按官方 Remarks 用 **mark=1** 选面
- [x] T-5804 ★★★ 诊断脚本查出 **`get_com_member`「取」会「调」** + 最小修复
  `→ 验收:` `python tools/diag_insert_dome.py`
- [x] T-5805 真机冒烟 `→ 验收:` `python tools/verify_dome_smoke.py`（**9/9**）
- [x] T-5806 能力证据 + 已知事实 84 + 地图重跑 + `sw_connect` 来源块
- [x] T-5807 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
