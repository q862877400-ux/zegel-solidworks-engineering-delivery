# acceptance 241 · 验收记录（废弃入口互锁的覆盖收口）

> 全部读数**本机实测**，命令在 `tasks.md`（可复制）。
> ★ 判据与门禁用**两个**解释器：pytest 风格 + 门禁全套用 **3.14.7**，纯静态探针用 **3.13.12**。

## 一、判据读数

| 判据 | 改前（红基线） | 改后 |
|---|---|---|
| `tests/test_deprecated_entry_interlock.py` | **2 failed, 4 passed** | **6 passed** |
| `tests/test_save_routing_interlock.py` | 5 passed | **5 passed**（+1 新例 = 6） |
| `tests/test_tool_specs_batch80.py` | 7 passed | **7 passed** |
| 合计（三文件） | — | **18 passed** |

★ 红基线**两例**：
1. `test_registration_table_has_no_dead_entries` —— `{'sw_assembly.py': {'AddMate5': {'now': 0, 'registered': 1}}, 'sw_assembly_doc.py': {'AddMate5': {'now': 0, 'registered': 1}}}`
   （★ 靶子表里**没有** `AddMate5` ⇒ 登记的就是**死条目**）
2. `test_dotted_call_form_is_not_a_blind_spot` —— `assert 'AddMate5' in {'InsertWrapFeature','SaveAs','SaveAs2'}`

## 二、★ 变异检验（证明扫描面改动 **load-bearing**）

| 文件 | 旧口径（只认字面量） | 新口径（+点式 +`call_assembly_doc`） |
|---|---|---|
| `sw_assembly.py` | `[]` ← ★ **读成 0 处** | `[(415, 'AddMate5')]` |
| `sw_assembly_doc.py` | `[(364, 'AddMate5')]` | `[(364, 'AddMate5')]` |
| `sw_connect.py` | `[]` ← ★ **读成 0 处** | `[(1167, 'SaveAs')]` |

⇒ ★★ **旧口径在 2 个文件上读成 0** —— 那不是"没有问题"，是**探测器漏了**
（★ 本仓纪律：「减少 = 探测器漏了，不是问题解决了」）。

## 三、门禁全套（3.14.7）

```
EXIT 0 · "status": "pass" · "missing": []
gate_wiring: scripts/check_*.py 44 个（★ 未新增）
signature_audit_freshness: 6 个模块逐项相符（sw_weldment.py 66 = 66）
digest_freshness: [PASS] 与生成器输出逐字节相同
dispatch_entry_guard: 分发口 37 · 已表态 37 · 违规 0 · 可见 1183 · 不可见 85 · [PASS]
fact_single_home: [WARN] 2 处逐字复述（★ **既有**：docs/dead-ends.md 复述事实 230 · specs/202 复述事实 303）—— 告警级，不拦
```

★ **两个门禁数都不变**：`release_check` 的 `gates` = **44** · `gate-classification.json` 的 `classification` = **48**。

## 四、★ 核心事实（本轮新立的）

1. ★★★ **「只认字面量形态」与「只看点式调用」是同一个病**（spec 239 ↔ spec 241，方向相反）：
   - 239：调用**藏在共用骨架**里（点式）⇒ 字面量扫描读成 **0**；
   - 241：调用**写成点式**（`asm_model.AddMate5(...)`）⇒ 只认字面量的扫描读成 **0**。
   ⇒ ★★ **通用形态**：**凡是"按某一种写法找调用"，都要问「换一种写法还找得到吗」**。
2. ★★ **靶子表里已有一个"一次都没被看见"的成员**：`SaveAs` 在 `sw_connect.py:1167` 是**点式**调的
   ⇒ ★ 它**一直在靶子表里**，却**从没被任何判据看见**（★ 与"一个存在但没人用的守卫与没有守卫等价"同族）。
3. ★★ **登记表是"现状"、不是"历史"** —— `tests/test_save_routing_interlock.py` 里那条
   `("sw_connect.py", (916, "SaveAs"))` **同时**踩两个坑：行号漂到 **1167** + **从没被任何判据读过**
   ⇒ ★ 一条死数据躺了 **5 天**。★ 与"mock 落后于换代"**同病**：**改了实现之后，配套的登记/mock/钉死数量
   都要跟着改，而它们不会自己报错**。
