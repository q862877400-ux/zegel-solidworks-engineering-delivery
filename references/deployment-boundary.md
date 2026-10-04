# 交付边界：这个项目会/不会动别人的机器与软件

> ★ 起因：业主问「你这个相当于是修改 SolidWorks 是吗？那别人装上，岂不是也要改他的软件？」
> ★ 本文是**实测核查的结论**（不是承诺），每条都带证据；★ 查不到的写「查不到」。

---

## 一 · 一句话结论

> ★ **本体零改动**：全仓**没有**一处写 SolidWorks 注册表、**没有**写安装目录、**没有**打补丁 / 注入 DLL，
> 全程走**官方公开的 COM API** —— 等同于用户自己在界面里点、或录一个宏。
> ★★ **但有一处真落点**：曾经有 **8 处**直接改用户的 **SolidWorks 全局用户偏好**且**多数不还原**
> ⇒ ★ 那等于"装一次我们的工具，他的设置被改掉且回不去"。**本轮已收口**（见 §三）。

---

## 二 · 核查证据（实测，逐条可复现）

| 检查项 | 结果 | 怎么查的 |
|---|---|---|
| 注册表**写入** | ★ **0 处** | AST 扫全仓 `SetValue*` / `CreateKey*` / `DeleteKey*`：唯一命中是 `tests/test_sw_topology_contract.py:303` 的 `fake.SetValue(75.0)` —— ★ 那是 `_FakeCom` **假对象**，与注册表无关 |
| 注册表**读取** | 28 处，**全是只读** | `cad_installation.py`（找安装位置）· `sw_routing.py` / `sw_featureworks.py`（查 add-in 有没有注册）· `probe_costing_manager.py`（读 ProgID）⇒ 只读不写 |
| SolidWorks 安装目录 | ★ **不写** | 全仓无对 `Program Files\SOLIDWORKS Corp` 的写操作 |
| 打补丁 / 注入 / Hook | ★ **没有** | 无 DLL 注入、无 API Hook、无进程内存改写 |
| 全局环境变量 | ★ **不写** | `fea_analysis.py` 只有**读**（为对照） |
| 用户偏好（**唯一的落点**） | ⚠ 曾有 **8 处**裸写 | 见 §三 |
| 可选的 C# Add-in | ⚠ **会写注册表**（可选、有卸载） | 见 §四 |

---

## 三 · 那一处真落点：SolidWorks **全局用户偏好**（★ 本轮已收口）

### 3.1 原来是什么样（8 处，多数**永不还原**）

| 位置 | 改什么 | 触发时机 |
|---|---|---|
| `scripts/sw_connect.py` `ensure_default_templates` | ★ **默认模板路径 ×3** + 关掉"新建提示" | 导入外来 CAD 文件（`LoadFile4`）那条路 |
| `scripts/sw_export.py` `export_to_stl` | ★ **STL 导出精细度**（偏好号 78） | 每次导 STL |
| `scripts/sw_import_mesh_reference.py` | ★ **STL/VRML 导入选项 ×6**（3 个 int + 3 个 toggle） | 每次导入网格 |
| `subskills/solidworks-fillet-chamfer-cnc/scripts/verify_advanced_fillets.py` | 隐藏原点/参考三轴 | 跑该验证时 |
| `…/verify_open_source_complex_case.py` | 同上 | 同上 |
| `_sw_export_backup.py` | STL 精细度（★ **死代码**：全仓 0 引用） | — （已进豁免名单，带理由） |

★ **为什么这是个问题**：这几条偏好**存在用户的 SolidWorks 配置里**（不是文档里），
★ 所以"用一次就永久改掉"—— ★ 与"替他点一下界面"完全不是一回事。

### 3.2 现在的样子（三条纪律 + 一道门禁）

1. ★ **新增 `scripts/sw_preference_guard.py`** —— **唯一被认可的写入姿势**：
   `with preference_guard(obj, [Preference(kind, pref_id, value, why=…)]) as rep:`
   · 读旧值 → 设 → **`finally` 还原**（★ 连异常路径也还原）；
   · **值本来相同就不写**（不制造无谓历史）；
   · **旧值读不到的条目不写**（★ 否则那条设置**永远回不去**）；
   · 还原后**读回校验**并给 `match`；★ 失败进 `restore_errors`、**不吞**；
   · `keep=` / `restore=False` 是**唯一**能留下的路，且**必须在报告里说出来**。
   ⇒ ★ 由 `tests/test_preference_guard.py`（**10 passed**）用负例逐条证明
   （★ 含"异常路径也还原"·"读不到旧值就不写"·"只差大小写不算变"·"还原失败必须可见"）。
