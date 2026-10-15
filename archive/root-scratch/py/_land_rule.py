import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")

#: ── ① 用户指令写进 AGENTS.md（本项目的作业方法段）──────────────────
A = W / "AGENTS.md"
t = A.read_text(encoding="utf-8")
MARK = "### 5.0 ★★ 判据优先去开源项目里找（用户指令 2026-10-01）"
if MARK in t:
    print("  AGENTS.md: 已在，跳过")
else:
    RULE = """### 5.0 ★★ 判据优先去开源项目里找（**用户指令 2026-10-01**）

> 用户原话：「**当你需要判据的时候，先去开源项目里找，找不到再自己搓**」

**落到可执行的形态**（顺序不可颠倒）：
```
1. ★ **先找**：写任何真机探针 / 证据脚本**之前**，先查四家有没有现成的判据 ——
     Get-ChildItem C:\\swprojects\\andrewbartels1 -Recurse -Filter 'test_live_*.py'
   ★ 那是本机**最富的真机判据语料**：**6 个 live、~3800 行 / 543 处断言**，
     写的是「**什么算对**」而不是实现（例：`test_live_sw_add_chamfer_tool.py`
     327 行 / 48 断言，带**几何推出的倒角体积公式** 与"点会漂移 1mm"这类实战警告）。
   （同族：Slacker-LLC 1 个 live · vespo92 0 个 · Eduardof0nt **0 个测试文件**）
2. ★ **抄判据，不抄实现**：
     · 期望值优先用**几何推出的公式**（如倒角体积 `0.5·w²·L`），不用"看着像对"
     · 抄它的**实战警告**（漂移量、边界条件）
     · ★ **实现**仍须过命名 / 单位 / 选择三关 **+ 真机验证** —— 理由见事实 170：
       本会话实测「声明层只占 29%」，**贵的是验证**；而四家 **3/4 没声明真机跑过**。
3. ★ **找不到才自己搓** —— 但要**说明"找过"**（在哪找的、结果如何），
   否则"自己搓"与"没去找"无法区分。
```

★ **许可**：`andrewbartels1` 是 **MIT** ⇒ 抄**判据/期望值**可，保留版权声明即可；
  Apache-2.0（`Slacker-LLC`）另带 NOTICE 义务。见铁律 6。

★ **为什么这条重要**：判据（"什么算对"）比代码更贵 —— 代码可以重写，
  而"知道该断言什么"要靠**真机试错**换来。开源项目里已经有人付过这个成本。

"""
    anchor = "5. 门禁与实测："
    i = t.find(anchor)
    assert i > 0, "AGENTS.md 锚点不符"
    #: 插在 §五 工作方法 的 5 之前（即 4. 标等级与出处 之后）
    j = t.rfind("4. 标等级与出处", 0, i)
    assert j > 0, "AGENTS.md 二级锚点不符"
    t = t[:j] + RULE + t[j:]
    A.write_text(t, encoding="utf-8")
    print("  ✓ AGENTS.md 已加 §5.0（可执行的形态 + 顺序 + 许可）")
print("  AGENTS.md 核对:", MARK in A.read_text(encoding="utf-8"))

