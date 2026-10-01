# 039 · 形位公差的真机冒烟 —— **抓到的是我自己上轮写的缺陷**

**Status**: Implemented（轮 120）

## 一、为什么挑它
`038`（轮 119）刚写了 `sw_gtol.py`，而且**整条路都押在 `IGtolFrame.AddIndicator` 上** ——
它若不成立，模块就是空的。★ 这正是「**验旧的不如验新写的**」。

## 二、真机冒烟：**3/5 —— 一半不通**
```
✓ 新建临时零件（不碰用户文档）
✓ insert_gtol（0 参，官方 InsertGtol()）          拿到 CDispatch
✗ ★ add_gtol_indicator(position, 基准 A)          RuntimeError: IGtol.GetFrame(1) 返回 None
✗   再加一个（flatness，无基准）                   同上
✓ ★ 收尾无残留模态框
```

## 三、★★ 按事实 53 停手：**连量三次，把那一步量清楚了**
| 轮次 | 试法 | 量到的结果 |
|---|---|---|
| 1 | 直接 `GetFrame(1)` | `GetFrameCount()` = **1**，但 `GetFrame(0/1/2)` **全 None** |
| 2 | 先 `AddFrame()` | `AddFrame()` 返回 **False**，计数**没涨** |
| 3 | 先 `CanConvertFormat()`→`ConvertFormat()` | 返回 **0（成功）**，但转换后 `GetFrameCount()` **掉到 0**，`GetFrame(1/2)` **仍全 None** |

⇒ **「2022 格式的帧路径」在本机（SW 2026 SP4.1 / pywin32 迟到绑定）上取不到帧。**
⚠ 而另一条路（`SetFrameSymbols2`）官方**明写只对 2022 之前的 Gtol 有效** ⇒ **两条路都不通**。
★ **按事实 53 停手** —— 同一处试了 3 次，**不再变着法试**。

## 四、处置：**如实分裂声明**，不粉饰
```
insert_gtol          ✅ **真机可用**（冒烟通过）
add_gtol_indicator   ❌ **真机到不了**（保留函数作**可复算的证据**，不删）
```
* `sw_gtol.py` 文件头：等级从单一 `stitched` 改成**「分成两半」**的声明；
* `add_gtol_indicator` 的 docstring 顶部：**明写"当前不可用"** + 那三次量到的事实；
* `capabilities.yaml`：`evidence` 写 **3/5**、`limitations` 逐条写清；
* **已知事实 66** 入库。

## 五、判据
| ID | 判据 |
|---|---|
| SC-3501 | 真机冒烟跑通并**如实报告 3/5**（**不改判据去迎合**）|
| SC-3502 | ★ **三次测量**的结果都记录在案（含 `ConvertFormat` 返回 0 那次）|
| SC-3503 | ★ 源码里**明写** `add_gtol_indicator` **当前不可用**（测试钉住）|
| SC-3504 | ★ 源码里**明写**为什么停手（**事实 53**）（测试钉住）|
| SC-3505 | 能力条目 `evidence` 写 **3/5**、`limitations` 逐条写清 |
| SC-3506 | `insert_gtol` 与 `add_gtol_indicator` 的**等级分开声明** |
| SC-3507 | 已知事实 66 入库 |
| SC-3508 | 门禁 + 回归不退化（回归 **1107 passed**）|

## ⚠ 明确记下的限度
* 只证了「**在这台机器 + 这个后端上取不到帧**」——
  ⚠ **未查证**换后端（`comtypes` / 进程内 C++）能否走通；
* `IGtolFrame.SetSymbolXml`（**XML 路径**）**未试**；
* `SetIndicator` / `DeleteFrame` / 取回族**未试**（都要先能拿到帧）；
* ⚠ **枚举本身没问题**（逐值核对过）—— **问题在取不到帧**。
