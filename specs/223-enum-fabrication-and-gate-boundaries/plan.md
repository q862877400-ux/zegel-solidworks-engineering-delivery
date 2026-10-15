---
description: "Implementation plan: 伪造枚举表裁决与门禁边界透明化"
---

# Implementation Plan: 伪造枚举表裁决与门禁边界透明化

**Feature**: `specs/223-enum-fabrication-and-gate-boundaries/`
**Spec**: [spec.md](./spec.md)
**Created**: 2026-10-08

---

## 一、三源与冲突裁决顺序（宪法 §II）

本特性涉及的官方源（**全部只读**）：

| # | 源 | 路径 | 本特性用它查什么 |
|---|---|---|---|
| S1 | 出厂反射转储（**裁决基准**） | `D:\AI\SW\_raw\enum_values_sldworks.txt`（10588 成员）· `D:\AI\SW\_raw\reflect\enum_cosworks.txt` | 枚举成员的**权威值**（铁律 4：冲突以出厂类型库为准） |
| S2 | `C:\swapi` 官方页 | `C:\swapi\enums\swPatternElementSelection_e.md` · `swFeaturesToPatternType_e.md` · `types\IModelDoc2\SketchAddConstraints.md` · `types\ILinearPatternFeatureData\PatternElement.md` | 枚举的**成员清单与语义**、属性取值域 |
| S3 | CHM 解包 | `D:\AI\SW\AI Solidworks\`（官方帮助 CHM 解包） | 本特性**未使用**（S1/S2 已足）；如需语义补充才启用 |

**冲突裁决顺序**（铁律 4）：**S1（出厂反射）> S2（swapi 页）> S3（CHM）**。
S1 与 S2 不一致时取 S1，并**显式列出**冲突（既有门禁 `check_enum_values_vs_reflection.py` 已实现该行为）。

**本特性实测到的两源状态**：两张 pattern 表的官方页（S2）与反射（S1）**完全一致**
（3 项 / 2 项，值 0/1/2 与 0/1 均相同）⇒ **无冲突**。

---

## 二、US1 裁决：为什么是「自造抽象冒官方名」而不是「照录写错」

判据（逐条可复现）：

| 检验 | 命令 | 结果 |
|---|---|---|
| 官方页项数 | `grep -c '^| sw' C:/swapi/enums/swPatternElementSelection_e.md` | **3** |
| 表项数 | 读 `scripts/sw_pattern.py:95` | **7** |
| 键是否在官方源出现过 | 官方全源检索 `point` / `edge` / `feature` / `sketch` / `curve` 作**枚举成员名** | **0 命中** |
| 值是否在官方源出现过 | 官方 `swPatternElementSelection_e` 的值为 0/1/2，表里是 0..6 | 只 0/1/2 偶然重叠，其余**无对应** |

⇒ **「照录写错」会保留官方成员名**（如 `swFeatureFaces` 写成 `swFeatureFace`）；
而这两张表用的是**语义抽象键**（`point`/`edge`/`face`/…），官方任何枚举里都没有。
**结论：自造抽象冒官方名**（来源块逐字写「照录官方页」是**假证据**）。

**修法**：不是删，而是**把它还原成它自称的东西** —— 官方枚举的忠实投影。

```python
# 修正后（键 = 小写语义键，值 = 官方值，行末 # 官方成员名）
SWS_PATTERN_ELEMENT_SELECTION = {
    "error": 0,            # swErrorInPatternElementSelection
    "feature_faces": 1,    # swFeatureFaces
    "bodies": 2,           # swBodiesToPattern
}
SWS_FEATURES_TO_PATTERN = {
    "selected_features": 0,  # swFeaturesToPatternSelectedFeatures
    "create_seed_cut": 1,    # swFeaturesToPatternCreateSeedCut
}
```

**为什么带 `# swXxx` 注释**：这是 F3 门禁 `check_enum_values_vs_reflection.py` 的 `CODE_ROW` 正则
（`"key": int,   # swMember`）能匹配的**唯一**形式 ⇒ 修正后这两张表**首次进入覆盖**，
未来再被改错会被机器抓住。**这是"修一次、永久可查"的落点。**

**公开面影响**：`__all__` 不变；`read_pattern_element()` 读的 `PatternElement` 属性官方取值域
**就是** `swPatternElementSelection_e`（`C:\swapi\types\ILinearPatternFeatureData\PatternElement.md`
的 `## Returns` 逐字）⇒ 旧表会让调用方**按错值解读**，修正即修复。

---

## 三、US2 设计：让「跳过」可见

### FR-010 `check_undefined_names.py`

现状：`_has_star_import(tree)` 为真 ⇒ `scan_file()` **直接 `return []`**，主流程只汇总 `total` 与命中数。
**跳过了谁、为什么**，输出里**一个字都没有**。

改法（最小、不改判定）：

