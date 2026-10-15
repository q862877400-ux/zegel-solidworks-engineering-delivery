# Tasks — 223 的 8 条既有红：逐条定权属

**Feature**: `specs/275-existing-red-ownership/`
**日期**: 2026-10-10

## T-001 ★★ 实跑 8 条 ⇒ 确认仍全红
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q -p no:cacheprovider \
    tests/test_server_wiring.py::test_expected_batch_size \
    tests/test_mcp_protocol_layer.py::test_protocol_tool_count_matches_the_two_paths_sum \
    tests/test_shell_params_capability.py::test_negative_case_the_two_count_guards_match_reality \
    tests/test_effect_declarations.py::test_effects_table_is_fresh \
    tests/test_effect_declarations.py::test_table_covers_every_tool \
    "tests/test_real_gap_triage_contract.py::test_real_capabilities_default_to_should_expose[sw_part-linear_pattern]" \
    tests/test_real_gap_triage_contract.py::test_wrapper_rule_does_not_swallow_real_gaps \
    tests/test_com_member_helpers.py::test_every_helper_user_can_actually_import_it
  ```
- **期望**：`8 failed, 3 passed`。 **状态**：☑ 完成（★ 8 failed · 3 passed）。

## T-002 ★★ 逐条定因
- **状态**：☑ 完成（★ 见 `spec.md` §1.2 的 8 行表）。

## T-003 ★★★ 逐条定**归属**（★ 这是 223 没做的）
- **验收**：
  ```bash
  cd "D:/AI/SW" && git diff HEAD --numstat -- mcp-server/
  ```
- **期望**：★ **5 个 batch 文件**在差异里（★ 那 20 条工具的来源）；★ 而 8 条涉及的测试文件**全在 HEAD 状态**。
- **状态**：☑ 完成（★ **5 阻塞 / 3 无关**）。

## T-004 修 B6/B7（★ 样本随事实更新）
- **期望**：★ `("sw_part","linear_pattern")` ⇒ `("sw_hole_features","create_hole_pattern")`；★ 实测新样本 `该挂`。
- **状态**：☑ 完成。

## T-005 修 B8（★ 正则 → AST 裸调用）
- **期望**：★ 注释**不再**命中；★ 裸调用**仍**被抓；★ 限定名不算。
- **状态**：☑ 完成。

## T-006 重跑 ⇒ ★ 8 → 5 红
- **验收**：同上命令（★ 两个文件整体跑）。
- **期望**：`5 failed, 34 passed`。 **状态**：☑ 完成。

## T-007 判据（★ 先红后绿）
- **验收**：
  ```bash
  cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest -q tests/test_existing_red_ownership.py 2>&1 | tail -2
  ```
- **期望**：`5 passed`。 **状态**：☑ 完成。

## T-008 门禁全套（★ 后台跑）
- **验收**：`output/_gate275.log` 末尾 `EXIT=0` · `"missing": []`。
- **状态**：☐ 见 `acceptance.md`。

## T-009 回写四处状态
- **状态**：☐
