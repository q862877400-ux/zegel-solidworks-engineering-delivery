# spec 235 —— 分发口**调用点**的非字面量实参门禁

> 收 spec 230–234 一路登记下来的**最后一块无判据区**：37 个分发口的 362 个调用点里，
> 有 **8 个**把成员名以**非字面量**传入 ⇒ `audit_byref_args` 看不见，而 `resolution()`
> 只把入口**分类计数**，**没有任何判据落在调用点上**。

## 一、来源与动因

| 项 | 内容 |
|---|---|
| 来源 | 本仓自身（元门禁）；动因 = `output/AUTO_HANDOFF.md` ② 段待办 1（2026-10-09 12:07 第 8 轮交接） |
| 上游切片 | spec 229（分发口守卫覆盖）· 230（解析面）· 231（一级转发调用点 by-ref）· 232（解析盲区普查）· 233（调用点去重口径）· 234（`local` 桶候选集） |
| 许可 | 本仓库 MIT。**无第三方代码引入**；官方依据只读 `_raw/**/iface_*.txt`（出厂程序集纯元数据反射）与 `C:\swapi\types\**`（官方 API 文档镜像，**只读**） |
| 三源 | ① `C:/swapi/types/<接口>/<成员>.md` ② CHM 解包（本轮未用到）③ `_raw` 反射转储 |

**为什么这条线还没走完**：`audit_byref_args` 只审「成员名**写在调用点**」的调用。
分发口的**调用点**若把成员名以条件式 / 变量 / 下标传入，静态审计**一律看不见**；
而 `check_dispatch_entry_guard.resolution()` 只回答「入口能不能解析」，不回答
「**这个调用点的实参到底是什么**」⇒ 8 个点长期「被计数、无判据」。

## 二、需求（每条带来源）

- **FR-001**（来源：交接单待办 1 ①）**先量**：列出 `partial` / `unresolved` / `no-callers`
  入口的调用点里，成员名实参**非字面量**的**全部**位置与形态。★ 结果见 §三 读数。
- **FR-002**（来源：待办 1 ②）**能枚举就核存在性**：候选集若可静态枚举（封闭形态清单），
  每个候选值必须能在**官方两源**里查到；查不到 ⇒ 要么拼错、要么**试名探测**，后者须表态。
- **FR-003**（来源：待办 1 ③）**枚举不出就要求声明**：调用点**正上方**必须有一行
  `#: dispatch-fwd: <code> <理由>`，`code ∈ {dynamic, upstream, probe}`（封闭词表）。
  ★ **二级转发只「要求声明」不「递归解析」** —— 追下去会变成会移动的靶子。
- **FR-004**（来源：spec 227 / 234 的教训）**每个 code 都自带自证条件**，防一键躺平：
  - `dynamic` ⇒ 静态**能**枚举 ⇒ 红；
  - `upstream` ⇒ 实参**必须**是包围 `def` 的形参，且包围 `def` 名**必须**等于声明的 caller 名；
    能枚举却声明 `upstream` ⇒ 红；
  - `probe` ⇒ 候选值**全部**查得到 ⇒ 红；**枚举不出** ⇒ 红（该用 `dynamic`）。
- **FR-005**（来源：事实 46）**零检查即红**：检查过的非字面量调用点 == 0 ⇒ `[zero-checked]`。
- **FR-006**（来源：spec 233）**只增不减**：调用点数 / 可枚举数 / 候选值 distinct 数**冻结下界**，
  减少 = 读取器或取点漏了（**不是**「问题解决了」）。
- **FR-007**（来源：spec 233 的教训「口径要有人守」）**口径不变量**：凡带非字面量调用点的入口，
  `resolution()` 给它的分类**必须**是 `partial` / `unresolved`（`resolved` 的定义就是
  「**全部**调用点的成员名都是字面量」）⇒ 不符 ⇒ `[class-mismatch]` 红。
- **FR-008**（来源：spec 230/234）**不许静默降级**：读取器读不出 ⇒ 返回 `None` + 原因，
  **不许**当成空集。

## 三、验收判据（可复制执行）

```bash
# ① 门禁本体（真树）
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B \
  scripts/check_dispatch_forward_arg_guard.py
#   ⇒ 非字面量 8 · 可枚举 4 · 候选值 12 · 违规 0 · [PASS] · exit 0

# ② 新判据（19 例）
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B \
  -m unittest tests.test_dispatch_forward_arg_guard

# ③ 229–235 合并回归
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest \
  tests.test_dispatch_entry_guard tests.test_dispatch_resolution \
  tests.test_dispatch_byref_guard tests.test_dispatch_blindspot_guard \
  tests.test_dispatch_call_site_dedup tests.test_dispatch_arg_guard \
  tests.test_dispatch_forward_arg_guard

# ④ 收尾链（生成器 → release_check → 聚焦测试）
pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests/test_dispatch_forward_arg_guard.py

# ⑤ 门禁全套（★ 必须用 3.14.7）
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py
#   ⇒ status pass · missing [] · gates 43 → 44 · classification 44 → 45
```

## 四、非目标

- **不**递归解析二级转发（`upstream` 只要求声明 + 自证）。
- **不**裁决「候选值对不对」（只判「名字在两源里存在」；真机语义需业主授权 COM）。
- **不**动 `check_dispatch_entry_guard.resolution()` 的口径（`resolved 18 / partial 3 /
  unresolved 4 / no-callers 12` 与 `327` 保持不变）。
- **不**改任何既有 `#: dispatch-guard:` / `#: dispatch-arg:` 声明。
- **不**扩 `_entry_sites()` 认别名（触发条件 = spec 232 门禁变红，真树 0 处）。
