# Tasks — 「同步打包副本」不是待办

**Feature**: `specs/286-bundle-sync-is-automatic/`
**日期**: 2026-10-10

## T-001 ★ 现场比对 `scripts/*.py` ↔ 副本
- **验收**：
  ```bash
  cd "D:/AI/SW" && for f in scripts/*.py; do b="apps/workbench-ui/src-tauri/resources/skill/$f"; cmp -s "$f" "$b" || echo "异/缺: $f"; done; echo "比对完"
  ```
- **期望**：★ **无输出**（★ 全一致）。
- **状态**：☑ 完成（★ **199 一致 · 0 不一致 · 0 缺**）。

## T-002 ★ 读门禁的两道守
- **验收**：
  ```bash
  cd "D:/AI/SW" && grep -c "bundled_skill_files\|digest_freshness" scripts/release_check.py
  ```
- **期望**：★ ≥2。 **状态**：☑ 完成（★ `bundled_skill_files` **471** · ★ `digest_freshness` 在 `gates` 里）。

## T-003 ★ 核链的**头尾**
- **期望**：★ 头 = 尾 = `scripts/sync_bundled_skill.py`。
- **状态**：☑ 完成。

## T-004 判据（★ 先红后绿 · ★ live 比对）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_bundle_sync_is_automatic.py 2>&1 | tail -2
  ```
- **期望**：`4 passed`。 **状态**：☑ 完成。

## T-005 门禁全套（★ 后台跑 · ★ **不跑生成器链** —— 没改 `scripts/`）
- **验收**：`output/_gate286.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-006 回写四处状态（★ **删号**：② 段 3 → 2）
- **状态**：☐