2. ★ **各站点改成成对写法**："设"的地方**记下旧值**，"还原"的地方**写回**，且**在 `finally` 里**：
   · `sw_connect.py`：`ensure_default_templates` ↔ `restore_default_templates`（包在 `LoadFile4` 的 `try/finally`）；
   · `sw_import_mesh_reference.py`：`configure_mesh_import_preferences` ↔ `restore_mesh_import_preferences`；
   · `sw_export.py::export_to_stl`：直接用 `preference_guard` 包住导出；
   · 两个 subskill 验证脚本：`hide_review_helpers` 返回旧值 ↔ `restore_review_helpers`，出图后 `finally` 还原。
3. ★ **新增硬门禁 `scripts/check_user_preference_writes.py`**（已接进 `release_check`，第 **28** 道）：
   扫全仓 `SetUserPreference*`，每处必须满足之一 ——
   ① 落在 `with preference_guard(...)` 里；② 所在函数带**非空理由**的 `preference-guard:` 标记；
   ③ 进 `docs/preference-write-exemptions.json`（★ 每条必须带 `reason` + `evidence`）。
   ★ 由 `tests/test_user_preference_writes_gate.py`（**7 passed**）负例证明 ——
   ★ 正例取自 **`git show` 的修复前原文**；★ 并含「只有标记、没有理由 ⇒ **必须仍被抓**」那一条。
   ⚠ **边界**：它保证"走过守卫 / 写过理由"，**不证明"还原真的生效"**（★ 后者由 guard 的 10 条负例在做）。

---

## 四 · 唯一真需要动系统的地方：**可选的** C# Add-in

| 模式 | 写什么 | 权限 |
|---|---|---|
| **CurrentUser** | `HKCU\Software\Classes\{ProgId, CLSID}` + `HKCU\Software\SOLIDWORKS\Addins\{GUID}` + `AddInsStartup\{GUID}` | ★ **免提权** |
| **Machine** | 64 位 `RegAsm /codebase /tlb` + `HKLM\SOFTWARE\SOLIDWORKS\Addins\{GUID}` | ⚠ **需要管理员** |

★ 它**只在**需要 PropertyManagerPage / TaskPane / 长期驻留 UI 时才用；★ 有 **`/unregister`** 卸载路径；
★ 读侧检查是 `solidworks_addin_host_status`（**只读**）；★ README 已把它列为 pilot。
⇒ ★ **默认交付不需要它**。

---

## 五 · 别人装上以后的真实清单

**必须**：
- ★ **已授权的** SolidWorks（我们只用它的公开 COM API；★ 不做、也不含任何破解/绕过）
- Python + 我们的 MCP server（`mcp-server/`）
- ★ **同一时刻只跑一个** SolidWorks MCP（事实 24：多进程抢同一 COM 连接会死锁）

**不需要**：管理员权限（除非选 Machine 模式 Add-in）· 改 SolidWorks 安装 · 动注册表 · 网络（除可选同步）
**默认不会再留下**：用户的 SolidityWorks 全局偏好改动（★ 这是本轮收的）

---

## 六 · 可复用定则

> ★★★★ **「驱动软件」与「修改软件」的分界，看**改动存在哪里****：
> · 改**文档/算例内**的东西（study 设置、模型、视图、图纸）⇒ ★ **用软件**：随文件走、可回退 ✓
> · 改**全局用户偏好 / 注册表 / 安装目录** ⇒ ★★ **动他的软件**：**必须可还原**，或**显式声明并给卸载路径** ✓
> · ★ 判据：**"卸载我们之后，他机器上还剩什么"** —— ★ 凡答不上来的，就是没收口的 ✓

★ 与**事实 40** 的关系：40 说「一个存在但没人用的守卫 = 没有守卫」；
★★ **本轮是它的延伸**：★ **守卫要挂门禁，门禁要有负例**（★ 否则"我们改了守卫"只是自我感觉）✓
