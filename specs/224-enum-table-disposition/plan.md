# Plan — 枚举表盲区收口

**Feature**: `specs/224-enum-table-disposition/`
**上游**: `specs/223-enum-fabrication-and-gate-boundaries/`

---

## 一、三源与冲突裁决顺序（本仓铁律 4）

本切片的**每一个 `enum` / `member` 声明都要能被三源之一坐实**：

| # | 源 | 路径 | 本切片用它做什么 | 拿不到时 |
|---|---|---|---|---|
| S1 | **出厂反射转储**（`SolidWorks.Interop.*.dll` 纯元数据读取） | `_raw/enum_values_sldworks.txt` · `_raw/reflect/enum_cosworks.txt` | 解析 `{枚举: {成员: 值}}`；`enum` 声明的**值集来源**；FR-001 的放宽对象 | 门禁**SKIP 并 exit 0**（既有便携性守卫，不动） |
| S2 | **官方 API 页** | `C:\swapi\enums\<枚举>.md` · `C:\swapi\types\<Iface>\<Member>.md` | `member` 声明的**成员页存在性**；`enum` 声明的**两源冲突**比对（既有 CONFLICT 段） | `member` 校验 **SKIP**（不判罪）；`enum` 值集只用 S1 |
| S3 | **CHM 解包 / `_raw` 产物** | `_raw/cosworks_signatures.md` · `_raw/reflect/iface_*.txt` · `_raw/member_registry.json` | 交叉佐证（本切片只用于**读**，未新增解析） | —— |

**裁决顺序（冲突时）**：**S1 > S2 > S3**（铁律 4：「签名与值以出厂类型库为准」）。
本切片里唯一用到该顺序的地方是**枚举名本身**：
`sw_topology` 的源码注释写 `swsTopologyGoalType_e`，而 S1（`enum_cosworks.txt:2908`）写
`swsTopologyStudyGoalType_e` ⇒ **以 S1 为准**，注释按 S1 订正（订正痕迹留在源码注释里）。

⚠ **本切片全程离线**：不调 SolidWorks / COM / 真机；S1/S2 都是**磁盘上的静态产物**。

---

## 二、改动面（两个文件 + 44 处声明）

```
scripts/check_enum_values_vs_reflection.py     ← 门禁本体（解析放宽 + 表级声明 + 未表态即红）
scripts/*.py  × 17 个文件 / 44 处               ← 每张盲区表上方插一行 `#: enum-gate: …`
tests/test_enum_table_disposition.py           ← 新判据（本轮先写、先红）
```

**为什么改 17 个文件却算「一件事」**：44 行声明是**同一个机制的落地**，
且**每行都必须能被门禁复核**（`enum` 查值集、`member` 查页、`not-enum` 查词表）。
它们不是 44 个独立改动，而是**一次「让 44 张表进入机器可查状态」的动作**。

**新增文件之外的既有文件**：只**插入**声明行，**不改任何既有代码行**（判据 T-013 钉死）。

---

## 三、门禁改法（逐条对应 FR）

### 3.1 FR-001：`DUMP_ROW` 放宽
```python
# 旧： r"^\s{2,}(?P<member>sw\w+)\s*=\s*(?P<value>-?\d+)\s*$"
# 新： r"^\s{2,}(?P<member>[A-Za-z_]\w*)\s*=\s*(?P<value>-?\d+)\s*$"
```
**为什么安全**：该正则**只在** `## <Enum>` 节内被使用（`parse_dump` 的 `cur` 机制），
节内的 `名字 = 整数` **就是**成员定义。实测成员数 +76、`ok`/不符/查不到/冲突**四个读数全不变**。

### 3.2 FR-002：表级声明解析
```python
DISPOSITION = re.compile(r"#:\s*enum-gate:\s*(?P<code>[a-z][a-z-]*)(?:\s+(?P<arg>\S.*?))?\s*$")
DISPOSITION_CODES = {"enum", "member", "not-enum"}
NOT_ENUM_SUBS = {"arity", "index", "mark", "derived", "observed"}
```
`parse_dispositions()` ⇒ `{(文件名, 表起始行): (code, arg, 行号)}`，归属规则见 spec FR-002。

