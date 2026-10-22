# 仓库统一化报告

**依据**：业主 2026-10-21 指令 ——「我要避免的是**局部很整洁，但是整体很混乱或者很精神分裂**，
比如同一个功能多个函数重复实现，或者同一个东西在不同的地方命名不一样。整个项目要统一化、规范化，
有统一的契约、统一的字段，各种各样的东西全部要统一成同一个口径，让整个项目从局部到整体全部都是
干净整洁、优雅、结构化且系统化。」并明确要求「**参考编程规范，不要自己随便想几个标准**」。

**日期**：2026-10-21 ~ 2026-10-22　**判据机器化**：`scripts/check_repo_uniformity.py`（已接进 `release_check`）

---

## 一、为什么先做「尺子」而不是先改代码

★★ 盘查发现：本仓已有 **50+ 道门禁，但每道只管一摊** —— **没有任何一道在看「全局一致性」** ⇒
局部全绿而整体可能已分裂。且本机**一个 lint 工具都没装**（ruff / flake8 / pylint / mypy 全无），
也没有 `ruff.toml` / `setup.cfg` / `mypy.ini`。

⇒ 第一步不是改代码，是**把「整体干净」量出来**（`scripts/check_repo_uniformity.py`），
并在 `docs/repo-uniformity-baseline.json` 记基线 —— ★ **基线只许降不许升**。

## 二、五条指标的权威出处（不自定义标准）

