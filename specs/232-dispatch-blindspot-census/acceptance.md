# acceptance 232 —— 分发口调用点的盲区形态普查 + 非 0 即红

> 收口时间：2026-10-09（主任务 `ff6c7344` 第 6 轮）· 性质：**纯离线静态门禁**
> 未调 COM / 真机 · 未提交 · 未部署 · 未删任何文件。

## 一、交付物

| 件 | 路径 | 状态 |
|---|---|---|
| 门禁 | `scripts/check_dispatch_blindspot_guard.py` | 新增 |
| 判据 | `tests/test_dispatch_blindspot_guard.py` | 新增（7 例） |
| 接线 | `scripts/release_check.py`（`_run_dispatch_blindspot_guard_gate()` + 聚合 + 结果字典） | 修改 |
| 登记 | `docs/gate-classification.json`（`kind: hard`） | 修改（42 → 43） |
| 量测 | `output/_probe232_alias.py` · `output/_probe232_blindspots.py` | 一次性探针（**不进仓库代码**） |
| 规格 | `specs/232-dispatch-blindspot-census/{spec,plan,tasks,acceptance}.md` | 四件齐 |

## 二、判据读数

| # | 判据 | 读数 |
|---|---|---|
| 1 | 门禁本体（真树） | `分发口 37 个 · 已覆盖调用点 362` · `a 0 · b 0 · c 0 · d 0 · e 0` · `违规 0` · `[PASS]` · **exit 0** |
| 2 | 新判据 | **Ran 7 tests · OK**（46.8 s） |
| 3 | 229 + 230 + 231 合并回归 | **Ran 43 tests · OK**（108.7 s） |
| 4 | `release_check` @ **3.14.7** | **EXIT 0** · `"status": "pass"` · `"missing": []` |
| 5 | 门禁数（两套口径） | `gates` **42**（41 → 42）· `classification` **43**（42 → 43）★ 都 +1 |
| 6 | 生成器链 | `门禁 39 道`（38 → 39）· 各产物重生成 OK |

## 三、★ 红基线（证明判据真的能红）

**合成树端到端负例**（形态 a；`DSH_DISPATCH_BLINDSPOT_ROOT` + `BASELINE_MIN=0`）：

```
== 分发口调用点的解析盲区普查（5 种形态，任一非 0 即红）==
扫描 `…/Temp/tmp.H1fxEPSRJu/scripts/**/*.py` · 分发口 1 个 · 已覆盖调用点 1
  (a) 模块别名     import m as x 后 x.f()         = 1
  (b) 名字别名     from m import f as g 后 g()    = 0
  (c) 点式基名     pkg.m.f()                     = 0
  (d) 同文件自限定 m.f() 写在 m.py 里                 = 0
  (e) getattr 动态 getattr(m, "f")()           = 0
[FAIL] 违规 1 处：
  [blindspot] …/scripts/other.py:5 sw_fixture::_dispatch —— 形态 (a) 有 1 处解析器看不见的调用点：…
[FAIL]
分发口盲区 · 已覆盖 1 · a 1 · b 0 · c 0 · d 0 · e 0 · 盲区合计 1 · 违规 1 · [FAIL] · exit 1
```

★ **5 种形态各自**都有负例（判据 `test_each_form_is_load_bearing` 用 `subTest` 逐形态断言
`exit 1` + `form_count == 1` + **`zero-checked` 不在输出里**）——
即证明红的原因**是盲区**，不是「检查量为 0」这种**错误的原因**。

★ 另两条承重判据：
- `test_covered_baseline_shrink_is_red`：`BASELINE_MIN=363` ⇒ `已覆盖调用点 362 < 下界 363` · **exit 1**。
- `test_zero_covered_is_red`：只有入口 `def`、没有调用点 ⇒ `[zero-checked]` · **exit 1**。
- `test_getattr_on_other_module_is_not_a_blindspot`：`getattr(other_mod, "_dispatch")()` ⇒ **exit 0**
  （形态 e 的**假阳性边界**：目标不是该模块 ⇒ 不算盲区）。

## 四、★★★ 核心事实（本切片的实质结论）

```
5 种「解析器看不见」的调用形态，真树实测全部 = 0：
  a 模块别名 0 · b 名字别名 0 · c 点式基名 0 · d 同文件自限定 0 · e getattr 动态 0
而现有三种口径已覆盖 362 个调用点。

交叉验证（原始 AST 普查，193 个 scripts/**/*.py）：
  import X as Y ........................ 94 处
  from X import Y as Z ................. 76 处
  别名目标命中某个分发口名/模块 ......... 0 处
⇒ 别名**大量存在**，但**没有一处**指向 37 个分发口的名字或其所在模块。
```

⇒ ★★ **结论：「扩 `_entry_sites()` 认别名」是一个没有靶子的改动** ——
写完永远跑不到，等于「一个存在但没人用的守卫与没有守卫等价」（事实 40 同族）。
**本切片因此不扩解析器，只把边界封死**：任一形态非 0 ⇒ 红，
逼下一轮**先扩解析器再放行**。语义与「未表态即红」（224/229）同源 —— 这里是**「有盲区即红」**。

## 五、★★ 核过的一条**错前提**（本仓纪律：交接单的前提也要核）

上一轮交接单待办 1 写：

> `check_dispatch_entry_guard._import_map` 只认 `from <stem> import <name>`，
> `as` 形式**只处理了 `ImportFrom` 的 asname、没处理 `Import` 的模块别名**。

**核对结果：这条前提有一半是错的。**
`scripts/check_dispatch_entry_guard.py:239-241` 的 `ast.Import` 分支**确实处理了** `asname`：

```python
elif isinstance(node, ast.Import):
    for al in node.names:
        m[al.asname or al.name.split(".")[-1]] = al.name.split(".")[-1]
        #   ↑ asname 被处理了
```

真正的缺口在**消费端** `_entry_sites()`（同文件 `:264-266`）—— 它要求
`f.value.id == stem`（基名**字面等于**模块名），**从不查 `_import_map`**。
⇒ ★ 若照原前提去「修 `_import_map`」，会改到**本来就对的地方**，
真正的缺口**一处没动**（与 spec 227「37 条正确的登记」同族陷阱）。

## 六、未过门 / 未完成

| 项 | 状态 | 触发条件 |
|---|---|---|
| 扩 `_entry_sites()` 认别名 | **不做** | ★★ **本门禁变红**时才做（真树 0 处 ⇒ 现在做没有靶子） |
| 16 条 arity 不符的定罪 | 未做 | **需业主另行授权 COM**（真机裁决「纯出参能否省略」） |
| `HEM_POSITIONS` 真机复核 | 未做 | **需业主另行授权 COM** |
| 局部变量 / 计算式桶（52 + 2） | 未做 | 先量「能还原成字面量的有多少」 |
| 真机验证 | 未做 | 本切片**纯离线** |
| 提交 / 部署 / 打 tag | 未做 | 硬约束禁止 |

★ 本切片**未改** `scripts/check_dispatch_entry_guard.py`（只 import 它的口径）⇒
229 / 230 / 231 三个门禁的读数**一个都没变**（合并回归 43/43 绿为证）。