4. ★★★ **官方 `AddMate5` 的三条分流是"按配合种类"分的，不是"按 `mate_type` 数值"** ——
   `swMateDISTANCE` 既可能是**平面距离**（⇒ `CreateMate`）也可能是**柱面距离**（⇒ `AddDistanceMate`）
   ⇒ ★★ **一个 `mate_type` 参数定不下来** ⇒ 换它**必须真机验**（铁律 2）。
   ★ 这也是本规格**只登记、不改路由**（FR-008）的**硬理由**。

## 五、★ 交接单前提**第十次**被推翻

交接单 ② 待办 1 写：「`scripts/sw_assembly.py::add_mate` 按 `mate_type` 分流」
⇒ ★ **实测：`scripts/sw_assembly.py` 里没有 `add_mate` 这个函数**。两个同名候选：

| 函数 | 位置 | 有没有 `mate_type` | 状态 |
|---|---|---|---|
| `add_mate(doc, *args)` | `scripts/sw_assembly_doc.py:331` | ✗（`*args` 15 个直传） | ★ docstring **已逐字记档保留**（**记档不是待办**） |
| `add_mate5_checked(asm_model, mate_type, …)` | `scripts/sw_assembly.py:363` | ✓ | ★ 真正带 `mate_type` 的那个；**本轮未改**（见 §四.4） |

## 六、★ 本轮踩到的坑

1. ★★★ **多行 docstring 忘了闭合** —— 新写的 `tests/test_deprecated_entry_interlock.py` 头部
   四段说明后**漏了 `"""`** ⇒ `SyntaxError: invalid character '★' (U+2605)`。
   ★ **这正是 AGENTS.md §十八 记的那个坑**（"多行 docstring 挨着来源块 ⇒ 总有人把来源块写进三引号"）——
   ★ 只是这次的形态是**整个模块 docstring 没闭合**，报错指向 `def _scan_calls` 的 docstring 行（**不是真因**）。
   ⇒ ★ 修法：在 `# ── 来源 ──` **之前**补 `"""`。
2. ★★ **`unittest` 收集不到本仓的 pytest 风格判据** —— `python -m unittest tests.test_save_routing_interlock`
   报 **`Ran 0 tests`**（该文件是 `def test_*` 函数、不是 `TestCase` 方法）
   ⇒ ★ 这类文件**只能用 3.14.7 `-m pytest`**（与 ③.33 一致）。
3. ★★ **登记表用"行号"必然腐烂** —— 见 §四.3。★ 本仓纪律早写着「判据按**名字**定位，不按行号」。
4. ★★★ **`docs/known-facts.md` 的事实 272 也是"落后于换代"的活样本** ——
   它逐字写着「`tests/test_deprecated_entry_interlock.py`（**4 个 test**）」与「恢复后 ⇒ **4 passed**」，
   ★ 而本轮加了 **2** 条判据 ⇒ 真值是 **6**。
   ★★ **没有任何门禁钉这个数**（`check_refuted_patterns` 只校 `refuted-patterns.json` 的 `anchor_quote`，
   ★ 那些 quote 里**不含**这串）⇒ ★ **它不会自己报错** —— ★ 与 §四.3 **同病**。
   ⇒ ★ 本轮**已改**（事实 272：两族 → **三族** · 4 个 test → **6 个 test** · 4 passed → **6 passed**），
   ★ 并把 spec 241 的两条新判据**写进家里**（★ 别处只链接）。

## 七、未过门（★ 如实列出，不掩盖）

- ★ **未跑 COM / 未真机验** ⇒ ★ **不宣称**任何废弃入口的替换**已可用**（三处调用点**保持原样**）。
- ★ `sw_assembly.py:415` / `sw_assembly_doc.py:364` 的 `AddMate5` 与 `sw_connect.py:1167` 的 `SaveAs`
  **仍是既有偏差**（★ 以登记形式**显式存在**，不是被掩盖）。
- ★ **靶子表仍只有 4 条** —— 官方索引里 **1671 条 / 1455 个成员名**，
  而**未过滤地按名字比对**会出 **147 处命中**、**绝大多数是假阳性**（三类已记档）
  ⇒ ★ 要把它们收进来，**每条都要读两边的签名**（那是**独立的一件工作**，未立项）。
- ★ 扫描器按**成员名**筛（★ 不按接口）⇒ ★ 若将来出现「同名但非 COM 对象」的点式调用，会**假阳性**；
  ★ 本树实测 **0 处**（★ 那是**下界**，不是证明）。
- ★ 223 登记的 8 条 `HEAD` 即红既有失败**未修**（权属不明）；`HEM_POSITIONS` 真机复核**未做**。
- ★ 未提交 / 未部署 / 未打 tag。
