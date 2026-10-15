import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

DOC = """# 死守卫的**第四种形态**：`server.py` 的 dispatch 表 vs 协议层

> 来源：`tools/probe_server_dispatch_wiring.py` + `tests/test_mcp_protocol_layer.py`
> （2026-10-01 轮 138，Spec Kit `057`）

## 一、判法（**纯集合比对**）
```
server.py 的 45 条  ∪  batch 模块的 41 条  ==  协议层实际给出的 86 条？
```
⚠ **安全**：起 server **只发 `initialize` + `tools/list`**，**一次工具都不调** ⇒ **不碰 COM**
（事实 24）。

## 二、★ 结果：**45 + 41 = 86 ✓ 完全对上**
| 方向 | 结果 |
|---|---|
| `server.py` 声明了、**却没进协议层** | **0** |
| 协议层有、`server.py` 里找不到声明 | **41** —— ★ **正好是 `register_capabilities` 贡献的那 41 条**（第二条注册路径）|
| **两条路径之间重名** | **0** |
| 每条路径**内部**重名 | **0** |

## 三、★★ 本轮查出的第一件事：**跨路径重名此前无人检查**
```
`tool_registry.check_specs` 只查 **batch 路径内部**的重名
⇒ ★ **两条注册路径之间的重名没有任何检查** ——
  若有人把同一名字加到 server.py 与某个 batch，**没人会拦**，
  而那时"哪一个赢"取决于注册顺序 ⇒ **不确定**。
⇒ ★ 而且从**协议层看不出来**（`tools/list` 是集合，重名会被去重）
⇒ 必须在**声明层**拦。已补 4 条结构判据。
```

## 四、★★★ 本轮查出的第二件事：**一个"顺手套上 fixture"的动作，会让判据在故障时静默跳过**
```
第一版把 `test_no_tool_is_declared_in_both_paths` 写成收 `tools` fixture
⇒ 故障注入时它报了 **`1 skipped`**（不是 failed）
⇒ 原因：重名让**注册失败 ⇒ server 起不来** ⇒ `tools` fixture 拿不到响应就 `skip`
⇒ ★★ **判据"恰好在被测故障发生时静默跳过"** —— 那是**最坏**的失效方式
   （比"没写这条判据"更糟：它看着是绿的）
⇒ 修法：这条判据**只看两个声明来源**（源码 + `all_specs()`），**不碰协议层**
```
★ 而这正与 `053`/`054` 那条呼应：**一条判据必须能被负例证伪** ——
"会 skip"等效于"不能被证伪"。

## 五、★ 一次**我自己的实验做错了**（如实记）
```
第一次故障注入：我往 batch10 塞了 `solidworks_current_selection`
⇒ 以为它"在 server.py 里"——**其实它在 batch 里**（协议层那 41 条之一）
⇒ 于是造出的是 **batch 内部重复**，而**跨路径**判据正确地保持绿
⇒ ⚠★ 而且我用 `-k declared_in_both` **只跑了一条**，把内部重复那条**排除了**
⇒ 结论：**是实验错了，不是判据错了** —— 换成真在 server.py 里的名字后，判据立刻红。
```
★ 教训：**故障注入本身也要"注对东西"** —— 否则会把"实验设计错"读成"判据失效"。

## 六、判据有效的证明（事实 62）
```
① 基线                       : exit=0 · 2 passed
② 注入**跨路径重名**（真在 server.py 里的名字）: exit=1 · **1 failed** ⇒ 判据确实会红
③ 复原后                     : exit=0 · 2 passed（文件精确复原 ✓）
```

## 七、四种形态，到此扫全
```
常量（053/054）：`_LEN_SUFFIX` · `_ANGLE_SUFFIX`        ⇒ **找到并接上**
函数（055）    ：`match_modules`                        ⇒ **找到并删除**
注册（056）    ：批次清单 / 注入解析器                   ⇒ 零发现
dispatch（本轮）：`server.py` ↔ 协议层                   ⇒ **零发现，但补了两条判据**
```
★ 后三种（056/057）都是**零发现** —— 而它们**都产出了结构判据**：
**零发现的价值不在于"没问题"，而在于"把不变量钉住，以后有问题会红"。**
"""

P = Path(r"C:\swprojects\sw-skill-fork\docs\dead-guards.md")
t = P.read_text(encoding="utf-8")
if "第四种形态" not in t:
    P.write_text(t.rstrip() + "\n\n---\n\n" + DOC.split("\n", 1)[1], encoding="utf-8")
    print("  ok 已把「第四种形态」并入 docs/dead-guards.md")
else:
    print("  已有")

# 已知事实 79
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
ADD = """

| # | 事实 | 依据 |
|---|---|---|
| 79 | **两条注册路径（`server.py` 直接声明 ↔ `batch` 模块）之间的重名此前无人检查；而"给判据套上 `tools` fixture"会让它恰好在被测故障发生时静默 `skip`** —— 2026-10-01（轮 138）：`server.py` 的 `name="…"` 字面量 **45** 条 · `all_specs()` **41** 条 · 协议层实测 **86** ⇒ **45+41=86 ✓**，且**跨路径重名 0**、**内部重名 0**。⚠ 但 `tool_registry.check_specs` **只查 batch 路径内部**的重名 ⇒ 跨路径重名**没有任何检查**（且从协议层看不出来 —— `tools/list` 是集合会去重）⇒ 已补 4 条结构判据。★★★ 更值钱的第二条：第一版把跨路径那条写成收 `tools` fixture ⇒ 故障注入时报 **`1 skipped`** —— 因为重名让注册失败、server 起不来、fixture 拿不到响应就 `skip` ⇒ **判据"恰好在被测故障发生时静默跳过"**（比没写更糟：它看着是绿的）⇒ 修法：该判据**只看两个声明来源，不碰协议层**。★ 故障注入验证：基线 2 passed ⇒ 注入**真在 `server.py` 里的**名字 ⇒ **1 failed** ⇒ 复原 2 passed。⚠ 另记一次**我自己的实验做错**：第一次注入了 `solidworks_current_selection`（它**在 batch 里**、不在 server.py 的 45 条里）⇒ 造出的是**内部重复**，跨路径判据正确地保持绿；且我用 `-k` **只跑一条**、把内部重复那条排除了 ⇒ **是实验错了，不是判据错了** | `tools/probe_server_dispatch_wiring.py`；`tests/test_mcp_protocol_layer.py`（**8 条**，含跨路径/内部重名/数量守卫）；`docs/dead-guards.md` 的「第四种形态」节；事实 24 / 62 / 78 |
"""
if "第四种形态" not in tk:
    K.write_text(tk.rstrip() + ADD, encoding="utf-8")
    print("  ok known-facts 已加 79")
else:
    print("  已有 79")
