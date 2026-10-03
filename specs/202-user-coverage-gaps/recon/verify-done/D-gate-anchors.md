# D · GATE-FINAL 的 12 条判据 · 仓内锚点对账

> **对象**：`specs/202-user-coverage-gaps/recon/gate-cand/GATE-FINAL.md` §三 的 **C1–C12 + 分流 R**。
> **核什么**：每条判据**引用的仓内东西**是否真的存在、引用得对不对（不是核判据设计得好不好）。
> **纪律**：只读核验（未跑 SolidWorks、未跑 pytest、未改仓内任何文件）；只写本文件；
> 每条结论给出**可搜索的原文位置 = 文件 + 片段**（★ 不写行号）；★ 查不到就说查不到（铁律 5）。
> ★ 路径说明：GATE-FINAL 里的 `recon/...` 全部相对 `specs/202-user-coverage-gaps/`；本报告一律写全相对路径。

---

## 〇 · 判定口径（★ 先写死，否则"成立几条"没有唯一定义）

- **成立** = 该判据引用的仓内锚点**全部存在**，且**引用的原文片段逐字对得上**（不因数字小出入降级，但要在"附注"里点名）。
- **存疑** = 锚点主体在，但判据**自己声明的仓内来源**有一半对不上（那条声明本身不成立）。
- **不成立** = 判据的**唯一判据所依赖的仓内对象根本不存在** ⇒ 这条闸现在无法执行。

---

## 一 · 逐条对账表

