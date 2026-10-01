# 118 · Tasks（全部完成，轮 198）

- [x] T-11801 ★★★ 写全仓扫描器 `tools/scan_silent_source_fallbacks.py`（纯静态）
  `→ 验收:` `python tools/scan_silent_source_fallbacks.py`（398 文件 / **125** 守卫 / 已说明 7 / **候选 12**）
- [x] T-11802 ★★★ 7 个门禁候选**逐个回代码核调用方** ⇒ **全部有正当理由**
- [x] T-11803 ★★★ 立定则：「缺陷是**缺源 ⇒ 结论变成通过**」，不是「缺源 ⇒ 返回值」⇒ 本扫描**只能当粗筛**
- [x] T-11804 ★★ **负例自证**（把 `SCAN` 指到临时目录：静默的列出 / 已说明的不计入）
  `→ 验收:` 见 `converge.md` 第二节
- [x] T-11805 事实 138（含我**三次**自己的错：`ast.Dict` · `relative_to` · 词表漏词）
- [x] T-11806 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）· 全量 **1260 passed**
