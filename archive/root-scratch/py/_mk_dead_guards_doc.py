import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

DOC = """# 死守卫的**第二种形态**：定义了却从没被调用的函数

> 来源：`tools/probe_uncalled_helpers.py` + `tests/test_no_uncalled_helpers.py`
> （2026-10-01 轮 136，Spec Kit `055`）

## 一、为什么扫这个形态
`053`/`054` 扫的是**常量**形态的死守卫 —— 规则 2 的两半
（`_LEN_SUFFIX` / `_ANGLE_SUFFIX`）**都定义了却没人用**。
★ 本轮扫**函数**形态：**门禁/工具模块里定义了却全仓库没人调的辅助函数**。

⚠ 已知事实 61 的定则④就说过这一类：
> 「写了一个好用的工具函数，就要在**所有**同类场合用它，别只用在门禁里」

## 二、判法（有界、可复核）
```
① 只看 6 类文件：scripts/check_*.py · scripts/audit_*.py · scripts/gen_*.py · tools/*.py
② 取它们**模块级**的 def（含 `_` 开头的私有函数）
③ 排除入口点：main / register / run
④ 数该名字**在整个仓库**（scripts · mcp-server · tools · tests · subskills）里
   除定义行与注释外还出现几次 ⇒ **0 次**即可疑
```

## 三、★ 结果：**164 扫过 · 1 可疑 · 1 真**（假阳性 **0%**）
| 可疑 | 判定 |
|---|---|
| `tools/propose_capability_sources.py:133` `match_modules(kws, files)` | ✗ **真的死代码** —— 它是 `stems_only()` 的**旧版**：会**扫文件体**（`body = f.read_text(...)[:1200]`），而 `stems_only()` 的 docstring 明写「**只按文件名主干**匹配（**不再扫文件体**）」「⚠ 第一版还扫了文件体 ⇒ 命中面进一步失控」 |

⇒ ★★ **被取代的旧版，作者留了说明却没删函数** —— 于是它作为死代码留在仓库里。

### 处置
* **删掉它**，并在原处留一条**墓碑注释**（写明它是谁、为什么删）——
  ⚠ 留注释而不是无声删掉：**读代码的人该知道这里发生过什么**；
* 删除是**可 git 追溯**的（提交信息里写了依据）。

## 四、★ 假阳性 0% —— 但**样本只有 n=1**
```
164 扫过 · 1 可疑 · 1 真 ⇒ 表面假阳性率 0%
⚠★ 但 n=1 **不足以**说"这个探针可靠" —— 一个数据点估不出率
⇒ ★ **不把它升成硬门禁**（那会挡住发布）；**先做成回归测试**，
  并对"动态调用"类留**显式豁免表**（`UNCALLED_EXEMPT`，每条带理由）。
⇒ 将来样本多了再考虑接进 `release_check`。
```
★ 这与本项目此前几次**方向相反**（`052`/`054` 都是"假阳性太高 ⇒ 不成门禁"）；
本轮是"**假阳性低，但样本太少 ⇒ 先不进硬门禁**" —— **两种克制是同一种**。

## 五、★ 一条**方法**上的自我纠正
```
第一版测试：它**自己重写了一遍判法**（`_fake_suspects`）来跑负例
⇒ ★ 那不叫"测到了工具" —— 测的是"测试自己写的一份"（事实 62 的精神）
⇒ 改成：把判法抽成 `probe.find_uncalled(root=…)`，
  **`main()` 与测试跑同一份代码**
```
⚠ 这条值得记：**负例如果绕开被测对象，就只是"另一个实现的自测"。**

## 六、与其它记录的关系
```
事实 40  存在但没人用的守卫 ≡ 没有守卫          ←  本条的**类**（常量形态在 053/054）
事实 61  好用的工具函数要用在所有同类场合        ←  本条的**动机**（定则④）
事实 62  门禁"写了"≠"有效"，负例是唯一的证明     ←  本条的**方法**（且本轮还纠正了负例的写法）
事实 74  按名字判语义的检查做不成门禁            ←  本条的**边界**（本探针判的是**结构**，不是语义）
```
★ 合起来：**判"结构"（有没有被调用）比判"语义"（是不是长度）可靠得多。**
"""

P = Path(r"C:\swprojects\sw-skill-fork\docs\dead-guards.md")
P.write_text(DOC, encoding="utf-8")
print("  ok 已写 docs/dead-guards.md（%d 行）" % len(DOC.splitlines()))

# 已知事实 77
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
ADD = """

| # | 事实 | 依据 |
|---|---|---|
| 77 | **死守卫的第二种形态：「定义了却从没被调用的函数」—— 而且判「结构」比判「语义」可靠** —— 2026-10-01（轮 136）用 `tools/probe_uncalled_helpers.py` 扫 6 类门禁/工具文件（`scripts/check_*`·`audit_*`·`gen_*`·`tools/*`）的**模块级 def**（排除 `main`/`register`/`run`），数名字在全仓库的出现次数：**164 扫过 · 1 可疑 · 1 真（假阳性 0%）**。唯一那个是 `tools/propose_capability_sources.py::match_modules` —— `stems_only()` 的**旧版**（会**扫文件体**，而 `stems_only()` 的 docstring 明写「**不再扫文件体**」「第一版…命中面进一步失控」）⇒ **被取代却一直留着** ⇒ 已**删除并留墓碑注释**。⚠★ **但样本只有 n=1** ⇒ "0% 假阳性" **不足以**升成硬门禁 ⇒ **先做成回归测试** + 显式豁免表（`UNCALLED_EXEMPT`）。★ 一条方法上的自我纠正：第一版测试**自己重写了一遍判法**跑负例 ⇒ **那不叫测到了工具**（事实 62 精神）⇒ 改成把判法抽成 `probe.find_uncalled(root=…)`，**`main()` 与测试跑同一份代码**。★ 与事实 74 对照：**判"结构"（有没有被调用）比判"语义"（是不是长度）可靠得多** | `tools/probe_uncalled_helpers.py`（`find_uncalled`）；`tests/test_no_uncalled_helpers.py`（3 条，含**调真函数**的负例）；`docs/dead-guards.md`；事实 40 / 61 / 62 / 74 |
"""
if "死守卫的第二种形态" not in tk:
    K.write_text(tk.rstrip() + ADD, encoding="utf-8")
    print("  ok known-facts 已加 77")
else:
    print("  已有 77")
