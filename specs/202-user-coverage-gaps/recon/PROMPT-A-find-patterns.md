# 提示词 A · 找规律（★ 整段复制给 Opus 5.5 / Sonnet 5.5）

> ★★ **这份提示词的目标只有一个：让你真的找到东西。**
> ★ 它不是"任务摘要"，★ 它把**你要读的全部源、判断缺陷的全部口径、搜索的具体配方、
> 以及"一条合格发现长什么样"的完整范例**都写在里面。★ **不需要你猜我的标准**。
> ★★ 唯一的形式要求：**先把 `PRICEY-FINDINGS-INDEX.md` 落盘**（万一中断，清单还在），
> **然后每写完一节立刻追加到 `PRICEY-FINDINGS.md`**。★ 其余**不要省**。

---

# 第 0 部分 · 你在什么仓库里

`D:\AI\SW` 是一个 **SolidWorks 自动化仓库**（Python + COM，pywin32 迟到绑定）。
它的目标是把**官方 SolidWorks API 全覆盖**，并把能力暴露成 **MCP 工具**。

**它的架构（你必须先懂这四个概念，否则认不出缺陷）**：

| 概念 | 是什么 | 在哪 |
|---|---|---|
| **能力层** | 真正干活的 Python 函数，直接调 COM（`get_com_member(obj, "MemberName", ...)`）| `scripts/sw_*.py` |
| **工具层（ToolSpec）** | 把能力层包成 MCP 工具：声明 `name` / `module` / `function` / `inject` / `params` / `pre_call` / `param_alias` / `doc` | `mcp-server/tool_specs_batch*.py` |
| **注册器** | 把 ToolSpec 变成可调函数 | `mcp-server/tool_registry.py` 的 `make_tool_function._impl` |
| ★ **调用顺序** | ★★ **`kwargs[inject] = RESOLVERS[inject](params)` → `spec.pre_call(params)` → `derived_args(params)` → `目标函数(**kwargs)`** | 同上 |
| **官方文档（离线）** | ★ 三套源：`C:\swapi\types\<接口>\<成员>.md`（**精确签名 + Remarks**）· `C:\swapi\examples\*.md`（**官方例子的调用序与配方实参**）· `C:\swapi\enums\*.md`（**枚举 name→value**）· `D:\AI\SW\AI Solidworks\官方文档\SWhelp\sldworksapi\`（CHM 解包）· 反射 `D:\AI\SW\_raw\` | 本机 |

★★ **注册器那个顺序是理解一大半缺陷的钥匙**：
- `inject` 解析器**先跑** ⇒ ★★ **MCP 客户端根本没有"在调用工具之前先选好某个东西"这条通路**
  ⇒ ★ **凡"要求调用方先选"的工具，必须把那次选择写进 `pre_call`**，否则**必然失败**；
- `param_alias` 里值为 `None` = 「**该参数由解析器/`pre_call` 消费、不进目标函数**」。

---

# 第 1 部分 · 你要读的**全部**源（★ 一份都别漏，漏了就找不到）

## 1.1 ★★ 核心输入：30 份逐条核对表
`specs/202-user-coverage-gaps/recon/audit-vs-official/`
★ 文件名形态：`audit-<域号>-<域名>-<核对面>.md` ⇒ **10 域 × 3 核对面 = 30 份**
- 域：`01-surface` `02-sheetmetal` `03-weldment` `04-assembly` `05-drawing` `06-features` `07-sketch` `08-mold-costing` `09-simulation` `10-misc`
- 核对面：**A** = 签名一致性 · **B** = 前置与 mark · **C** = 废弃链与枚举取值

★ 每份的结构（★ 直接读，格式固定）：
```
# audit-01-surface · 核对 A（签名一致性）
- 域 / 我们这边的文件 / 官方源 / 判据        ← 头部说明

## 分歧表
| # | 我们的原文（文件 + 片段）| 官方的原文（文件 + 片段）| 分歧点 | 置信度 |
|---|---|---|---|---|
| 1 | ... | ... | ... | 高 |

## 查不到（不计入分歧）
- ...（没找到官方依据的，★ 不算分歧）

