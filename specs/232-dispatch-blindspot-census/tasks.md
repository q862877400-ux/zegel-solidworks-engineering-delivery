# tasks 232 —— 分发口调用点的盲区形态普查 + 非 0 即红

> ★ 每条任务带**可复制执行**的验收命令。解释器：受管 **3.13.12**（判据）；
> `release_check` 用 **3.14.7**（受管 3.13.12 缺 comtypes/win32com ⇒ 假红 + 挂死风险）。

## T-232-01 ★ 先量（改任何代码之前）

产出：`output/_probe232_alias.py` · `output/_probe232_blindspots.py`（一次性探针，**不进仓库代码**）。

```bash
cd /d/AI/SW && C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_probe232_alias.py; echo EXIT=$?
cd /d/AI/SW && C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_probe232_blindspots.py; echo EXIT=$?
```

预期：`现有口径调用点总数 = 362` · `★ 别名形态调用点 = 0`；
`(a)…(e)` **5 种形态全部 = 0** · `★ 已覆盖口径的调用点总数 = 362`。

★ 交叉验证（原始 AST 普查）：`Import with asname 94` · `ImportFrom with asname 76` ·
`★ 别名目标命中某个分发口名/模块 = 0`。

- [x] 完成

## T-232-02 门禁本体

产出：`scripts/check_dispatch_blindspot_guard.py`

```bash
cd /d/AI/SW && C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_dispatch_blindspot_guard.py; echo EXIT=$?
```

预期：`分发口 37 个 · 已覆盖调用点 362` · `(a)…(e) 全 0` · `[PASS]` ·
`分发口盲区 · 已覆盖 362 · a 0 · b 0 · c 0 · d 0 · e 0 · 盲区合计 0 · 违规 0 · [PASS] · exit 0`。

- [x] 完成

## T-232-03 判据（★ 先证能红）

产出：`tests/test_dispatch_blindspot_guard.py`（**7 例**）。

```bash
cd /d/AI/SW && C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest tests.test_dispatch_blindspot_guard 2>&1 | tail -4
```

预期：`Ran 7 tests ... OK`。

★ **红基线**（合成树端到端负例；**5 种形态各自**一个，见判据 `test_each_form_is_load_bearing`）：

```bash
cd /d/AI/SW && T=$(mktemp -d) && mkdir -p "$T/scripts" \
 && printf 'def _dispatch(obj, member, *args):\n    return get_com_member(obj, member, *args)\n\n\ndef covered_caller(obj):\n    return _dispatch(obj, "SomeMember", 1)\n' > "$T/scripts/sw_fixture.py" \
 && printf 'import sw_fixture as X\n\n\ndef use(o):\n    return X._dispatch(o, "SomeMember", 1)\n' > "$T/scripts/other.py" \
 && DSH_DISPATCH_BLINDSPOT_ROOT="$T" DSH_DISPATCH_BLINDSPOT_BASELINE_MIN=0 \
    C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_dispatch_blindspot_guard.py; echo EXIT=$?
```

预期：`(a) 模块别名 … = 1` · `[FAIL] 违规 1 处` · `[blindspot] … 形态 (a) 有 1 处解析器看不见的调用点` ·
**exit 1**。

★ **夹具必须自带一个「已覆盖」调用点**（`covered_caller`）—— 否则 `covered == 0` 会让
`[zero-checked]` 先红，负例就**因错误的原因**通过。

- [x] 完成

## T-232-04 接进发布门禁

产出：`scripts/release_check.py` 的 `_run_dispatch_blindspot_guard_gate()` + 聚合 + 结果字典；
`docs/gate-classification.json` 登记（`kind: hard`）。

```bash
cd /d/AI/SW && C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py 2>&1 | tail -3; echo EXIT=${PIPESTATUS[0]}
```

预期：`"missing": []` · **exit 0**。门禁数 `gates` **42**（41 → 42）；
`classification` **43**（42 → 43）。★ 两套口径**都 +1**（别混，spec 229 教训）。

- [x] 完成

## T-232-05 生成器链（新门禁会让产物过期）

```bash
cd /d/AI/SW && C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe -B tools/gen_harvest_digest.py
```

预期：`门禁 39 道`（38 → 39）。★ 首跑 `release_check` 若报
`docs/harvest-digest.md 与生成器输出不一致`（第 343 行 `共 38 道` vs `应为 39 道`）⇒
跑生成器即绿（**这是预期行为，不是缺陷**）。

- [x] 完成

## T-232-06 回归（★ 证明没碰坏 229/230/231）

```bash
cd /d/AI/SW && C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest tests.test_dispatch_entry_guard tests.test_dispatch_resolution tests.test_dispatch_byref_guard 2>&1 | tail -4
```

预期：`Ran 43 tests ... OK`（20 + 11 + 12）。★ 本切片**未改**
`check_dispatch_entry_guard.py`（只 import 它的口径）。

- [x] 完成

## T-232-07 收尾链

```bash
pwsh -File D:\AI\SW\tools\round_chain.ps1
```

预期：`release_check: 第 1 轮 OK`。

- [x] 完成

## T-232-08 收口三处状态

`docs/ROADMAP.md` §一游标 · `.workbuddy-ai/memory/2026-10-09.md`（append）·
`output/AUTO_HANDOFF.md`（覆盖写）· `output/AUTO_RUN_2026-10-09-*.md`。

- [x] 完成

## 未完成（登记，不在本切片）

- [ ] **扩 `_entry_sites()` 去认别名** —— ★★ **触发条件是本门禁变红**，不是「想做就做」：
      真树 0 处 ⇒ 现在写等于**没有靶子的守卫**。★ 下一轮**不要**主动扩。
- [ ] 局部变量 / 计算式两个桶（52 + 2）—— 先量「能还原成字面量的有多少」。
- [ ] 16 条 arity 不符的**定罪** —— **需业主另行授权 COM**。
- [ ] `HEM_POSITIONS` 真机复核 —— **需业主另行授权 COM**。
- [ ] 真机复核（本切片纯离线）。
