# spec 237 · `CreateDefinition` 站点的**逐站点处置**门禁

> **来源**：spec 236 交接单 ② 段待办 ⑤（「候选值的接口归属」）的**先量结果**。
> ★ 先量把待办 ⑤ 推翻了（见 §三），量出来的真靶子是**另一件**：`CreateDefinition` 站点的处置
> **被合成一个计数**（静默降级），且其中藏着一处**读取器太窄**的真缺陷。
> 许可：本仓库 MIT。无第三方代码引入。官方依据 = `C:\swapi\types\**` + `_raw/**` 反射转储。

## 一、问题（为什么需要）

`scripts/check_interface_member_ownership.py`（**诊断**，非门禁）末尾只打印一行：

```
扫描 197 个文件；**检查过 5 个 `CreateDefinition` 站点**；跳过 5（映射表没有 / 成员集空 / 没收集到成员）
```

★★★ **四种**语义完全不同的处置被**合成一个 `跳过 5`**：

| 真实处置 | 含义 | 风险 |
|---|---|---|
| `no-const` | 站点的常量**静态解析不出** | 可能是**读取器太窄**（假「解析不出」） |
| `unmapped` | 常量解析出来了，但**不在** `CONST → 接口` 映射表里 | 该站点的成员**一个都没被审** |
| `empty-members` | 期望接口在官方文档树里**没有成员页** | 数据源缺 |
| `no-members-used` | data 对象建了但**没设任何成员** | 真的无事可查 |

⇒ ★★ **这四种里，前两种都是「本来该审却漏审」，后两种是「确实无事可审」** ——
合成一个数之后，**一次把 `checked` 退化成 `unmapped` 的回归完全不可见**（读数仍是「跳过 5→6」）。
这正是本仓反复出现的病灶族：**「解析不出」被静默降级**（spec 230/231/233/234/235/236 六次）。

★★ **并且本轮「先量」当场量出一处真缺陷**（见 §三.2）：
`module_consts()` 的正则要求常量行**以数字结尾**（`\s*$`）⇒ **带尾注释的常量行一律读不到** ⇒
`scripts/sw_weldment.py` 的 `SW_FM_*` 三个常量**全部读不到** ⇒ 它唯一的站点被静默判成 `no-const`。
⇒ 这是「**窄读取器读出 0 也会骗人**」（spec 233/234 同族）的第七次。

## 二、需求

| # | 需求 | 判据 |
|---|---|---|
| **FR-001** | `check_interface_member_ownership` 的取点循环抽成 **`scan_sites(paths)`**，返回**逐站点**记录 `{file, line, var, arg, const, code, used, bad}`；`code` ∈ **封闭词表** `SITE_CODES`；`main()` 改为消费它（**读数与原来一致 + 多一行分码明细**）。★ 口径**不重写**，只搬家 | `tests/test_cd_site_disposition.py` 的真树用例 + 原诊断输出行仍在 |
| **FR-002** | ★★ **非 `checked` 站点必须逐站点表态**：其**正上方第一行非空行**（确定性关联，向上跳过空行）必须是 `#: cd-site: <code> [<const>…] <理由>`。**未表态即红** | 红基线：补声明之前 ⇒ `[undeclared] ×5 · exit 1` |
| **FR-003** | **每个 code 自带自证条件**（写错即红） | 见 §二.1 |
| **FR-004** | **只增不减**（下界冻结）：站点数 / `checked` 数 / 各 code 计数 | 常量被改小 ⇒ `[baseline-shrunk]` |
| **FR-005** | **零检查即红**（事实 46）：`站点 == 0` 或 `checked == 0` ⇒ FAIL | 合成树夹具 |
| **FR-006** | ★ **读取器宽化**：`module_consts()` 允许**行尾注释**（`SW_FM_X = 3  # swFmDraft`） | ★ **能红的判据**：`test_module_consts_reads_trailing_comment`（改实现前必红） |
| **FR-007** | **便携**：官方文档树不在 ⇒ `[SKIP]` + `exit 0`（缺数据源 ≠ 检查失败） | 合成树/环境开关 |

### 二.1 封闭词表与自证条件

```
#: cd-site: unmapped <const>…       <理由>
#: cd-site: empty-members           <理由>
#: cd-site: no-members-used         <理由>
#: cd-site: dynamic                 <理由>
```

| code | 自证条件（写错即红） |
|---|---|
| `unmapped` | 列出的常量集合 **必须等于** 该站点**实际**未映射常量集合（漏列 / 多列 ⇒ 红） |
| `empty-members` | 该站点期望接口的成员集**确实为空** |
| `no-members-used` | 该站点**确实** 0 个 `data.X`（有 ⇒ 红） |
| `dynamic` | ★★ **读取器太窄的守卫**：实参文本必须**同时**满足 ① 不含 `swFm\w+` 字面量 ② 不是纯数字 ③ 不在同文件模块常量表里 —— 任一不满足 ⇒ 红 `reader-too-narrow`（**不许把「读取器读不出」写成「它就是动态的」**） |
| `checked`（隐式，**不需要**声明） | ★ 若在 `checked` 站点上写声明 ⇒ 红 `redundant-decl`（多余声明 = 噪声，且会掩盖真回归） |

## 三、先量（2026-10-09 · 本规格开工前）