## 结尾三行
- 都核了 **35 处**调用点与官方 **Signature**
- 报了 **4 条**（#1 #2 顺序不符 · #3 标量/数组类型不符 · #4 short/int 声明类型不符）
- 置信度为**高**的是：**#1、#2**
```
★ 目录里还有 `patterns-shard-{1,2,3}.md`（前一轮的抽录稿）—— **也读，但别当结论**。

## 1.2 官方契约摘要（10 份，按域）
`specs/202-user-coverage-gaps/recon/api-pre/`
★ 已落：`api-01-surface` `api-03-weldment` `api-04-assembly` `api-06-features` `api-07-sketch` `api-09-simulation` `api-10-routing-pdm-anim`（★ 其余可能仍在生成，★ 缺的就直接去 `C:\swapi` 读原文）。
★ 每份含：**精确签名**（含几个参数）· **`## Remarks` 的前置** · **官方例子的调用序与配方实参** · **枚举值** · **废弃链**。

## 1.3 ★ 两份官方索引（机器可读，★ 用它们做定量核）
| 文件 | 内容 |
|---|---|
| `specs/202-user-coverage-gaps/recon/official-obsolete-index.json` | ★ 官方废弃成员 **1671** 个，★ 每条含**官方那句原文**（`Obsolete. Superseded by [[IEntity::Select4]].`）+ **点名后继**（1586 个有）|
| `specs/202-user-coverage-gaps/recon/official-members-index.json` | ★ 官方全量：**566 接口** · **8239 唯一成员名** · 每个成员的所属接口与是否废弃 |

## 1.4 本仓的知识库（★ 判断"是不是已知/已证伪"就靠这些）
| 文件 | 内容 |
|---|---|
| `docs/known-facts.md` | ★★ **500+ 条已知事实**（★ **必读**，★ 至少通读标题列）|
| `docs/dead-ends.md` | ★ **45 条走死的路 / 28 个能力**（★ 由脚本生成）|
| `capabilities.yaml` | 每条能力的 `level` 与 **`limitations`**（★ **第一现场**；走死的路先看这里）|
| `specs/202-user-coverage-gaps/recon/preselect-family-merged.md` | 「要求调用方先选」工具族的合并总表（★ 分档：真危险 / 安全 / 无关）|
| `specs/202-user-coverage-gaps/recon/s2b-A-wireability-merged.md` | 「台账有、工具无」41 条的**可挂性**判定 |
| `specs/202-user-coverage-gaps/recon/PATTERN-SCORECARD.md` | ★★ **我的验收标准**（六维度 + 两道否决闸）|
| `docs/ROADMAP.md` / `docs/metrics.md` | 进度与指标 |

## 1.5 代码（★ 你要**认得出**缺陷，就得读这些）
| 路径 | 读它的什么 |
|---|---|
| `mcp-server/tool_specs_batch*.py` | ★ **全部 ToolSpec**：`name` / `params` / `pre_call` / `param_alias` / `doc` |
| `mcp-server/tool_registry.py` | ★ 注册器（`_impl` 的调用顺序、`param_alias` 语义、`Param` 的字段名是 **`kind`** 不是 `type`）|
| `scripts/sw_*.py` | ★ 能力层：真正的 COM 调用、前置判据、`return` 的形状 |
| `tools/` | ★ 已有的扫描器与探针（★ 很多判据已经写好了，**先读它们再动手**）|

---

# 第 2 部分 · ★★★ 缺陷类型名录（**带真实例子** —— 拿它当"打猎模板"）

★★ 下面**每一类都是我在这个仓库里真实找到并修过的**。★ **你的任务是：用这些模板去 30 份核对表 + 代码里，
把还没被找到的同类实例找出来。** ★ 每类我都给了「**怎么认出它**」和「**一个真实实例**」。

