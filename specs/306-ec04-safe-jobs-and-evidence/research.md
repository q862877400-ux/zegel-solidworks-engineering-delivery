# Research — 306-ec04-safe-jobs-and-evidence

**Feature**: `specs/306-ec04-safe-jobs-and-evidence/`

**来源**: ★ **本会话真做过的决定与真读数**（★ 不编）

---

### 1. ★ `uncertain` **不能回 `running`**

★ ★★★ 那是「不重试」的**结构性保证** —— 想重试也走不通

### 2. ★ 节点租约 + **围栏令牌**（单调递增）

★ ★ **过期 worker 不能继续修改**

### 3. ★ 批准**绑 contract/plan/model 三版本**

★ ★★ **旧证据不能放行新模型**

### 4. ★ **`HAS_GLOBAL_TRANSACTION = False`**

★ ★★ COM **没有**数据库式全局事务 ⇒ 用**前向补偿**

### 5. ★ 前向补偿**绝不删用户文件**

★ ★ 「失败不丢用户文件」

### 6. ★ 独立验收器**只读** + **自评拒**

★ ★ 不把同一 Agent 自评当放行者

### 7. ★ 无许可 ⇒ **`design_advice_only`**

★ ★ **不是 pass、也不是 fail**

