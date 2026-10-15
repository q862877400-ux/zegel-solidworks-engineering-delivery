# Tasks — **EC07 机械与自动化设计纵切片**

**Feature**: `specs/309-ec07-automation-slice/`

**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md`

---

## 五、★★★★★ 任务逐条（★ T01–T08）

| ★ 任务 | ★ 状态 | ★ 依据 |
|---|---|---|
| **EC07-T01** 冻结节拍/负载/行程/精度/环境/人员接近/失电失气 | ✅ **完成** | ★ `MotionIR.is_complete()`（★ **缺项 ⇒ 不选型**）· ★ `FaultKind` 含**失电/失气** |
| **EC07-T02** MotionIR + 选型（电机/减速/丝杠/气动） | ✅ **完成** | ★ `MotionIR`（★ 曲线/峰值/RMS/效率/制动/热边界）· ★ `select_drive()` |
| **EC07-T03** AutomationIR（IO/传感器/状态机/互锁/超时/故障恢复） | ✅ **完成** | ★ `AutomationIR`（★ **传感器须有来源+版本**） |
| **EC07-T04** SafetyFunctionIR（★ **分开普通互锁与安全功能**） | ✅ **完成** | ★ `SafetyFunctionIR`（★ **方法 + 责任人** · ★ **`unknown` 不放行**） |
| **EC07-T05** 七类故障的有限状态可达性 | ✅ **完成** | ★ `StateMachine`（★ **可达/不可达/死端**）· ★ `FaultMatrix`（★ **七类具名**） |
| **EC07-T06** 行程止挡/制动/能量释放/维护模式交叉检查 | ✅ **完成** | ★ CrossCheck（★ **四类** · ★ **每类机械侧与控制侧都要有交代** —— ★ 只写一侧 ⇒ **不算交叉检查**）· ★ 判据 5 例 |
| **EC07-T07** 输出选型计算/IO 表/功能状态图/联锁矩阵/故障清单/安全验证计划 | ✅ **完成** | ★ `select_drive` · ★ `AutomationIR.io_points` · ★ `StateMachine`（状态图）· ★ `interlock_by_kind`（联锁矩阵）· ★ `FaultMatrix`（故障清单）· ★ `SafetyFunctionIR.verdict`（安全验证计划） |
| **EC07-T08** 软硬件联调接口做仿真桩；★ **真实设备连接另立安全审批** | ✅ **完成** | ★ `UNVERIFIED_ON_REAL_MACHINE` 强制标记 · ★ **模块里无实机驱动**（★ V7 判据） |

---
