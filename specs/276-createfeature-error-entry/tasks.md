# Tasks — 给「`CreateFeature` 回 `None`」找到能报错的入口

**Feature**: `specs/276-createfeature-error-entry/`
**日期**: 2026-10-10

## T-001 ★★ 搜「报错入口」候选
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -in "GetCreateFeatureErrors\|GetLastError\|GetErrorMessages\|GetWhatsWrong" _raw/reflect_sldworks/iface_sldworks.txt
  ```
- **期望**：★ 3 个候选（★ `GetCreateFeatureErrors` · `GetErrorMessages` · `GetWhatsWrong`）。
- **状态**：☑ 完成。

## T-002 ★★★ 逐条读**官方 Remarks** 判适用性
- **验收**：★ 读 `C:/swapi/types/IFeatureManager/GetCreateFeatureErrors.md` · `ISldWorks/GetErrorMessages.md` · `IModelDocExtension/GetWhatsWrong.md`。
- **期望**：★ `GetCreateFeatureErrors` 只对 **Mate Controller** ⇒ **排除**；★ `GetErrorMessages` = **会话级最近 20 条** ⇒ **可用**。
- **状态**：☑ 完成。

## T-003 写只读真机探针（★ 走护栏）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" tools/sw_guard.py --timeout 300 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" output/_probe276_error_entry.py
  ```
- **期望**：★ 预检「0 个文档」· ★ 用完关闭 · ★ 读数落 `output/_probe276_error_entry.txt`。
- **状态**：☑ 完成。

## T-004 ★★★ 清栈 → 触发失败 → **立刻**读栈
- **期望**：★ 读到 **`选择失败。`** + **`基体-法兰1: 所选的草图对此操作无效。`**（★ MsgID **909 / 1124 / 1124**）。
- **状态**：☑ 完成（★ **真因首次可读**）。

## T-005 顺带实测另两个入口（★ 留证）
- **期望**：★ `GetWhatsWrong` ⇒ `Features=None`；★ `GetCreateFeatureErrors` ⇒ 类型不匹配（★ 不适用）。
- **状态**：☑ 完成。

## T-006 ★★ 读官方示例逐字对比
- **期望**：★ 官方**不调 `AccessSelections`**；★ 官方靠关草图后的**自带选中** ⇒ `GetSelectedObject6(1,-1)`。
- **状态**：☑ 完成。

## T-007 判据（★ 先红后绿）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_createfeature_error_entry.py 2>&1 | tail -2
  ```
- **期望**：`5 passed`。 **状态**：☑ 完成。

## T-008 门禁全套（★ 后台跑）
- **验收**：`output/_gate276.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-009 回写四处状态
- **状态**：☐
