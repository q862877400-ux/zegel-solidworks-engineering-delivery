# Tasks — **EC10 安装、跨宿主适配与线上执行节点**

**Feature**: `specs/312-ec10-install-and-nodes/`

**上游**: `output/ENGINEERING_CONSTRUCTION_PLAN.md`

---

## 五、★★★★★ 任务逐条（★ T01–T08）

| ★ 任务 | ★ 状态 | ★ 依据 |
|---|---|---|
| **EC10-T01** 能力包内容（六类 + 不带密钥） | ✅ **完成** | ★ `CapabilityPackage`（★ **六类内容齐** + ★ **整包扫凭据**） |
| **EC10-T02** DSH/WorkBuddy 适配只做宿主差异层 | ✅ **完成** | ★ `SessionLeaseRegistry`（★ **宿主级互斥** —— ★ 共享同一会话） |
| **EC10-T03** 诊断（九项；★ **不自动启动真实修改**） | ✅ **完成** | ★ `DiagnosisResult`（★ `read_only = True`） |
| **EC10-T04** 可复现依赖/最小权限/升级回滚/不污染全局 | ✅ **完成** | ★ `UpgradePlan`（★ **`touched_user_global_env = False`**） |
| **EC10-T05** 云编排 + 受管节点 | ⏸ **不做**（★ **有意**） | ★★ **EC10-T08 逐字**：★「★ **本轮不创建云服务**」⇒ ★ **如实登记，★ 不假装** |
| **EC10-T06** 访问控制/保留/脱敏/下载授权/外发确认 | ✅ **完成** | ★ `AccessPolicy`（★ **四项控制** · ★ **跨项目拒**） |
| **EC10-T07** 安装→诊断→受控案例→证据→卸载/回滚 | ✅ **完成** | ★ 诊断 + ★ `UpgradePlan.rollback()`（★ 全流程可离线判） |
| **EC10-T08** 多客户端队列与断连/过期审批；★ **部署独立审批** | ✅ **完成** | ★ `SessionLeaseRegistry`（★ 多客户端）· ★ **部署边界已声明**（★ 见 `baseline.md` §二） |

---
