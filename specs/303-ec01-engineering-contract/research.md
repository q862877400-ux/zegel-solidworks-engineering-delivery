# Research — 303-ec01-engineering-contract

**Feature**: `specs/303-ec01-engineering-contract/`

**来源**: ★ **本会话真做过的决定与真读数**（★ 不编）

---

### 1. ★ 唯一入口的判据是 `required_missing`

★ ★ 只有**必需缺失**才阻断 ⇒ 其余是**降级**不是**阻断**

### 2. ★ `Datum` 的身份 = **语义角色**，不是 CAD 平面名

★ ★★ 平面名随 UI 语言变（事实 9）⇒ 拿它当身份会**跨语言失效**

### 3. ★ 温度用**偏移单位**（`OFFSET_UNITS`），不是乘法

★ ★★ 乘法对 °C 是**错的**（0 °C ≠ 0 K × k）

### 4. ★ `compute_hash` **排除自指字段**

★ ★★ 否则哈希**永远算不稳**（算一次变一次）

### 5. ★ `com_eligible()` **只在冻结后**为真

★ ★ 未冻结的契约**不得进 COM**