1. `_has_star_import()` 改为返回**原因**（`None` / `"star-import"` / `"globals-injection"`），
   保留一个 `_skips_whole_file()` 的布尔薄壳给现有调用点，避免破坏既有测试。
2. `scan_file()` 旁增 `skip_reason(path) -> str | None`（只读、不重复解析的轻量版可接受）。
3. `main()` 汇总 `skipped: list[(file, reason)]`，**无论有没有命中都打印**：
   ```
   跳过 **7** 个文件（判据无法判定 ⇒ 不静默）：
     star-import        scripts/sw_part.py
     globals-injection  mcp-server/server.py
   ```
4. 退出码**不变**（跳过不是失败 —— 它是**看得见的豁免**，与 `KNOWN_BROKEN` 同族）。

**为什么不是"改成 FAIL"**：那 7 个文件里有 5 个是**合法的**（`from x import *` 的模块本就无法静态判定），
把它们判红会逼人加 `# noqa` —— 正是门禁注释里明写禁止的做法。**要的是可见，不是判罪。**

### FR-011/FR-012 `check_enum_values_vs_reflection.py`

现状：`parse_code()` 只 `glob("sw_*.py")`，且只认 `"key": int, # swMember` 行。
**表若没有 `# swXxx` 注释 ⇒ 一行都不产生 ⇒ 静默漏过**（F3 那两张表正是这样漏的）。

改法：

1. **扫描边界**：`glob("sw_*.py")` → `rglob("*.py")`（递归 `scripts/`），
   跳过 `__pycache__`。**覆盖判据不变**（仍是「值 + `# swXxx`」）——扩的是**可见性**，不是放宽判定。
   ★ 实测收益：`scripts/sketch_relations.py` 的 **38 条**合格行**首次**进入比对（原先文件名不以
   `sw_` 开头 ⇒ 一条都没查过）。
2. **键的字符集**：`[a-z0-9_]+` → `[A-Za-z0-9_]+`。
   ★ 又一处**静默边界**：**驼峰键**（如 `sw_ref_geometry.py` 的 `"Parallel": 1, # swRefPlane…`）
   原先**一律匹配不到**。实测放宽后正好多出 `REF_PLANE_CONSTRAINTS` 的 **10 行**，
   且**新值全部与反射一致、0 处新冲突** ⇒ 安全 ✓
3. **新增覆盖清单** `find_int_tables()` / `find_uncovered_claimed_tables()`：
   用 AST 找 `scripts/**/*.py` 的**模块级** `Assign`/`AnnAssign`，其值形如 `Dict[str, int]`
   （全 `str` 键 + 全 `int` 值，**非空**）。对每张表：
   - 若它贡献了 ≥1 条覆盖行 ⇒ **已覆盖**；
   - 否则 ⇒ **未覆盖**；其中「紧邻注释自称官方（`官方` / `swapi` / `sw[A-Z]…`）」的
     另计为**门禁盲区**（★ 那正是 F1 那一类的探测器）。
4. `main()` 在现有输出**之后**打印：
   ```
   覆盖清单 · 扫描 **189** 个文件 · 模块级整数表 **101** 张 · 已覆盖 **33** · 未覆盖 **68**
   其中**自称官方却无 `# swXxx` 标注**（★ 门禁盲区）：**44** 张
      未覆盖：sw_assembly_doc.py:89 ASSEMBLY_DOC_ARITY（134 项）
      …（另有 24 张未列出）
   ```
5. 退出码**不变**（未覆盖的表未必是枚举；把它判红是**噪音**）。

**为什么"未覆盖"必须列名而不是只给数**：F3 的教训正是「只知道 122 行被覆盖，不知道**谁没被覆盖**」。

**★ 已核但**不**纳入的边界（如实登记，不假装已覆盖）**：

| 候选边界 | 处置 | 依据 |
|---|---|---|
| `_raw/topo-reflect/enum_cosworks.txt`（第 3 份转储，被 `sw_topology.py:127` 引用） | **不纳入 `DEFAULT_DUMPS`** | 实测它与第 2 份 `_raw/reflect/enum_cosworks.txt` **逐成员相同**（2372/2372，**0 处值冲突、0 个独有成员**）⇒ 纳入它**不产生任何新判定**（`setdefault` 语义下第 1 份已赢）⇒ 属**无效改动** ✓ |
| `WZD_FASTENER_ANSI_METRIC_SIMPLE`（`sw_hole_features.py:1131`） | **不改、不标** | 值 40/41/38/704 自称「**真机观测**」，官方三源**查不到** ⇒ 铁律 5：**查不到就说查不到**，不猜也不改 ✓ |
| `ROTATION_AXIS_MAP`（`sw_body_ops.py:98`） | **不改、不标** | 同上（真机定案、官方无此映射）✓ |
| D 类余下 42 张「无标注但可溯源」的表 | **只让它可见**（进覆盖清单），**不强行加注释** | 它们**经核对可溯源**（`output/223-verify/fabrication-candidates.md` 逐张给了溯源）⇒ 加注释是**改写**，不是修复；本切片只做**可见性** ✓ |

---

## 三·补、US4 设计：同类候选（门禁双盲的错值表）

**怎么找到的**：委派只读核对成员做**全仓同类候选扫描**（`output/223-verify/fabrication-candidates.md`）。
它的分类是 A（确认伪造）/ B（值不符）/ C（查不到）/ D（无标注盲区），并**额外**单列了
**B′「门禁双盲」**：表**既无** `# swXxx` 注释（门禁看不见），值**又**与出厂反射不符。

