# spec 234 —— `local` 桶调用点的候选集门禁

> 特性目录：`specs/234-local-bucket-candidate-gate/`
> 施工轮：主任务 `ff6c7344` 第 8 轮（2026-10-09）· 性质：**纯离线静态判据**
> 未调 COM / 真机 · 未提交 · 未部署 · 未删任何文件 · 未 create/update 任何自动任务。

## 一、来源与动因

| 项 | 内容 |
|---|---|
| 来源 | spec 229 量出的「审计不可见」三个桶之一（`local`）· spec 230/231/232/233 四次登记「只计数、不判罪」 |
| 上游读数 | spec 233 去重后：`可见 1185 · 不可见 85（形参转发 37 / **局部变量 46** / 计算式 2）` |
| 许可 | 本仓库 MIT；数据源为**本仓自带**反射转储 + 本机官方文档镜像，无第三方代码引入 |
| 缺口 | `audit_byref_args` 只认「第二实参是字符串字面量」⇒ 这 46 个点**静态审计看不见**；`check_dispatch_entry_guard` 只把它们**计数**进 `buckets["local"]` |

## 二、需求（每条带来源）

| # | 需求 | 来源 | license |
|---|---|---|---|
| FR-001 | 枚举 `local` 桶调用点（成员名以**局部变量**传入），口径**与 `check_dispatch_entry_guard.scan()` 一致**（含 spec 233 的嵌套去重） | spec 233 §四 | 本仓 MIT |
| FR-002 | **候选集读取器**按**封闭形态清单**解析：字面量容器 / 元组解包**按位置投影** / dict 字面量 `.items()` **按位置** / `.keys()` / `.values()` / 模块级常量 / `DICT.get()` **取值** / 下标 | 本切片量测（`output/_probe234_values.py`） | 本仓 MIT |
| FR-003 | 读出的每个候选值必须能在**官方两源并集**里查到：`_raw/**/iface_*.txt`（★ 属性须按 `get_`/`set_` **剥前缀**、接口名取 `## <接口>` 头行）∪ `C:\swapi\types\<接口>\<成员>.md` | 官方 `C:\swapi` 镜像 + 出厂反射转储 | 官方文档镜像，只读 |
| FR-004 | 候选值查不到 ⇒ 该调用点必须表态 `#: dispatch-arg: probe <理由>`（试名探测：fallback 列表**有意**含查不到的候选名） | 本切片实测（3 处 `probe`） | 本仓 MIT |
| FR-005 | 候选集**枚举不出** ⇒ 该调用点必须表态 `#: dispatch-arg: dynamic <理由>` | spec 230/231 的「解析不出必须显式判出来」 | 本仓 MIT |
| FR-006 | **未表态即红**；且两个逃生门**各自带自证条件**：能枚举却声明 `dynamic` ⇒ 红；候选值全查得到却声明 `probe` ⇒ 红；枚举不出却声明 `probe` ⇒ 红 | spec 229「一句话不是守卫」+ spec 227「门禁不得自动挑选约定」 | 本仓 MIT |
| FR-007 | 下界冻结（调用点 46 · 可枚举 42 · 候选值 distinct 131，只增不减）；检查量为 0 判失败 | 事实 46 + spec 230/231/232 同族 | 本仓 MIT |
| FR-008 | 两源**都**读不到 ⇒ `[SKIP]` + `exit 0`（缺数据源 ≠ 检查失败） | spec 227 便携性口径 | 本仓 MIT |
| FR-009 | 与 `scan()` 的 `buckets["local"]` **必须相等**（两个独立实现 + 一致性断言） | spec 233「别另起一套口径」 | 本仓 MIT |

## 三、验收判据（可复制执行）

```bash
# ① 门禁本体（真树）
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_dispatch_arg_guard.py
#   ⇒ local 46 · 可枚举 42 · 候选值 131 · 违规 0 · [PASS] · exit 0

# ② 新判据（17 例）
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest tests.test_dispatch_arg_guard

# ③ 229–234 合并回归
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest \
  tests.test_dispatch_entry_guard tests.test_dispatch_resolution tests.test_dispatch_byref_guard \
  tests.test_dispatch_blindspot_guard tests.test_dispatch_call_site_dedup tests.test_dispatch_arg_guard

# ④ 收尾链（生成器 → release_check → 聚焦测试）
pwsh -File D:\AI\SW\tools\round_chain.ps1 -Tests tests/test_dispatch_arg_guard.py

# ⑤ 门禁全套（★ 必须用 3.14.7）
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B scripts/release_check.py
#   ⇒ status pass · missing [] · gates 42 → 43 · classification 43 → 44
```

## 四、非目标

- **不判**候选值属于**哪个接口**（只判「这个名字在官方两源里存在」）—— 接口归属是 `check_interface_member_ownership.py` 的职责。
- **不扩** `_entry_sites()` 认别名（触发条件是 spec 232 门禁变红）。
- **不动** `dynamic` / `probe` 之外的值集（不把候选集写进门禁常量：真源留在源码里）。
- 真机验证：**不做**（需业主另行授权 COM）。
