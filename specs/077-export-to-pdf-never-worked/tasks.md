# 077 · Tasks（全部完成，轮 158）

- [x] T-7301 做工程图补上轮矩阵的空格 ⇒ **推翻"对象不对"**
  `→ 验收:` `python tools/probe_pdf_on_drawing.py`（末行打印"扫了 N 个窗口 · 无模态框"）
- [x] T-7302 ★★★ 读源码定位第一处（`GetSldWorksObject` 两套源都没有）
- [x] T-7303 修第一处 ⇒ **暴露第二处**（`Path`）
- [x] T-7304 ★★ 修后真机验证 `%PDF-1.4` + **页数 = 1**
- [x] T-7305 回归判据 4 条 `→ 验收:` `python -m pytest tests/test_sw_export_pdf_contract.py -q`（**4 passed**）
- [x] T-7306 事实 98 + 能力证据 + 门禁 + 回归（`release_check` exit 0）
