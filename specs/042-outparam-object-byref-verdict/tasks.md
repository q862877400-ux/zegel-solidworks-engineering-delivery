# 042 · Tasks（全部完成，轮 123）

- [x] T-3801 定位真正悬着的 A5 遗留（批次 7 的「未查证的遗留」）
- [x] T-3802 写 `tools/probe_outparam_object_byref.py`（四形态）
  `→ 验收:` `python tools/probe_outparam_object_byref.py`（裁定 out-required）
- [x] T-3803 ★ 修探针自己的 bug（`pythoncom.VARIANT` 不存在 ⇒ `win32com.client.VARIANT`）
- [x] T-3804 ★ 加 D 形态 ⇒ **返回 True** ⇒ 拿到正确传法
- [x] T-3805 修 `audit_call_arity.py` 的 arity 口径（`count = len(_params)`）
- [x] T-3806 ★ 负例固化进仓库 `tools/arity_negative_case.py` + `tests/test_arity_audit_negative.py`
  `→ 验收:` `python -m pytest tests/test_arity_audit_negative.py -q`（**5 passed**）
- [x] T-3807 更新 `docs/signature-audit.md` + 已知事实 68
- [x] T-3808 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
