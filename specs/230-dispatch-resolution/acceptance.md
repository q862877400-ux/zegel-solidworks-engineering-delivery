# acceptance 230 · 验收读数

> 建立：2026-10-09（主任务 `ff6c7344` 第 4 轮）· 状态：**离线切片已完成**

## 一 · 本轮量测（★ 这是本切片最有价值的部分）

**问题**：229 把 37 个分发口逐个表态，但 `exempt` 只说明「已知盲区」。
**没人量过**：这些分发口的**调用点**能不能静态解析出成员名？

### 1.1 调用点可解析性（`output/_probe230_classes.py`）

```
解析类计数：no-callers 12 · resolved 18 · partial 3 · unresolved 4
可解析调用点 = 327 / 362（90 %）
```

| 类 | 个数 | 说明 |
|---|---|---|
| `no-callers` | 12 | **全是** `sw_api_*.py::call_index`（生成模块，仓库内无调用点） |
| `resolved` | 18 | 每个调用点都解析出**字面量**成员名 ⇒ **可继承 `audit_byref_args` 判据** |
| `partial` | 3 | `sw_assembly_doc.call_assembly_doc`(20) · `sw_drawing_create_missing._read`(12) · `sw_part._safe_com_member`(13) |
| `unresolved` | 4 | `sw_drawing_view.call_view`(1) · `sw_preference_guard._member`(2) · `sw_simulation_loads._check`(27) · `sw_simulation_study_options.set_option`(2) |

### 1.2 ★ 过程中纠正的两处**探针自己的错**（★ 值得记）

| 错 | 现象 | 纠正 |
|---|---|---|
| ① 实参错位 | 把「调用方实参第 `idx+1` 位之后」当成 COM 实参 ⇒ 报出 **43** 条 arity 不符 | ★ `sw_fingerprint._read(member, obj, *args)` 的**成员名是第 0 参、对象是第 1 参** ⇒ 该口径**整体错位**（把 `obj` 也算成 COM 实参）。改为**真位置绑定**（调用方实参 → 形参 → 内部包装调用的实参槽）⇒ 降到 **16** 条 |
| ② 二级转发被静默算成 0 实参 | `sw_simulation_loads._check` 报「实参 0」而它明明有 4 个 | ★ 内部是 `get_com_member(manager, member, *tail)`，而 **`tail` 是局部 list**（不是 vararg）⇒ 属**二级数据流**。改为**严格一级判定** ⇒ 该入口判 `unresolved`（不再产生假读数） |

⇒ ★★ **通用教训**：**「解析不出」必须显式判出来，不能静默降级成 0** ——
静默降级产出的读数**看起来像结论**（如「实参 0」），会把人骗到错的方向。

### 1.3 ★ 一条**未定罪**的观察（★ 记下来，不冒充缺陷）

解析后接 `audit_byref_args` 的判据：**by-ref 裸传 0 处**。
而 **arity 不符 16 处** —— 但**这 16 处全部**是「调用方实参 = 反射计数 − 1」，
且它们的**内联签名表自己写着**「不含末尾 by-ref `ErrorCode`」
（如 `sw_simulation_study._checked` 的 `CreateNewStudy`：表说 3、反射说 4）。

⇒ ★★ **这是**约定问题**，不是缺陷**：门禁**不得自动挑选约定**（spec 227 的教训）。
本轮**只登记读数、不判罪**（FR-6）；真正裁决需**业主授权 COM 的真机证据**
（与 229 待办 3「跨工具 by-ref 口径不一致」同族）。

## 二 · 门禁读数

| 判据 | 读数 |
|---|---|
| 门禁本体（真树） | `分发口 37 · 已表态 37 · 违规 0 · 可见 1219 · 不可见 91 · 可解析 18/37 · [PASS] · exit 0` |
| 解析面 | `resolved 18 · partial 3 · unresolved 4 · no-callers 12 · 可解析调用点 327` |
| ★ 红基线 ①（`resolved` 下界 → 19） | `[baseline-shrunk] 可解析分发口 18 < 下界 19` · **exit 1** |
| ★ 红基线 ②（可解析调用点下界 → 328） | `[baseline-shrunk] 可解析调用点 327 < 下界 328` · **exit 1** |
| 新判据 `tests/test_dispatch_resolution.py` | **Ran 11 tests · OK**（24.3 s） |
| 229 回归 `tests/test_dispatch_entry_guard.py` | **Ran 20 tests · OK**（14.8 s） |
| 收尾链 `round_chain.ps1` | 见 §三 |
| 门禁全套 `release_check.py` @3.14.7 | 见 §三 |

## 三 · 收尾链与门禁全套

（本轮实测读数，见 `output/AUTO_RUN_2026-10-09-1053.md`。）

## 四 · 改动清单

| 文件 | 改动 |
|---|---|
| `scripts/check_dispatch_entry_guard.py` | 新增 `_import_map` / `_entry_sites` / `_bind` / `_one_level_forward` / `resolution`；`_baseline()` 支持 3 或 5 值；`main()` 打印解析面 + 两条下界 + 假绿守卫 |
| `tests/test_dispatch_resolution.py` | 新增 **11 例** |
| `specs/230-dispatch-resolution/` | 四件 |
| `output/_probe230_dispatch_resolve.py` · `_probe230_internal_shape.py` · `_probe230_resolved_check.py` · `_probe230_classes.py` | 一次性量测（**不进仓库代码**） |

★ **未改**：`release_check.py`（改的是**既有已登记门禁**，门禁数不变）·
`docs/gate-classification.json` · 37 个 `#: dispatch-guard:` 声明（**零改动**）·
`tests/test_dispatch_entry_guard.py`（229 的 20 例**原样回归绿**）。

## 五 · 未过门（★ 不许冒充通过）

1. ★★ **解析出的成员名还没有接进 `audit_byref_args`** —— `resolved` 的 18 个入口
   （327 个调用点）的 by-ref 占位**仍未核**。⇒ **spec 231**。
2. `partial` 3 · `unresolved` 4 · `no-callers` 12 **仍无任何运行期证据**。
3. **别名导入未覆盖**（`import sw_a as x` 后 `x._d(...)`；`from sw_a import _d as f`）。
4. **同名 `def` 的跨模块歧义不解析**（判据只保证**不合并**，不保证选对）。
5. `*局部变量` / 计算式成员名**一律判不可解析**（二级数据流不做）。
6. **16 条 arity 不符未定罪**（约定问题，需真机裁决）。
7. **真机未验**（纯静态切片）。
8. **未提交 / 未部署 / 未打 tag**。
