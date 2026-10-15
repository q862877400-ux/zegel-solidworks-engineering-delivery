import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")

#: ① 修 spec 的命令（特性还没 converge ⇒ 允许改）
P = W / "specs" / "126-view-selection-batch" / "tasks.md"
t = P.read_text(encoding="utf-8")
OLD = "`→ 验收:` `Select-String -Path C:\\swprojects\\sw-skill-fork\\mcp-server\\tool_specs_batch*.py -Pattern 'ActiveView|sw_view'`（**空**）"
NEW = ("`→ 验收:` `Select-String -Path C:\\swprojects\\sw-skill-fork\\mcp-server\\tool_specs_batch*.py "
       "-Pattern 'ActiveView|sw_view' | Where-Object { $_.Filename -ne 'tool_specs_batch14.py' }`（**空**）\n"
       "  ⚠⚠ **第一次记的命令是坏的**：`tool_specs_batch*.py` **包含本批自己新写的 `batch14.py`**\n"
       "  ⇒ 它搜到了自己的头部注释（3 处命中）⇒ ★ **判据被自己的产物污染**。\n"
       "  ★ 定则：**"期望空"式的判据，若搜的目录包含本批新写的文件，必须排除本批产物**（或先跑、后写）。\n"
       "  实测（排除后）：**空** ⇒ 「前 13 批无 view 包装先例」成立。")
assert OLD in t, "锚点不符"
P.write_text(t.replace(OLD, NEW, 1), encoding="utf-8")
print("  ok 已修正 T-12602 的命令（含污染说明）")

#: ② converge 里补一条未查证
C = W / "specs" / "126-view-selection-batch" / "converge.md"
c = C.read_text(encoding="utf-8")
ADD = """* ⚠ ★ **本特性的判据曾被自己的产物污染**：T-12602 第一版用
  `tool_specs_batch*.py` 搜 `ActiveView|sw_view`，而那**包含本批刚写的 `batch14.py`**
  ⇒ 搜到自己的注释 3 处 ⇒ 排除本批产物后才是**空**（论断成立）。
  ★ 定则：**"期望空"式判据必须排除本批产物**。见 known-facts 147。
"""
if "判据曾被自己的产物污染" not in c:
    C.write_text(c.rstrip() + "\n" + ADD, encoding="utf-8")
    print("  ok converge 已补污染说明")

#: ③ known-facts 147
FACT = """| 147 | **"期望空"式的判据会被**自己的产物**污染** —— 搜的目录里包含本批新写的文件时，必须排除它** —— 2026-10-01（轮 207 / Spec Kit `126`）。

★★ **实测（当场撞到）**：
```
Spec Kit `126` 的 T-12602 要证明「既有批次里**没有** view 包装先例」，命令是
    Select-String -Path mcp-server\\tool_specs_batch*.py -Pattern 'ActiveView|sw_view'   （期望空）
★ 而 `tool_specs_batch*.py` **包含本批刚写的 `batch14.py`** —— 它的头部注释里就写着 `sw_view`
⇒ 命令**搜到了自己的产物**，返回 **3 处命中**。
★ 排除本批产物后重跑：**空** ⇒ 论断成立（前 13 批确实没有先例）。
```
★★★ **定则（可复用）**：
> **凡是"期望空 / 期望不存在"的判据，若它搜的目录里包含**本批新写的文件**，
> 必须在命令里**排除本批产物**，或者**在写之前先跑一遍**。**
```
★ 为什么容易漏：那条命令**在执行者眼里完全合理**（"搜全部批次"），
  而它的**失效方式**是"命中自己的注释" —— ★ 一个**看起来像"发现了问题"的假阳性**。
⇒ ★ 这类判据的**正确形状**是「**范围 - 本批产物**」，与**事实 51**（范围要贴合组织单元）同源，
  只是这次要扣掉的不是"别的函数的代码"，而是**"我自己刚写下的那句话"**。
```
⚠ **同轮的另一处**：那条命令**已经写进 spec 并被复制到 tasks.md** ——
  ★ 若不回头修，**下一个人重跑会得到同样的假阳性，并据此以为"有先例"**。
  ⇒ 趁特性**还没 converge** 修掉它，并把污染本身写进 tasks/converge（Flow-forward 允许在 converge 前修正）。

**依据**：`specs/126-view-selection-batch/tasks.md` T-12602 · `specs/126-view-selection-batch/converge.md` ·
`mcp-server/tool_specs_batch14.py`；事实 51 / 143
"""

K = W / "docs" / "known-facts.md"
tk = K.read_text(encoding="utf-8")
if "| 147 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT, encoding="utf-8")
    print("  ok known-facts 已加 147")

#: ④ ROADMAP 游标
R = W / "docs" / "ROADMAP.md"
B = """           696 🎯 **Spec Kit `126`：视图读取 + 体上实体枚举 —— 而队列列了 4 个，****实测只挂 2 个******（轮 207）——
               ```
               可注入（inject="model"）：get_active_view(model) ✓ · entities_on_body(model, kind, *, body_index=0) ✓
               ★ 不可直接挂：activate_view(view) · add_perspective(view) —— **首参是 `view`，不在约定注入点里**
                 （约定的四个是 `""` / `model` / `sw_app` / `study`）
               ⇒ ★ **不硬挂**：记进队列 A10（先定"无活动文档时 ActiveView 返回什么"，再加 `view` 注入器或包装层）
               ```
            697 ★ `kind` 的合法值**从常量读**（`sw_selection_spec.ENTITY_KINDS = ['EDGE','FACE']`），不手抄；
               并把该函数的**"序号不保证稳定"警告**搬进工具描述（**不许把它丢掉**）。
            698 ★★ **五处口径一致地动 2**（第四次同一模式）：被引用函数 103→**105** · 孤立能力 292→**290** ·
               首参可注入 41→**39** · 并集 434→**436** · 独家 85→**87** · 缺口 338 **不变** ⇒ 计数 51→**53** · 96→**98**。
            699 ⚠⚠⚠ **一处我自己的错，当场撞到并修掉**：T-12602 要证明"既有批次里没有 view 包装先例"，
               命令用 `tool_specs_batch*.py` 搜 `ActiveView|sw_view`（**期望空**）——
               ★ 而那个 glob **包含本批刚写的 `batch14.py`** ⇒ **搜到了自己的注释（3 处）**。
               ⇒ 排除本批产物后重跑：**空** ⇒ 论断成立。
               ★★ **定则**：**凡是"期望空 / 期望不存在"的判据，若搜的目录包含**本批新写的文件**，
                 必须**排除本批产物**，或**先跑、后写**。**
               ★ 而它的失效方式是**"命中自己的注释"** —— 一个**看起来像"发现了问题"的假阳性**；
                 且它**已写进 spec/tasks** ⇒ **不回头修，下一个人会据此以为"有先例"**（趁未 converge 修掉）。
            700 ▶ **队列续作**：下一项 = **A4 审查/报告族**（`build_review_report` / `activate_plot`）⇒ 继续自动推进。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None
before = "".join(lines)
if re.search(r"^\s+696 ", before, re.M):
    print("  游标 696 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+700 ", R.read_text(encoding="utf-8"), re.M)
    print("  复核: 700 行已存在 ✓")
