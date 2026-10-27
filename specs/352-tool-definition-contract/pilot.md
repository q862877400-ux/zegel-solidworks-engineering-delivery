# 规格 352 · 试点报告（21 条样板：语言判决 + 改写手法）

> 判据：`spec.md` A3（可懂性）。仪器：`tools/eval_lean_comprehension.py`
> （21 题，答案键**从结构化字段机械取**：`read_only` / `writes` / 文档里的
> `仍不可用`·`NOT USABLE` / `generate_macro_with_guard`）。

## 一 · 为什么试点是这 21 条

★ 它们**正好是评测集本身**：5 条管线内部件 + 3 条钣金「本机不可用」+ 10 条只读 + 3 条会改状态。
★ 这四类各考一件事：**身份 / 可用性 / 副作用 / 会不会写** —— 而这四件事**全都该在首句里**，
所以「首句写成元数据」时它们**必然答不出**，正是业主抱怨的那个缺口。

## 二 · 读数

| 臂 | 契约违规 | 可懂性 | read_only 维度 | 首句是元数据 |
|---|---|---|---|---|
| **基线（改写前）** | —（棘轮里 3709 条之一） | **15/21 = 71.4%** | **4/10** | 6 题只能答「看不出来」 |
| ★ **英文改写后** | ★ **0** | ★★ **21/21 = 100%** | ★ **10/10** | 0 |

★ 6 条「看不出来」的落点：2 条只读工具的首句没写 `Read-only`（写的是「★ 遍历…读侧」这类
中文考古），4 条 `solidworks_catalog_*` **根本没有 `doc=`**（空描述，`::` 后面什么都没有）。

## 三 · 语言判决（D2）

★ 选了**英文**。依据三条，按权重排：

1. **`。` 会断句，`.` 不会**（`index.mjs` L34 逐字 `text.split(/[。\n]/)[0]`）⇒
   中文首句一旦按正常中文写法用 `。`，模型只看到**第一个短句**（本仓实测中位 30–50 字），
   而英文整段可用满 **120 字符**。★ 为让中文版通过，我**必须刻意不用 `。`** ——
   这本身就说明：中文能用，但要靠一条**与自然中文写法相反**的约束维持。
2. **本仓已有 216/498 是英文** ⇒ 统一到英文是**收敛**，不是新增第三种状态。
3. DSH 官方 n=72 实测：82% 动词开头、99% 句号收尾、参数描述 100% 句号收尾。

★ **中文对照臂也跑了**（`pilot-zh.json`：21 条同样信息量的中文首句，**刻意不用 `。`**）：
★ 结果 **21/21 = 100%**，与英文臂**平手** ⇒ ★★ **按上面第 1 条选英文**
（英文不依赖「写中文时不许用中文句号」这条反直觉约束）。读数落 `output/comprehension-pilot-zh.json`。

## 四 · 试点改出来的两条工程经验（已写进全量派活规则）

1. ★ **4 条 `catalog_*` 根本没有 `doc=`** ⇒ `migrate_tool_evidence.py --apply-docs`
   现在会在 `params=` 之前**插入** `doc=`（原来只会替换现有节点，那 4 条永远改不到）。
2. ★ **19 条 spec 是工厂生成的**（`_spec(name, title, function, doc, params)`）⇒
   只扫 `ToolSpec(...)` **一条都改不到**；已加「工厂调用」第二落点。
   ★ 「一条都没改」与「那些工具本来就没描述」**长得一模一样** —— 这是本项目反复记过的形态。

## 五 · 样板（照这个抄）

见 `pilot-en.json`。三个典型：

- 只读：`List the assembly feature tree node by node, covering components, features and
  mates. Read-only. Use solidworks_assembly_list_components instead when you only need
  the component list.`
- 本机不可用：`Skip this tool, NOT USABLE on this machine: bend-line and fixed-face
  selection is still unsolved. The CreateDefinition(35) sketch-bend entry point itself is
  correct, so nothing is written to the part.`
- 会写状态：`Create a circular pattern of one feature about an axis. Writes a pattern
  feature into the active part and does not save the document; count counts the
  instances including the seed …`