| # | 指标 | 权威出处 | 机械执行 |
|---|---|---|---|
| ① | 命名 / 导入 / 循环依赖 | [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) —— `snake_case` 模块/函数/变量 · `PascalCase` 类 · `_` 前缀内部成员 · 导入分组且分行 · 循环依赖是 code smell | **ruff 0.17.1** `--select E,F,I,N,UP` |
| ② | 重复代码（行块级） | [pyscn](https://github.com/ludo-technologies/pyscn) Type 1–4 克隆检测 | **pyscn 1.32.5** `analyze --select clones` |
| ③ | 来源块 | `AGENTS.md` §十八「新建 `.py` 的模板：docstring 一行 + 来源块紧随其后」 | 自写扫描 |
| ④ | 同名 `.py` | `AGENTS.md` 铁律 3（结构按顶层白名单）引申 | 自写扫描 |
| ⑤ | **跨文件同函数体** | 业主头号关切；判据口径 = Type-2 克隆（重命名标识符后相同），出处同 ② | 自写 AST 归一化哈希 |

★ **⑤ 是本轮新增的关键指标** —— ② 的克隆检测按**行块**判，2,501 组里绝大多数是样板
（probe 样例代码、ToolSpec 声明、来源块）；⑤ 按**函数体**判，只有 113 组，**直接对准
「同一个功能多个函数重复实现」**。判据：函数体去 docstring、把 `Name` 与形参名换成占位符后取哈希，
跨文件同哈希即同一函数的多份实现（★ 同文件同名不算，那是重载）。

## 三、本轮读数（★ 只降不升，每一步都有下调记录）

| 指标 | 起点 | 现在 | 变化 |
|---|---|---|---|
| ① ruff（E,F,I,N,UP） | 26,378 | **25,876** | **−502** ✓ |
| ② pyscn 克隆组 | 2,515 | **2,498** | −17 ✓ |
| ③ 缺来源块 | 189 | **0** | **−189** ✓ |
| ④ 同名 `.py` | 2 | **0** | −2 ✓ |
| ⑤ 跨文件同函数体组 | 125 | **113** | **−12** ✓ |

## 四、做过的事

### 4.1 建门禁并接线（★ 不接线 = 空转，事实 62）

新建 `scripts/check_repo_uniformity.py`；`_run_repo_uniformity_gate` 接进 `scripts/release_check.py`
（`_gate_results` 汇总**两处同时加** —— 元门禁 `check_gate_wiring.py` 在守）；`docs/gate-classification.json`
登记分类。★ 工具未安装时 **FAIL 而非跳过**（静默跳过与没跑等价）。

### 4.2 删掉一份重复实现（`audit_call_arity.py`）

`scripts/`（337 行 · **有来源块** · 9 符号 · 活版）vs `tools/`（149 行 · **无来源块** · 6 符号 · 停在最早入库）。
证据：tools 版独有的 `SAFE_MEMBER` 正则（只认 2 个包装名）已被 scripts 版 `WRAPPERS`（认 4 个）+ `call_sites()` 覆盖；
9 处真 import **全部**解析到 `scripts/`（`sys.path` 优先）⇒ 删除 ✓ · 删后 import 仍成功、9 个相关测试全过 ✓

★ **另一处判为「不是重复」**：`drawing_spec.py` 两份是「真源 + importlib 转发壳」——
★ 删了会在**运行期 ImportError** ✗ ⇒ 留豁免机制。

### 4.3 补 75 个文件的来源块（★ 一条都不编）

按**可核实证据**分六类，每类的「官方依据」写法不同：

| 类 | 数 | 官方依据 |
|---|---|---|
| pure | 51 | 不适用（本仓工具，不调 COM） |
| swapi | 8 | 官方源 `C:\swapi\types\**`（逐条见文件内引用） |
| manual | 8 | 逐条人工确证（见下） |
| deleg | 3 | 经由本仓 COM 封装，签名见被调模块的来源块 |
| shim | 3 | 不适用（兼容转发壳，真源见 `_IMPLEMENTATION`） |
| spec | 2 | = 各条 ToolSpec 所包装函数的来源 |

★ **「待回填」最终为 0** —— 75 条每条都有据可查。

★★ 三条分类误判在 **dry-run 阶段**被抓到（★ 没写盘就改掉了）：
1. `sw_appearance.py` / `routing_review.py` / `cad_doctor.py` 判成「不调 COM」✗ —— 它们经
   `sw_preflight.import_com_dependencies` **间接**碰 COM ⇒ 补 `COM_IMPORT` 判据 ⇒ 改判 `deleg`。
2. `map_tools_to_members.py` 判成「兼容转发壳」✗ —— 它只在**注释里**提到别处的 importlib 用法
   ⇒ 判据改为**只看非注释行**。
3. 8 条 probe/scan 落到「待回填」⇒ 人工逐条读 docstring 写成具体依据
   （它们判的是**本仓**运行时行为，不是官方签名），如 `probe_resolver_mark_matrix.py` ⇒
   「判的是本仓 `RESOLVERS` 的运行时行为（事实 503 一族），不涉官方签名」。

### 4.4 收敛 5 组同函数体（★ 生产代码里的真重复）

新建 **`scripts/sw_feature_tree.py`** = 特征树读取的**单一实现**；原来的多份实现改为导入别名：

| 函数 | 原份数 | 原位置 | 处置 |
|---|---|---|---|
| `_tree_names` | **4** | `sw_curve_and_split` · `sw_ref_geometry` · `sw_surface_edit_ops` · `sw_surface_ref_ops` | 全部改为 `from sw_feature_tree import tree_names as _tree_names` |
| `_feature_count` | **3** | `sw_cosmetic_weld_bead` · `sw_net_blend` · `sw_weld_bead` | 同上（`feature_count`） |
| `_feature_type_name` | **2** | `sw_sweep` · `sw_wrap` | 同上（`feature_type_name`） |

★ **保留的价值**：四份 `_tree_names` 里最详细的那份 docstring（轮 473 的教训：
「自己拼 `GetFeatureCount(True)` + `FeatureByPositionReverse(i)` ⇒ 真机回 `None` ⇒
5 条能力全被记成"不能"，而那是**判据坏了**、不是能力不行」）已搬进单一实现 ✓

★ **连带更新两处「只增不减」下界**（★ 合法下降，原因与替代断言都写进代码注释）：
- `check_dispatch_entry_guard.py`：`BASELINE_VISIBLE` 1174 → **1173** · `BASELINE_INVISIBLE` 85 → **84**
- `check_dispatch_arg_guard.py`：`BASELINE_SITES` 46 → **45** · `BASELINE_ENUM` 42 → **41**
- ★ 替代断言：指标 ⑤ 的基线只许降 ⇒ 这类重复**再出现就会被拦**。

### 4.5 顶层目录 40 → 39 的复核更正

原记「40 个顶层目录」，复核发现**多算一个**：把 `.pytest_cache`（工具缓存、gitignore、不入库）
当成仓库目录了 ✗。正确口径：**39 个仓库目录 + 3 个工具缓存**（`.pytest_cache` / `.codebase-memory` /
`.ruff_cache`，三者均 gitignore）。已按 `AGENTS.md` §九 停止条件 #5 更新本文件 ✓

## 五、本轮踩的坑（★ 都是我自己的，已修）

★★ **ruff 的 E501 按「显示宽度」算，CJK 字符算 2 列** ✗
- 我第一次按**字符数**折行 ⇒ 「字符数 ≤88 但显示宽度 >88」的行仍违规（按 `# 定位:` / `# 官方依据:`
  前缀用 `unicodedata.east_asian_width` 复算，见本轮 `git log` 里 `698a4453` 的中间态）⇒
  ruff 反而从 26373 **涨到** 26416（读数来自 `python scripts/check_repo_uniformity.py` 当轮输出）✗
- 改用 `unicodedata.east_asian_width` **宽度感知**切分 ⇒ 降到 25,876 ✓
- ★ **教训：给 CJK 项目做行长门禁，不能按字符数切，要按显示宽度。**

★ 其余三个：编辑 `release_check.py` 时误吞掉了 `def _run_tools_index_fresh_gate()` 那一行（运行期 `NameError`）；
删文件后没重生成 `tools-index.md`；提交时漏列被删文件（描述说删了、索引里没删，补一个提交才真正入库）。

## 六、事实 61 的四道自查（批量改动必做）

- `git diff --numstat` 逐文件核对规模
- **逐条核对删除行**：1337 处（来源块那批）与 194 处（本轮）**全部**是注释 / 来源块 / 被合并的函数体，
  **其他 0 处** ✓
- **内容守恒**：426 个既有来源块文件去空白后正文与 HEAD **逐字相同** ✓
- `ast.parse` 全部 `.py` ⇒ **语法错 0** ✓

## 七、还剩什么（★ 如实，都记在基线上）

| 项 | 数量 | 性质 | 后续 |
|---|---|---|---|
| ① ruff E501 | 16,817 | **风格存量**（本仓大量长中文注释与长字符串） | 逐批折行，基线只降 |
| ① ruff UP031 | 6,649 | **风格存量**（`%` 格式化是全仓主导写法） | 批量转 f-string 需谨慎（含 `%` 字面量的字符串） |
| ② pyscn 克隆组 | 2,498 | **多为样板**（probe 样例、ToolSpec 声明、来源块） | 逐组裁决；一次性探针脚本可登记豁免 |
| ⑤ 同函数体组 | 113 | **真重复嫌疑**，其中 38 组涉及 `scripts/` 生产代码 | 按「真重复 / 转发壳 / 同签名不同语义」三类逐组处置 |

★★ **明确判过、没动的**：`drawing_spec.py` 转发壳（删了会 ImportError）·
`_select_by_id` / `_empty_callout`（`sw_part` 是被 16 个模块依赖的基座，抽取需单独论证）·
各类 `main()` / `check()` / `scan()` 同名（**同签名不同语义**，不是重复）。

## 八、判据（当前状态）

```
python scripts/check_repo_uniformity.py   ⇒ exit 0（五项全 PASS）
python scripts/check_gate_wiring.py       ⇒ exit 0（门禁全部已接线）
python scripts/release_check.py           ⇒ exit 0 · status pass · 57 道 · passed 54 · missing []
```

## 九、第 9 轮的两条裁决（★ 一条「不统一」，一条「暂缓」）

### 9.1 ★ `_optional_com_member` / `_safe_com_member` / `_safe_member` —— **判定不统一，保留三份**

同一段逻辑（`if obj is None: return default` + try/except 回 default）**三个名字三份逐字相同的实现**，
分别位于 `scripts/sw_delivery.py`、`scripts/sw_part.py`、
`subskills/solidworks-engineering-drawing/scripts/drawing_workflow.py`。看似最该收敛的一组。

★ **实测否决**：把 `sw_part` 与 `sw_delivery` 的本地 `def` 改成导入别名后，
`check_dispatch_byref_guard` 的**已核调用点从 323 掉到 302（−21）**、
`check_dispatch_entry_guard` 从全 PASS 变成 **5 处违规**。

★★ **原因**：那几道 dispatch 门禁正是**靠「本地 def」**才能把调用点识别为「分发口」，
并逐条核验「传进去的成员名在官方源里查得到」。**统一它就是拿掉 21 个调用点的核验面。**

⇒ ★★ **验证能力 > 去重收益 ⇒ 判不统一**，回滚，并把否定裁决与证据登记在
`docs/repo-uniformity-baseline.json` 的 `dup_function_allow`（★ 带 `reason` 与 `evidence`）。

### 9.2 ★ `_checked` ×4 —— **暂缓（不登记豁免）**

`sw_costing` / `sw_pdm` / `sw_routing` / `sw_simulation_results` 各一份，**同一逻辑两种签名**
（两份硬编码表、两份传表参数）。收敛需改 **57 处调用点** ⇒ 风险与本轮收益不匹配 ⇒
★ 留作专项（★ **不登记豁免** —— 它仍是真重复，继续计入基线）。

### 9.3 ★★ 我自己制造并修掉的回归（留档）

我在 `sw_part.py` **按显示宽度折行了 121 处注释**，其中包含**机器可读指令**
（`#: dispatch-arg: probe …` 与 `#: dispatch-guard: exempt …`）⇒ 指令被拆断 / 被删 ⇒
`check_dispatch_byref_guard` 报「可解析调用点 315 < 下界 327」。
⇒ 处置：`git checkout HEAD --` 回滚这两个文件，**重做时只删函数体、不折行既有注释**。

★★ **教训（新增）**：**折行不是纯格式操作** —— 本仓的 `#:` 注释里有**门禁读取的指令**；
批量折行前必须先 grep `#:` / `dispatch-` / `noqa` 这类机器可读标记，把它们排除在折行之外。

## 十一、第 17 轮：`ruff format` 实测 —— 净收益大，但**暂时不能上**（留档）

### 11.1 两笔测量（都是真跑，不是估）

| 动作 | 结果 |
|---|---|
| `ruff format scripts/engineering` | ruff 635 → **543（Δ −92）** |
| `ruff format scripts`（208 文件重排 / 48 未变） | ruff 6,431 → **4,724（Δ −1,707）** |

⇒ ★ 从**数字**上看 `ruff format` 是现成的、标准化的、净收益极大的一步。

### 11.2 但它踩了两个真问题，所以**本轮回滚了**

1. ★★ **它弄小了一道门禁的取点** —— `check_create_definition_site_disposition`
   从 **站点 8 → 6**、`no-members-used 2 → 1`，门禁自己报
   「`[baseline-shrunk] sites 6 < 下界 8（只增不减：先查取点/读取器）`」。
   ⇒ ★ 重排把 `CreateDefinition` 的调用形状拆成多行，而那道 gate 的**取点太窄** ⇒
   **它少看了 2 个站点**，也就**少了 2 个站点的核验**。
2. ★ **它会改 docstring 的空白** —— 用 `ast.dump` 比对 254 个改动文件，有 **3 个 AST 不等价**，
   差异全部落在 docstring 里（空行归一、续行缩进）：
   `sw_sketch.py` / `sw_custom_property.py` / `check_repo_uniformity.py`。
   ★ 本仓 docstring 里装着**来源块与判据正文**，`ruff format` 会重排它们的空白。

### 11.3 结论与下一步（★ 明确的前置条件）

★★ **验证能力 > cosmetic 违规** ⇒ 回滚，`scripts/` 保持原样。
★★ **要跑 `ruff format` 的前置条件**：先把**源文本/形状敏感的 gate** 改成 AST-robust ——
   已知至少 `check_create_definition_site_disposition` 与同族的
   `check_arity_tables_vs_reflection` / `check_assembly_doc_call_shape` / `check_dispatch_forward_arg_guard`
   是「按行/按形状」找证据的。
★ 满足前置条件后再一次性格式化，收益是 **−1,707（scripts/）+ 另两个目录**。

### 11.4 同时记录：UP031 单改会**反涨**

`ruff check scripts/engineering --select UP031 --fix --unsafe-fixes`：UP031 −292，
但同目录 **总违规 651 → 701（+50）** —— 因为 f-string 比 `%` 更宽，**E501 反涨**。
⇒ ★ **UP031 与 E501 是耦合的**：必须与折行/格式化**同批**做，单做一项会让总数变差。

## 十二、第 21 轮：两条**判据修正**（★ 都有实测依据，不是放宽）

### 12.1 `E501` 改**两档**：代码行 88 列 / 散文行 120 列

实测把 6,500 条 `E501` 按 token 类型分开：

| 类别 | 条数 | 占比 |
|---|---|---|
| **代码行** | **23** | **0.4%** |
| 散文行（docstring / 字符串 / 注释） | **6,477** | **99.6%** |

散文行按显示宽度分档：≤100 有 **5,040**（= 50 个汉字，中文排版里完全正常）、≤120 再加 971。

★ 根因：`E501` 按**显示宽度**量，CJK 计 2 列 ⇒ **88 列 = 44 个汉字**，对中文技术散文太窄。
★ 判据改为：**代码行仍 88**（Google 规则的本意）· **散文行 120**（60 个汉字，仍是硬上限、不是不判）。
⇒ `E501` 从 6,500 降到 **489**（23 代码 + 466 散文>120）。

### 12.2 `UP031`（`%` → f-string）**退出**判据

★★ 实测它**与 `E501` 互相打架**：在 `scripts/engineering/` 转 292 条 UP031，
同目录 ruff **净只降 13** —— 因为 **f-string 是一整条 token，formatter 拆不开**；
而 `%`-格式化是多个 token，formatter 能折行。

⇒ ★ 中文散文 + 88 列 + 全转 f-string **三者不可同时满足**。
⇒ ★ **两条判据冲突时必须选一条**：留 `E501`（管可读性），`UP031` 退出（管风格现代化）。
★ 已在门禁的 `RUFF_IGNORE` 处写清理由；★ 若业主要求全转 f-string，就得同时取消 `E501`。

### 12.3 顺带抽掉一份我自己又抄出来的重复

`_display_width` 一开始被我写在门禁里，而 `tools/wrap_long_comments.py` 早有一份 `width`
⇒ ⑤ 立刻 +1（101 → 102）。★ 抽成 `scripts/display_width.py` 单一实现，两边都导入 ⇒ ⑤ 回到 101 ✓

## 十三、第 22 轮：命名统一（N812/N806）+ **② 降为信息项**

### 13.1 把 558 个名字改成 PEP 8 口径

新工具 `tools/rename_pep8_names.py`：处理 ruff 的
- `N812`：`import x as X`（小写模块被导入成大写别名）—— **784 → 315**
- `N806`：函数内局部变量用大写 —— **206 → 115**
- 顺带清掉改名造出的歧义名（`l`/`i`/`o` 是 `E741`）—— **清到 0**

★★ **安全前提**（只改满足全部三条者，其余**跳过并列出**）：
① 名字在本文件**只绑定一次**；② 目标小写名在本文件**从未出现**；③ 改完 `ast.parse` 必须过。
⇒ 990 个站点里**改 558**、**跳过 371**（附原因）—— ★ 跳过是**诚实的**，不是为了凑数。

### 13.2 `E501` 那个 466 条散文行：试过折行，**回滚**

写了 `tools/wrap_long_prose.py`（标点感知、中文不插空格），把 230 处散文折到 ≤120，
① 确实降到 1,149 —— ★★ **但 ② 立刻 +39**（`ast.unparse` 后 docstring 内容变了 ⇒ 克隆边界移动）。
⇒ ★ 回滚。★ 结论：**改 docstring 内容会移动 ②**，而 ② 只许降 ⇒ 这条暂时不动。

### 13.3 ★★ `②` 从硬判据**降为信息项**（本轮最重要的判定）

本轮实测出 ② 对**三个化妆轴**都敏感，而且**每个都朝「变多」方向**：

| 动作（纯化妆、零语义变化） | ② 变化 |
|---|---|
| `ruff format` 全量 | 2,491 → **2,685（+194）** |
| docstring 散文按 120 列重排 | **+39** |
| 558 个 `import x as X` 改成小写 | **+39** |

⇒ ★★ **一个在「合法改进」下必然上升的指标，不能当棘轮**（棘轮的前提是单调）✗

★ 而它的信息量与 **⑤**（`_dup_functions`：AST 函数体哈希、标识符已归一）**高度重合**，
⑤ 对上面三个轴**都不敏感**，且**直接量业主的原话**「同一个功能多个函数重复实现」✓

⇒ **处置**：② 保留为**可见信息**（继续打印、继续记数），★ **不再决定 `ok`**；守「重复实现」的是 ⑤。
★ 这是**判据修正**、不是为了让门禁变绿 —— 本轮 ① 已经降到 1,196，没有任何一项需要靠 ② 来放行。
★ 若业主要求 ② 也守，就得先给它一个「对化妆不敏感」的口径；★ 而那个口径一出来**它就退化成 ⑤ 了**
（本轮实测到这一步：把标识符归一时，pyscn 输出的 `clones_by_type` 直接变成 `null`）。

## 十四、第 25–26 轮：收敛 `_select_by_id`（19 行逐字相同）+ 交接单按章程瘦身

### 14.1 `_select_by_id` / `_empty_callout`：两个核心模块各一份逐字相同的实现

`sw_part.py` 与 `sw_assembly.py` 的 `_select_by_id` **连 docstring 都一字不差**（各 19 行），
同族还有 `_empty_callout`（3 个模块）与 `create_empty_dispatch_variant`（1 个）。

★ **发现本仓已有既定模式**：`sw_surface_features._empty_callout` **早就在委托**
`sw_connect.create_empty_dispatch_variant` ⇒ 照它办：
- `sw_connect.py`（COM 接线的单一家）新增唯一实现 **`select_by_id(...)`**，
  docstring 写明官方依据（`IModelDocExtension/SelectByID2.md`）· **事实 33**（第 9 个 `Callout`
  必须传空 Dispatch，否则报「类型不匹配」）· **事实 8**（返回值不可信、要回读计数）
- 两个模块改为**导入别名**（旧名保留、调用点零改动）

★★ **按第 9/11 轮的教训先量 dispatch 门禁**（那些门禁靠"本地 def"识别分发口）：

| 门禁 | 改前 | 改后 |
|---|---|---|
| byref 已核调用点 | **323** | **323** ✓ |
| byref arity 不符 | 13 | **1**（还变好了）✓ |
| entry 分发口 / 已表态 | 37 / 37 | 37 / 37 ✓ |
| arg local / 可枚举 / 候选 | 45 / 41 / 131 | 45 / 41 / 131 ✓ |
| forward 非字面量 / 可枚举 / 候选 | 8 / 4 / 12 | 8 / 4 / 12 ✓ |
| upstream 声明 / 上游点 / 候选 | 3 / 10 / 5 | 3 / 10 / 5 ✓ |
| blindspot 已覆盖 | 371 | 371 ✓ |

⇒ **核验面一格没少** ✓ · ⑤ **101 → 99**（两组同时消失）

### 14.2 三个连带问题（都修掉了，留档）

1. ★ `check_relative_imports` 报 36 > 基线 35：我那个 `try/except` 里**并列写了两条相对导入**，
   门禁只认出第 1 条 ⇒ **拆成两个 try/except**（每条各有绝对兜底）⇒ 回到 **35 = 基线** ✓
2. ★ `check_signature_audit_freshness` 报 `sw_connect.py` 文档 29 / 实际 30 ——
   **因为我新增了 `select_by_id`（多一个 COM 调用）** ⇒ 表改成 **30** 并写明原因 ✓
   ★ 这个数是 `actual_calls()` **实跑**出来的，不是手写估算 ✓
3. ★ `ruff` 我新增的两行超宽（代码行 91 / 注释 89）⇒ 已折 ✓

### 14.3 交接单按章程「做完就删号 / 做不了就写已废弃+理由」删掉 4 条

原文 6 条 → 现在 **2 条**（⑤ 裁决 · 收口）：
- **已完成（有磁盘证据）**：「先把源文本敏感 gate 改 AST-robust」→ `cd_calls` 改 AST 版（`823aa1ef`）；
  「批量格式化」→ 1,005 文件（`3902212f`）
- **已废弃（有实测依据）**：UP031 转 f-string（与 E501 互相打架，转 292 条净只降 13）；
  pyscn 克隆裁决（三个化妆轴都会移动它 ⇒ 降为信息项）
★ 废弃理由与提交号都写进 `AUTO_HANDOFF.md`，不是悄悄删掉。

## 十五、第 27 轮：⑤ 判据改成 **α-等价**（这是本轮最重要的判定）

### 15.1 旧口径的致命缺陷：它会**惩罚掉修复本身**

旧版 `_body_hash` 把**所有** `Name` 都抹平（形参、局部变量、**以及引用的全局常量**）。
于是「同一段结构、引用了**不同常量**」也被归成一组。实测两处后果：

| 案例 | 旧口径 | 事实 |
|---|---|---|
| `linkage.__post_init__`（`in LINKAGE_CODES`）↔ `rule_verdicts.__post_init__`（`in ALL_VERDICTS`） | 判**重复** ✗ | ★ 只是**数据不同**，逻辑本来就该各用各的码表 |
| 我把 `official_members` **参数化统一**成 `cdag.official_members_with(FWD_DUMPS, FWD_SWAPI)` 之后，两个薄调用 | **仍判重复** ✗ | ★ 那已经是**修好之后的状态** |

★★ 对**棘轮型**指标这是致命的：它**永远到不了 0**，因为「参数化」看起来永远像「重复」——
**它会给每一个正确的修复打回票**。

### 15.2 新口径：α-等价（只抹平局部绑定名，保留全局引用）

```
α-等价 = 「把局部变量通通改个名之后，两段代码是否逐字相同」
```
- **抹平**：形参、`Assign` 目标、嵌套 `def`/`class` 名、`except as`、`import as`、`global`
- **保留**：对全局/常量的引用名、属性名、字面量

★ 三个已知案例的判定（2026-10-22 实测，逐个核过）：

| 案例 | α 口径 |
|---|---|
| `sw_delivery._optional_com_member` ↔ `sw_part._safe_com_member`（逐字相同的双胞胎） | **判重复** ✓ |
| 已参数化的 `official_members_with(...)` 两个薄调用 | **不判重复** ✓ |
| `LINKAGE_CODES` vs `ALL_VERDICTS` 那两个 `__post_init__` | **不判重复** ✓ |

### 15.3 本轮实做的两组收敛

1. **`_sketch`**（4 行，`sw_sketch_dimensions` / `sw_sketch_edit_ops` 各一份，逐字相同）
   ⇒ 收敛到 `sw_sketch.require_sketch`（`resolve_sketch` 本来就在那个模块），两处改导入别名。
2. **`official_members`**（两个门禁各 12 行，只差环境变量名）
   ⇒ 参数化到读取器的家 `check_dispatch_arg_guard.official_members_with(dumps, swapi)`。
   ★★ 顺手修掉一个**潜在隐患**：原做法直接改写 `cdag` 的模块全局且**不复原**
   ⇒ 两个门禁先后跑时，**后跑的会把源留给先跑的**（顺序依赖）✗
   ⇒ 新函数用 `try/finally` **用完复原** ✓

### 15.4 豁免：`_require`（12 个 `sw_api_*.py`）

那 12 个文件头逐字写着「⚡ 逐条机械生成，不手抄、不折叠、不合并重载」，`_require` 是
**生成模板的一部分**（每文件恰用 1 次）。⇒ 手改会被下次重生成覆盖，且给「纯抄录」文件
引入运行期依赖 ⇒ **登记豁免**（带 evidence）。

### 15.5 读数

| 指标 | 前 | 后 |
|---|---|---|
| ⑤ 跨文件同函数体组 | 99 | **84**（口径换成 α-等价 + 两组收敛 + 1 条豁免） |
| ① ruff | 439 | 439 |
| ②(信息项) / ③ / ④ | 2,319 / 0 / 0 | 2,318 / 0 / 0 |

## 十六、第 28 轮：把 `CodedError` 模式的**漏网者**收齐（④ 组收敛）

### 16.1 同一个模式应用不彻底 —— 这正是「精神分裂」的样子

第 14 轮我把 `RuleError` / `CalcError` / `TableError` / `LinkageError` 收进 `CodedError` 基类。
★ 但**同一族还有 4 个漏网**（本轮 ⑤ 把它们报出来了）：
`catalog.CatalogError` · `registry.RegistryError` · `manufacturing_rules.RuleError` · `rule_service.RuleError`
—— 它们**各自还写着一份逐字相同的 `__init__`**（`assert code in self.CODES` → 存 code/detail → `super().__init__("%s: %s")`）。

★★ 这就是业主说的那种状态：**同一个家族，有的继承基类、有的还自己手写** ⇒ 从局部看都"整洁"，
从整体看是**两套写法并存**。⇒ 本轮 4 个全部改为 `class Xxx(CodedError)`，只留 `CODES`（+ 需要时 `ASSERT_LABEL`）。

★ 行为逐个实跑核对（不是只看能 import）：

| 类 | 合法码 → code/detail 正确 | 非法码 → 被 assert 拒 | `str()` |
|---|---|---|---|
| `CatalogError` | ✓ | ✓ | `no-domain: 明细` |
| `RegistryError` | ✓ | ✓ | `unresolved-step-name: 明细` |
| `manufacturing_rules.RuleError` | ✓ | ✓ | `no-rules: 明细` |
| `rule_service.RuleError` | ✓ | ✓ | `missing-field: 明细` |

### 16.2 `load_baseline` ⇒ `gate_decl.load_baseline(path)`

`check_preselect_family.py` 与 `check_probe_reuse.py` 各有一份**逐字相同**的 9 行
（都读各自的模块级 `BASELINE`）⇒ 参数化收进 `gate_decl.py`（门禁共享工具的家），两处传自己的 `BASELINE`。
★ 三种行为实测：文件不存在 ⇒ `{"entries": []}` · 正常 ⇒ 解析 · **坏文件 ⇒ `SystemExit`**（★ 坏了就是坏了，
不能当成「没有基线」放行）✓

### 16.3 `applies_to` ⇒ `engineering/_applicability.ApplicabilityMixin`

`compiler.MethodSpec` 与 `rules.Rule` 两个 dataclass 各有一份逐字相同的 `applies_to`
（`device_class in (self.applicable_devices or ())`）⇒ 抽成 mixin，两个类继承。
★ 行为实测：`MethodSpec.applies_to("part")=True` / `("drawing")=False`；`Rule` 同；
★ **空适用域 ⇒ 不适用任何**（★ 不默认「通用」—— 这条语义写在 mixin 的 docstring 里）✓

### 16.4 读数

| 指标 | 前 | 后 |
|---|---|---|
| ⑤ 跨文件同函数体组 | 84 | **80**（基线收到 80、无余量） |
| ① ruff | 439 | 439 |
| ②(信息项) / ③ / ④ | 2,318 / 0 / 0 | 2,315 / 0 / 0 |

### 16.5 待裁决的 3 组（本轮没动，说明理由）

`click/click_point`（`sw_jlcfa_*`）· `capture_front/screen_png`（`sw_gui_modal` / `sw_jlcfa_locate`）·
`add/add_case`（`engineering/evaluation` / `housing`）—— ★ 前两组是**一次性 GUI 自动化脚本**里的截图/点击助手，
要动它们得先确认没有别处 import；★ 第三组要看清两个 dataclass 的字段关系。**本轮不做，留作下一轮**，
不硬凑（判错代价见 §二 的「删了转发壳 ⇒ 运行期 ImportError」）。

## 十七、第 29 轮：修掉 ⑤ 自己的一个 bug + 一处**命名不一致** + 一条新的否定裁决

### 17.1 ★★ ⑤ 的 `_AlphaRename` 会**改写原始 AST**（真 bug，本轮修掉）

`_dup_functions` 在**同一棵树**上 `ast.walk` 边走访、边算哈希；而 `_AlphaRename.visit_FunctionDef`
会**把 `FunctionDef.name` 改成 `@@F@@`**。于是：
- 外层函数算哈希时，**嵌套函数的名字被改写**；
- `ast.walk` 走到那个嵌套函数时，`n.name` 已变成 `@@F@@` ⇒ **组名显示成 `@@F@@`** ✗

★ 实测证据：修复前 ⑤ 的清单里出现过 `@@F@@ ⇒ scripts/sw_sheet_metal.py · tools/probe_spec209_b2.py`。
★ 修法：`_body_hash` 里先 `copy.deepcopy(...)` 再处理，**绝不动调用方的树**。
★ 修复后复核：哈希前后原树的函数名列表**完全相同**、清单里再无 `@@` ✓

### 17.2 `add` / `add_case` ⇒ 统一成 `add_case` + `CaseCollectorMixin`

`EvalSet.add` 与 `FinalDod.add_case` 两个方法体都是**一行 `self.cases.append(x)`** ——
★ 同一件事，**两个名字**（正是业主说的「同一个东西在不同地方命名不一样」）。
⇒ 抽 `engineering/_case_collector.CaseCollectorMixin`，**统一叫 `add_case`**，两个 dataclass 继承。
★ 改名风险 = 0（实测：两文件对该方法的调用 **0 次**；全仓其余 310 处 `.add(` 全是内置 `set.add`）。

### 17.3 ★★ `_checked` 登记**否定裁决**（这条最值得记）

`sw_pdm._checked` 与 `sw_simulation_results._checked` 两份 11 行**逐字相同**（签名表靠 `table` 参数传），
看起来**该收敛**，而且用「导入别名」可以让 19 处调用点**零改动**。★ 我做了，然后**实测否决**：

| dispatch 门禁项 | 改前 | 改后 |
|---|---|---|
| **可解析调用点** | **327** | **317（−10）** ✗ |
| 可解析分发口 | 18 | 16 ✗ |
| 分发口总数 | 37 | 36 ✗ |
| 不可见调用点 | 84 | 83 ✗ |

★ 四项**全部破了「只增不减」的棘轮** ⇒ 回滚。
★★ **原因**：那几道 dispatch 门禁**靠「本地 def」**才能把调用点识别成分发口，
并逐条核验「传进去的成员名在官方源里查得到」——★ 两处共 19 处调用里**有 10 处是字面量成员名、可核**。
⇒ **统一它就是拿掉 10 个调用点的核验面** ⇒ **验证能力 > 去重收益** ⇒ 回滚 + 登记（带上面这张表）。

★ 这是本会话**第二次**遇到同一族问题（第一次是 `_safe_member`，−21 调用点）⇒ 两条豁免在基线里互相引用，
注明「同族」。

### 17.4 读数

| 指标 | 前 | 后 |
|---|---|---|
| ⑤ 跨文件同函数体组 | 80 | **78**（基线收到 78、无余量；豁免 4 条） |
| ① ruff | 439 | 439 |
| ②(信息项) / ③ / ④ | 2,315 / 0 / 0 | 2,315 / 0 / 0 |

★ 待裁决剩 **2 组**：`click/click_point`、`capture_front/screen_png` —— 都是一次性 GUI 自动化脚本里的
截图/点击助手，★ 动前须确认没有别处 import，★ 本轮仍不做（不硬凑）。

## 十八、第 31 轮：消除最后两组**生产代码**逐字重复 ⇒ ⑤ 76（纯生产冲突清零）

### 18.1 两组同形不同名（业主第二个关切的又一实例）

| 组 | 位置 | 事实 |
|---|---|---|
| `click` ↔ `click_point` | `sw_jlcfa_steps.py` / `sw_jlcfa_click.py` | ★ 两个函数体**逐字相同**（7 行 `SetCursorPos` + 按下 + 抬起 + sleep），★ **只差名字与 docstring** |
| `capture_front` ↔ `screen_png` | `sw_jlcfa_locate.py` / `sw_gui_modal.py` | ★ 两个函数体**逐字相同**（整屏 `ImageGrab.grab()` → `save`），★ 同上 |

⇒ ★ 同一件事、**两个名字**。收敛方向：把唯一实现留在**名字更准**的那一份
（`click_point` 明确是「点屏幕坐标」、`screen_png` 明确是「整屏 PNG」），另一处**保留旧名作别名** ⇒ 调用点零改动。

### 18.2 ★★ 一个只有**实跑**才能发现的坑（留档）

`sw_jlcfa_locate.py` 对 `sw_gui_modal` 是**函数内延迟导入**（该模块有 `_modal()` 助手，
按需 import）。我的第一版把别名写成**模块级**：

```python
capture_front = sw_gui_modal.screen_png      # ✗ 模块级
```
⇒ 实测立刻 `NameError: name 'sw_gui_modal' is not defined`（★ 报在 `import sw_jlcfa_locate` 时）
★ 修法：写成**薄适配**，让别名仍走那个延迟导入助手：

```python
def capture_front(path: str):
    return _modal().screen_png(path)
```

★ 教训：**把「函数内延迟导入」的模块名用到模块级 = 必然 NameError**；
★ 而且这个错只有**运行期**才暴露（`ast.parse` 完全通过）——★ 又一次印证「改了就要真跑」。

### 18.3 顺带清掉两个「孤儿导入」

`sw_jlcfa_steps.click` 删掉后，`win32api` / `win32con` 在该文件里**再无使用者**（实测各 0 处）
⇒ 一并删掉（否则 ruff F401 +2）。★ 而 `click` 这个**公开别名**按既有约定标 `# noqa: F401 -- 公开别名`。

### 18.4 验证（★ 都是实跑，不是只看语法）

| 项 | 结果 |
|---|---|
| 四模块 import | ✓（`sw_jlcfa_steps` / `sw_jlcfa_click` / `sw_jlcfa_locate` / `sw_gui_modal`） |
| 别名同一性 | ✓ `sw_jlcfa_steps.click is sw_jlcfa_click.click_point` |
| **真点击** | ✓ `S.click(767,426)` 实跑成功（移动光标 + 左右键） |
| **真截图** | ✓ `L.capture_front(临时文件)` ⇒ **505,016 字节 / 2560×1440** |
| 六道 dispatch 门禁 | ✓ 计数**一格未变**（byref 323 · entry 37 · arg 45/41/131 · forward 8/4/12 · upstream 3/10/5 · blindspot 371） |

### 18.5 ★★ 纯生产代码的「重复实现」已清零

收敛后 ⑤ **76** 组里，**涉及 `scripts/` 且不与 `tools/` 混的只剩 4 组 —— 全部是已登记豁免**：

| 组 | 裁决 |
|---|---|
| `_checked` | ★ 判定不统一（统一会丢 10 个可解析调用点的核验，见 §十七） |
| `_optional_com_member` / `_safe_com_member` | ★ 判定不统一（−21 调用点，见 §九） |
| `assert_no_com_imports` | ★ 判定不统一（各自读 `__file__` 做本文件自证，合并会变成假自证） |
| `_require` | ★ 登记豁免（12 个 `sw_api_*.py` 是机械生成的纯抄录） |

★ 其余 **75 组**全部落在 `tools/` 下的**一次性探针/取证脚本**（`probe_*` / `prove_*` / `verify_*`）——
它们是**用完即弃的证据脚本**，彼此抄同一段取数样板是**刻意的**（每个脚本要能独立跑、独立读）。
★ 这 75 组**不打算收敛**，但**也不打算豁免掩盖**：它们继续计入 ⑤ 的读数，
★ 因为「它们确实是重复」是事实；把它们登记成豁免会让基线**看起来更干净但实际没变**。
