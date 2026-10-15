import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ── 事实 107 ────────────────────────────────────────────────────────
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
FACT = "| 107 | " + "".join([
    "**模态框：`MoldUndercutDetect` 参数名与官方全不对应 ⇒ 空零件上弹「此拔模方向尚未定义。」并**静默挂起**；",
    "已根因解决 + 建立**零硬编码**的检测/点掉机制** —— 2026-10-01（轮 167，**由用户截图发现**）。",
    "### 一、根因（读官方 md 读出，不猜）",
    "官方签名：`MoldUndercutDetect(Int32 ColUndercut, Int32 ColBase, **bool BCoordInput**, Double Dx, Double Dy, Double Dz)`；",
    "md 原文：`BCoordInput` = \"True to enable coordinate input to control the direction of pull\"，`Dx/Dy/Dz` = \"direction of pull\"。",
    "★ 而仓库旧签名是 `(direction, option, include_hidden, a, b, c)` ⇒ **第 3 位传 `include_hidden=False`**，",
    "**恰好落在官方第 3 参 `BCoordInput` 上** ⇒ 「**不启用坐标输入**」⇒ 退回「用模型已定义方向」",
    "⇒ **空零件上没有已定义方向** ⇒ 弹「此拔模方向尚未定义。」。",
    "### 二、★★★ 弹框会**静默挂起**，而**点掉之后调用方察觉不到**",
    "端到端实测（`tools/verify_modal_dialog_lifecycle.py`）：触发进程**自己报「竟然没弹框就返回了」**，",
    "而前台**在同一时刻确实抓到并点掉了 1 个模态框** ⇒ ★★ **有人点 ⇒ 调用看起来「成功」；没人点 ⇒ 永久挂起**。",
    "（用户看到的「卡住一动不动」就是这个。）",
    "### 三、★★ 模态框是**异步**弹出的 ⇒ 一次性检查会漏",
    "实测：**第 0.86 秒**才出现（另一轮 2.5 秒）。⚠ 各工具原先在收尾**只查一次** ⇒",
    "**检查通过 ≠ 不会弹框**（那次会话就是这样谎报「无残留」的）。⇒ 必须**轮询**。",
    "### 四、★★★ 零硬编码（用户明确要求「禁止硬编码」）",
    "```",
    "PID   ：ISldWorks.GetProcessID()（官方反射）—— 此前 **36 处**写死 SW_PID = 20456",
    "        ⇒ 失效表现是「查不到残留模态框」＝ **一个静默失效的安全检查**（比没有更糟）",
    "对话框：Win32 预定义类 **#32770**（WC_DIALOG）",
    "点掉  ：发 **WM_COMMAND + IDOK**（Win32 标准命令）—— **不看按钮叫什么**（中文「确定」/英文 OK 都行）、不按坐标",
    "```",
    "★ 共享函数 `sw_connect`：`solidworks_process_id(sw)` · `count_residual_dialogs(target=None)`（**只读**）·",
    "`dismiss_residual_dialogs(target=None)`；`target=None` 时**自己连 COM 派生** ⇒ 调用方 `residual_dialogs()` 无参即可。",
    "★ 迁移实测：**40 个文件 · 常量删 36/36 · 调用改 34/34 · 0 个语法坏 · 无意外删除**。",
    "### 五、两条易错",
    "① **发现与点掉要分开计数** —— 混在一个计数里时我把「已点掉」读成了「没点掉」（已加只读的 `count_*`）；",
    "② **复现要用空零件** —— **有实体**的零件上 SolidWorks 能自己推断方向 ⇒ **不弹框**（第一次复现因此失败）。",
    "### 六、连带修正",
    "`sw_mold.mold_undercut_detect` 参数名照官方改（`col_undercut`/`col_base`/`b_coord_input`/`dx`/`dy`/`dz`，",
    "默认 `b_coord_input=True` + `(0,0,1)`）+ **零向量当场 `ValueError`**（不许把零向量送进去）；",
    "MCP 工具 spec（`tool_specs_batch9.py`）同步改名 ⇒ 回归 **1247 passed**。",
    " | `tools/verify_modal_dialog_lifecycle.py`；`D:/AI/SW/probe`；`scripts/sw_connect.py` 的 `solidworks_process_id`；",
    "`C:/swapi/types/IFeatureManager/MoldUndercutDetect2.md`；事实 61 / 64 / 88 |",
])
if "| 107 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 107")
else:
    print("  已有 107")

