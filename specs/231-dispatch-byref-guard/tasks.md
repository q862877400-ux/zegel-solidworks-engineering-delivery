# tasks 231 —— 分发口调用点的标量 by-ref 占位门禁

> ★ 每条任务带**可复制执行**的验收命令。解释器：受管 **3.13.12**（判据）；
> `release_check` 用 **3.14.7**（受管 3.13.12 缺 comtypes/win32com ⇒ 假红 + 挂死风险）。

## T-231-01 门禁本体

产出：`scripts/check_dispatch_byref_guard.py`

```bash
cd /d/AI/SW && C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_dispatch_byref_guard.py; echo EXIT=$?
```
预期：`可一级转发入口 23 · 其中已核 by-ref 的 21 个 · 已核调用点 311` ·
`（非字面量调用点 6 · 成员名查不到 0 · arity 不符 16 · 形参未绑定 0 —— 只计数、不判罪）` ·
`[PASS]` · `exit 0`。

- [x] 完成

## T-231-02 `check_dispatch_entry_guard.py` 最小重构（向后兼容）

产出：`iter_sources(root=None)` / `scan(root=None)` / `inner_wrapper_call()` / `forward_slots()`。

```bash
cd /d/AI/SW && C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest tests.test_dispatch_entry_guard tests.test_dispatch_resolution 2>&1 | tail -4
```
预期：`Ran 31 tests ... OK`（229 的 20 + 230 的 11，**原样绿**）。

- [x] 完成

## T-231-03 判据（★ 先证能红）

产出：`tests/test_dispatch_byref_guard.py`（**12 例**）。

```bash
cd /d/AI/SW && C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest tests.test_dispatch_byref_guard 2>&1 | tail -4
```
预期：`Ran 12 tests ... OK`。

★ **红基线**（改动前必须红过；合成树端到端负例）：

```bash
cd /d/AI/SW && T=$(mktemp -d) && mkdir -p "$T/scripts" "$T/dumps" \
 && printf '#: dispatch-guard: exempt internal-helper\ndef _dispatch(obj, member, *args):\n    return get_com_member(obj, member, *args)\n\n\ndef use(obj):\n    return _dispatch(obj, "SomeMember", 5)\n' > "$T/scripts/sw_fixture.py" \
 && printf '## Fixture\n  Int32 SomeMember(Int32&)\n' > "$T/dumps/iface_fixture.txt" \
 && DSH_DISPATCH_BYREF_ROOT="$T" DSH_DISPATCH_BYREF_DUMPS="$T/dumps/iface_fixture.txt" DSH_DISPATCH_BYREF_BASELINE_MIN=0,0 \
    C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_dispatch_byref_guard.py; echo EXIT=$?
```
预期：`[FAIL] 违规 1 处` · `[bare-byref] scripts/sw_fixture.py:7 SomeMember <- sw_fixture.py::_dispatch 第 0 位应为 Int32&，实参是 `5`` · **exit 1**。

- [x] 完成

## T-231-04 接进发布门禁

产出：`scripts/release_check.py` 的 `_run_dispatch_byref_guard_gate()` + 聚合；
`docs/gate-classification.json` 登记（`kind: hard`）。

```bash
cd /d/AI/SW && C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py 2>&1 | tail -3; echo EXIT=${PIPESTATUS[0]}
```
预期：`"missing": []` · **exit 0**。门禁数 `gates` **41**（40 → 41）；`classification` **42**（41 → 42）。

- [x] 完成

## T-231-05 收尾链

```bash
pwsh -File D:\AI\SW\tools\round_chain.ps1
```
预期：`release_check: 第 1 轮 OK`。

- [x] 完成

## T-231-06 收口三处状态

`docs/ROADMAP.md` §一游标 · `.workbuddy-ai/memory/2026-10-09.md`（append）·
`output/AUTO_HANDOFF.md`（覆盖写）· `output/AUTO_RUN_2026-10-09-*.md`。

- [x] 完成

## 未完成（登记，不在本切片）

- [ ] 16 条 arity 不符的**定罪** —— **需业主另行授权 COM**（真机裁决「纯出参能否省略」）。
- [ ] 别名导入（`import x as y` / `from x import f as g`）的调用点 —— 先量再决定。
- [ ] 局部变量 / 计算式两个桶（52 + 2）—— 先量「能还原成字面量的有多少」。
- [ ] 真机复核（本切片纯离线）。
