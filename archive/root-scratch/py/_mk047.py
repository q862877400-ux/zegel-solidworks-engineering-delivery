import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\047-batch10-expose-verified-entries")
S.mkdir(parents=True, exist_ok=True)

spec = """# 047 · 把轮 123~127 查证并**真机跑过**的 4 个入口接出去（batch10）

**Status**: Implemented（轮 128）

## 一、为什么补这一轮
`042`~`046` 查证并接出了一批高层入口，但它们**只活在 `scripts/` 里**：
```
sw_part.get_bounding_box                    轮 127 · 真机 8/8 · 偏差 0.00e+00
sw_hole_features.list_hole_standards        轮 124 · 真机 6/6 · 15 条真实标准
sw_hole_features.list_fastener_types        轮 125 · 真机 11/11 · 14 条
sw_hole_features.list_fastener_table_types  轮 125 · 真机 11/11
```
★ 与 `014`/`015` 的「孤立函数从没跑过」相对：这几个**跑过了**，
但**还没接出去** —— **不接出去，外部使用者拿不到**。

## 二、★ 一个需要说清的点：`inject="sw_app"`
`list_*` 三个要的是 **`ISldWorks`**（不是活动文档）。
⇒ `tool_registry` 的 `inject` **本来就支持 `"sw_app"`**
（`register_capabilities.RESOLVERS` 里有解析器）⇒ **不需要新造机制**。

## 三、★★ 比「直接调函数」更值钱的一步：走**声明层**验证
```
已有的两个冒烟证的是**函数**能用；
本轮新增的冒烟证的是**声明**能用 —— 即
  ToolSpec（手抄的参数名 + 注入名） → RESOLVERS 解析宿主对象 → 真调
★ 这条路上任何一个环节写错（参数名手抄错、注入名搞错、read_only 标错），
  静态测试**都发现不了** —— 只有真机跑一次才知道。
```
真机 **7/7**：
```
✓ batch10 的 4 条都在 all_specs() 里      all_specs() 共 41 条
✓ ★ solidworks_part_bounding_box    (inject=model)
✓ ★ solidworks_hole_standards       (inject=sw_app)  15 条
✓ ★ solidworks_fastener_types       (inject=sw_app)  14 条
✓ ★ solidworks_fastener_table_types (inject=sw_app)  3 条
✓ 收尾无残留模态框
```

## 四、判据
| ID | 判据 |
|---|---|
| SC-4301 | 4 条声明都在 `all_specs()` 里（37 → **41**）|
| SC-4302 | ★ 参数名逐条与 `inspect.signature` 对得上 |
| SC-4303 | ★ **两种注入混用**（`model` / `sw_app`）且与真实首参一致 |
| SC-4304 | ★ 4 条**都标了 `read_only`**（与 batch9 相反：那 3 个改几何）|
| SC-4305 | ★★ **走声明层真机 7/7**（声明 → 解析器 → 调用）|
| SC-4306 | ★ 每条声明把**实测警告**带给调用方（approximate / 毫米 / UI 语言 / Int32 ID）|
| SC-4307 | 数量守卫测试同步更新（**37 → 41**），并保留历史说明 |
| SC-4308 | 门禁 + 回归不退化（回归 **1149 passed**）|

## 五、暴露面变化
```
`all_specs()` 37 → **41**；并集 420 → **424 操作**；本仓库独家 71 → **75**
```

## ⚠ 明确记下的限度
* ⚠ **只证到「声明 → 解析器 → 调用」**，**不证 MCP 协议层**（那要起 server）；
* `harvest-report.md` 里的「工具 83 个」一类**总暴露数**本轮**没有重新统计**；
* 4 条都是**只读**；`bbox` 只测了 1 个盒子；孔标准只测了 `hole_type_id=0`。
"""