探针：`output/_probe237_ownership.py` · `_probe237b_literal.py` · `_probe237c_cd_sites.py`（**均不进仓库代码**）。

### 三.1 ★★ 待办 ⑤「候选值的接口归属」**没有靶子**（先量把它推翻）

| 量了什么 | 读数 | 结论 |
|---|---|---|
| 37 个分发口能否在 docstring 显式登记宿主接口（`:param <名>: <Iface>`） | **0 / 37**（**37/37 连 `:param` 段都没有**） | 宿主接口**根本没被登记** |
| 235 的 12 个候选值落在几个接口上 | **唯一 2 · 歧义 10 · 查不到 0** | 10/12 歧义 ⇒ 判不了 |
| 236 的 5 个候选值 | **唯一 3 · 歧义 2 · 查不到 0** | 只有 5/17 能唯一落 |
| 37 个分发口的**字面量**调用点成员名存在性 | 调用点 **362** · 字面量 **354** · 两源查不到 **0** | 已干净，且 `check_member_names.py` 已覆盖该形态 |

⇒ ★ 只有 **5/17** 能唯一落 ⇒ 不够格当判据；且宿主接口 **0/37 登记** ⇒ 建表无依据。
★ **不改解析器、不建 37 行人工表**（照 232 的纪律：**没有靶子的守卫不写**）。

### 三.2 ★★★ 真靶子：`CreateDefinition` 站点的**逐站点处置**（10 个计划）

```
checked 5 · skipped 5 = unmapped 2 + no-members-used 2 + no-const 1
```

| # | 文件:行 | 常量 | 处置 | 说明 |
|---|---|---|---|---|
| 1 | `sw_motion.py:211` | `swFmAEMRotationalMotor` | **unmapped** | 映射表没有 ⇒ **`motor_data.DirectionReference` 等成员从未被审** |
| 2 | `sw_sheet_metal.py:252` | `swFmBaseFlange` | checked | used 10 · bad 0 |
| 3-7 | `sw_sheet_metal.py:395` | `swFmSketchBend` / `swFmEdgeFlange` / **`swFmDraft`** / `swFmSMGusset` / `swFmSweptFlange` | checked ×4 + **unmapped ×1** | ★ **一行 5 个计划，其中一个未映射** ⇒ 声明必须**能指名常量** |
| 8 | `sw_sweep.py:91` | `swFmSweepCut` | **no-members-used** | data 建了但**只调 `AccessSelections`/`CreateFeature`**，**不设任何成员**（实测 0 个 `data.X`）⇒ 真的无事可查 |
| 9 | `sw_sweep.py:206` | `swFmRefSurface` | **no-members-used** | 同上 |
| 10 | `sw_weldment.py:686` | **（读不出）** | **no-const** | ★★★ **读取器太窄**：`SW_FM_MATE_PROFILE_CENTER = 101  # swFmMateProfileCenter` **带尾注释** ⇒ `module_consts()` 的 `\s*$` 不匹配 ⇒ 该文件常量表 **`{}`** ⇒ 站点被静默跳过 |

★★ **#10 是真缺陷**（不是「它就是动态的」）：把正则放宽到容忍尾注释后，该站点常量解析为
`swFmMateProfileCenter`（**官方**：`_raw/enum_values_sldworks.txt:105` = 101 · `C:\swapi\enums\swFeatureNameID_e.md` 有）
⇒ 真实处置是 **`unmapped`**（映射表没有），**不是** `no-const`。

## 四、验收判据（可复制执行）

```bash
# ① 本规格新判据 —— 期望 OK
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest tests.test_cd_site_disposition -v

# ② 门禁本体（真树）—— 期望 [PASS] · exit 0
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_create_definition_site_disposition.py

# ③ 原诊断仍在且读数一致 —— 期望 exit 0 且含「检查过 5 个」
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_interface_member_ownership.py

# ④ 门禁全套（★ 必须 3.14.7）
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py
```

## 五、不做什么（边界）

- **不**给 `swFmDraft` / `swFmAEMRotationalMotor` / `swFmMateProfileCenter` 往 `MANUAL_MAP` 里补映射 ——
  补表需要「逐条读官方 `_overview.md` 的 Description」，本轮**不做** ⇒ 只按 `unmapped` **如实表态**并登记为未过门
  （★ 门禁**不得自动挑选约定**，也不得把「我不知道」写成「它属于 X」）。
- **不**判「成员是否属于**这个**接口」—— 那需要映射表覆盖，本轮只把**处置**摊开。
- **不**改 `check_member_names.py` / `check_member_owner_interface.py` 的判据。
- **不**动 `audit_byref_args` / 229–236 的任何常量。
- **不**主动扩 `_entry_sites()` 认别名（触发条件 = spec 232 门禁变红，现在不红）。

## 六、未过门（如实登记）

- 3 个常量（`swFmDraft` / `swFmAEMRotationalMotor` / `swFmMateProfileCenter`）**未进映射表** ⇒
  其站点的成员**仍未审**（本规格只把这件事**变成可见 + 必须表态**）。
- `dynamic` 的自证是**文本级**的（不含 `swFm\w+` / 非纯数字 / 不在模块常量表），**不是**数据流级。
- 判据只扫 `scripts/*.py`（与原诊断一致）；`tools/**` 未纳入。
- 真机未验；223 的 8 条既有红未修；未提交未部署。
