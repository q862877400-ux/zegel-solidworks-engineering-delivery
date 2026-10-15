# tasks 230 · 可复制执行

> 受管解释器（判据）：`C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B`
> 门禁全套：`C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe`

## T-230-01 · 门禁本体（解析面）

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B D:/AI/SW/scripts/check_dispatch_entry_guard.py
```

**期望**：`exit 0` · `[PASS]` · 含
`★ 解析面（按文件作用域索引调用点）：resolved 18 · partial 3 · unresolved 4 · no-callers 12 · 可解析调用点 327`
· 末行 `分发口 37 · 已表态 37 · 违规 0 · 可见 1219 · 不可见 91 · 可解析 18/37 · [PASS] · exit 0`

## T-230-02 · 判据

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest tests.test_dispatch_resolution -v
```

**期望**：`Ran 11 tests` · `OK`（≈25 s）

## T-230-03 · 红基线（★ 证明能红）

```bash
# ① resolved 下界抬高 ⇒ baseline-shrunk
DSH_DISPATCH_BASELINE_MIN=37,91,1219,19,327 C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B D:/AI/SW/scripts/check_dispatch_entry_guard.py; echo "exit=$?"
# ② 可解析调用点下界抬高 ⇒ baseline-shrunk
DSH_DISPATCH_BASELINE_MIN=37,91,1219,18,328 C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B D:/AI/SW/scripts/check_dispatch_entry_guard.py; echo "exit=$?"
```

**期望**：两次均 `[FAIL]` · `exit=1` · 报文分别含
`可解析分发口 18 < 下界 19` / `可解析调用点 327 < 下界 328`

## T-230-04 · 229 回归（★ 不许破）

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -m unittest tests.test_dispatch_entry_guard
```

**期望**：`Ran 20 tests` · `OK`

## T-230-05 · 收尾链（生成器 + release_check + 聚焦测试）

```bash
pwsh -File D:/AI/SW/tools/round_chain.ps1 -Tests tests/test_dispatch_resolution.py
```

**期望**：`release_check 第 1 轮 OK` · 11 passed

## T-230-06 · 门禁全套（★ 必须 3.14.7）

```bash
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe D:/AI/SW/scripts/release_check.py
```

**期望**：`EXIT 0` · `"status": "pass"` · `"missing": []`