## 模板 1 · 「注册了，但根本跑不通」
**怎么认出**：★ spec 声明的参数 **≠** 目标函数的形参；或目标函数有**硬前置**（读选区计数、0 就回退），
★ 而 spec **既没有"给选区"的参数、也没有 `pre_call`** ⇒ ★★ **调用方无从满足** ⇒ 必然失败。
**真实实例**：
- ★ **11 条**注入名 ≠ 形参名（`inject="sw"` 而目标是 `model`）⇒ 真机 `TypeError`；
- ★ `solidworks_delivery_pack_and_go_audit_matrix` 缺 **5 个必填形参** ⇒ 真机 `TypeError: missing 2 required positional arguments`；
- ★★ **「显式拒」四件套**：`part_sweep` / `part_loft` / `part_axis` / `part_wrap`
  —— 目标函数读到 `mark=0` 就 `return {"ok": False, "stage": "selection"}`，
  ★ 而 spec **只有 `cut` / `closed` 这类参数** ⇒ ★ 真机实测四条**全部**停在 `stage: selection`。

## 模板 2 · **成功路径没有 `return`**
**怎么认出**：★ 函数**最后一个语句是 `except` 分支里的 `return`** ⇒ ★ 正常路径"掉出末尾"返回 `None`
⇒ ★★ **调用方分不清"没建成"与"没返回值"**。
**真实实例**：★ `scripts/sw_sweep.py::create_sweep_report`（★ 已修）。
★★ 它造成的**真实后果**：★ 我一度据此写下"卡在扫描 API 自身"的结论，★ **而当时是没有证据的** ——
★ 我把 `None` 读成了"没建成"。

## 模板 3 · **docstring 承诺了、代码没做**
**怎么认出**：★ spec 的 `doc` 或函数 docstring 里**逐字写着一个判据**，★ 而代码里**没有那个检查**。
**真实实例**：★ `create_sweep_report` 的 docstring 写着
「判据：**特征树多了新特征** **且** **类型名 = `Sweep`**」★ 而**类型名检查从来没实现**（★ 已修，补上了）。

## 模板 4 · **mark 值不对 / 没给 mark**
**怎么认出**：★ 官方 `## Remarks` 里有一张 **mark 表**（"…with the following Marks: Direction of pull → **1** / Parting line edges → **4**"），
★ 而我们**要么没选**、**要么 mark 传了 0**。
**真实实例**：★ 本仓 30 份核对里 **20 条（33%）**都是这一类；
★ 具体如：「官方要求**参考曲面**先以 **mark=1** 选中（`UseAutoSelect` 管的是**体**、不是这张曲面）；★ 我们既没选曲面、也没用 mark=1」。

## 模板 5 · **调用序不对**
**怎么认出**：★ 官方**例子**（`C:\swapi\examples\*.md`）给的是**调用序**，★ 而我们顺序不对。
**真实实例**：★ 「官方是 **Pre → 选中剪裁面 → Post**；★ 我们是 **选中 → Pre → Post**，★ 两步之间不再选一次」。

## 模板 6 · **用了官方废弃成员**（★ 但**必须按接口判**，见模板 9 的陷阱）
**真实实例**：★ `_select_com_object` 里 **`Select2` 被排在前面**，★ 而官方页逐字
「**Obsolete. Superseded by [[IEntity::Select4]].**」；★ 且它的 `Select4` 分支
**给 `Select4` 传的是空 VARIANT**、而官方签名是 `Select4(bool Append, **SelectData** Data)`
⇒ ★★ **`Select4` 分支的 `Mark` 永远是 0**（★ 被 `Select2` 盖住了，★ 已修）。

## 模板 7 · **枚举取值不是合法成员**
**怎么认出**：★ 代码里把**字面量整数**（如 `195` / `2` / `4`）当枚举传，★ 去 `C:\swapi\enums\*.md` 查那个**值**是不是合法成员。
**真实实例**：★ `swSurfaceExtendEndCondUpToSurface` / `swRuledSurfaceType_TangentToSurface` —— ★ 这两个名字**不是合法枚举成员**。

## 模板 8 · **判据本身是假的（"判 0 处 = 没问题"）**
**怎么认出**：★ 一个检查器/门禁打印"0 处问题"，★ 但**它其实什么都没比**（读了不存在的字段、或者没跟调用图）。
**真实实例**：★ 我曾写出一条判据读 `getattr(p, "type", None)`，★ 而 `Param` 的字段名是 **`kind`**
⇒ ★★ **"0 处不符"是真空的**（★ 我靠"无默认值的 0 个"这个**不可能**的读数才发现）；
★ 另一例：★ 我把 3 个 `pre_call` 判成"没有回读计数"，★ 而它们其实是**薄包装**（`_pre_edge_flange → _select → resolve_selection` 会回读）。
★★ **教训**：★ **判据必须自报覆盖面、必须跟调用图、必须先标定**。

