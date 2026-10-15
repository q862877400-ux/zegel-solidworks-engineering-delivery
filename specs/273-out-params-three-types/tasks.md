# Tasks — 改表前先量：12 处的 by-ref 出参只有 3 种类型

**Feature**: `specs/273-out-params-three-types/`
**日期**: 2026-10-10

## T-001 ★★ 先量：读 271 落盘的 13 条（12 arity + 1 all-byref）
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n '成员     :' output/_probe271_retriage.txt
  ```
- **期望**：**13** 个成员名（★ 其中 `GetWhatsWrong` 是 `all-byref` 桶）。
- **状态**：☑ 完成（★ 13 条逐条核过）。

## T-002 ★★★ 取出各成员的 by-ref 出参并归集类型
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n '反射签名 :' output/_probe271_retriage.txt | grep -o '&\{1,\}' | wc -l
  ```
- **期望**：出参类型去重后 **3 种**（`Int32&` **9** · `Double&` **6** · `SwDmTableError&` **1**）。
- **状态**：☑ 完成。

## T-003 ★★ 核 `GetWhatsWrong` 不在 12 条里
- **验收**：`GetWhatsWrong` 的签名是 `(Object&, Object&, Object&)` ⇒ ★ 出参**为空**（差 0）⇒ ★ 它是 `all-byref` 桶。
- **期望**：★ 逐成员表 **12** 条 · 出参总数 **16**。
- **状态**：☑ 完成。

## T-004 写判据（★ 先红）+ 三组负例
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_out_params_three_types.py -q 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-005 门禁全套（★ 后台跑）
- **验收**：`output/_gate273.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-006 回写四处状态
- **状态**：☐