plan = """# 047 · Plan

## 步骤
1. 看 MCP 层的形态 ⇒ `tool_specs_batch*.py` 声明式 + `inject`
2. ★ 确认 `inject` **本来就支持 `sw_app`** ⇒ 不需要新造机制
3. 写 `tool_specs_batch10.py`（4 条，参数逐条照真实签名抄）
4. 注册进 `register_capabilities.BATCH_MODULES`
5. 守卫测试（**16 条**）—— 含 `read_only` 与"警告要带给调用方"
6. ★★ **走声明层的真机冒烟**（比直接调函数更值钱）⇒ **7/7**
7. 更新数量守卫（37 → 41）+ 重生成 + 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 为 `sw_app` 新造注入机制 | ★ **先查** ⇒ 已支持，不加东西（"不重造"）|
| 只测函数、不测声明 | ★ **走声明层跑一次**（参数名抄错只有真机能发现）|
| 忘了标 `read_only` | ★ 测试会红（**本轮真的红了**）|
| 数量守卫忘了改 | ★ 它设计成"变了就红" ⇒ 同步更新并留历史说明 |
"""

tasks = """# 047 · Tasks（全部完成，轮 128）

- [x] T-4301 查 MCP 层形态 + 确认 `inject` 支持 `sw_app`（**不新造机制**）
- [x] T-4302 写 `mcp-server/tool_specs_batch10.py`（4 条）
- [x] T-4303 注册进 `BATCH_MODULES`
  `→ 验收:` `python -c "import register_capabilities as rc; print(len(rc.all_specs()))"`（**41**）
- [x] T-4304 守卫测试 `tests/test_tool_specs_batch10.py`（**16 passed**）
- [x] T-4305 ★★ 走声明层的真机冒烟 `tools/verify_batch10_smoke.py`
  `→ 验收:` `python tools/verify_batch10_smoke.py`（**7/7**）
- [x] T-4306 数量守卫测试同步（37 → **41**，保留历史说明）
- [x] T-4307 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 047 · Converge

**Converged**: 2026-10-01（轮 128）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-4301 4 条都在 all_specs() | ✅ 37 → **41** |
| SC-4302 参数名对得上签名 | ✅ 16 条测试 |
| SC-4303 两种注入混用且与首参一致 | ✅ `model` / `sw_app` |
| SC-4304 都标 `read_only` | ✅（**第一次跑真的红了**，补上才过）|
| SC-4305 走声明层真机 7/7 | ✅ |
| SC-4306 实测警告带给调用方 | ✅ 测试钉住 4 条要点 |
| SC-4307 数量守卫同步 | ✅ 保留历史说明 |
| SC-4308 门禁 + 回归 | ✅ `release_check` exit 0 · **1149 passed** |

**暴露面**：`all_specs()` **37 → 41** · 并集 420 → **424 操作** · 独家 71 → **75**

## 二、★★ 本轮的形状：**先查有没有现成机制，再动手**
```
需求：把 `list_*` 三个接出去 —— 它们要的是 `ISldWorks`，不是活动文档
⇒ 第一反应可以是"给 registry 加一种注入"
⇒ ★ **先查** ⇒ `inject="sw_app"` **本来就支持**，`RESOLVERS` 里也有解析器
⇒ **一行都不加机制**
```
★ 这正是「**不要为了修房子创建公司**」在这一轮的具体落点。

## 三、★★ 为什么"走声明层跑一次"比"直接调函数"值钱
```
函数冒烟（已有 2 个）：证 `get_bounding_box` / `list_*` 能跑
声明冒烟（本轮）   ：证 **手抄的声明**能不能把调用**正确地**送进去
⇒ 参数名抄错、注入名搞错、`read_only` 标错 ——
  这些**静态测试只能查"存不存在"，查不出"对不对得上语义"**
```
★ 而本轮**真的抓到了一条**：`read_only` **忘了标** ⇒ 测试红 ⇒ 补上。
⚠ 若只跑函数冒烟，这条**永远不会被发现**（函数本身完全正常）。

## 四、⚠ 一条仍未被证的边界
```
本轮只证到「**声明 → RESOLVERS → 调用**」；
**MCP 协议层**（起 server、经 JSON-RPC 真调一次）**未证**。
⇒ 那句"接出去了"目前是**到这个深度为止**，不是"端到端已通"。
```
★ 与 `014`/`015` 的教训一脉相承：**"接出去"要分层说清楚接到了哪一层。**

## 五、未查证
* **MCP 协议层未证**；
* `harvest-report.md` 的**总暴露数**（"工具 83 个"一类）本轮**没有重新统计**；
* 4 条都是只读；`bbox` 只测 1 个盒子；孔标准只测 `hole_type_id=0`。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
