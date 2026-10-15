import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           362 🎯 **Spec Kit `057`：死守卫的****第四种形态**** —— `server.py` 的 dispatch 表 vs 协议层**（轮 138）——
               判法：`server.py 的 45 条 ∪ batch 的 41 条 == 协议层实测的 86 条？`
               ⚠ **只发 `initialize` + `tools/list`，一次工具都不调** ⇒ 不碰 COM（事实 24）。
               ⇒ **45 + 41 = 86 ✓ 完全对上**；四个方向全 0（声明了没进 0 · 跨路径重名 0 · 内部重名 0）。
            363 ★★ **查出的第一件事：跨路径重名此前无人检查** ——
               `check_specs` 只查 **batch 路径内部**的重名 ⇒ 两条路径之间的重名**没有任何检查**，
               重名时"哪一个赢"取决于注册顺序 ⇒ **不确定**；
               ★ 而且**从协议层看不出来**（`tools/list` 是集合、会去重）⇒ 必须在**声明层**拦。
               ⇒ 已补 4 条结构判据（并集==协议层 · 跨路径交集空 · 各自内部无重名 · 数量守卫）。
            364 ★★★ **查出的第二件事（本轮最值钱）：「会 skip」比「没写」更糟**：
               ```
               第一版跨路径判据收了 `tools` fixture
               ⇒ 故障注入时报 **1 skipped**（不是 failed）
               ⇒ 重名让注册失败 ⇒ server 起不来 ⇒ fixture 拿不到响应就 skip
               ⇒ ★★ 判据"**恰好在被测故障发生时静默跳过**" ——
                 它**看起来完全正常**，比"没写"更糟（没写至少你知道没有）
               ⇒ 修法：该判据**只看两个声明来源**（源码 + all_specs()），**不碰协议层**
               ```
               ★★ 这把 `056` 的结论**又推进一步**：**故障注入不只验"判据会不会红"，
                 还验"它在故障时会不会假装没事"。**
            365 ★ **一次"实验错 vs 判据错"的澄清**：
               ```
               第一次注入注错了名字（`solidworks_current_selection` **在 batch 里**、
                 不在 server.py 的 45 条里）⇒ 造出的是**内部重复** ⇒ 跨路径判据**正确地**保持绿
               ⇒ ⚠ 且我用 `-k` **只跑一条**，把内部重复那条也排除了
               ⇒ ★ **先问"我注的是不是那个东西"** ⇒ 是**实验错**，不是判据错
               ```
               ★ 本会话**第二次**「绿了/红了先别下结论，先核对量的是什么」（上次在 `048`：判据爬错层）。
            366 ⚑ **四种形态到此扫全**：
               ```
               常量（053/054）：找到并**接上**（规则 2 的两半）
               函数（055）    ：找到并**删除**（match_modules）
               注册（056）    ：**零发现**
               dispatch（本轮）：**零发现**，但补了**两条判据**
               ```
               ★ 后两种都是零发现 —— 而它们**都产出了结构判据**：
                 **零发现的价值不在于"没问题"，而在于"把不变量钉住，以后有问题会红"。**
               ⚑ **未查证**：⚠ `subskills/` 的清单**仍未扫**；故障注入只注了跨路径重名一条；
                 数量守卫（86）会随加工具而过时（刻意设计成"变了就红"）。
               已知事实 **79** 入库 · 回归 **1188 passed**。
               下轮候选：① 扫 `subskills/` 清单（最后一块未扫的）；② 继续补「真缺」；
               ③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+362 ", before, re.M):
    print("  游标 362 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+366 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 366 行已存在 ✓")
