# acceptance 233 —— 分发口调用点的去重口径修正

> 收口时间：2026-10-09（主任务 `ff6c7344` 第 7 轮）· 性质：**纯离线静态口径修正**
> 未调 COM / 真机 · 未提交 · 未部署 · 未删任何文件 · 未 create/update 任何自动任务。

## 一、交付物

| 件 | 路径 | 状态 |
|---|---|---|
| 门禁 | `scripts/check_dispatch_entry_guard.py`（`scan()` 去重 + `bucket_consistency()` + 两个下界常量） | 改 |
| 判据 | `tests/test_dispatch_call_site_dedup.py` | 新增（6 例） |
| 判据 | `tests/test_dispatch_entry_guard.py` · `tests/test_dispatch_resolution.py` | 改（**只订正常量**，判据不变） |
| 登记 | `docs/gate-classification.json`（`reason` 追加订正段） | 改（`classification` 仍 **43**） |
| 量测 | `output/_probe233_{buckets,dup,binding,final,wide}.py` | 一次性探针（**不进仓库代码**） |
| 规格 | `specs/233-dispatch-callsite-dedup/{spec,plan,tasks,acceptance}.md` | 四件齐 |

## 二、判据读数

| # | 判据 | 读数 |
|---|---|---|
| 1 | 门禁本体（真树） | `可见（字面量）1185 · 不可见 85（形参转发 37 / 局部变量 46 / 计算式 2）` · `分发口 37 · 已表态 37 · 违规 0 · [PASS] · exit 0` |
| 2 | 新判据 `test_dispatch_call_site_dedup` | **Ran 6 tests · OK**（15.1 s） |
| 3 | 229+230+231+232+233 合并回归 | **Ran 56 tests · OK**（144.1 s） |
| 4 | 收尾链 `round_chain.ps1` | `release_check: 第 1 轮 OK` · `6 passed` · 合计 107.7 s |
| 5 | 门禁全套 `release_check.py` @**3.14.7** | **EXIT 0** · `"status": "pass"` · `"missing": []` · `gates 42`（**不变**，本切片未新增 `check_*.py`） |
| 6 | 登记条目 | `classification` **43**（**不变**） |
| 7 | 解析面（未受影响，回归为证） | `resolved 18 · partial 3 · unresolved 4 · no-callers 12 · 可解析调用点 327`（**一个没变**） |

## 三、★ 红基线（证明判据真的能红）

**① 去重判据承重**（把去重那一行删掉的**副本**，同一合成树夹具）：

```
=== 旧口径（去重行已删）===
exit = 0
可见 = 2 （新口径应为 1）
```

⇒ `test_nested_def_call_site_counted_once` 在旧代码上**必红**（`2 != 1`）。

**② 断言本体承重**（`bucket_consistency` 直接喂历史缺陷那组数）：

```python
bucket_consistency({"param": 37, "local": 52, "computed": 2}, 85)   # ⇒ 非 None，含「口径不自洽」「91」
bucket_consistency({"param": 37, "local": 46, "computed": 2}, 85)   # ⇒ None（否则门禁永远红）
```

**③ 防「去重去过头」**：并列两个 `def` 各一个调用点 ⇒ 必须 `可见 2`（不是 1）。

## 四、★★★ 核心事实

```
scan() 旧口径（每次 ast.walk 命中都计数）      去重口径（按调用点 + 最内层包围 def）
  合计 1310                                      合计 1270
  可见 1219                                      可见 1185      （虚增 +34）
  不可见 91                                      不可见 85      （虚增 +6）
    ├ 形参转发 37                                   ├ 形参转发 37
    ├ 局部变量 52                                   ├ 局部变量 46  （虚增 +6）
    └ 计算式 2                                      └ 计算式 2

6 处重复的两种形态：
  · 3 处**同时计进两个桶**（外层判 local、内层判 param）：
      sw_mass_property.py:360 · sw_mold.py:332 · sw_mold.py:339
  · 3 处**被计两次 local**：
      sw_simulation_loadprops.py:114/118 · sw_topology.py:440
```

★ 这组数（1219 / 91 / 52）**被写进 spec 229–232 四轮的 ROADMAP / 交接单 / memory 当事实**，
而**没有任何判据在守它** ⇒ 典型「量测口径写错会让读数整体错位而看不出错」。
★ 本切片补的正是**守着它**的判据：`sum(buckets) == nonliteral`（口径自洽）+ 去重口径的端到端负例。

## 五、★★ 本轮自己踩到的坑（第二、三次同族）

**合成树夹具又因「检查量为 0」先红**：首版三个夹具**都没有分发口**（只有包装器调用点）
⇒ `[zero-checked] 检查过的分发口 == 0` **先红** ⇒ 负例会**因错误的原因**通过。
⇒ 修法：**每个夹具自带一个已表态的分发口**（`#: dispatch-guard: exempt internal-helper` + `_covered`）。
★ 这与 spec 232 踩的是**同一条**（232 是 `covered == 0`，本轮是 `entries == 0`）——
⇒ 该条纪律应升级为：**凡合成树端到端夹具，必须先问「本门禁的『零检查』判据会不会先红？」**。

**第二次踩**：`exempt internal-helper` 要求 `def` 名以 `_` 开头 ⇒ 夹具里的 `inner` 被判 `invalid-claim`。
⇒ 夹具里的 `def` 命名要**先看自证条件**，不要事后补。

## 六、★★ 量测结论（spec 234 的输入）

`local` 桶去重后 **46** 个调用点，宽读取器（`output/_probe233_wide.py`）下：

```
可静态枚举 39 / 46   ·   仍不可枚举 7
候选值 distinct 135 · 出现总数 221
读取路径：for 字面量容器 34 · assign 字面量 2 · 模块级 dict 常量 .get() 2 · dict 字面量下标 1
仍不可枚举 7 处的形态：for 的迭代对象是**函数局部 dict 字面量**或**元组解包**（5 处）
                      变量由**调用方传入**（2 处：sw_simulation_loadprops.py:114/118 的 begin/end）
```

⇒ ★★ **「能还原成字符串字面量的有多少」的答案不是 0，而是 39/46**。
首版读取器（只认「本函数内 `X = "…"`」）读出 **0** —— **是读取器太窄**，不是不可还原。
★ 这正是本仓纪律「**解析不出 ≠ 不存在**；不能静默降级成 0」的又一次实例：
**窄读取器的 0 看起来像结论**。

## 七、未过门 / 未完成

| 项 | 状态 | 触发条件 / 下一步 |
|---|---|---|
| `local` 桶候选集门禁（39 可枚举 + 7 须表态） | **未做** | ★ 下一轮开 `specs/234-*`，量测已备齐（§六） |
| `def` 外的调用点不在扫描面内 | **只登记** | 真树实测 **0 处**（无靶子）；触发条件 = 出现第 1 处 |
| 16 条 arity 不符定罪 / `HEM_POSITIONS` 真机复核 | 未做 | **需业主另行授权 COM** |
| 真机验证 | 未做 | 本切片**纯离线** |
| 223 的 8 条 `HEAD` 即红既有失败 | 未修 | 权属未确认 |
| 提交 / 部署 / 打 tag | 未做 | 硬约束禁止 |