# ── Spec Kit 087 ────────────────────────────────────────────────────
S = Path(r"D:\AI\SW\specs\087-modal-dialog-root-cause")
S.mkdir(parents=True, exist_ok=True)
spec = """# 087 · 模态框根因：参数名不对 ⇒ 弹框并**静默挂起**；建立**零硬编码**的检测/点掉机制

**Status**: Implemented（轮 167）· 由**用户截图**发现（我卡住不动）

## 一、用户给的三条要求
> 「你要根因解决，先排查为啥会触发，然后再重复看看如果又触发了怎么发现怎么点掉。**禁止硬编码**」

## 二、★ 根因（读官方 md 读出，不猜）
```
官方：MoldUndercutDetect(Int32 ColUndercut, Int32 ColBase, **bool BCoordInput**, Double Dx, Double Dy, Double Dz)
md 原文：BCoordInput = "True to enable coordinate input to control the direction of pull"
        Dx/Dy/Dz      = "direction of pull"
★ 仓库旧签名 (direction, option, **include_hidden**, a, b, c)
  ⇒ 第 3 位传 include_hidden=False ⇒ **恰好落在官方第 3 参 BCoordInput 上**
  ⇒ 「不启用坐标输入」⇒ 退回「用模型已定义方向」
  ⇒ 空零件上没有已定义方向 ⇒ **弹「此拔模方向尚未定义。」**
⇒ ★★★ 根因解决：默认 b_coord_input=True + 非零方向 (0,0,1) ⇒ 不依赖模型 ⇒ **从根上不弹框**
   ＋ 零向量当场 ValueError（不许把"没给方向"当"给了方向"送进去）
```

## 三、★★★ 弹框**静默挂起**，而点掉之后**调用方察觉不到**
```
端到端实测（tools/verify_modal_dialog_lifecycle.py）：
  ③ 第 **0.86 秒** 发现 1 个模态框
  ④ **点掉 1 个**   ⑤ 剩余 0 · 后台退出码 0 ⇒ 解卡
  ── 但触发进程**自己报「竟然没弹框就返回了」** ← ★★ 它**不知道**自己被挡住过
⇒ ★★ 有人点 ⇒ 调用看起来"成功"；没人点 ⇒ **永久挂起**（用户看到的"卡住一动不动"）
```

## 四、★★ 模态框是**异步**的 ⇒ 一次性检查会漏
```
实测：**第 0.86 秒**才出现（另一轮 2.5 秒）
⚠ 各工具原先在收尾**只查一次** ⇒ **检查通过 ≠ 不会弹框**（那次会话谎报「无残留」就是这个原因）
⇒ 必须**轮询**
```

## 五、★★★ 零硬编码（用户明确要求）
| 维度 | 硬编码（旧） | 现在（零硬编码） |
|---|---|---|
| PID | **36 处** `SW_PID = 20456` | `ISldWorks.GetProcessID()`（官方反射）|
| 对话框 | — | Win32 预定义类 **`#32770`**（`WC_DIALOG`）|
| 点掉 | — | **`WM_COMMAND` + `IDOK`** —— **不看按钮文本**、不按坐标 |
| 调用方 | 传 `SW_PID` | `residual_dialogs()` **无参**（`target=None` 自己连 COM 派生）|

★ 迁移实测：**40 个文件 · 常量删 36/36 · 调用改 34/34 · 0 个语法坏 · 无意外删除**。

## 六、两条易错（我都犯过）
```
① **发现与点掉要分开计数** —— 混在一个计数里时我把「已点掉」读成了「没点掉」
   ⇒ 已加只读的 `count_residual_dialogs`
② **复现要用空零件** —— **有实体**的零件上 SolidWorks 能自己推断方向 ⇒ **不弹框**
   （第一次复现因此失败：「竟然没弹框就返回了」）
```

## 七、判据
| ID | 判据 |
|---|---|
| SC-8701 | ★★★ **根因**：读官方 md 得出「第 3 参是 `BCoordInput`」⇒ 空零件弹框 |
| SC-8702 | ★★★ **根因解决**：默认坐标输入 + 非零方向 ⇒ **不弹框**（真机复跑：无 `#32770`）|
| SC-8703 | ★★★ **故意复现 + 发现 + 点掉 + 解卡**（端到端 4 步全成立）|
| SC-8704 | ★★ **零硬编码**：PID 从 COM 派生（36 处硬编码清零）· 不认按钮文本 |
| SC-8705 | ★ **轮询**（实测第 0.86 秒才出现 ⇒ 一次性检查会漏）|
| SC-8706 | ★ 发现/点掉**分开计数**；零向量**当场拒绝** + 契约测试 |
| SC-8707 | MCP 工具 spec 同步改名 ⇒ 回归 **1247 passed** · `release_check` exit 0 |

## ⚠ 明确记下的限度
* ⚠ `MoldUndercutDetect` 官方标 **Obsolete**（后继 `MoldUndercutDetect2`）⇒ 语义仍**未查证**；
* ⚠ 只处理**模态对话框**（`#32770`）—— 其它形态（如浮动面板）不在内；
* ⚠ 「点掉」的假设是**默认按钮 = 安全动作**；⚠ 若某对话框的默认按钮是**破坏性**的，点掉可能不是无害的
  （本仓库的用法里未遇到，但这是个**未验证的假设**）；
* ⚠ 其余 35 个文件的硬编码清了，但**别处是否还有别的形态的硬编码**本轮**未全面扫**。
"""
plan = """# 087 · Plan

## 步骤
1. 用户截图指出：弹窗「此拔模方向尚未定义。」而我卡住不动
2. ★ **先查根因**（不先点掉）：读官方 md ⇒ 第 3 参是 `BCoordInput`
3. ⇒ 仓库旧参数名把 `include_hidden=False` 送到了 `BCoordInput` ⇒ 退回"用模型方向" ⇒ 空零件弹框
4. ★★★ **根因解决**：默认 `b_coord_input=True` + (0,0,1) ⇒ 不弹框（真机复跑确认无 `#32770`）
5. ★★ 建**零硬编码**机制：PID 从 `GetProcessID()` 派生 · `#32770` · `WM_COMMAND/IDOK`
6. ★★ **故意复现** + 轮询发现 + 点掉 + 解卡（端到端）
7. ★ 迁移 36 处硬编码（按事实 61 先看 diff 再确认）
8. 事实 107 + 连带修 MCP spec + 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 先点掉、不查根因 | ★ 用户明确要求**先根因**（本轮照做）|
| 硬编码 PID/按钮文本 | ★ **禁止**（用户明确）⇒ 官方 `GetProcessID()` + Win32 常量 |
| 一次检查就报「无残留」 | ★ **轮询**（实测 0.86 秒才出现）|
| 批量替换切坏文件 | ★ 事实 61：跑完先看 `git diff --stat` + 逐类核对删除数 |
| 复现不出来就以为没事 | ★ 第一次复现**失败**（有实体不弹）⇒ 换成空零件才复现 |
"""
tasks = """# 087 · Tasks（全部完成，轮 167）

- [x] T-8701 读官方 md 查根因（`BCoordInput` 参数名与语义）
- [x] T-8702 ★★★ 根因解决：默认坐标输入 + 非零方向 `→ 验收:` `python tools/verify_batch9_smoke.py`（**不再弹框**）
- [x] T-8703 ★★ 零硬编码机制 `→ 验收:` `python -c "import sw_connect; print(sw_connect._resolve_pid(None))"`
- [x] T-8704 ★★★ 端到端复现 `→ 验收:` `python tools/verify_modal_dialog_lifecycle.py`（**发现 1 / 点掉 1 / 解卡**）
- [x] T-8705 迁移 36 处硬编码（常量删 36/36 · 调用改 34/34 · 0 语法坏）
- [x] T-8706 契约测试 + MCP spec 改名 `→ 验收:` `python -m pytest tests/test_sw_mold_contract.py -q`（**10 passed**）
- [x] T-8707 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）· **1247 passed**
"""
converge = """# 087 · Converge

**Converged**: 2026-10-01（轮 167）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-8701 根因 | ✅ `BCoordInput` 收到 `False` |
| SC-8702 根因解决 | ✅ 真机复跑无 `#32770` |
| SC-8703 复现/发现/点掉/解卡 | ✅ 0.86 秒发现 · 点掉 1 · 退出码 0 |
| SC-8704 零硬编码 | ✅ 36 处清零 |
| SC-8705 轮询 | ✅ |
| SC-8706 分开计数 + 零向量拒绝 | ✅ 10 passed |
| SC-8707 门禁 + 回归 | ✅ exit 0 · **1247 passed** |

## 二、★★★ 本轮最重要的发现：**模态框会静默挂起，而调用方察觉不到**
```
端到端实测里，触发进程**自己报「竟然没弹框就返回了」** ——
而前台**在同一时刻确实抓到并点掉了 1 个模态框**。
⇒ ★★ **有人点 ⇒ 调用看起来"成功"；没人点 ⇒ 永久挂起。**
⇒ 这解释了这个仓库**最危险**的失效形态：**不是报错，是安静地停住。**
```

## 三、★ 一次「先根因、后处置」的正确顺序
```
用户要求「先排查为啥会触发」—— 若我直接去点弹窗，就会**留下一个每次都会弹的调用**
（而且它的表现是"成功"）⇒ 下一个人还会踩。
⇒ ★ 根因解决后**它根本不弹** ⇒ 点掉机制退化为**兜底**（仍需要，但不该被依赖）。
```

## 四、未查证
* ⚠ `MoldUndercutDetect` 官方标 Obsolete，语义未查证；
* ⚠ 只处理 `#32770`；其它形态（浮动面板）不在内；
* ⚠ **「默认按钮是安全的」这个假设未验证** —— 若某对话框默认按钮是破坏性的，点掉就不无害；
* ⚠ 别处是否还有别的形态的硬编码，本轮未全面扫。
"""
for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
