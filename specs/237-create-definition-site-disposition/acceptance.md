# acceptance 237 · `CreateDefinition` 站点处置门禁 —— 验收记录

**日期**：2026-10-09 · **切片**：`specs/237-create-definition-site-disposition/` · **离线切片（未调 COM / 未动真机）**

## 一、交付物

| 件 | 路径 | 说明 |
|---|---|---|
| 门禁 | `scripts/check_create_definition_site_disposition.py` | **新增**（逐站点表态 + 四 code 自证 + 下界冻结 + 零检查即红 + `[SKIP]` 便携） |
| 判据 | `tests/test_cd_site_disposition.py` | **新增 15 例**（真树 2 · 端到端合成树 10 · FR-006 1 · 便携 1 · 源隔离 1） |
| 取点共用 | `scripts/check_interface_member_ownership.py` | 改：新增 `SITE_CODES` + **`scan_sites()`**（`main()` 改为消费它，多一行分码明细）；★ **`module_consts` 正则宽化**（容忍行尾注释，FR-006） |
| 声明 | `scripts/sw_motion.py` · `sw_sheet_metal.py` · `sw_sweep.py`(×2) · `sw_weldment.py` | **5 行纯插入零删除** |
| 接线 | `scripts/release_check.py` | 改：`_run_cd_site_disposition_gate` + `raise` 判据 + `_gate_results` 登记 |
| 登记 | `docs/gate-classification.json` | 改：`classification` **46 → 47** |
| 打包副本 | `apps/**`（由 `sync_bundled_skill.py` 同步） | `files 470 · pruned []` |
| 规格 | `spec.md` / `plan.md` / `tasks.md` / `acceptance.md` | 四件齐 |
| 探针（**不进仓库代码**） | `output/_probe237_ownership.py` · `_probe237b_literal.py` · `_probe237c_cd_sites.py` | 先量用 |

## 二、读数（全绿）

| 判据 | 命令 | 读数 |
|---|---|---|
| 门禁本体（真树） | `python -B scripts/check_create_definition_site_disposition.py` | `站点 10 · checked 5 · unmapped 3 · empty-members 0 · no-members-used 2 · dynamic 0 · 违规 0 · [PASS] · exit 0` |
| ★ **红基线（证明能红）** | 补声明**之前**跑门禁 | `[undeclared] ×5`（`sw_motion.py:211` · `sw_sheet_metal.py:395` · `sw_sweep.py:91` · `sw_sweep.py:206` · `sw_weldment.py:686`）· **exit 1** |
| 新判据 | `python -B -m unittest tests.test_cd_site_disposition -v` | **Ran 15 tests · OK**（13.6 s） |
| ★ **变异检验** | 短路 `judge()`（首行插 `return None`）⇒ 跑判据 | `Ran 15 tests · FAILED (failures=4)` ⇒ **判据不是空判据**；已 `md5sum -c` 复核还原 |
| ★ **FR-006 能红判据** | `test_module_consts_reads_trailing_comment` | 宽化前 **红**（`SW_FM_B` 读不到）⇒ 宽化后 **绿** |
| 原诊断未回归 | `python -B scripts/check_interface_member_ownership.py` | `exit 0`；`检查过 5 个站点；跳过 5` **不变**，新增分码行 `checked 5 · unmapped 3 · empty-members 0 · no-members-used 2 · dynamic 0` |
| 229–237 合并回归 | `python -B -m unittest tests.test_dispatch_* tests.test_cd_site_disposition` | 见 §三 |
| **门禁全套** `release_check.py` @**3.14.7** | `C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py` | `EXIT 0` · `status pass` · `missing []` · `gates` **45 → 46** · `cd_site_disposition: pass` |
| 登记条目 | 同上次 | `classification` **46 → 47**（★ 两套口径**都 +1**） |
| 打包副本新鲜度 | `scripts/sync_bundled_skill.py` | `files 470 · pruned []` |

## 三、★ 核心结论

### 3.1 真靶子：四种处置被合成一个数（静默降级）

`check_interface_member_ownership.py` 原先只报「检查过 5 个站点；**跳过 5**」。摊开后是：

| 站点 | 常量 | 真实处置 | 含义 |
|---|---|---|---|
| `sw_motion.py:212` | `swFmAEMRotationalMotor` | `unmapped` | **该审却漏审**（映射表没有） |
| `sw_sheet_metal.py:396` | `swFmDraft` | `unmapped` | 同上（同一行其余 4 个常量均已覆盖） |
| `sw_sweep.py:92` | `swFmSweepCut` | `no-members-used` | 确实无事可查（只调 `AccessSelections`/`CreateFeature`） |
| `sw_sweep.py:208` | `swFmRefSurface` | `no-members-used` | 同上 |
| `sw_weldment.py:687` | `swFmMateProfileCenter` | `unmapped` | ★ **此前被误判成「解析不出」**（见 3.2） |

