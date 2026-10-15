# Tasks — 造钣金件失败

**Feature**: `specs/262-base-flange-creation-regression/`
**日期**: 2026-10-10

## T-001 先量：自己搭探针
- **状态**：☑ 完成（★ 失败，但**不能作为证据** —— 可能是我搭错）。

## T-002 ★★ 用**仓里维护的**配方复现
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tools/sw_guard.py --timeout 420 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B tests/solidworks_sheet_metal_regression.py --output-dir "D:/AI/SW/output/fixtures/_probe262"
  ```
- **期望**：`"status": "failed"` · `CreateFeature(IBaseFlangeFeatureData) 创建失败`。
- **状态**：☑ 完成（★ **也失败** ⇒ 是能力的问题）。

## T-003 ★★★ 静态排除 261
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
  import sys, importlib.util
  sys.path[:0]=['D:/AI/SW','D:/AI/SW/scripts','D:/AI/SW/tests']
  s=importlib.util.spec_from_file_location('t','D:/AI/SW/tests/test_base_flange_creation_regression.py')
  m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
  b=m._create_flange_body()
  print('含 _read_k_factor:', '_read_k_factor' in b)
  print('含写路径:', m.WRITE_PATH in b)
  "
  ```
- **期望**：`含 _read_k_factor: False` · `含写路径: True`。 **状态**：☑ 完成。

## T-004 判据能红 / 转绿
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_base_flange_creation_regression.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-005 门禁全套（★ 后台跑）
- **状态**：☐ 见 `acceptance.md`。

## T-006 回写四处 + 把新缺陷加进 ② 段
- **状态**：☐
