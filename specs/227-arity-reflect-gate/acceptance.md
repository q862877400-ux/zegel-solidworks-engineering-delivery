# 验收 227 · `*_ARITY` 表 × 出厂反射门禁

> 全部为**离线**读数。未提交 / 未部署 / 未调 COM 或真机 / 未删任何文件 / 未派任何成员。

## 一、判据读数

| 判据 | 命令 | 读数 |
|---|---|---|
| 新判据 | `python -B tests/test_arity_tables_vs_reflection.py` | **Ran 14 tests · OK** |
| 新判据（★ 改动前红基线） | 同上门禁本体，**未加声明时** | **未表态 14 · 值不符 15 · [FAIL] · exit 1** |
| 224 回归 | `python -B tests/test_enum_table_disposition.py` | **8/8 OK** |
| 225 回归 | `python -B tests/test_gate_blind_spot_claim.py` | **11/11 OK** |
| 226 回归 | `python -B tests/test_gate_prose_provenance_claim.py` | **9/9 OK** |
| 契约回归 | `pytest tests/test_sw_view_contract.py test_extended_modules_contract.py test_sw_assembly_doc_contract.py test_sw_pattern_contract.py` | **53 passed** |
| 未调用助手（元） | `pytest tests/test_no_uncalled_helpers.py tests/test_uncalled_exempt_has_reason.py` | **7 passed**（232 s） |
| **门禁全套** | `pythoncore-3.14-64/python.exe scripts/release_check.py` | **EXIT 0 · status pass · missing [] · 38 道门禁** |

## 二、门禁本体读数（真树）

```
转储 49814 行 · 成员名 13671 个 · 表 14 张 · 声明 552 条
by-ref 约定：included 1 张 / excluded 13 张（未表态 0 张）
调用站点覆盖（下界 · 只认 `_checked` / `call_assembly_doc`）：113 / 552 条（20.5 %）
同名多接口（按声明值可对上）：25 条
[PASS] 已表态 14 · 未表态 0 · 值不符 0 · exit 0
```

★ 与 224/225/226 的关系：枚举门禁的**盲区张数 55 → 56**（新增 `sw_view.py:113 VIEW_ARITY`，
因为它表体内的注释进了盲区窗口 ⇒ 按 226 的规矩补了 `#: enum-gate: not-enum arity`）。
**只增不减**，与三道判据的**下界断言**（44 / 54 / 55）相容 ⇒ 不制造新红。

## 三、改动清单（全部离线）

| 文件 | 改动 | 性质 |
|---|---|---|
| `scripts/check_arity_tables_vs_reflection.py` | 新增门禁本体 | 新增 |
| `scripts/release_check.py` | `_run_arity_tables_gate()` + `_gate_results` 登记 + `raise` | 新增（**第 19 道并入门禁**，全套 38 项） |
| `docs/gate-classification.json` | 登记 `hard` / `_run_arity_tables_gate` / reason | 新增 1 条（39 条） |
| `scripts/sw_assembly_doc.py` 等 **13** 个模块 | 各插 1 行 `#: arity-reflect: byref=excluded` | **纯插入零删除** |
| `scripts/sw_assembly_doc.py` | 插 `#: arity-reflect: byref=included` | 同上 |
| `scripts/sw_view.py` | 插 2 行声明 + `ShowMagnifyingGlass` **5 → 6** + 3 行出处注释 | 值订正（**真缺陷**） |
| `tests/test_arity_tables_vs_reflection.py` | 新判据 14 例 | 新增 |
| `apps/workbench-ui/.../resources/skill/**` | 打包副本同步（462 文件，`pruned=[]`） | 生成器产物 |

## 四、未过门（★ 明确列出，不许冒充通过）

1. **`ASSEMBLY_DOC_ARITY` 的 15 条含 by-ref 条目 × `call_assembly_doc` 的潜伏陷阱**：
   该函数把 `*args` 原样转发给 COM，而 by-ref 出参**不由调用方传入** ⇒ 按表调用会
   **多要一个给不出的实参** ⇒ arity 校核**假拒**。★ **当前未爆**（被调用的 19 个成员全部不含 by-ref）。
   本规格**只登记不修** —— 修法需先定「by-ref 出参怎么占位」，未立项。
2. **只比实参个数**：类型 / 顺序 / 语义一律未验。
3. **同名成员多接口**（25 条）：只要声明值在**任一出现处**成立即算对，**未核归属**（223 已登记）。
4. **439 条「只登记、无人调用」**：无任何运行期证据（本规格只**报出**，不判失败）。
5. **真机未验**（离线切片）；`HEM_POSITIONS` 真机复核**需业主另行授权 COM**。
6. 223 登记的 **8 条 `HEAD` 即红既有失败**未修（权属待确认）。
7. **未提交 / 未部署 / 未打 tag**。

## 五、可复用纪律（本轮新增）

1. ★★ **表体内部的注释也在盲区窗口里**（`check_enum_values_vs_reflection.py` 的窗口是
   `lines[lo-15 : hi]`）⇒ 给表**加出处注释**会**同时**影响枚举门禁的分类。
   本轮当场踩到（`VIEW_ARITY` 由「非盲区」变「未表态盲区」），修法是**按规矩补 `#: enum-gate:`**
   而不是把注释删掉。
2. ★★ **门禁不得自动挑选约定**：两种约定并存时，「取残差最小」会让**错值被自动解释掉**。
   约定**由人写死**，门禁只负责「按你写的查」—— 判据里必须有一条证明约定**承重**
   （同一条 by-ref 成员：`included` 绿 / `excluded` 红）。
3. ★ **关联声明用「向上跳过空行取第一行非空行」**（确定性），**不要**用行窗口启发式
   —— 225 已证明窗口对插注释敏感。
4. ★ **「能红的判据」可以是「门禁本体的红基线」**：本轮先跑出 `未表态 14 · 值不符 15 · exit 1`
   再动手，这条读数就是「判据真的能红」的证据。
