# 121 · Plan

1. 业主说"许可装好了" ⇒ ★ **去量**（先看 SW 在不在、探针在不在、账本怎么记）
2. 跑现成探针 ⇒ 结论"② 类：许可/安装问题" ⇒ ★ **不采信**（它没查返回码含义）
3. 查 `LoadAddIn` 的**官方参数**（`C:\swapi\types\ISldWorks\LoadAddIn.md`）⇒ 要**完整路径**
4. 查 `swLoadAddinError_e`（9 个成员）⇒ **3=文件没找到 · 7=许可错** ⇒ 旧归因**错了**
5. **只读**注册表拿真 CLSID → `InprocServer32` ⇒ 真路径
6. 用**真路径**调 `LoadAddIn` ⇒ **0 = swSuccess** ⇒ `GetAddInObject` 非 None ✓
7. ★ 持久修复：`ensure_simulation_addin()` 做进正常路径 + 更正错归因 + 账本插更正
8. 修**下游**（改了脚本 ⇒ signature-audit 行 45→47 · 地图要重生成）⇒ 三处全绿
9. ★ 查清回归 skipped 15→17 的归因（事实 57 的守卫）⇒ **不是回归**
10. 事实 141 → Spec Kit 121 → ROADMAP 游标 → 门禁 + 回归 → 两仓库 commit

## 风险与对策
| 风险 | 对策 |
|---|---|
| 采信现成探针的错结论 | ★★ **查枚举含义**（3 vs 7）⇒ 一眼看穿 |
| `LoadAddIn` 加载 40 MB 进程内 COM 有风险 | ★ 只调**一次**（不重试）· `CommandInProgress` finally 关 · 收尾点弹窗 · 复用已有实例 |
| 误以为"许可问题"就停手 | ★ 先证伪它（返回 3 ⇒ 与许可无关）|
| 以为跑通了整链 | ⚠ **明说没跑求解**，不夸大 |
| 把 skipped +2 当回归糊过去 | ★ **查清**（事实 57 的守卫）|
