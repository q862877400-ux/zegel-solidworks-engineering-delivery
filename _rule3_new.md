### 规则 3 · 选择：**必须用声明式 `selection`，禁止裸坐标**

**实际形态**（★ 照代码写，见下「与文档的差异」）：

```python
#: `selection` 是**字符串选择器**（或一个 COM 对象），另配 `kind` 说明选什么
"selection": "__current_selection__"   #: 用当前选区里的第一个（**不重选**）
"selection": "index:<n>"               #: 该体上第 n 个实体（0 基；**会重选**，带越界检查）
"selection": <COM 对象>                 #: 直接 Select4 它
"kind": "EDGE" | "FACE"                #: 合法值来自 `sw_selection_spec.ENTITY_KINDS`
```

实现与入口（可 grep 核对）：

| 函数 | 作用 |
|---|---|
| `sw_selection_spec.resolve_entity(model, selector, kind, *, body_index=0)` | 解析选择器 → **已选中的实体对象** |
| `sw_selection_spec.resolve_selection(model, selector, kind, *, body_index=0)` | 同上，但**只回读选区计数**（0 表示没选中 ⇒ 调用方**不得继续**）|
| `sw_selection_spec.select_entity_by_index` / `select_object` | 按序号 / 按对象选 |
| `sw_selection_spec.entities_on_body(model, kind, *, body_index=0)` | 列出体上的实体（序号来源）|

底层把选择解析为**实体上的一点**再按 3D 坐标选（绕开 pywin32 无法 QueryInterface
`Face2`→`IEntity` 的限制），并**按 mark 分配**（多引用特征读 mark 0/1/2，不读选择顺序）。

**为什么禁止裸坐标**：侧边栏一拉、DPI 一变、几何一重建，坐标就错。
本仓库已在嘉立创 GUI 上为此吃过 12 轮返工。

**来源**：Slacker-LLC（Apache-2.0）· 其 README 明写「Exposing that to an agent is hopeless」。

#### ⚠⚠ 与文档的差异（2026-10-01 轮 218 实测核对，**本节是更正**）

本规则此前还写了下面这两条 —— ★ **代码里没有**（按铁律 5，**写明"未实现"**，不再当作既有能力）：

| 此前文档所述 | 实测 | 处置 |
|---|---|---|
| dict 形态：`{ "selection": { "edges": [4, 6, 9] } }` · `{ "face_edges": [2] }` · `{ "planes": ["front"] }` | `resolve_entity` / `resolve_selection` 接受的是**字符串选择器或 COM 对象**，**没有 dict 分支** | ★ **未实现** —— 保留为**目标形态**，不当作现状 |
| 「索引来自 `list_faces` / `list_edges` / `list_vertices` / `list_sketch_segments`」 | 这四个函数 **grep 0 命中（不存在）** | ★ **未实现** —— 现存序号来源是 `entities_on_body` |

**核查命令**（可重跑，两条都应给出"不存在"）：
```
grep -rn "def list_faces\|def list_edges\|def list_vertices\|def list_sketch_segments" scripts/
python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\scripts'];import inspect,sw_selection_spec as m;print(inspect.signature(m.resolve_entity))"
```

#### 校验（★ 只覆盖本规则三句里的**第一句**）

**已实现**：新增工具的参数 schema 里不出现裸 `x`/`y`/`z` 浮点
（`mcp-server/tool_registry.py` 的 `_BARE_COORD_NAMES`；除非该工具本身是
`*_at_point` 类且注明用途）。

**★ 未实现（因此无人看守，会漂移）**：
1. **「选择必须是声明式的」** —— 门禁**不检查** `selection` 参数的取值形态；
2. **「按 mark 分配」** —— 门禁**不检查**；且 `select_object` / `Select4` **不取 mark**，
   多引用特征所需的 mark 0/1/2 目前只能由**各调用点自己传**。

> ★ 一条规则若含多个子句，要**逐子句问"机器验了哪几个"**；没验的子句不是不存在，
> 而是**在无人看守地漂移**（事实 153）。

