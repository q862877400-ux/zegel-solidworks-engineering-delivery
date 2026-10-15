import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\039-gtol-smoke-found-it-broken")
S.mkdir(parents=True, exist_ok=True)

spec = """# 039 · 形位公差的真机冒烟 —— **抓到的是我自己上轮写的缺陷**

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
"""

plan = """# 039 · Plan

## 步骤
1. 写冒烟：新零件 → `insert_gtol` → `add_gtol_indicator` → 关件不保存
2. 跑 ⇒ **3/5**：`insert_gtol` 通过、`add_gtol_indicator` **失败**
3. ★ **不猜，量**：`GetFrameCount` / `AddFrame` / `GetFrame(0,1,2)` 各读一次
4. ★ 查官方有没有"转换格式"这一步 ⇒ 有 `CanConvertFormat` / `ConvertFormat` ⇒ **量第 3 次**
5. ⇒ 转换**成功（返回 0）**但**仍取不到帧** ⇒ ★ **按事实 53 停手**
6. 如实分裂声明（源码 / 能力条目 / 已知事实）
7. 更新测试（桩要 `GetFrameCount`；新判据钉住"不可用"与"为什么停手"）
8. 重生成 + 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| **继续变着法试**（第 4、5 次）| ★ **事实 53**：3 次就停，把测量记下来 |
| 为了"好看"删掉不可用的函数 | ★ **保留** —— 它是**可复算的证据** |
| 改判据迎合现状 | ★ 冒烟**如实报 3/5**，不改阈值 |
| 文档仍说"应该能用" | ★ 三处（源码头 / docstring / 能力条目）**都写明不可用** |
"""

tasks = """# 039 · Tasks（全部完成，轮 120）

- [x] T-3501 写 `tools/verify_gtol_smoke.py`
  `→ 验收:` `python tools/verify_gtol_smoke.py`（**3/5**）
- [x] T-3502 ★ 冒烟抓到 `add_gtol_indicator` **第一步就不通**
- [x] T-3503 ★ 补 `add_gtol_frame` / `ensure_gtol_frame` ⇒ **仍不通**
- [x] T-3504 ★ 查 `CanConvertFormat` / `ConvertFormat` ⇒ **转换成功但仍不通**
- [x] T-3505 ★ **按事实 53 停手**，如实分裂声明（源码头 / docstring / 能力条目 / 事实 66）
- [x] T-3506 更新测试（**16 passed**）
  `→ 验收:` `python -m pytest tests/test_sw_gtol_contract.py -q`
- [x] T-3507 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 039 · Converge

**Converged**: 2026-10-01（轮 120）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-3501 如实报告 3/5 | ✅ 没改判据 |
| SC-3502 三次测量都记录 | ✅ 见 spec §三 |
| SC-3503 源码明写"不可用" | ✅ 测试钉住 |
| SC-3504 源码明写"为什么停手" | ✅ 测试钉住（含"事实 53"字样）|
| SC-3505 能力条目如实 | ✅ `evidence` 写 3/5 |
| SC-3506 两半等级分开声明 | ✅ 文件头「验证等级：分成两半」|
| SC-3507 事实 66 入库 | ✅ |
| SC-3508 门禁 + 回归 | ✅ `release_check` exit 0 · **1107 passed** |

## 二、★★ 这一轮是**冒烟测试的价值**的最好例证
```
038（上轮）：写完 sw_gtol.py，静态证据齐全（签名互核 + 10 条契约测试）——**全绿**
039（本轮）：真机冒烟 ⇒ **发现那条路根本走不通**
⇒ 上轮那 10 条契约测试**一条都没发现**，因为它们测的是"参数传对了没"，
  **而问题是"那个 API 在这台机器上不给帧"**。
```
★ 与 `014`/`015`（孤立函数从没跑过）、`029`/`032`（废弃入口）**同一族**：
**静态证据的覆盖面有边界，边界外的东西只有真机能看见。**

## 三、★ 事实 53 在本轮**真的拦住了我**
```
第 1 次  直接 GetFrame(1)        → None
第 2 次  先 AddFrame()           → 仍 None
第 3 次  先 ConvertFormat()      → **转换成功（返回 0）**，仍 None
         ⇒ **停手**
```
⚠ 第 3 次那个结果**特别有诱惑力**：`ConvertFormat` 返回 **0（成功）** ——
**看起来只差最后一步**。★ 但**它的成功是"转换"的成功，不是"取到帧"的成功** ——
**再往下试第 4 种写法，就是在赌"再试一次就好了"**。
⇒ **停手并如实记录，比"多半能修好"更有价值。**

## 四、`insert_gtol` 与 `add_gtol_indicator` 的等级**必须分开**
```
insert_gtol        ✅ 真机可用      （冒烟通过）
add_gtol_indicator ❌ 真机到不了    （保留作证据）
⇒ 若只写一个等级，无论写哪个都是**错的**
```
★ 这是本项目**第一次**遇到"**一条能力里两半分家**"的情况。

## 五、未查证
* 只证了「**这台机器 + 这个后端**取不到帧」—— **换后端未试**；
* `SetSymbolXml`（**XML 路径**）**未试**；
* `SetIndicator` / `DeleteFrame` / 取回族**未试**（都要先能拿到帧）；
* ⚠ **枚举本身没问题**（逐值核对过）—— **问题在取不到帧**。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
