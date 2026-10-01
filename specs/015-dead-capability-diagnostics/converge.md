# 015 · Converge

**Converged**: 2026-10-01（轮 95）

## 结果
| 判据 | 结论 |
|---|---|
| SC-1101/1102 两处抛**可诊断的 `RuntimeError`** | ✅ 真机复验：消息含成员名与「后端」/「不可用」 |
| SC-1103 docstring 写明不可用 | ✅ 由测试钉住 |
| SC-1104 桩测 | ✅ **3 passed** |
| SC-1105 门禁 + 回归 | ✅ `release_check` exit 0 · 回归 **1003 passed** |

## 实测记录
**修后真机输出**：
```
create_cut_list ⇒ RuntimeError: IFeatureManager.InsertWeldmentCutList2 在当前后端（pywin32 迟到绑定）上
                  **取不到**（权威类型库里有该成员，但 COM 分发解析为 None）
                  ⇒ 切割清单在当前后端**不可用**；这不是调用参数的问题。
get_mass_property_override_options ⇒ RuntimeError: IModelDocExtension.GetMassProperties 在当前后端
                  （pywin32 迟到绑定）上**调用失败**（原始错误：(-2147352561, …)）
                  ⇒ 质量属性覆盖选项在当前后端**不可用**；…⚠ 这不是调用参数的问题。
```
⇒ **从"看不出真因"变成"一眼能判"**。

## 三处红都是"改了运行时文件没同步"（正常流程，非缺陷）
1. `check_signature_audit_freshness`：`sw_weldment.py` 调用点 71 → **72**（我加了判空调用）；
2. `check_report_freshness`：报告偏离数字；
3. `test_release_check_passes_current_tree`：上面两条的下游。

## 未查证
* **`InsertWeldmentCutList2` 到底能不能用**：本轮只证"pywin32 迟到绑定取不到"，
  **没查**换后端（`comtypes` / 进程内 C++）或换调用方式能否走通；
* 同理 `IMassProperty2` 的获取路径未穷尽。
⇒ 两条都记为**后端相关的未决**，不是"永远做不到"。
