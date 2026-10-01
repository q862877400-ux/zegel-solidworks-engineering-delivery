### 规则 3 · 选择：**必须用声明式 `selection`，禁止裸坐标**

```jsonc
{ "selection": { "edges": [4, 6, 9] } }
{ "selection": { "face_edges": [2] } }
{ "selection": { "planes": ["front"] } }
```

索引来自 `list_faces` / `list_edges` / `list_vertices` / `list_sketch_segments`。
底层把选择解析为**实体上的一点**再按 3D 坐标选（绕开 pywin32 无法 QueryInterface
`Face2`→`IEntity` 的限制），并**按 mark 分配**（多引用特征读 mark 0/1/2，不读选择顺序）。

**为什么禁止裸坐标**：侧边栏一拉、DPI 一变、几何一重建，坐标就错。
本仓库已在嘉立创 GUI 上为此吃过 12 轮返工。

**来源**：Slacker-LLC（Apache-2.0）· 其 README 明写「Exposing that to an agent is hopeless」。

**校验**：新增工具的参数 schema 里不出现裸 `x`/`y`/`z` 浮点（除非该工具本身是
`*_at_point` 类且注明用途）。