### 3.3 FR-002：三种 code 的校验
- `enum` ⇒ `enum_value_sets()[arg]` 必须存在；表内值集 ⊆ 它。**不做键名校验**（本地语义键表会假红）。
- `member` ⇒ `C:\swapi\types\*\arg.md` 至少一个；`C:\swapi` 不存在 ⇒ 计入 `skipped`，不判罪。
- `not-enum` ⇒ `arg` ∈ `NOT_ENUM_SUBS`。
- **认不出的 code** ⇒ FAIL（否则声明是装饰品，等于 223 判过的「空判据」）。

### 3.4 FR-003：未表态即红
`main()` 的覆盖清单段改为三段读数：**已覆盖 / 已表态 / 未表态**。
- 既有「门禁盲区）：**N** 张」那一行**保留**（223 判据按它做正则），但 **N 的语义改为「未表态」** ——
  44 张表态后 N 自然为 0，223 的 `len(details) == min(blind, 20)` 仍自洽。
- `未表态 > 0` ⇒ `return 1`。

⚠ **与 223 判据的兼容性**（必须明说，否则下一轮会以为我改坏了）：
`tests/test_gate_boundary_transparency.py::test_enum_gate_reports_coverage_inventory` 断言
「盲区计数」与「`未覆盖：` 明细行数」一致；`::test_enum_gate_exit_code_unchanged` 断言 exit 0。
**两条都继续成立**（表态后盲区 = 0、明细 = 0、exit 0）。

---

## 四、44 处声明的落地方式（可复现）

**不手改**（44 处手改必然错行）。用一次性脚本按 **AST 定位**插入：

```
① find_int_tables() 给出 (文件, 起始行, 表名)
② 对每个待表态的表：在「起始行的上一行」插入 `#: enum-gate: <code> <arg>`
   （同一文件内**从下往上**插入，避免行号漂移）
③ 重跑 find_int_tables() 复核：表名/行号集合必须与插入前**逐项相同**（只多出声明行）
```

⚠ **插入点为什么是「起始行正上方」而不是「注释块顶端」**：见 spec FR-002 的归属规则 ——
`sw_ref_geometry.py` 的相邻表注释块**连成一片**，插在正上方才能让「块里最后一条」唯一归属。

---

## 五、验收命令（每条可复制）

```bash
PY=C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe

# 判据（本切片主判据）
$PY -B tests/test_enum_table_disposition.py

# 门禁本体
$PY -B scripts/check_enum_values_vs_reflection.py

# 223 判据必须仍绿（兼容性）
$PY -B tests/test_gate_boundary_transparency.py

# 222 枚举对齐判据必须仍绿（值没被本轮改动）
$PY -B tests/test_relation_enum_alignment.py
$PY -B tests/test_pattern_enum_alignment.py
```

---

## 六、风险与止损

| 风险 | 止损 |
|---|---|
| 放宽 `DUMP_ROW` 让既有 177 行**冒出新的值不符** | 已**先量后改**（+76 成员、四个读数全不变）；若冒出 ⇒ **停下报业主**，不自行调宽窄 |
| `enum` 声明的值集校验对某张表**假红** | 先按 S1/S2 复核是**表错**还是**声明错**；表错就按铁律 4 改表（记进 acceptance），声明错就改声明。**不改校验强度** |
| `member` 页在别的机器上拿不到 | 设计上 SKIP（不判罪）；`C:\swapi` 在本机存在 ⇒ 本机是**真校验** |
| 44 处插入把行号搞乱 | AST 定位 + 从下往上 + 插入后复核表集合 |
| 未表态判红挡住后续轮次 | 这正是 FR-003 的目的；若下一轮开新表 ⇒ 补一行声明即可，成本 <1 分钟 |
