# Tasks — `Double&` 出参不吃 by-ref VARIANT

**Feature**: `specs/274-double-out-param-form/`
**日期**: 2026-10-10

## T-001 ★★ 查 4 个 out 包装器各自的真机证据
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n "真机" scripts/sw_connect.py scripts/sw_sensor.py | grep -i "out_i4\|out_dispatch\|out_double\|照同一形态"
  ```
- **期望**：★ `out_i4` / `out_dispatch` **有**逐形态实测；★ `out_double` / `out_bstr` **只有类推**。
- **状态**：☑ 完成。

## T-002 写只读真机探针（★ 走护栏）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" tools/sw_guard.py --timeout 300 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" output/_probe274_double_out.py
  ```
- **期望**：★ 预检「0 个文档」· ★ 用完关闭 · ★ 读数落 `output/_probe274_double_out.txt`。
- **状态**：☑ 完成（★ 2 次运行：第一次 5 形态；第二次**加判别器**）。

## T-003 ★★★ 靶子 A：`IBody2::GetExtremePoint` 的 3 个 `Double&`
- **期望**：★ by-ref VARIANT ⇒ **`TypeError`**；★ 裸值 / 省略 ⇒ **通过**且出参**随返回元组回来**。
- **状态**：☑ 完成（`(True, 0.0275, 0.0, 0.0)`）。

## T-004 ★★ 靶子 B（判别器）：`GetWhatsWrong` 的 3 个 `Object&`
- **期望**：★ **只有** by-ref VARIANT 通过；★ 裸值 ⇒ `DISP_E_TYPEMISMATCH`；★ 省略 ⇒ `DISP_E_PARAMNOTOPTIONAL`。
- **状态**：☑ 完成。

## T-005 判据（★ 先红后绿 · ★ 回源码核形态）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_double_out_param_form.py -q 2>&1 | tail -2
  ```
- **期望**：`5 passed`。 **状态**：☑ 完成。

## T-006 ★ 把结论写回 `sw_sensor.out_double`（★ 只写警告，**不改行为**）
- **状态**：☑ 完成。

## T-007 生成器链 7 步 + 门禁全套
- **验收**：★ 7 步全 `exit 0`；★ `output/_gate274.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☑ 链完成（7/7 exit 0）· ☐ 门禁见 `acceptance.md`。

## T-008 回写四处状态
- **状态**：☐