#: ── ② known-facts 171（W6 交付 + 用户指令）────────────────────────
FACT = """| 171 | **W6 交付：装配只读（含干涉检查的**第一次**真机验证）—— 并落定用户的「判据先去开源找」指令** —— 2026-10-01（轮 237）。

★★★ **交付**：`solidworks_assembly_list_components` / `_list_mates` / `_check_interference`；
  `all_specs()` **78 → 81**；能力清单 **45 → 46** 条。★ **能力层一行未改**。

★★★★ **最大的一处：干涉检查的第一次真机验证**
```
`sw_assembly.get_interference_detection` 的源码注释自述（轮 159）：
   「① 入口是 `InterferenceDetectionManager`（带 Manager）② 取结果用 `GetInterferences()`（复数）
     ③ `IInterference` 上没有 `Name` … **两处都在 `try:` 里 ⇒ 此前静默降级**
     （不炸，但**永远拿不到数据**）」
★ 而它**没有任何真机证据** ⇒ ★★ **"修过"不等于"验过"**。
⇒ 真机结果（一正一反）：
     重叠（两次都插在 z=0） ⇒ `interference_count` = **1**
     分开（z=0 与 z=60）    ⇒ **0**（`status: pass`）
     ★★ 两个数**不同** ⇒ **它真的在看几何** ✓
```

★★ **只读批也能做对照实验**（第 12 条套路的新用法）：
```
★ 事实 165 那条是"读官方没写的语义时设计对照实验"，当时用在**写**批（倒角：选没选边）。
★ 本批证明它在**只读**批同样适用 —— ★ **变量换成几何**（重叠 vs 分开）。
⇒ 定则：**只读能力也能被"证伪"** —— 给它两个**该给出不同答案**的输入。
```

★★ **注入名机制（事实 169）的落地**：`RESOLVERS` **加一行** `"asm_model": resolve_model`
  ⇒ `inject="asm_model"` 可用。★ 不动 `tool_registry`（它明确"不硬编码宿主 API，全从这里供给"）。

★★★★★ **用户指令（2026-10-01）已落成纪律**：
```
用户原话：「**当你需要判据的时候，先去开源项目里找，找不到再自己搓**」
⇒ ★ 写进 `AGENTS.md` 的 **§5.0**，且**落到可执行形态**（顺序不可颠倒）：
   1 ★ **先找**：`Get-ChildItem C:\\swprojects\\andrewbartels1 -Recurse -Filter 'test_live_*.py'`
     （★ 本机最富的真机判据语料：**6 个 live、~3800 行 / 543 处断言**，写的是「什么算对」）
   2 ★ **抄判据，不抄实现**：期望值优先用**几何推出的公式**；抄它的**实战警告**
     （★ 实现仍须过三关 + 真机验证 —— 事实 170 实测「声明层只占 29%」，贵的是验证）
   3 ★ **找不到才自己搓** —— 且**要说明"找过"**（在哪找的、结果如何），
     否则"自己搓"与"没去找"无法区分
★ **本批执行了它**：先查四家 live 测试 ⇒ **不含干涉**（覆盖的是倒角/切除拉伸/单位/参考点）
  ⇒ 所以**自己搓** —— 但**这是"找过之后"才决定的**。
★ **同一轮的待办**：倒角那个 `test_live_sw_add_chamfer_tool.py`（327 行/48 断言）
  **正好覆盖我刚做完的 W4 续c**，带**几何推出的倒角体积公式**
  ⇒ ★ 回头把倒角断言从「多了一个特征」升级成「**倒掉的体积符合几何期望**」。
```

★ **门禁链** 8 条 exit 0 · 全量 **1274 passed / 0 failed** · 两个「钉死数量」守卫同步
  （`all_specs()` 81 / 协议层 126）· 无人值守基线**只加一条**。

⚑ **限度**：① 复杂装配 / 子装配未验（真机用"两个零件、同一文件"的夹具）· ② 配合清单只验了"空"
  · ③ `explode_assembly` / `mirror_component` / `pattern_component_*` 未挂 ·
  ④ `sw_assembly_doc.collect_assembly_doc_evidence(doc, …)` 首参是 `doc` ⇒ 同一注入名问题（同解法）。

**依据**：`specs/139-assembly-read/` 五件套 · `mcp-server/resp`（注册器 `RESOLVERS`）·
`mcp-server/tool_specs_batch25.py` · `tools/capture_assembly_evidence.py` +
`output/assembly-evidence.json`（`verdict: pass`）· `docs/plan-10h.md` 新增纪律 ·
`C:\\swprojects\\andrewbartels1\\tests\\live\\*.py` · 事实 169 / 170
"""
K = W / "docs" / "known-facts.md"
tk = K.read_text(encoding="utf-8")
if "| 171 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT.strip().replace(chr(10), " ") + "\n", encoding="utf-8")
    print("  ✓ known-facts 已加 171")
else:
    print("  known-facts 171 已在")
print("  核对（精确）:", "| 171 |" in K.read_text(encoding="utf-8"))
