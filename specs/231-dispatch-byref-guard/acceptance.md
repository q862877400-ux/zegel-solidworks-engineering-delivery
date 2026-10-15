# acceptance 231 —— 分发口调用点的标量 by-ref 占位门禁

## 一、判据读数（全绿）

| 判据 | 读数 |
|---|---|
| 门禁本体（真树） | `可一级转发入口 23 · 已核 21 个 · 已核调用点 311` · `查不到 0 · arity 不符 16 · 形参未绑定 0` · `违规 0` · `[PASS]` · **exit 0** |
| 反射转储 | 15 份 · 成员 **11120** 个 |
| 新判据 `tests/test_dispatch_byref_guard.py` | **Ran 12 tests · OK**（50.9 s） |
| 229 回归 `tests/test_dispatch_entry_guard.py` | **Ran 20 tests · OK**（含在下面 31 里） |
| 230 回归 `tests/test_dispatch_resolution.py` | **Ran 11 tests · OK** |
| 229 + 230 合并回归 | **Ran 31 tests · OK**（33.2 s）★ 证明 `check_dispatch_entry_guard.py` 的重构**向后兼容** |
| 收尾链 `round_chain.ps1` | `release_check: 第 1 轮 OK`（合计 72.1 s） |
| **门禁全套** `release_check.py` @**3.14.7** | **EXIT 0 · `"status": "pass"` · `"missing": []` · `gates 41`**（40 → 41） |
| `docs/gate-classification.json` | **42** 条（41 → 42）★ 与 `gates` 是**两套口径**，别混 |

## 二、★★ 红基线（证明判据真的能红）

### 2.1 合成树端到端负例（核心）

夹具（**只含被测对象**：一个分发口 + 一个裸传标量出参的调用点 + 一份最小转储）：

```python
# scripts/sw_fixture.py
#: dispatch-guard: exempt internal-helper
def _dispatch(obj, member, *args):
    return get_com_member(obj, member, *args)


def use(obj):
    return _dispatch(obj, "SomeMember", 5)      # ← 第 0 位签名说 Int32&
```
```
# dumps/iface_fixture.txt
## Fixture
  Int32 SomeMember(Int32&)
```

读数：

```
[FAIL] 违规 1 处：
  [bare-byref] scripts/sw_fixture.py:7 SomeMember <- sw_fixture.py::_dispatch 第 0 位应为 Int32&，实参是 `5`
[FAIL]
分发口 by-ref · 可核分发口 1 · 已核调用点 1 · 查不到 0 · arity 不符 0 · 形参未绑定 0 · 违规 1 · [FAIL] · exit 1
```

⇒ **exit 1**。判据**能红**。

### 2.2 下界承重（两条）

| 命令 | 读数 |
|---|---|
| `DSH_DISPATCH_BYREF_BASELINE_MIN=22,311` | `[baseline-shrunk] 可核分发口 21 < 下界 22` · **exit 1** |
| `DSH_DISPATCH_BYREF_BASELINE_MIN=21,312` | `[baseline-shrunk] 已核调用点 311 < 下界 312` · **exit 1** |
| 合成树 + `BASELINE_MIN=0,1`（非字面量调用点） | `[zero-checked] 已核调用点 == 0` · **exit 1** |

### 2.3 覆盖完整性（★ 防静默漏点）

```
已核调用点 311 + arity 不符 16 + 形参未绑定 0 == 327 == spec 230 的 `resolved_sites`
```
★ 由 `test_coverage_equals_spec230_resolved_sites` 钉死。若哪天对不上 ⇒ 有调用点**被静默吞掉**。

## 三、本轮修正的两处

| # | 问题 | 处置 |
|---|---|---|
| ① | 首版只判 `classes == "resolved"` 的 18 个入口 ⇒ 只核 **269** 个调用点，**漏掉 3 个 `partial` 入口贡献的 42 个** | 改为判**所有可一级转发**的入口 ⇒ **311**，与 230 的 327 对上 |
| ② | 首版 `com_args()` 用 `None` 表示两种不同情况（成员名非字面量 / 形参槽没绑上）⇒ **静默降级** | 改**三态显式返回**（`ok` / `nonliteral` / `unbound`），后两者**分别计数并打印** |

★ ②正是 spec 230 的教训（「解析不出必须显式判出来」）在**本切片自己的实现**上又出现了一次 ——
**教训写进散文不会拦人，只有把它变成形态才拦得住。**

## 四、★ 一条**未定罪**的观察（别当缺陷去修）

`arity 不符 16` 条，**全是**「实参 = 反射计数 − 1」，且它们的内联签名表**自己写着**
「不含末尾 by-ref `ErrorCode`」（如 `sw_simulation_study._checked` 的 `CreateNewStudy`：表说 3、反射说 4）。

⇒ ★★ **这是约定问题、不是缺陷**。门禁**不得自动挑选约定**（spec 227 教训）⇒ **只登记、不判罪**。
定罪需要**真机裁决**（`省略 by-ref 形参` 是否可行）—— 本仓已有反证据
（`out_i4()` 真机实测：`省略该参数` ✗ `DISP_E_PARAMNOTOPTIONAL`，见 spec 228 §三），
但那 16 条的内联表**另一种写法**是否等价，**未验**。

## 五、未过门（如实登记）

1. **真机未验**：本切片纯离线静态门禁，未调 COM / 真机。
2. **16 条 arity 不符未定罪**（需业主另行授权 COM）。
3. **别名导入未覆盖**（`import x as y` / `from x import f as g`）—— spec 230 已登记。
4. **局部变量 / 计算式两个桶（52 + 2）未覆盖** —— 只计数、不判罪。
5. **`partial` / `unresolved` / `no-callers` 入口的非字面量调用点未核**。
6. **223 的 8 条 `HEAD` 即红既有失败未修**（先确认权属）。
7. 未提交 / 未部署 / 未删任何文件 / 未派任何成员。
