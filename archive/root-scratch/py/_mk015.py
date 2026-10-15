import sys
from pathlib import Path
S = Path(r"D:\AI\SW\specs\015-dead-capability-diagnostics")
S.mkdir(parents=True, exist_ok=True)

spec = """# 015 · 把两个「跑不通的函数」改成**失败可见**

**Status**: Implemented（轮 95）

## 背景
`014` 的普查定性出 **2 个真缺陷**（孤立函数，从没跑通过）：
* `sw_export.get_mass_property_override_options`
* `sw_weldment.create_cut_list`

**修之前它们抛的是**：
```
create_cut_list              ⇒ TypeError: 'NoneType' object is not callable      ← 看不出是「成员取不到」
get_mass_property_override…  ⇒ com_error (-2147352561, '非选择性的参数。')        ← 看不出是「后端不可用」
```

## 为什么不"修好"，而是"让失败可见"
查证表明**两条路都走不通**：
* `IFeatureManager.InsertWeldmentCutList` / `InsertWeldmentCutList2`
  **权威类型库里有**，但 pywin32 迟到绑定**取到 `None`**；
* `IModelDocExtension.GetMassProperties` **任何参数数都失败**；
  `GetMassProperties2` 能跑但**返回数值数组**，拿不到 `IMassProperty2`。

⇒ **不是参数问题，是后端能力问题** ⇒ 与仓库对 `IModeler.Create*Surface` 的先例一致
（已知事实 40）：**不可靠时唯一能修的是「让失败可见」**。

## 判据
| ID | 判据 |
|---|---|
| SC-1101 | `create_cut_list` 在成员取不到时抛 **`RuntimeError`**，消息含**成员名 + 「后端」** |
| SC-1102 | `get_mass_property_override_options` 把 COM 失败**包成 `RuntimeError`**，消息含成员名 + 「不可用」 |
| SC-1103 | 两处 docstring 写明「**跑不通 / 不可用**」与「**后端**」（文档串与代码同步）|
| SC-1104 | 上述三条由**桩测**钉住（不连 COM）⇒ `tests/test_dead_capability_diagnostics.py` **3 passed** |
| SC-1105 | 门禁 + 回归不退化（本次因改了运行时文件，需同步签名审计表与报告数字）|

## 明确不做
不换 COM 后端（`comtypes` / 进程内 C++）—— 那是**另一个量级**的工程，超范围。
"""

plan = """# 015 · Plan

**不重造**：沿用仓库对 `IModeler.Create*Surface` 的既有修法（`sw_surface._invoke` 的注释先例）。

## 步骤
1. 查权威类型库确认成员**存在**（`iface_sldworks.txt`）⇒ 排除"名字写错"
2. 真机探测三种参数数 ⇒ 排除"参数没调对"
3. ⇒ 定性为**后端能力问题**
4. 修：**判空再调** + **COM 失败包成 RuntimeError**，消息带成员名与后端
5. 桩测钉住"抛什么"
6. 收工（**改了运行时文件 ⇒ 必须同步签名审计表与报告数字**）

## 风险与对策
| 风险 | 对策 |
|---|---|
| 为了"修好"而反复试参数（事实 53）| 探测**一次**三种参数数就停，定性为后端问题 |
| 文档串与代码不同步 | SC-1103 由测试钉住（本仓库踩过这个坑）|
| 改了运行时文件忘同步 | 同步签名审计表 + 报告数字 + `sync_bundled_skill` |
"""

tasks = """# 015 · Tasks（全部完成，轮 95）

- [x] T-1101 查权威类型库确认两个成员**存在**
  `→ 验收:` `Select-String scripts\\sw_api_sldworks.py -Pattern 'InsertWeldmentCutList'`
- [x] T-1102 真机探测 `GetMassProperties` 三种参数数 + `GetMassProperties2`
- [x] T-1103 定性：**后端能力问题**，非参数问题
- [x] T-1104 修 `sw_weldment.create_cut_list`（判空 + 可诊断消息）
  `→ 验收:` `python -m pytest tests/test_dead_capability_diagnostics.py -q`
- [x] T-1105 修 `sw_export.get_mass_property_override_options`（包 COM 失败）
- [x] T-1106 桩测 `tests/test_dead_capability_diagnostics.py`（**3 passed**）
- [x] T-1107 同步签名审计表（`sw_weldment.py` 71→72）与报告数字
- [x] T-1108 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 015 · Converge

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
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