## 模板 9 · ★★★ **陷阱：同名成员散在多个接口上**（★ 这一条会毁掉你的定量结论）
**怎么认出**：★ 你按**成员名**去对官方名单时，★ 先问：**这个名字在几个接口上出现？其中几个命中？**
**真实实例**：★ 我按名字扫废弃名单，报出 **870 处** —— ★ 而**头几名全是假阳性**：
| 名字 | 定义它的接口数 | 其中废弃的 |
|---|---|---|
| ★★ **`FeatureCut4`** | 2 | 1 —— ★★ **而本仓事实 1 逐字说它才是"切除的正确入口"** |
| ★ **`Name`** | **24** | **2** |
| ★ `GetBodies2` | 2 | 1（`IComponent2`，★ 而 `IModelDoc2.GetBodies2` 好好的）|
| ★ `CreateLine` / `GetEdges` | 3 / 8 | 1 |
⇒ ★★ **官方 API 是「接口 × 成员」的二维表**（566 接口 × 8239 成员名），
★ 而 **`get_com_member(x, "GetBodies2")` 里的 `x` 属于哪个接口，静态源码里看不出来**（运行时对象）。
⇒ ★★ **凡你的规律涉及"按名字对名单"，必须自带这个检查，并在报告里报出你的误报率。**

---

# 第 3 部分 · ★ 「一条合格的发现长什么样」（★ 完整范例，照这个写）

★★ 下面是一条**真合格**的发现（★ 我实际做过的），★ **你要交的东西就是这个粒度**：

> ### 规律：`create_sweep_report` 的**成功路径没有 `return`**，导致"没返回值"被读成"没建成"
>
> **覆盖量**：★ **1 条函数**，★ 但**影响面** = 所有调用它的 spec（★ 现 1 条：`solidworks_part_sweep`）。
> ★ **可独立重算**：★ `python -c "import ast; t=ast.parse(open('scripts/sw_sweep.py').read()); f=[n for n in ast.walk(t) if isinstance(n,ast.FunctionDef) and n.name=='create_sweep_report'][0]; print(sorted(n.lineno for n in ast.walk(f) if isinstance(n,ast.Return)))"`
> ★ 修复前输出 `[75, 84, 93, 96, 119]` —— ★★ **最后一个 `return` 在 `except` 分支里，行号 120 是函数末尾**。
>
> **我们的原文**：`scripts/sw_sweep.py`：
> ```python
>     try:
>         feat = get_com_member(fm, "CreateFeature", data)
>     except Exception as exc:
>         return {"ok": False, "stage": "CreateFeature", ...}   # ← 函数里最后一个 return
> ```
> **官方的原文**：★ 不适用（★ 这是**本仓自身**的缺陷，不是与官方分歧）——
> ★★ **但它有一份"内部契约"可以对**：★ 同函数 docstring 逐字写着
> 「判据：**特征树多了新特征** **且** **类型名 = `Sweep`**」⇒ ★ **代码没实现它**。
>
> **后果（★ 有实证）**：★ 探针读到 `ret_type=None` ⇒ ★ 我据此写下"卡在扫描 API 自身"的结论
> ⇒ ★★ **而当时是没有证据的**（★ 我把 `None` 读成了"没建成"）。
>
> **误报检验**：★ 拿反例表试 ⇒ ★ 与 `FeatureCut4`/`Name` 那类无关（★ 本条**不按名字对名单**）⇒ **不误报**。
>
> **批量可行性**：
> - ★ **一个脚本能找全吗？** ★★ **能** —— ★ **AST 扫"函数最后一条语句是不是 `Return`"**，
>   而且**能扫全仓**（★ 这是一个**通用形态**，不是这一处）。
> - ★ **一个共用修法能改全吗？** ★ **半能** —— ★ "补 `return`"是共用形态，
>   ★ 但**每个函数该返回什么字段**要看它的 docstring ⇒ ★ 需要逐条定字段。
>
> **建议动作**：★ ★★ **造门禁** —— 加一条静态判据「**凡声明返回 `dict` 的函数，其函数体最后一条语句必须是 `Return`**」
> ★ 并配负例（★ 用 `git show <修复前>:scripts/sw_sweep.py` 当输入，★ **必须命中**）。
>
> **置信度**：★ **高** —— ★ AST 可复算、★ 后果有真机证据、★ 修复已验证。

