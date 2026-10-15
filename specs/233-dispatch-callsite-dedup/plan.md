# plan 233 —— 去重口径修正（施工计划）

> 上游规格：`specs/233-dispatch-callsite-dedup/spec.md`
> 性质：**纯离线静态口径修正**。不碰 COM / 真机。

## 一、三源与冲突裁决顺序

| 源 | 位置 | 本切片用它的什么 |
|---|---|---|
| **本仓代码（真源）** | `scripts/check_dispatch_entry_guard.py::scan()` | ★ **唯一口径来源** —— 取点、`_params`、`wrapper_names()` 全部**复用**，**不重写** |
| 官方转储 `_raw/**/iface_*.txt` | 工作区（`gitignore` 外） | 本切片**不用**（去重是纯 AST 问题，与官方签名无关） |
| `C:/swapi` · CHM 解包 | 工作区外 | 本切片**不用**（同上） |

**冲突裁决顺序**：本切片无跨源冲突（只有一处口径缺陷，真源唯一）。
⇒ 不存在「按哪个源」的问题；判据是**内部自洽**（`sum(buckets) == nonliteral`）。

## 二、改动清单

| 文件 | 动作 | 说明 |
|---|---|---|
| `scripts/check_dispatch_entry_guard.py` | 改 | ① `scan()` 建 `innermost: {id(Call) → 最内层包围 def}`，命中非最内层即 `continue`；② 新增 `bucket_consistency()`；③ `BASELINE_INVISIBLE` 91→85 · `BASELINE_VISIBLE` 1219→1185；④ 文件头读数表按去重口径订正 |
| `tests/test_dispatch_call_site_dedup.py` | 新增 | **6 例**：真树读数 2 · 嵌套去重 1 · 嵌套形参归属 1 · **防去重过头** 1 · 断言本体承重 1 |
| `tests/test_dispatch_entry_guard.py` | 改 | 真树下界 1219→1185 · 91→85（**只改常量，判据不变**） |
| `tests/test_dispatch_resolution.py` | 改 | 基线串 `37,91,1219,…` → `37,85,1185,…`（否则会**因错误的原因**变红） |
| `docs/gate-classification.json` | 改 | 该门禁的 `reason` **追加** spec 233 订正段（`classification` 仍 **43**，不增不减） |
| `output/_probe233_*.py` | 新增 | 一次性量测探针（**不进仓库代码**） |

## 三、实现要点（★ 三条纪律的落点）

1. **去重必须按「最内层包围 `def`」归属，不能只「见过就跳过」** ——
   否则那 3 处「内层是形参转发」的调用点会被**错误地记进 `local`**（数对、分类错）。
   `ast.walk` 先外后内 ⇒ 后写者即最内层。
2. **断言本体必须自己也能红** —— 抽出 `bucket_consistency()`，
   判据直接喂**历史缺陷的那组数**（桶和 91 · 不可见 85）⇒ 必须返回非 `None`。
   ★ 若把断言写成内联 `if`，就没有能红的东西可测（「修宽判据本身必须有能红的判据」）。
3. **合成树夹具必须自带一个已表态的分发口** —— 否则 `[zero-checked]` **先红**，
   负例会**因错误的原因**通过（spec 232 当场踩到；本轮**又踩一次**，见 acceptance §五）。

## 四、执行顺序

```
① 写判据（tests/test_dispatch_call_site_dedup.py）并**确认能红**（旧口径 ⇒ 可见 2 ≠ 1）
② 改 scan() + 常量 + 断言
③ 跑新判据 ⇒ 6/6 绿
④ 订正两个受影响既有判据的常量 ⇒ 229–232 合并回归 56/56 绿
⑤ 生成器链 → release_check @3.14.7 ⇒ exit 0
⑥ 更新 ROADMAP §一 · memory · 交接单 · AUTO_RUN 报告
```

## 五、风险与回退

| 风险 | 处置 |
|---|---|
| 去重改错 ⇒ `entries` / `resolution()` 跟着变 | ★ 实测**不变**（37 / 327）；合并回归 56/56 绿为证 |
| 合成树负例因 `zero-checked` 先红（错误原因） | 夹具自带已表态分发口（本轮实测踩到过） |
| `--basetemp` 落进仓库内 | 本切片不用 pytest；临时树一律 `tempfile.mkdtemp()`（仓库外） |
