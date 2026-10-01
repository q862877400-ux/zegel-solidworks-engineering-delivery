# 047 · 把轮 123~127 查证并**真机跑过**的 4 个入口接出去（batch10）

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