★★ **注意这条发现的形态**：★ 它**不是**"某处参数写错了"，★ 而是「**一个通用形态**（缺 `return`）
★ + **可被静态扫全** + **可造门禁**」。★★ **这正是"可批量"的含义** —— ★ 你要找的是**这种**，★ 不是单点 bug。

---

# 第 4 部分 · ★★ 搜索配方（★ 直接用，省你摸索）

```bash
cd D:\AI\SW

# ① 30 份核对表里所有"分歧点"列（★ 先做频次统计，★ 找大类）
grep -h "^| *[0-9]" specs/202-user-coverage-gaps/recon/audit-vs-official/audit-*.md

# ② 所有 ToolSpec 的 pre_call / param_alias 现状（★ 找"缺 pre_call 却需要前置"的）
grep -n "pre_call=\|param_alias=\|^        name=\"" mcp-server/tool_specs_batch*.py

# ③ 所有"读到选区计数就回退"的硬前置（★ 这些**必须**有 pre_call 或"给选区"的参数）
grep -n "GetSelectedObjectCount2" scripts/*.py

# ④ 所有 scripts/ 里的 COM 成员调用名（★ 拿去与官方索引对）
grep -oh 'get_com_member([^,]*, *"[A-Za-z_][A-Za-z0-9_]*"' scripts/*.py | sort | uniq -c | sort -rn

# ⑤ 所有当字面量传的整数（★ 拿去与 C:\swapi\enums\ 对）
grep -n "get_com_member(.*, *[0-9]\{1,4\}" scripts/*.py

# ⑥ ★★ 全仓"函数最后一条语句不是 return"的（★ 模板 2 的通用扫描）
python - <<'PY'
import ast, pathlib
for f in list(pathlib.Path("scripts").glob("*.py")) + list(pathlib.Path("mcp-server").glob("*.py")):
    try: t = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError: continue
    for n in ast.walk(t):
        if isinstance(n, ast.FunctionDef) and n.body and not isinstance(n.body[-1], (ast.Return, ast.Raise)):
            # ★ 只在"声明了 -> dict"时才是可疑的（★ 否则 if/else 全返回也算正常）
            if n.returns is not None and "dict" in ast.unparse(n.returns):
                print(f"{f}:{n.lineno} {n.name}  最后一条={type(n.body[-1]).__name__}")
PY
```

---

# 第 5 部分 · ★★ 已证伪 / 已记档 —— **不要重复**（★ 重复 = 扣分）

★ 下列结论**已被实测推翻或已记档**。★ 你若发现"规律"其实是它们之一，★ 直接跳过。
★ 要核原文就 `grep -n "| 511 |" docs/known-facts.md`（编号可换）。

| # | 结论 | 状态 |
|---|---|---|
| **511** | ★ 「按**成员名**扫官方废弃名单就能批量修」 | ★★ **已证伪**（★ 见模板 9：870 处、头几名全假阳性）|
| **509** | ★ 「`RESOLVERS[inj]`（注入解析器）会清空选区」 | ★★ **已证伪**：16/16 + 6/6 两组受控实验都没掉。★ **但"前置要写 `pre_call`"这个结论仍成立**，★ 只是机制不是这个（★ 真机制：**MCP 客户端没有"预选"通路**）|
| **506 / 507 / 510** | ★ 「判据报 0 处 = 没问题」 | ★★ **已证伪**（★ 见模板 8）|
| **504 / 505** | ★ 「焊件顶端盖只是前置没调好」 | ★★ **已排除**：`InsertEndCapFeature3` 与 `InsertEndCapFeature2` **两条官方路线都建不成**（★ 五轮排除：选面 6 张全试 · 体是真焊件 · 官方配方实参 · 实心/空心型材）|
| **502** | ★ 「注册了 = 能用」 | ★★ **已证伪**：★ 本会话已修 **18 条**"注册 ≠ 能跑" |
| **36 / 40 / 47** | ★ 「报错指得出真因」/「返回值可信」/「指针族接口能调」| ★★ **已证伪**：★ 同名接口用错时**连读都读不到**；★ `IModeler.Create*Surface` 返回值**跨次都变**；★ **`IAccessSelections` 那族在 pywin32 迟到绑定下不可调用**（★ 20+ 种形态已穷尽）|

