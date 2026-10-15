import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           352 🎯 **Spec Kit `055`：死守卫的****第二种形态**** —— 定义了却从没被调用的函数**（轮 136）——
               判法（有界）：6 类门禁/工具文件（`scripts/check_*`·`audit_*`·`gen_*`·`tools/*`）
               的**模块级 def**（排除 `main`/`register`/`run`），数名字在**全仓库**的出现次数
               ⇒ **0 次**即可疑。⇒ **164 扫过 · 1 可疑 · 1 真**。
            353 ★★ **那 1 个是真的死代码**：`tools/propose_capability_sources.py:133` `match_modules`
               是 `stems_only()` 的**旧版**（会**扫文件体** `body = f.read_text(...)[:1200]`），
               而 `stems_only()` 的 docstring **明写**「**只按文件名主干**匹配（**不再扫文件体**）」
               「⚠ 第一版还扫了文件体 ⇒ **命中面进一步失控**」
               ⇒ ★★ **被取代的旧版，作者留了说明却没删函数。**
               ⇒ 处置：**删除 + 墓碑注释**（可 git 追溯；**留注释而不是无声删掉** ——
                 读代码的人该知道这里发生过什么）。
            354 ★★ **「0% 假阳性」不等于「可以升门禁」**：
               ```
               164 扫过 · 1 可疑 · 1 真 ⇒ 表面 0%
               ⇒ 最自然的冲动：升成第 17 道硬门禁
               ⇒ ★ 但 **n=1** 估不出率 —— 一个数据点不是证据
               ⇒ 决定：**先做成回归测试**（会红但可控），**不接进 release_check**（那会挡住发布）
               ```
               ★ 与 `052`/`054`（"假阳性太高 ⇒ 不成门禁"）**方向相反、克制相同**。
            355 ★★ **一条方法上的自我纠正**：
               ```
               第一版测试**自己重写了一遍判法**（`_fake_suspects`）去跑负例
               ⇒ ★ 那测的是"测试自己写的一份"，**不是工具**（事实 62 的精神）
               ⇒ 改成把判法抽成 `probe.find_uncalled(root=…)`，**main() 与测试跑同一份代码**
               ```
               ★ 这是事实 62 的一个**更细的落点**：**负例必须打到被测对象本身。**
            356 ⚑ **三种形态的死守卫，到此扫了两种**：
               ```
               常量形态（053/054）：`_LEN_SUFFIX` · `_ANGLE_SUFFIX` —— 规则 2 的两半
               函数形态（本轮）    ：`match_modules` —— 被取代的旧版
               ⚠ 第三种（**注册了却没接进 dispatch 的表**）**仍未扫**
               ```
               ★ 三者共同判法都是**结构**的：「**定义了，却没人引用**」——
                 与事实 74（"按名字判语义做不成"）**恰成对照**：**判结构可靠，判语义不可靠。**
               ⚑ **未查证**：**样本 n=1**；判法**看不到动态调用**（靠 `UNCALLED_EXEMPT` 人工兜）；
                 ⚠ **只扫了 6 类文件**；测试**跑 11 秒**。
               已知事实 **77** 入库 · 回归 **1179 passed**。
               下轮候选：① 扫**第三种形态**（注册了却没接进 dispatch 的表）；
               ② 继续补「真缺」；③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+352 ", before, re.M):
    print("  游标 352 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+356 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 356 行已存在 ✓")
