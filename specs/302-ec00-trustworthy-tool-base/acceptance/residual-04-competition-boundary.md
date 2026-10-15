# 残留 ④ 收口 —— 真机双客户端 COM 竞争的**永久边界**（★ 有据的 `blocked`）

**Feature**: `specs/302-ec00-trustworthy-tool-base/`
**日期**: 2026-10-10
**对应**: ★ 清 **EC00 残留 ④**（★ T027 的「真机双客户端 COM 竞争」原记 `blocked`，★ 现定**永久边界**）
**证据**: `output/_probe_t027_mutex.json` · ★ 判据 `tests/test_ec00_t027_recovery.py`

---

## 一、★★★★★ 为什么这条**永久**不做（★ 三条独立依据）

### 依据 ① · ★★ 官方外的**同源项目**逐字（★ `Slacker-LLC` · **Apache-2.0** ⇒ 可引）

★★★ `C:\swprojects\Slacker-LLC\README.md` **逐字**（★ `## Known limitations` 段 · ★ **原文在 `Two` 后换行**）：

> ★ **One SOLIDWORKS session, one COM apartment: tool calls are serialised. Two
> clients driving the same session at once will deadlock it.**

★★ **⇒ 逐字（★ 去掉排版换行后）**：★
`One SOLIDWORKS session, one COM apartment: tool calls are serialised. Two clients driving the same session at once will deadlock it.`
★★ **注**：★ 原文在 `Two` 之后有一个**排版换行**（★ 引文里已按原文保留）—— ★ 判据会**归一化换行**后比对。

★★ 同仓 `CONTRIBUTING.md` **逐字**：

> ★ **Never open a modal dialog.** One modal box blocks the COM call that opened
> it and **deadlocks the whole server**.

★★★ **⇒ 「两客户端同时驱动一个会话会死锁」是**已被独立观察到的现象****，★ 不是我猜的。

### 依据 ② · ★★ 本仓自己的**硬约束**登记

★ `AGENTS.md` §〇 逐字：★「**运行时只能有一个 SolidWorks MCP**——多个进程抢同一 COM 连接**会死锁**」
★（★ 依据：**已知事实 24**）。

### 依据 ③ · ★★★ COM 的**架构性**原因（★ 不是配置问题）

★ COM 是 **STA**（单线程单元）且**线程亲和** —— ★ `AGENTS.md` 铁律 2 逐字：
★「COM 是 STA 且线程亲和，★ **调用一旦开始无法强制中止**」。
★★★ **⇒ 「两个客户端同时改」在**架构上**就不成立** ⇒ ★ 不是「本机没配好」。

---

## 二、★★★★ 那为什么**不能**用「跑一次试试」来验

★★★ **T027 完成判据逐字**：★「★ **不故意破坏用户会话，不盲重试/危险确认**」。

| ★ 若真的去抢 | ★ 后果 |
|---|---|
| ★ 两个进程同时 `GetActiveObject` 并发改 | ★★ **死锁** ⇒ ★ **SolidWorks 卡死**（★ 那正是依据 ① 说的） |
| ★ 死锁之后 | ★★ 要么**强杀 SW**（★ 丢用户的未保存工作）★ 要么**等**（★ 无人值守挂死） |
| ★★★ **⇒ 代价** | ★ **破坏用户会话** —— ★ 那是 T027 **明文禁止**的 |

★★★ **⇒ 这是「无**安全**复现条件」**，★ 不是「懒得验」。

---

## 三、★★★★★ 我**改验**了什么（★ 那才是能验的部分）

| ★ 验了什么 | ★ 读数 | ★ 依据 |
|---|---|---|
| ★★ **互斥机制存在** | ★ `sw_connect._LaunchGuard`（★ `scripts/sw_connect.py:55`） | ★ 静态核 |
| ★★ **它是**跨进程**的** | ★ **命名 Mutex**（★ `kernel32.CreateMutexW(None, False, name)` —— `sw_connect.py:69`） | ★ 静态核 |
| ★★★ **它真的串行** | ★★ **`['enter:A','exit:A','enter:B','exit:B']`** ⇒ ★ **无交叉** ✓ | ★ 真机（★ `output/_probe_t027_mutex.json`） |
| ★ 释放后可再取 | ★ `True` ✓ | ★ 真机 |
| ★ 有超时（★ 不永久等） | ★ `WaitForSingleObject(handle, 15000)` —— **15 s** | ★ 静态核 |
| ★ 护栏杀冻住的调用 | ★ `True`（★ `taskkill` / `aborted_for_llm`） | ★ 静态核 |

★★★ **⇒ 「最多一个修改者」**机制上**成立** ✓（★ 而「真实双客户端争抢」**架构上不可能安全复现**）。

---

## 四、★★★★★ 永久边界（★ 这条写死）

★★★ **EC00 的边界声明**：

1. ★★ **EC00 只接**现有本地互斥边界**（★ 命名 Mutex + 15 s 超时）** —— ★ 逐字承 `data-model.md` §4.1。
2. ★★★ **完整的节点级租约、围栏令牌、跨主机仲裁属于 EC04** —— ★ EC00 **不做**。
3. ★★★ **真机双客户端 COM 竞争的**端到端**验证**永久不做**** —— ★ 理由见 §一/§二；
   ★★ **替代判据** = ★ 「互斥机制串行」（★ 已有真机读数）+ ★ 「架构原因有据」（★ 三条依据）。
4. ★★ **本条的结论永久为 `blocked`（★ 有据）**，★ **不是 `not_run`（★ 未做）** ——
   ★★ 两者不同：★ `blocked` = **做了能做的，剩下的无安全条件**；★ `not_run` = **没开始**。

★★★ **⇒ 这条边界**本身就是 EC00 的交付物之一**（★ 它让接手方**不再重走**）✓

---

## 五、★★★ 残留 ④ 的收口判据

| ★ # | ★ 判据 | ★ 怎么验 |
|---|---|---|
| ① | ★ 三条依据**可定位**（★ 两个逐字引文 + 一条架构原因） | ★ 本文件 §一 |
| ② | ★ **不能**用「跑一次试试」—— ★ 理由**写明** | ★ 本文件 §二 |
| ③ | ★ **替代判据**有真机读数 | ★ `output/_probe_t027_mutex.json`（★ `serialized=True`） |
| ④ | ★ 边界**写死**（★ 含「永久不做」与 EC04 分工） | ★ 本文件 §四 |
| ⑤ | ★ 结论用 **`blocked`** 而不是 `not_run` | ★ `acceptance/T027-recovery.md` §二 |
