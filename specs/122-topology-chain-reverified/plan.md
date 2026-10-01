# 122 · Plan

1. **specify**：验收命令是红的 + 账本归因为"环境/许可" ⇒ 目标：查到底并跑绿
2. **clarify**：业主说"许可装好了" ⇒ ★ 那"许可"这个归因**必须先被证伪或证实**（不能直接信）
3. **analyze**：查官方文档（`LoadAddIn` 参数形态）+ 枚举含义 ⇒ **3=文件没找到 · 7=许可错**
   ⇒ 旧探针的结论**错**（它把 3 读成了许可）
4. **plan**：① 只读注册表拿真路径 ② 用完整路径 `LoadAddIn` ③ 若得 0/2 ⇒ 持久修复进正常路径
5. **implement**：`scripts/sw_simulation.py` 加 `SIMULATION_ADDIN_DLL` / `LOAD_ADDIN_CODES` /
   `ensure_simulation_addin()`；`get_cosmosworks()` 复用；账本两条能力插**更正归因**
6. **verify**：`get_cosmosworks(sw)` ⇒ `CDispatch` ✓；然后**真跑整链**
7. **converge**：六条判据全走回读 ⇒ `verdict: pass`；修下游（签名审计 45→47 · 重生成地图 · 报告数字）
8. 事实 → Spec Kit → ROADMAP 游标 → 门禁 + 回归 → 两仓库 commit

## 风险与对策
| 风险 | 对策 |
|---|---|
| 采信"许可问题"就停手 | ★★★ 查**枚举含义** ⇒ 一眼看穿（3 ≠ 7）|
| `LoadAddIn` 加载 40 MB 进程内 COM 有风险 | ★ 只调**一次** · `CommandInProgress` finally 关 · 收尾点弹窗 · 复用已有实例 |
| 求解吃 20–25 GB | ★ **先量成本**：脚本自己写"单次约 3 分钟"⇒ 实测 228.9 s · 85,748 单元 |
| 把"跑绿了"当"整条仿真链都通了" | ⚠ **明说只跑了拓扑那条**，静力学没跑 |
| 以为许可和加载项是同一件事 | ★ 拆开：**许可=7**、**加载项没启用=能加载但没注册** ⇒ 本次是后者 |