⇒ ★★ 合成一个数之后，**一次把 `checked` 退化成 `unmapped` 的回归完全不可见**（读数仍是「跳过 5→6」）。

### 3.2 ★★★ 真缺陷：`module_consts` 的窄正则（「窄读取器读出 0 也会骗人」第七次）

`module_consts()` 旧正则 `^\s*([A-Z][A-Z0-9_]*)\s*=\s*(\d+)\s*$` 要求常量行**以数字结尾**：

```
scripts/sw_weldment.py:50   SW_FM_MATE_PROFILE_CENTER = 101  # swFmMateProfileCenter
```

⇒ `\s*$` 不匹配 ⇒ **该文件常量表 `{}`** ⇒ 它唯一的 `CreateDefinition` 站点（`_create_from_definition`，
调用方 `:828` 传 `SW_FM_MATE_PROFILE_CENTER`）被**静默判成「常量解析不出」**（`no-const 1`）。

宽化后（允许 `[ \t]*(#.*)?$`）：该站点常量解析为 **`swFmMateProfileCenter`**
（官方：`_raw/enum_values_sldworks.txt:105` = 101 · `C:\swapi\enums\swFeatureNameID_e.md` 有）
⇒ 真实处置是 **`unmapped`**。★ 全仓**只有 `sw_weldment.py` 的三个常量带行尾注释** ⇒ 影响面 = 1 个站点。

### 3.3 ★★ 交接单 ⑤「候选值的接口归属」**没有靶子**（先量推翻）

| 量了什么 | 读数 |
|---|---|
| 37 个分发口的宿主接口能否在 docstring 显式登记（`:param <名>: <Iface>`） | **0 / 37**（**37/37 连 `:param` 段都没有**） |
| 235 的 12 个候选值落在几个接口上 | **唯一 2 · 歧义 10 · 查不到 0** |
| 236 的 5 个候选值 | **唯一 3 · 歧义 2 · 查不到 0** |
| 37 个分发口的**字面量**调用点成员名存在性 | 调用点 **362** · 字面量 **354** · 两源查不到 **0** |

⇒ 只有 **5/17** 能唯一落 ⇒ **不建 37 行人工表、不改解析器**（照 232 的纪律：没有靶子的守卫不写）。

## 四、本切片自己踩到的坑

1. ★★ **合成树夹具的声明挂载点搞错了**：首版把声明写在**调用方**那行上方 ⇒ 门禁读的是
   **`CreateDefinition` 调用行**（helper 那行）⇒ 声明找不到 ⇒ 7 例假红。
   ★ 教训：**先想清「站点」的定义**（站点 = `CreateDefinition` 调用，不是它的调用方）。
2. ★★ **夹具漏了模块常量定义** ⇒ `to_const` 解析不出 ⇒ 站点全成 `dynamic`（**因错误的原因**通过/失败）。
3. ★★ **合成树下界没归零** ⇒ `[baseline-shrunk]` **先红** ⇒ 负例被噪声淹没（232/233 同族）。
4. ★★ **整数表会进枚举盲区**：`BASELINE = {...}`（6 项）首跑 `release_check` 当场被
   `check_enum_values_vs_reflection` 报「1 张未表态」⇒ 改成 **6 个独立常量**（与姊妹门禁同形状）。
5. ★ `Edit` 插函数后**立刻复核** `# ── 来源 ──` 头 ⇒ 本轮**没有**吞头。

## 五、未过门（如实登记）

- 3 个常量（`swFmDraft` / `swFmAEMRotationalMotor` / `swFmMateProfileCenter`）**未进映射表** ⇒
  其站点的成员**仍未审**；本门禁只把这件事**变成可见 + 必须表态**，
  **不**替它们补映射（补表要逐条读官方 `_overview.md` 的 Description；★ 门禁**不得自动挑选约定**）。
- `dynamic` 的自证是**文本级**的（不含 `swFm\w+` / 非纯数字 / 不在同文件模块常量表），**不是**数据流级。
- 判据只扫 `scripts/*.py`（与原诊断一致）；`tools/**` 未纳入。
- 桶判定是**静态**的；真机未验；223 的 8 条 `HEAD` 即红既有失败未修；未提交未部署。