| 判据 | 它引的仓内锚点 | 在不在 | 判定 | 依据原文（可搜索片段） |
|---|---|---|---|---|
| **C1** 输入契约 | `recon/scan-S4-obsolete-usage.md`：散文+表、`:36`「46」、`:57`「不可单独采信」却填了判定 | ✅ | **成立** | 全文是 markdown 表、零可解析字段；表尾有「★ 其中与其它接口重名、判定受歧义影响的行 \| 46」；行内逐字「★ 该名字在本仓 >20 命中，其中多为同名局部符号 / 属性，★ 本行判定不可单独采信」而同行判定列写「**用了后继**」⇒ ★ 自认不可采信却仍填判定，成立 |
| **C2** 数 | ① `recon/preselect-family-merged.md`「30 条」② 事实 510「估 30、实测 52」③ 事实 346「该挂 36 → 32，它一直在虚报」 | ✅ | **成立** | ①「★ 这条门禁一次就会抓住本表 **30 条**」；② 事实 510 内逐字「★★ 而"判据的作者估了几条"**不能替代实测**（★ 本例估 30、实测 52…）」与「★★ **按原判据会被报：52 条**（★ 不是它估的 30）」；③ 事实 346 标题逐字「**分诊修正：该挂 36 → 32**（★ 它一直在**虚报**）」 |
| **C3** 覆盖面 | ① `output/obsolete-usage-in-repo.json` 的键集 ② 事实 506（读了不存在的字段 `type`）③ `tools/scan_param_kind_consistency.py` docstring | ✅ | **成立**（附注：仓内零正例，见 §二·问1） | ① 该 JSON 顶层键**逐字只有** `at` / `official_obsolete_members` / `scanned_files` / `hit_rows` / `hit_occurrences` / `rows` ⇒ 无任何假阳性抽样字段；② 事实 506 标题「一个读了**不存在字段**的判据会安静地永远绿」；③ 其 docstring 首行逐字「用**正确的字段名 `kind`**（不是 `type`）重做判据」＋「★★ 打印"0 处矛盾"而其实一个都没比」 |
| **C4** 名字可判定性 | ① `recon/official-members-index.json` ② 1163 安全 / 292 歧义 ③ 事实 1 说 `FeatureCut4` 是正解 ④ 事实 511「最常用的名字恰好都在歧义名单里」 | ✅ | **成立**（附注 2 处数字，见 §二·问2） | ① 文件在，头部逐字 `"interfaces": 566` / `"unique_member_names": 8239`；② 事实 511 内逐字「★ 官方页 12123 篇 · 接口 566 个 · 唯一成员名 8239 个」「★ **在所有接口上都废弃**的名字 **1163** 个」「★★ **有歧义的**…**292** 个」；③ 事实 1 首行逐字「切除的正确入口是 `IFeatureManager.FeatureCut4`」；④ 事实 511 逐字「★ `Name` / `Select` / `GetType` 这些**最常用的名字恰好都在歧义名单里**」 |
| **C5** 判据形态 | ① 事实 507「3 个违规恰恰是写得最规范的三个」② `_pre_edge_flange` 是薄包装 ③ scan-S4 的 46 行 | ✅ | **成立** | ① 事实 507 内逐字「★ **3 个违规恰恰是写得最规范的三个**」，同条列出 `_pre_draft` · `_pre_edge_flange` · `_pre_gusset`；② 同条逐字「例如 `_pre_edge_flange(params)` 的**全部函数体**就是 `_select(params, "EDGE")`，★ 而**回读发生在被调用的 `_select` 里**」；③ scan-S4 表尾逐字「★ **没做接收者类型判定**：46 行成员名跨接口重名…已在表内逐行标 ★」 |
| **C6** 回读 | ① `docs/judge-registry.json` 的 `usable_on` / `unusable_on` 两栏 ② 事实 508「111 个工具」③ 事实 504「必须用特征树增量当判据」④ `tools/scan_obsolete_usage.py` docstring 自称「★ 只读」 | ⚠️ 半对 | **存疑** | ①②③④ 全部逐字命中（事实 508「静态扫（`tools/scan_nondict_returns.py`）报 **111 个工具**的返回里有**裸 return**」；事实 504「★ **"返回值是 `None` 且不抛异常"这一类静默失败，必须用"特征树增量"当判据**」；该判据脚本 docstring 末段逐字「★ **只读**；★ 产出 `output/obsolete-usage-in-repo.json`」）。★ **但判据的「机器形态」自称"取值必须来自本仓已登记的回读判据"** —— 枚举里的 **`tree_delta` / `unique_name` / `file_sha256` 这三个 token 在全仓只出现在 GATE-FINAL.md 自己**；`docs/judge-registry.json` 的 4 条 `id` 只有 `loads_count_plus_one` / `count_property_on_a_fresh_study` / `loads_count_plus_one_first_load` / `load_objects_by_index` ⇒ **3/5 取值在登记表里没有出处** |
| **C7** 已实现 | 四个已落地判据的 docstring：`tools/scan_preselect_requiring_tools.py` · `tools/census_pre_calls.py` · `tools/scan_param_kind_consistency.py` · `tools/check_tool_param_binding.py` | ✅ | **成立** | 四个文件都在；docstring 逐字对得上：① scan_preselect「★ 精确扫「**前置**依赖调用方选区」的工具族（★ 比 bunny 的"读到选区"精确）」（事实 510 的修正版，且打印「无 pre_call 且读到选区的工具：%d 条」）；② census_pre_calls 首行「★ 普查 2.0：**跟调用图**再判 pre_call 有没有回读（★ 上一版只看一个函数的文本 ⇒ 假阳性 3 个）」＋ 函数签名 `gather(pc, depth: int = 3)`（= 事实 507 记的「v2，递归收集本模块被调函数，**深 3 层**」）；③ scan_param_kind_consistency「用**正确的字段名 `kind`**（不是 `type`）」；④ check_tool_param_binding 来源块逐字「ToolSpec 声明了 `wall_ratio`，★ 而能力层形参是 `wall_thickness_ratio`」 |
| **C8** 台账分叉 | ★ **`docs/refuted-patterns.json`** ＋ 事实 503/509 的锚点 ＋ `scripts/sw_surface_features.py` 那两处注释 ＋ `release_check.py` 的 `_run_judge_preflight_gate` ＋ `scripts/check_gate_wiring.py` 五层 ＋ `docs/gate-classification.json` | ❌ **判据对象不存在** | **不成立** | ★ **全仓 grep `refuted-patterns` 只有 3 处命中，全是散文**（GATE-FINAL 自己 + `gate-cand/gate-cand-C-loop.md`「我照这个同型做法，把闸 B 的清单抽成 **`docs/refuted-patterns.json`**」）⇒ **该文件在仓里不存在**，`docs/` 下只有 `judge-registry.json` 与 `gate-classification.json` ⇒ ★ C8 的「唯一判据」当前**没有可读对象**。★ 其余锚点全部命中：事实 503/505–511 编号全在表里；`scripts/sw_surface_features.py` 两处注释仍写「★★ **为什么**（★ 真机隔离出来的，事实 503）：注册器调工具的**顺序**是…而 **`RESOLVERS["model"]` 经 `connect_solidworks()` 会清空选区**」与「★★ 声明式选区拿不到（★ 事实 503）⇒ **回退到自动路**」⇒ ★ 负例是真的；事实 509 逐字「★ **必须把 503 的机制断言改掉**」＋「✅ **理由（改后的）**：★ **工具层没有"调用方预选"这条通路**」＋「**16 组** ⇒ ★★ **0/16 掉**」「**6 次**…⇒ ★ **6/6 全部 `1 → 1`，一次没掉**」；`scripts/release_check.py` 有 `def _run_judge_preflight_gate()`；`scripts/check_gate_wiring.py` 的 `gates = sorted(... glob("check_*.py"))` 只扫 `scripts/` ✓、`CLASSIFICATION = ROOT / "docs" / "gate-classification.json"` ✓、末尾打印「汇总完整性（每个 `_run_*` 的结果都要进 `_gate_results`）」✓ |
| **C9** 重复 | 事实表标记 25 条 ∪ 种子 8 条 = 30 · 交集 3 · 标记独有 22 · 种子独有 5 · 事实 511 的 `FeatureCut4`/`Name`/`scan_obsolete_usage` · 事实 509 的 `RESOLVERS` | ✅ | **成立**（★ 本仓唯一一条我能把数**逐个复算**的） | 只读复算 `docs/known-facts.md`（脚本见 §三）得：**rows 509 · max 511 · marked 25 · union 30 · inter {505,509,511} · seedonly {502,504,506,507,510} · markedonly 22**，且 41 / 49 确实落在标记集内 ⇒ 与判据里那两串清单（22 条与 5 条）**逐个吻合**。标识符侧亦成立：事实 511 逐字「`FeatureCut4` \| 2 \| 1 \| ★ **假阳性**」＋痕迹行「`tools/scan_obsolete_usage.py`（★ **误报版，留着当反例**）」；事实 509 标题逐字「纠正事实 503 的**机制**：`RESOLVERS["model"]` **不会**清空选区」 |
| **C10** 静态不可判 | 事实 156「按 mark 分配 ⇒ 静态判不了，如实记」＋「同条还记了仓里已经把这件事写成一条测试」 | ✅ | **成立** | 事实 156 正文逐字：「句3「按 mark 分配」 ⇒ ★★ **静态判不了，如实记** —— 那是**运行行为**（多引用特征读 mark 0/1/2、不读选择顺序），静态检查做不到；它的证据**只能来自真机**」；同条另有「★★★ 而本轮最值钱的一条：**我被一条既有测试拦住**，撤掉了我自己多加的判据」⇒ ★「已写成一条测试」这句也成立 |
| **C11** 负例存在性 | `tools/classify_audit_divergences.py`（有序关键词表 + `break` · `split("|")` · `what+theirs`）＋ `patterns-shard-1.md` 的 `:49-53` ＋ `patterns-shard-3.md`「14/27 不一致」 | ✅ | **成立**（附注 1 处计数，见 §二·问3） | 源码逐字：`PATTERNS = [` 起、十条目、`break` 命中即停；`cells = [c.strip() for c in line.strip().strip("|").split("|")]`；`blob = r["what"] + " " + r["theirs"]`。`patterns-shard-1.md` 逐字「`tools/classify_audit_divergences.py` 的 `PATTERNS` 是一个**有序关键词表 + `break` 命中即停**，且搜索对象是 `what + theirs`（**含官方原文**）。三点后果…」；`patterns-shard-3.md` 逐字「我**用它自己的 `PATTERNS` 表跑了一遍**我这片 27 行，结果与我的判断 **14/27 不一致**，其中 **4 条直接落进「（未能归类）」**」。★「无门禁引用、无测试」成立：全仓 grep 该脚本名，**`tests/` 与 `scripts/` 里 0 命中** |
| **C12** 证据不可变 | `tools/scan_obsolete_usage.py` 自称「★ 只读」＋ `output/obsolete-usage-in-repo.json` 的 `at`/文件数/行数/次数 | ✅ | **成立** | 产物当前读数**逐字**为 `"at": "2026-10-03 23:42:25"` · `"scanned_files": 646` · `"hit_rows": 677` · `"hit_occurrences": 876` ⇒ 与判据写的"被重写为"那组值**完全一致**；脚本 docstring 同时写着「★ 只读；★ 产出 `output/obsolete-usage-in-repo.json`」⇒ ★ 自称只读却写共享证据，矛盾为真。改前那组值（`23:29:01` · 644 · 671 · 870）**本轮无法再核**（文件已被覆盖），但事实 511 里逐字「它报出 **870 处**」与"改前 870"一致 ⇒ ★ 只核到改后一侧（铁律 5） |
| **R** 分流 | `recon/preselect-family-merged.md` 的 7 档口径表 ＋ `patterns-shard-2.md`「不能一类一修…11 条（33%）」 | ✅ | **成立** | 分档表逐字 7 档：**安全 / 真危险·官方前置 / 真危险·显式拒 / 真危险·诊断型 / 真危险·条件 / 真危险·软失败 / 无关**（表头逐字「### 分档口径（本轮统一，三路原本不一致）」）；`patterns-shard-2.md` 逐字「★★ **不能一类一修。** 全 33 条里只有 **11 条（33%）** 真正「一类一修」得动」，其小计表写「**33.3%**」 |

