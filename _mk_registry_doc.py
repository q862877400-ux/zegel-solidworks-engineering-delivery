import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

DOC = """# 死守卫的**第三种形态**：登记了却没接上（注册表 / 注入 / 批次清单）

> 来源：`tools/probe_registry_wiring.py` + `tests/test_registry_wiring.py`
> （2026-10-01 轮 137，Spec Kit `056`）

## 一、三种形态，到此扫全
```
常量形态（053/054）：`_LEN_SUFFIX` · `_ANGLE_SUFFIX` —— 规则 2 的两半，**都定义了却没人用**
函数形态（055）    ：`match_modules` —— 被 `stems_only()` 取代后**一直留着**
注册形态（本轮）    ：**登记表 / 解析器 / 批次清单** —— 有没有"登记了却没接上"
```

## 二、★ 本轮的结果是**零发现** —— 而且这是**好消息**
| 方向 | 结果 |
|---|---|
| 磁盘上的 `tool_specs_batch*.py` **没登记进 `BATCH_MODULES`** | **0 个**（10 个文件全登记）|
| 登记了、**文件却不在** | **0 个** |
| 批次里 `SPECS_*` 声明的工具**没进 `all_specs()`** | **0 个**（41 条全在）|
| 用了某个 `inject` 名却**没有解析器** | **0 个** |
| 登记了 `RESOLVERS` 却**没有任何 spec 用** | **0 个**（`model` 31 · `sw_app` 6 · `study` 1）|

⇒ ★ **接线是一致**的 —— 本轮**没有**找到第三种形态的死守卫。

### ⚑ 零发现也要**说清楚扫了什么、没扫什么**
* **扫了**：`tool_specs_batch*.py` ↔ `BATCH_MODULES` · `SPECS_*` ↔ `all_specs()` ·
  `inject` ↔ `RESOLVERS`（两个方向）；
* ⚠ **没扫**：`server.py` 的 dispatch 表本身（它的形状还没摸清）·
  `sw_api_*.py` 那几份名字登记表 · `subskills/` 下的清单。

## 三、★★ 为什么这一种可以（而且应该）当**回归**，前两种不行
```
名称/语义类（052/054）：假阳性 50%~100% ⇒ **只出清单、人工判**
结构类（055/056）：**集合比对** —— 磁盘上的文件 vs 清单项、用的名字 vs 解析器
⇒ ★ 结构类**没有"解释空间"**：一个文件要么在清单里、要么不在。
```
★ 而这一点在本轮被**再推进一步**：

### ★★ 结构类判据**可以被"故障注入"确定性地验证**（事实 62）
```
① 基线              : exit=0 · 5 passed
② **造故障**（往 mcp-server/ 放一个没登记的 tool_specs_batch99.py）
                    : exit=1 · **1 failed** ⇒ 判据确实会红
③ 复原（删掉假文件） : exit=0 · 5 passed
```
⚠ **这一点名称/语义类判据做不到** ——
你想"注入一个假故障"时，**先得说清"什么叫错"**，而那正是它判不了的东西。
⇒ ★★ **"能不能被故障注入验证"本身就是一条分界线：**
**能注入的是结构判据，不能注入的是语义判据。**

## 四、判据的边界（本轮**没**宣称的事）
* ⚠ **没有**说 `server.py` 的 dispatch 表也对得上（**未扫**）；
* ⚠ **没有**说 `subskills/` 的清单也对得上（**未扫**）；
* ⚠ 故障注入用的是**假批次文件** —— 它验证的是"文件在却没登记"这一条；
  另四条（幽灵登记 / SPECS 漏项 / 缺解析器 / 多解析器）**没有各自注入**，
  但它们与那一条**同形**（都是集合比对）。
"""

P = Path(r"C:\swprojects\sw-skill-fork\docs\dead-guards.md")
t = P.read_text(encoding="utf-8")
if "第三种形态" not in t:
    P.write_text(t.rstrip() + "\n\n---\n\n" + DOC.split("\n", 1)[1], encoding="utf-8")
    print("  ok 已把「第三种形态」并入 docs/dead-guards.md")
else:
    print("  已有")

# 已知事实 78
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
ADD = """

| # | 事实 | 依据 |
|---|---|---|
| 78 | **死守卫的第三种形态「登记了却没接上」：本轮零发现；而「能不能被故障注入验证」本身是结构判据与语义判据的分界线** —— 2026-10-01（轮 137）扫了四个方向：磁盘 `tool_specs_batch*.py` ↔ `BATCH_MODULES`（10/10 全登记）· 反向幽灵登记（0）· 批次 `SPECS_*` ↔ `all_specs()`（41 条全在）· `inject` ↔ `RESOLVERS` 两个方向（`model` 31 / `sw_app` 6 / `study` 1，**无缺、无多**）⇒ ★ **接线一致，零发现**。★★ 关键区别：名称/语义类判据（事实 74 / 76）假阳性 50%~100%，**只能出清单**；而这四条是**集合比对（结构）**，没有解释空间 ⇒ **可以当回归**。★★ 更进一步：结构类判据**能被故障注入确定性验证**（事实 62）—— 基线 5 passed ⇒ **往 `mcp-server/` 放一个没登记的 `tool_specs_batch99.py`** ⇒ **1 failed** ⇒ 删掉 ⇒ 5 passed。⚠ **名称/语义类做不到这一点**：要"注入一个假故障"先得说清"什么叫错"，而那正是它判不了的东西 ⇒ ★★ **"能不能被故障注入验证"本身就是那条分界线**。⚠ 边界：`server.py` 的 dispatch 表本身 · `sw_api_*.py` 名字登记表 · `subskills/` 清单**未扫** | `tools/probe_registry_wiring.py`；`tests/test_registry_wiring.py`（**5 条**，含故障注入验证）；`docs/dead-guards.md` 的「第三种形态」节；事实 40 / 62 / 74 / 76 / 77 |
"""
if "第三种形态「登记了却没接上」" not in tk:
    K.write_text(tk.rstrip() + ADD, encoding="utf-8")
    print("  ok known-facts 已加 78")
else:
    print("  已有 78")
