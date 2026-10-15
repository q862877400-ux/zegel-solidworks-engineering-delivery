# Tasks — `create_draft` 首次真机验证

**Feature**: `specs/283-create-draft-machine-verified/`
**日期**: 2026-10-10

## T-001 造方块 + **只给面**（6 面 × 3 标记）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" tools/sw_guard.py --timeout 300 -- "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" output/_probe283_draft.py
  ```
- **期望**：★ 18 臂**全失败** · ★ 报文**恒定**「此拔模方向尚未定义。」。
- **状态**：☑ 完成。

## T-002 ★ 读栈
- **期望**：★ **「此拔模方向尚未定义。」**。
- **状态**：☑ 完成。

## T-003 ★★★ 单变量：**mark 1 上挂什么**
- **验收**：`output/_probe283_draft_dir.py`（★ 走护栏）。
- **期望**：★ **`Front Plane` + 面#0 ⇒ 成功 `拔模1`**。
- **状态**：☑ 完成（★ **决定性**）。

## T-004 判据（★ 先红后绿）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_create_draft_machine_verified.py 2>&1 | tail -2
  ```
- **期望**：`5 passed`。 **状态**：☑ 完成。

## T-005 状态表 **升为 `True`**
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n '"create_draft": (True' scripts/sw_sheet_metal.py
  ```
- **期望**：★ 那一格是 **`True`**（★ 详细理由在**注释**里）。
- **状态**：☑ 完成。

## T-006 生成器链（★ 改了 `scripts/`）
- **期望**：★ 7 步全 `exit 0`。 **状态**：☑ 完成（7/7）。

## T-007 门禁全套（★ 后台跑）
- **验收**：`output/_gate283.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-008 回写四处状态
- **状态**：☐
