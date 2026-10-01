import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           501 🎯 **Spec Kit `087`：模态框根因 —— 参数名不对 ⇒ 弹框并****静默挂起****；建立****零硬编码****的检测/点掉机制**（轮 167）——
               起因：**用户截图**指出弹窗「此拔模方向尚未定义。」而我卡住不动。
               用户三条要求：「**先排查为啥会触发**，然后再重复看看**如果又触发了怎么发现怎么点掉**。**禁止硬编码**」。
            502 ★★★ **根因（读官方 md 读出，不猜）**：
               ```
               官方：MoldUndercutDetect(Int32 ColUndercut, Int32 ColBase, **bool BCoordInput**,
                                         Double Dx, Double Dy, Double Dz)
               md 原文：BCoordInput = "True to enable coordinate input to control the direction of pull"
                       Dx/Dy/Dz      = "direction of pull"
               ★ 而仓库旧签名是 (direction, option, **include_hidden**, a, b, c)
                 ⇒ 第 3 位传 include_hidden=False ⇒ **恰好落在官方第 3 参 BCoordInput 上**
                 ⇒ 「不启用坐标输入」⇒ 退回「用模型已定义方向」
                 ⇒ **空零件上没定义** ⇒ 弹「此拔模方向尚未定义。」
               ⇒ ★★★ **根因解决**：默认 b_coord_input=True + 非零方向 (0,0,1)
                 ⇒ 不依赖模型 ⇒ **从根上不弹框**（真机复跑确认无 #32770）；
                 并加**零向量当场 ValueError**（不许把"没给方向"当"给了方向"送进去）。
               ```
            503 ★★★ **本轮最重要的发现：模态框会静默挂起，而调用方察觉不到** ——
               端到端实测（`tools/verify_modal_dialog_lifecycle.py`）：
               ```
               ③ 第 **0.86 秒** 发现 1 个模态框   ④ **点掉 1 个**   ⑤ 剩余 0 · 退出码 0 ⇒ 解卡
               ── 而触发进程**自己报「竟然没弹框就返回了」** ← ★★ 它**不知道**自己被挡住过
               ```
               ⇒ ★★ **有人点 ⇒ 调用看起来「成功」；没人点 ⇒ 永久挂起**（用户看到的「卡住一动不动」）。
               ★★★ 这解释了这个仓库**最危险**的失效形态：**不是报错，是安静地停住。**
            504 ★★ **模态框是**异步**弹出的 ⇒ 一次性检查会漏**：实测**第 0.86 秒**才出现（另一轮 2.5 秒）。
               ⚠ 各工具原先在收尾**只查一次** ⇒ **检查通过 ≠ 不会弹框**
               （那次会话谎报「无残留」就是这个原因）⇒ **必须轮询**。
            505 ★★★ **零硬编码**（用户明确要求）：
               ```
               PID   ：ISldWorks.GetProcessID()（官方反射）—— 此前 **36 处**写死 SW_PID = 20456
                       ⇒ 失效表现是「查不到残留模态框」＝ **一个静默失效的安全检查**（比没有更糟）
               对话框：Win32 预定义类 **#32770**（WC_DIALOG）
               点掉  ：发 **WM_COMMAND + IDOK** —— **不看按钮叫什么**（中文「确定」/英文 OK 都行）、不按坐标
               调用方：`residual_dialogs()` **无参**（`target=None` 时自己连 COM 派生 PID）
               ```
               ★ 迁移实测：**40 个文件 · 常量删 36/36 · 调用改 34/34 · 0 个语法坏 · 无意外删除**
                 （★ 事实 61 的定则**这次执行到位**：跑完先看 `git diff --stat` 并逐类核对删除数）。
            506 ★ **两条易错（我都犯过，如实记）**：
               ① **发现与点掉要分开计数** —— 混在一个计数里时我把「已点掉」读成了「没点掉」⇒ 加了只读的
                  `count_residual_dialogs`；② **复现要用空零件** —— **有实体**的零件上 SolidWorks 能自己
                  推断方向 ⇒ **不弹框**（第一次复现因此失败：「竟然没弹框就返回了」）。
               ★ **连带修正**：`sw_mold.mold_undercut_detect` 参数名照官方改；
                 MCP 工具 spec（`tool_specs_batch9.py`）同步改名 ⇒ 回归 **1247 passed**。
            507 ★ **一次「先根因、后处置」的正确顺序**（这是用户要求的）：
               若我**直接去点弹窗**，就会**留下一个每次都会弹的调用**（而且它的表现是"成功"）
               ⇒ 下一个人还会踩。★ 根因解决后**它根本不弹** ⇒ 点掉机制退化为**兜底**（仍需要，但不该被依赖）。
               门禁 + `release_check` exit 0 · 回归 **1247 passed**。
               ⚑ **未查证**：⚠ `MoldUndercutDetect` 官方标 **Obsolete**（后继 `MoldUndercutDetect2`）语义仍**未查证**；
                 ⚠ 只处理 `#32770`，其它形态（浮动面板）不在内；⚠ **「默认按钮是安全的」这个假设未验证** ——
                 若某对话框默认按钮是破坏性的，点掉就不无害；⚠ 别处是否还有别的形态的硬编码，本轮**未全面扫**。
               下轮候选：① 扫别处是否还有硬编码（其它形态）；② 把「轮询式模态框检查」接进各冒烟的收尾；
               ③ 回到 `SetSymbolXml`（frame 已到手）或「真缺」继续补。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+501 ", before, re.M):
    print("  游标 501 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+507 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 507 行已存在 ✓")
