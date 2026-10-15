# plan 237 · `CreateDefinition` 站点处置门禁

## 一、三源与冲突裁决顺序

| 序 | 源 | 路径 | 本规格用它做什么 |
|---|---|---|---|
| ① | **官方 API 文档镜像** | `C:\swapi\types\<接口>\<成员>.md` | 期望接口的**成员集**（`members_of(iface)`）；接口是否存在 |
| ② | **CHM 解包 / 官方枚举页** | `C:\swapi\enums\swFeatureNameID_e.md` | 佐证 `swFmMateProfileCenter` 等常量**是官方的**（本规格只用它做**事实核对**，不进判据） |
| ③ | **出厂程序集反射转储** | `_raw/enum_values_sldworks.txt`（`swFm* = <int>`） | 模块常量 → `swFm*` 名的**反查**（`enum_values()`） |

**冲突裁决顺序**：反射转储（`_raw`，机器事实）> 官方文档镜像（`C:\swapi`）> 本仓既有登记。
★ 本规格**不新增任何值**，只**读**三源 ⇒ 不产生新的冲突面。

## 二、取点口径（★ 全部 import，不重写）

| 件 | 来源 |
|---|---|
| 站点枚举（`module_consts` / `cd_calls` / `to_const` / `enclosing_func_name` / `param_index` / `calls_of` / `enclosing_range`） | `check_interface_member_ownership`（**本轮把它抽成 `scan_sites()`**，`main()` 与门禁共用） |
| `CONST → 接口` 映射表 | `check_interface_member_ownership.build_map()` |
| 期望接口的成员集 | `check_interface_member_ownership.members_of()` |
| 忽略名单 | `check_interface_member_ownership.IGNORE` |

★ **不重写任何读取器**；唯一改动是把 `main()` 的取点循环**搬家**到 `scan_sites()`（行为等价 + 多一行分码明细）。

## 三、改动清单

| # | 文件 | 改动 | 规模 |
|---|---|---|---|
| 1 | `scripts/check_interface_member_ownership.py` | ① 新增 `SITE_CODES` + `scan_sites(paths)`；`main()` 改为消费它（**读数不变**，多打一行分码明细）；② ★ **`module_consts` 正则宽化**（容忍行尾注释）—— FR-006 | 小 |
| 2 | `scripts/check_create_definition_site_disposition.py` | **新增门禁**（声明解析 + 自证 + 下界冻结 + 零检查即红 + `[SKIP]` 便携） | ~190 行 |
| 3 | `tests/test_cd_site_disposition.py` | **新增判据**（真树 1 + 端到端合成树负例 ≥10 + 自证 4 + 源隔离 1 + FR-006 1） | ~230 行 |
| 4 | 4 个 `scripts/sw_*.py` | **5 行声明纯插入**（`#: cd-site: …`） | 5 行 |
| 5 | `scripts/release_check.py` | 接线（`_run_cd_site_disposition_gate` + fail 判据 + `_gate_results`） | 小 |
| 6 | `docs/gate-classification.json` | `classification` 46 → **47** | 小 |

## 四、施工顺序（★ 先证能红）

1. 写 `spec/plan/tasks` 四件；
2. **先写判据** `tests/test_cd_site_disposition.py` ⇒ 跑 ⇒ **必红**（门禁文件还不存在）；
3. 实现门禁 ⇒ 跑判据 ⇒ **仍红**（真树 5 个站点未表态）；
4. 跑门禁本体 ⇒ 拿**红基线** `[undeclared] ×5 · exit 1`（这就是「能红」的证据）；
5. 补 5 行声明（**纯插入零删除**）⇒ 判据绿、门禁绿；
6. **FR-006 的能红判据**：先跑 `test_module_consts_reads_trailing_comment` ⇒ **红** ⇒ 再宽化正则 ⇒ 绿；
7. 接线 `release_check` + `gate-classification.json`；
8. **变异检验**：短路 `judge()` ⇒ 判据必须出现非零 `failures`（证明不是空判据）；
9. 收尾链 + 合并回归 + 门禁全套（**3.14.7**）。

## 五、合成树夹具的两条纪律（前几轮踩过）

- ★★ 夹具必须**自带一个已表态样本**（否则 `[zero-checked]` / `entries == 0` **先红** ⇒ 负例**因错误的原因**通过）。
- ★★ 夹具必须**同时桩掉被复用门禁的扫描根与数据源**：
  `DSH_CD_SITE_ROOT`（本门禁自己的扫描根）+ `DSH_CD_SITE_TYPES`（官方文档树）
  ⇒ 否则被复用的 `check_interface_member_ownership` 会去读**真树/真文档**。

## 六、风险

| 风险 | 处置 |
|---|---|
| 宽化 `module_consts` 会改变原诊断的读数（`no-const 1 → unmapped 1`） | 预期行为：原诊断的「检查过 5」**不变**；跳过仍是 5，但**分码明细**从 `no-const 1` 变成 `unmapped 3`。★ 在 acceptance 里写清前后读数 |
| 一行 5 个计划的声明归属歧义 | 声明**必须指名常量**（`unmapped <const>…`）；自证要求**集合相等** |
| 下界常量被别的轮次改小 | 下界冻结 + `[baseline-shrunk]` 即红 |