**两处 B′ 的裁决（本代理**自己**复核过，不采信成员结论）**：

| 表 | md | 出厂反射 | 谁对 | 依据 |
|---|---|---|---|---|
| `sw_ref_geometry.REF_PLANE_CONSTRAINTS` 的 `…NearestLocation` / `…AlongSketchNormal` | `1028` / `2056`（写 `1028 or 0x400`） | `1024` / `2048` | **反射** | ★ **md 自己矛盾**：`0x400 = 1024`、`0x800 = 2048` ⇒ md 的**十进制列抄错**，其**十六进制列**与反射一致 ⇒ 铁律 4 ✓ |
| `sw_sheet_metal.HEM_POSITIONS` | `Inside=1` / `Outside=2` | `0` / `1` | **反射**（按铁律 4） | ★ **真两源冲突**（两边各自自洽）⇒ 铁律 4「以出厂类型库为准」；★ 而 `create_hem` 在本机**五种形态全部回 `None`**（事实 34/53）⇒ 改它**不回退任何已验证路径**；★ 冲突**写进注释**，真机可推翻 ✓ |

**为什么必须连"注释"一起改**：只改值 ⇒ 门禁仍**看不见**（无 `# swXxx`）⇒ 下次再错还是没人抓。
⇒ ★ 改值 + 补注释 = **一次修好、永久可查**（与 US1 同一手法）。

**文档那一处（`references/part-modeling.md`）**：222 只改了 `.py`，**漏了这份文档** ——
它的「常用约束类型」清单行仍把 `sgEQUAL` / `sgMIDPOINT` 当合法值列给用户。
⇒ 改成官方名 `sgSAMELENGTH` / `sgATMIDDLE`，**并保留一条订正说明**（说明里**必然**要提到旧名）。

---

## 四、US3 设计：同步只做复制

`sync_bundled_skill()` 既有实现会**裁剪**目标里已无源文件的副本。本切片要求**不删任何文件**，
故执行前先算**待裁剪集**（`collect_runtime_files()` 的键集 vs 目标实际文件集），实测：
- 待裁剪 **0** 个（无文件会被删）；
- 目标**缺失 1** 个：`scripts/sw_sketch_relations.py`（同步会**新增**它）。

⇒ 执行 `sync_bundled_skill()` 后复算 `find_bundled_skill_drift()`，须为 `[]`。

---

## 五、测试装置

| 文件 | 判据 | 桩 |
|---|---|---|
| `tests/test_pattern_enum_alignment.py` | 两张表 ⟺ 官方枚举（值 + 成员名 + 项数） | 用 `importlib` 加载 `sw_pattern`，桩掉 `sw_connect`（宽松桩：任意属性返回可调用对象） |
| `tests/test_gate_boundary_transparency.py` | 两道门禁的**边界可见性** | `subprocess` 跑门禁，`encoding='utf-8'` |
| `tests/test_bundled_skill_enum_freshness.py` | 打包副本无 `sgEQUAL`/`sgMIDPOINT` + 与源一致 | 无（纯文件读 + `cmp`） |

**★ 环境坑（必须处理）**：`sw_part.py` 等模块在缺 COM 依赖时会**交互式**问
「是否授权自动安装 [Y/N]」⇒ 无人值守会**挂死**。故凡 import 到 `sw_part` 的测试，
**必须同时桩掉 `sw_preflight`**（宽松桩：任意属性返回可调用对象，但
`import_com_dependencies` 必须返回三元组 `(None, None, None)`）。
本切片的 `test_pattern_enum_alignment.py` 只加载 `sw_pattern`（不触 `sw_part`），
但为稳妥仍装 `sw_preflight` 桩。

---

## 六、并发纪律

- **实现由主代理串行完成**：`sw_pattern.py`（US1）、两道门禁（US2）各是单文件，串行改。
- **核对可委派**：同类候选的全仓扫描（只读、报告落 `output/223-verify/`）派 `ds-eng-worker`。
- **禁止**混元与其他模型；**禁止** COM / 真机。

---

## 七、回滚

- 单文件级：US1 只动 `scripts/sw_pattern.py` 的两个字典 + 一段来源块；US2 各动一个门禁脚本。
- 门禁改动**不改退出码**⇒ 即便回滚也不会让 `release_check` 的红绿翻转。
- 打包副本由 `sync_bundled_skill.py` 幂等重建。
