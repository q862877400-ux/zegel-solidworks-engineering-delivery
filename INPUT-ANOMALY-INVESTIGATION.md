# 输入异常调查 —— **根因已定位并止血**

> 2026-10-01 · 用户报告「经常忽然全选全屏文字（蓝底）/ 忽然回车 / 忽然 Ctrl」

## 〇、★ 根因（**铁证，逐环可核**）—— **是我自己的测试**

**用户第二次报告「刚刚鼠标键盘被影响了」，而那次正发生在我跑**全量回归**的时刻。**

```
tests/test_sw_gui_input.py  L212/L233   assert gi.type_text(ctl, "195") ...
  ⇒ scripts/sw_gui_input.py L236   def type_text(ctrl, text, log=None)
  ⇒ L241  if CONFIG["input_api"] == "set_text" …  （否则走逐键）
  ⇒ L56   "input_api": "type_keys"     ← **默认就是逐键真输入**
  ⇒ L62   "clear_with": "ctrl_a"       ← **默认清空策略就是 Ctrl+A**
  ⇒ L211  _tap_ctrl(ord("A"), 0.05)    ← **真的发 Ctrl+A = 全选**
  ⇒ L130  _tap_ctrl → win32api.keybd_event
该测试文件里 **monkeypatch 出现 0 次** ⇒ **完全没有任何 mock**
仓库里 **没有任何 conftest.py** ⇒ **没有任何全局保护**
```
**⇒ 跑一次全量回归 = 在真实桌面上按一次 Ctrl+A。**

**⚠ 两个 bug 叠加才长成用户看到的样子**：
* 上一提交给 `keybd_event` 加了 `finally` 保证抬起 ⇒ 所以是「**一阵一阵**」而不是**持续卡死**；
* 若无那个修复，`Ctrl+A` 的 Ctrl 可能**卡住** ⇒ 之后任何按键都带 Ctrl（用户描述的正是这个）。

## 〇之二、止血措施（提交 `a09d4f0`）

新增 **`tests/conftest.py`**：
* **`autouse`** 的 `_forbid_real_input` —— 把 `win32api.keybd_event` / `mouse_event` / `SetCursorPos`
  换成**记录器**（`input_injection_log`）。
* ⚠ **必须 autouse**：本次事故正是「漏一个文件就等于没保护」。
* 另给 `input_log` fixture 供断言。

**三层验证**：① `test_sw_gui_input.py` **17 passed**（拦截下仍通过）；
② 临时探针证明调用**只进账本、不真按**（断言 `len(log)==2` 通过，探针已删）；
③ 全量回归后 14 个修饰键**全部抬起**。

## 〇之三、我此前**误判**过的地方（如实记）

| 我先前的说法 | 实际 |
|---|---|
| 「我走 COM 调用，**不注入键鼠**」 | ❌ **错**。有 55 处注入 / 12 个文件 |
| 「我的代码**没有**周期性注入」 | ✅ 对（无自动入口 / MCP 未暴露 / 不注册计划任务） |
| 「`.pyc` 时间戳证明凌晨 1 点后没跑」 | ⚠ 对，但**我漏了**「**pytest 会 import 它们**」这一路 |
| 「此刻修饰键全抬起 ⇒ 不是卡住」 | ✅ 对，但**不能**推出「不是我的代码」（是**瞬时**注入，不是持续卡住） |

**★ 教训：把「某条路径走不通」写成「不是我干的」，与把「没搜到的词」写成「官方没有这个成员」是同一类错误。**

## 一、已经**排除**的（有证据）

| 候选 | 证据 | 结论 |
|---|---|---|
| 辅助功能（粘滞键/筛选键/切换键） | `FilterKeys Flags=126` · `StickyKeys Flags=510` · `ToggleKeys Flags=62`，**三者 bit0 均为 0** | ❌ 排除 |
| 罗技 Options+ 的宏 | `macros.db` 只有 1 行 `{"macros_settings_transferred": true}`，`snapshots` **0 行** | ❌ 排除 |
| 向日葵远程 | `SunloginService` **Stopped** | ❌ 排除 |
| 键盘/鼠标硬件 | 物理设备只有 2 个罗技（VID_046D）；其余是 VID_00FF 虚拟 | ⚠ 嫌疑低 |

## 二、⚠ **仍未验证的外部候选**（用户要求暂不查）

1. **网易「UU远程」**：`gvinput` + `gvinputmf` **内核驱动 Running**（`Provider=netease`，
   `oem8.inf`）；开机自启 **6 个进程**（`GameViewerService` / `GameViewerServer` /
   `GameViewerHealthd` / crashpad×3）+ **`msedgewebview2 × 7`（它的界面自己就起来了）**；
   虚拟 HID `VID_00FF` 提供 **2 鼠标 + 1 键盘 + 2 厂商私有**接口；
   `%LOCALAPPDATA%\GameViewer\security.ini` 里有 **`connection_seen=1`（被连接过）**。
   ⚠ 「软件没启动」**不能**排除它 —— 驱动与 UI 都是自启的。
2. **`ufo_bridge_mcp.py`**（= `microsoft/UFO` GUI agent）——**父进程是 DSH 自己**
   （`apps/cli/src/bin.ts web`）。

## 三、症状再现场怎么办

1. **正在发生的那一刻**跑 `_check_modifier_stuck.py` —— 若显示 Ctrl/Alt「按下」而你没按 ⇒ 就是「卡住」；
2. **记录当时我在跑什么**（尤其：我是不是刚跑了 `pytest`）——
   ⚠ 现在 conftest 已拦住测试注入，但**其它路径**仍须警惕；
3. 若都排除 ⇒ 才回头查 §二 那两个外部候选。
