import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           271 🎯 **Spec Kit `039`：形位公差的真机冒烟 —— 抓到的是我自己上轮写的缺陷**（轮 120）——
               挑它的理由：`038` 刚写完 `sw_gtol.py`，而且**整条路都押在 `IGtolFrame.AddIndicator` 上**。
               **真机 3/5**：✅ `insert_gtol` 通过 · ❌ `add_gtol_indicator` **第一步就不通** · ✓ 无残留模态框。
            272 ★★ **按事实 53 停手：连量三次把那一步量清楚**：
               | 轮次 | 试法 | 结果 |
               |---|---|---|
               | 1 | 直接 `GetFrame(1)` | `GetFrameCount()`=**1**，但 `GetFrame(0/1/2)` **全 None** |
               | 2 | 先 `AddFrame()` | 返回 **False**，计数**没涨** |
               | 3 | 先 `CanConvertFormat()`→`ConvertFormat()` | 返回 **0（成功）**，但转换后计数**掉到 0**、`GetFrame` **仍全 None** |
               ⇒ **「2022 格式的帧路径」在本机（SW 2026 SP4.1 / pywin32）上取不到帧**；
                 而另一条路（`SetFrameSymbols2`）官方**明写只对 2022 之前的 Gtol 有效** ⇒ **两条路都不通**。
            273 ⚠ **第 3 次那个结果特别有诱惑力**：`ConvertFormat` 返回 **0（成功）** ——
               **看起来只差最后一步**。★ 但**它的成功是"转换"的成功，不是"取到帧"的成功** ——
               **再往下试第 4 种写法，就是在赌「再试一次就好了」。**
               ⇒ **停手并如实记录，比"多半能修好"更有价值。**
            274 ★★ **这是冒烟测试价值的最好例证**：
               ```
               038（上轮）：写完 sw_gtol.py，静态证据齐全（签名互核 + 10 条契约测试）—— **全绿**
               039（本轮）：真机冒烟 ⇒ **发现那条路根本走不通**
               ⇒ 上轮那 10 条契约测试**一条都没发现** —— 它们测的是"参数传对了没"，
                 **而问题是"那个 API 在这台机器上不给帧"**。
               ```
               ★ 与 `014`/`015`（孤立函数从没跑过）、`029`/`032`（废弃入口）**同一族**：
                 **静态证据的覆盖面有边界，边界外的东西只有真机能看见。**
            275 ★ **处置：如实分裂声明**（不粉饰）—— `insert_gtol` ✅ 真机可用 ·
               `add_gtol_indicator` ❌ 真机到不了（**保留函数作可复算的证据，不删**）。
               三处都写明：源码头「验证等级：**分成两半**」· docstring 顶部「当前不可用」· 能力条目 `evidence` 写 **3/5**。
               ★ 这是本项目**第一次**遇到「**一条能力里两半分家**」—— **只写一个等级，无论写哪个都是错的**。
               ⚠ 未查证：换后端（comtypes / 进程内 C++）能否走通 · `SetSymbolXml`（XML 路径）未试 ·
                 `SetIndicator`/`DeleteFrame`/取回族未试（都要先能拿到帧）；**枚举本身没问题**，问题在取不到帧。
               已知事实 **66** 已入库 · 回归 **1107 passed**。
               下轮候选：① 继续给剩下 5 条 `stitched` 做真机冒烟（**这条路已被证明有产出**）；
               ② 继续补「真缺」；③ A5 的 2 条存疑。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+271 ", before, re.M):
    print("  游标 271 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+275 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 275 行已存在 ✓")
