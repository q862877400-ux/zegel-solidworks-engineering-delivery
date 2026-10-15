# spec 232 —— 分发口调用点的**盲区形态普查 + 非 0 即红**

> 状态：**离线切片已完成**（2026-10-09 · 主任务 `ff6c7344` 第 6 轮）
> 上游：spec 231 `specs/231-dispatch-byref-guard/` 的「未完成」第 1 条（别名导入）
> 性质：**纯离线静态门禁**。未调 COM / 真机，未提交，未部署。

## 一、为什么（靶子）

spec 231 的交接单待办 1 写：

> **别名导入**（`import sw_a as x` 后 `x._d(...)`；`from sw_a import _d as f`）——
> 现在 `check_dispatch_entry_guard._import_map` 只认 `from <stem> import <name>`，
> `as` 形式**只处理了 `ImportFrom` 的 asname、没处理 `Import` 的模块别名**。

### ★★ 前提先核（本仓纪律：交接单的前提也可能是错的）

读 `scripts/check_dispatch_entry_guard.py:239-241` 后确认，**这条前提有一半是错的**：

```python
elif isinstance(node, ast.Import):
    for al in node.names:
        m[al.asname or al.name.split(".")[-1]] = al.name.split(".")[-1]
        #   ↑ `asname` **被处理了**（`import sw_a as x` ⇒ m["x"]="sw_a"）
```

真正的缺口不在 `_import_map`，而在**消费端** `_entry_sites()`（同文件 `:264-266`）：

```python
elif (isinstance(f, ast.Attribute) and f.attr == fn.name
      and isinstance(f.value, ast.Name) and f.value.id == stem and p != path):
      #                                        ↑ 要求基名**字面等于 stem**
```

⇒ `import sw_a as x` 后 `x._d(...)` 的基名是 `x` ⇒ **不匹配**；`_import_map` 里
明明有 `x → sw_a` 这条映射，**却没人用它**。

### ★★★ 先量：这条盲区到底有多大（真树实测 · 2026-10-09）

一次性探针 `output/_probe232_alias.py` / `output/_probe232_blindspots.py` 量了
**5 种**「解析器看不见」的形态：

| 形态 | 例 | 真树调用点数 |
|---|---|---|
| a 模块别名 | `import sw_part as P` 后 `P._safe_com_member(...)` | **0** |
| b 名字别名 | `from sw_part import _safe_com_member as f` 后 `f(...)` | **0** |
| c 点式基名 | `pkg.sw_part._safe_com_member(...)`（`f.value` 是 Attribute） | **0** |
| d 同文件自限定 | `sw_part._safe_com_member(...)` 写在 `sw_part.py` 自己里（`_entry_sites` 要求 `p != path`） | **0** |
| e `getattr` 动态 | `getattr(mod, "_safe_com_member")(...)` | **0** |
| —— 对照：现有三种口径**已覆盖**的调用点 | | **362** |

原始 AST 普查（193 个 `scripts/**/*.py`）交叉验证：`import X as Y` **94** 处、
`from X import Y as Z` **76** 处 —— 别名**确实大量存在**，但**没有一处**的别名指向
37 个分发口的名字或其所在模块（`别名目标命中某个分发口名/模块 = 0`）。

### ⇒ 结论与切片的定形

**真树今天 0 处 ⇒ 直接「扩解析器支持别名」是一个没有靶子的改动**：
写完了也永远跑不到，等于「一个存在但没人用的守卫与没有守卫等价」（事实 40 同族）。

但**盲区本身是真的**（形态 a 确实看不见，代码为证）。⇒ 本切片**不扩解析器**，
而是把这条边界**封死**：

> **5 种盲区形态任一非 0 ⇒ 门禁红**（tripwire）。
> 语义：一旦有人写出别名调用，门禁**不会静默漏点**，而是当场红，
> 逼下一轮**先把解析器扩到能认它**，再放行。

这与本仓既有形态同源：**「未表态即红」（spec 224/229）** → 这里是**「有盲区即红」**。

## 二、需求

### FR-001 五种盲区形态逐形态普查（门禁主体）
对 37 个分发口的每一个，在全部 `scripts/**/*.py` 里统计 5 种**解析器看不见**的
调用形态的出现次数，逐形态打印。

- **来源**：本仓 `scripts/check_dispatch_entry_guard.py`（`_entry_sites()` 的三种形态为
  「已覆盖」口径）；形态清单由本轮真树量测得出（`output/_probe232_blindspots.py`）。
- **license**：本仓库 MIT。无第三方代码引入。
- **口径纪律**：取点/entries/已覆盖口径**全部 import，不重写** ——
  `check_dispatch_entry_guard.{iter_sources, scan, _entry_sites, _import_map, ROOT}`。

### FR-002 任一形态非 0 即红
`a + b + c + d + e > 0` ⇒ `[blindspot]` `[FAIL]`（exit 1），并逐条打印命中位置。

- **来源**：本仓纪律「**盲区必须被枚举且不会被悄悄扩大**」（spec 229 的 `exempt *` 语义）；
  与 spec 230 教训「**解析不出必须显式判出来，不能静默降级**」同族。
- **理由**：静默漏点产出的读数**看起来像结论**（「可解析 362」），会把人骗到错的方向。
- **license**：本仓 MIT。

### FR-003 已覆盖口径的对照读数 + 零检查守卫
必须打印「现有三种口径已覆盖的调用点总数」（真树 **362**）作为对照；
且该数 **== 0** ⇒ `[zero-checked]` `[FAIL]`（事实 46：`检查过 0 个` 不许 PASS）。

- **来源**：本仓既有纪律（`audit_byref_args.py` 的「≥300」同源）。
- **license**：本仓 MIT。

### FR-004 只增不减（下界冻结）
「已覆盖调用点总数」**只允许增**；减少 ⇒ `[baseline-shrunk]` `[FAIL]`。

- **来源**：spec 229/230/231 立的同族纪律。
- **理由**：减少 = **取点漏了**，**不是**「问题解决了」。
- **license**：本仓 MIT。

### FR-005 合成树可跑（负例能在临时树上端到端红）
扫描根可被 `DSH_DISPATCH_BLINDSPOT_ROOT` 覆盖 ⇒ 负例能在**仓库外**的合成树上跑。

- **来源**：spec 225/228/231 的既有做法（`DSH_ENUM_GATE_ROOT` / `DSH_DISPATCH_ROOT` / `DSH_DISPATCH_BYREF_ROOT`）。
- **license**：本仓 MIT。

## 三、非目标（明确不做）

| 不做 | 理由 |
|---|---|
| **扩 `_entry_sites()` 去认别名** | ★★ 真树 **0 处** ⇒ 写了永远跑不到（「没有靶子的守卫」）。**本切片只封边界，不扩解析器**；扩解析器的触发条件是**本门禁变红** |
| 给 16 条 arity 不符**定罪** | 需**真机裁决** —— **需业主另行授权 COM**（spec 231 同款） |
| 局部变量 / 计算式两个桶（52 + 2） | spec 229 已登记；需先量「能还原成字面量的有多少」 |
| `partial` / `unresolved` / `no-callers` 入口的**非字面量**调用点 | 那不是静态可判的 |
| 覆盖 `dumps/` 之外的**非 `scripts/` 目录** | 分发口只定义在 `scripts/**`（口径继承 229/230/231） |

## 四、验收

见 `acceptance.md`（判据读数 + 红基线 + 未过门）。
