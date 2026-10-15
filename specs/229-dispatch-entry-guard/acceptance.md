# acceptance 229 —— 分发口守卫覆盖门禁

> 特性目录：`specs/229-dispatch-entry-guard/`
> 完成：2026-10-09（主任务 `ff6c7344` 第 3 轮）
> ★ 本文件**只写实测读数**。任何未跑过的项**不得**写成通过。

## 一、完成判据与读数

| # | 判据 | 命令 | 读数 | 结论 |
|---|---|---|---|---|
| A1 | 门禁本体在真树上通过且**非空** | `python -B scripts/check_dispatch_entry_guard.py` | `分发口 37 · 已表态 37 · 违规 0 · 可见 1219 · 不可见 91 · [PASS] · exit 0` | ✅ |
| A2 | ★ 改动前**真的能红** | 门禁写完、声明未插时 | `[FAIL] 违规 37 处`（全部 `undeclared`）· `已表态 0` · `exit 1` | ✅ |
| A3 | 判据 20 例全绿 | `python -B tests/test_dispatch_entry_guard.py` | `Ran 20 tests in 4.625s · OK` | ✅ |
| A4 | 逐张表态 = **37**（纯插入） | `python -B -W ignore output/_add_229_declarations.py` | 首跑 `插入 = 37`；复跑 `插入 = 0`（幂等） | ✅ |
| A5 | 声明分布 | `grep -rh "#: dispatch-guard:" scripts/*.py \| …` | `12 generated-api` · `20 internal-helper` · `2 module-local` · `2 covered-wrappers` · `1 covered check_assembly_doc_call_shape.py` = **37** | ✅ |
| A6 | 接进 `release_check.py`（硬门禁） | 收尾链 | `release_check: 第 1 轮 OK` | ✅ |
| A7 | 登记 `docs/gate-classification.json` | `git diff --stat` | **+6 行**（40 → **41** 条） | ✅ |
| A8 | 224 / 225 / 226 / 227 / 228 回归 | 见 tasks T-229-07 | `OK · OK · OK · OK · OK` | ✅ |
| A9 | 收尾链 `round_chain.ps1` | `pwsh -File tools/round_chain.ps1 -Tests tests/test_dispatch_entry_guard.py` | 见 §二 | ✅ |
| A10 | 门禁全套（3.14.7） | `pythoncore-3.14-64/python.exe scripts/release_check.py` | `EXIT 0` · `"status": "pass"` · `"missing": []` · `gates 40`（39 → 40） | ✅ |

## 二、门禁全套读数（@3.14.7）

```
$ C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py
EXIT=0 · "status": "pass" · "missing": [] · gates = 40（39 → 40）
"dispatch_entry_guard": "pass"
```
★ 口径说明：`gates`（实跑门禁数）**39 → 40**；`docs/gate-classification.json` 的
`classification` 条目 **40 → 41**（该表含若干非 runner 登记项，两个数本来就不等 —— 以实测为准）。

★ 用 **3.14.7** 的理由：受管 3.13.12 **缺 comtypes/win32com** ⇒「参数绑定门禁」会触发
`sw_part.py` 的交互式询问「是否授权自动安装 [Y/N]」⇒ 提示文本被当门禁输出 ⇒
**假红 + 无人值守挂死风险**（spec 224 §五 实测）。判据仍用 3.13.12（桩掉 COM）。

## 三、本切片**改了什么**（逐文件）

| 文件 | 改动 | 性质 |
|---|---|---|
| `scripts/check_dispatch_entry_guard.py` | **新增**（门禁本体） | 新文件 |
| `tests/test_dispatch_entry_guard.py` | **新增**（20 例） | 新文件 |
| `specs/229-dispatch-entry-guard/{spec,plan,tasks,acceptance}.md` | **新增**（四件齐） | 新文件 |
| `output/_probe229_buckets.py` | **新增**（一次性量测探针，**不进仓库代码**） | 量测产物 |
| `output/_add_229_declarations.py` | **新增**（一次性插入脚本，幂等） | 施工产物 |
| `output/_add_229_classification.py` | **新增**（一次性登记脚本，幂等） | 施工产物 |
| 37 个 `def` 上方 | **各插入 1 行** `#: dispatch-guard: …` | ★ **纯插入、零删除**（涉及 30 个文件） |
| `scripts/release_check.py` | `_run_dispatch_entry_guard_gate()` + 调用点 + `raise` + `_gate_results` | 接线 |
| `docs/gate-classification.json` | 新增 1 条（`kind: hard`） | 登记（+6 行） |

## 四、★ 未过门（**不许冒充通过**）

1. ★★ **`exempt` 只表示「已知盲区、登记在案」，不表示「已验证安全」**（spec §三）。
   36 个被豁免的入口（20 internal-helper + 12 generated-api + 2 module-local + 2 covered-wrappers
   中的 `safe_get_com_member` 等）**其 by-ref 占位仍未核**。
2. ★★ **`covered-wrappers` 的承重性只到「名字在白名单里」**，不到「调用形状对」——
   那由 `audit_byref_args`（by-ref 占位）与 `audit_call_arity`（arity）分别负责；
   本门禁**不重复**它们的判定，只保证**入口没被漏掉**。
3. ★ **局部变量 52 个 + 计算式 2 个不可见调用点未表态**（spec §四 明确划界）——
   只计数 + 冻结下界（`BASELINE_INVISIBLE = 91`）。
4. ★ **真机未验**：本切片纯静态，**未新增任何真机证据**；by-ref 语义依据仍是
   `out_i4` / `out_dispatch` 的既有真机结论（2026-10-01 / 2026-10-03）。
5. ★ **别名导入未覆盖**（`from ... import call_assembly_doc as cad`）—— 仓库当前无此写法。
6. ★ **同名 `def` 的跨模块歧义**：量测时观察到 `_checked` 这类名字在 9 个模块里重复
   （早期探针按**裸名**索引调用点，把 9 个 `_checked` 的调用点合并成 94）⇒
   本门禁的 `module-local` 自证因此**按「全仓同名定义数」判**（保守：重复即不许自称 module-local）。
   ★ **同名歧义下「哪些调用点属于哪个 `def`」本门禁不解析**（属 §五「不做」）。
7. **未提交 / 未部署 / 未打 tag**（硬约束）。
8. **223 登记的 8 条 `HEAD` 即红既有失败未修**（权属未确认）。

## 五、★ 下一轮的入口（**具体到文件与动作**）

1. **真正把盲区收掉**（新 spec，需先量）：把 36 个豁免入口的**调用方实参 ↔ 形参对应**解析出来，
   从而**继承 `audit_byref_args` 的判据**（即「一级分发解析」）。
   ★ 第一动作：量「每个分发口的调用点里，成员名实参是**字面量**的比例」——
   `output/_probe229_buckets.py` 已有雏形（`all-callers-literal` 7 / `has-nonliteral-caller` 18，
   但后者的 18 里含**同名歧义**造成的假命中，须先按**限定名**重算）。
2. **52 + 2 两个桶**：先量「能还原成字面量的有多少」，再决定是否要求声明。
3. 其余待办（**需业主另行授权 COM**，未授权前不做）：跨工具 by-ref 口径不一致
   （`audit_call_arity.PURE_OUT`，5 条）· `HEM_POSITIONS` 真机复核。
