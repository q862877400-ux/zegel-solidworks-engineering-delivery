# Tasks — 16 条 arity 不符的分桶定罪

**Feature**: `specs/253-arity-mismatch-triage/`
**日期**: 2026-10-09

---

## T-001 先量：导出 16 条明细

- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B output/_probe253_arity_sites.py > output/_probe253_arity_sites.txt 2>&1
  grep -c "^--- " output/_probe253_arity_sites.txt
  ```
- **期望**：**16**。
- **状态**：☑ 完成（16）。

## T-002 ★★ 按差值归桶（★ 推翻「全部 −1」）

- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -E "实参个数|反射签名" output/_probe253_arity_sites.txt | head -8
  ```
- **期望**：出现 **差 0**（`GetWhatsWrong`）· **差 −10/−11/−6**（三个 `*args`）· **差 −3**（两个 `Get*Location`）· 其余 −1。
- **状态**：☑ 完成（★ 只有 **10** 条是 −1）。

## T-003 先写判据并**证明它能红**

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
  import sys, importlib.util
  sys.path[:0]=['D:/AI/SW','D:/AI/SW/scripts','D:/AI/SW/tests']
  s=importlib.util.spec_from_file_location('t','D:/AI/SW/tests/test_arity_mismatch_triage.py')
  m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
  print('正常:', len(m._bucket_failures(m._TRIAGE)))
  f=dict(m._TRIAGE); f[('sw_simulation_results.py',246)]=('GetNodeLocation',1,4,'byref-tail')
  print('翻 real-gap:', len(m._bucket_failures(f)))
  "
  ```
- **期望**：`正常: 0` · `翻 real-gap: 1`。
- **状态**：☑ 完成。

## T-004 判据转绿

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_arity_mismatch_triage.py -q 2>&1 | tail -2
  ```
- **期望**：`5 passed`。
- **状态**：☑ 完成。

## T-005 ★★ 真机只读复核（★ 走护栏）

- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tools/sw_guard.py --timeout 240 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B output/_probe253_whatswrong.py
  ```
- **期望**：`3 个 by-ref VARIANT  OK` · `2 个 …  FAIL` · `0 实参  FAIL`。
- **状态**：☑ 完成（★ SW rev 34.4.1）。

## T-006 真机后确认环境干净

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tools/sw_guard.py --scan
  ```
- **期望**：`弹窗 0 个`；★ 且预检显示 **0 个文档**（★ 临时零件已关）。
- **状态**：☑ 完成。

## T-007 门禁全套（★ 后台跑）

- **状态**：☐ 见 `acceptance.md`。

## T-008 回写四处状态

- **状态**：☐

## T-009 未改 `scripts/` 的证明

- **验收**：
  ```bash
  cd "D:/AI/SW" && ls -l --time-style="+%m-%d %H:%M" scripts/check_dispatch_byref_guard.py scripts/sw_routing.py scripts/sw_simulation_study.py
  ```
- **期望**：mtime 全部**早于** `23:56`（★ 本切片开工时刻）。
- **状态**：☑ 完成。