---

## 二 · 三个被点名要"逐个看"的问（★ 用户指定）

### 问1 · C3 说"判据必须自报覆盖面" ⇒ ★ **仓内哪些门禁真的自报了？**

逐个看了 `scripts/check_*.py` 与 `tools/check_*.py` 的打印。**自报了"比了几个"的只有 6 个**：

| 门禁 | 打印原文（可搜索片段） | 自报的是 |
|---|---|---|
| `scripts/check_python_syntax.py` | 「.py 语法门禁 · 扫 **%d** 个文件 · 失败 **%d** 处」 | 文件数 |
| `scripts/check_report_criteria_alignment.py` | 「[PASS] 扫了 **%d** 张自评表」 | 表数 |
| `tools/check_com_write_form.py` | 「扫了 %d 个 .py」 | 文件数 |
| `tools/check_same_parser.py` | 「扫了 **%d** 个 .py（★ 先报数量 —— 事实 357）」 | 文件数 |
| `tools/check_tool_param_binding.py` | 「核对参数个数：%d（★ **这就是覆盖面** —— 判据必须自报它比了几个）」 | 核对条数 |
| `scripts/check_negative_input_selfproof.py` | 「⚠ **覆盖面声明**：本审计只判「**变换没生效**」这一类（类型 1）」 | 只报**范围**、**不报数** |