---

# 第 6 部分 · 反例表（★ 你的每条结论都要拿它试，并报结果）

| 反例 | 为什么它能证伪你的规律 |
|---|---|
| ★★ **`FeatureCut4`** | ★ 本仓事实 1：它是**正确入口**，★ 却在废弃名单里（同名不同接口）|
| ★ **`Name` / `GetBodies2` / `GetEdges` / `CreateLine`** | ★ 同名不同接口，只有个别接口废弃 |
| ★★ **`part_sweep` / `part_loft`** | ★★ **已手工修好**（挂了 `pre_call` + 参数）⇒ 说它们"缺前置"**是过期的** |
| ★ **`surface_fill` 的硬前置** | ★ **已修**（改成回退）|
| ★ **`create_sweep_report` 缺 `return`** | ★ **已修** |
| ★★ **`Select2` → `Select4`** | ★ **已修**（★ 现在优先走后继 + 真 `ISelectData`，★ 真机验过 mark 落得上）|

---

# 第 7 部分 · 输出与顺序

## ★★ 第一件事（★ 必须先落盘）
`specs/202-user-coverage-gaps/recon/PRICEY-FINDINGS-INDEX.md`
★ 一张表：★ 你**打算**分析的规律清单（每条一行：**候选规律名 · 预计覆盖条数 · 一句话 · 线索来源（哪个文件/哪个模板）**）。

## 然后：每条规律写一节，**追加**到 `PRICEY-FINDINGS.md`
★ 每节按**第 3 部分那个范例的粒度**写，含：
**规律一句话** · **覆盖量（确切条数 + 可独立重算的命令）** · **我们的原文** · **官方的原文 / 或内部契约** ·
**后果（有实证的）** · **误报检验（拿第 6 部分逐个试，报结果）** · **批量可行性（找全？改全？）** ·
**建议动作（造门禁 / 挂共用 `pre_call` / 逐条改 / 只记档）** · **置信度 + 理由**

## ★★★ 优先级（★ 按顺序做，做到哪算哪）
1. ★★ **先写 `PRICEY-FINDINGS-INDEX.md`**
2. ★★★ **把 30 份核对表的分歧做一次全量频次统计**（★ 按第 2 部分那 9 个模板分类）⇒
   **报出：每类几条 · 占比 · 哪些类可批量**（★ 这一节价值最高）
3. ★★ **用模板 1/2/3 去扫全仓代码**（★ 这三类**不需要官方对照**、★ 纯静态可扫、★ 且**最能做成门禁**）
4. ★ 把排序前 5 条写成**完整节**
5. ★ 其余规律写**简表**
6. ★（★ 还有额度）★ **挑战 `PATTERN-SCORECARD.md` §四 里我预填的两条**：★ 它们够不够满分、★ 有没有被我低估的类

---

# 第 8 部分 · 纪律

- ★★ **只写你亲手读到的**；★ 每条论断给**可搜索的原文位置**（★ **不写行号** —— 行号会漂移，★ 要写**原文片段**）；
- ★★ **查不到就说查不到** —— ★ 不许用相似名字蒙混；
- ★★ **不许写"建议注意 / 建议进一步分析"** —— ★ 要么给判据，要么说清为什么给不出；
- ★★ **宁少勿滥** —— ★ 报 3 条铁的，好过报 30 条含水的（★ 本仓已实测过好几次"22 条 → 真的只有 2 条"）；
- ★ **不要重述第 5 部分**；
- ★★ **每写完一节立刻落盘**；
- ★★ **不要改仓库里任何文件**，★ 你的产物只写进 `specs/202-user-coverage-gaps/recon/` 与 `output/`。
