import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           656 🎯 **Spec Kit `119`：「339」是轮 86 的数，四轮人工核早已变 —— 而两处文档****各说一半、互不指认******（轮 199）——
               ★ 起因：objective ② 明写「B 级并入 **339** 个缺口操作」⇒ 本轮**去量它现在是几**（不照抄）。
            657 ★★★ **量出来的事实**：
               ```
               【union-gap-triage.md】（轮 86 起）把 339 拆四档，**四轮人工核**过：
                 轮 101 核样「能力在、未暴露 144」档 ⇒ 真实命中率 ≈ **25%**
                 轮 102 **全核**两档别名 ⇒ 强 7/26≈27% · 弱 6/37≈16%（**连自称"极可能同一操作"的强档也不例外**）
                 轮 103 **反向核**「真缺 132」档 ⇒ 反向错误率 ≈ **18%**（`tooling_split`/`save_as`/`measure` 其实我们有）
                 ⇒ 四轮合并：真匹配 ≈ 73 ⇒ **真实缺口 ≈ 265（区间约 245~265）**
                 ★ 根因写明：那些档来自**后缀词匹配**，而 sketch/view/template/macro 是高频通用词
                   ⇒ ★★ **这一档不该由字符串匹配给结论，只能人工核**
               【harvest-report.md §10.3 判据更正】那个数是
                 「**四家以 MCP 工具暴露、而本仓库没有以 MCP 工具暴露**的操作数」
                 （根因：`build_union_map.py` 的 `_our_tools()` **只数 `server.py` 的 `@mcp.tool` 名字**）
                 ⇒ **「能力缺口」≈ 0**（唯一真缺口是模具 1 个，轮 86 已并入）
               ```
            658 ★★★ **两处都没错，但口径不同，且此前**互不指认** ⇒ 只看一处必读错**：
               ```
               · 「**能力**缺口」（有没有这个能力）≈ **0** —— 逐域核过：
                 焊件 缺5/**实际14(verified)** · 草图 42/**57** · 装配 19/**54** · 工程图 49/**44**
                 真实能力面：**72 个模块 / 814 个公开函数**
               · 「**操作名**缺口」（有没有以**那个名字**暴露）≈ 那张表四轮核出的数
               ⇒ ★ 而 objective 引用的正是被判为**口径错误**的那个 339
               ```
            659 ★★★ **修法（不新造第三个数 —— 数字会腐坏，事实 187/195）**：
               ```
               ① union-gap-triage.md 顶部加「**口径声明**」：明写它量的是**操作名缺口**，
                  逐域列出能力口径的实证，并**指向** harvest-report §10.3
               ② harvest-report §10.3 追记：**指向**那张表，并把两个口径**都说出来**
                  （本节成立于"能力"口径；**不要用它否定那张表，反之亦然**）
               ③ ★★ 加**结构性检查**（`test_gap_number_has_exactly_two_named_readings`）：
                  两份文档**必须互相指认** + 各自明说口径
                  ⇒ ★ **能靠结构保证的，不要靠约定**（轮 191/192/193 同一条主线）
                  ⇒ 与 `AGENTS.md §一 A2`「① 与 ② 不是同一件事 …… 两条线不该混」**同型**
               ★ 最直觉的修法是"把 339 改成 265" —— **我没这么做**：
                 写进散文的 265 会在下一次并入后立刻过期，而**没有任何门禁看着它**。
                 ⇒ 改成"**两口径互指 + 指向唯一权威**"，于是**"分叉"这个失败模式被结构挡住**。
               ```
            660 ★★ **实测**：`git diff --stat` = **31 insertions(+)、0 deletions**（**事实 61**：纯加法）·
               回读落盘（harvest-report 603 → **620** 行，+17）· 新测试 **8 passed**；
               **负例**：临时删掉 triage 里的指向 ⇒ **failed** ✓（从自己的备份还原）
               ⇒ 全量回归 **1261 passed**（+1）。
               ⚠ **又一次事实 48**：新测试断言消息里嵌同类引号（`"能力缺口"`）⇒ `SyntaxError` ⇒ 改用「」
                 —— 与轮 197「知道定则 ≠ 写的时候会想起来」同型。
               ⚑ **未查证**：⚠ 本轮**没把 339/265 变成生成物** ⇒ **它仍会腐坏**
                 （只做到"指向唯一权威 + 两口径互指"）；
                 ⚠ triage 表里那 4 档的**逐条明细本轮没重核**；
                 ⚠ `union-coverage-matrix.md` §五（339 的**出处**）**本轮没改** —— 它由生成器写，
                   改它要走生成器（**未做**）；
                 ⚠ **AGENTS.md 的目标口径未改**（受 65536 字节预算约束，且改指令文件另有合约）。
               下轮候选：① 把「缺口数」做成**生成物**（让它随并入自动变，而不是靠人记着改）；
               ② 改 `union-coverage-matrix.md` §五 的口径（走生成器）；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+656 ", before, re.M):
    print("  游标 656 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+660 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 660 行已存在 ✓")
