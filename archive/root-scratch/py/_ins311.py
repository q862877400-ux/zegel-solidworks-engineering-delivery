import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           311 🎯 **Spec Kit `047`：把轮 123~127 查证并**真机跑过**的 4 个入口接出去（batch10）**（轮 128）——
               那几个入口此前**只活在 `scripts/` 里**：
               `bbox`（真机 8/8）· `list_hole_standards`（6/6）· `list_fastener_types`（11/11）·
               `list_fastener_table_types`。
               ★ 与 `014`/`015` 的「孤立函数从没跑过」相对：这几个**跑过了**，但**还没接出去** ——
                 **不接出去，外部使用者拿不到**。
            312 ★★ **先查有没有现成机制，再动手**：
               ```
               需求：`list_*` 三个要的是 `ISldWorks`（不是活动文档）
               ⇒ 第一反应可以是"给 registry 加一种注入"
               ⇒ ★ **先查** ⇒ `inject="sw_app"` **本来就支持**，`RESOLVERS` 里也有解析器
               ⇒ **一行都不加机制**
               ```
               ★ 这正是「**不要为了修房子创建公司**」在这一轮的具体落点。
            313 ★★ **比"直接调函数"更值钱的一步：走**声明层**验证**：
               ```
               函数冒烟（已有 2 个）：证 get_bounding_box / list_* 能跑
               声明冒烟（本轮）   ：证 **手抄的声明**能不能把调用**正确地**送进去
               ```
               ★ 参数名抄错 / 注入名搞错 / `read_only` 标错 —— 静态测试**只能查"存不存在"**。
               ⇒ 真机 **7/7**（`inject=model` 1 条 + `inject=sw_app` 3 条，15/14/3 条结果）。
               ★★ 而本轮**真的抓到一条**：**`read_only` 忘了标** ⇒ 测试红 ⇒ 补上。
                 ⚠ **若只跑函数冒烟，这条永远不会被发现**（函数本身完全正常）。
            314 ★ **暴露面**：`all_specs()` **37 → 41** · 并集 420 → **424 操作** · 独家 71 → **75**。
               数量守卫测试同步更新（**37 → 41**，保留历史说明）—— 它设计成"变了就红"。
            315 ⚠ **一条仍未被证的边界**：本轮只证到「**声明 → RESOLVERS → 调用**」；
               **MCP 协议层**（起 server、经 JSON-RPC 真调一次）**未证**。
               ⇒ 那句"接出去了"目前是**到这个深度为止**，**不是**"端到端已通"。
               ★ 与 `014`/`015` 一脉相承：**"接出去"要分层说清楚接到了哪一层。**
               ⚠ 另：`harvest-report.md` 的**总暴露数**（"工具 83 个"一类）本轮**没有重新统计**。
               回归 **1149 passed**。
               下轮候选：① 把 MCP 协议层也验一次（起 server 真调）；② 继续补「真缺」；
               ③ 给剩下 3 条 `stitched` 冒烟。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+311 ", before, re.M):
    print("  游标 311 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+315 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 315 行已存在 ✓")
