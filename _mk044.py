import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\044-fastener-chain-and-warmup")
S.mkdir(parents=True, exist_ok=True)

spec = """# 044 · 把剩下 3 个孤儿也接上 —— 顺带查出一条**官方没写的行为约束**

**Status**: Implemented（轮 125）

## 一、做法（同一套）
链路：**标准（15）→ 紧固件类型（14）→ 表类型（`[0,1,2]`）**，把每一步接成可用入口。

## 二、★★ 查出一条**官方没写**的约束：`IHoleStandardsData` 必须**先热身**
```
第一版：拿到 data 后**直接**调 GetFastenerTypes          ⇒ 返回 False
        （同一个探针早先明明拿到过 True ⇒ 说明有隐藏状态）
⇒ 不猜，量四组对照：
   A 拿到 data 直接调                        ⇒ False
   B **先调 GetHoleStandards** 再调           ⇒ **True** ✓
   C 在 A 那个未热身对象上**再调一次**         ⇒ 仍 False（⇒ 不是"调一次就好"）
   D 换标准名 'ISO'                          ⇒ 仍 False（⇒ 不是名字问题）
```
⇒ **必须先调一次 `GetHoleStandards` 热身。** 官方文档**只写了各方法自己的前置**，
**没有**这条跨方法的顺序约束。
⇒ 已在 `_hole_standards_data()` 里默认热身（`initialize=False` 可跳过）。

## 三、★ 真机冒烟 **11/11** —— 含一条**反向验证**
```
✓ list_hole_standards            → 15 条 · 命中 ISO / DIN
✓ list_fastener_types('ANSI Inch') → 14 条 · 名不重复
✓ 名称随 UI 语言（中文 UI ⇒ '六角精致螺栓'）
✓ list_fastener_table_types('ANSI Inch', 4) → [0, 1, 2]
✓ ★★ **不热身**时 GetFastenerTypes 返回假值    未热身 -> False（热身 -> True）
```
★★ 最后那条是**反向验证**：它**证明热身步骤真的必要** —— 不是「加了也没坏处」。
★ **这是本项目第一次用「去掉它就会失败」的方式验出一条行为约束。**

## 四、❌ `get_fastener_table` **到不了**
```
官方 Boolean GetFastenerTable(String, Int32, Int32, **out Object** HoleTable)
用**同族另外三个已验过**的容器形态 VARIANT(VT_BYREF|VT_VARIANT, None) 传：
  TableID = 0 / 1 / 2 ⇒ 全报 com_error -2147352571「类型不匹配」**位置 4**
⇒ ★ **同族里只有这一个到不了**（另外三个用同一形态都通）
⚠ 按**事实 53** 停手；保留函数作**可复算的证据**。
```

## 五、判据
| ID | 判据 |
|---|---|
| SC-4001 | 3 条高层入口都在（`list_fastener_types` / `list_fastener_table_types` / `get_fastener_table`）|
| SC-4002 | ★★ **查出击热身约束**，且用**四组对照**排除两种替代解释 |
| SC-4003 | ★ 默认热身；`initialize=False` 可跳过 |
| SC-4004 | ★★ 冒烟含**反向验证**（去掉热身 ⇒ 返回 `False`）|
| SC-4005 | ★ 官方第 2 参是 **Int32**（紧固件 ID）而非尺寸名（真机第一版就栽在这）|
| SC-4006 | ❌ `get_fastener_table` 到不了 —— 源码**如实写明**（含失败位置 4）|
| SC-4007 | ★ 已知事实 69 入库 |
| SC-4008 | 门禁 + 回归不退化（回归 **1124 passed**）|

## 六、**本轮又踩了同一处来源块问题（第三次）**
```
`# 覆盖: 后续同级定义` **会被下一个来源块截断** ——
而我把新函数插进了**两段已有来源块之间**（L262）⇒ 那块不覆盖它
⇒ 改用 `# 覆盖: 全文件`（并在块里写明"为什么这里不能用后续同级定义"）
```
⚠ 这是该问题**第三次**出现 ⇒ **应写进纪律**（每次当场发现不是办法）。

## ⚠ 明确记下的限度
* 只证了 `ANSI Inch` + `hole_type_id=0` 这一条组合；其余标准/孔型**未测**；
* **不证 15 / 14 / `[0,1,2]` 是全集**；`id` 的语义未核；
* `get_fastener_table` **到不了**（未查证换后端能否走通）；
* **没有**注册成 MCP 工具。
"""

