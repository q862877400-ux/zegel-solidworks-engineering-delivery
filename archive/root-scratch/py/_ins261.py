import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           261 🎯 **Spec Kit `037`：「模块 ↔ 能力条目」覆盖核对 —— **问了错的问题****（轮 118）——
               起因：`036` 碰巧发现 `sw_sketch.py` 没有条目 ⇒ 记了「下轮系统核对」。
               ★ **两版判据都失败**（当场发现并拦住）：
               ```
               版 1 模块名出现   ⇒ 报 43 个「没覆盖」⇒ 把 sw_routing↔routing、
                                    sw_weldment↔weldments、sw_topology↔topology_optimization
                                    这些**明明有条目**的也报了（条目用**域标签**，不写文件名）
               版 2 函数名被提到 ⇒ 报 43 个（另一批）⇒ sw_helix **刚建条目**却被判「没覆盖」
               版 3 两信号并集   ⇒ 仍 38 个 ⇒ **停手**（事实 53）
               ```
               ★ 假阳性约 **38/64 ≈ 59%** —— 比 `029`（26%）与 `032`（50%）**都高**。
            262 ★★ **更重要的一层：这个核对**问错了问题****：
               ```
               A1 原文：「**域覆盖矩阵**里本仓库每一格都有来源」⇒ **A1 的单位是「域」，不是「文件」**
               而 capabilities.yaml 的条目**本来就是域级的**
                 （routing · weldments · surface_modeling · assembly_and_mates …）
               ⇒ **条目已经在正确的粒度上** —— 「模块名没出现」**根本不是缺陷**
               ```
               ⓘ `036` 那次之所以是**真发现**，不是因为字符串没匹配，而是因为
                 **「草图读回」是一个域级能力、而它真的没有条目** —— 那是**判断**。
               ⇒ **本核对把「域级覆盖」误当成「文件级覆盖」来量，量出来的东西没有意义。**
            263 ★ **处置**：**不做门禁**（59% 假阳性）；探针保留供**人工**扫一眼；
               ★ **探针源码里写明两版判据都失败**（免得下一个人又拿它当判据）。
               ★ **如果我第一版就采信**，会得出「43 个模块缺条目」这个**错的数字**并写进报告。
            264 ★★ **第 8 例：名字匹配在这个项目里反复出问题** ——
               020/021/022 核样 · 027 探针 · 029 废弃成员（26%）· 032（50%）· 037（59%）。
               **更强的表述**：
               > **名字匹配不但假阳性多，还可能把「问题本身」定错** ——
               > 它默认「名字对得上 = 有关系」，而**这个仓库里关系是语义的**。
               ⇒ 凡「按名字判有无」的检查，先问一句：
                 **这两样东西的对应关系是名字上的，还是语义上的？**
            265 ⚑ **未查证**：★ **「还有多少个模块真缺条目」这个数字没得出** ——
               字符串匹配答不了，**不要当成"已核对完毕"**；唯一的真实例仍是 `036` 的 `sketch_query`。
               回归 **1091 passed**。
               下轮候选：① 回到补「真缺」；② 人工按域过一遍能力条目（要专门花一轮）；
               ③ 给剩下 3 条 `stitched` 做真机冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+261 ", before, re.M):
    print("  游标 261 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+265 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 265 行已存在 ✓")
