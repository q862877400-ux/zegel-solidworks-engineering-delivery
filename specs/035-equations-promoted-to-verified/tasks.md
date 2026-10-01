# 035 · Tasks（全部完成，轮 116）

- [x] T-3101 决定**不补新能力**，改给已有 `stitched` 条做真机验证
- [x] T-3102 挑风险最低的 ⇒ `equations`
- [x] T-3103 写 `tools/verify_equation_smoke.py`（新零件 + 收尾查模态框）
  `→ 验收:` `python tools/verify_equation_smoke.py`（**5/5**）
- [x] T-3104 ★ 核对**往返一致**（写入 == 读回）
- [x] T-3105 升等级：`capabilities.yaml` + 源码来源块 + 测试断言
  `→ 验收:` `python -m pytest tests/test_sw_equation_contract.py -q`（10 passed）
- [x] T-3106 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