⇒ ★ **C3 要求的第二键 `fp_sampled >= 1`（抽过假阳性），仓内 0 个门禁在打印**。
最接近的是 `tools/check_tool_capability_coverage.py` 的「★ 它只回答「有没有人认领」这个事实问题 ⇒ ★ **假阳性为零**」—— 那是**一句断言**，样本数仍是 0。
⇒ ★ **判据成立，但它的 `E4_NO_FP_SAMPLE` 在本仓有 0 个正例**（谁都得不了分）。

### 问2 · C4 的机器形态那两个数

- 文件在：**1.54 MB**（判据写「1.6 MB」—— 量级对，精确值对不上）；头部 `"interfaces": 566` ✓ `"unique_member_names": 8239` ✓（与判据"含 `_overview` 一项"的说法一致）。
- 判据写「**11557** 成员槽」，但它**自己 §六 给的复算命令**跑出来是 **12123**（`sum(len(v) for v in per_interface.values())`）；**12123 − 566 个 `_overview` 伪成员 = 11557** ⇒ ★ 这个数**能推出来**，但**没有一条命令直接产出它**，与事实 511 里「官方页 **12123** 篇」也是两个口径。
⇒ ★ 不降级，但写明：**11557 与 12123 在仓内同时成立，取决于是否把每接口的 `_overview` 算成成员槽。**

