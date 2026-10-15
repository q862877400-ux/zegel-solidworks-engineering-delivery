# Tasks — 两种改法对比 + 拍板

**Feature**: `specs/289-arity-change-route-decision/`
**日期**: 2026-10-10

## T-001 ★ 搜「与表同口径的镜像」
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -n "'ICWStudyManager': {" -A 4 scripts/sw_api_cosworks.py
  ```
- **期望**：★ `ARITY` 表里有 `ICWStudyManager` 段，★ 值与 `STUDY_MANAGER_ARITY` **同口径**。
- **状态**：☑ 完成（★ **第 5 类同步点**）。

## T-002 ★ 核它同口径
- **期望**：★ `CreateNewStudy: 3` · ★ `RunAllStudies: 0` ✓
- **状态**：☑ 完成。

## T-003 ★ 列两条路 + 四维对比
- **期望**：★ **甲 5 类同步 ↔ 乙 2 处**。
- **状态**：☑ 完成。

## T-004 ★★★ **拍板**
- **期望**：★ **乙** + ★ 两条理由（★ `arity` 桶只计数 · ★ 目标是运行期能调通）。
- **状态**：☑ 完成。

## T-005 判据（★ 先红后绿）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_arity_change_route_decision.py 2>&1 | tail -2
  ```
- **期望**：`6 passed`。 **状态**：☑ 完成。

## T-006 门禁全套（★ **不跑生成器链** —— 没改 `scripts/`）
- **验收**：`output/_gate289.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☑ 完成。

## T-007 回写四处状态
- **状态**：☐
