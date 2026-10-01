# Plan · Feature 131 草图只读查询

## 一、要查的官方源与冲突裁决顺序

| 序 | 源 | 本特性用它查什么 |
|---|---|---|
| 1 | 出厂类型库反射（`D:\AI\SW\_raw\reflect_sldworks\`） | **裁决者**：`ISketch` 的成员名与 arity |
| 2 | `C:\swapi\types\ISketch\*.md` | 精确签名与枚举 |
| 3 | `D:\AI\SW\AI Solidworks\官方文档\`（CHM 解包，`手册\swdoc.ps1`） | 语义与用法 |
| 4 | 本机实测 | ★ **返回结构**——官方**没写**（见下） |

**冲突裁决**：以**出厂类型库反射**为准（照铁律 4）；三源都查不到 ⇒ 写「查不到」并停下换思路。

## 二、★ 一个官方没写、只能实测的东西：返回结构

```
`ISketch.GetLines2` / `GetArcs2` 的**返回结构官方没有文档**。
⇒ 本机实测（`tools/probe_sketch_getter_shapes.py`，产物 `output/sketch-getter-shapes.json`）：
   画 1 条线 → 12 个 float · 2 条 → 24 · 3 条 → 36
   画 1 段弧 → 16 个 float · 2 段 → 32
⇒ ★ 除数 12 / 16 **来自实测，不是官方**；已写进代码常量并附证据指针。
```

## 三、包装层的形状（★ 由真机探针定，不是设计出来的）

```
真机读数（`tools/probe_sketch_object_routes.py`）：
                    草图打开中   草图已关闭
  GetActiveSketch2      草图1      **None**
  ActiveSketch          草图1      **None**
  按名取                 草图1      **草图1**  ✓
⇒ 取草图对象**只能按名取**；而调用方的实际用法（"草图建完了看看里面有什么"）
  恰恰发生在**草图已经关闭之后**。
```

**分层落点**：
| 逻辑 | 落在哪 | 为什么 |
|---|---|---|
| 取草图对象（按名 / 中英文候选 / 特征树兜底） | `scripts/sw_sketch.resolve_sketch` | ★ **能力应落在 `scripts/`**（别的代码也能用），不藏在工具声明里 |
| 条数翻译（数值数组 → 条数） | `scripts/sw_sketch.count_lines` / `count_arcs` / `count_segments` | 同上 |
| 参数搬运与 MCP 表面 | `mcp-server/tool_specs_batch18.py` | 只做声明 |

★ **不用 `extra_op`**：`batch1` 立的规矩是「全部声明式」；查过它当初不用的原因是**加了 `inject` 后就不需要了**，不是它有问题 ⇒ 本特性沿用同一方向。

## 四、注册机制上的三个决定（都有依据）

| 决定 | 依据 |
|---|---|
| `inject` **不设**（默认 `''` ⇒ 不注入） | 目标函数要的是 `sketch`，不是 `model`；若设 `inject="model"` 会把 model 当第一个位置参数传 ⇒ `TypeError` |
| `param_alias = {"sketch_name": None}` | 该入参由 `derived_args` 消费，**不传给目标函数**（不标记则 `TypeError`） |
| `model` 由 `derived_args` **自己连一次**取 | 照 `tool_specs_batch4.py::_model` 的既有模式 |

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| 官方返回结构变了（除数不再整除） | 薄函数**抛错**，**不静默圆整**（形状变了要被看见） |
| 中英文 UI 名字不同 | 走 `_get_sketch_name_candidates` 候选中英文名，再兜底特征树 |
| 草图已关闭取不到 | 按名取（探针证明可行）；`resolve_sketch` 三步兜底 |
| 多草图场景取错 | 显式 `sketch_name` 优先；留空时按"当前草图名 → 候选名 → 树里最后一个草图特征" |
