# plan 232 —— 分发口调用点的盲区形态普查 + 非 0 即红

> 性质：**纯离线静态门禁**。三源里只用**第一源**（本仓 AST）+ 本仓登记表。
> 不碰 COM / 反射转储 / CHM。

## 一、三源与冲突裁决顺序

| 序 | 源 | 本切片用到的部分 | 冲突时 |
|---|---|---|---|
| ① | **本仓源码（AST）** | `scripts/**/*.py` 全部 193 个文件；`check_dispatch_entry_guard.scan()` 产出的 37 个分发口 | **唯一事实源** |
| ② | `C:/swapi` 官方页 | 不使用 | — |
| ③ | CHM 解包 | 不使用 | — |
| ④ | `_raw` 反射转储 | 不使用（⇒ 无 `[SKIP]` 路径） | — |

★ 本切片**不涉及** by-ref / arity 语义 ⇒ **不触发**「官方 Remarks 与官方示例冲突」
（`docs/recon-206/pre-code-conflict-lookup.md`）的任何条目。

## 二、口径来源（**全部 import，不重写**）

```python
import check_dispatch_entry_guard as G
entries, visible, nonliteral, _b, _df, _cf, files = G.scan(root=...)   # 取点
imap = G._import_map(files)                                            # 现有别名表
covered = sum(len(G._entry_sites(e, files, imap)) for e in entries)     # 已覆盖口径
```

★ 「已覆盖」只有**一处**定义（`_entry_sites`）——本门禁**不重新实现**三种形态，
只**补量**它没覆盖的 5 种。否则两边会各自漂移。

## 三、5 种盲区形态的判定规则（**必须精确**，否则假阳性）

设当前分发口 = `(path, fn)`，`stem = path.stem`，扫描文件 `p`。

| 形态 | 判定 | 为什么它**真的是**对该分发口的调用 |
|---|---|---|
| a 模块别名 | `f = Attribute(attr=fn.name, value=Name(id=base))`，`p != path`，`base != stem`，且 `mod_alias[p][base] == stem` | `base` 确是该模块的别名 ⇒ `base.fn.name(...)` 就是调该 `def` |
| b 名字别名 | `f = Name(id=alias)`，`p != path`，`alias != fn.name`，且 `name_alias[p][alias] == (stem, fn.name)` | `alias` 确是该 `def` 的别名 |
| c 点式基名 | `f = Attribute(attr=fn.name, value=Attribute)` | `a.b.fn.name(...)`；`f.value` 不是 `Name` ⇒ 现有形态 ③ 漏掉 |
| d 同文件自限定 | `f = Attribute(attr=fn.name, value=Name(id=stem))`，且 `p == path` | 现有形态 ③ 硬要求 `p != path` ⇒ 漏掉 |
| e `getattr` 动态 | `f = Call(func=Name(id="getattr"), args[1] == Constant(fn.name))`，且 `args[0]` 是 `Name` ∈ `{stem} ∪ {该 stem 的模块别名}` | ★ 收紧到「目标确是该模块」—— 否则 `_checked` 这种**9 个模块重名**的入口会大量假阳性（spec 229 的教训） |

★ **e 的收紧是必须的**：`_checked` / `_num` / `_read` 在多个模块重名，
松判定会把无关对象的 `getattr(obj, "_checked")` 全算进来。

## 四、门禁结构

```
scripts/check_dispatch_blindspot_guard.py
  ROOT      = Path(env DSH_DISPATCH_BLINDSPOT_ROOT or 仓库根)
  BASELINE_COVERED = 362                       # 只增不减
  blindspot_sites(entries, files) -> (counts, samples)
  main() -> 0/1
```

输出（真树预期）：

```
== 分发口调用点的解析盲区普查（5 种形态，任一非 0 即红）==
扫描 `…/scripts/**/*.py` · 分发口 37 个 · 已覆盖调用点 362
  (a) 模块别名   import m as x 后 x.f()          = 0
  (b) 名字别名   from m import f as g 后 g()     = 0
  (c) 点式基名   pkg.m.f()                      = 0
  (d) 同文件自限定 m.f() 写在 m.py 里             = 0
  (e) getattr 动态 getattr(m, "f")()            = 0
[PASS]
分发口盲区 · 已覆盖 362 · a 0 · b 0 · c 0 · d 0 · e 0 · 违规 0 · [PASS] · exit 0
```

## 五、假绿守卫

| 守卫 | 判据 |
|---|---|
| 零检查 | `entries == 0` 或 `covered == 0` ⇒ `[zero-checked]` `[FAIL]`（事实 46）|
| 下界 | `covered < 362` ⇒ `[baseline-shrunk]` `[FAIL]` |
| 合成树例外 | 下界只在**真树口径**生效；合成树用 `DSH_DISPATCH_BLINDSPOT_BASELINE_MIN` 覆盖为 0 |

## 六、测试策略（★ 先证能红）

`tests/test_dispatch_blindspot_guard.py`：

1. **真树读数**：`exit 0` · `已覆盖 362` · `a/b/c/d/e 全 0` · `[PASS]`。
2. **每种形态各一个合成树负例**（a/b/c/d/e **各 1 例**）⇒ `exit 1` · `[blindspot]` ·
   该形态计数 `= 1`。★ 这是「5 种形态都承重」的证据，不是只证一种。
3. **绿例**：合成树里只有现有三种形态 ⇒ `exit 0`（证明门禁**不是**「一律红」）。
4. **下界承重**：真树 + `BASELINE_MIN=363` ⇒ `exit 1` · `baseline-shrunk`。
5. **零检查守卫**：合成树 + `BASELINE_MIN=1` 而 `covered=0` ⇒ `exit 1` · `zero-checked`。

★ 合成树夹具**只含被测对象**（不放任何旧口径形态以外的调用），
否则判据会「**因错误的原因**」通过（spec 226 教训）。
★ 合成树建在**仓库外**（`tempfile.mkdtemp`）—— 本仓多条判据以「`tmp_path` 在仓库外」
为隐含前提（spec 223 教训）。

## 七、接线

- `scripts/release_check.py`：新增 `_run_dispatch_blindspot_guard_gate()` + 聚合 + 结果字典。
  ★ 插函数时**务必复核相邻函数的 `# ── 来源 ──` 头**（spec 231 第二次踩到）。
- `docs/gate-classification.json`：登记 `check_dispatch_blindspot_guard.py`（`kind: hard`）。
  ⇒ `classification` **42 → 43**；`release_check` 的 `gates` **41 → 42**（两套口径**都** +1）。

## 八、风险

| 风险 | 处置 |
|---|---|
| 形态 e 假阳性（重名入口） | 已收紧到「目标确是该模块」；真树实测 0 |
| 合成树夹具含旧形态 ⇒ 判据因错误原因通过 | 夹具**只含被测形态**；绿例单独覆盖旧形态 |
| `_entry_sites` 是私有函数，被 import 使用 | 本仓既有做法（231 已这么做）；只在 `scripts/` 内部耦合，可接受 |
| 真树 0 处 ⇒ 门禁「看起来没用」 | ★ 它守的是**边界**不是**实例**：非 0 即红 ⇒ 任何人引入别名调用都会被拦住 |