### 问3 · C11 说"判据脚本必须被一条测试命中" ⇒ ★ **去 `tests/` 核的结果**

- 判据的机器形态是「`grep tests/ -r '<脚本名>'`」。
- ★ 我把这批**判据脚本**逐个在 `tests/` 下 grep：**`scan_obsolete_usage` · `census_pre_calls` · `scan_param_kind_consistency` · `check_tool_param_binding` · `scan_preselect_requiring_tools` · `classify_audit_divergences` ⇒ 全部 0 命中**；连它们的产物 `obsolete-usage-in-repo.json` / `official-members-index.json` 在 `tests/` 里也 0 命中。
- ⇒ ★ **按 C11 现在的写法，仓内这 6 台判据脚本一台都过不了（E14）**；`tests/` 里真正有覆盖的是 `check_gate_wiring`（`tests/test_gate_negative_cases.py`）与 `tools/check_judge_preflight.py` + `judge-registry.json`（`tests/test_judge_preflight_gate.py`）—— ★ **也就是说 C11 有一条正例，但正例的门禁不在 `tools/` 那批里**。
- 附注：C11 负例段写「★ 全仓提及只有 **3** 处 markdown 叙述」⇒ **对不上**：实际全仓 16 处、分布在 **5** 个文件，除三份 shard/候选稿外还有 `recon/PROMPT-B-batch-generator.md` 两处，其中一处逐字写着「（分类器：`tools/classify_audit_divergences.py`，★ **你可以直接跑它**）」⇒ ★ 「无门禁引用、无测试」这个**结论**不受影响（`tests/` 与 `scripts/` 确实 0 命中），但那个「3 处」不是实数。

---

## 三 · 复算命令（★ 只读，不跑 SolidWorks / pytest）

