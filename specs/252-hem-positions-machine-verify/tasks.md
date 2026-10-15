# Tasks — `HEM_POSITIONS` 的真机类型库复核

**Feature**: `specs/252-hem-positions-machine-verify/`
**日期**: 2026-10-09

---

## T-001 弹窗预扫（★ 真机前必做）

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tools/sw_guard.py --scan
  ```
- **期望**：`弹窗 0 个 ⇒ 清理完成`。
- **状态**：☑ 完成（0 个）。

## T-002 定位本机类型库

- **验收**：
  ```bash
  find "/d/Program Files/SOLIDWORKS Corp" -maxdepth 2 -iname "swconst.tlb" 2>/dev/null
  ```
- **期望**：`/d/Program Files/SOLIDWORKS Corp/SOLIDWORKS/swconst.tlb`。
- **状态**：☑ 完成（★ 本机在 **D 盘**；★ 枚举在 `swconst.tlb`，不在 `sldworks.tlb`）。

## T-003 先量：三源对照（★ 走护栏）

- **验收**（★ 复制执行）：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tools/sw_guard.py --timeout 240 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B output/_probe252_hem_tlb.py
  ```
- **期望**：`真机类型库 == 代码 ?  **是**`。
- **状态**：☑ 完成（★ 读到 `Inside=0` / `Outside=1`）。

## T-004 先写判据并**证明它能红**

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
  import sys, importlib.util
  sys.path[:0]=['D:/AI/SW','D:/AI/SW/scripts','D:/AI/SW/tests']
  s=importlib.util.spec_from_file_location('t','D:/AI/SW/tests/test_hem_positions_machine_verified.py')
  m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
  tlb=m._tlb_enum(); print('真机:', tlb)
  print('正常:', len(m._failures(m.HEM_POSITIONS, tlb)))
  print('变异:', m._failures({'inside':1,'outside':2}, tlb))
  "
  ```
- **期望**：`正常: 0` · `变异: [两条不一致]`。
- **状态**：☑ 完成。

## T-005 判据转绿

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_hem_positions_machine_verified.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`（★ 不是 `4 skipped` —— skip 说明没读到类型库）。
- **状态**：☑ 完成（4 passed）。

## T-006 写真机证据

- **验收**：
  ```bash
  cd "D:/AI/SW" && cat output/hem-positions-tlb-evidence.json
  ```
- **期望**：含 `machine_type_library` 与 `verdict`。
- **状态**：☑ 完成。

## T-007 门禁全套（★ 后台跑）

- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/release_check.py > output/_gate252.log 2>&1; tail -4 output/_gate252.log
  ```
- **期望**：`EXIT=0` · `missing []`。
- **状态**：☐ 见 `acceptance.md`。

## T-008 回写四处状态

- **状态**：☐

## T-009 只读证明

- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -cE "SaveAs|Insert[A-Z]|Create[A-Z]" output/_probe252_hem_tlb.py tests/test_hem_positions_machine_verified.py
  ```
- **期望**：**0**（★ 探针与判据都不含任何写/建调用）。
- **状态**：☑ 完成（0）。
