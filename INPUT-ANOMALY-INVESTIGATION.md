# 输入异常调查 —— 重启前证据快照 + 重启后清单

> 快照时间：2026-10-01 · 用户报告「经常忽然全选全屏文字（蓝底）/ 忽然回车 / 忽然 Ctrl」
> ⚠ **重启会杀掉所有进程 ⇒ 本文件里的 PID 与进程表重启后失效，但"当时谁在跑"这一事实必须留存。**

## 一、已经**排除**的（有证据）

| 候选 | 证据 | 结论 |
|---|---|---|
| 辅助功能（粘滞键/筛选键/切换键） | `FilterKeys Flags=126` · `StickyKeys Flags=510` · `ToggleKeys Flags=62`，**三者 bit0 均为 0** | ❌ 排除 |
| 罗技 Options+ 的宏 | `%LOCALAPPDATA%\LogiOptionsPlus\macros.db` 只有 1 行 `{"macros_settings_transferred": true}`，`snapshots` **0 行** | ❌ 宏没有内容（但进程常驻，见 §三） |
| 向日葵远程 | `SunloginService` **Stopped** | ❌ 排除（`OrayUSBVHCI` 驱动仍在，见 §三） |
| 键盘/鼠标硬件（多个设备冲突） | 3 键盘 / 4 鼠标，其中 3 个是 **VID_00FF 虚拟设备**（见下） | ⚠ **物理设备只有 2 个罗技**（VID_046D ×2）⇒ 硬件嫌疑低 |

## 二、⚠ **重启前的关键发现（未验证完）**

### 2.1 虚拟键鼠设备 = 网易「UU远程」的 `gvinput` 驱动
```
设备      : HID\GVINPUT&COL01..COL05（5 个接口：2 鼠标 + 1 **键盘** + 2 厂商私有）
HardwareId: HID\VID_**00FF**&UP:0001_U:0006     ← VID_00FF 不是真实厂商
Parent    : ROOT\HIDCLASS\0000                  ← ROOT\ = **纯软件创建**
驱动      : oem8.inf · 服务 gvinput / gvinputmf · **Provider = netease**
驱动文件  : C:\Windows\system32\drivers\gvinput.sys (26.7 KB) / gvinputmf.sys (23.2 KB)
服务状态  : **两者均 State=Running**（StartMode=Manual）
程序      : D:\Program Files\Netease\GameViewer\  （卸载项名 **「UU远程」**，发布者 Netease，v4.39.2.1561）
            安装于 **2026-09-08 09:59**，2026-09-14 更新过一次
自启      : HKCU\...\Run\GameViewer = "...\GameViewer.exe" --auto-run
Trace     : %LOCALAPPDATA%\GameViewer\security.ini 里有 **connection_seen=1**（**被连接过**）
            setting.ini 里有 remoteassist_guide=true · trusted_web_app_domain 含 *.webapp.163.com
```
⚠ **用户反馈「软件都没启动，现象还在」** —— 这条**不能**用来排除它：
**`gvinput.sys` 是**内核驱动**，`GameViewerService` 是**Windows 服务**，
两者都在跑；不开 `GameViewer.exe` 界面**不代表**驱动没在注入。**
⇒ **但仍未证明它就是元凶** —— 只证明了「它有能力注入且当时在跑」。

### 2.2 ★★ **`ufo_bridge_mcp.py` —— 父进程是 DSH 自己**
```
PID 7872   D:/AI/oss-research-and-deployments/UFO/.venv/Scripts/python.exe ufo_bridge_mcp.py
   └─ 父进程 2576 = node.exe --import tsx/esm **D:\AI\DSH\deepseek-harness\apps\cli\src\bin.ts web**
                    ↑ **DSH 的 Web CLI（就是用户正在用的这个 GUI 的后端）**
PID 33352  7872 的子进程（另一套 python）
```
**🔴 `UFO` = `microsoft/UFO`（微软的 **GUI 自动化 agent**）—— 它的**工作方式就是注入键鼠**。**
**⇒ 它是**被 DSH 拉起**的 MCP 桥 ⇒ 只要有任何一次工具调用打到它，它就会操作真实键鼠。**

### 2.3 ⚠ **我自己的代码也有键鼠注入（我上轮错误地否认过）**
```
scripts/sw_gui_input.py     keybd_event(VK_CONTROL)         ← Ctrl
scripts/sw_gui_focus.py     keybd_event(VK_MENU)            ← Alt
scripts/sw_gui_modal.py     keybd_event(VK_MENU / vk)
scripts/sw_jlcfa_fill.py    keybd_event(VK_CONTROL)
scripts/sw_jlcfa_cards.py   mouse_event(LEFTDOWN/LEFTUP)    ← 鼠标左键
scripts/sw_jlcfa_click.py   mouse_event(LEFTDOWN/LEFTUP)
```
**🔴 发现一个真实缺陷模式**：`sw_gui_input.py::_tap_ctrl()` 是
```python
keybd_event(VK_CONTROL, 0, 0, 0)      # 按下
_tap(vk, 0.03)                         # ⚠ 这一步若抛异常…
keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)   # ⇒ 抬起到了不了 ⇒ **Ctrl 卡在按下态**
```
**⇒ 没有 `try/finally`。Ctrl 卡住会让之后**任何**按键都变成 `Ctrl+xxx` ⇒ 完全吻合「忽然 Ctrl / 忽然全选」。**
（`sw_jlcfa_fill.py` 的 Ctrl 段落有同样问题。）
⇒ **待办**：给这两处加 `try/finally` 保证 KEYUP（**这是与用户现象高度吻合的真缺陷**）。

## 三、重启后要查的清单（**按优先级**）

1. **DSH 的 MCP 配置里有没有 `ufo_bridge_mcp`** —— 查 `~/.dsh/` 下 MCP 配置与该 server 的定义，
   以及**谁在调它**（本轮 `ufo_bridge_mcp.py` 由 DSH 拉起，这条最可疑）。
   ⚠ 若确认它在被调用，**先把它停掉**再看现象是否消失（**判定性实验**）。
2. **重启后立刻再抓一次进程表**（`ufo_bridge_mcp` / `GameViewer*` / `gvinput*` 是否自动起来），
   与 §二 的快照对比 ⇒ 分清「谁常驻」与「谁是被拉起的」。
3. **`gvinput` 的判定性实验**（用户自己决定，我不动系统）：
   停 `GameViewerService` + 禁用 `gvinput`/`gvinputmf` 驱动 ⇒ 观察现象是否消失。
   ⚠ 但**先做第 1 项**（成本更低，且 DSH 侧我能查）。
4. **给 `_tap_ctrl` / `sw_jlcfa_fill` 的 Ctrl 加 `try/finally`**（我自己的真缺陷）。
5. ⚠ 需要时再查：`ctxusbm`（Citrix USB Monitor，`StartMode=Auto`）、`OrayUSBVHCI`（向日葵 USB 虚拟，
   服务已停但驱动在）—— 两者也在 §二 的驱动清单里，但**优先级低于 1–3**。

## 四、另一件**独立**的事（别和上面的混）

**「莫名其妙自己又继续了」= **goal 自动续轮**，不是键盘触发。**
证据：`roundsStarted=62` 而用户上一轮说过「暂停」⇒ 我**只收了工作、没把 goal 置 paused** ⇒ 机制自动开了轮 62。
**⇒ 这不是输入设备问题。** 现在 `phase=paused`；重启后会是 `disarmed`，用户说「继续」时再 `update_goal resume`。