```powershell
# C9 的 25 / 8 / 30 / 3 / 5 / 22（★ 判据 §六 的同一条命令，我原样跑过，输出见表格）
python -c "import io,re;t=io.open(r'D:\AI\SW\docs\known-facts.md',encoding='utf-8',errors='replace').read();p=re.split(r'^\|\s*(\d+)\s*\|',t,flags=re.M);b={int(a):x for a,x in zip(p[1::2],p[2::2])};m={i for i,x in b.items() if any(k in x for k in ('已证伪','已排除','自证伪','纠正'))};s={502,504,505,506,507,509,510,511};print('rows',len(b),'max',max(b),'marked',len(m),'union',len(m|s),'inter',sorted(m&s),'seedonly',sorted(s-m),'markedonly',len(m-s))"

# C3 的键集（★ 只有 6 个键，无任何假阳性抽样字段）
python -c "import json,io;print(list(json.load(io.open(r'D:\AI\SW\output\obsolete-usage-in-repo.json',encoding='utf-8')).keys()))"

# C12 的当前读数（★ 与判据写的"改写后"那组值逐字一致）
python -c "import json,io;d=json.load(io.open(r'D:\AI\SW\output\obsolete-usage-in-repo.json',encoding='utf-8'));print(d['at'],d['scanned_files'],d['hit_rows'],d['hit_occurrences'])"

# C4 的槽数（★ 12123，不是判据写的 11557；差值 566 = 每接口一个 _overview）
python -c "import json,io;d=json.load(io.open(r'D:\AI\SW\specs\202-user-coverage-gaps\recon\official-members-index.json',encoding='utf-8'));print('ifaces',len(d['per_interface']),'slots',sum(len(v) for v in d['per_interface'].values()))"

# C8 的判据对象（★ 无输出 = 不存在）
python -c "import pathlib;print(pathlib.Path(r'D:\AI\SW\docs\refuted-patterns.json').exists())"
```

---

## 四 · ★ 结论：**12 条里成立几条**

> ### **10 条成立 · 1 条存疑（C6）· 1 条不成立（C8）**　　（分流 **R** 另计：成立）

| 判定 | 判据 | 一句话 |
|---|---|---|
| **不成立（1）** | **C8** | ★ 它自称「★★ **唯一常驻硬门禁**」，判据的唯一依据 `docs/refuted-patterns.json` **在仓里不存在**（全仓只有 3 处散文提及它）⇒ ★ 这条闸今天**没有可读对象**、**跑不起来**；它其余锚点（事实 503/509、`sw_surface_features.py` 那两处旧注释、`_run_judge_preflight_gate`、接线五层）**全都命中** ⇒ ★ 缺的就是那份台账 |
| **存疑（1）** | **C6** | 四个负例锚点逐字全中；但判据自称「取值必须来自**本仓已登记的回读判据**（`docs/judge-registry.json`）」—— ★ 枚举里 **`tree_delta` / `unique_name` / `file_sha256` 三个 token 全仓只出现在 GATE-FINAL.md 自己**，登记表 4 条 `id` 里只有 `*count_plus_one*` ⇒ ★ **3/5 的取值没有仓内出处** |
| **成立（10）** | C1 · C2 · C3 · C4 · C5 · C7 · C9 · C10 · C11 · C12 | 引用的文件全部在仓内，且**引用的原文片段逐字对得上**（C4 附 2 处数字口径、C11 附 1 处计数，均已在 §二 点名） |

### ★ 三条最该知道的

1. ★ **C8 是这 12 条里唯一的"唯一常驻硬门禁"，而它是 12 条里唯一跑不起来的** —— 差一份 `docs/refuted-patterns.json`。
2. ★ **C9 的数字是全套里唯一我能逐个复算且全中的**（25 / 8 / 30 / 3 / 5 / 22 + 22 条清单逐个吻合）⇒ ★ 按事实 510「估出来的数不算数」，**这一条过**。
3. ★ **C3 的两个键，仓内一个正例都没有**：6 个门禁自报了"比了几个"，**0 个**自报了"抽了几条假阳性" ⇒ ★ 按 C3 现写法，**本仓没有一台判据能拿到 E3/E4 之外的分**。

### ★ 查不到的（如实记，按铁律 5）

- `docs/refuted-patterns.json` 的**内容形态**（若它将来要建）：查不到，GATE-FINAL 与候选稿 C 都只给了字段名 `anchor_quote`，**没有给样本**。
- C12 的**改前**读数（`23:29:01` / 644 / 671 / 870）：查不到（产物已被覆盖，本轮只核到改后一侧）。
- C11 那 3 台"仓外判据脚本"是否**曾经**有过测试：查不到（无 git 历史检索，本轮只核"现在没有"）。