plan = """# 044 · Plan

## 步骤
1. 照 `043` 的做法，先走一遍链路量清楚每步要什么、返回什么
2. ⇒ 第二步就暴露：官方第 2 参是 **Int32（紧固件 ID）**，我传了尺寸名
3. 走到 `GetFastenerTable` ⇒ 报「类型不匹配 位置 4」⇒ ★ **按事实 53 停手**
4. 回来写高层入口时发现：**直接调 `GetFastenerTypes` 返回 `False`**
5. ★ **不猜**：四组对照（A/B/C/D）⇒ 查出**必须热身**
6. 把热身做进 `_hole_standards_data()` 默认路径
7. ★ 冒烟里加**反向验证**（去掉热身 ⇒ 失败）
8. 契约测试 + 已知事实 69 + 能力条目 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 看到 `False` 就以为"名字传错了" | ★ **四组对照**排除替代解释 |
| 加个热身"反正没坏处" | ★ **反向验证**证明它必要 |
| 继续试 `GetFastenerTable` 的第 5 种写法 | ★ 事实 53 停手（同族三个已通，只有它不通）|
| 新函数插在两段来源块之间 | ★ 用 `# 覆盖: 全文件` |
"""

tasks = """# 044 · Tasks（全部完成，轮 125）

- [x] T-4001 走链路量清楚每步的参数与返回（`_probe_fastener_chain.py`）
- [x] T-4002 ★ 发现第 2 参是 Int32（紧固件 ID）而非尺寸名
- [x] T-4003 ★ `GetFastenerTable` 报「类型不匹配 位置 4」⇒ 按事实 53 停手
- [x] T-4004 ★★ 四组对照查出**必须热身**（`_probe_fastener_ordering.py`）
- [x] T-4005 写 `list_fastener_types` / `list_fastener_table_types` / `get_fastener_table`
- [x] T-4006 把热身做进 `_hole_standards_data()` 默认路径
- [x] T-4007 冒烟加**反向验证**（11/11）
  `→ 验收:` `python tools/verify_hole_standards_smoke.py`（**11/11**）
- [x] T-4008 契约测试（**19 passed**）+ 已知事实 69 + 能力条目
- [x] T-4009 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 044 · Converge

**Converged**: 2026-10-01（轮 125）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-4001 三条入口都在 | ✅ |
| SC-4002 查出热身约束 + 四组对照 | ✅ A/B/C/D |
| SC-4003 默认热身、可跳过 | ✅ |
| SC-4004 反向验证 | ✅ 未热身 → `False` |
| SC-4005 第 2 参是 Int32 | ✅ 测试钉住 |
| SC-4006 到不了的如实写明 | ✅ 含「位置 4」 |
| SC-4007 事实 69 入库 | ✅ |
| SC-4008 门禁 + 回归 | ✅ `release_check` exit 0 · **1124 passed** |

## 二、★★ 本轮最有价值的是**「四组对照」这个方法**
```
第一版看到 `False` ⇒ 最自然的反应是"名字传错了吧？"
⇒ 若只改名字试一次，会继续 `False`，然后可能去怀疑标准名、怀疑对象、怀疑后端……
★ 四组对照（A/B/C/D）一次把三种替代解释**同时排除**：
   · 不是"调一次就好"（C：同一对象再调仍 False）
   · 不是"名字问题"（D：换 'ISO' 仍 False）
   · 只剩"必须先调 GetHoleStandards"（B）
```
★ 与 `042` 的四形态实验是**同一个手法**：**把候选解释列出来，一次全测**。

## 三、★ 「反向验证」是本项目第一次
```
以往的证据都是"做了 X 之后 Y 成立"
本轮的是"**不做 X 就不成立**"（不热身 ⇒ False）
⇒ ★ 这才证明 X **必要**，而不只是"无害"
```
★ 与事实 62（「一个门禁『写了』不等于它『有效』，负例是唯一的证明」）**同一思路**，
只是这次的对象不是门禁，而是**一条运行期约束**。

## 四、★ 两轮的对照很干净
```
043：接上 1 个孤儿（`list_hole_standards`），真机 6/6
044：接上另 3 个（其中 2 个可用、1 个到不了），真机 11/11
⇒ ★ 而"到不了"那一条也**如实写进了源码与能力条目**
```
★ **"接上"不等于"都能用"** —— 本轮把「**能用的**」与「**到不了的**」分开报。

## 五、⚠ 同一个来源块问题**第三次**出现
```
`# 覆盖: 后续同级定义` 会被下一个来源块截断
⇒ 新函数插在两段已有块之间时，用「后续同级定义」不生效
⚠ 三次了（119 是判据被文档串误伤；124/125 是覆盖范围）
```
⇒ **该写进纪律**，而不是每次当场发现。

## 六、未查证
* 只证了 `ANSI Inch` + `hole_type_id=0` 一条组合；
* **不证** 15 / 14 / `[0,1,2]` 是全集；`id` 语义未核；
* `get_fastener_table` 到不了（换后端未试）；
* **没有**注册成 MCP 工具。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
