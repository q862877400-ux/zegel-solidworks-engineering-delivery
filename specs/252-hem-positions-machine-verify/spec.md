# Spec — `HEM_POSITIONS` 的**真机类型库**复核（把「反射转储」升级为「本机实读」）

**Feature**: `specs/252-hem-positions-machine-verify/`
**日期**: 2026-10-09
**上游**: `tests/test_pattern_enum_alignment.py::test_hem_positions_matches_reflection`（★ 它核的是**离线反射转储**）
**本轮只做一件事**：**直读本机装好的 SolidWorks 类型库**，核 `HEM_POSITIONS` 的两源冲突。

---

## 一、背景（两源冲突 + 一个从未核过的环节）

官方 **md** 写 `swHemPositionTypes_e` = **1 / 2**；**出厂反射转储**写 **0 / 1**。
铁律 4：冲突以**出厂类型库**为准 ⇒ 代码 `HEM_POSITIONS` 取 **0 / 1**。

★★ **但那个「出厂反射转储」是离线文件，从未在真机上核过** —— 245 之前的交接单一直把它列为
「需业主另行授权 COM」的未过门项（`HEM_POSITIONS` 真机复核）。

★ 另一条背景：`create_hem` 在本机**五种形态全部回 `None`**（事实 34 / 53）
⇒ ★ **拿不到行为证据** ⇒ 唯一可行的真机证据 = **读类型库本身**。

---

## 二、★★★ 本轮实测（真机，只读）

★ 走弹窗护栏：`tools/sw_guard.py --timeout 240 -- python output/_probe252_hem_tlb.py`
（★ 护栏预检：连上 SW，**读到文档 0 个** ⇒ 放行）

| 源 | `swHemPositionTypeInside` | `swHemPositionTypeOutside` |
|---|---|---|
| 代码 `HEM_POSITIONS` | **0** | **1** |
| 官方 **md**（`C:/swapi/enums/swHemPositionTypes_e.md`） | 1 | 2 |
| ★★ **真机类型库**（`D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\swconst.tlb`） | **0** | **1** |

⇒ ★★★ **真机类型库 == 代码** ⇒ **代码正确**；★ **官方 md 的 1/2 是错的**（★ 铁律 4 的**首次真机实证**）。

★ 证据落盘：`output/hem-positions-tlb-evidence.json`。

### ★★ 踩的坑（本轮）

1. **类型库不在 C 盘** —— 本机装在 **`D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\`**。
   ★ 且 **枚举在 `swconst.tlb`（常量库）**，不在 `sldworks.tlb`（接口库）—— ★ 只加载后者会**一个常量都读不到**。
2. **`swHemPositionTypes_e`（枚举类型本身）也匹配前缀 `swHemPositionType`** ——
   ★ 它是 `ctypes.c_long` **类**、不是值 ⇒ ★ 必须加 `isinstance(val, int)` 过滤，
   ★ 否则「读数」虚高且**不可 JSON 序列化**。

---

## 三、需求

### FR-001 直读本机类型库，核代码表的值

- **来源**：铁律 4（冲突以出厂类型库为准）+ 交接单登记的未过门项。
- **规则**：`swconst.tlb` 里的 `swHemPositionType*` 常量必须**等于** `sw_sheet_metal.HEM_POSITIONS` 的值。
- **验收场景**：`test_hem_positions_match_machine_type_library` 通过；★ 不一致即红。

### FR-002 ★ 永久负例：官方 **md** 的 1/2 必须**不通过**

- **来源**：两源冲突的另一侧（`C:/swapi/enums/swHemPositionTypes_e.md`）。
- **规则**：md 值必须**不等于**真机类型库值（★ 否则「两源冲突」这个前提就是假的）。
- **验收场景**：`test_official_md_values_are_rejected_by_machine_type_library` 通过。

### FR-003 ★★ 读取器不许太窄（★「读不到」与「全通过」同形）

- **来源**：本仓铁律（「凡量出 0，先怀疑读取器太窄」）。
- **规则**：必须真读到 **≥2** 个 `swHemPositionType*` **整数常量**；★ 且本文件要核的成员必须在读数里。
- **验收场景**：`test_type_library_reader_is_not_too_narrow` 通过；★ 读不到即红。

### FR-004 ★★ 判据必须能红（合成负例）

- **来源**：本仓铁律（「不能红的判据等于空判据」）。
- **规则**：纯函数 `_failures` 在「代码表 = md 值」时必须报 **2** 条；在「类型库为空」时必须报 ≥1 条。
- **验收场景**：`test_pure_function_is_red_able` 通过。

### FR-005 ★ 缺数据源 ≠ 检查失败

- **来源**：本仓纪律。
- **规则**：本机没有 `swconst.tlb` ⇒ `pytest.skip`（★ 不是红）。
- **验收场景**：三个真机判据都有 `skip` 分支。

### FR-006 ★ **只读**：不碰任何文档

- **来源**：业主授权 A（只读）。
- **规则**：探针只**加载类型库、读常量**；★ **不调用任何建模 API、不改/不存任何文档**。
- **验收场景**：护栏预检「读到文档 0 个」；★ 探针代码里无 `SaveAs` / `Insert*` / `Create*` 调用。

---

## 四、非目标

- **不**改 `HEM_POSITIONS` 的值（★ 真机证明它**已经是对的**）。
- **不**改官方 md 侧的任何文件（★ 那是只读来源）。
- **不**去调 `create_hem`（★ 事实 34/53：五种形态全回 `None` ⇒ 拿不到行为证据，白花时间）。

## 五、可测的成功判据（SC）

| # | 判据 | 怎么验 |
|---|---|---|
| SC-1 | 判据**能红** | 代码表改成 md 值 ⇒ **2 条**不一致；类型库为空 ⇒ 「读取器太窄」 |
| SC-2 | 判据**是绿的** | `tests/test_hem_positions_machine_verified.py` **4/4 通过** |
| SC-3 | 门禁全套不破 | `release_check.py` @3.14.7 `exit 0` · `missing []` |
| SC-4 | ★ 只读 | 护栏预检「读到文档 0 个」；★ 探针无任何写操作 |
| SC-5 | 证据落盘 | `output/hem-positions-tlb-evidence.json` 存在 |

## 六、未过门（本轮不做，如实登记）

- **`create_hem` 的行为证据仍拿不到** —— ★ 五种形态全回 `None`（事实 34/53）；
  ★ 本轮是**类型库证据**，★ **不是**「调通 `create_hem`」。
- **其余 16 条 arity 定罪**（★ 需真机逐个调，属下一个切片）。
- 真机未验的其他项（换路由 7 类）；223 的 8 条既有红未修；未提交未部署。
